from bleak import BleakClient
import asyncio
import logging as log
import time
import numpy as np
import math
from ros4hc_msgs.msg import HR
from geometry_msgs.msg import Vector3Stamped


class PolarH10:
    HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
    HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
    PMD_SERVICE_UUID = "fb005c80-02e7-f387-1cad-8acd2d8df0c8"
    PMD_CHAR1_UUID = "fb005c81-02e7-f387-1cad-8acd2d8df0c8"
    PMD_CHAR2_UUID = "fb005c82-02e7-f387-1cad-8acd2d8df0c8"

    ECG_WRITE = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])
    ACC_WRITE = bytearray([0x02, 0x02, 0x00, 0x01, 0xC8, 0x00, 0x01, 0x01, 0x10, 0x00, 0x02, 0x01, 0x08, 0x00])

    ACC_SAMPLING_FREQ = 200
    ECG_SAMPLING_FREQ = 130
    MAX_DATA_AGE_SEC = 1.0

    def __init__(self, node, bleak_device, bt_adapter, publish_acceleration, publish_hr, publish_ecg):
        self.bleak_device = bleak_device
        self.bt_adapter = bt_adapter
        self.node = node
        self.publish_acceleration = publish_acceleration
        self.publish_hr = publish_hr
        self.publish_ecg = publish_ecg
        self.combined_streaming_active = False
        self.hr_streaming_active = False

        self.acc_stream_values = []
        self.acc_stream_times = []
        self.ecg_stream_values = []
        self.ecg_stream_times = []
        self.ibi_stream_values = []
        self.ibi_stream_times = []

        if publish_acceleration:
            self.pub_acc = self.node.create_publisher(Vector3Stamped, "polar_acc", 10)
        if publish_hr:
            self.pub_hr = self.node.create_publisher(HR, "polar_hr", 10)
        if publish_ecg:
            self.pub_ecg = self.node.create_publisher(Vector3Stamped, "polar_ecg", 10)

    async def connect(self):
        try:
            self.bleak_client = BleakClient(self.bleak_device, adapter=self.bt_adapter)
            await self.bleak_client.connect(timeout=20.0)
            print("Connected!")
            self.bleak_client.set_disconnected_callback(self.handle_disconnect)
        except asyncio.TimeoutError:
            log.error("[PolarH10::connect] Connection failed. Retrying...")
            await self.connect()

    def handle_disconnect(self, client):
        log.warning(f"[PolarH10] Disconnected. Reconnecting...")
        asyncio.create_task(self.connect())

    async def disconnect(self):
        if self.bleak_client and self.bleak_client.is_connected:
            await self.bleak_client.disconnect()
            print("Disconnected.")

    async def start_combined_stream(self):
        await self.bleak_client.write_gatt_char(self.PMD_CHAR1_UUID, self.ECG_WRITE, response=True)
        await self.bleak_client.write_gatt_char(self.PMD_CHAR1_UUID, self.ACC_WRITE, response=True)
        await self.bleak_client.start_notify(self.PMD_CHAR2_UUID, self.pmd_data_conv)
        self.combined_streaming_active = True
        print("Streaming ECG and ACC...")

    async def stop_combined_stream(self):
        if self.bleak_client and self.bleak_client.is_connected and self.combined_streaming_active:
            try:
                await self.bleak_client.stop_notify(self.PMD_CHAR2_UUID)
                print("Stopped streaming ECG and ACC.")
            except Exception as e:
                log.warning(f"[PolarH10] Failed to stop notify: {e}")
            self.combined_streaming_active = False

    async def start_hr_stream(self):
        await self.bleak_client.start_notify(self.HEART_RATE_MEASUREMENT_UUID, self.hr_data_conv)
        self.hr_streaming_active = True
        print("Started HR stream.")


    async def stop_hr_stream(self):
        if self.bleak_client and self.bleak_client.is_connected and self.hr_streaming_active:
            try:
                await self.bleak_client.stop_notify(self.HEART_RATE_MEASUREMENT_UUID)
                print("Stopped HR stream.")
            except Exception as e:
                log.warning(f"[PolarH10] Failed to stop HR notify: {e}")
            self.hr_streaming_active = False


    def pmd_data_conv(self, sender, data):
        if data[0] == 0x00:
            self.ecg_data_conv(sender, data)
        elif data[0] == 0x02:
            self.acc_data_conv(sender, data)

    def hr_data_conv(self, sender, data):
        flags = data[0]
        hr_format = (flags & 0x01) == 0
        rr_present = (flags >> 4) & 1
        if not rr_present:
            return

        index = 2 if hr_format else 3
        hr = data[1] if hr_format else (data[2] << 8) | data[1]

        if self.publish_hr:
            hr_msg = HR()
            hr_msg.hr = hr
            hr_msg.header.header.stamp = self.node.get_clock().now().to_msg()
            self.pub_hr.publish(hr_msg)

        if (flags >> 3) & 1:  # Skip energy exp
            index += 2
        for i in range(index, len(data), 2):
            ibi = (data[i + 1] << 8) | data[i]
            ibi_ms = np.ceil(ibi / 1024 * 1000)
            self.ibi_stream_values.append(ibi_ms)
            self.ibi_stream_times.append(time.time_ns() / 1e9)

    def acc_data_conv(self, sender, data):
        if data[0] != 0x02:
            return
        timestamp = self.convert_to_unsigned_long(data, 1, 8) / 1e9
        frame_type = data[9]
        resolution = (frame_type + 1) * 8
        time_step = 1.0 / self.ACC_SAMPLING_FREQ
        step = math.ceil(resolution / 8.0)
        samples = data[10:]
        offset = 0
        n_samples = len(samples) // (3 * step)
        sample_timestamp = timestamp - (n_samples - 1) * time_step

        while offset + 3 * step <= len(samples):
            x = self.convert_array_to_signed_int(samples, offset, step)
            y = self.convert_array_to_signed_int(samples, offset + step, step)
            z = self.convert_array_to_signed_int(samples, offset + 2 * step, step)
            offset += 3 * step
            self.acc_stream_values.append([x, y, z])
            self.acc_stream_times.append(sample_timestamp)
            if self.publish_acceleration:
                msg = Vector3Stamped()
                msg.header.stamp = self.node.get_clock().now().to_msg()
                msg.vector.x = x / 1000
                msg.vector.y = y / 1000
                msg.vector.z = z / 1000
                self.pub_acc.publish(msg)
            sample_timestamp += time_step

    def ecg_data_conv(self, sender, data):
        timestamp = self.convert_to_unsigned_long(data, 1, 8) / 1e9
        time_step = 1.0 / self.ECG_SAMPLING_FREQ
        step = 3
        samples = data[10:]
        sample_timestamp = timestamp - ((len(samples) // step) - 1) * time_step
        offset = 0

        while offset + step <= len(samples):
            ecg_val = self.convert_array_to_signed_int(samples, offset, step)
            self.ecg_stream_values.append(ecg_val)
            self.ecg_stream_times.append(sample_timestamp)
            if self.publish_ecg:
                ecg_msg = Vector3Stamped()
                ecg_msg.header.stamp = self.node.get_clock().now().to_msg()
                ecg_msg.vector.x = ecg_val / 1000.0
                self.pub_ecg.publish(ecg_msg)
            offset += step
            sample_timestamp += time_step

    @staticmethod
    def convert_array_to_signed_int(data, offset, length):
        return int.from_bytes(data[offset:offset + length], byteorder="little", signed=True)

    @staticmethod
    def convert_to_unsigned_long(data, offset, length):
        return int.from_bytes(data[offset:offset + length], byteorder="little", signed=False)

    def get_acc_data(self):
        times = np.array(self.acc_stream_times)
        if len(times) == 0:
            return None
        latest_time = times[-1]
        return {
            'times': times - times[0],
            'values': np.array(self.acc_stream_values)
        }

    def get_ibi_data(self):
        if not self.ibi_stream_times:
            return None
        times = np.array(self.ibi_stream_times)
        latest_time = times[-1]
        return {
            'times': times - times[0],
            'values': np.array(self.ibi_stream_values)
        }
