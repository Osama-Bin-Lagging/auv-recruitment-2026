# Where to learn this

You are not expected to know ROS 2 or Gazebo already. Both are learnable in a
few days, and this page is the short path — organised by what each question
actually needs, so you are not reading tutorials you will not use.

**Versions matter.** We use **ROS 2 Humble** and **Gazebo Fortress**. Google will
happily hand you docs for a different version whose API is subtly different, so
prefer the links here, and if you land on something else check the version
selector before you trust it.

---

## Day 0 — the absolute basics (1 hour)

Do these inside the container, in order. They take about an hour and everything
else assumes them.

1. [Configuring your environment](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Configuring-ROS2-Environment.html)
   — what `source install/setup.bash` actually does. If you skip one thing, do
   not skip this; half of all "command not found" problems are this.
2. [Nodes, topics, and `ros2 topic`](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes.html)
   — the mental model: independent processes talking over named channels.
3. [`ros2 topic echo` / `hz` / `list`](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics.html)
   — your debugger. When something does not work, these three tell you whether
   data is flowing before you start reading your own code.

---

## Q1 — Find the Pinger

| you need | read this |
|---|---|
| writing a node in Python | [Simple publisher and subscriber](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html) |
| package structure, `setup.py` | [Creating a package](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html) |
| the custom messages we give you | [Custom interfaces](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html) |
| tuning without editing source | [Parameters in a class](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Using-Parameters-In-A-Class-Python.html) |
| starting sim + controller together | [Creating launch files](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Creating-Launch-Files.html) |
| why your subscriber gets nothing | [Quality of Service](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html) |

That last one is worth ten minutes even though it looks like an advanced topic.
Our sensor topics are **best-effort, depth 1** — subscribe with mismatched QoS
and you will silently receive nothing at all, with no error anywhere.

**On the estimation problem itself**, we are deliberately not linking a
tutorial. Working out what to do with a direction that carries no distance is
the question. If you want background reading, look up *bearing-only
localisation* or *triangulation from a moving baseline* — but run the simulator
and watch it fail first, because the failure tells you more than the reading
will.

---

## Q2 — Fly the Course

| you need | read this |
|---|---|
| what Gazebo Fortress even is | [Getting started](https://gazebosim.org/docs/fortress/getstarted) |
| moving a model with `cmd_vel` | [Moving the robot](https://gazebosim.org/docs/fortress/moving_robot) |
| **the bridge — the core of Part A** | [ROS 2 integration](https://gazebosim.org/docs/fortress/ros2_integration) |
| bridge argument syntax and type table | [`ros_gz_bridge` README](https://github.com/gazebosim/ros_gz/tree/humble/ros_gz_bridge) |
| reading the world file | [SDFormat specification](http://sdformat.org/spec) |
| recording your run | [Recording and playing back data](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data.html) |

The `ros_gz_bridge` README contains the **table of supported type pairs**. You
will need it, because a wrong pairing fails silently — the bridge starts, the
topic appears, and nothing ever arrives.

Useful commands that are Gazebo's, not ROS's, and therefore easy to forget:

```bash
ign topic -l                      # list Gazebo-side topics
ign topic -e -t /model/auv/odometry   # echo one
ign gazebo -s -r world.sdf        # headless server, running (no GUI)
```

When a topic is missing, check *which side* it is missing from. `ign topic -l`
and `ros2 topic list` showing different things is the normal state of affairs
and tells you exactly where the bridge is failing.

---

## Q3 — Gate Detection *(optional)*

- [Ultralytics YOLO docs](https://docs.ultralytics.com/) — training and export
- [YOLO dataset format](https://docs.ultralytics.com/datasets/detect/) — what
  those `.txt` label files mean
- [Albumentations](https://albumentations.ai/docs/) — if you want augmentation
  beyond the built-in options, which for this dataset you probably do

Free GPU: [Google Colab](https://colab.research.google.com/). The dataset is
small enough to train on the free tier.

---

## Debugging, generally

Most of the time you lose on this assignment will not be algorithmic. It will be
one of these:

| symptom | first thing to check |
|---|---|
| "command not found" after building | did you `source install/setup.bash` in *this* shell? |
| node runs, receives nothing | QoS mismatch, or wrong topic name. `ros2 topic list` then `ros2 topic hz <name>` |
| Gazebo topic exists, ROS side silent | wrong type pairing in the bridge |
| code edits have no effect | Python nodes are *copied* at build time. Re-run `colcon build`, or build once with `--symlink-install` |
| vehicle drifts away from the target | frame confusion — `cmd_vel` is body frame, waypoints are world frame |
| Gazebo dies on startup | memory. Docker Desktop → Resources → 6 GB+ |

The general method: **prove where the data stops before you read any code.**
`ros2 topic hz` at each stage of the chain finds the break faster than staring
at your callback will.

---

## Asking for help

Ask on the group. Setup problems especially are not part of what we are
measuring. Post the exact command and the exact error — not "it does not work".
