# ros2 launch auv_sim pinger.launch.py
#   seed:=1234            repeat one arena instead of a random one
#   mode:=lockstep        run the way grading does
#   trace_file:=run.csv   record a CSV trace of the run

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    seed = LaunchConfiguration("seed")
    mode = LaunchConfiguration("mode")
    trace = LaunchConfiguration("trace_file")

    return LaunchDescription([
        DeclareLaunchArgument("seed", default_value="-1",
                              description="omit for a random arena"),
        DeclareLaunchArgument("mode", default_value="realtime",
                              description="realtime | lockstep"),
        DeclareLaunchArgument("trace_file", default_value="",
                              description="CSV trace of the run"),
        Node(
            package="auv_sim", executable="sim_node", name="auv_sim",
            output="screen",
            parameters=[{"seed": seed, "mode": mode, "trace_file": trace}],
        ),
        Node(
            package="auv_controller", executable="controller_node",
            name="auv_controller", output="screen",
        ),
    ])
