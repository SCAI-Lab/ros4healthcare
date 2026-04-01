import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()

    config = os.path.join(
        get_package_share_directory('polar_ros2'),
        'config',
        'params_two.yaml'
        )

    polar_node=Node(
        package = 'polar_ros2',
        name = 'polar_connector1',
        executable = 'polar_connector',
        parameters = [config],
        output = "screen",
    )
    polar_node2=Node(
        package = 'polar_ros2',
        name = 'polar_connector2',
        executable = 'polar_connector',
        parameters = [config],
        output = "screen",
        remappings=[
            ('/polar_hr', '/polar_hr2') # Remap topic
        ]
    )
    ld.add_action(polar_node)
    ld.add_action(polar_node2)
    return ld
