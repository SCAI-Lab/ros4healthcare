std_msgs/Header header

uint16 rows                           # Number of rows in the pressure grid
uint16 cols                           # Number of columns in the pressure grid
float32 resolution                    # Spatial resolution [meters per cell]
float32[] pressures                   # Flattened row-major pressure data [kPa]
