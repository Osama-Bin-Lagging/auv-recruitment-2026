# Where to learn this

You're not expected to know ROS 2 or Gazebo. Both are a few days of learning.
This page is the short path, organised by what each question needs so you're not
reading tutorials you'll never use.

We use **ROS 2 Humble** and **Gazebo Fortress**. Google will happily give you
docs for a different version with a subtly different API, so use the links here,
and check the version selector if you land somewhere else.

## Start here

About an hour, inside the container, in order. Everything below assumes these.

1. [Configuring your environment](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Configuring-ROS2-Environment.html).
   What `source install/setup.bash` does. Half of all "command not found"
   problems are this one thing.
2. [Nodes and topics](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes.html).
   Separate processes talking over named channels.
3. [The `ros2 topic` tools](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics.html):
   `list`, `echo`, `hz`. These are your debugger. When something doesn't work
   they tell you whether data is flowing before you start reading your own code.

## Q1

| you need | read |
|---|---|
| a Python node | [Publisher and subscriber](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html) |
| package layout, `setup.py` | [Creating a package](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html) |
| the custom messages we give you | [Custom interfaces](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html) |
| tuning without editing source | [Parameters](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Using-Parameters-In-A-Class-Python.html) |
| starting sim and controller together | [Launch files](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Creating-Launch-Files.html) |
| why your subscriber gets nothing | [Quality of Service](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html) |

That last one is worth ten minutes even though it looks advanced. Our sensor
topics are best-effort with depth 1, and a mismatched QoS means you receive
nothing at all, with no error anywhere.

We're deliberately not linking anything about the estimation problem itself.
Working out what to do with a direction that carries no distance is the question.
If you want background, search for *bearing-only localisation*, but run the
simulator and watch it fail first. The failure tells you more than the reading
will.

## Q2

| you need | read |
|---|---|
| what Fortress is | [Getting started](https://gazebosim.org/docs/fortress/getstarted) |
| moving a model with `cmd_vel` | [Moving the robot](https://gazebosim.org/docs/fortress/moving_robot) |
| the bridge, which is Part A | [ROS 2 integration](https://gazebosim.org/docs/fortress/ros2_integration) |
| bridge syntax and the type table | [`ros_gz_bridge` README](https://github.com/gazebosim/ros_gz/tree/humble/ros_gz_bridge) |
| reading the world file | [SDFormat spec](http://sdformat.org/spec) |
| recording your run | [rosbag](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data.html) |

The `ros_gz_bridge` README has the table of supported type pairs. You'll need it,
because a wrong pairing fails silently.

Gazebo's own commands, which aren't ROS commands and are easy to forget:

```bash
ign topic -l                           # Gazebo-side topics
ign topic -e -t /model/auv/odometry    # echo one
ign gazebo -s -r world.sdf             # headless server
```

If a topic is missing, work out which side it's missing from. `ign topic -l` and
`ros2 topic list` disagreeing is normal, and it tells you exactly where the
bridge is failing.

## Q3

No reading list here on purpose. Which detector you train, what you train it
with, and how you augment are all yours to decide, and picking those is part of
what we want to see.

The only fixed things are the label format, the output contract and the latency
budget, all in the [question](q3_detection/). The dataset is small enough to
train on a free cloud GPU.

## Debugging

Most of the time you lose won't be algorithmic. It'll be one of these:

| symptom | check first |
|---|---|
| "command not found" after building | did you `source install/setup.bash` in *this* shell? |
| node runs, receives nothing | QoS mismatch, or wrong topic name |
| Gazebo topic exists, ROS side silent | wrong type pairing in the bridge |
| edits have no effect | Python nodes are copied at build time. Rebuild, or use `--symlink-install` |
| vehicle drifts off target | frame confusion. `cmd_vel` is body frame, waypoints are world frame |
| Gazebo dies on startup | memory. Docker Desktop, Resources, 6 GB or more |

The method that works: find where the data stops before you read any code.
`ros2 topic hz` at each stage finds the break faster than staring at a callback.

## Asking for help

Ask. Post the exact command and the exact error, not "it doesn't work".
