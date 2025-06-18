
from dataclasses import dataclass
from gi.repository import GLib
import logging as log
from pydbus import SystemBus
from pydbus.proxy import ProxyObject
from re import Pattern
import time
from typing import Any, Dict, Optional

@dataclass
class BluetoothDevice:
    path: str
    properties: Dict[str, Any]


def list_devices(proxy: ProxyObject, adapter: ProxyObject, rescan: bool, scan_time_s: int = 3):
    if rescan:
        try:
            adapter.StartDiscovery()
            time.sleep(scan_time_s)  # Allow time for device discovery
            adapter.StopDiscovery()
        except Exception as e:
            log.error(f"[bluetooth_common::list_devices] Failed to rescan: {e}")

    return {
        path: props
        for path, props in proxy.GetManagedObjects().items()
        if "org.bluez.Device1" in props
    }

def find_first_matching_device(device_list: Dict[str, Any], pattern: Pattern) -> Optional[BluetoothDevice]:
    for path, props in device_list.items():
        name = props["org.bluez.Device1"].get("Name", "")
        if pattern.match(name):
            return BluetoothDevice(path=path, properties=props)
    return None


def trust_device(bus: SystemBus, device_path: str):
    try:
        device = bus.get("org.bluez", device_path)
        props_iface = device["org.freedesktop.DBus.Properties"]

        # Set "Trusted" to True
        props_iface.Set("org.bluez.Device1", "Trusted", GLib.Variant("b", True))
        log.debug(f"[bluetooth_common::trust_device] Device at {device_path} trusted.")
    except Exception as e:
        log.error(f"[bluetooth_common::trust_device] Could not trust the device: {e}")
