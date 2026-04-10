import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()

    config_imu = os.path.join(
        get_package_share_directory('mbient_ros'),
        'config',
        'params.yaml'
        )

    mbient_node=Node(
        package = 'mbient_ros',
        name = 'mbient_ros',
        executable = 'mbient_wrapper.py',
        parameters = [config_imu]
    )
    ld.add_action(mbient_node)

    config_corsano = os.path.join(
        get_package_share_directory('corsano_ros'),
        'config',
        'params.yaml'
        )

    corsano_node=Node(
        package = 'corsano_ros',
        name = 'corsano_ros',
        executable = 'corsano_wrapper.py',
        parameters = [config_corsano]
    )
    ld.add_action(corsano_node)

    config_sensomative = os.path.join(
        get_package_share_directory('sensomative_ros'),
        'config',
        'params.yaml'
        )

    sensomative_node=Node(
        package = 'sensomative_ros',
        name = 'sensomative_ros',
        executable = 'sensomative_wrapper.py',
        parameters = [config_sensomative]
    )
    ld.add_action(sensomative_node)
    
    adl_node=Node(
        package = 'healthcare_adl_classifier',
        name = 'healthcare_adl_classifier',
        executable = 'pub_adl',
    )
    ld.add_action(adl_node)

    config_dashboard = os.path.join(
        get_package_share_directory('ros2_dash'),
        'config',
        'params.yaml'
        )
    
    dashboard_node=Node(
        package = 'ros2_dash',
        name = 'ros2_dash',
        executable = 'subscriber',
        output = 'screen',
        parameters = [config_dashboard]
    )
    ld.add_action(dashboard_node)

    return ld
