# ROS2 Healthcare Examples

The `ros4hc_examples` repository provides a collection of example applications and nodes demonstrating how to use and visualize biosignals through the given `ros4hc_msgs` interface. These examples are designed to help developers understand the integration of sensors, data processing, and visualization in a ROS 2 environment.

### 1. Applications

The `applications` directory includes example applications that showcase systems using biosignals. The current example focuses on a healthcare wheelchair dashboard, which provides real-time visualization and interaction with biosignal data.

- **`healthcare_wheelchair_dashboard/`**  
  This application serves as a visualization tool for raw signals coming from biosensors such as vivalink, mbient wrist band and pressure mat, as well as thier adl classification
  
- **`topic_visualization/`**  
  This contains examples and tools for visualizing ROS2 topics related to biosignals.

### 2. Nodes

The `nodes` directory contains example publisher and subscriber nodes that demonstrate how to interact with biosignals using the `ros4hc_msgs` interface. These examples shows the starting points to create their own ROS2 nodes for processing or visualizing healthcare data.

