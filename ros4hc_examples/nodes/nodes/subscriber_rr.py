import rclpy
from rclpy.node import Node
from ros_healthcare_msg.msg import RR


class RRSubscriber(Node):
    def __init__(self):
        super().__init__('subscriber_rr')
        self.subscription = self.create_subscription(
            RR,
            'sub_rr',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info('Received RR readings: "%s"' % msg)


def main(args=None):
    rclpy.init(args=args)

    subscriber_rr = RRSubscriber()

    rclpy.spin(subscriber_rr)

    subscriber_rr.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
