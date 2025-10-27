from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Callable, Optional, List


@dataclass
class StressRecord:
    """
    Container for parsed Corsano stress record.

    Attributes:
        timestamp_ms: Timestamp in milliseconds.
        stress_skin: Skin-based stress level (arbitrary units).
        stress_skin_quality: Quality indicator (0–4).
        cz: CZ parameter (0–3).
        pcz: PCZ parameter (0–3).
        pczt_min: PCZT value, scaled by 1/100.
        czh: CZH parameter (0–3).
        cc: CC parameter, scaled by 1/100.
        quality: Overall signal quality indicator.
    """

    timestamp_ms: int
    stress_skin: int
    stress_skin_quality: int
    cz: int
    pcz: int
    pczt_min: float
    czh: int
    cc: float
    quality: int


class StressParser:
    """
    Parser for Corsano Stress Records.

    Each record is 18 bytes long. The first 15 bytes contain known fields,
    with the remaining 3 reserved for future use.
    """

    HEADER_SIZE = 0
    RECORD_PAYLOAD_SIZE = 18  # bytes per stress record

    def __init__(self, callback: Optional[Callable[[StressRecord], None]] = None):
        """
        Args:
            callback: Optional function that receives a `StressRecord` instance.
        """
        self.callback = callback
        self.records: List[StressRecord] = []

    # -------------------------------------------------------------------------
    # Core parsing logic
    # -------------------------------------------------------------------------
    def parse_last_record(self, buffer_data: bytes, print_raw: bool = True) -> bool:
        """
        Parse the most recent stress record from the provided buffer.

        Args:
            buffer_data: Raw bytes containing one or more stress records.
            print_raw: Whether to print raw bytes for debugging.

        Returns:
            True if parsing succeeded, False otherwise.
        """
        total_len = len(buffer_data)
        record_size = self.HEADER_SIZE + self.RECORD_PAYLOAD_SIZE

        if total_len < record_size:
            print(f"[Error] Buffer too small: {total_len} bytes (expected ≥ {record_size})")
            return False

        # Extract last complete record
        last_record_bytes = buffer_data[-record_size:]

        if print_raw:
            print(f"[Debug] Last record raw bytes: {last_record_bytes.hex()}")

        payload = last_record_bytes[self.HEADER_SIZE:]
        if len(payload) != self.RECORD_PAYLOAD_SIZE:
            print(f"[Error] Payload size mismatch: {len(payload)} bytes (expected {self.RECORD_PAYLOAD_SIZE})")
            return False

        try:
            # Unpack the first 15 bytes — known Corsano stress fields
            # Format: <I H B B B H B H B
            unpacked = struct.unpack("<I H B B B H B H B", payload[:15])

            record = StressRecord(
                timestamp_ms=unpacked[0],
                stress_skin=unpacked[1],
                stress_skin_quality=min(unpacked[2], 4),
                cz=min(unpacked[3], 3),
                pcz=min(unpacked[4], 3),
                pczt_min=unpacked[5] / 100.0,
                czh=min(unpacked[6], 3),
                cc=unpacked[7] / 100.0,
                quality=unpacked[8],
            )
            print(f"Stress: {record}")

        except struct.error as e:
            print(f"[Error] Failed to unpack stress record: {e}")
            return False

        if print_raw:
            print(f"[Parsed] {record}")

        self.records.append(record)

        if self.callback:
            self.callback(record)

        return True

    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------
    def get_last_record(self) -> Optional[StressRecord]:
        """Return the last successfully parsed record, if available."""
        return self.records[-1] if self.records else None

    def reset(self) -> None:
        """Clear the record buffer."""
        self.records.clear()
