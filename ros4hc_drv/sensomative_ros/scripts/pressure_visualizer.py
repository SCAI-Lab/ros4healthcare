#!/usr/bin/env python3

import numpy as np
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
import matplotlib.pyplot as plt
from sensor_msgs.msg import Image
from ros4hc_msgs.msg import PressureMat
from io import BytesIO
from PIL import Image as Im
import cv2

class PressureVisualiser(Node):

    def __init__(self):
        super().__init__('pressure_visualiser')

        self.declare_parameter('input_topic', '/pressure1')
        self.declare_parameter('output_topic', '/pressure_visualiser')
        self.declare_parameter('array_width', 50)
        self.declare_parameter('array_height', 50)
        self.declare_parameter('debug_mode', False)
        self.declare_parameter('smoothing_sigma', 3.0)

        self.input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        self.output_topic = self.get_parameter('output_topic').get_parameter_value().string_value
        self.array_width = self.get_parameter('array_width').get_parameter_value().integer_value
        self.array_height = self.get_parameter('array_height').get_parameter_value().integer_value
        self.debug_mode = self.get_parameter('debug_mode').get_parameter_value().bool_value
        self.smoothing_sigma = self.get_parameter('smoothing_sigma').get_parameter_value().double_value

        self.pressures = [0 for _ in range(12)]
        self.bridge = CvBridge()

        self.sub_pressure = self.create_subscription(PressureMat, self.input_topic, self.pressure_callback, 10)

        self.img_pub = self.create_publisher(Image, self.output_topic, 10)

        #self.pub_pressure_img = self.create_publisher(Image, self.output_topic, 10)
        #self.timer = self.create_timer(0.1, self.timer_callback)

        self.get_logger().info('Pressure Visualiser Node Running')

    def pressure_callback(self, msg):
        col_indices = np.array([0, 1, 0, 1, 0, 1, 2, 3, 2, 3, 2, 3])
        row_indices = np.array([0, 1, 2, 3, 4, 4, 4, 4, 3, 2, 1, 0])
        grid = np.zeros((5, 4), dtype=np.uint8)
        grid[row_indices, col_indices] = msg.pressures

        res = 600

        fig, ax = plt.subplots(figsize=(6, 6), dpi=res/6)

        ax.set_position([0, 0, 1, 1])
        fig.text(0.5, 0.95, 'FRONT', ha='center', va='center', fontsize=16, color='white', fontweight='bold')
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')

        ax.axis('off')

        ax.imshow(grid, interpolation="gaussian", cmap="turbo", vmin=0, vmax=255, aspect='auto')
        fig.canvas.draw()

        width, height = fig.canvas.get_width_height()
        rgb_buffer = fig.canvas.tostring_rgb()

        numpy_img_rgb = np.frombuffer(rgb_buffer, dtype=np.uint8).reshape(height, width, 3)

        plt.close(fig)

        numpy_img_bgr = cv2.cvtColor(numpy_img_rgb, cv2.COLOR_RGB2BGR)

        msg = self.bridge.cv2_to_imgmsg(numpy_img_bgr, "bgr8")

        msg.header.stamp = self.get_clock().now().to_msg()
        self.img_pub.publish(msg)

    def timer_callback(self):
        smoothed_pressure = self.create_smooth_heatmap()

        smoothed_pressure = np.flipud(smoothed_pressure)

        zmin = np.nanmin(smoothed_pressure)
        zmax = np.nanmax(smoothed_pressure)
        if zmin == zmax:
            zmax = zmin + 1e-5

        fig = go.Figure(data=go.Heatmap(
            z=smoothed_pressure,
            colorscale='Turbo',
            zmin=zmin,
            zmax=zmax,
            hoverongaps=False,
            showscale=True
        ))

        fig.add_annotation(
            text="REAR",
            x=0.5, y=0.05,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=25, color="black", family="Arial Black"),
            opacity=0.8
        )


        fig.update_layout(
            width=600,
            height=600,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        try:
            img_bytes = fig.to_image(format="png")
        except Exception as e:
            self.get_logger().error(f"Plotly image export failed: {e}")
            return

        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        cv_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        msg = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")
        self.pub_pressure_img.publish(msg)



def main(args=None):
    rclpy.init(args=args)
    node = PressureVisualiser()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
