#!/usr/bin/env python3

import numpy as np
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from ros2_hc_msgs.msg import Pressure
import plotly.graph_objects as go
import cv2
from scipy.ndimage import gaussian_filter
from scipy.interpolate import griddata

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

        self.pressure = [0 for _ in range(12)]
        self.bridge = CvBridge()

        self.sub_pressure = self.create_subscription(Pressure, self.input_topic, self.pressure_callback, 10)
        self.pub_pressure_img = self.create_publisher(Image, self.output_topic, 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

        self.get_logger().info('Pressure Visualiser Node Running')

    def pressure_callback(self, msg):
        self.pressure = msg.pressure

    def create_smooth_heatmap(self):
        points = np.array([
            [0, 0], [20, 20], [40, 0], [60, 30],
            [90, 0], [90, 30], [90, 60], [90, 90],
            [60, 60], [40, 90], [20, 70], [0, 90]
        ])
        
        values = np.array(self.pressure)

        grid_x, grid_y = np.mgrid[0:100:complex(0, self.array_width), 
                                   0:100:complex(0, self.array_height)]

        grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

        nan_mask = np.isnan(grid_z)
        grid_z[nan_mask] = griddata(points, values, (grid_x[nan_mask], grid_y[nan_mask]), method='nearest')

        smoothed = gaussian_filter(grid_z, sigma=self.smoothing_sigma)

        return smoothed

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
