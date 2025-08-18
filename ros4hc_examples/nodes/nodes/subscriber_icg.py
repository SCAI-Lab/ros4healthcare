#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from ros_healthcare_msg.msg import ICGLeads


class ICGSubscriber(Node):
    def __init__(self):
        super().__init__('subscriber_icg')
        self.subscription = self.create_subscription(
            ICGLeads,
            'sub_icg',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info('Received ICG Leads: "%s"' % msg)


def main(args=None):
    rclpy.init(args=args)

    subscriber_icg = ICGSubscriber()

    rclpy.spin(subscriber_icg)

    subscriber_icg.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
