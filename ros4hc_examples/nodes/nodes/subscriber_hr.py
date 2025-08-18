#!/usr/bin/env python3

import rclpy

from ros_healthcare_msg.msg import HR


class Subscriber_hr(rclpy.node.Node):
    ''' Node for subscribing to HR messages'''

    def __init__(self):
        '''Initialize the node'''
        super().__init__('pubsub_hr')

        # Create the subscriber. This subscriber will receive HR messages
        self.subscription = self.create_subscription(
            HR,
            'sub_hr',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        '''Callback function for handling HR messages'''
        self.get_logger().info('Received HR: "%s"' % msg)

def main(args=None):
    '''Main function for running the node'''

    # Initialize the node
    rclpy.init(args=args)

    # Create the node
    subscriber_hr = Subscriber_hr()

    # Spin the node so the callback function is called.
    rclpy.spin(subscriber_hr)

    # Destroy the node explicitly
    Subscriber_hr.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
