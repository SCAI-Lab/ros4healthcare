from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import timezone
from typing import Callable, Optional
import numpy as np


@dataclass
class BioZSampleBatch:
    """
    Container for BioZ (bio-impedance) sample batches.

    Attributes:
        timestamp_ms: Timestamp in milliseconds since start of session.
        record_index: Packet index (0–255).
        quality: Quality indicator (deprecated or reserved).
        bpi: Body position index.
        biozf: Sample format (e.g., 1 = 25 Hz).
        bioz_raw: Raw BioZ samples (int32).
        adc_values: ADC reference values (int32).
        eda_us: Estimated skin conductance (µS).
        normalized_bioz: Normalized BioZ values (optional).
    """

    timestamp_ms: float
    record_index: int
    quality: int
    bpi: int
    biozf: int
    bioz_raw: np.ndarray
    adc_values: np.ndarray
    eda_us: np.ndarray
    normalized_bioz: Optional[np.ndarray] = None


class BioZParser:
    """
    Parser for Corsano BioZ (bio-impedance) data streams.

    Supports both standard 3-byte BioZ samples and extended 6-byte BioZ+ADC frames.
    """

    BIOZ_SR = 25  # Sampling rate in Hz

    def __init__(
        self,
        callback: Optional[Callable[[BioZSampleBatch], None]] = None,
        time_zone=timezone.utc,
        normalize: bool = False,
    ):
        """
        Args:
            callback: Optional function receiving a `BioZSampleBatch`.
            time_zone: Time zone for timestamping (default: UTC).
            normalize: Whether to scale raw BioZ values to [0, 1] range.
        """
        self.bioz_time = 0.0
        self.time_zone = time_zone
        self.callback = callback
        self.normalize = normalize
        self.last_index = None

    def process_metric_array(
        self,
        metric_array: bytes,
        processed_index: int,
        metric_id: int,
        metric_size: int,
    ) -> int:
        """
        Dispatch parsing based on metric ID and payload size.

        Returns:
            Updated processed_index after this metric has been handled.
        """
        if metric_id not in (0x3D, 0x3E):
            print(f"[Info] Skipping unsupported metric ID: 0x{metric_id:02X}")
            return processed_index + metric_size

        if metric_size >= 154:
            return self._process_bioz_adc(metric_array, processed_index, metric_size)
        return self._process_bioz(metric_array, processed_index, metric_size)

    # -------------------------------------------------------------------------
    # Standard 3-byte BioZ samples
    # -------------------------------------------------------------------------
    def _process_bioz(self, metric_array: bytes, processed_index: int, metric_size: int) -> int:
        print("[BioZ] Processing standard BioZ samples")

        # Skip 4-byte header (index, quality, BPI, format)
        processed_index += 4

        no_samples = math.floor((metric_size - 4) / 3)
        raw_values = np.empty(no_samples, dtype=np.int32)

        for i in range(no_samples):
            raw_bytes = metric_array[processed_index:processed_index + 3]
            val = int.from_bytes(raw_bytes, byteorder="little", signed=False)
            processed_index += 3

            # Convert unsigned 24-bit to signed
            if val >= 0x800000:
                val -= 0x1000000
            raw_values[i] = val

        normalized = None
        if self.normalize:
            normalized = (raw_values + 8388608) / 16777216.0

        # Optional callback
        if self.callback:
            batch = BioZSampleBatch(
                timestamp_ms=self.bioz_time,
                record_index=-1,
                quality=-1,
                bpi=-1,
                biozf=-1,
                bioz_raw=raw_values,
                adc_values=np.empty(0, dtype=np.int32),
                eda_us=np.empty(0, dtype=float),
                normalized_bioz=normalized,
            )
            self.callback(batch)

        self.bioz_time += no_samples * 1000 / self.BIOZ_SR
        return processed_index

    # -------------------------------------------------------------------------
    # Extended BioZ + ADC format (6-byte samples)
    # -------------------------------------------------------------------------
    def _process_bioz_adc(self, metric_array: bytes, processed_index: int, metric_size: int) -> int:
        print("[BioZ] Processing BioZ + ADC samples")

        # Header: [index, quality, bpi, biozf]
        index = metric_array[processed_index]
        quality = metric_array[processed_index + 1]
        bpi = metric_array[processed_index + 2]
        biozf = metric_array[processed_index + 3]
        processed_index += 4

        # Packet drop detection
        if self.last_index is not None:
            expected = (self.last_index + 1) % 256
            if index != expected:
                print(f"[Warning] BioZ packet drop: expected {expected}, got {index}")
        self.last_index = index

        no_samples = (metric_size - 4) // 6
        raw_values = np.empty(no_samples, dtype=np.int32)
        adc_values = np.empty(no_samples, dtype=np.int32)
        eda_values = np.empty(no_samples, dtype=float)

        for i in range(no_samples):
            # BioZ (3 bytes unsigned, 24-bit)
            raw_bytes = metric_array[processed_index:processed_index + 3]
            raw_val = int.from_bytes(raw_bytes, byteorder="little", signed=False)
            if raw_val >= 0x800000:
                raw_val -= 0x1000000
            processed_index += 3

            # ADC (3 bytes signed)
            adc_bytes = metric_array[processed_index:processed_index + 3]
            adc_val = int.from_bytes(adc_bytes, byteorder="little", signed=True)
            processed_index += 3

            raw_values[i] = raw_val
            adc_values[i] = adc_val
            eda_values[i] = 1e6 / abs(raw_val) if raw_val != 0 else np.nan

        normalized = None
        if self.normalize:
            normalized = (raw_values + 8388608) / 16777216.0

        batch = BioZSampleBatch(
            timestamp_ms=self.bioz_time,
            record_index=index,
            quality=quality,
            bpi=bpi,
            biozf=biozf,
            bioz_raw=raw_values,
            adc_values=adc_values,
            eda_us=eda_values,
            normalized_bioz=normalized,
        )
        if self.callback:
            self.callback(batch)
        print(f"BIOZ: {batch.eda_us}")
        self.bioz_time += no_samples * 1000 / self.BIOZ_SR
        return batch

    def reset(self) -> None:
        """Reset parser timestamp and last index."""
        self.bioz_time = 0.0
        self.last_index = None
