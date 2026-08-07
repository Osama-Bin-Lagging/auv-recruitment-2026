"""Bring up the simulator and your controller together.

    ros2 launch auv_sim pinger.launch.py seed:=<your_roll_number>

Add mode:=lockstep to run the way grading does.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    seed = LaunchConfiguration("seed")
    mode = LaunchConfiguration("mode")

    return LaunchDescription([
        DeclareLaunchArgument("seed", default_value="0",
                              description="your roll number"),
        DeclareLaunchArgument("mode", default_value="realtime",
                              description="realtime | lockstep"),
        Node(
            package="auv_sim", executable="sim_node", name="auv_sim",
            output="screen",
            parameters=[{"seed": seed, "mode": mode}],
        ),
        Node(
            package="auv_controller", executable="controller_node",
            name="auv_controller", output="screen",
        ),
    ])
