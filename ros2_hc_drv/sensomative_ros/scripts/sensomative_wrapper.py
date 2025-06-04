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
        
        if self.hci_mac:
            self.driver = SensomativeDriver(self.address, hci_mac=self.hci_mac)
        else:
            self.driver = SensomativeDriver(self.address)

        self.publisher_ = self.create_publisher(Pressure, 'pressure1', 10)
        self.device_exists = self.driver.get_device_exists()
        self.logger_ = self.get_logger()
        
        self.device_unavailable_logged = False
        
        # Add some logging to help debug
        self.logger_.info(f"Attempting to connect to device: \"{self.address}\"")
        if self.hci_mac:
            self.logger_.info(f"Using HCI MAC: \"{self.hci_mac}\"")
        
        timer_period = 0.1  # 1 - Frequency of the sampling
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Pressure()
        msg.header = PressureHeader()
        msg.header.header = Header()
        msg.header.header.stamp = self.get_clock().now().to_msg()
        msg.header.device_serial_number = self.address
        msg.header.unit = "Pa" 
        msg.header.sampling_frequency = 10  
        msg.header.resolution = 1.0
        msg.header.accuracy = 0.95 
        msg.header.max_range = 65535.0
        msg.header.min_range = 0.0
        msg.header.rows = 3
        msg.header.cols = 4
        
        if not self.device_exists:
            # Log once that device is not available
            if not self.device_unavailable_logged:
                self.logger_.info("Device not available, publishing zero data")
                self.device_unavailable_logged = True
            
            msg.pressure = [0] * 12  
            msg.time_signal_recorded = []  
            self.publisher_.publish(msg)
            return
        
        try:
            data = self.driver.get_data()  
            msg.pressure = [int(max(0, min(65535, x))) for x in data[0:12]]
            
            msg.time_signal_recorded = []
            
            self.publisher_.publish(msg) 

        except Exception as e:
            self.logger_.info('Failed to read data from peripheral: %s' % self.address)
            self.logger_.info('Error: %s' % str(e))
            
            # Publish zero data as fallback
            msg.pressure = [0] * 12
            msg.time_signal_recorded = []
            self.publisher_.publish(msg)

def main(args = None):
    try:
        rclpy.init(args=args)  
        semsomative_wrapper = SensomativeWrapper()

        rclpy.spin(semsomative_wrapper)

        semsomative_wrapper.destroy_node()
        rclpy.shutdown()
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    main()



