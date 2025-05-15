# m5stickc2plus_udp
This repository contains a ROS2 package for interfacing with the M5StickC2 Plus device via UDP. The package includes nodes to receive and publish IMU data.
## Prerequisits 
Make sure you have ROS2 Galactic or another compatible version installed aswell as phyton 3.8+

## Cloning the repository
Open a terminal, navigate into the scr-folder of the desired workspace and use the following command to clone the repository: 

```
git clone git@github.com:SCAI-Lab/m5stickc2plus_udp.git

```

Navigate to the cloned repository and install the necessary Pythond depencencies using:

```
cd m5stickc2plus_udp
pip install -r requirements.txt

```
The requirement.txt is an extensive list containing all the dependencies install on my workspace and not all are needed for it to work. To see what is needed specificly, please take a look [here]m5_udp_listener/package.xml) 

## Building the package 
Navigate to the root of the workspace, source it and build it 
```
cd ~/<workspace name>
source install/setup.bash
colcon build --symlink-install --packages-select src/m5stickc2plus_udp/

```

## M5 Software 
To use the M5 stick the following two softwares have to be downloaded: 
[M5 Burner](https://docs.m5stack.com/en/uiflow/m5burner/intro)
[M5 UIflow](https://docs.m5stack.com/en/uiflow/uiflow_desktop)

### M5 Burner 
After launching the burner you have to search for "UIFlow_StickC_Plus2" Software, connect the M5stick c2 plus with a cabel to the computer and use the "brun" button to burn it onto the stick. Once finished, you have to press the configure button and set the stick to "USB-Mode" to be able to access it through the M5 software.

### M5 UIFlow
After completing the previous steps, open UIFlow and choost the connected device(light orange stick). Choose the mycropython interface on the top of the page and copy the [m5_code](m5_udp_listener/m5_udp_listener/m5_code.py) into the interface. 

## Runnning the Node 
Before runnning the Node, make sure that the M5stick is publishing(indicated by the loading bar on the screen). Open a terminal a terminal and navigate to root of your work, source the setup script, and run the node:


### **4. Setup and Build `m5_udp_listener` (M5 IMU)**
- **Burn firmware** with the correct **local IP address**.
```bash
cd ros4healthcare
colcon build --packages-select m5_udp_listener --symlink-install
source install/setup.bash
```


If you have multiple m5 sticks and set them up according to the description above, a publisher will be created automatically for every acitve m5 sticke once the are turned on and the node is running.
