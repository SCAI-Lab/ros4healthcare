#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import numpy as np
from std_msgs.msg import Int32, Float32, Float32MultiArray

from corsano_ros.retrieve_data import (
    connect,
    get_last_activity_data,
    get_last_bioz_data,
    get_last_stress_data,
    get_last_accelerometer_data,
)
from corsano_ros.commands import VENDOR_CMD_FD53, VENDOR_CMD_FD7D, VENDOR_CMD_FC2D, VENDOR_CMD_FD57


class CorsanoWrapper(Node):
    def __init__(self):
        super().__init__('corsano_wrapper')

        # Parameters
        self.declare_parameter('mac_add', "C4:8D:E7:96:BD:AD")
        self.declare_parameter('adapter_mac_add', "E4:1F:D5:66:FA:93")

        self.address = self.get_parameter('mac_add').get_parameter_value().string_value
        self.adapter_address = self.get_parameter('adapter_mac_add').get_parameter_value().string_value

        # Connect to Corsano
        self.cors, is_connected = connect(self.address, self.adapter_address)
        if not is_connected:
            self.get_logger().error("Failed to connect to Corsano device.")
            return

        # Map commands
        type_to_command = {type(v).__name__: v for v in self.cors.commands.values()}
        self.cmd_get_file_size = type_to_command["CMD_GET_FILE_SIZE"]
        self.cmd_stream_file_with_size = type_to_command["CMD_START_STREAMING_FILE_WITH_SIZE"]
        self.cmd_stream_file_with_size_offset = type_to_command["CMD_START_STREAMING_FILE_WITH_SIZE_OFFSET"]

        # Set activity plan
        # self.cors.set_max_act_plan()

        # Enable BioZ recording via vendor commands
        for cmd_class in [VENDOR_CMD_FD53, VENDOR_CMD_FD7D, VENDOR_CMD_FC2D, VENDOR_CMD_FD57]:
            cmd = cmd_class()
            packet = cmd.execute()  # raw bytes
            self.cors.write(packet)  # Send directly
            print("Sent packet:", packet.hex())


        # ROS publishers
        self.hr_pub = self.create_publisher(Int32, 'hr', 10)
        self.rr_pub = self.create_publisher(Int32, 'rr', 10)
        self.eda_pub = self.create_publisher(Float32, 'eda', 10)
        self.accel_pub = self.create_publisher(Float32MultiArray, 'acc', 10)

        # Timer for periodic data retrieval
        self.create_timer(0.5, self.timer_callback)

    # --- Callbacks for streaming data ---
    def bioz_callback(self, bioz):
        if bioz.eda_us.size > 0 and not np.isnan(bioz.eda_us[-1]):
            msg = Float32()
            msg.data = float(bioz.eda_us[-1])
            self.eda_pub.publish(msg) 
            self.get_logger().info(f"EDA: {bioz.eda_us} {msg.data:.3f} µS")

    def accel_callback(self, acceleration):
        if acceleration.x_values.size > 0:
            msg = Float32MultiArray()
            msg.data = [float(acceleration.x_values[-1]), float(acceleration.y_values[-1]), float(acceleration.z_values[-1])]
            self.accel_pub.publish(msg)
            self.get_logger().info(f"Accel: X={msg.data[0]:.3f}, Y={msg.data[1]:.3f}, Z={msg.data[2]:.3f}")

    # --- Timer callback ---
    def timer_callback(self):
        try:
            # --- HR / RR ---
            print("Fetching activity")
            activity = get_last_activity_data(
                self.cors,
                self.cmd_get_file_size,
                self.cmd_stream_file_with_size,
                self.cmd_stream_file_with_size_offset
            )
            if activity:
                self.hr_pub.publish(Int32(data=activity.hr_filtered))
                self.rr_pub.publish(Int32(data=int(activity.rr_filtered)))
                self.eda_pub.publish(Float32(data=float(activity.stress)))
            print("Fetching eda")
            # --- EDA ---
            get_last_bioz_data(
                self.cors,
                self.cmd_get_file_size,
                self.cmd_stream_file_with_size,
                self.cmd_stream_file_with_size_offset,
                callback=self.bioz_callback
            )
            print("Fetching stress")

            # --- Stress ---
            get_last_stress_data(
                self.cors,
                self.cmd_get_file_size,
                self.cmd_stream_file_with_size,
                self.cmd_stream_file_with_size_offset
            )
            print("Fetching accelerometer")

            # --- Accelerometer ---
            get_last_accelerometer_data(
                self.cors,
                self.cmd_get_file_size,
                self.cmd_stream_file_with_size,
                self.cmd_stream_file_with_size_offset,
                callback=self.accel_callback
            )

        except TimeoutError as e:
            self.get_logger().warn(f"Command timed out: {e}")
        except Exception as e:
            self.get_logger().error(f"Failed to read data: {e}")


def main(args=None):
    rclpy.init(args=args)
    try:
        wrapper = CorsanoWrapper()
        rclpy.spin(wrapper)
    except Exception as e:
        print(f"An exception occured: {e}")
    finally:
        wrapper.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
