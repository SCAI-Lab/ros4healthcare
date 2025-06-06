#!/usr/bin/env python3

import argparse
import logging as log
import rclpy

from sensomative_ros.sensomative_ros import SensomativeRos


def main():
    parser = argparse.ArgumentParser(description="Run the Sensomative ROS 2 Node")
    parser.add_argument(
        "--regex-pattern", type=str, default="^Sensomative.*", help="Regex to match device name"
    )
    parser.add_argument(
        "--adapter", type=str, default="hci0", help="Bluetooth adapter name"
    )
    parser.add_argument(
        "--target-uuids",
        type=str,
        nargs="+",
        default=[
            "000055c0-0000-1000-8000-00805f9b34fb",
            "000055c2-0000-1000-8000-00805f9b34fb",
        ],
        help="List of target GATT characteristic UUIDs",
    )
    args = parser.parse_args()

    rclpy.init()

    print("Hello")
    
    try:
        print("Start")
        node = SensomativeRos(
            regex_pattern=args.regex_pattern,
            adapter=args.adapter,
            target_uuids=args.target_uuids,
        )
        rclpy.spin(node)
    except KeyboardInterrupt:
        log.info("Sensomative Node received an interrupt signal, shutting down.")
    except Exception as e:
        log.error("An error occurred in Sensomative Wrapper:", str(e))
    finally:
        print("Finally")
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
