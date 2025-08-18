from rclpy.node import Node
from ros4hc_msgs.msg._pressure import Pressure
from ros4hc_msgs.msg._pressure_header import PressureHeader
from std_msgs.msg import Header
from typing import List, Optional

from bluetooth_common.bluetooth_connection_manager import BluetoothConnectionManager


class SensomativeRos(Node):
    def __init__(
        self,
        regex_pattern: str,
        adapter: str,
        mac_address: Optional[str],
        target_uuids: List[str],
    ):
        super().__init__("sensomative")

        self.bluetooth_connection_manager = BluetoothConnectionManager(
            pattern=regex_pattern,
            adapter=adapter,
            mac_address=mac_address,
            target_uuids=target_uuids,
        )
        self.driver_context = self.bluetooth_connection_manager.__enter__()
        self.driver = self.driver_context

        self.publisher_ = self.create_publisher(Pressure, "pressure1", 10)

        timer_period = 0.1  # Frequency of the sampling
        self.timer = self.create_timer(timer_period, self.timer_callback)

    @property
    def mac_address(self) -> Optional[str]:
        return self.bluetooth_connection_manager.mac_address

    def timer_callback(self):
        if self.driver is None:
            self.get_logger().warn(
                "The bluetooth driver is None. Not publishing any data."
            )
            return
        data = self.driver.get_data()
        if data is not None:
            msg = Pressure()
            msg.header = PressureHeader()
            msg.header.header = Header()
            msg.header.header.stamp = self.get_clock().now().to_msg()
            msg.header.device_serial_number = str(self.mac_address)
            msg.header.unit = "Pa"
            msg.header.sampling_frequency = 10
            msg.header.resolution = 1.0
            msg.header.accuracy = 0.95
            msg.header.max_range = 65535.0
            msg.header.min_range = 0.0
            msg.header.rows = 3
            msg.header.cols = 4
            msg.pressure = [int(max(0, min(65535, x))) for x in data[0:12]]
            msg.header.rows = 3
            msg.header.cols = 4
            msg.header.header.stamp = self.get_clock().now().to_msg()

            self.publisher_.publish(msg)

    def destroy_node(self):
        if hasattr(self, "driver_context"):
            self.driver_context.__exit__(None, None, None)
        super().destroy_node()
