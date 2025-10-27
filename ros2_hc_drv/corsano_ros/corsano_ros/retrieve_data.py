from corsano_ros.corsano_driver import CorsanoDriver
from corsano_ros.parsers.activity_parser import ActivityParser, ActivityData
from corsano_ros.parsers.bioz_parser import BioZParser, BioZData
from corsano_ros.parsers.stress_parser import StressParser, StressData
from corsano_ros.parsers.accelerometer_parser import AccelerometerParser, AccelerometerData
from corsano_ros.corsano_enums import FileNames
from corsano_ros.commands import Command
from logging import error, warning
import time
from typing import Optional


def get_last_activity_data(
    driver: CorsanoDriver,
    cmd_get_file_size: Command,
    cmd_stream_file_with_size: Command,
    cmd_stream_file_with_size_offset: Command,
) -> Optional[ActivityData]:
    try:
        file = driver.execute(cmd_get_file_size.cmd, file=FileNames["Activity_file"])
        size: int = file["size"]
    except Exception as e:
        error(f"[corsano_ros::get_last_activity_data] Failed to get Activity file size: {e}")
        return None

    offset: int = size - 38

    if offset < 0:
        driver.execute(cmd_stream_file_with_size.cmd, file=FileNames["Activity_file"], size=38)
    else:
        driver.execute(
            cmd_stream_file_with_size_offset.cmd, file=FileNames["Activity_file"], size=38, offset=offset
        )

    time.sleep(1)
    buffer_data: bytes = driver.get_buffer().read()
    activity: Optional[ActivityData] = ActivityParser.parse(buffer_data)

    if activity is None:
        warning("[corsano_ros::get_last_activity_data] CRC check failed or invalid data")
        return None

    return activity


def get_last_bioz_data(
    driver: CorsanoDriver,
    cmd_get_file_size: Command,
    cmd_stream_file_with_size: Command,
    cmd_stream_file_with_size_offset: Command,
    file_name: str = FileNames["BioZ_file"],
) -> Optional[BioZData]:
    parser = BioZParser()

    try:
        file = driver.execute(cmd_get_file_size.cmd, file=file_name)
        size: int = file["size"]
    except Exception as e:
        error(f"[corsano_ros::get_last_bioz_data] Failed to get BioZ file size: {e}")
        return None

    if size == 0:
        warning("[corsano_ros::get_last_bioz_data] BioZ file is empty — check measurement plan.")
        return None

    offset: int = max(size - 1024, 0)

    try:
        if offset == 0:
            driver.execute(cmd_stream_file_with_size.cmd, file=file_name, size=size)
        else:
            driver.execute(
                cmd_stream_file_with_size_offset.cmd, file=file_name, size=size, offset=offset
            )
    except Exception as e:
        error(f"[corsano_ros::get_last_bioz_data] Failed to stream BioZ file: {e}")
        return None

    time.sleep(1)
    buffer_data: bytes = driver.get_buffer().read()
    if not buffer_data:
        warning("[corsano_ros::get_last_bioz_data] No data returned from buffer.")
        return None

    return parser.process_metric_array(buffer_data, 0, metric_id=0x3D, metric_size=len(buffer_data))


def get_last_stress_data(
    driver: CorsanoDriver,
    cmd_get_file_size: Command,
    cmd_stream_file_with_size: Command,
    cmd_stream_file_with_size_offset: Command,
    file_name: str = FileNames["STRESS_FILE"],
) -> Optional[StressData]:
    parser = StressParser()

    try:
        file = driver.execute(cmd_get_file_size.cmd, file=file_name)
        size: int = file["size"]
    except Exception as e:
        error(f"[corsano_ros::get_last_stress_data] Failed to get Stress file size: {e}")
        return None

    if size == 0:
        warning("[corsano_ros::get_last_stress_data] Stress file is empty — check measurement plan.")
        return None

    offset: int = max(size - 18, 0)

    try:
        driver.execute(cmd_stream_file_with_size_offset.cmd, file=file_name, size=18, offset=offset)
    except Exception as e:
        error(f"[corsano_ros::get_last_stress_data] Failed to stream Stress file: {e}")
        return None

    time.sleep(1)
    buffer_data: bytes = driver.get_buffer().read()
    if not buffer_data or len(buffer_data) < 18:
        warning("[corsano_ros::get_last_stress_data] No data returned or not enough bytes.")
        return None

    return parser.parse_last_record(buffer_data)


def get_last_accelerometer_data(
    driver: CorsanoDriver,
    cmd_get_file_size: Command,
    cmd_stream_file_with_size: Command,
    cmd_stream_file_with_size_offset: Command,
    file_name: str = FileNames["ACC_FILE"],
) -> Optional[AccelerometerData]:
    parser = AccelerometerParser()

    try:
        file = driver.execute(cmd_get_file_size.cmd, file=file_name)
        size: int = file["size"]
    except Exception as e:
        error(f"[corsano_ros::get_last_accelerometer_data] Failed to get accelerometer file size: {e}")
        return None

    if size == 0:
        warning("[corsano_ros::get_last_accelerometer_data] Accelerometer file is empty — check measurement plan.")
        return None

    offset: int = max(size - 1024, 0)

    try:
        if offset == 0:
            driver.execute(cmd_stream_file_with_size.cmd, file=file_name, size=size)
        else:
            driver.execute(
                cmd_stream_file_with_size_offset.cmd, file=file_name, size=size, offset=offset
            )
    except Exception as e:
        error(f"[corsano_ros::get_last_accelerometer_data] Failed to stream accelerometer file: {e}")
        return None

    time.sleep(1)
    buffer_data: bytes = driver.get_buffer().read()
    if not buffer_data:
        warning("[corsano_ros::get_last_accelerometer_data] No data returned from buffer.")
        return None

    return parser.process_metric_array(buffer_data, 0, metric_id=0x2B, metric_size=len(buffer_data))
