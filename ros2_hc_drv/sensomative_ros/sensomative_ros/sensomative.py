import time
import sys
from rclpy.node import Node
import simplepyble

class SensomativeDriver(Node):
    def __init__(self, address, hci_mac=None):
        super().__init__('sensomative_driver')
        
        self.peripheral = None
        self.address = address
        self.device_exists = False

        ## logger init
        self.logger_ = self.get_logger()
        self.logger_.info('Publishing sensomative data')
        self.get_logger().info('Attempting to connect to device: "%s"' % self.address)

        ## try connection with the devices
        adapter = None
        all_adapters = simplepyble.Adapter.get_adapters()
        if hci_mac is not None:
            for adapt in all_adapters:
                if adapt.address() == hci_mac.upper():
                    adapter = adapt
                    break
        if adapter is None:
            adapter = all_adapters[0]

        self.logger_.info('Scanning for 10 seconds...')
        adapter.scan_for(10000)  
        peripherals = adapter.scan_get_results()
        self.logger_.info('Found %d peripherals' % len(peripherals))
        self.peripherals = {x.address():x for x in peripherals}

        # List all peripherals found
        for address, peripheral in self.peripherals.items():
            self.device_exists = True
            self.logger_.info('Found peripheral at address: %s' % address)

        if not self.connect_peripheral():
            sys.exit('Failed to connect to peripheral')

    def get_data(self):
        return list(self.peripheral.read("000055c0-0000-1000-8000-00805f9b34fb", "000055c2-0000-1000-8000-00805f9b34fb"))

    def get_device_exists(self):
        return self.device_exists
    
    def connect_peripheral(self, max_retries=10, retry_delay=5.0):
        # Check if the device address exists in the peripheral list
        if self.address not in self.peripherals:
            self.logger_.info('Peripheral %s not found' % self.address)
            self.peripheral = None
            return False

        # If device address exists, attempt to connect
        self.peripheral = self.peripherals[self.address]
        for attempt in range(max_retries):
            try:
                self.peripheral.connect()
                self.logger_.info('Connected to peripheral: %s' % self.address)
                return True
            except Exception as e:
                self.logger_.info('Failed to connect to peripheral: %s' % self.address)
                self.logger_.info('Error: %s' % str(e))
                if attempt < max_retries - 1:  # if it's not the last attempt
                    time.sleep(retry_delay)  # delay before next attempt
                else:
                    self.peripheral = None
                    return False


    def __del__(self):
        if self.peripheral:
            self.peripheral.disconnect()


