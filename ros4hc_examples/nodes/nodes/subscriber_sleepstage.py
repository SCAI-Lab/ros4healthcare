import rclpy
from rclpy.node import Node
from ros_healthcare_msg.msg import Sleepstage


class SleepstageSubscriber(Node):
    def __init__(self):
        super().__init__('subscriber_sleepstage')
        self.subscription = self.create_subscription(
            Sleepstage,
            'sub_sleepstage',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info('Received Sleepstage readings: "%s"' % msg)


def main(args=None):
    rclpy.init(args=args)

    subscriber_sleepstage = SleepstageSubscriber()

    rclpy.spin(subscriber_sleepstage)

    subscriber_sleepstage.destroy_node()
    rclpy.shutdown()


if __name__ == 'report__main__':
    main()
