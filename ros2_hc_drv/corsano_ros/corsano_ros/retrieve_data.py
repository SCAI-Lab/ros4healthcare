from corsano_ros.corsano_driver import CorsanoDriver
from corsano_ros.parsers.activity_parser import ActivityParser, ActivityData
from corsano_ros.parsers.bioz_parser import BioZParser, BioZData
from corsano_ros.parsers.stress_parser import StressParser, StressData
from corsano_ros.parsers.accelerometer_parser import (
    AccelerometerParser,
    AccelerometerData,
)
from corsano_ros.corsano_enums import FileNames
from corsano_ros.commands import Command
from dataclasses import dataclass
from logging import error, warning
import time
from typing import List, Optional, Tuple
import sys


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
        error(
            f"[corsano_ros::get_last_activity_data] Failed to get Activity file size: {e}"
        )
        return None

    offset: int = size - 38

    if offset < 0:
        driver.execute(
            cmd_stream_file_with_size.cmd, file=FileNames["Activity_file"], size=38
        )
    else:
        driver.execute(
            cmd_stream_file_with_size_offset.cmd,
            file=FileNames["Activity_file"],
            size=38,
            offset=offset,
        )

    time.sleep(1.0)
    buffer_data: bytes = driver.get_buffer().read()
    if not buffer_data or len(buffer_data) < ActivityParser.STRUCT_SIZE + 1:
        warning(
            "[corsano_ros::get_last_activity_data] No data returned or not enough bytes."
        )
        return None

    activity: Optional[ActivityData] = ActivityParser.parse(buffer_data)

    if activity is None:
        warning(
            "[corsano_ros::get_last_activity_data] CRC check failed or invalid data"
        )
        return None

    return activity


def dump_bioz_file(
    driver: CorsanoDriver,
    cmd_get_file_size: Command,
    cmd_stream_file_with_size: Command,
    cmd_stream_file_with_size_offset: Command,
    output_path: str,
    file_name: str = FileNames.BioZ_file,
    chunk_size: int = 2048,
) -> bool:
    """
    Download the entire BioZ file from the device and write it to a local file.
    Returns True on success.
    """

    # --- Get total size ---
    try:
        file_info = driver.execute(cmd_get_file_size.cmd, file=file_name)
        size: int = file_info["size"]
        print(f"BioZ file size: {size} bytes")
    except Exception as e:
        error(f"[dump_bioz_file] Failed to get BioZ file size: {e}")
        return False

    if size == 0:
        warning("[dump_bioz_file] BioZ file is empty.")
        return False

    # --- Open local file ---
    with open(output_path, "wb") as f_out:

        bytes_downloaded = 0

        while bytes_downloaded < size:
            try:
                remaining = size - bytes_downloaded
                read_size = min(chunk_size, remaining)

                # choose correct command
                if bytes_downloaded == 0:
                    driver.execute(
                        cmd_stream_file_with_size.cmd, file=file_name, size=read_size
                    )
                else:
                    driver.execute(
                        cmd_stream_file_with_size_offset.cmd,
                        file=file_name,
                        size=read_size,
                        offset=bytes_downloaded,
                    )

                # give the buffer time to fill
                time.sleep(0.1)
                data = driver.get_buffer().read()

                if not data:
                    error("[dump_bioz_file] No data returned from device. Retrying...")
                else:

                    f_out.write(data)
                    bytes_downloaded += len(data)

                    print(f"Downloaded {bytes_downloaded}/{size} bytes")
            except Exception as e:
                error(f"[dump_bioz_file] Error downloading the file, retrying... {e}")
        print(f"[dump_bioz_file] File successfully saved to: {output_path}")
        sys.exit()


