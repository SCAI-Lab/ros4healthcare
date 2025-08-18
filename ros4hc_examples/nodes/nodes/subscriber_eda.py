#!/usr/bin/env python3

import rclpy

from ros_healthcare_msg.msg import EDA


class EDASubscriber(rclpy.node.Node):
    ''' Node for subscribing to EDA messages'''

    def __init__(self):
        '''Initialize the node'''
        super().__init__('subscriber_eda')

        # Create the subscriber. This subscriber will receive EDA messages
        self.subscription = self.create_subscription(
            EDA,
            'sub_eda',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        '''Callback function for handling EDA messages'''
        self.get_logger().info('Received EDA readings: "%s"' % msg)

def main(args=None):
    '''Main function for running the node'''

    # Initialize the node
    rclpy.init(args=args)

    # Create the node
    subscriber_eda = EDASubscriber()

    # Spin the node so the callback function is called.
    rclpy.spin(subscriber_eda)

    # Destroy the node explicitly
    subscriber_eda.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
