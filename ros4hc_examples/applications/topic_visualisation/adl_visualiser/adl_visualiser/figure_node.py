#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import cv2
import os
import numpy as np

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# LOG_FOLDER = os.path.normpath(os.path.join(BASE_DIR, '../../../../../../data/ecg_files/'))
PKG_PATH= "/home/heba/SCAI_LAB/class_image_publisher/adl_visualiser/src/"
PKG_NAME = 'publishadl_visualiser_figures'
class ADLVisualiser(Node):

    def __init__(self):
        super().__init__('adl_visualiser')
        # Parameters
        self.declare_parameter('input_topic', '/adl_class')
        self.declare_parameter('output_topic', '/adl_visualiser')

        self.input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        self.output_topic = self.get_parameter('output_topic').get_parameter_value().string_value

        self.adl_class = 'Empty'
        self.bridge = CvBridge()

        self.sub_adl = self.create_subscription(String, "/adl_class", self.adl_callback, 10)
        self.pub_adl_img = self.create_publisher(Image, '/adl_visualiser', 10)
        
        timer_period = 1 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.get_logger().info('Node Running')

    def get_adl_icon_path(self,package_path, pkg_name, adl_class):
        '''
            returns image path to the input adl class
        '''
        adl_class_map = {
        'Resting':  "resource/State-Resting.png",
        'Self Propulsion':  "resource/State-Mobility.png",
        'Arm Raises':  "resource/State-Exercise.png",
        'Transfer':  "resource/State-Transfer.png",
        'Using Phone':  "resource/State-Leisure.png",
        'Conversation':  "resource/State-Social.png",
        'Washing Hands':  "resource/State-Selfcare.png",
        'Eating,Drinking':  "resource/State-Eating.png",
        'Assisted Propulsion':  "resource/State-Mobility.png",
        'Working on Computer':  "resource/State-Social.png",
        'Changing Clothes':  "resource/State-Selfcare.png",
        'Pressure Relief':  "resource/State-Transfer.png",
        'Empty':  "resource/State-Empty.png",
    }
        return os.path.join(package_path,adl_class_map[adl_class])


    def adl_callback(self, msg):
        self.adl_class = msg.data
        print("adl_class",self.adl_class)


    def timer_callback(self):
        msg = Image()
        img_path = self.get_adl_icon_path(PKG_PATH, PKG_NAME, self.adl_class )
        print("img_path",img_path)
        self.cv_image = cv2.imread(img_path)
        msg = self.bridge.cv2_to_imgmsg(np.array(self.cv_image), "bgr8")
        self.pub_adl_img.publish(msg)
        self.get_logger().info('Publishing: "%s"' % self.adl_class)

def main(args=None):
    rclpy.init(args=args)
    adl_visualiser = ADLVisualiser()
    rclpy.spin(adl_visualiser)
    adl_visualiser.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()