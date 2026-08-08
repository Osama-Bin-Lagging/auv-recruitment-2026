# Q2 — Fly the Course

**Gazebo · ~5 hours · Days 5–7**

## What this is testing

Not clever algorithms. This checks you can **get a simulator running and talk to
it from ROS 2**, then plan a sensible path through a known map. That sounds
trivial and it is where most people lose their first week on a robotics team.

Setup help is available — ask on the group. Nobody is being marked on their
ability to configure Docker.

---

## Your course

```bash
python3 generate_world.py --seed <your_roll_number> --out course.sdf
```

That writes two files:

- `course.sdf` — the world: a 40 × 60 × 12 m pool, **3–5 gates**, and spherical
  obstacles
- `course_gates.yaml` — the map: gate poses in the order you must pass them,
  and every obstacle's position and radius

You may generate **as many courses as you like** with different seeds, and you
should. Your solution has to work on courses you have never seen — we grade on
seeds that are not published.

---

## Part A — Bring it up and bridge it

Start the world, then connect Gazebo to ROS 2.

Gazebo speaks Gazebo Transport. ROS 2 speaks DDS. They are different middlewares
with different message types, and `ros_gz_bridge` exists to translate between
them. Configuring it correctly is the skill this part tests.

You need these as **ROS 2** topics:

| what | Gazebo topic | direction |
|---|---|---|
| vehicle odometry | `/model/auv/odometry` | Gazebo → ROS |
| velocity command | `/model/auv/cmd_vel` | ROS → Gazebo |
| IMU | `/auv/imu` | Gazebo → ROS |

**Deliverable:** a bridge configuration and a **launch file** that starts Gazebo
and the bridge together with one command.

> **The failure mode to expect.** Get a message type wrong and the bridge starts
> happily, the topic appears in `ros2 topic list`, and no data ever arrives.
> Nothing errors. If a topic exists but is silent, suspect the type mapping
> before you suspect your code.

---

## Part B — Plan a path and fly it

Write a ROS 2 node that drives the vehicle through **every gate in order**,
passing between the posts, without hitting an obstacle or a post.

You are given the full map, so this is a **planning** problem, not a perception
one. Two things make it non-trivial:

- **Obstacles sit between the gates.** A node that drives straight at each gate
  in turn will hit something. We checked.
- **Gates are 2.0 m wide** and the vehicle is 0.9 m long. Arriving at an angle
  clips a post, so *how* you approach a gate matters as much as reaching it.

Useful geometry: a gate at `(x, y, z, yaw)` faces along `(cos yaw, sin yaw)`.
Your vehicle's half-diagonal is about 0.5 m, so keep your path at least
`radius + 0.5` m from any obstacle centre.

**Deliverable:** your navigation node, started by the same launch file, plus a
**rosbag** of one complete run and a short screen recording.

---

## Two things that will catch you out

**`cmd_vel` is in the BODY frame.** `linear.x` is forward *relative to the
vehicle*, not east. Your waypoints are in the world frame. Skip that rotation
and your vehicle curves away from every target, and it looks like a control bug
rather than a frame bug.

**The GUI changes your loop rate.** Running Gazebo with the browser view open
costs about 40% of your control rate (we measured ~17 Hz with the GUI versus
~30 Hz headless). We grade headless. If you tune anything against wall-clock
timing rather than the timestamps in the odometry messages, it will behave
differently under grading. Develop headless (`ign gazebo -s -r`) and open the
GUI only when you need to look at something.

---

## Bonus, purely if you feel like exploring

Not part of the assignment. Not scored. Do not attempt it unless Parts A and B
are finished and you are curious.

The vehicle can carry a forward camera:

```bash
python3 generate_world.py --seed <your_roll_number> --with-camera --out course.sdf
```

That adds `/auv/camera` and the posts are red and blue against blue-green water,
so in principle you could find the gates yourself instead of reading their
positions from the map file.

Two honest warnings. The camera forces Gazebo to render, which is noticeably
slower on a machine without a GPU — that is why it is off by default. And we
have not tried solving the course this way ourselves, so we do not know how hard
it is. Treat it as a sandbox, not a challenge with a known answer.

If underwater vision is the part you find interesting, **Q3 is the real version
of this** — same problem, real footage from our pool, and it is actually scored.

---

## How it's graded

We run your launch file on **course seeds you have never seen** and count:

1. **Gates passed in order** (primary)
2. **Collisions** (penalty)
3. **Time to complete** (tiebreak)

Part A is effectively a precondition: if the bridge is wrong, no commands reach
Gazebo, the vehicle never moves, and nothing downstream can be measured.

## Submission

A ROS 2 package with your bridge config, launch file and navigation node, plus
the rosbag, the screen recording, and **half a page** on the single thing that
took you longest to debug.
