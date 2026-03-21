import rclpy
from rclpy.node import Node
import threading
import time
import cv2
import numpy as np

# Custom Healthcare Messages
from ros2_hc_msgs.msg import PupilGaze, Blink

# Standard ROS 2 Messages & Services
from sensor_msgs.msg import Imu, Image
from std_msgs.msg import String, Float32
from std_srvs.srv import Trigger

# OpenCV bridge for Scene Video
from cv_bridge import CvBridge

from pupil_labs.realtime_api.simple import discover_one_device

# Workaround for https://github.com/opencv/opencv/issues/21952
cv2.imshow("cv/av bug", np.zeros(1))
cv2.destroyAllWindows()

class PupilLabsFullDriver(Node):
    def __init__(self):
        super().__init__('pupil_labs_driver')
        
        self.bridge = CvBridge()
        
        self.get_logger().info("Looking for Pupil Labs device on network...")
        self.device = discover_one_device(max_search_duration_seconds=10)
        
        if self.device is None:
            self.get_logger().error("No device found. Check Wi-Fi connection. Shutting down.")
            raise SystemExit()
            
        self.get_logger().info(f"Connected to Glasses: {self.device.serial_number_glasses} | Phone: {self.device.phone_name}")

        # ==========================================
        # 1. PUBLISHERS (Data Streams)
        # ==========================================
        self.gaze_pub_ = self.create_publisher(PupilGaze, 'biosensing/raw_biosignals/eye/pupil_gaze', 10)
        self.blink_pub_ = self.create_publisher(Blink, 'biosensing/derived_biosignals/eye/blink', 10)
        self.imu_pub_   = self.create_publisher(Imu, 'biosensing/raw_biosignals/imu/head_movement', 50)
        self.video_pub_ = self.create_publisher(Image, 'biosensing/raw_biosignals/eye/scene_camera', 10)
        self.battery_pub_ = self.create_publisher(Float32, 'hardware/biosensors/device/battery_level', 1)

        # ==========================================
        # 2. SERVICES & SUBSCRIBERS (Remote Control)
        # ==========================================
        self.srv_start_rec = self.create_service(Trigger, 'pupil_labs/recording_start', self.start_recording_cb)
        self.srv_stop_rec  = self.create_service(Trigger, 'pupil_labs/recording_stop', self.stop_recording_cb)
        self.event_sub = self.create_subscription(String, 'pupil_labs/send_event', self.send_event_cb, 10)

        # ==========================================
        # 3. BACKGROUND THREADS (Blocking API Calls)
        # ==========================================
        # Replaced separate Gaze and Video threads with a single Synchronized thread
        threads = [
            threading.Thread(target=self.stream_matched_data),
            threading.Thread(target=self.stream_events),
            threading.Thread(target=self.stream_imu)
        ]
        
        for t in threads:
            t.daemon = True
            t.start()

        self.status_timer = self.create_timer(10.0, self.publish_status)

    # ---------------------------------------------------------
    # STREAMING FUNCTIONS
    # ---------------------------------------------------------
    def stream_matched_data(self):
        """Synchronized stream for perfectly matched Gaze and Scene Video."""
        try:
            while rclpy.ok():
                matched = self.device.receive_matched_scene_and_eyes_video_frames_and_gaze()
                
                if not matched:
                    self.get_logger().debug("Waiting for matched frames...")
                    continue

                # 1. Generate a single, unified timestamp for perfect ROS bag syncing
                sec = int(matched.scene.timestamp_unix_seconds)
                nanosec = int((matched.scene.timestamp_unix_seconds - sec) * 1e9)

                # 2. Publish Gaze
                gaze_msg = PupilGaze()
                gaze_msg.header.stamp.sec = sec
                gaze_msg.header.stamp.nanosec = nanosec
                gaze_msg.header.frame_id = "pupil_glasses"
                
                gaze_msg.gaze_x = float(matched.gaze.x)
                gaze_msg.gaze_y = float(matched.gaze.y)
                gaze_msg.worn = bool(matched.gaze.worn)
                
                gaze_msg.pupil_diameter_right = float(matched.gaze.pupil_diameter_right)
                gaze_msg.pupil_diameter_left = float(matched.gaze.pupil_diameter_left)
                
                self.gaze_pub_.publish(gaze_msg)

                # 3. Process and Publish Video
                # Use .copy() to avoid modifying the original read-only array from the API
                scene_img = matched.scene.bgr_pixels.copy()

                # Overlay Gaze Circle
                cv2.circle(
                    scene_img,
                    (int(matched.gaze.x), int(matched.gaze.y)),
                    radius=80,
                    color=(0, 0, 255),
                    thickness=15,
                )

                # Overlay Eyes Video (Picture-in-Picture)
                if hasattr(matched, 'eyes') and matched.eyes is not None:
                    height, width, _ = matched.eyes.bgr_pixels.shape
                    scene_img[:height, :width, :] = matched.eyes.bgr_pixels

                # Convert to ROS Image and stamp with the EXACT same time as gaze
                image_msg = self.bridge.cv2_to_imgmsg(scene_img, encoding="bgr8")
                image_msg.header.stamp.sec = sec
                image_msg.header.stamp.nanosec = nanosec
                image_msg.header.frame_id = "pupil_scene_camera"
                
                self.video_pub_.publish(image_msg)

        except Exception as e:
            self.get_logger().error(f"Matched stream thread stopped: {e}")

    def stream_events(self):
        try:
            while rclpy.ok():
                event = self.device.receive_eye_events()
                if hasattr(event, 'event_type') and event.event_type == 4: # Blink Event
                    
                    # 1. Calculate the duration in seconds
                    duration_sec = (event.end_time_ns - event.start_time_ns) / 1e9
                    blink_msg = Blink()
                    blink_msg.header.stamp.sec = int(event.timestamp_unix_ns // 1e9)
                    blink_msg.header.stamp.nanosec = int(event.timestamp_unix_ns % 1e9)
                    blink_msg.header.frame_id = "pupil_glasses"
                    blink_msg.duration = float(duration_sec)
                    blink_msg.start_time_ns = int(event.start_time_ns)
                    blink_msg.end_time_ns = int(event.end_time_ns)
                    self.blink_pub_.publish(blink_msg)
        except Exception as e:
            self.get_logger().error(f"Event thread stopped: {e}")

    def stream_imu(self):
        try:
            while rclpy.ok():
                imu_data = self.device.receive_imu_datum()
                if not imu_data:
                    continue

                msg = Imu()
                
                # 1. Exact timestamp parsing from your output
                sec = int(imu_data.timestamp_unix_seconds)
                nanosec = int((imu_data.timestamp_unix_seconds - sec) * 1e9)
                msg.header.stamp.sec = sec
                msg.header.stamp.nanosec = nanosec
                msg.header.frame_id = "pupil_glasses_imu"
                
                # 2. Extract Acceleration (from Data3D object)
                msg.linear_acceleration.x = float(imu_data.accel_data.x)
                msg.linear_acceleration.y = float(imu_data.accel_data.y)
                msg.linear_acceleration.z = float(imu_data.accel_data.z)
                
                # 3. Extract Gyroscope (from Data3D object)
                msg.angular_velocity.x = float(imu_data.gyro_data.x)
                msg.angular_velocity.y = float(imu_data.gyro_data.y)
                msg.angular_velocity.z = float(imu_data.gyro_data.z)
                
                # 4. Extract Orientation (from Quaternion object)
                msg.orientation.x = float(imu_data.quaternion.x)
                msg.orientation.y = float(imu_data.quaternion.y)
                msg.orientation.z = float(imu_data.quaternion.z)
                msg.orientation.w = float(imu_data.quaternion.w)
                
                self.imu_pub_.publish(msg)
        except Exception as e:
            self.get_logger().error(f"IMU thread stopped: {e}")

    # ---------------------------------------------------------
    # REMOTE CONTROL & STATUS API
    # ---------------------------------------------------------
    def publish_status(self):
        try:
            battery = Float32()
            battery.data = float(self.device.battery_level_percent)
            self.battery_pub_.publish(battery)
        except Exception as e:
            self.get_logger().warning(f"Could not read battery: {e}")

    def start_recording_cb(self, request, response):
        try:
            rec_id = self.device.recording_start()
            response.success = True
            response.message = f"Recording started on phone with ID: {rec_id}"
            self.get_logger().info(response.message)
        except Exception as e:
            response.success = False
            response.message = f"Failed to start recording: {str(e)}"
        return response

    def stop_recording_cb(self, request, response):
        try:
            self.device.recording_stop_and_save()
            response.success = True
            response.message = "Recording stopped and saved successfully."
            self.get_logger().info(response.message)
        except Exception as e:
            response.success = False
            response.message = f"Failed to stop recording: {str(e)}"
        return response

    def send_event_cb(self, msg):
        try:
            event_result = self.device.send_event(msg.data, event_timestamp_unix_ns=int(time.time() * 1e9))
            self.get_logger().info(f"Injected Timeline Event: {msg.data}")
        except Exception as e:
            self.get_logger().error(f"Failed to send event: {e}")

    def destroy_node(self):
        if hasattr(self, 'device') and self.device:
            self.device.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = PupilLabsFullDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()