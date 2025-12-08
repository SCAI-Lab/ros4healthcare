from __future__ import annotations

import struct
from dataclasses import dataclass
from datetime import datetime
from logging import error
from typing import Optional

from corsano_ros.corsano_enums import ACTIVITY_TYPE, check_crc


@dataclass
class ActivityData:
    """Container for parsed activity data from a Corsano device."""

    timestamp: datetime
    hr_filtered: int
    hr_filtered_q: int
    steps: int
    activity_type: ACTIVITY_TYPE
    speed: int
    spo2: int
    energy: int
    rr_filtered: float
    rr_raw_q: int
    battery: int
    hr_raw: int
    hr_raw_q: int
    spo2_q: int
    stress: int
    stress_q: int
    calories: int
    temp1: int
    temp2: int
    wearing: int


class ActivityParser:
    """
    Parser for Corsano activity packets.

    Reference:
        https://developer.corsano.com/ble/ble_commands/files_format/acitivity_file

    Field layout:
        B0–B3   Unix timestamp                                                [long]
        B4      Filtered heart rate                                           [unsigned char]
        B5      Quality of Filtered Heart rate 4(good) – 0(bad)               [unsigned char]
        B6–B7   Number of steps in the last period                            [unsigned short]
        B8      Activity Type Enum (ACTIVITY_TYPE)                            [unsigned char]
        B9      Speed                                                         [unsigned char]
        B10     SPO₂%                                                         [unsigned char]
        B11–B12 Energy expenditure                                            [unsigned short]
        B13     Filtered respiration rate ×4                                  [unsigned char]
        B14     Quality of raw respiration rate 4(good) – 0(bad)              [unsigned char]
        B15     Battery level                                                 [unsigned char]
        B16     Raw BPM                                                       [unsigned char]
        B17     Quality of raw BPM 4(good) – 0(bad)                           [unsigned char]
        B18     Quality of SPO₂ 4(good) – 0(bad)                              [unsigned char]
        B19–B20 Stress level HRM                                              [unsigned short]
        B21     Quality of Stress Level HRM 4(good) – 0(bad)                  [unsigned char]
        B22–B23 Active calories                                               [unsigned short]
        B24–B30 Undocumented                                                  [pad byte]
        B31–B32 Temperature 1 ×100 (CBT on 287-2b)                            [signed short]
        B33–B34 Temperature 2 ×100 (Skin temperature at nights)               [signed short]
        B35     Reserved                                                      [pad byte]
        B36     Wearing status (0 = not wearing, 4 = on wrist)                [unsigned char]
        B37     CRC-8 of the message                                          [unsigned char]
    """

    STRUCT_FORMAT = "<l2BH3BH6BHBH7x2hxB"
    STRUCT_SIZE = struct.calcsize(STRUCT_FORMAT)

    @classmethod
    def parse(cls, data: bytes) -> Optional[ActivityData]:
        """
        Parse a raw activity packet.

        Args:
            data: Raw binary data (should match STRUCT_SIZE + 1 bytes including CRC).

        Returns:
            An ActivityData object if CRC is valid, otherwise None.
        """
        # Validate CRC
        if check_crc(data[:-1]) != data[-1]:
            return None

        # Unpack binary payload
        try:
            unpacked = struct.unpack(cls.STRUCT_FORMAT, data[:-1])
        except struct.error as e:
            error(f"[ActivityParser] Failed to unpack activity data: {e}")
            return None

        # Construct structured ActivityData
        return ActivityData(
            timestamp=datetime.fromtimestamp(unpacked[0]),
            hr_filtered=unpacked[1],
            hr_filtered_q=unpacked[2],
            steps=unpacked[3],
            activity_type=ACTIVITY_TYPE(unpacked[4]),
            speed=unpacked[5],
            spo2=unpacked[6],
            energy=unpacked[7],
            rr_filtered=unpacked[8] / 4.0,
            rr_raw_q=unpacked[9],
            battery=unpacked[10],
            hr_raw=unpacked[11],
            hr_raw_q=unpacked[12],
            spo2_q=unpacked[13],
            stress=unpacked[14],
            stress_q=unpacked[15],
            calories=unpacked[16],
            temp1=unpacked[17],
            temp2=unpacked[18],
            wearing=unpacked[19],
        )
