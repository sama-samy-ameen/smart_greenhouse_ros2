from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='serial_bridge',
            executable='serial_bridge',
            name='serial_bridge',
            output='screen',
        ),
        Node(
            package='climate_controller',
            executable='climate_controller',
            name='climate_controller',
            output='screen',
        ),
        Node(
            package='safety_monitor',
            executable='safety_monitor',
            name='safety_monitor',
            output='screen',
        ),
        Node(
            package='logger_display',
            executable='logger_display',
            name='logger_display',
            output='screen',
        ),
        Node(
            package='gui',
            executable='gui',
            name='gui'
        ),
    ])