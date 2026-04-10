import abc
from util import FileNames, ModeID, CHG_STATUS, PLAN, PLAN_FREQUENCY, SPECIAL_MODES
import struct
from datetime import datetime

class BaseCommand(metaclass=abc.ABCMeta):
    cmd = int()
    sidechannel = False

class Command(BaseCommand):
    def execute(self):
        return self.cmd.to_bytes(1, "little")

class CMD_START_STREAMING_DATA(Command):
    """Send the currently selected file"""
    cmd = 1
    sidechannel = True

class CMD_SET_NORMAL_MODE(Command):
    """Set the watch to normal mode"""
    cmd = 15
    def process(self, data):
        m_data = {}
        m_data["result"] = data[1]
        return m_data

class APP_CMD_UPDATE_TIME(Command):
    """Set current time on the watch
    
    Arguments:
    year -- Year to set
    month
    day
    hours
    minutes
    seconds
    utc_offset -- offset in minutes from UTC
    """
    cmd = 22
    def execute(self, year: int, month: int, day:  int, hour: int, 
                minute: int, seconds: int, utc_offset: int):
        return self.cmd.to_bytes(1, "little") + (year-2000).to_bytes(1, "little") +\
            month.to_bytes(1, "little") + day.to_bytes(1, "little") + hour.to_bytes(1, "little") +\
            minute.to_bytes(1, "little") + seconds.to_bytes(1, "little") +\
            utc_offset.to_bytes(2, "little")

class CMD_UPDATE_TIME(Command):
    """Set current time on the watch
    
    Arguments:
    year -- Year to set
    month
    day
    hours
    minutes
    seconds
    utc_offset -- offset in minutes from UTC
    """
    cmd = 22
    def execute(self, year: int, month: int, day:  int, hour: int, 
                minute: int, seconds: int, utc_offset: int):
        return self.cmd.to_bytes(1, "little") + (year-2000).to_bytes(1, "little") +\
            month.to_bytes(1, "little") + day.to_bytes(1, "little") + hour.to_bytes(1, "little") +\
            minute.to_bytes(1, "little") + seconds.to_bytes(1, "little") +\
            utc_offset.to_bytes(2, "little")
    
    def process(self, data):
        m_data = {}
        m_data["result"] = data[1]
        return m_data



class CMD_RESET(Command):
    """Reset the watch"""
    cmd = 24

class CMD_ERASE_FROM_FILE(Command):
    """Erase data from a file
    
    Arguments:
    file -- file to erase from FileNames(Enum)
    size -- number of bytes to erase
    """
    cmd = 45
    def execute(self, file: FileNames, size: int):
        return self.cmd.to_bytes(1, "little") + file.value.to_bytes(1, "little") + size.to_bytes(4, "little")

    def process(self, data):
        m_data = {}
        m_data["result"] = data[1]
        return m_data

class CMD_GET_FILE_SIZE(Command):
    """Report file size
    
    Arguments:
    file -- file to return size, from FileNames(Enum)
    """
    cmd = 46
    def execute(self, file: FileNames):
        return self.cmd.to_bytes(1, "little") + file.value.to_bytes(1, "little")
    
    def process(self, data):
        m_data = {}
        m_data["file"] = FileNames(data[1])
        m_data["size"] = struct.unpack("i", data[2:6])[0]
        return m_data
    
    def str(self, data):
        return f'Selected file {data["file"].name}, file size: {data["size"]}'

class CMD_START_STREAMING_FILE(Command):
    """Start streaming from specific file
    
    Arguments:
    file -- file to stream, from FileNames(Enum)
    """
    cmd = 47
    sidechannel = True
    def execute(self, file: FileNames):
        return self.cmd.to_bytes(1, "little") + file.value.to_bytes(1, "little")

class CMD_START_STREAMING_FILE_WITH_SIZE(Command):
    """Start streaming from specific file with specific data amount, if size is bigger
    than actual size, the full file will be sent.
    
    Arguments:
    file -- file to stream, from FileNames(Enum)
    size -- 4 bytes
    """
    cmd = 48
    sidechannel = True
    def execute(self, file: FileNames, size: int):
        return self.cmd.to_bytes(1, "little") + file.value.to_bytes(1, "little") + size.to_bytes(4, "little")

class CMD_GET_ACTIVE_MODE(Command):
    """Get current mode from the watch"""
    cmd = 49
    def process(self, data):
        m_data = {}
        m_data["mode_id"] = ModeID(int(data[1]))
        return m_data
    
    def str(self, data):
        return f'Current mode {ModeID(data["mode_id"]).name}'

