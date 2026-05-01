import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # 1. Display Dual System in Rviz
    display_launch_path = os.path.join(
        get_package_share_directory('dual_arm_description'),
        'launch',
        'display.launch.py'
    )
    display_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(display_launch_path)
    )
    # 2. Activate MoveIt Servo
    servo_launch_path = os.path.join(
        get_package_share_directory('dual_arm_moveit_config'),
        'launch',
        'servo.launch.py'
    )
    servo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(servo_launch_path)
    )

    # 2. Execute Robot_control file
    robot_node = ExecuteProcess(
        cmd=['python3', '/home/trungtran/ros2_ws/src/dual_arm_moveit_config/src/robot_control.py'],
        output='screen'
    )

    # 3. Trigger command for servo control
    trigger_left = ExecuteProcess(
        cmd=['ros2 service call /left_arm/servo_node/start_servo std_srvs/srv/Trigger "{}"'],
        shell=True,
        output='screen'
    )
    
    trigger_right = ExecuteProcess(
        cmd=['ros2 service call /right_arm/servo_node/start_servo std_srvs/srv/Trigger "{}"'],
        shell=True,
        output='screen'
    )

    # Delay for 10s to wait for Rviz 
    delayed_triggers = TimerAction(
        period=10.0,
        actions=[trigger_left, trigger_right]
    )

    return LaunchDescription([
        display_launch,
        servo_launch,
        robot_node,
        delayed_triggers
    ])
