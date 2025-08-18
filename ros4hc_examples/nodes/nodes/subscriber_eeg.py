#!/usr/bin/env python3

import rclpy

from ros_healthcare_msg.msg import EEGchannels


class EEGSubscriber(rclpy.node.Node):
    ''' Node for subscribing to EEG messages'''

    def __init__(self):
        '''Initialize the node'''
        super().__init__('subscriber_eeg')

        # Create the subscriber. This subscriber will receive EEGchannels messages
        self.subscription = self.create_subscription(
            EEGchannels,
            'sub_eeg',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        '''Callback function for handling EEGchannels messages'''
        self.get_logger().info('Received EEG channels: "%s"' % msg)

def main(args=None):
    '''Main function for running the node'''

    # Initialize the node
    rclpy.init(args=args)

    # Create the node
    subscriber_eeg = EEGSubscriber()

    # Spin the node so the callback function is called.
    rclpy.spin(subscriber_eeg)

    # Destroy the node explicitly
    subscriber_eeg.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