def get_last_bioz_data(
    driver: CorsanoDriver,
    cmd_get_file_size: Command,
    cmd_stream_file_with_size: Command,
    cmd_stream_file_with_size_offset: Command,
    file_name: str = FileNames.BioZ_file,
    chunk_size: int = 2048,
) -> Optional[BioZData]:
    """
    Fetch the last portion of the BioZ file and decode the last BioZ record.
    Returns a BioZData object containing record_index, quality, and 25 measurements.
    """
    parser = BioZParser()

    # --- Get file size ---
    try:
        file_info = driver.execute(cmd_get_file_size.cmd, file=file_name)
        size: int = file_info["size"]
        print(f"BioZ file size: {size} bytes")
    except Exception as e:
        error(f"[get_last_bioz_data] Failed to get BioZ file size: {e}")
        return None

    if size == 0:
        warning("[get_last_bioz_data] BioZ file is empty.")
        return None

    # --- Download last chunk of file ---
    offset = max(0, size - chunk_size)
    read_size = min(chunk_size, size - offset)
    try:
        if offset == 0:
            driver.execute(
                cmd_stream_file_with_size.cmd, file=file_name, size=read_size
            )
        else:
            driver.execute(
                cmd_stream_file_with_size_offset.cmd,
                file=file_name,
                size=read_size,
                offset=offset,
            )
    except Exception as e:
        error(f"[get_last_bioz_data] Failed to stream BioZ file: {e}")
        return None

    time.sleep(0.5)  # allow buffer to fill
    buffer_data = driver.get_buffer().read()

    if not buffer_data:
        warning("[get_last_bioz_data] No data returned from buffer.")
        return None

    # --- Parse packets and get last ---
    parser.parse_packets(buffer_data)
    last_packet = parser.get_last_packet()
    if last_packet is None:
        print("[get_last_bioz_data] No BioZ packets found in buffer.")
        return None

    print(
        f"[get_last_bioz_data] Decoded last BioZ record: "
        f"timestamp={last_packet.timestamp}, "
        f"index={last_packet.record_index}, "
        f"measurements={last_packet.values}"
    )

    return last_packet


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
        error(
            f"[corsano_ros::get_last_stress_data] Failed to get Stress file size: {e}"
        )
        return None

    if size == 0:
        warning(
            "[corsano_ros::get_last_stress_data] Stress file is empty — check measurement plan."
        )
        return None

    offset: int = max(size - 18, 0)

    try:
        driver.execute(
            cmd_stream_file_with_size_offset.cmd, file=file_name, size=18, offset=offset
        )
    except Exception as e:
        error(f"[corsano_ros::get_last_stress_data] Failed to stream Stress file: {e}")
        return None

    time.sleep(1)
    buffer_data: bytes = driver.get_buffer().read()
    if not buffer_data or len(buffer_data) < 18:
        warning(
            "[corsano_ros::get_last_stress_data] No data returned or not enough bytes."
        )
        return None

    stress = parser.parse_last_record(buffer_data)
    print(stress)
    return stress


@dataclass
class AccCalibration:
    """Links a device-clock activity timestamp to an ACC file position.

    activity_ts_s  -- Unix timestamp (seconds) from the most recent activity record.
                      This comes from the device's own RTC, not the host clock.
    acc_file_pos   -- ACC file size read immediately after the activity record.
                      A chunk at file position P was written at:
                          T = activity_ts_s + (P - acc_file_pos) / 205.0
    """
    activity_ts_s: float
    acc_file_pos: int


def get_acc_calibration(
    driver: CorsanoDriver,
    cmd_get_file_size: Command,
    cmd_stream_file_with_size: Command,
    cmd_stream_file_with_size_offset: Command,
) -> Optional[AccCalibration]:
    """Read the latest activity record and ACC file size to build a timestamp anchor."""
    activity = get_last_activity_data(
        driver, cmd_get_file_size, cmd_stream_file_with_size, cmd_stream_file_with_size_offset
    )
    if activity is None:
        warning("[corsano_ros::get_acc_calibration] Could not read activity record.")
        return None
    try:
        result = driver.execute(cmd_get_file_size.cmd, file=FileNames["ACC_FILE"])
        if result is None:
            return None
        cal = AccCalibration(
            activity_ts_s=activity.timestamp.timestamp(),
            acc_file_pos=result["size"],
        )
        warning(
            f"[corsano_ros::get_acc_calibration] anchor: "
            f"activity_ts={cal.activity_ts_s:.3f} s  acc_pos={cal.acc_file_pos} bytes"
        )
        return cal
    except Exception as e:
        error(f"[corsano_ros::get_acc_calibration] Failed to read ACC file size: {e}")
        return None



