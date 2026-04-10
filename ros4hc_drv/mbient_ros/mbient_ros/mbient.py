import time
from rclpy.node import Node
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from ctypes import CFUNCTYPE, POINTER



class MbientDriver(Node):
    SENSOR_DATA_HANDLER_FUNC_TYPE = CFUNCTYPE(None, c_void_p, POINTER(Data))

    def __init__(self, address, callback, hci_mac=None, dummy_mode=False, max_retries=100, retry_delay=5.0):
        super().__init__('mbient_driver')
        self.callback = callback
        self.sensor_data_handler = self.sensor_data_handler
        self.sensor_data_handler_func = self.SENSOR_DATA_HANDLER_FUNC_TYPE(self.sensor_data_handler)
        self.dummy_mode = dummy_mode
        self.address = address
        self.hci_mac = hci_mac
        self.get_logger().info('attempting to connect to IMU device: "%s"' % self.address)
        if self.hci_mac:
            self.device = MetaWear(self.address, hci_mac=self.hci_mac)
        else:
            self.device = MetaWear(self.address)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.connect_device()

        self.device.on_disconnect = lambda status: ( self.get_logger().info("device out of range ... ") , self.connect_device() )

        

    def connect_device(self):
        while not self.device.is_connected:
            time.sleep(self.retry_delay)  # delay before next attempt
            self.get_logger().info(f"Trying to connect to device {self.address}")
            try:
                self.device.connect()
            except Exception as e:
                self.get_logger().info(f"Could not connect to device: {e} , retrying...")
        
        if self.device.is_connected:
            self.get_logger().info("Connected to device")
                    
            

    def sensor_data_handler(self, ctx, data):
        euler = parse_value(data)
        self.callback(euler)


    def start_sensor(self):
        if self.device and self.device.is_connected:
            self.get_logger().info("Configuring device")
            libmetawear.mbl_mw_settings_set_connection_parameters(self.device.board, 7.5, 7.5, 0, 6000)
            time.sleep(1.5)
            signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
            libmetawear.mbl_mw_datasignal_subscribe(signal, None, self.sensor_data_handler_func)
            libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.device.board)
            libmetawear.mbl_mw_acc_start(self.device.board)
        else:
            self.get_logger().info("Trying to connect to device...")
            self.connect_device()

    def stop_sensor(self):
        libmetawear.mbl_mw_acc_stop(self.device.board)
        libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.device.board)
        signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
        libmetawear.mbl_mw_datasignal_unsubscribe(signal)
        self.device.disconnect()
        time.sleep(1)


    def device_is_connected(self):
        return self.device and self.device.is_connected
    
