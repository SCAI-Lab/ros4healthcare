#!/usr/bin/env python3

import argparse
import sys
import traceback
from logging import error
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.utilities import remove_ros_args
from sensor_msgs.msg import Imu

from corsano_ros.corsano_driver import CorsanoDriver
from corsano_ros.helpers import load_config
from corsano_ros.retrieve_data import get_new_accelerometer_data
from corsano_ros.parsers.accelerometer_parser import AccelerometerData, AccelerometerParser


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Corsano ROS2 wrapper node")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to YAML config file containing adapter_name and mac_address_or_name.",
    )
    parser.add_argument(
        "--adapter-name",
        type=str,
        default=None,
        help="Bluetooth adapter name, e.g. hci0",
    )
    parser.add_argument(
        "--mac-address-or-name",
        type=str,
        default=None,
        help="Device MAC address or name. Defaults to '287-2B'.",
    )
    clean_args = remove_ros_args(sys.argv)
    return parser.parse_args(clean_args[1:])


class CorsanoRosWrapper(Node):
    """ROS 2 wrapper — streams accelerometer data, polling only when the ACC file grows."""

    _MAX_ACCEL_MS2 = 8.0 * 9.80665  # physical limit: ±8 g

    def __init__(self, driver: CorsanoDriver):
        super().__init__("corsano_wrapper")

        self.driver = driver
        self.address = driver.address
        self.adapter_name = driver.adapter_name

        self.get_logger().info(
            f"Using adapter: {self.adapter_name}, address: {self.address}"
        )

        # --- Map commands ---
        type_to_command = {type(v).__name__: v for v in driver.commands.values()}
        required = [
            "CMD_GET_FILE_SIZE",
            "CMD_START_STREAMING_FILE_WITH_SIZE",
            "CMD_START_STREAMING_FILE_WITH_SIZE_OFFSET",
        ]
        for name in required:
            if name not in type_to_command:
                raise RuntimeError(f"Driver is missing required command: {name}")
        self.cmd_get_file_size = type_to_command["CMD_GET_FILE_SIZE"]
        self.cmd_stream_file_with_size = type_to_command["CMD_START_STREAMING_FILE_WITH_SIZE"]
        self.cmd_stream_file_with_size_offset = type_to_command["CMD_START_STREAMING_FILE_WITH_SIZE_OFFSET"]

        # --- ROS publisher ---
        self.accel_pub = self.create_publisher(Imu, "corsano/acceleration", 10)

        # None = first poll, captures current file position and skips historical data.
        self._last_acc_size: Optional[int] = None

        # ACC index-based timestamping
        self._acc_t0_ms: Optional[float] = None    # wall-clock ms when first chunk arrived
        self._acc_first_index: Optional[int] = None
        self._acc_prev_index: Optional[int] = None
        self._acc_laps: int = 0                    # full 256-chunk rollovers since t0

        self._poll_timer = self.create_timer(2.0, self._poll_loop)

        self.get_logger().info("CorsanoWrapper node initialized and ready.")

    # -------------------- Callbacks --------------------

    def _acc_timestamp_ms(self, index: int) -> float:
        """Return the wall-clock timestamp (ms) for a chunk given its 0-255 rolling index."""
        import time as _time
        now_ms = _time.time() * 1000.0
        if self._acc_t0_ms is None:
            self._acc_t0_ms = now_ms
            self._acc_first_index = index
            self._acc_prev_index = index
            self._acc_laps = 0
            return self._acc_t0_ms

        # Detect rollover: index jumped backward by more than half the range.
        prev = self._acc_prev_index
        if prev is not None and index < prev and (prev - index) > 128:
            self._acc_laps += 1
        self._acc_prev_index = index

        effective = self._acc_laps * 256 + (index - self._acc_first_index) % 256
        return self._acc_t0_ms + effective * 1000.0

    def _publish_acceleration(self, acceleration: AccelerometerData):
        """Validate and publish one packet of accelerometer samples."""
        import numpy as np
        if acceleration.x_values.size == 0:
            return

        limit = self._MAX_ACCEL_MS2
        any_bad = (
            (np.abs(acceleration.x_values) > limit) |
            (np.abs(acceleration.y_values) > limit) |
            (np.abs(acceleration.z_values) > limit)
        )
        n_total = acceleration.x_values.size
        if any_bad.any():
            n_publish = int(np.argmax(any_bad))
            if n_publish == 0:
                self.get_logger().warning(
                    f"[Accel] First sample out of range — skipping packet index={acceleration.index}"
                )
                return
            self.get_logger().warning(
                f"[Accel] Truncating at sample {n_publish}/{n_total} "
                f"(index={acceleration.index})"
            )
        else:
            n_publish = n_total

        chunk_ts_ms = self._acc_timestamp_ms(acceleration.index)
        sample_period_ms = 1000.0 / AccelerometerParser.ACC_SR
        for i in range(n_publish):
            sample_ts_ms = chunk_ts_ms + i * sample_period_ms
            msg = Imu()
            msg.header.frame_id = "corsano_imu"
            msg.header.stamp.sec = int(sample_ts_ms / 1000)
            msg.header.stamp.nanosec = int((sample_ts_ms % 1000) * 1e6)
            msg.linear_acceleration.x = float(acceleration.x_values[i])
            msg.linear_acceleration.y = float(acceleration.y_values[i])
            msg.linear_acceleration.z = float(acceleration.z_values[i])
            msg.orientation_covariance[0] = -1.0
            msg.angular_velocity_covariance[0] = -1.0
            self.accel_pub.publish(msg)

        self.get_logger().info(
            f"[Accel] published {n_publish}/{n_total} samples "
            f"index={acceleration.index} "
            f"t0={chunk_ts_ms:.0f} ms"
        )

    # -------------------- Poll loop --------------------

    def _poll_loop(self):
        if not self.driver.connected:
            return

        try:
            chunks, new_size = get_new_accelerometer_data(
                self.driver,
                self.cmd_get_file_size,
                self.cmd_stream_file_with_size,
                self.cmd_stream_file_with_size_offset,
                self._last_acc_size,
            )
            self._last_acc_size = new_size
            for chunk in chunks:
                self._publish_acceleration(chunk)
        except Exception as e:
            self.get_logger().error(f"[ACC] {type(e).__name__}: {e}")
            traceback.print_exc()

    # -------------------- Cleanup --------------------

    def destroy_node(self):
        self.get_logger().info("Shutting down CorsanoWrapper node...")
        try:
            if self.driver and self.driver.peripheral and self.driver.peripheral.is_connected():
                self.driver.peripheral.disconnect()
        except Exception as e:
            self.get_logger().warning(f"Error during disconnect: {e}")
        super().destroy_node()


