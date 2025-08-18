from commands import commands, FW_SET_WAKE_UP, CMD_UNKNOWN
import simplepyble
import threading
from util import check_crc
import io
import time
import subprocess

CORSANO_SERVICE           = "6e400001-b5a3-f393-e0a9-e50e24dcca3e"
WRITE_CHARACTERISTIC      = "6e400002-b5a3-f393-e0a9-e50e24dcca3e"
FILE_RX_CHARACTERISTIC    = "6e400003-b5a3-f393-e0a9-e50e24dcca3e"
COMMAND_RX_CHARACTERISTIC = "6e400004-b5a3-f393-e0a9-e50e24dcca3e"

class CorsanoInterface:
    ping = None
    stack = {}
    buffer = None
    m_block = True
    start_tx = False

    def __init__(self, address, adapter_address):
        self.hash_func = check_crc
        self.address = address
        self.adapter_address = adapter_address
        self.adapter = None

        self.get_adapter_by_address()

        hci_command = "hcitool dev | grep " + self.adapter.address()
        output = subprocess.check_output(hci_command, shell=True)
        output_str = output.decode('utf-8')
        hci_id = ' '.join(output_str.split()[0:1])
        self.hci_reset_command = "echo scai | sudo hciconfig " + hci_id + " reset"

    def get_adapter_by_address(self):
        adapter = None
        all_adapters = simplepyble.Adapter.get_adapters()
        for ind in range(len(all_adapters)):
            if all_adapters[ind].address() == self.adapter_address:
                self.adapter = simplepyble.Adapter.get_adapters()[ind]
                break        
        if self.adapter:
            print("Using adapter with mac address:", self.adapter.address())
        else:
            print("Bluetooth adapter not found.")

    def reconnect(self):
        subprocess.check_output(self.hci_reset_command, shell=True)
        conn_dev = self.adapter.get_paired_peripherals()
        for dev in range(len(conn_dev)):
            conn_dev[dev].unpair()
            time.sleep(1)

        return self.connect()

    def connect(self):
        # subprocess.check_output(self.hci_reset_command, shell=True)
        retry = 5
        if self.adapter == None : return False
        # print("Connecting: already connected hardware to adapter:", len(self.adapter.get_paired_peripherals()))
        
        peripherals = self.adapter.get_paired_peripherals()
        
        while (retry > 0 and self.address not in [x.address() for x in peripherals]):
            print(f"Searching for Watch. Try {6 - retry} / 5")
            self.adapter.scan_for(5000)
            peripherals.extend(self.adapter.scan_get_results())
            retry -= 1
            
        if retry == 0:
            return False
        
        p = {x.address(): x for x in peripherals}
        self.peripheral = p[self.address]
        retry = 2
        connected = False
        while (retry > 0):
            try:
                self.peripheral.connect()
            except RuntimeError:
                if retry == 1:
                    self.peripheral.unpair()
                    return False
            if self.peripheral.is_connected():
                self.peripheral.notify(CORSANO_SERVICE, FILE_RX_CHARACTERISTIC, self.transfer)
                self.peripheral.notify(CORSANO_SERVICE, COMMAND_RX_CHARACTERISTIC, self.rx)
                connected = True
                break
            retry -= 1
            print(f"Could not connect, retrying... {2 - retry} / 2")
        
        if not connected:
            return False

        
        self.commands = {}
        for cmd in commands:
            self.commands[cmd.cmd] = cmd()
        return True

    def block(self):
        self.m_block = threading.Event()
        self.start_tx = False
        while not self.start_tx:
            pass
        while self.m_block.wait(0.2):
            self.m_block.clear()
            yield self.buffer.tell()
        return True
    def __del__(self):
        if hasattr(self, "peripheral"):
            self.peripheral.disconnect()
    def transfer(self, data):
        if self.buffer:
            self.start_tx = True
            self.buffer.write(data)
            # self.m_block.set()
    def rx(self, data):
        if self.hash_func(data) == 0:
            cmd = self.commands[data[0]]
            try:
                if data[0] in (FW_SET_WAKE_UP.cmd, CMD_UNKNOWN.cmd):
                    if self.ping:
                        self.ping.update(cmd, cmd.process(data))
                else:
                    if cmd.cmd in self.stack:
                        self.stack[cmd.cmd].set()
                        self.stack[cmd.cmd] = cmd.process(data)
                    else:
                        if hasattr(cmd, "process"):
                            print(cmd.process(data))
                        else:
                            print(data)
            except Exception as e:
                print(e)
                import traceback; print(traceback.format_exc())
        else:
            print("Hash failed")
    def get_buffer(self):
        if self.buffer:
            self.buffer.flush()
            self.buffer.seek(0)
            return self.buffer
    def register_ping(self, instance):
        self.ping = instance
    def write(self, data):
        self.peripheral.write_command(CORSANO_SERVICE, WRITE_CHARACTERISTIC, data)
    def execute(self, cmd, *args, **kwargs):
        if self.commands[cmd].sidechannel:
            # Command uses the sidechannel prepare to receive data
            if self.buffer:
                self.buffer.close()
            self.buffer = io.BytesIO()
        self.write(self.commands[cmd].execute(*args, **kwargs))
        if hasattr(self.commands[cmd], "process"):
            self.stack[cmd] = threading.Event()
            if not self.stack[cmd].wait(2.0):
                print("Command timed out")
                raise TimeoutError("Command exceeded timeout.")
            return self.stack[cmd]
        return None

def main():
    import cli
    cli.main()

if __name__ == "__main__":
    main()