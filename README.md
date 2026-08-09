# AUV-IITB Recruitment Assignment 2026

Two questions are required. One is optional.

| | question | what it's about |
|---|---|---|
| **Q1** | [Find the Pinger](q1_pinger/) | ROS 2, and estimating something you can't measure directly |
| **Q2** | [Fly the Course](q2_gazebo/) | Gazebo, the ROS/sim bridge, and path planning |
| **Q3** | [Gate Detection](q3_detection/) | underwater vision on real footage from our pool. Optional |

Start with [SETUP.md](SETUP.md). If ROS 2 and Gazebo are new to you,
[LEARNING.md](LEARNING.md) is the short way through the docs.

## What we're looking for

We're not testing whether you already know ROS 2. Most of you won't. It's a few
days of learning and we'll teach it properly once you're on the team.

We're looking for people who debug well. Both required questions are built so
that the obvious first attempt gets you most of the way and then visibly fails.
Working out why is the assignment. That's also why we ask you to write about what
went wrong. We'd rather read about a failure you understood than a success you
can't explain.

## What to submit

Your fork, containing:

```
your-fork/
  REPORT.md                                    required, see below

  q1_pinger/
    ros2_ws/src/auv_controller/                your controller node
    ros2_ws/src/auv_sim/launch/                your launch file

  q2_gazebo/
    bridge.yaml                                your bridge config
    bringup.launch.py                          your launch file
    nav_node.py                                your navigation node
    run.bag                                    rosbag of a complete run
    run.mp4                                    screen recording of the same run

  q3_detection/                                optional, only if you attempt Q3
    infer.py
    weights/
    requirements.txt
```

File names under `q2_gazebo/` and `q3_detection/` are suggestions. Put them where
you like as long as `REPORT.md` says where they are and your launch file works.

`REPORT.md` is not a suggestion. It goes at the root, with that name.

## How to submit

1. **Fork this repository** on GitHub and clone your fork, not this one. Commands
   are in [SETUP.md](SETUP.md).
2. **Work in your fork**, committing as you go. One large commit at the end tells
   us nothing about how you worked. Several small ones tell us a lot.
3. **Keep your fork public** so we can read it. If you'd rather it stayed
   private, add us as collaborators. We can't grade a fork we can't open.
4. **Run `q1_pinger/validate.sh`** and fix anything it flags. It checks that your
   Q1 code builds and runs, which is the part we can't grade if it's broken.
5. **Submit your fork's URL** through the submission form: `<SUBMISSION_LINK>`

Pushing to your fork does not submit anything. We collect URLs through the form,
so if you don't fill it in, you haven't applied.

We take whatever is on your default branch when the deadline passes. Anything
pushed after that is ignored. The deadline is in the recruitment email and on the
form.

## The report

`REPORT.md` at the root of your fork. There's a skeleton in this repo already:
open it, replace the instructions with your own writing, keep the headings.

Roughly two pages. It covers, per question, what your solution does and why, what
you tried that didn't work and how you diagnosed it, and what you'd do with more
time. It also has to declare how you used AI, and list what you know is broken.

Write it in your own words. We read these closely, and the interview is a
conversation about this document. If it reads like something you didn't write,
that will become obvious quickly and it won't go well for you.

Full instructions are in [REPORT.md](REPORT.md).

## Use of AI

You may use it. We'd be surprised if you didn't: we've told you ROS 2 isn't a
prerequisite and then set you two ROS 2 tasks, so closing that gap with a model
is a reasonable thing to do.

What we assess is whether you understand what you handed in. The interview goes
through your code and your report, line by line where it matters, and asks why
you did things the way you did. Not being able to explain your own submission is
the thing that fails you. Having used a tool is not.

You have to declare it in your report: which tools, which parts of your
submission they produced, and what you changed afterwards. Be specific. "Used
ChatGPT for help" tells us nothing. "It wrote the first version of the bridge
config, I fixed the type mapping for odometry and rewrote the launch file" tells
us plenty, and costs you nothing.

Undeclared use is the problem. Declared use isn't.

## Rules

Work alone. Talking about ideas is fine, sharing code isn't.

Don't modify `auv_interfaces`. Our grading simulator is built against those exact
message definitions, so changing them means your controller can't talk to it.
`q1_pinger/validate.sh` hashes them and will tell you if you have.

One fork, one branch.

## Grading

| | metric |
|---|---|
| Q1 | fraction of private seeds where you hold station on the pinger |
| Q2 | gates passed in order, minus collisions, time as tiebreak |
| Q3 | mAP on a held-out test set, within a CPU latency budget |

Those three are scored automatically, on scenarios and data you haven't seen.
The report is required and we read all of them. Top scorers are invited to a
short interview.

## Stuck?

Ask on the group. Setup problems especially aren't part of what we're measuring,
and we'd rather spend five minutes unblocking you than have you lose a day to a
Docker flag. Post the exact command and the exact error.
