import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion
import socket
import json

class UdpListener(Node):

    def __init__(self):
        super().__init__('m5_listener')

        self.declare_parameter('udp_ip', '192.168.1.192')
        self.declare_parameter('udp_port', 1234)

        udp_ip = self.get_parameter('udp_ip').get_parameter_value().string_value
        udp_port = self.get_parameter('udp_port').get_parameter_value().integer_value

        self.publisher_ = self.create_publisher(Imu, 'imu_data', 10)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((udp_ip, udp_port))

        
        self.timer = self.create_timer(0.02, self.timer_callback)

        

    def timer_callback(self):
        try:
            data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
            
            imu_data = json.loads(data.decode())
            
            
            msg = Imu()

            degtopi = 0.0174533

            # Set linear acceleration
            msg.linear_acceleration.x = imu_data['linear_acceleration']['x']
            msg.linear_acceleration.y = imu_data['linear_acceleration']['y']
            msg.linear_acceleration.z = imu_data['linear_acceleration']['z']

            # Set angular velocity (gyroscope)
            msg.angular_velocity.x = (imu_data['angular_velocity']['x'])* degtopi
            msg.angular_velocity.y = (imu_data['angular_velocity']['y'])* degtopi
            msg.angular_velocity.z = (imu_data['angular_velocity']['z'])* degtopi

            # Set orientation (pitch and roll)
            orientation_quat = Quaternion()
            orientation_quat.x = imu_data['orientation']['yaw']
            orientation_quat.y = imu_data['orientation']['pitch']
            orientation_quat.z = imu_data['orientation']['roll']

            msg.orientation = orientation_quat
            

            self.publisher_.publish(msg)
            
        except socket.timeout:
            self.get_logger().warn("UDP socket timed out")
        except Exception as e:
            self.get_logger().error(f"Error receiving UDP data: {e}")

    def destroy_node(self):
        self.sock.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = UdpListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
