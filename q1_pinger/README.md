# Q1: Find the Pinger

Somewhere in the pool there's an acoustic pinger. Your vehicle has to find it and
park on top of it. You can't see it and you have no map. All you have is a
hydrophone.

A hydrophone gives you a direction. It never gives you a distance. Sit with that
before you write anything.

## Running it

```bash
cd ros2_ws
colcon build --merge-install
source install/setup.bash
ros2 launch auv_sim pinger.launch.py
```

Every run gives you a different arena. The seed is printed at startup, so if
something interesting happens you can repeat it with `seed:=<that number>`.

## Seeing what happened

There's no live view. Record a run and look at it yourself:

```bash
ros2 launch auv_sim pinger.launch.py trace_file:=run.csv
```

That writes a CSV, one row per step:

```
t,x,y,heading,valid,bearing,hold_time
```

and, once the episode is over, two trailing comment lines giving the pinger's
true position and the capture radius. They're written at the end on purpose, so
the file can't help you mid-run.

Plotting it is up to you. Your path against the pinger, and your distance to it
over time, are the two that tend to make the problem obvious.

Do this with the starter controller before you write anything.

## What you get

| topic | type | rate | contents |
|---|---|---|---|
| `/auv/state` | `VehicleState` | 60 Hz | your position, velocity, heading |
| `/auv/hydrophone` | `HydrophoneFix` | 60 Hz | `valid` + `bearing` |
| `/auv/episode` | `EpisodeStatus` | 5 Hz | how long you've held station |

`bearing` is the direction to the pinger relative to your heading, in radians.
There is no range field.

`valid` is true roughly once every 2 seconds, and not reliably:

- 3 to 9 degrees of noise on every fix, depending on your seed
- 5 to 20 percent of pings never arrive
- the pinger goes quiet for 8 to 15 seconds at some point

You can't tell these apart. `valid == false` means "nothing right now". Real
hydrophones can't distinguish them either.

## Your vehicle

Holonomic in the horizontal plane, like a vectored-thruster AUV. It strafes
without turning. You publish `VelocityCommand` on `/auv/cmd` with a world-frame
velocity and a desired heading. Both arrive through a first-order lag, because
thrusters aren't instant. Top speed 1.5 m/s.

Heading aims the hydrophone. It doesn't steer you.

## The task

Get within 1.0 m of the pinger and stay there for 5 continuous seconds.

Leaving the radius resets the timer. Orbiting isn't holding. You have 200
seconds.

## Seeds

By default every run draws a new arena: different pinger position, different
noise level, different dropout rate, different quiet window. That's deliberate.
A controller tuned to one scenario should fail here, in front of you, rather than
at grading where you can't see it.

Pin a seed when you're debugging something specific:

```bash
ros2 launch auv_sim pinger.launch.py seed:=1234
```

Grading uses its own seeds, from a range you can't draw. Getting it working on
one arena means nothing. Run it twenty times.

## Timing modes

`realtime` is the default. The sim steps on a wall clock and uses your most
recent command, so a slow controller means stale commands, like a real robot.

`lockstep` is what grading uses. The sim publishes state and waits for a command
tagged with the matching step before advancing, so your score doesn't depend on
how busy the grading machine was.

Set `header.frame_id` to the `step` of the `VehicleState` you're answering and
your controller works in both. If it doesn't match, that step coasts and counts
against you. Try `mode:=lockstep` before you submit.

## Submitting

Your `controller_node`, plus:

- tuning as ROS parameters, not constants in the source
- a launch file that brings up sim and controller together

Run `./validate.sh` first. It won't tell you your score, only whether we can run
your code at all.

Write up this question in `REPORT.md` at the root of your fork. See the
[submission instructions](../README.md#the-report).

## Grading

Your controller runs against private seeds. Your score is the fraction where you
hold station. Top scorers get a short interview about their approach.

## One warning

The starter controller drives at the last known bearing, full speed. It reaches
the pinger on nearly every seed and holds station on none of them.

Run it. Watch what happens when it arrives. Working out why is most of the
problem, and you won't get there by reading this page.
