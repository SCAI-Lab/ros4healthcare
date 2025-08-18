#!/usr/bin/env python3

import rclpy

from ros_healthcare_msg.msg import ECGLeads


class ECGSubscriber(rclpy.node.Node):
    ''' Node for subscribing to ECG messages'''

    def __init__(self):
        '''Initialize the node'''
        super().__init__('subscriber_ecg')

        # Create the subscriber. This subscriber will receive ECGLeads messages
        self.subscription = self.create_subscription(
            ECGLeads,
            'sub_ecg',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        '''Callback function for handling ECGLeads messages'''
        self.get_logger().info('Received ECG Leads: "%s"' % msg)

def main(args=None):
    '''Main function for running the node'''

    # Initialize the node
    rclpy.init(args=args)

    # Create the node
    subscriber_ecg = ECGSubscriber()

    # Spin the node so the callback function is called.
    rclpy.spin(subscriber_ecg)

    # Destroy the node explicitly
    subscriber_ecg.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
