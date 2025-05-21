# ROS2 Healthcare Launch

This directory contains example configuration and launch files for the ros2_hc system. These examples are designed to help you get started with creating your own launch configs and parameter files.

## Directory Structure

- **`ros2_hc_launch/config`**: Contains example configuration files such as `params.yaml`. Use these files as a reference to create your own configuration files.
- **`ros2_hc_launch/launch`**: Contains example launch files such as `launch.py`. This file demonstrates how to start nodes and apply configurations.

## Example Configuration File

The `params.yaml` file contains example parameters for configuring different ROS2 nodes. Customize these parameters according to your setup and needs.

## Example Launch File

The `hc.launch.py` file provides an example of how to launch nodes with the specified configurations. Modify this file to include the nodes you need and adjust the parameters as necessary.

## Creating Your Own Launch Files

1. **Configuration Files:**
   - Create your own YAML configuration files in the `config` directory.
   - Define parameters such as sensor settings and node configurations.

2. **Launch Files:**
   - Use the example launch file as a template.
   - Add nodes and configurations specific to your setup.

## Getting Started

To use the example launch file:

1. Place your configuration files in the `config` directory.
2. Update `hc.launch.py` to include your nodes and configurations.
3. Run the launch file using ROS2 launch commands.



