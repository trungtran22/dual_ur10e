#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from itertools import combinations
import os

def generate_acm(urdf_file):
    if not os.path.exists(urdf_file):
        print(f"Không tìm thấy file: {urdf_file}")
        return

    tree = ET.parse(urdf_file)
    root = tree.getroot()

    # 1. Tìm tất cả các khớp liền kề nhau (Adjacent)
    adjacent_pairs = set()
    for joint in root.findall('joint'):
        parent = joint.find('parent')
        child = joint.find('child')
        if parent is not None and child is not None:
            p = parent.get('link')
            c = child.get('link')
            if p and c:
                adjacent_pairs.add(tuple(sorted([p, c])))

    # 2. Gom nhóm các link của cổ tay và bộ kẹp (Gripper) để tắt va chạm nội bộ
    links = [link.get('name') for link in root.findall('link') if link.get('name')]
    
    left_wrist_gripper = [l for l in links if 'left' in l and ('wrist' in l or 'gripper' in l or 'robotiq' in l or 'flange' in l or 'tool' in l)]
    right_wrist_gripper = [l for l in links if 'right' in l and ('wrist' in l or 'gripper' in l or 'robotiq' in l or 'flange' in l or 'tool' in l)]

    never_pairs = set()
    for group in [left_wrist_gripper, right_wrist_gripper]:
        for l1, l2 in combinations(group, 2):
            pair = tuple(sorted([l1, l2]))
            if pair not in adjacent_pairs:
                never_pairs.add(pair)

    # 3. In ra màn hình cấu trúc XML chuẩn của MoveIt
    print("\n\n")
    for p1, p2 in sorted(adjacent_pairs):
        print(f'    <disable_collisions link1="{p1}" link2="{p2}" reason="Adjacent"/>')
    for p1, p2 in sorted(never_pairs):
        print(f'    <disable_collisions link1="{p1}" link2="{p2}" reason="Never"/>')
    print("\n\n")

if __name__ == "__main__":
    # Đảm bảo đường dẫn này trỏ đúng tới file .urdf tĩnh mà bạn đã gen ra lúc trước
    urdf_path = "src/dual_arm_description/urdf/dual_ur10e_robotiq.urdf" 
    generate_acm(urdf_path)