def main(args=None):
    cli_args = parse_args()
    adapter_name = cli_args.adapter_name
    mac_address_or_name = cli_args.mac_address_or_name

    if cli_args.config:
        cfg = load_config(cli_args.config)
        adapter_name = adapter_name or cfg.get("adapter_name")
        mac_address_or_name = mac_address_or_name or cfg.get("mac_address_or_name")

    adapter_name = adapter_name or "hci0"
    mac_address_or_name = mac_address_or_name or "287-2B"

    rclpy.init(args=args)
    node = None
    try:
        with CorsanoDriver(name_or_address=mac_address_or_name, adapter_name=adapter_name) as driver:
            node = CorsanoRosWrapper(driver)
            rclpy.spin(node)
    except KeyboardInterrupt:
        error("[CorsanoWrapper] User interrupt received — shutting down cleanly.")
    except rclpy.executors.ExternalShutdownException:
        error("[CorsanoWrapper] External ROS 2 shutdown requested.")
    except Exception as e:
        error(f"[CorsanoWrapper] Unhandled exception: {type(e).__name__}: {e}")
        traceback.print_exc()
    finally:
        if node is not None:
            node.destroy_node()
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except rclpy._rclpy_pybind11.RCLError:
            pass
        except Exception as e:
            error(f"[CorsanoWrapper] Error during shutdown: {e}")


if __name__ == "__main__":
    main()
