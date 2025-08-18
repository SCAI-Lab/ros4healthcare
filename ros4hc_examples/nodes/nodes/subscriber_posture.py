#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from ros_healthcare_msg.msg import Posture


class PostureSubscriber(Node):
    def __init__(self):
        super().__init__('subscriber_posture')
        self.subscription = self.create_subscription(
            Posture,
            'sub_posture',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info('Received Posture readings: "%s"' % msg)


def main(args=None):
    rclpy.init(args=args)

    subscriber_posture = PostureSubscriber()

    rclpy.spin(subscriber_posture)

    subscriber_posture.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
