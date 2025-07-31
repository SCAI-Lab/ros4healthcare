import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()

    config = os.path.join(
        get_package_share_directory('sensomative_ros'),
        'config',
        'params.yaml'
        )

    sensomative_node = Node(
        package='sensomative_ros',
        name='sensomative_ros',
        executable='sensomative_wrapper.py',
        parameters=[config],
        output='screen'
    )
    
    visualiser_node = Node(
        package='sensomative_ros',
        name='pressure_visualizer',
        executable='pressure_visualizer.py',
        parameters=[{
            'input_topic': '/pressure1',
            'output_topic': '/pressure_visualizer',
            'array_width': 50,
            'array_height': 50,
            'smoothing_sigma': 3.0,
            'debug_mode': False
        }],
        output='screen'
    )
    
    ld.add_action(sensomative_node)
    ld.add_action(visualiser_node)
    
    return ld