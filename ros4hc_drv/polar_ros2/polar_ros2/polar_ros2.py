from bleak import BleakScanner
import asyncio
import logging as log
from .submodules.PolarH10 import PolarH10
from .submodules.BreathingAnalyser import BreathingAnalyser
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3Stamped

class PolarConnector(Node):

    def __init__(self):
        super().__init__('polar_connector')      

        self.declare_parameter('publish_hr', True) 
        self.declare_parameter('publish_acceleration', True) 
        self.declare_parameter('publish_ecg', False) 
        self.declare_parameter('bluetooth_adapter', "hci0") 
        self.pub_rr = self.create_publisher(Vector3Stamped, "polar_rr", 10)

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
            log.info("[PolarConnector] Polar recording stopped by user.")
        except Exception as e:
            log.error(f"[PolarConnector] Uncaught exception: {e}")
        finally:
            loop_0.run_until_complete(self.disconnect(self.pd))
    
  
    async def get_device(self):
        devices = await BleakScanner.discover()
        print(f"Devices: {devices}")
        for device in devices:
            if device.name is not None and "Polar H10" in device.name:
                return PolarH10(self, device, self.bluetooth_adapter, self.publish_acceleration, self.publish_hr, self.publish_ecg)
        
        log.error("[PolarConnector] No Polar device found. Retrying...")
        await self.get_device()
            

    async def run(self, polar_device):
        await polar_device.connect()
        log.info("[PolarConnector] Polar device is connected.")
        # await polar_device.get_device_info()
        # await polar_device.print_device_info()
        if self.publish_acceleration or self.publish_ecg:
            await polar_device.start_combined_stream()
        if self.publish_hr:
            await polar_device.start_hr_stream()

              
        while True:
            await asyncio.sleep(1)
            acc_data = polar_device.get_acc_data()
            ibi_data = polar_device.get_ibi_data()
            if acc_data is None or ibi_data is None:
                log.warning(f"Received invalid data. Acc: {acc_data}, ibi_data: {ibi_data}")
                continue
            breathing_analyser = BreathingAnalyser(acc_data, ibi_data)
            msg = Vector3Stamped()
            msg.vector.x = float(breathing_analyser.get_rr())
            msg.header.stamp = self.get_clock().now().to_msg()
            self.pub_rr.publish(msg)
    
    async def disconnect(self, polar_device):
        if polar_device is not None:
            if self.publish_acceleration or self.publish_ecg:
                await polar_device.stop_combined_stream()
            if self.publish_hr:
                await polar_device.stop_hr_stream()
            await polar_device.disconnect()



def main(args=None):
    rclpy.init(args=args)

    polar_node = PolarConnector()
    
    polar_node.start()
    polar_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
