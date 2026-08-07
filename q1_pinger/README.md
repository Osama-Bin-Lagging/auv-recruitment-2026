# Q1 — Find the Pinger

**ROS 2 · ~5 hours · Days 1–4**

## Background

Every AUV competition has an acoustic task: somewhere in the pool there is a
pinger, and your vehicle has to find it and park over it. You cannot see it —
the water is murky and it is too far away. All you have is a hydrophone.

A hydrophone tells you a **direction**. It does not tell you a **distance**.
That distinction is the whole of this problem, and it is worth sitting with
before you write any code.

## Running it

```bash
cd ros2_ws
colcon build --merge-install
source install/setup.bash
ros2 launch auv_sim pinger.launch.py seed:=<your_roll_number>
```

## Seeing what your controller did

There is no live GUI, but you can record a run and plot it:

```bash
ros2 launch auv_sim pinger.launch.py seed:=1234 trace_file:=run.csv
python3 plot_run.py run.csv          # writes run.png
```

That draws your path, where each bearing fix arrived, and your distance to the
pinger over time. The pinger's true position is written to the trace **only
when the episode ends**, so it cannot help you mid-run — but afterwards it
usually makes the problem obvious in one glance.

Do this with the starter controller before you write anything.

## What you're given

| topic | type | rate | contents |
|---|---|---|---|
| `/auv/state` | `VehicleState` | 60 Hz | your own position, velocity, heading |
| `/auv/hydrophone` | `HydrophoneFix` | 60 Hz | `valid` + `bearing` — see below |
| `/auv/episode` | `EpisodeStatus` | 5 Hz | how long you have held station so far |

**About the hydrophone.** `bearing` is the direction to the pinger *relative to
your heading*, in radians. There is no range field and there will not be one.

`valid` is true only about once every 2 seconds, and not reliably even then:

- **3–9° of noise** on every fix (how much depends on your seed)
- **5–20% of pings are lost**
- the pinger **goes silent for 8–15 seconds** at some point

You cannot tell these apart. `valid == false` means "no fix right now" and
nothing more — real hardware cannot distinguish them either.

## Your vehicle

Holonomic in the horizontal plane, like a vectored-thruster AUV: it moves
sideways without turning. You publish `VelocityCommand` on `/auv/cmd` with a
**world-frame velocity** and a desired heading; both arrive through a
first-order lag, because thrusters are not instant. Top speed 1.5 m/s.

Heading only points the hydrophone. It does not steer you.

## The task

> **Get within 1.0 m of the pinger and stay there for 5 continuous seconds.**

Leaving the capture radius resets the hold timer to zero. Orbiting the pinger is
not holding station over it. You have 200 seconds.

## Your seed

Your arena comes from **your roll number** — pinger position, noise level,
dropout rate and silent window all differ per candidate. Gains that work for
your friend will not work for you. Grading uses seeds you have never run.

## Timing modes

The simulator runs in `realtime` (default) or `lockstep`.

- **realtime** — steps on a wall clock using the most recent command. If your
  controller is slow, commands go stale, exactly like a real robot.
- **lockstep** — publishes state, then waits for a command tagged with the
  matching step before advancing. **Grading uses this**, so your score never
  depends on how loaded the grading machine was.

Set `header.frame_id` to the `step` of the `VehicleState` you are answering and
your controller works unchanged in both. If it does not match, that step coasts
and is counted against you. Try `mode:=lockstep` before submitting.

## What to submit

Your `controller_node`, plus:

- **Tuning as ROS parameters**, not constants buried in the source
- A **launch file** bringing up simulator and controller together
- **`REPORT.md`, one page maximum** — your approach, and one paragraph on what
  you tried that did not work and how you worked out why

Run `./validate.sh <your_roll_number>` before submitting. It does not tell you
your score; it tells you whether we can grade you at all.

## How it's graded

Your controller runs against **N private seeds**. Your score is the fraction on
which you hold station. Top scorers are invited to a short interview to talk
through their approach.

## One deliberate warning

The starter controller drives at the last known bearing at full speed. It will
reach the pinger on essentially every seed, and hold station on none of them.

**Run it first.** Watch what happens when it arrives. Understanding exactly why
it fails is most of this problem, and it is not something you can reason out
from this document.
