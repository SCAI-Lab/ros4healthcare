#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from ros2_hc_msgs.msg import Pressure
import cv2
import numpy as np
import matplotlib.pyplot as plt
import io

class PressureVisualiser(Node):

    def __init__(self):
        super().__init__('pressure_visualiser')
               
        # Parameters
        self.declare_parameter('input_topic', '/pressure')
        self.declare_parameter('output_topic', '/pressure_visualiser')
        self.declare_parameter('array_width', 10)
        self.declare_parameter('array_height', 10)

        self.input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        self.output_topic = self.get_parameter('output_topic').get_parameter_value().string_value
        self.array_width = self.get_parameter('array_width').get_parameter_value().integer_value
        self.array_height = self.get_parameter('array_height').get_parameter_value().integer_value

        #set all pressure squares to zero by default
        self.pressure = [0 for i in range(0,12)]

        #initialize the pressure matrix (initialized to -1)
        self.mat_arr = np.zeros((10,10))
        self.mat_arr = np.array(self.mat_arr).reshape((self.array_height, self.array_width)) - 1

        self.bridge = CvBridge()

        #publishers and subscribers
        self.sub_pressure = self.create_subscription(Pressure, self.input_topic, self.pressure_callback, 10)
        self.pub_pressure_img = self.create_publisher(Image,self.output_topic, 10)
        
        timer_period = 1 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.get_logger().info('Node Running')

    def pressure_callback(self, msg):
        self.pressure = msg.pressure

    def timer_callback(self):
        msg = Image()

        #set the pressure values
        self.mat_arr[0][0] = self.pressure[0]
        self.mat_arr[0][9] = self.pressure[11]
        self.mat_arr[2][2] = self.pressure[1]
        self.mat_arr[2][7] = self.pressure[10]
        self.mat_arr[4][0] = self.pressure[2]
        self.mat_arr[4][9] = self.pressure[9]
        self.mat_arr[6][3] = self.pressure[3]
        self.mat_arr[6][6] = self.pressure[8]
        self.mat_arr[9][0] = self.pressure[4]
        self.mat_arr[9][3] = self.pressure[5]
        self.mat_arr[9][6] = self.pressure[6]
        self.mat_arr[9][9] = self.pressure[9]

        # Generate heatmap
        fig, ax = plt.subplots(figsize=(20,20))
        ax.matshow(self.mat_arr)      
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        cax = ax.matshow(self.mat_arr)
        fig.colorbar(cax)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)

        buf_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
        cv_image = cv2.imdecode(buf_arr, cv2.IMREAD_COLOR)
        msg = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")

        #publish image
        self.pub_pressure_img.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    pressure_visualiser = PressureVisualiser()
    rclpy.spin(pressure_visualiser)
    pressure_visualiser.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()