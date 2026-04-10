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
        executable='sensomative.py',
        parameters=[config],
        output='screen'
    )

    ld.add_action(sensomative_node)

    return ld
