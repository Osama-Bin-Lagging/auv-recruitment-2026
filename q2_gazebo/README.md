# Q2: Fly the Course

This one isn't about clever algorithms. It checks you can get a simulator
running, talk to it from ROS 2, and plan a path through a map you've been given.
That sounds easy, and it's where most people lose their first week on a robotics
team.

Ask on the group if setup fights you. Nobody's being marked on Docker.

## Your course

```bash
python3 generate_world.py --out course.sdf
```

Every call builds a different course. The seed is printed, so you can repeat one
with `--seed <that number>` while you're debugging.

You get two files:

- `course.sdf`, a 40 x 60 x 12 m pool with 3 to 5 gates and some spherical
  obstacles. Everything sits inside those bounds, so you can clamp your planner
  to them
- `course_gates.yaml`, the gate poses in the order you must pass them, plus every
  obstacle's position and radius

Generate a lot of them. Your solution has to work on courses you've never seen,
because that's what we grade on, and a planner that clears one course tells you
very little.

## Part A: bring it up and bridge it

Start the world, then connect Gazebo to ROS 2.

Gazebo speaks Gazebo Transport, ROS 2 speaks DDS. Different middlewares,
different message types. `ros_gz_bridge` translates between them, and
configuring it is the skill here.

You need these as ROS 2 topics:

| what | Gazebo topic | direction |
|---|---|---|
| odometry | `/model/auv/odometry` | Gazebo to ROS |
| velocity command | `/model/auv/cmd_vel` | ROS to Gazebo |
| IMU | `/auv/imu` | Gazebo to ROS |

Deliver a bridge config and a launch file that starts Gazebo and the bridge with
one command.

Expect this failure. Get a message type wrong and the bridge starts fine, the
topic shows up in `ros2 topic list`, and no data ever arrives. Nothing errors. If
a topic exists but is silent, check the type mapping before you check your code.

## Part B: plan a path and fly it

Drive the vehicle through every gate in order, between the posts, without hitting
an obstacle or a post.

You have the whole map, so this is planning, not perception. Two things make it
awkward:

- Obstacles sit between the gates. Drive straight at each gate in turn and you'll
  hit something. We checked.
- Gates are 2.0 m wide and the vehicle is 0.9 m long, so arriving at an angle
  clips a post. How you approach matters as much as getting there. Each gate
  faces roughly along the leg you arrive on, within about 30 degrees, so lining
  up on the gate normal before you go through is a workable approach. Pick where
  you line up from by checking the map, though: obstacles are only guaranteed
  clear of the gate itself, not of a point an arbitrary distance out along the
  normal.

A gate at `(x, y, z, yaw)` has its two posts separated along `(cos yaw, sin yaw)`,
so you fly through it along the perpendicular, `(-sin yaw, cos yaw)`. Your vehicle's
half-diagonal is about 0.5 m, so stay at least `radius + 0.5` m from any obstacle
centre.

Deliver your navigation node, started by the same launch file, plus a rosbag of a
complete run and a short screen recording.

## Two things that will bite you

`cmd_vel` is body frame. `linear.x` is forward relative to the vehicle, not east.
Your waypoints are world frame. Miss that rotation and the vehicle curves away
from every target, which looks like a control bug rather than a frame bug.

The GUI costs you loop rate. With the browser view open we measured about 17 Hz
against 30 Hz headless. We grade headless. Tune against the timestamps in the
odometry messages, not against wall-clock time, or it'll behave differently when
we run it. Develop with `ign gazebo -s -r` and open the GUI when you actually
need to look at something.

## Bonus, if you're curious

Not part of the assignment, not scored, and don't touch it until Parts A and B
work.

The vehicle can carry a forward camera:

```bash
python3 generate_world.py --with-camera --out course.sdf
```

That adds `/auv/camera`. The posts are red and blue against blue-green water, so
in principle you could find the gates yourself instead of reading the map file.

Two warnings. The camera makes Gazebo render, which is slow without a GPU, and
that's why it's off by default. And we haven't solved the course this way
ourselves, so we don't know how hard it is. It's a sandbox, not a challenge with
a known answer.

If underwater vision is the interesting part for you, Q3 is the real version of
it. Actual footage from our pool, and actually scored.

## Grading

We run your launch file on course seeds you've never seen and count gates passed
in order, then collisions as a penalty, then time as a tiebreak.

Part A is a precondition. If the bridge is wrong, nothing reaches Gazebo, the
vehicle never moves, and there's nothing else to measure.

## Submitting

Your bridge config, launch file and navigation node, plus a rosbag of one
complete run and a screen recording of the same run.

Write up this question in `REPORT.md` at the root of your fork. See the
[submission instructions](../README.md#the-report).
