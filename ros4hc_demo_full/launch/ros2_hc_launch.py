import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    ld = LaunchDescription()

    # Parameters for mbient_ros node
    mbient_config = os.path.join(
        get_package_share_directory('ros2_hc_launch'),
        'config',
        'params.yaml'
    )

    # Node for mbient_ros
    mbient_node = Node(
        package='mbient_ros',
        executable='mbient_wrapper.py',
        name='mbient_ros',
        parameters=[mbient_config],
        output='screen'
    )
    ld.add_action(mbient_node)

    # Parameters for sensomative_ros node
    sensomative_config = os.path.join(
        get_package_share_directory('ros2_hc_launch'),
        'config',  
        'params.yaml'
    )

    # Node for sensomative_ros
    sensomative_node = Node(
        package='sensomative_ros',
        executable='sensomative_wrapper.py',
        name='sensomative_ros',
        parameters=[sensomative_config],
        output='screen'
    )
    ld.add_action(sensomative_node)

    # Node for healthcare_adl_classifier
    adl_node = Node(
        package='healthcare_adl_classifier',
        executable='pub_adl',
        name='adl_classifier',
        parameters=[mbient_config],
        output='screen'
    )
    ld.add_action(adl_node)

    # Node for dashboard
    dashboard_node = Node(
        package='dashboard',
        executable='dashboard',
        name='dashboard',
        parameters=[mbient_config],
        output='screen'
    )
    ld.add_action(dashboard_node)

    return ld