def get_new_accelerometer_data(
    driver: CorsanoDriver,
    cmd_get_file_size: Command,
    cmd_stream_file_with_size: Command,
    cmd_stream_file_with_size_offset: Command,
    last_size: Optional[int],
    file_name: str = FileNames["ACC_FILE"],
    calibration: Optional[AccCalibration] = None,
) -> Tuple[List[AccelerometerData], int]:
    """
    Stream only the bytes added to the ACC file since last_size.

    Pass last_size=None on the first call: the function captures the current
    end-of-file position, skips all historical data, and returns ([], current_size).
    On subsequent calls pass the returned size to receive only new chunks.

    Returns (parsed_chunks, updated_file_position).
    On error or no new data returns ([], last_size) so the caller can retry next poll.
    If the file shrank (device erased it) returns ([], 0) to reset.
    """
    try:
        result = driver.execute(cmd_get_file_size.cmd, file=file_name)
        if result is None:
            warning("[corsano_ros::get_new_accelerometer_data] CMD_GET_FILE_SIZE returned None")
            return [], (0 if last_size is None else last_size)
        current_size: int = result["size"]
    except Exception as e:
        error(f"[corsano_ros::get_new_accelerometer_data] Failed to get file size: {e}")
        return [], (0 if last_size is None else last_size)

    if last_size is None:
        return [], current_size

    if current_size < last_size:
        warning("[corsano_ros::get_new_accelerometer_data] ACC file shrank — resetting position.")
        return [], current_size

    # No new data yet.
    if current_size == last_size:
        return [], last_size

    new_bytes = min(current_size - last_size, 2048)

    try:
        t_cmd_ms: float = time.time() * 1000.0
        if last_size == 0:
            driver.execute(cmd_stream_file_with_size.cmd, file=file_name, size=new_bytes)
        else:
            driver.execute(
                cmd_stream_file_with_size_offset.cmd,
                file=file_name,
                size=new_bytes,
                offset=last_size,
            )
    except Exception as e:
        error(f"[corsano_ros::get_new_accelerometer_data] Failed to stream: {e}")
        return [], last_size

    # Wait until the buffer stops growing (transfer complete) or the deadline expires.
    _SETTLE_TICKS = 3
    _MAX_WAIT = 5.0
    deadline = time.time() + _MAX_WAIT
    prev_buf_size = -1
    stable = 0
    while time.time() < deadline:
        time.sleep(0.05)
        if driver.buffer is None:
            break
        driver.buffer.seek(0, 2)
        cur_buf_size = driver.buffer.tell()
        if cur_buf_size == prev_buf_size:
            stable += 1
            if stable >= _SETTLE_TICKS:
                break
        else:
            stable = 0
            prev_buf_size = cur_buf_size

    buf = driver.get_buffer() if driver.buffer else None
    buffer_data: bytes = buf.read() if buf is not None else b""
    if not buffer_data:
        warning("[corsano_ros::get_new_accelerometer_data] No data returned from buffer.")
        return [], last_size

    # Parse all complete 205-byte chunks found in the new bytes.
    # Layout: [8-byte HR header] [pds-byte packet data] [1-byte 0x4F separator]
    FILE_HEADER_SIZE = 8
    HR_MAGIC = b"\x48\x52\xc8\x00\x0f\x2b"
    sample_period_ms = 1000.0 / AccelerometerParser.ACC_SR
    parser = AccelerometerParser()

    chunk_spans: List[tuple] = []
    pos = 0
    while True:
        start = buffer_data.find(HR_MAGIC, pos)
        if start < 0:
            break
        if len(buffer_data) - start < FILE_HEADER_SIZE + 4:
            break
        pds = int.from_bytes(buffer_data[start + 6:start + 8], "little")
        if not (10 <= pds <= 512):
            pos = start + 1
            continue
        chunk_end = start + FILE_HEADER_SIZE + pds
        if chunk_end > len(buffer_data):
            break
        chunk_spans.append((start, pds))
        pos = chunk_end + 1  # skip 0x4F separator

    if not chunk_spans:
        warning("[corsano_ros::get_new_accelerometer_data] No complete HR chunks found.")
        return [], last_size

    n_chunks = len(chunk_spans)
    results: List[AccelerometerData] = []
    for i, (start, pds) in enumerate(chunk_spans):
        declared_samples = (pds - 4) // 6
        if calibration is not None:
            # File position of this chunk's HR magic in the ACC file.
            # A chunk is written when its last sample is captured, so the first
            # sample is (declared_samples - 1) periods earlier.
            chunk_file_pos = last_size + start
            elapsed_s = (chunk_file_pos - calibration.acc_file_pos) / 205.0
            parser.acc_time = (
                (calibration.activity_ts_s + elapsed_s) * 1000.0
                - (declared_samples - 1) * sample_period_ms
            )
        else:
            chunks_from_end = n_chunks - 1 - i
            parser.acc_time = (
                t_cmd_ms
                - (declared_samples - 1) * sample_period_ms
                - chunks_from_end * 1000.0
            )
        data = parser.process_metric_array(
            buffer_data[start:], FILE_HEADER_SIZE, metric_id=0x2B, metric_size=pds
        )
        if data is not None:
            results.append(data)

    # Advance the file position past all consumed chunks.
    last_start, last_pds = chunk_spans[-1]
    new_last_size = last_size + last_start + FILE_HEADER_SIZE + last_pds + 1
    return results, new_last_size


