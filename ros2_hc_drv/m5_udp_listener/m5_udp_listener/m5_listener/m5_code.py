from m5stack import *
from m5ui import *
from uiflow import *
import network
import socket
import imu
import json
import time

setScreenColor(0x111111) 

#-------Setup---------------------------------

#Network credentials
ssid ='LLUI_LWI_5G'
password = 'CARINg123%'

# Set static IP address of IMU (within the same subnet as your computer)
static_ip = '192.168.1.102'  # Choose an IP address not in use in your network (Convention: part ip_address_computer.10unique_id; Exp: ip_address_computer=192.168.1.192, unique_id= imu_2, static_ip = 192.168.1.102) 
subnet_mask = '255.255.255.0'
gateway = '192.168.1.1'  # Usually the router's IP address
dns = '8.8.8.8'  # Google's public DNS

# Unique identifier for this device
unique_id = 'imu_2' #Convention: imu_x -> x {1,...,n}

#Computer IP and port 
ip_address_computer = '192.168.1.192' 
port = 1234

#Translation frequency in Hz
frequency = 50
interval = 1.0 / frequency

#------------------------------------------------

attempts = 0



# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.ifconfig((static_ip, subnet_mask, gateway, dns))
wlan.connect(ssid, password)

# Wait for connection
while not wlan.isconnected():
    lcd.clear()
    lcd.print('Connecting to WiFi...', 0, 20, 0xFFFFFF)
    time.sleep(1)

lcd.clear()
lcd.print('Connected to WiFi', 10, 10, 0xFFFFFF)

# Initialize IMU
imu0 = imu.IMU()

# UDP setup
udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


lcd.clear()
lcd.print(unique_id, 30, 20, 0xFFFFFF) 

while True:
    try:
        accel_x = imu0.acceleration[0]
        accel_y = imu0.acceleration[1]
        accel_z = imu0.acceleration[2]
        ypr_yaw = imu0.ypr[0]
        ypr_pitch = imu0.ypr[1]
        ypr_roll = imu0.ypr[2]
        gyro_x = imu0.gyro[0]
        gyro_y = imu0.gyro[1]
        gyro_z = imu0.gyro[2]

        # Create a JSON object with accelerometer, YPR, and gyroscope data
        imu_data = {
            'id': unique_id,
            
            'linear_acceleration': {
                'x': accel_x,
                'y': accel_y,
                'z': accel_z
            },
            'orientation': {
                'yaw': ypr_yaw,
                'pitch': ypr_pitch,
                'roll': ypr_roll
            },
            'angular_velocity': {
                'x': gyro_x,
                'y': gyro_y,
                'z': gyro_z
            }
        }
        
        # Convert the JSON object to a string
        imu_data_str = json.dumps(imu_data)

        # Send the data
        udpsocket.sendto(imu_data_str.encode(), (ip_address_computer, port))
    
        # Display the data on the screen
        rectangle0 = M5Rect(0, 60, 800, 800, 0x111111, 0x111111) #clear only part with asterisks 
        asterisks = '*' * ((attempts % 4) + 1)
        lcd.print(asterisks, 40, 120, 0xFFFFFF)
        attempts += 1
        

    except Exception as e:
        lcd.clear()
        lcd.print('Error: {}'.format(e), 0, 20, 0xFF0000)
    
    # Wait for the next interval
    time.sleep(interval)
