import rclpy
from rclpy.node import Node
from ros_healthcare_msg.msg import PPG


class Subscriber_ppg(Node):
    def __init__(self):
        super().__init__('pubsub_ppg')
        self.subscription = self.create_subscription(
            PPG,
            'sub_ppg',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info('Received PPG: "%s"' % msg)


def main(args=None):
    rclpy.init(args=args)

    subscriber_ppg_new = Subscriber_ppg()

    rclpy.spin(subscriber_ppg_new)

    Subscriber_ppg.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
