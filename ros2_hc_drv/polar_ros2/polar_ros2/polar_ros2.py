from bleak import BleakScanner
import asyncio
import numpy as np
import argparse
from .submodules.PolarH10 import PolarH10
from .submodules.BreathingAnalyser import BreathingAnalyser
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class PolarConnector(Node):

    def __init__(self):
        super().__init__('polar_connector')      

        self.declare_parameter('publish_hr', True) 
        self.declare_parameter('publish_acceleration', True) 
        self.declare_parameter('publish_ecg', False) 
        self.declare_parameter('bluetooth_adapter', "hci0") 
        self.pub_rr = self.create_publisher(Int32, "polar_rr", 10)

    def start(self):
        self.publish_acceleration = self.get_parameter('publish_acceleration').get_parameter_value().bool_value
        self.publish_hr = self.get_parameter('publish_hr').get_parameter_value().bool_value
        self.publish_ecg = self.get_parameter('publish_ecg').get_parameter_value().bool_value
        self.bluetooth_adapter = self.get_parameter('bluetooth_adapter').get_parameter_value().string_value

        try:
            loop_0 = asyncio.get_event_loop()
            self.pd = loop_0.run_until_complete(self.get_device())
           
            if self.pd is not None:
                loop_0.run_until_complete(self.run(self.pd))
        except KeyboardInterrupt:
            print("Polar recording stopped by user.")
            loop_0.run_until_complete(self.disconnect(self.pd))
    
  
    async def get_device(self):
        devices = await BleakScanner.discover()
        polar_device_found = False
        acc_data = None
        ibi_data = None    
        for device in devices:
            if device.name is not None and "Polar" in device.name:
                polar_device_found = True
                polar_device = PolarH10(self, device, self.bluetooth_adapter, self.publish_acceleration, self.publish_hr, self.publish_ecg)
        
        if not polar_device_found:
            print("No Polar device found")
        return polar_device

    async def run(self, polar_device):
        await polar_device.connect()
        await polar_device.get_device_info()
        await polar_device.print_device_info()
        if self.publish_acceleration:
            await polar_device.start_acc_stream()
        if self.publish_hr:
            await polar_device.start_hr_stream()
        if self.publish_ecg:
            await polar_device.start_ecg_stream()
              
        while True:
            await asyncio.sleep(1)
            acc_data = polar_device.get_acc_data()
            ibi_data = polar_device.get_ibi_data()
            breathing_analyser = BreathingAnalyser(acc_data, ibi_data)
            msg = Int32()
            msg.data = int(breathing_analyser.get_rr())
            self.pub_rr.publish(msg)
    
    async def disconnect(self, polar_device):
        if self.publish_acceleration:
            await polar_device.stop_acc_stream()
        if self.publish_hr:
            await polar_device.stop_hr_stream()
        if self.publish_ecg:
            await polar_device.stop_ecg_stream()
        await polar_device.disconnect()



def main(args=None):
    rclpy.init(args=args)

    polar_node = PolarConnector()
    
    polar_node.start()
    polar_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()