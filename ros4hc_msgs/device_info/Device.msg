std_msgs/Header header

string 	device_manufacturer             # Name of the device manufacturer
string 	device_name                     # Name of the device
string 	device_type                     # What the device is used for (sensors included)
float32	battery_level                   # Remaining battery level from 0-1 [%]

float32	minimal_operation_temperature   # Minimal temperature required in degree celsius [°C]
float32	maximal_operation_temperature   # Maximal temperature required in degree celcius [°C]
float32	maximal_relative_humidity       # Maximal relative humdidity tolerated by device from 0-1 [%]
float32	minimal_atmospheric_pressure    # Minimal required atmospheric pressure in [atm]
float32	maximal_atmospheric_pressure    # Maximal atomspheric pressure in [atm]
