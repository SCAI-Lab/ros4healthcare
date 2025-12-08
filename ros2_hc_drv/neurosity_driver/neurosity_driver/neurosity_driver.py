#!/usr/bin/env python3
import os
from dotenv import load_dotenv

import rclpy
from rclpy.node import Node
from healthcare_msgs.msg import EEG, EEGInfo

from neurosity import NeurositySDK

load_dotenv()

class NeurosityEEGDriver(Node):
    def __init__(self):
        super().__init__('neurosity_eeg_driver')

        # ROS publishers
        self.eeg_pub = self.create_publisher(EEG, 'neurosity/eeg', 10)
        # TODO: Make latched topic
        self.eeg_info_pub = self.create_publisher(EEGInfo, 'neurosity/eeg_info', 1)
        self.info_published = False

        # Neurosity SDK
        self.sdk = NeurositySDK({"device_id": os.getenv("NEUROSITY_DEVICE_ID")})
        self.sdk.login({
            "email": os.getenv("NEUROSITY_EMAIL"),
            "password": os.getenv("NEUROSITY_PASSWORD")
        })

        self.get_logger().info("Subscribed to Neurosity EEG stream")
        self.unsubscribe = self.sdk.brainwaves_raw(self.brainwave_callback)
        # Use .brainwaves_raw_unfiltered() if you want raw unfiltered

    def brainwave_callback(self, data):
        """
        Example structure of `data` returned by NeurositySDK:
        {
            'data': [[ch1_samples], [ch2_samples], ...],
            'info': {
                'samplingRate': 256,
                'channelNames': ['FP1', 'FP2', ...],
                'notchFrequency': 60,
                ...
            }
        }
        """
        eeg_msg = EEG()
        eeg_msg.header.stamp = self.get_clock().now().to_msg()
        eeg_msg.header.frame_id = 'neurosity'
        eeg_msg.session_id = getattr(data.get('info', {}), 'session_id', 'unknown')

        channels = data['data']
        if not channels:
            return

        # Flatten: [channel][sample] -> 1D array
        flattened = []
        for ch in channels:
            flattened.extend(ch)

        eeg_msg.sample_size = len(channels[0])
        eeg_msg.eeg = flattened
        eeg_msg.quality = [1.0]*len(channels)  # Placeholder; Neurosity SDK may not provide per-channel quality

        self.eeg_pub.publish(eeg_msg)

        if not self.info_published:
            # EEGInfo
            info_msg = EEGInfo()
            info_msg.device_info.session_id = getattr(data.get('info', {}), 'session_id', 'unknown')
            info_msg.channel_size = len(channels)
            info_msg.units = EEGInfo.UNIT_UV  # typical for EEG
            info_msg.selected_preprocessing = [EEGInfo.EEG_PREPROC_NOTCH, EEGInfo.EEG_PREPROC_BANDPASS]
            info_msg.montage_type = EEGInfo.MONTAGE_TYPE_REFERENTIAL
            info_msg.electrode_sites = [getattr(EEGInfo, f"ELECTRODE_{name.upper()}", EEGInfo.ELECTRODE_CUSTOM)
                                        for name in data.get('info', {}).get('channelNames', [])]
            info_msg.electrode_physical_type = [EEGInfo.ELECTRODE_PHYSICAL_AGCL]*len(channels)
            info_msg.placement_method = [EEGInfo.PLACEMENT_METHOD_1020]*len(channels)
            info_msg.signal_mode = EEGInfo.SIGNAL_MODE_SURFACE

            self.eeg_info_pub.publish(info_msg)
            self.info_published = True

def main(args=None):
    rclpy.init(args=args)
    node = NeurosityEEGDriver()
    rclpy.spin(node)
    node.unsubscribe()  # cleanup
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
