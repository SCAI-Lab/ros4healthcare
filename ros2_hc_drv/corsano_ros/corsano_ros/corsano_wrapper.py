#!/usr/bin/env python3

import argparse
from logging import error
import rclpy
from rclpy.node import Node
import numpy as np
from std_msgs.msg import Int32, Float32, Float32MultiArray
import sys
from rclpy.utilities import remove_ros_args

from corsano_ros.corsano_driver import CorsanoDriver
from corsano_ros.helpers import load_config
from corsano_ros.retrieve_data import (
    get_last_activity_data,
    get_last_bioz_data,
    get_last_stress_data,
    get_last_accelerometer_data,
)
from corsano_ros.commands import (
    VENDOR_CMD_FD53,
    VENDOR_CMD_FD7D,
    VENDOR_CMD_FC2D,
    VENDOR_CMD_FD57,
)
from corsano_ros.parsers.accelerometer_parser import AccelerometerData
from corsano_ros.parsers.activity_parser import ActivityData
from corsano_ros.parsers.bioz_parser import BioZData
from corsano_ros.parsers.stress_parser import StressData

def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Corsano ROS2 wrapper node")

    parser.add_argument(
        "--config",
        type=str,
        help="Path to YAML config file containing adapter_name and mac_address_or_name."
    )
    parser.add_argument(
        "--adapter-name",
        type=str,
        default=None,
        help="Bluetooth adapter name, e.g. hci0"
    )
    parser.add_argument(
        "--mac-address-or-name",
        type=str,
        default=None,
        help="Device MAC address or name. If omitted, will look for a device named '287-2B'."
    )
    clean_args = remove_ros_args(sys.argv)
    return parser.parse_args(clean_args[1:])

