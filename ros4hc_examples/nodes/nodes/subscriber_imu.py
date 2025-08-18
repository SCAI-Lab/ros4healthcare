#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from ros_healthcare_msg.msg import IMU


class Subscriber_imu(Node):
    def __init__(self):
        super().__init__('pubsub_imu')
        self.subscription = self.create_subscription(
            IMU,
            'sub_imu',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info('Received IMU: "%s"' % msg)


def main(args=None):
    rclpy.init(args=args)

    subscriber_imu = Subscriber_imu()

    rclpy.spin(subscriber_imu)

    Subscriber_imu.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
