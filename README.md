<h1 align="center">
<img src="assets/ROS4HC Logo.png" width="550">
</h1><br>

# ROS4 Healthcare

Welcome to the **ROS4 Healthcare** project! This repository contains ROS2 packages for healthcare applications, including message definitions, drivers, libraries, tools, and examples. **`ros4hc`** serves as an example of how one can use biosignals coming from wearable medical devices like Vivalink and mbient wristbands to track patients' activities. In addition, we have developed an Activities of Daily Living (ADL) classifier that will help doctors visualize their patients' daily activity patterns and consequently help them recommend a suitable routine. This can be visualised through our `healthcare_wheelchair_dashboard`.


## Repository Structure

- **`ros2_hc_drv`**: Includes drivers for various biosensors.
- **`ros2_hc_examples`**: Example applications and use cases demonstration.
- **`ros2_hc_lib`**: Libraries
- **`ros2_hc_msgs`**: Contains all message definitions and structure for biosensor data.
- **`ros2_hc_launch`**: Example launch files
- **`ros2_hc_tools`**: Tools and utilities for development and operation.



```
ros2-healthcare
├── ros2_hc_drv
│   ├── mbient_ros
│   │   ├── CMakeLists.txt
│   │   ├── config
│   │   ├── launch
│   │   ├── mbient_ros
│   │   └── scripts
│   ├── sensomative_ros
│   │   ├── config
│   │   ├── launch
│   │   ├── scripts
│   │   └── sensomative_ros
│   └── corsano_ros
│       ├── config
│       ├── launch
│       ├── scripts
│       └── corsano_ros
├── ros2_hc_examples
│   ├── applications
│   │   ├── healthcare_wheelchair_dashboard
│   │   └── topic_visualization
│   └── nodes
│       └── example_nodes
├── ros2_hc_lib
│   └── healthcare_adl_classifier
├── ros2_hc_msgs
│   ├── msg
│   │   ├── biometrics
│   │   │   ├── behavioral
│   │   │   │   └── mood
│   │   │   ├── physiological
│   │   │   │   ├── adl
│   │   │   │   ├── gait
│   │   │   │   └── posture
│   │   ├── biosensing
│   │   │   ├── derived_biosignals
│   │   │   │   ├── co
│   │   │   │   ├── hr
│   │   │   │   ├── hrv
│   │   │   │   ├── rr
│   │   │   │   └── sv
│   │   │   ├── raw_biosignals
│   │   │   │   ├── bcg
│   │   │   │   ├── ecg
│   │   │   │   ├── eda
│   │   │   │   ├── eeg
│   │   │   │   ├── emg
│   │   │   │   ├── eog
│   │   │   │   ├── icg
│   │   │   │   └── ppg
│   │   ├── physical_sensors
│   │   │   ├── derived_signals
│   │   │   │   ├── elevation_angle
│   │   │   │   ├── joint_angles
│   │   │   │   ├── joint_angular_velocity
│   │   │   │   ├── pose
│   │   │   │   └── steps
│   │   │   ├── external_signals
│   │   │   │   ├── force
│   │   │   │   └── pressure
└── ros2_hc_launch
│   ├── config
│   │   └── ros2_hc_params.yaml
│   └── launch
│   │   └── ros2_hc_launch.py
│   └── README.md
└── ros2_hc_tools
```
## Setup



We then need to clone the repositories into our workspace

```
cd ros2_ws/src
git clone --recurse-submodules git@github.com:SCAI-Lab/ros2_healthcare.git
cd ..
```
then build and source the workspace 

```
colcon build --symlink-install
source install/setup.bash
```

## Running the Wrappers

We have included wrappers for several devices in the `ros2_hc_drv` repository.

Each wrapper receives either a device mac address or a file path as a parameter. Feel free to change the parameters in the respective config/params.yaml
file for each device wrapper.

To run the wrappers for BLE devices, make sure the PC Bluetooth is on, the device is charged and is nearby, then run the wrapper

by running ```ros2 launch package_name launch_file```  

To run our dashboard, we will need to connect to the mbient sensor and to the sensomative mat, for this run:

```
ros2 launch mbient_ros mbient_node.launch.py
```

in a new terminal, source the repo and run the sensomative launch file

```
source install/setup.bash
ros2 launch sensomative_ros sensomative_node.launch.py
```

## Running ADL Classifier 

In order to have our model classify the data coming from the wearable devices, we need to run the healthcare_adl_classifier

To do this open a new tab, source the repo and run

```
source install/setup.bash
ros2 run healthcare_adl_classifier pub_adl
```


We first need to make sure our python environment is well set up

simply run ```pip install -r requirements.txt``` to install the dependencies


We then need to clone the repositories into our workspace

```
cd ros2_ws/src
git clone --recurse-submodules git@github.com:SCAI-Lab/ros2_healthcare.git
cd ..
```
then build and source the workspace 

```
colcon build --symlink-install
source install/setup.bash
```

## Running the Wrappers

We have included wrappers for several devices in the `ros2_hc_drv` repository.

Each wrapper receives either a device mac address or a file path as a parameter. Feel free to change the parameters in the respective config/params.yaml
file for each device wrapper.

To run the wrappers for BLE devices, make sure the PC Bluetooth is on, the device is charged and is nearby, then run the wrapper

by running ```ros2 launch package_name launch_file```  

To run our dashboard, we will need to connect to the mbient sensor and to the sensomative mat, for this run:

```
ros2 launch mbient_ros mbient_node.launch.py
```

in a new terminal, source the repo and run the sensomative launch file

```
source install/setup.bash
ros2 launch sensomative_ros sensomative_node.launch.py
```

## Running ADL Classifier 

In order to have our model classify the data coming from the wearable devices, we need to run the healthcare_adl_classifier

To do this open a new tab, source the repo and run

```
source install/setup.bash
ros2 run healthcare_adl_classifier pub_adl
```


# Acknowledgments

<!-- ![JST Moonshot R&D Logo](https://example.com/jst_logo.png)  ![ETH-SPS Logo](https://example.com/eth_logo.png) -->

This work was partially supported by:

- The JST Moonshot R&D Program [Grant Number JPMJMS2034]
- The ETH-SPS Digital Transformation in Personalized Health Care for SCI [Grant Number: 2021-HS-348]

<h1 align="center">
<img src="assets/Acknowledgement_JST_2.png" width="550">
</h1><br>