class CorsanoWrapper(Node):
    """ROS 2 wrapper around the CorsanoDriver BLE interface."""


    def __init__(self, driver: CorsanoDriver):
        super().__init__('corsano_wrapper')

        self.driver = driver
        self.address = self.driver.address
        self.adapter_name = self.driver.adapter_name

        self.get_logger().info(f"Using adapter: {self.adapter_name}, address: {self.address}")

        # --- Map commands ---
        type_to_command = {type(v).__name__: v for v in self.driver.commands.values()}
        self.cmd_get_file_size = type_to_command.get("CMD_GET_FILE_SIZE")
        self.cmd_stream_file_with_size = type_to_command.get("CMD_START_STREAMING_FILE_WITH_SIZE")
        self.cmd_stream_file_with_size_offset = type_to_command.get("CMD_START_STREAMING_FILE_WITH_SIZE_OFFSET")

        # --- Enable BioZ and sensor streaming ---
        self._enable_bioz_streaming()

        # --- ROS publishers ---
        self.hr_pub = self.create_publisher(Int32, 'hr', 10)
        self.rr_pub = self.create_publisher(Int32, 'rr', 10)
        self.bioz_pub = self.create_publisher(Float32MultiArray, 'eda', 10)
        self.accel_pub = self.create_publisher(Float32MultiArray, 'acc', 10)

        # --- Timer for periodic polling ---
        self.acceleration_timer = self.create_timer(0.1, self.request_accelerometer_data)
        self.activity_timer = self.create_timer(0.1, self.request_activity_data)
        self.bioz_timer = self.create_timer(0.001, self.request_bioz_data)
        self.stress_timer = self.create_timer(0.1, self.request_stress_data)

        self.get_logger().info("CorsanoWrapper node initialized and ready.")


    def _enable_bioz_streaming(self):
        """Enable BioZ recording via vendor commands."""
        self.get_logger().info("Enabling BioZ streaming...")
        for cmd_class in [VENDOR_CMD_FD53, VENDOR_CMD_FD7D, VENDOR_CMD_FC2D, VENDOR_CMD_FD57]:
            try:
                cmd = cmd_class()
                packet = cmd.execute()
                self.driver.write(packet)
                self.get_logger().info(f"Sent {cmd_class.__name__} ({packet.hex()})")
            except Exception as e:
                self.get_logger().warn(f"Failed to send {cmd_class.__name__}: {e}")

    def acceleration_callback(self, acceleration: AccelerometerData):
        """Callback for accelerometer data."""
        print(f"Acceleration: {acceleration}")
        if acceleration.x_values.size > 0:
            msg = Float32MultiArray()
            msg.data = [
                float(acceleration.x_values[-1]),
                float(acceleration.y_values[-1]),
                float(acceleration.z_values[-1]),
            ]
            self.accel_pub.publish(msg)
            self.get_logger().debug(
                f"Accel: X={msg.data[0]:.3f}, Y={msg.data[1]:.3f}, Z={msg.data[2]:.3f}"
            )

    def request_accelerometer_data(self):
        acceleration = get_last_accelerometer_data(
            self.driver,
            self.cmd_get_file_size,
            self.cmd_stream_file_with_size,
            self.cmd_stream_file_with_size_offset,
        )
        if acceleration is not None:
            self.acceleration_callback(acceleration=acceleration)

    def activity_callback(self, activity: ActivityData):
        """Callback for incoming EDA data."""
        print(f"activity: {activity}")
        if activity is not None:
            self.hr_pub.publish(Int32(data=activity.hr_filtered))
            self.rr_pub.publish(Int32(data=int(activity.rr_filtered)))
    
    def request_activity_data(self):
        activity = get_last_activity_data(
            self.driver,
            self.cmd_get_file_size,
            self.cmd_stream_file_with_size,
            self.cmd_stream_file_with_size_offset,
        )
        if activity is not None:
            self.activity_callback(activity=activity)


    def bioz_callback(self, bioz: BioZData):
        """Callback for incoming EDA data."""
        print(f"bioz {bioz}")
        if bioz.eda_us.size > 0 and not np.isnan(bioz.eda_us[-1]):
            msg = Float32MultiArray()
            msg.data = bioz.eda_us.astype(float).tolist()
            self.bioz_pub.publish(msg)

            
    def request_bioz_data(self):
        bioz= get_last_bioz_data(
            self.driver,
            self.cmd_get_file_size,
            self.cmd_stream_file_with_size,
            self.cmd_stream_file_with_size_offset,
        )
        if bioz is not None:
            self.bioz_callback(bioz)

    def stress_callback(self, stress: StressData):
        pass

    def request_stress_data(self):
        stress = get_last_stress_data(
            self.driver,
            self.cmd_get_file_size,
            self.cmd_stream_file_with_size,
            self.cmd_stream_file_with_size_offset,
        )
        if stress is not None:
            self.stress_callback(stress)



    def destroy_node(self):
        """Clean shutdown."""
        self.get_logger().info("Shutting down CorsanoWrapper node...")
        try:
            if self.driver and self.driver.peripheral and self.driver.peripheral.is_connected():
                self.driver.peripheral.disconnect()
        except Exception as e:
            self.get_logger().warn(f"Error during disconnect: {e}")
        super().destroy_node()


def main(args=None):
    cli_args = parse_args()
    adapter_name = cli_args.adapter_name
    mac_address_or_name = cli_args.mac_address_or_name

    # Load config if provided. Cmd line args have override config
    if cli_args.config:
        cfg = load_config(cli_args.config)
        adapter_name = adapter_name or cfg.get("adapter_name")
        mac_address_or_name = mac_address_or_name or cfg.get("mac_address_or_name")

    if not adapter_name:
        adapter_name = "hci0"

    if not mac_address_or_name:
        mac_address_or_name = '287-2B'

    rclpy.init(args=args)
    node = None
    try:
        with CorsanoDriver(name_or_address=mac_address_or_name, adapter_name=adapter_name) as driver:
            node = CorsanoWrapper(driver)
            rclpy.spin(node)
    except KeyboardInterrupt:
        # User hit Ctrl+C
        error("[CorsanoWrapper] User interrupt received — shutting down cleanly.")
    
    except rclpy.executors.ExternalShutdownException:
        # e.g., ros2 daemon requested shutdown
        error("[CorsanoWrapper] External ROS 2 shutdown requested.")
    
    except Exception as e:
        # Catch all other errors from your driver or node
        error(f"[CorsanoWrapper] Unhandled exception: {type(e).__name__}: {e}")
    
    finally:
        if node is not None:
            node.destroy_node()
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except rclpy._rclpy_pybind11.RCLError:
            pass  # already shut down
        except Exception as e:
            error(f"[CorsanoWrapper] Error during shutdown: {e}")


if __name__ == "__main__":
    main()
