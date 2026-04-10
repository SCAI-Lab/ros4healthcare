from __future__ import annotations
from logging import warning
from dataclasses import dataclass
from datetime import timezone
from typing import Optional, Tuple
import numpy as np


@dataclass
class AccelerometerData:
    """
    Container for parsed accelerometer data from a Corsano device.

    Attributes:
        index: Packet counter (0–255).
        quality: Data quality flag.
        bpi: Body position index.
        af: Accelerometer format.
        x_values: Array of X-axis accelerometer readings (m/s²).
        y_values: Array of Y-axis accelerometer readings (m/s²).
        z_values: Array of Z-axis accelerometer readings (m/s²).
        timestamp_ms: Timestamp of the first sample in milliseconds.
    """

    index: int
    quality: int
    bpi: int
    af: int
    x_values: np.ndarray
    y_values: np.ndarray
    z_values: np.ndarray
    timestamp_ms: float


class AccelerometerParser:
    """
    Parser for accelerometer metric arrays received from Corsano devices.

    This class decodes raw binary accelerometer packets into structured
    arrays of acceleration data, converting to SI units (m/s²).
    """

    ACC_SR: int = 32  # Sampling rate in Hz (samples per second)

    def __init__(self, time_zone: timezone = timezone.utc) -> None:
        self.acc_time: float = 0.0
        self.time_zone: timezone = time_zone
        self.normalize: bool = False
        self.last_index: Optional[int] = None

    def process_metric_array(
        self,
        metric_array: bytes,
        processed_index: int,
        metric_id: int,
        metric_size: int
    ) -> Tuple[int, Optional[AccelerometerData]]:
        """
        Process a metric array and return parsed accelerometer data.

        Args:
            metric_array: The raw binary array of metric data.
            processed_index: The current index within the array.
            metric_id: Identifier for the metric type (0x2B = accelerometer).
            metric_size: Total size of this metric in bytes.

        Returns:
            A tuple containing the updated processed index and an
            AccelerometerData object if the metric was recognized,
            or None otherwise.
        """
        if metric_id != 0x2B:
            warning(
                f"[AccelerometerParser] Skipping unsupported metric ID: "
                f"0x{metric_id:02X} ({metric_id})"
            )
            return None

        return self._process_acc(metric_array, processed_index, metric_size)

    def _process_acc(
        self,
        metric_array: bytes,
        processed_index: int,
        metric_size: int
    ) -> Tuple[int, AccelerometerData]:
        """Decode an accelerometer metric packet into structured data."""
        # --- Parse 4-byte header ---
        index = metric_array[processed_index]
        quality = metric_array[processed_index + 1]
        bpi = metric_array[processed_index + 2]
        af = metric_array[processed_index + 3]
        processed_index += 4

        # Detect dropped packets
        if self.last_index is not None:
            expected = (self.last_index + 1) % 256
            if index != expected:
                warning(
                    f"[AccelerometerParser] Packet drop detected: "
                    f"expected {expected}, got {index}"
                )
        self.last_index = index

        # --- Number of samples ---
        # Each sample = 3 axes × 2 bytes per axis = 6 bytes per sample
        num_samples = (metric_size - 4) // 6
        scale = 9.80665 / 512.0  # Convert raw units to m/s²

        x_values = np.empty(num_samples, dtype=np.float32)
        y_values = np.empty(num_samples, dtype=np.float32)
        z_values = np.empty(num_samples, dtype=np.float32)

        for i in range(num_samples):
            x_values[i] = int.from_bytes(
                metric_array[processed_index:processed_index + 2],
                byteorder="little",
                signed=True,
            ) * scale
            y_values[i] = int.from_bytes(
                metric_array[processed_index + 2:processed_index + 4],
                byteorder="little",
                signed=True,
            ) * scale
            z_values[i] = int.from_bytes(
                metric_array[processed_index + 4:processed_index + 6],
                byteorder="little",
                signed=True,
            ) * scale
            processed_index += 6

        # Create structured result
        data = AccelerometerData(
            index=index,
            quality=quality,
            bpi=bpi,
            af=af,
            x_values=x_values,
            y_values=y_values,
            z_values=z_values,
            timestamp_ms=self.acc_time,
        )

        # Update timestamp
        self.acc_time += num_samples * 1000.0 / self.ACC_SR
        return data

    def reset(self) -> None:
        """Reset parser timestamp and packet counter."""
        self.acc_time = 0.0
        self.last_index = None
