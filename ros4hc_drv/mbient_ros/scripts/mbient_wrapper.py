#!/usr/bin/env python3
from mbient_ros.mbient import MbientDriver
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from threading import Event

class MbientWrapper(Node):
    def __init__(self):
        super().__init__('mbient_wrapper')

        self.declare_parameter('mac_add', "F1:1F:CC:0E:65:86")
        self.declare_parameter('hci_mac', None)
        self.address = self.get_parameter('mac_add').get_parameter_value().string_value
        self.hci_mac = self.get_parameter('hci_mac').get_parameter_value().string_value
        if self.hci_mac:
            self.driver = MbientDriver(self.address, self.callback, self.hci_mac)
        else:    
            self.driver = MbientDriver(self.address, self.callback)
        self.publisher_ = self.create_publisher(Imu, 'imu', 10)
        self.logger_ = self.get_logger() 
        self.e = Event()

    def callback(self, euler):
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.linear_acceleration.x = euler.x
        msg.linear_acceleration.y = euler.y
        msg.linear_acceleration.z = euler.z
        self.publisher_.publish(msg)
        self.e.set()

    def run(self):
        self.driver.start_sensor()
        while rclpy.ok():
            rclpy.spin_once(self)
            if self.driver.device_is_connected():
                self.e.wait()
                self.e.clear()
            else:
                self.driver.connect_device()
        self.driver.stop_sensor()

def main(args = None):
    rclpy.init(args=args)  
    mbient_wrapper = MbientWrapper()
    mbient_wrapper.run()
    mbient_wrapper.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
    
