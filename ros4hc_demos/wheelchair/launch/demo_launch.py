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
        name = 'polar',
        executable = 'polar_connector',
        parameters = [polar_config]
    )
    ld.add_action(polar_node)

    sensomative_node = Node(
        package='sensomative_ros',
        executable='sensomative_wrapper.py',
        name='sensomative',
        parameters=['--adapter', 'hci0'],
        output='screen'
    )
    ld.add_action(sensomative_node)

    sensomative_visualizer = Node(
        package='sensomative_ros',
        executable='pressure_visualizer.py',
        name='sensomative_visualizer',
        parameter=[{'adapter': 'hci1'}]
        output='screen'
    )
    ld.add_action(sensomative_visualizer)

    m5_node = Node(
        package='m5_udp_listener',
        executable='udp_listener_multiple',
        name='m5_udp_multiple',
        output='screen'
    )
    ld.add_action(m5_node)

    return ld
