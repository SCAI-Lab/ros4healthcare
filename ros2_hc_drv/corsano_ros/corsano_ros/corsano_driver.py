import io
import time
import subprocess
import threading
import simplepyble
from corsano_ros.commands import commands, APP_CMD_SET_PLAN, FW_SET_WAKE_UP, CMD_UNKNOWN
from corsano_ros.corsano_enums import PLAN, PLAN_FREQUENCY,check_crc

# BLE Service & Characteristics
CORSANO_SERVICE = "6e400001-b5a3-f393-e0a9-e50e24dcca3e"
WRITE_CHAR = "6e400002-b5a3-f393-e0a9-e50e24dcca3e"
FILE_RX_CHAR = "6e400003-b5a3-f393-e0a9-e50e24dcca3e"
COMMAND_RX_CHAR = "6e400004-b5a3-f393-e0a9-e50e24dcca3e"


class CorsanoDriver:
    """
    High-level interface to a Corsano watch via BLE.
    Supports connection, reconnection, command execution,
    sidechannel streaming, and CRC validation.
    
    Use as a context manager:
        with CorsanoDriver(address, adapter) as driver:
            driver.connect()
            driver.execute(cmd_id)
    """

    def __init__(self, address: str, adapter_address: str):
        self.address = address
        self.adapter_address = adapter_address
        self.adapter = None
        self.peripheral = None

        self.ping = None
        self.commands = {}
        self.stack = {}
        self.buffer = None
        self._start_tx = False

        self.hash_func = check_crc

        self._get_adapter_by_address()
        self._init_hci_reset()
        self._init_commands()

    def _get_adapter_by_address(self):
        """Find BLE adapter by MAC address."""
        for adapter in simplepyble.Adapter.get_adapters():
            if adapter.address() == self.adapter_address:
                self.adapter = adapter
                print("Using adapter:", adapter.address())
                return
        raise RuntimeError("Bluetooth adapter not found.")

    def _init_hci_reset(self):
        """Prepare HCI reset command for reconnection."""
        output = subprocess.check_output(
            f"hcitool dev | grep {self.adapter.address()}", shell=True
        )
        hci_id = output.decode('utf-8').split()[0]
        self.hci_reset_command = f"echo scai | sudo hciconfig {hci_id} reset"

    def _init_commands(self):
        """Initialize command objects."""
        for cmd in commands:
            self.commands[cmd.cmd] = cmd()

    def connect(self, max_retries: int = 5):
        """Connect to the Corsano watch and subscribe to notifications."""
        if self.adapter is None:
            return False

        peripherals = self.adapter.get_paired_peripherals()
        retries = max_retries

        while retries > 0 and self.address not in [p.address() for p in peripherals]:
            print(f"Searching for watch... Attempt {max_retries - retries + 1}/{max_retries}")
            self.adapter.scan_for(5000)
            peripherals.extend(self.adapter.scan_get_results())
            retries -= 1
        if retries == 0:
            return False

        peripheral_map = {p.address(): p for p in peripherals}
        self.peripheral = peripheral_map[self.address]

        for attempt in range(2):
            try:
                self.peripheral.connect()
                if self.peripheral.is_connected():
                    self.peripheral.notify(CORSANO_SERVICE, FILE_RX_CHAR, self._on_file_data)
                    self.peripheral.notify(CORSANO_SERVICE, COMMAND_RX_CHAR, self._on_command_data)
                    print(f"Connected to {self.address}")
                    return True
            except RuntimeError:
                if attempt == 1:
                    self.peripheral.unpair()
                    return False
            print(f"Connection failed, retrying... {attempt + 1}/2")
        return False

    def reconnect(self):
        """Reset adapter and reconnect to the device."""
        subprocess.check_output(self.hci_reset_command, shell=True)
        for dev in self.adapter.get_paired_peripherals():
            dev.unpair()
            time.sleep(1)
        return self.connect()

    def _on_file_data(self, data: bytes):
        """Handle incoming file data (sidechannel)."""
        if self.buffer:
            self._start_tx = True
            self.buffer.write(data)

    def _on_command_data(self, data: bytes):
        """Handle incoming command responses."""
        if self.hash_func(data) != 0:
            print("CRC check failed")
            return

        cmd_id = data[0]
        cmd = self.commands.get(cmd_id)
        if not cmd:
            print(f"Unknown command: {cmd_id}")
            return

        try:
            if cmd_id in (FW_SET_WAKE_UP.cmd, CMD_UNKNOWN.cmd) and self.ping:
                self.ping.update(cmd, cmd.process(data))
            elif cmd_id in self.stack:
                self.stack[cmd_id].set()
                self.stack[cmd_id] = cmd.process(data)
            elif hasattr(cmd, "process"):
                print(cmd.process(data))
            else:
                print(data)
        except Exception as e:
            import traceback
            print(f"Error processing command {cmd_id}: {e}")
            print(traceback.format_exc())

    def execute(self, cmd_id, *args, **kwargs):
        """Execute a command and optionally wait for its response."""
        cmd = self.commands[cmd_id]
        print(f"Executing command {cmd}")

        if cmd.sidechannel:
            if self.buffer:
                self.buffer.close()
            self.buffer = io.BytesIO()
            self._start_tx = False

        self.peripheral.write_command(CORSANO_SERVICE, WRITE_CHAR, cmd.execute(*args, **kwargs))

        if hasattr(cmd, "process"):
            self.stack[cmd_id] = threading.Event()
            if not self.stack[cmd_id].wait(5.0):
                raise TimeoutError(f"Command {cmd_id} timed out")
            return self.stack[cmd_id]
        return None

    def get_buffer(self):
        """Return the buffer for sidechannel data if available."""
        if self.buffer:
            self.buffer.flush()
            self.buffer.seek(0)
            return self.buffer
        
    def set_max_act_plan(self):
        """
        Set the Corsano device to the maximum activity plan.
        Uses PLAN.HOSPITAL_MULTICOLOR, PPG frequency 32 Hz, activity frequency 1 s.
        """
        return self.execute(
            APP_CMD_SET_PLAN.cmd,
            plan=PLAN.HOSPITAL_MULTICOLOR,
            ppgfreq=PLAN_FREQUENCY['FREQ_32HZ'],
            actfreq=1
        )

    def register_ping(self, ping_instance):
        """Register a ping handler for FW_SET_WAKE_UP and CMD_UNKNOWN."""
        self.ping = ping_instance
    
    def write(self, data: bytes):
        """Send raw bytes to the device over BLE."""
        if not self.peripheral or not self.peripheral.is_connected():
            raise RuntimeError("Device not connected")
        self.peripheral.write_command(CORSANO_SERVICE, WRITE_CHAR, data)

    # ---------------- Context Manager ----------------
    def __enter__(self):
        """Connect when entering context."""
        if not self.connect():
            raise RuntimeError("Failed to connect to Corsano device")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnect when exiting context."""
        if self.peripheral and self.peripheral.is_connected():
            self.peripheral.disconnect()
