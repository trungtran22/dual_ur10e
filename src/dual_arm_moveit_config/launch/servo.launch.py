import os
import yaml
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def load_file(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return file.read()
    except EnvironmentError:
        return None

def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        return None

def generate_launch_description():
    # 1. Load URDF
    urdf_file = os.path.join(get_package_share_directory('dual_arm_description'), 'urdf', 'dual_ur10e_robotiq.urdf.xacro')
    robot_description_config = xacro.process_file(urdf_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    # 2. Load SRDF 
    robot_description_semantic_config = load_file('dual_arm_moveit_config', 'config/dual_ur10e.srdf')
    robot_description_semantic = {'robot_description_semantic': robot_description_semantic_config}

    # 3. Load Servo Params 
    servo_left_yaml = load_yaml('dual_arm_moveit_config', 'config/servo_left.yaml')
    servo_left_params = {'moveit_servo': servo_left_yaml}

    servo_right_yaml = load_yaml('dual_arm_moveit_config', 'config/servo_right.yaml')
    servo_right_params = {'moveit_servo': servo_right_yaml}

    # 4. Create Node for left
    servo_left_node = Node(
        package='moveit_servo',
        executable='servo_node_main',
        parameters=[servo_left_params, robot_description, robot_description_semantic],
        output='screen',
        namespace='left_arm'
    )

    # 5. Create Node for right
    servo_right_node = Node(
        package='moveit_servo',
        executable='servo_node_main',
        parameters=[servo_right_params, robot_description, robot_description_semantic],
        output='screen',
        namespace='right_arm'
    )

    return LaunchDescription([
        servo_left_node,
        servo_right_node
    ])
