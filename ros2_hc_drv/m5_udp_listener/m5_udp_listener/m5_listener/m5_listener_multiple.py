import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion
import socket
import json

class UdpListener(Node):
    def __init__(self):
        super().__init__('m5_listener')
        
        # Declare parameters with different default values
        self.declare_parameter('udp_ip', '0.0.0.0') 
        self.declare_parameter('udp_port', 1234)

        # Get parameters
        udp_ip = self.get_parameter('udp_ip').get_parameter_value().string_value
        udp_port = self.get_parameter('udp_port').get_parameter_value().integer_value

        # Setup UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind((udp_ip, udp_port))
            self.get_logger().info(f'Successfully bound to {udp_ip}:{udp_port}')
        except Exception as e:
            self.get_logger().error(f'Failed to bind to {udp_ip}:{udp_port}: {e}')
            raise

        self.sock.settimeout(1.0)  
        
        self.imu_publishers = {}
        
        self.timer = self.create_timer(0.02, self.timer_callback)

    def timer_callback(self):
        try:
            data, addr = self.sock.recvfrom(1024)  
            self.get_logger().debug(f'Received data from {addr}')
            
            imu_data = json.loads(data.decode())
            unique_id = imu_data['id']

            # Check if a publisher for this unique ID exists, if not create one
            if unique_id not in self.imu_publishers:
                self.imu_publishers[unique_id] = self.create_publisher(
                    Imu, f'{unique_id}_data', 10)
                self.get_logger().info(f"Created new topic for {unique_id}")

            msg = Imu()
            degtopi = 0.0174533

            # Set linear acceleration
            msg.linear_acceleration.x = imu_data['linear_acceleration']['x']
            msg.linear_acceleration.y = imu_data['linear_acceleration']['y']
            msg.linear_acceleration.z = imu_data['linear_acceleration']['z']

            # Set angular velocity (gyroscope)
            msg.angular_velocity.x = imu_data['angular_velocity']['x'] * degtopi
            msg.angular_velocity.y = imu_data['angular_velocity']['y'] * degtopi
            msg.angular_velocity.z = imu_data['angular_velocity']['z'] * degtopi

            # Set orientation (pitch and roll)
            orientation_quat = Quaternion()
            orientation_quat.x = imu_data['orientation']['yaw']
            orientation_quat.y = imu_data['orientation']['pitch']
            orientation_quat.z = imu_data['orientation']['roll']
            msg.orientation = orientation_quat

            # Publish the message to the appropriate topic
            self.imu_publishers[unique_id].publish(msg)
            
        except socket.timeout:
            self.get_logger().debug("Waiting for UDP data...")
        except json.JSONDecodeError as e:
            self.get_logger().warn(f"Invalid JSON data received: {e}")
        except Exception as e:
            self.get_logger().error(f"Error processing UDP data: {e}")

    def destroy_node(self):
        self.sock.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    try:
        node = UdpListener()
        rclpy.spin(node)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()