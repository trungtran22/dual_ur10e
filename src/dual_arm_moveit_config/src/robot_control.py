#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory
from std_msgs.msg import Float64

class MockRobot(Node):
    def __init__(self):
        super().__init__('mock_robot')
        # Publish through /servo_joint_states to control
        self.pub = self.create_publisher(JointState, '/servo_joint_states', 10)
        
        # Servoing msgs
        self.sub_left = self.create_subscription(JointTrajectory, '/left_arm/command', self.left_cb, 10)
        self.sub_right = self.create_subscription(JointTrajectory, '/right_arm/command', self.right_cb, 10)
        
        # Gripper msgs
        self.sub_grip_l = self.create_subscription(Float64, '/left_gripper/cmd_width', self.grip_l_cb, 10)
        self.sub_grip_r = self.create_subscription(Float64, '/right_gripper/cmd_width', self.grip_r_cb, 10)

        self.js = JointState()
    
        self.js.name = [
            'left_shoulder_pan_joint', 'left_shoulder_lift_joint', 'left_elbow_joint', 'left_wrist_1_joint', 'left_wrist_2_joint', 'left_wrist_3_joint',
            'right_shoulder_pan_joint', 'right_shoulder_lift_joint', 'right_elbow_joint', 'right_wrist_1_joint', 'right_wrist_2_joint', 'right_wrist_3_joint',
            'left_gripper_robotiq_85_left_knuckle_joint',  
            'right_gripper_robotiq_85_left_knuckle_joint'  
        ]
        
        # Init Pose for both arms and grippers
        self.js.position = [
            -1.57, -1.57, -1.57, -1.57, 1.57, 0.0,   # left ur
            -1.57, -1.57, -1.57, -1.57, 1.57, 0.0,   # right ur
            0.0, 0.0                            # grippers
        ]

        self.timer = self.create_timer(0.02, self.timer_cb)

    def left_cb(self, msg):
        if msg.points:
            pt = msg.points[-1]
            for i, name in enumerate(msg.joint_names):
                if name in self.js.name:
                    idx = self.js.name.index(name)
                    self.js.position[idx] = pt.positions[i]

    def right_cb(self, msg):
        if msg.points:
            pt = msg.points[-1]
            for i, name in enumerate(msg.joint_names):
                if name in self.js.name:
                    idx = self.js.name.index(name)
                    self.js.position[idx] = pt.positions[i]
                    
    def grip_l_cb(self, msg):
        
        self.js.position[12] = (1.0 - msg.data) * 0.8 
        
    def grip_r_cb(self, msg):
        self.js.position[13] = (1.0 - msg.data) * 0.8

    def timer_cb(self):
        self.js.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(self.js)

def main():
    rclpy.init()
    node = MockRobot()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