class CMD_GET_BATTERY_LEVEL(Command):
    """Get battery level from the watch"""
    cmd = 50
    def process(self, data):
        m_data = {}
        m_data["level"] = int(data[1])
        m_data["voltage"] = struct.unpack("h", data[2:4])[0]/1000
        m_data["status"] = CHG_STATUS(data[4])
        return m_data
    
    def str(self, data):
        return f'Battery {data["level"]}% Voltage: {data["voltage"]} status: {data["status"].name}'

class CMD_GET_CURRENT_TIME(Command):
    """Get time from watch"""
    cmd = 51
    def process(self, data):
        m_data = {}
        m_data["time"] = datetime.fromtimestamp(struct.unpack("i", data[1:5])[0])
        return m_data
    
    def str(self, data):
        return f'Current time {data["time"]}'

class CMD_GET_CURRENT_FILE(Command):
    """Get selected file from watch"""
    cmd = 58
    def process(self, data):
        m_data = {}
        m_data["file"] = FileNames(data[1])
        return m_data
    
    def str(self, data):
        return f'Current file {data["file"].name}'

class CMD_GET_STREAMING_STATE(Command):
    """Get streaming state from watch"""
    cmd = 59
    def process(self, data):
        m_data = {}
        m_data["streaming"] = bool(data[1])
        return m_data
    
    def str(self, data):
        return f'Currently {"" if data["streaming"] else "not"} streaming'

class CMD_START_STREAMING_FILE_WITH_SIZE_OFFSET(Command):
    """Start streaming from specific file with specific data amount, 
    and an offset from the beginning, if size is bigger than actual 
    size, the full file will be sent.
    
    Arguments:
    file -- file to stream, from FileNames(Enum)
    size -- 4 bytes
    offset -- 4 bytes
    """
    cmd = 68
    sidechannel = True
    def execute(self, file: FileNames, size: int, offset: int):
        return self.cmd.to_bytes(1, "little") + file.value.to_bytes(1, "little") + size.to_bytes(4, "little") + offset.to_bytes(4, "little")

class APP_CMD_SET_PLAN(Command):
    """Set currently active plan
    
    Arguments:
    plan -- Measurement plan to select, from PLAN(Enum)
    ppgfreq -- PPG Frequency to use, from PLAN_FREQUENCY(Enum)
    actfreq -- Activity frequency, value between 0 and 255 in seconds, 0 and 255 are the default (10s)
    """
    cmd = 149
    def execute(self, plan: PLAN, ppgfreq: PLAN_FREQUENCY, actfreq: int):
        return self.cmd.to_bytes(1, "little") + plan.value.to_bytes(1, "little") + ppgfreq.value.to_bytes(1, "little") + actfreq.to_bytes(1, "little")
    
    def process(self, data):
        m_data = {}
        m_data["plan"] = data[1]
        return m_data
    
    def str(self, data):
        return f'Set plan {data["plan"]} successfully'

class APP_CMD_GET_PLAN(Command):
    """Get streaming state from watch"""
    cmd = 150
    def process(self, data):
        m_data = {}
        m_data["plan"] = PLAN(data[1])
        m_data["ppgfreq"] = PLAN_FREQUENCY(data[2])
        m_data["actfreq"] = int(data[3])
        return m_data
    
    def str(self, data):
        return f'Current plan {data["plan"].name}, PPG Frequency {data["ppgfreq"].name}, Activity frequency {data["actfreq"]}'

class APP_SET_PREV_USER_STATUS(Command):
    """Set Preventicus user status
    
    Preventicus refers to a reading of 5 min every 30 min
    Arguments:
    preventicus -- Preventicus mode to activate, either 100 (enabled) or 101 (disabled)
    """
    cmd = 189
    def execute(self, preventicus: int):
        return self.cmd.to_bytes(1, "little") + preventicus.to_bytes(1, "little")
    
    def process(self, data):
        m_data = {}
        m_data["preventicus"] = int(data[1])
        return m_data
    
    def str(self, data):
        return f'Set preventicus to {data["preventicus"]}'

class APP_GET_PREV_USER_STATUS(Command):
    """Get Preventicus user status
    
    Preventicus refers to a reading of 5 min every 30 min
    Mode is 100 (enabled) or 101 (disabled)
    """
    cmd = 190
    def process(self, data):
        m_data = {}
        m_data["preventicus"] = int(data[1])
        return m_data
    
    def str(self, data):
        return f'Preventicus set to {data["preventicus"]}'

