#!/usr/bin/env python3

import rclpy

from ros_healthcare_msg.msg import ADL


class ADLSubscriber(rclpy.node.Node):
    ''' Node for subscribing to ADL messages'''

    def __init__(self):
        '''Initialize the node'''
        super().__init__('subscriber_adl')

        # Create the subscriber. This subscriber will receive ADL messages
        self.subscription = self.create_subscription(
            ADL,
            'sub_adl',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        '''Callback function for handling ADL messages'''
        self.get_logger().info('Received ADL readings: "%s"' % msg)

def main(args=None):
    '''Main function for running the node'''

    # Initialize the node
    rclpy.init(args=args)

    # Create the node
    subscriber_adl = ADLSubscriber()

    # Spin the node so the callback function is called.
    rclpy.spin(subscriber_adl)

    # Destroy the node explicitly
    subscriber_adl.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
