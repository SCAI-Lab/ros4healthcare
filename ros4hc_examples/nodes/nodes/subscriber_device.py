#!/usr/bin/env python3

import rclpy

from ros_healthcare_msg.msg import Device


class DeviceSubscriber(rclpy.node.Node):
    ''' Node for subscribing to Device messages'''

    def __init__(self):
        '''Initialize the node'''
        super().__init__('subscriber_device')

        # Create the subscriber. This subscriber will receive Device messages
        self.subscription = self.create_subscription(
            Device,
            'sub_device',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        '''Callback function for handling Device messages'''
        self.get_logger().info('Received Device status readings: "%s"' % msg)

def main(args=None):
    '''Main function for running the node'''

    # Initialize the node
    rclpy.init(args=args)

    # Create the node
    subscriber_device = DeviceSubscriber()

    # Spin the node so the callback function is called.
    rclpy.spin(subscriber_device)

    # Destroy the node explicitly
    subscriber_device.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
