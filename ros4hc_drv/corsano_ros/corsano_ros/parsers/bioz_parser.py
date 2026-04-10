from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import struct

@dataclass
class BioZData:
    timestamp: float
    record_index: int
    values: np.ndarray  # raw decoded integers

class BioZParser:
    """
    Parses 3D Optical Heart Rate (OHR) packets from raw byte buffers.
    """

    SAMPLE_RATE = 25.0  # Hz, based on your original code

    def __init__(self):
        self._ohr_time = 0.0
        self._last_packet: Optional[BioZData] = None

        # Fixed header layout
        self.header_magic = b'OHR'
        self.header_len = 13
        self.msg_type_offset = 6
        self.samples = 25
        self.bytes_per_sample = 3
        self.packet_size = self.header_len + self.samples * self.bytes_per_sample

    def parse_packets_from_file(self, filename: str) -> List[BioZData]:
        """Reads a binary file and parses all OHR 3D packets."""
        with open(filename, "rb") as f:
            data = f.read()
        return self.parse_packets(data)

    def parse_packets(self, buffer_data: bytes) -> List[BioZData]:
        """Parses all OHR 3D packets contained in a buffer."""
        packets: List[BioZData] = []
        i = 0
        n = len(buffer_data)

        while i < n:
            # Find "OHR"
            idx = buffer_data.find(self.header_magic, i)
            if idx == -1:
                break

            # Ensure message type byte exists
            if idx + self.msg_type_offset >= n:
                break

            # Check message type == 0x3D
            if buffer_data[idx + self.msg_type_offset] != 0x3D:
                i = idx + 1
                continue

            # Ensure full packet fits
            if idx + self.packet_size > n:
                break

            # Extract packet payload
            payload = buffer_data[idx + self.header_len : idx + self.packet_size]

            # Decode 25 samples
            values = np.empty(self.samples, dtype=int)
            for k in range(self.samples):
                chunk = payload[k*self.bytes_per_sample : k*self.bytes_per_sample + 3]
                value = struct.unpack("<H", chunk[:2])[0] 
                if value >= 0x80000:
                    value = 0x80000 - value
                if value < 10000:
                    values[k] = value
                else:
                    values[k] = 0  # optional: ignore invalid samples

            record = BioZData(
                timestamp=self._ohr_time,
                record_index=len(packets),
                values=values
            )
            self._ohr_time += self.samples * 1000.0 / self.SAMPLE_RATE
            packets.append(record)
            self._last_packet = record

            i = idx + self.packet_size  # move to next possible packet

        return packets

    def get_last_packet(self) -> Optional[BioZData]:
        """Returns the most recently parsed OHR 3D packet."""
        return self._last_packet
