import re
import traceback
from gi.repository import GLib
import logging as log
from pydbus import SystemBus
from pydbus.proxy import ProxyObject
from typing import List, Optional, Type
from types import TracebackType

from bluetooth_common.helper_functions import (
    find_first_matching_device,
    list_devices,
    trust_device,
)


class BluetoothConnectionError(RuntimeError):
    def __str__(self):
        return f"[BluetoothConnectionError] {self.args[0]}"


class BluetoothConnectionManager:
    def __init__(
        self,
        pattern: re.Pattern,
        adapter: str,
        target_uuids: Optional[List[str]] = None,
        reconnect_delay_s: int = 5,
    ):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.adapter_name = adapter
        self.target_uuids = target_uuids
        self.reconnect_delay_s = reconnect_delay_s

        self.bus = SystemBus()
        self.adapter = self.bus.get("org.bluez", f"/org/bluez/{self.adapter_name}")
        self.manager = self.bus.get("org.bluez", "/")
        self.device_path: Optional[str] = None
        self.device: Optional[ProxyObject] = None

        self.reconnecting = False
        self.connected = False
        self.loop = GLib.MainLoop()

    @property
    def mac_address(self) -> Optional[str]:
        if self.device_path and self.device:
            try:
                return self.device.Get("org.bluez.Device1", "Address")
            except GLib.GError as e:
                log.warning(
                    f"[BluetoothConnectionManager::mac_address] Failed to retrieve MAC: {e}"
                )
        return None

    def __enter__(self) -> "BluetoothConnectionManager":
        self._subscribe_to_disconnects()
        self._ensure_connected()
        return self

    def __exit__(
        self,
        _exc_type: Optional[Type[BaseException]],
        _exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):

        self._disconnect()
        self.loop.quit()

    def _connect_device(self, device_path: str):
        trust_device(bus=self.bus, device_path=device_path)
        self.device = self.bus.get("org.bluez", device_path)
        try:
            self.device.Connect()
            self.device_path = device_path
            self.connected = True
            log.info(
                f"[BluetoothConnectionManager::_connect_device] Connected to {device_path}"
            )
        except GLib.GError as e:
            self.connected = False
            self.adapter.RemoveDevice(device_path)
            raise BluetoothConnectionError(
                f"[_connect_device] Failed to connect to {device_path}. Forgetting current "
                "device and reattempting..."
            )

        except Exception as e:
            self.connected = False
            log.error(
                "[BluetoothConnectionManager::_connect_device] Unknown error when trying "
                f"to connect: {e}"
            )
            raise

    def _disconnect(self):
        if self.device:
            try:
                log.info(
                    "[BluetoothConnectionManager] Finishing. Disconnecting from "
                    f"{self.device_path}"
                )
                self.device.Disconnect()
                self.device = None
                self.device_path = None
                self.connected = False
            except Exception as e:
                log.error(
                    f"[BluetoothConnectionManager] Error while disconnecting: {e}"
                )

    def _ensure_connected(self, rescan: bool = False):
        try:
            device = find_first_matching_device(
                device_list=list_devices(
                    proxy=self.manager, adapter=self.adapter, rescan=rescan
                ),
                pattern=self.pattern,
            )
            if device is None:
                log.warning(
                    "[BluetoothConnectionManager::_ensure_connected] No matching device "
                    f"found for regex {self.pattern}. Rescanning..."
                )
                return self._ensure_connected(rescan=True)
            if device.properties["org.bluez.Device1"].get("Connected", True):
                log.info(
                    "[BluetoothConnectionManager::_ensure_connected] Already connected "
                    f"to {device.properties['org.bluez.Device1']['Name']} at {device.path}"
                )
                self.device_path = device.path
                self.device = self.bus.get("org.bluez", device.path)
                self.connected = True
            else:
                self._connect_device(device.path)

        except BluetoothConnectionError as e:
            log.error(e)
        except Exception as e:
            log.error(
                f"[BluetoothConnectionManager::_ensure_connected] Unknown error: {e}"
            )
            traceback.print_exc()
        finally:
            self._schedule_reconnect()

    def _schedule_reconnect(self):
        if not self.reconnecting:
            self.reconnecting = True
            GLib.timeout_add_seconds(self.reconnect_delay_s, self._try_reconnect)

    def _try_reconnect(self):
        log.info(
            "[BluetoothConnectionManager::_try_reconnect] Attempting to reconnect..."
        )
        self.reconnecting = False
        self._ensure_connected()
        return False  # Don't reschedule this timeout

    def _subscribe_to_disconnects(self):
        def on_props_changed(_sender, obj_path, _iface, _signal, params):
            if obj_path != self.device_path:
                return

            iface_name, changed, _ = params

            if iface_name == "org.bluez.Device1" and "Connected" in changed:
                try:
                    still_connected = self.device.Get("org.bluez.Device1", "Connected")
                except Exception as e:
                    log.warning(
                        f"[BluetoothConnectionManager::_subscribe_to_disconnects] Could "
                        "not get connection state: {e}"
                    )
                    still_connected = False

                if not changed["Connected"] and not still_connected:
                    log.warning(
                        f"[BluetoothConnectionManager::_subscribe_to_disconnects] "
                        f"Device {self.device_path} disconnected."
                    )
                    self.connected = False
                    self._schedule_reconnect()
                else:
                    self.connected = True

        self.bus.subscribe(
            iface="org.freedesktop.DBus.Properties",
            signal="PropertiesChanged",
            signal_fired=on_props_changed,
        )

    def read_characteristic(self):
        if not self.device_path or not self.target_uuids:
            raise BluetoothConnectionError(
                "[read_characteristic] Device or UUID not set."
            )
        target_uuids = [uuid.lower() for uuid in self.target_uuids]

        for path, ifaces in self.manager.GetManagedObjects().items():
            if not path.startswith(self.device_path):
                continue

            char = ifaces.get("org.bluez.GattCharacteristic1", {})
            uuid = char.get("UUID", "").lower()
            if uuid in target_uuids:
                proxy = self.bus.get("org.bluez", path)
                value = proxy.ReadValue({})
                log.debug(
                    f"[BluetoothConnectionManager::read_characteristic] UUID={uuid} → {list(bytes(value))}"
                )
                return value

        log.warning(
            f"[BluetoothConnectionManager::read_characteristic] None of the target UUIDs found: {target_uuids}"
        )
        return None

    def get_data(self) -> Optional[str]:
        if self.connected:
            try:
                return self.read_characteristic()
            except Exception as e:
                log.error(
                    "[BluetoothConnectionManager::start_periodic_read] Failed to "
                    f"read characteristic: {e}"
                )
        return None

    def run_loop(self):
        log.info(
            "[BluetoothConnectionManager::run_loop] Running main loop. Press Ctrl+C to quit."
        )
        try:
            self.loop.run()
        except KeyboardInterrupt:
            log.info(
                "[BluetoothConnectionManager::run_loop] Loop interrupted. Closing..."
            )
            self.loop.quit()
