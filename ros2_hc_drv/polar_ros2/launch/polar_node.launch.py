import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()

    config = os.path.join(
        get_package_share_directory('polar_ros2'),
        'config',
        'params.yaml'
        )

    polar_node=Node(
        package = 'polar_ros2',
        name = 'polar_connector',
        executable = 'polar_connector',
        parameters = [config]
    )
    ld.add_action(polar_node)

    return ld
