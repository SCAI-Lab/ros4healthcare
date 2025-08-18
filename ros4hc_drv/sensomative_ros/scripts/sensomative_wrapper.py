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
        "--mac-address",
        type=str,
        default=None,
        help="MAC address of the device (optional)",
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
    args, _unknown = parser.parse_known_args()

    rclpy.init()

    node = SensomativeRos(
        regex_pattern=args.regex_pattern,
        adapter=args.adapter,
        mac_address=args.mac_address,
        target_uuids=args.target_uuids,
    )

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        log.info("Ctrl+C received. Shutting down Sensomative node cleanly.")
    except rclpy._rclpy_pybind11.RCLError as e:
        log.warning(f"Caught an rclpy exception. Attempting shutdown {e}")
    finally:
        try:
            node.destroy_node()
            rclpy.shutdown()
        except rclpy._rclpy_pybind11.RCLError as e:
            log.warning(f"Could not shut down ros cleanly: {e}")

if __name__ == "__main__":
    main()
