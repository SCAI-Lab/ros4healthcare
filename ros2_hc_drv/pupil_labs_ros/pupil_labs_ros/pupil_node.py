import rclpy
from rclpy.node import Node
import threading
import time
import cv2
import numpy as np

# Custom Healthcare Messages
from ros2_hc_msgs.msg import PupilGaze, Blink, Fixation, Saccade

# Standard ROS 2 Messages & Services
from sensor_msgs.msg import Imu, Image
from std_msgs.msg import String, Float32
from std_srvs.srv import Trigger
from rclpy.qos import qos_profile_sensor_data

# OpenCV bridge for Scene Video
from cv_bridge import CvBridge

from pupil_labs.realtime_api.simple import discover_one_device
from pupil_labs.realtime_api.streaming.eye_events import (
    BlinkEventData,
    FixationEventData,
)

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
        self.fixation_pub_ = self.create_publisher(Fixation, 'biosensing/derived_biosignals/eye/fixation', 10)
        self.saccade_pub_ = self.create_publisher(Saccade, 'biosensing/derived_biosignals/eye/saccade', 10)
        
        self.imu_pub_   = self.create_publisher(Imu, 'biosensing/raw_biosignals/imu/head_movement', qos_profile_sensor_data)
        self.video_pub_ = self.create_publisher(Image, 'biosensing/raw_biosignals/eye/scene_camera', qos_profile_sensor_data)
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
        threads = [
            threading.Thread(target=self.stream_gaze),
            threading.Thread(target=self.stream_video),
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
    def stream_gaze(self):
        """Dedicated high-speed stream for Gaze and Eyestate (200Hz)."""
        try:
            while rclpy.ok():
                gaze = self.device.receive_gaze_datum()
                if not gaze: continue
                
                msg = PupilGaze()
                sec = int(gaze.timestamp_unix_seconds)
                nanosec = int((gaze.timestamp_unix_seconds - sec) * 1e9)
                msg.header.stamp.sec = sec
                msg.header.stamp.nanosec = nanosec
                msg.header.frame_id = "pupil_glasses"
                
                # Basic Gaze & Worn Status
                msg.gaze_x = float(gaze.x)
                msg.gaze_y = float(gaze.y)
                msg.worn = bool(gaze.worn)
                
                # Pupil Diameters
                msg.pupil_diameter_right = float(gaze.pupil_diameter_right)
                msg.pupil_diameter_left = float(gaze.pupil_diameter_left)

                # Eyelid State (Left)
                msg.eyelid_angle_top_left = float(gaze.eyelid_angle_top_left)
                msg.eyelid_angle_bottom_left = float(gaze.eyelid_angle_bottom_left)
                msg.eyelid_aperture_left = float(gaze.eyelid_aperture_left)

                # Eyelid State (Right)
                msg.eyelid_angle_top_right = float(gaze.eyelid_angle_top_right)
                msg.eyelid_angle_bottom_right = float(gaze.eyelid_angle_bottom_right)
                msg.eyelid_aperture_right = float(gaze.eyelid_aperture_right)
                
                self.gaze_pub_.publish(msg)
        except Exception as e:
            self.get_logger().error(f"Gaze stream stopped: {e}")

    def stream_video(self):
        """Matched stream used ONLY to publish the Video with the Gaze overlay (30Hz)."""
        try:
            while rclpy.ok():
                matched = self.device.receive_matched_scene_and_eyes_video_frames_and_gaze()
                if not matched: continue

                sec = int(matched.scene.timestamp_unix_seconds)
                nanosec = int((matched.scene.timestamp_unix_seconds - sec) * 1e9)

                # Overlay Gaze Circle on Video
                scene_img = matched.scene.bgr_pixels.copy()
                cv2.circle(
                    scene_img,
                    (int(matched.gaze.x), int(matched.gaze.y)),
                    radius=80,
                    color=(0, 0, 255),
                    thickness=15,
                )

                # Overlay Eyes Video (Picture-in-Picture)
                if matched.eyes is not None:
                    height, width, _ = matched.eyes.bgr_pixels.shape
                    scene_img[:height, :width, :] = matched.eyes.bgr_pixels

                # Convert and publish ONLY the image topic
                image_msg = self.bridge.cv2_to_imgmsg(scene_img, encoding="bgr8")
                image_msg.header.stamp.sec = sec
                image_msg.header.stamp.nanosec = nanosec
                image_msg.header.frame_id = "pupil_scene_camera"
                
                self.video_pub_.publish(image_msg)

        except Exception as e:
            self.get_logger().error(f"Matched video stream stopped: {e}")

    def stream_events(self):
        """Asynchronous stream for Blinks, Fixations, and Saccades."""
        try:
            while rclpy.ok():
                eye_event = self.device.receive_eye_events()
                
                # --- PROCESS BLINKS ---
                if isinstance(eye_event, BlinkEventData):
                    duration_sec = (eye_event.end_time_ns - eye_event.start_time_ns) / 1e9
                    
                    # Exact hardware start time for the ROS header
                    ts_sec = eye_event.rtp_ts_unix_seconds
                    ros_sec = int(ts_sec)
                    ros_nanosec = int((ts_sec - ros_sec) * 1e9)

                    msg = Blink()
                    msg.header.stamp.sec = ros_sec
                    msg.header.stamp.nanosec = ros_nanosec
                    msg.header.frame_id = "pupil_glasses"
                    
                    msg.duration = float(duration_sec)
                    msg.start_time_ns = int(eye_event.start_time_ns)
                    msg.end_time_ns = int(eye_event.end_time_ns)
                    
                    self.blink_pub_.publish(msg)
                    self.get_logger().info(f"[BLINK] Duration: {duration_sec:.3f}s")


                # --- PROCESS FIXATIONS & SACCADES ---
                elif isinstance(eye_event, FixationEventData):
                    duration_sec = (eye_event.end_time_ns - eye_event.start_time_ns) / 1e9
                    
                    ts_sec = eye_event.rtp_ts_unix_seconds
                    ros_sec = int(ts_sec)
                    ros_nanosec = int((ts_sec - ros_sec) * 1e9)

                    # FIXATION (Type 1)
                    if eye_event.event_type == 1:
                        msg = Fixation()
                        msg.header.stamp.sec = ros_sec
                        msg.header.stamp.nanosec = ros_nanosec
                        msg.header.frame_id = "pupil_glasses"
                        
                        msg.duration = float(duration_sec)
                        msg.start_time_ns = int(eye_event.start_time_ns)
                        msg.end_time_ns = int(eye_event.end_time_ns)
                        
                        msg.start_gaze_x = float(eye_event.start_gaze_x)
                        msg.start_gaze_y = float(eye_event.start_gaze_y)
                        msg.end_gaze_x = float(eye_event.end_gaze_x)
                        msg.end_gaze_y = float(eye_event.end_gaze_y)
                        msg.mean_gaze_x = float(eye_event.mean_gaze_x)
                        msg.mean_gaze_y = float(eye_event.mean_gaze_y)
                        msg.amplitude_pixels = float(eye_event.amplitude_pixels)
                        msg.amplitude_angle_deg = float(eye_event.amplitude_angle_deg)
                        msg.mean_velocity = float(eye_event.mean_velocity)
                        msg.max_velocity = float(eye_event.max_velocity)
                        
                        self.fixation_pub_.publish(msg)
                        self.get_logger().info(f"[FIXATION] Duration: {duration_sec:.2f} seconds.")

                    # SACCADE (Type 0)
                    elif eye_event.event_type == 0:
                        msg = Saccade()
                        msg.header.stamp.sec = ros_sec
                        msg.header.stamp.nanosec = ros_nanosec
                        msg.header.frame_id = "pupil_glasses"
                        
                        msg.duration = float(duration_sec)
                        msg.start_time_ns = int(eye_event.start_time_ns)
                        msg.end_time_ns = int(eye_event.end_time_ns)
                        
                        msg.start_gaze_x = float(eye_event.start_gaze_x)
                        msg.start_gaze_y = float(eye_event.start_gaze_y)
                        msg.end_gaze_x = float(eye_event.end_gaze_x)
                        msg.end_gaze_y = float(eye_event.end_gaze_y)
                        msg.mean_gaze_x = float(eye_event.mean_gaze_x)
                        msg.mean_gaze_y = float(eye_event.mean_gaze_y)
                        msg.amplitude_pixels = float(eye_event.amplitude_pixels)
                        msg.amplitude_angle_deg = float(eye_event.amplitude_angle_deg)
                        msg.mean_velocity = float(eye_event.mean_velocity)
                        msg.max_velocity = float(eye_event.max_velocity)

                        self.saccade_pub_.publish(msg)
                        self.get_logger().info(
                            f"[SACCADE] Amplitude: {msg.amplitude_angle_deg:.1f}° | Max Vel: {msg.max_velocity:.0f} pixels/deg"
                        )

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
            self.device.send_event(msg.data, event_timestamp_unix_ns=int(time.time() * 1e9))
            self.get_logger().info(f"Injected Timeline Event: {msg.data}")
        except Exception as e:
            self.get_logger().error(f"Failed to send event: {e}")

    def destroy_node(self):
        if self.device:
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