import struct
from datetime import datetime
from util import check_crc, ACTIVITY_TYPE

q = b'\xcaR\xaee\x00\x00\x00\x00\x00\x00\x00\xdf\x17\x00\x00d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xaa\x00l\xf6S\xaee\x00\x00\x00\x00\x00\x00\x00\xdf\x17\x00\x00d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xaa\x00='

class ActivityParser:
    """
    https://developer.corsano.com/ble/ble_commands/files_format/acitivity_file
    B0-B3   Unix timestamp                                                [long]
    B4      Filtered heart rate                                           [unsigned char]
    B5      Quality of Filtered Hear rate  4(good) - 0(bad)               [unsigned char]
    B6-B7   Number of steps in the last period                            [unsigned short]
    B8      Activity Type Enum(ACTIVITY_TYPE)                             [unsigned char]
    B9      Speed                                                         [unsigned char]
    B10     SPO2%                                                         [unsigned char]
    B11-B12 Energy expenditure                                            [unsigned short]
    B13     Filtered respiration rate x4                                  [unsigned char]
    B14     Quality of raw respiration rate 4(good) - 0(bad)              [unsigned char]
    B15     Battery level                                                 [unsigned char]
    B16     Raw BPM                                                       [unsigned char]
    B17     Quality of raw BPM 4(good) - 0(bad)                           [unsigned char]
    B18     Quality of SPO2 4(good) - 0(bad)                              [unsigned char]
    B19-B20 Stress level HRM                                              [unsigned short]
    B21     Quality of Stress Level HRM 4(good) - 0(bad)                  [unsigned char]
    B22-B23 Active calories                                               [unsigned short]
    B24-B30 Undocumented                                                  [pad byte]
    B31-B32 Temperature 1 x100 (CBT on 287-2b)                            [signed short]
    B33-B34 Temperature 2 x100 (Skin temperature at nights)               [signed short]
    B35     Reserved                                                      [pad byte]
    B36     Wearing status of the bracelet 0(not wearing) 4(on the wrist) [unsigned char]
    B37     CRC8 of the message                                           [unsigned char]
    """
    activity_struct = "<l2BH3BH6BHBH7x2hxBx"
    @classmethod
    def parse(self, data):
        if check_crc(data[:-1]) != data[-1]:
            return None
        d = {}
        u = struct.unpack(self.activity_struct, data)
        d["timestamp"] = datetime.fromtimestamp(u[0])
        d["hr_filtered"] = u[1]
        d["hr_filtered_q"] = u[2]
        d["steps"] = u[3]
        d["activity_type"] = ACTIVITY_TYPE(u[4])
        d["speed"] = u[5]
        d["spo2"] = u[6]
        d["energy"] = u[7]
        d["rr_filtered"] = u[8]/4.0
        d["rr_raw_q"] = u[9]
        d["battery"] = u[10]
        d["hr_raw"] = u[11]
        d["hr_raw_q"] = u[12]
        d["spo2_q"] = u[13]
        d["stress"] = u[14]
        d["stress_q"] = u[15]
        d["calories"] = u[16]
        d["temp1"] = u[17]
        d["temp2"] = u[18]
        d["wearing"] = u[19]
        return d