def get_new_activity_data(
    driver: CorsanoDriver,
    cmd_get_file_size: Command,
    cmd_stream_file_with_size: Command,
    cmd_stream_file_with_size_offset: Command,
    last_size: Optional[int],
    file_name: FileNames = FileNames["Activity_file"],
) -> Tuple[List[ActivityData], int]:
    """Stream only new complete activity records since last_size.

    Pass last_size=None on the first call to skip history.
    Returns (new_records, updated_file_position).
    """
    RECORD_SIZE = ActivityParser.STRUCT_SIZE + 1  # 38 bytes (37 data + CRC)

    try:
        result = driver.execute(cmd_get_file_size.cmd, file=file_name)
        if result is None:
            return [], (0 if last_size is None else last_size)
        current_size: int = result["size"]
    except Exception as e:
        error(f"[corsano_ros::get_new_activity_data] Failed to get file size: {e}")
        return [], (0 if last_size is None else last_size)

    if last_size is None:
        return [], current_size

    if current_size < last_size:
        warning("[corsano_ros::get_new_activity_data] Activity file shrank — resetting position.")
        return [], current_size

    new_bytes = current_size - last_size
    n_complete = new_bytes // RECORD_SIZE
    if n_complete == 0:
        return [], last_size

    read_size = n_complete * RECORD_SIZE
    try:
        if last_size == 0:
            driver.execute(cmd_stream_file_with_size.cmd, file=file_name, size=read_size)
        else:
            driver.execute(
                cmd_stream_file_with_size_offset.cmd,
                file=file_name,
                size=read_size,
                offset=last_size,
            )
    except Exception as e:
        error(f"[corsano_ros::get_new_activity_data] Failed to stream: {e}")
        return [], last_size

    deadline = time.time() + 5.0
    prev_buf_size, stable = -1, 0
    while time.time() < deadline:
        time.sleep(0.05)
        if driver.buffer is None:
            break
        driver.buffer.seek(0, 2)
        cur = driver.buffer.tell()
        if cur == prev_buf_size:
            stable += 1
            if stable >= 3:
                break
        else:
            stable, prev_buf_size = 0, cur

    buf = driver.get_buffer() if driver.buffer else None
    buffer_data = buf.read() if buf is not None else b""
    if not buffer_data:
        warning("[corsano_ros::get_new_activity_data] No data returned from buffer.")
        return [], last_size

    results: List[ActivityData] = []
    for i in range(len(buffer_data) // RECORD_SIZE):
        record_bytes = buffer_data[i * RECORD_SIZE : (i + 1) * RECORD_SIZE]
        parsed = ActivityParser.parse(record_bytes)
        if parsed is not None:
            results.append(parsed)

    new_last_size = last_size + (len(buffer_data) // RECORD_SIZE) * RECORD_SIZE
    return results, new_last_size


def get_new_bioz_data(
    driver: CorsanoDriver,
    cmd_get_file_size: Command,
    cmd_stream_file_with_size: Command,
    cmd_stream_file_with_size_offset: Command,
    last_size: Optional[int],
    file_name: FileNames = FileNames.BioZ_file,
) -> Tuple[List[BioZData], int]:
    """Stream only new bytes from the BioZ file and parse all complete OHR packets.

    Pass last_size=None on the first call to skip history.
    Returns (new_packets, updated_file_position).
    """
    try:
        result = driver.execute(cmd_get_file_size.cmd, file=file_name)
        if result is None:
            return [], (0 if last_size is None else last_size)
        current_size: int = result["size"]
    except Exception as e:
        error(f"[corsano_ros::get_new_bioz_data] Failed to get file size: {e}")
        return [], (0 if last_size is None else last_size)

    if last_size is None:
        return [], current_size

    if current_size < last_size:
        warning("[corsano_ros::get_new_bioz_data] BioZ file shrank — resetting position.")
        return [], current_size

    if current_size == last_size:
        return [], last_size

    new_bytes = current_size - last_size
    try:
        if last_size == 0:
            driver.execute(cmd_stream_file_with_size.cmd, file=file_name, size=new_bytes)
        else:
            driver.execute(
                cmd_stream_file_with_size_offset.cmd,
                file=file_name,
                size=new_bytes,
                offset=last_size,
            )
    except Exception as e:
        error(f"[corsano_ros::get_new_bioz_data] Failed to stream: {e}")
        return [], last_size

    deadline = time.time() + 5.0
    prev_buf_size, stable = -1, 0
    while time.time() < deadline:
        time.sleep(0.05)
        if driver.buffer is None:
            break
        driver.buffer.seek(0, 2)
        cur = driver.buffer.tell()
        if cur == prev_buf_size:
            stable += 1
            if stable >= 3:
                break
        else:
            stable, prev_buf_size = 0, cur

    buf = driver.get_buffer() if driver.buffer else None
    buffer_data = buf.read() if buf is not None else b""
    if not buffer_data:
        warning("[corsano_ros::get_new_bioz_data] No data returned from buffer.")
        return [], last_size

    parser = BioZParser()
    packets = parser.parse_packets(buffer_data)

    if not packets:
        return [], last_size

    new_last_size = last_size + new_bytes
    return packets, new_last_size
