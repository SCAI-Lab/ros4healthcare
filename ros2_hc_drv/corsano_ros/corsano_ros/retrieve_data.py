from corsano_ros.corsano_driver import CorsanoDriver
from corsano_ros.parsers.activity_parser import ActivityParser
from corsano_ros.parsers.bioz_parser import BioZParser
from corsano_ros.parsers.stress_parser import StressParser
from corsano_ros.parsers.accelerometer_parser import AccelerometerParser
from corsano_ros.corsano_enums import FileNames
import time


def connect(mac_address: str, adapter_address: str):
    """
    Connect to a Corsano device via BLE.

    Returns:
        Tuple[CorsanoDriver, bool]: (interface instance, success flag)
    """
    cors = CorsanoDriver(mac_address, adapter_address)
    if cors.connect():
        return cors, True
    return None, False


def reconnect(cors: CorsanoDriver):
    """
    Attempt to reconnect a Corsano device.

    Returns:
        Tuple[CorsanoDriver, bool]: (interface instance, connected flag)
    """
    is_connected = cors.reconnect()
    return cors, is_connected

import time
from typing import Optional, Tuple

def get_last_activity_data(cors: CorsanoDriver, cmd_get_file_size, 
                           cmd_stream_file_with_size, cmd_stream_file_with_size_offset
                          ) -> Optional[Tuple[int, int, float, int, int, int]]:
    """
    Retrieve the latest activity record from the Corsano device.

    Returns:
        Tuple[int, int, float, int, int, int]: hr_filtered, hr_quality, rr_filtered, rr_quality, battery, stress
        Returns None if no valid data is found.
    """
    debug = False

    size = cors.execute(cmd_get_file_size.cmd, file=FileNames["Activity_file"])["size"]
    offset = size - 38 

    if offset < 0 :
        data = cors.execute(cmd_stream_file_with_size.cmd, file=FileNames["Activity_file"], size = 38)
        if debug:
            print('choice 1 offset')
    else: 
        data = cors.execute(cmd_stream_file_with_size_offset.cmd, file=FileNames["Activity_file"], size = 38, offset= offset)
        if debug:
            print('choice 2 offset')
        
    time.sleep(1)
    buffer_data = cors.get_buffer().read()
    activity = ActivityParser.parse(buffer_data)
    print(f"Activity {activity}")


    if activity is None:
        if debug:
            print("[Warning] CRC check failed or invalid data")
        return None

    return activity



def get_last_bioz_data(cors: CorsanoDriver, cmd_get_file_size, cmd_stream_file_with_size, 
                       cmd_stream_file_with_size_offset, file_name=FileNames["BioZ_file"], callback=None) -> bool:
    """
    Stream BioZ (EDA) data from the device using BioZParser.

    Calls callback(timestamp_ms, values, normalized_values) for each record.
    """
    parser = BioZParser(callback=callback)

    try:
        file = cors.execute(cmd_get_file_size.cmd, file=file_name)
        size = file["size"]
    except Exception as e:
        print(f"Failed to get BioZ file size: {e}")
        return False

    if size == 0:
        print("BioZ file is empty — check measurement plan.")
        return False

    offset = max(size - 1024, 0)

    try:
        if offset == 0:
            cors.execute(cmd_stream_file_with_size.cmd, file=file_name, size=size)
        else:
            cors.execute(cmd_stream_file_with_size_offset.cmd, file=file_name, size=size, offset=offset)
    except Exception as e:
        print(f"Failed to stream BioZ file: {e}")
        return False

    time.sleep(1)
    buffer_data = cors.get_buffer().read()
    if not buffer_data:
        print("No data returned from buffer.")
        return False

    parser.process_metric_array(buffer_data, 0, metric_id=0x3D, metric_size=len(buffer_data))
    return True


def get_last_stress_data(cors: CorsanoDriver, cmd_get_file_size, cmd_stream_file_with_size, 
                         cmd_stream_file_with_size_offset, file_name=FileNames["STRESS_FILE"], callback=None) -> bool:
    """
    Read only the last Stress record (18 bytes) from the Corsano device.
    """
    parser = StressParser(callback=callback)

    try:
        file = cors.execute(cmd_get_file_size.cmd, file=file_name)
        size = file["size"]
        print(f"Stress file size: {size}")
    except Exception as e:
        print(f"Failed to get Stress file size: {e}")
        return False

    if size == 0:
        print("Stress file is empty — check measurement plan.")
        return False

    offset = max(size - 18, 0)

    try:
        cors.execute(cmd_stream_file_with_size_offset.cmd, file=file_name, size=18, offset=offset)
    except Exception as e:
        print(f"Failed to stream Stress file: {e}")
        return False

    time.sleep(1)
    buffer_data = cors.get_buffer().read()
    if not buffer_data or len(buffer_data) < 18:
        print("No data returned or not enough bytes.")
        return False

    parser.parse_last_record(buffer_data, print_raw=True)
    return True


def get_last_accelerometer_data(cors: CorsanoDriver, cmd_get_file_size, cmd_stream_file_with_size, 
                                cmd_stream_file_with_size_offset, file_name=FileNames["ACC_FILE"], callback=None) -> bool:
    """
    Stream accelerometer data from the device using AccelerometerParser.

    Calls callback(timestamp_ms, x_values, y_values, z_values) for each record.
    """
    parser = AccelerometerParser(callback=callback)

    try:
        file = cors.execute(cmd_get_file_size.cmd, file=file_name)
        size = file["size"]
    except Exception as e:
        print(f"Failed to get accelerometer file size: {e}")
        return False

    if size == 0:
        print("Accelerometer file is empty — check measurement plan.")
        return False

    offset = max(size - 1024, 0)

    try:
        if offset == 0:
            cors.execute(cmd_stream_file_with_size.cmd, file=file_name, size=size)
        else:
            cors.execute(cmd_stream_file_with_size_offset.cmd, file=file_name, size=size, offset=offset)
    except Exception as e:
        print(f"Failed to stream accelerometer file: {e}")
        return False

    time.sleep(1)
    buffer_data = cors.get_buffer().read()
    if not buffer_data:
        print("No data returned from buffer.")
        return False

    parser.process_metric_array(buffer_data, 0, metric_id=0x2B, metric_size=len(buffer_data))
    return True