class APP_CMD_GET_VITAL_PARAM(Command):
    """Get current state of a vital parameter
    
    Arguments:
    param -- Vital parameter to get
    """
    cmd = 193
    def execute(self, param: int):
        return self.cmd.to_bytes(1, "little") + param.to_bytes(1, "little")

    def process(self, data):
        m_data = {}
        m_data["param"] = int(data[1])
        m_data["setting"] = struct.unpack("h", data[2:4])[0]
        return m_data
    
    def str(self, data):
        return f'Vital param {data["param"]} setting {data["setting"]}'

class APP_CMD_START_SPECIAL_MODE(Command):
    """Set watch to special mode
    
    Arguments:
    param -- Special mode to set
    """
    cmd = 216
    def execute(self, param: SPECIAL_MODES):
        return self.cmd.to_bytes(1, "little") + param.value.to_bytes(1, "little")

class APP_PING_SPECIAL_MODE(Command):
    """Set watch to ping special mode"""
    cmd = 218
    
    def process(self, data):
        m_data = {}
        m_data["q_green"] = int(data[2])
        m_data["q_red"]   = int(data[3])
        m_data["q_ir"]    = int(data[4])
        m_data["acc_x"]   = struct.unpack("h", data[6:8])[0]
        m_data["acc_y"]   = struct.unpack("h", data[8:10])[0]
        m_data["acc_z"]   = struct.unpack("h", data[10:12])[0]
        return m_data
    
    def str(self, data):
        return f"QGreen {data[q_green]}, QRed {data[q_red]}, QIRed{data[q_ired]}, Acc: X {data[acc_x]}, Y {data[acc_y]}, Z {data[acc_z]}"

class FW_SET_WAKE_UP(BaseCommand):
    """Periodic watch to device ping to keep the connection alive"""
    cmd = 125
    
    def process(self, data):
        m_data = {}
        m_data["battery"]      = int(data[2])
        m_data["ppg_size"]     = struct.unpack("H", data[3:5])[0]
        m_data["act_size"]     = struct.unpack("H", data[5:7])[0]
        m_data["hrv_size"]     = struct.unpack("H", data[7:9])[0]
        m_data["workout_size"] = struct.unpack("H", data[9:11])[0]
        m_data["sleep_size"]   = struct.unpack("H", data[11:13])[0]
        m_data["log_size"]     = struct.unpack("H", data[13:15])[0]
        return m_data

    def str(self, data):
        return (
            f'Ping! Battery: {data["battery"]}% PPG Size {data["ppg_size"]} '
            f'Act Size {data["act_size"]} HRV Size {data["hrv_size"]} '
            f'Workout Size {data["workout_size"]} Sleep Size {data["sleep_size"]} '
            f'Log Size {data["log_size"]}'
        )

class CMD_UNKNOWN(BaseCommand):
    """Still unknown"""
    cmd = 222
    
    def process(self, data):
        m_data = {}
        m_data[0] = int(data[0])
        m_data[1] = int(data[1])
        m_data[2] = int(data[2])
        m_data[3] = int(data[3])
        m_data[4] = int(data[4])
        m_data[5] = int(data[5])
        m_data[6] = int(data[6])
        m_data[7] = int(data[7])
        m_data[8] = int(data[8])
        m_data[9] = int(data[9])
        m_data[10] = int(data[10])
        m_data[11] = int(data[11])
        m_data[12] = int(data[12])
        m_data[13] = int(data[13])
        m_data[14] = int(data[14])
        m_data[15] = int(data[15])
        return m_data

    def str(self, data):
        return (data.values())

commands = (
    CMD_START_STREAMING_DATA,
    CMD_SET_NORMAL_MODE,
    CMD_ERASE_FROM_FILE,
    CMD_GET_FILE_SIZE,
    CMD_RESET,
    CMD_START_STREAMING_FILE,
    APP_CMD_UPDATE_TIME,
    CMD_START_STREAMING_FILE_WITH_SIZE,
    CMD_GET_ACTIVE_MODE,
    CMD_GET_BATTERY_LEVEL,
    CMD_GET_CURRENT_TIME,
    CMD_GET_CURRENT_FILE,
    CMD_GET_STREAMING_STATE,
    CMD_START_STREAMING_FILE_WITH_SIZE_OFFSET,
    APP_CMD_SET_PLAN,
    APP_CMD_GET_PLAN,
    APP_SET_PREV_USER_STATUS,
    APP_GET_PREV_USER_STATUS,
    APP_CMD_GET_VITAL_PARAM,
    APP_CMD_START_SPECIAL_MODE,
    APP_PING_SPECIAL_MODE,
    FW_SET_WAKE_UP,
    CMD_UNKNOWN,
)
