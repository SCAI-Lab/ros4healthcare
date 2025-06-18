import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    ld = LaunchDescription()

    polar_config = os.path.join(
        get_package_share_directory('polar_ros2'),
        'config',
        'params.yaml'
        )

    polar_node=Node(
        package = 'polar_ros2',
        name = 'polar_connector',
        executable = 'polar_connector',
        parameters = [polar_config]
    )
    ld.add_action(polar_node)

    sensomative_config = os.path.join(
        get_package_share_directory('ros2_hc_launch'),
        'config',  
        'params.yaml'
    )

    sensomative_node = Node(
        package='sensomative_ros',
        executable='sensomative_wrapper.py',
        name='sensomative_ros',
        parameters=[sensomative_config],
        output='screen'
    )
    ld.add_action(sensomative_node)

    m5_node = Node(
        package='m5_udp_listener',
        executable='m5_listener_multiple.py',
        name='sensomative_ros',
        output='screen'
    )
    ld.add_action(m5_node)

    return ld
