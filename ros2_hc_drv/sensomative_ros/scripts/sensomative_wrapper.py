#!/usr/bin/env python3

from sensomative_ros.sensomative import SensomativeDriver
import rclpy
import rclpy.logging
from rclpy.node import Node
from ros2_hc_msgs.msg._pressure import Pressure
from ros2_hc_msgs.msg._pressure_header import PressureHeader

from std_msgs.msg import Header


class SensomativeWrapper(Node):
    def __init__(self):
        super().__init__('sensomative_wrapper')

        # Declare parameters with proper types
        self.declare_parameter('mac_add', "CC:CC:CC:0A:39:73")
        self.declare_parameter('hci_mac', "")  

        # Get parameter values
        self.address = self.get_parameter('mac_add').get_parameter_value().string_value
        self.hci_mac = self.get_parameter('hci_mac').get_parameter_value().string_value
        
        # Only pass hci_mac if it's not empty
        if self.hci_mac:
            self.driver = SensomativeDriver(self.address, hci_mac=self.hci_mac)
        else:
            self.driver = SensomativeDriver(self.address)

        self.publisher_ = self.create_publisher(Pressure, 'pressure1', 10)
        self.device_exists = self.driver.get_device_exists()
        self.logger_ = self.get_logger()
        
        # Add some logging to help debug
        self.logger_.info(f"Attempting to connect to device: \"{self.address}\"")
        if self.hci_mac:
            self.logger_.info(f"Using HCI MAC: \"{self.hci_mac}\"")
        
        timer_period = 0.1  # 1 - Frequency of the sampling
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Pressure()
        msg.header = PressureHeader()
        msg.header.header= Header()
        msg.header.device_serial_number = self.address
        try:
            data = self.driver.get_data()  
            msg.pressure = data[0:12]
            msg.header.rows = 3
            msg.header.cols = 4
            msg.header.header.stamp = self.get_clock().now().to_msg()

            self.publisher_.publish(msg) # publish the message

        except Exception as e:
            self.logger_.info('Failed to read data from peripheral: %s' % self.address)
            self.logger_.info('Error: %s' % str(e))


def main(args = None):
    try:
        rclpy.init(args=args)  
        semsomative_wrapper = SensomativeWrapper()

        if semsomative_wrapper.device_exists:
            rclpy.spin(semsomative_wrapper)

        semsomative_wrapper.destroy_node()
        rclpy.shutdown()
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    main()
    
