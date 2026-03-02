# Dual UR10e System for Teleoperation tasks with Leap Motion
## ROS Humble - UR10e - Robotiq 2f-85
## The system features Custom Collision Matrices (ACM) for self-collision avoidance
The package includes necessary packages for the UR10e, Gripper Robotiq 2F-85 (CAD Meshes included) and package Serial for the gripper

## Result
![](https://github.com/trungtran22/dual_ur10e/pic/dual_ur10e.png)
![](https://github.com/trungtran22/dual_ur10e/pic/dual_arm.gif)

## Methodology
Due to hardware constraint (unable to initiate Moveit_setup_assistant), MoveIt SRDF and Collision Matrix were manually written and generated.
### 1. XACRO/URDF 
The system was built modularly using XACRO macros:
- A `base_table` link was created. Both UR10e arms were retrieved from the standard `ur_macro.xacro` and attached to this common base via fixed joints with distinct spatial offsets (translations and rotations).
- To prevent `tf` tree collisions between two identical robots, strict prefixing (`left_` and `right_`) was applied to all links and joints for each arm and its respective gripper.
- The Robotiq 85 grippers were instantiated and rigidly attached to the `tool0` (flange) of each respective UR10e arm.

### 2. MoveIt 2 SRDF Configuration & Kinematic Groups
To enable independent yet coordinated control:
- The SRDF was configured with distinct planning groups (e.g., `left_arm`, `right_arm`, `left_gripper`, `right_gripper`).
- KDL (Kinematics and Dynamics Library) was assigned to both arms to handle inverse kinematics calculations required by the MoveIt Servo engine.

### 3. Automated Allowed Collision Matrix (ACM) Generation
- A custom Python script (`generate_acm.py`) was developed to programmatically generate the Allowed Collision Matrix. 
- The script automatically disables collision checking for adjacent links while strictly enforcing collision detection between the `left_arm` links, `right_arm` links, and the environment. This ensures the robot safely avoids self-collision during rapid teleoperation without manual XML tweaking.

### 4. MoveIt Servo Tuning for Teleoperation
To bridge the gap between the Leap Motion hardware and the robot controllers:
- The `moveit_servo` YAML configurations were explicitly tuned for low-latency, real-time command streaming.
- To prevent MoveIt Servo from getting stuck in dynamic singularities (e.g., when the UR10e arm is perfectly straight), a mock hardware script initialized the robot in a initial posture.

## Environment Setup & Installation
### 1. Install System Dependencies
Update your system and install MoveIt 2 and required ROS 2 dependencies:
```
sudo apt update
sudo apt install python3-pip python3-colcon-common-extensions -y
sudo apt install ros-humble-moveit ros-humble-ur ros-humble-ros2-control ros-humble-ros2-controllers -y
```

### 2. Workspace Setup & Cloning
Create a new ROS 2 workspace and clone:
```
mkdir -p ~/sereact_ws
cd ~/sereact_ws
git clone https://github.com/trungtran22/dual_ur10e.git .
```

### 3. Install ROS Dependencies via rosdep
Install any remaining dependencies declared in the `package.xml` files:
```
cd ~/sereact_ws
sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### 4. Build the Workspace
Build the packages using `colcon`:
```
cd ~/sereact_ws
colcon build --symlink-install
```
Source the workspace:
```
source install/setup.bash
```

## How to Run the System

The system has been optimized into a single bringup launch file for the robot infrastructure, and a separate node for the Leap Motion hardware logic.

**Terminal 1: Launch Robot Infrastructure (RViz, MoveIt Servo, Robot Control & Triggers)**
```
source ~/sereact_ws/install/setup.bash
ros2 launch dual_arm_description teleop_bringup.launch.py
```
*Wait approximately 5 seconds for MoveIt Servo to fully load the SRDF/ACM and start receiving commands.*

**Terminal 2: Launch Leap Motion Teleoperation Node**
```
source ~/ws_teleop/install/setup.bash
python3 src/teleop_leap_servo/teleop_leap_servo/leap_twist_publisher.py
```
*Once the terminal logs `Leap Motion Connected --- Tracking both hands...`, you can move your hands over the Leap sensor to control the dual UR10e setup.*
