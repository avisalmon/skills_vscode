---
name: Robotics with ROS 2
description: >
  Build and debug robotics software with ROS 2: workspaces, packages, nodes,
  topics, services, actions, parameters, launch files, rosbag recording,
  simulation, sensors, transforms, and robot debugging workflows. TRIGGER: ROS,
  ROS 2, robotics, robot node, topic, service, action, launch file, rosbag,
  Gazebo, RViz, TF, URDF.
version: 1.0.0
category: Robotics
tags: [ros2, robotics, python, simulation, sensors, control, rviz, gazebo]
---

# Robotics with ROS 2

## Overview

Use this skill when building, debugging, or teaching robotics software using ROS 2. It focuses on practical engineering workflows: creating packages, writing nodes, inspecting topics, recording data, using launch files, and debugging robot behavior from observable signals.

**Trigger words:** "ROS 2", "ROS", "robotics", "node", "topic", "service", "action", "launch", "rosbag", "RViz", "Gazebo", "URDF", "TF", "robot sensor".

---

## 1. Mental Model

ROS 2 is a robotics middleware made of small processes called nodes. Nodes communicate using typed interfaces:

- **Topics**: streaming data such as camera images, joint states, odometry, IMU, or velocity commands
- **Services**: request/response calls for quick operations such as reset, save map, or set mode
- **Actions**: long-running goals with feedback, such as navigation or arm movement
- **Parameters**: runtime configuration such as frame names, gains, limits, or feature flags
- **Launch files**: repeatable startup recipes for many nodes
- **Bags**: recorded message streams for replay and debugging

When debugging, always ask: which node publishes the signal, which node consumes it, what type is it, what frame is it in, and what rate should it have?

---

## 2. Workspace Basics

Typical workspace layout:

```text
robot_ws/
├── src/
│   ├── robot_bringup/
│   ├── robot_description/
│   ├── robot_control/
│   └── robot_perception/
├── build/
├── install/
└── log/
```

Common commands:

```bash
# Create workspace
mkdir -p robot_ws/src
cd robot_ws

# Build packages
colcon build

# Source the workspace
source install/setup.bash

# Build one package while developing
colcon build --packages-select robot_control
source install/setup.bash
```

Windows users often develop in WSL or Linux containers for ROS 2 compatibility.

---

## 3. Create a Python Package

```bash
cd robot_ws/src
ros2 pkg create robot_demo --build-type ament_python --dependencies rclpy std_msgs geometry_msgs
```

Minimal publisher node:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('velocity_publisher')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.publish_command)

    def publish_command(self):
        msg = Twist()
        msg.linear.x = 0.2
        msg.angular.z = 0.0
        self.publisher.publish(msg)


def main():
    rclpy.init()
    node = VelocityPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Minimal subscriber node:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class ScanMonitor(Node):
    def __init__(self):
        super().__init__('scan_monitor')
        self.sub = self.create_subscription(LaserScan, '/scan', self.on_scan, 10)

    def on_scan(self, msg):
        valid = [r for r in msg.ranges if msg.range_min <= r <= msg.range_max]
        if valid:
            self.get_logger().info(f'min range: {min(valid):.2f} m')


def main():
    rclpy.init()
    node = ScanMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

---

## 4. CLI Debugging Checklist

Start with introspection before changing code:

```bash
# What nodes are running?
ros2 node list

# What topics exist?
ros2 topic list

# What type is a topic?
ros2 topic type /cmd_vel

# Print messages
ros2 topic echo /odom

# Check publish rate
ros2 topic hz /scan

# Check bandwidth
ros2 topic bw /camera/image_raw

# Show interface definition
ros2 interface show geometry_msgs/msg/Twist

# Inspect parameters
ros2 param list /some_node
ros2 param get /some_node use_sim_time

# Call service
ros2 service list
ros2 service type /reset
ros2 service call /reset std_srvs/srv/Empty {}
```

Debug order:

1. Is the node running?
2. Is the topic/service/action name correct?
3. Is the message type correct?
4. Is the publish rate plausible?
5. Are frame IDs correct?
6. Are timestamps valid and using the same clock source?
7. Is `use_sim_time` consistent across nodes in simulation?

---

## 5. Launch Files

Use launch files for repeatable startup. Keep bringup logic out of ad-hoc terminal history.

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='robot_demo',
            executable='scan_monitor',
            name='scan_monitor',
            output='screen',
            parameters=[{'use_sim_time': False}],
        ),
        Node(
            package='robot_demo',
            executable='velocity_publisher',
            name='velocity_publisher',
            output='screen',
        ),
    ])
```

Run:

```bash
ros2 launch robot_demo demo.launch.py
```

Launch file best practices:

- Keep robot bringup, simulation bringup, and testing launch files separate.
- Expose important paths and modes as launch arguments.
- Put frame names and tuning values in YAML parameter files.
- Prefer namespaced launch for multi-robot tests.

---

## 6. Bags for Debugging

Record evidence before guessing.

```bash
# Record all topics
ros2 bag record -a

# Record specific topics
ros2 bag record /tf /tf_static /odom /scan /cmd_vel

# Inspect bag info
ros2 bag info rosbag2_YYYY_MM_DD-HH_MM_SS

# Replay
ros2 bag play rosbag2_YYYY_MM_DD-HH_MM_SS

# Replay with clock for simulation-aware nodes
ros2 bag play bag_folder --clock
```

Good bag capture for mobile robot issues:

- `/tf` and `/tf_static`
- `/odom`
- `/cmd_vel`
- `/scan` or camera topics
- localization output
- navigation goal/action topics
- diagnostics

---

## 7. Frames and TF

Many robotics bugs are frame bugs. Be explicit with frame names.

Common mobile robot frames:

```text
map -> odom -> base_link -> sensor frames
```

Rules of thumb:

- `map`: globally consistent frame, may jump when localization corrects
- `odom`: locally smooth frame, drifts over time
- `base_link`: robot body frame
- sensor frame: camera, lidar, IMU, wheel encoder frame

Useful checks:

```bash
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo /tf
```

If transforms are wrong, check parent/child direction, timestamp age, units, and whether static transforms belong in URDF or a static transform publisher.

---

## 8. Simulation Workflow

For simulation:

1. Start simulator.
2. Start robot state publisher with URDF.
3. Start controllers or plugins.
4. Start perception/localization.
5. Start behavior/navigation.
6. Record a bag when behavior differs from expectation.

Simulation-specific checks:

- All nodes that consume simulated time use `use_sim_time: true`.
- Joint names match URDF and controller config.
- Sensor frame names match message headers.
- Update rates are realistic.
- Physics time step is stable.

---

## 9. Useful Prompts for Copilot

```text
Create a ROS 2 Python node that subscribes to /scan, filters invalid ranges, and publishes a warning if any obstacle is closer than 0.5 meters.
```

```text
Write a ROS 2 launch file that starts robot_state_publisher, RViz, and a Python perception node with use_sim_time enabled.
```

```text
Given these ROS 2 topics and rates, help me debug why my robot does not move when I publish /cmd_vel.
```

```text
Design a rosbag recording plan for debugging intermittent localization jumps.
```

---

## Best Practices

- Use CLI introspection before editing code.
- Record bags for intermittent failures.
- Treat frames and timestamps as first-class data.
- Keep launch files small and composable.
- Put tuning in parameter YAML, not hardcoded constants.
- Build one package at a time while developing.
- Use simulation to reproduce logic bugs, but validate timing and sensors on hardware.
- Never run motors from unreviewed code without a physical safety stop.
