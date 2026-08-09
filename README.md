# AUV-IITB Recruitment Assignment 2026

Two questions are required. One is optional.

| | question | what it's about |
|---|---|---|
| **Q1** | [Find the Pinger](q1_pinger/) | ROS 2, and estimating something you can't measure directly |
| **Q2** | [Fly the Course](q2_gazebo/) | Gazebo, the ROS/sim bridge, and path planning |
| **Q3** | [Gate Detection](q3_detection/) | underwater vision on real footage from our pool. Optional |

Start with [SETUP.md](SETUP.md). If ROS 2 and Gazebo are new to you,
[LEARNING.md](LEARNING.md) is the short way through the docs.

Fork this repo and work in your fork. That fork is your submission.

## What we're looking for

We're not testing whether you already know ROS 2. Most of you won't. It's a few
days of learning and we'll teach it properly once you're on the team.

We're looking for people who debug well. Both required questions are built so
that the obvious first attempt gets you most of the way and then visibly fails.
Working out why is the assignment. That's also why each question asks for a
paragraph about something that went wrong. We'd rather read about a failure you
understood than a success you can't explain.

## About AI

Use it. Everyone will, and pretending otherwise just rewards whoever hides it
best.

It won't get you far here, for structural reasons rather than moral ones. Both
simulators draw a fresh random scenario on every run, and grading uses seeds and
data nobody has seen. A model can write you a controller. It can't tell you why
yours overshoots on the arena you just watched, because it has never run your
simulator.

The interview at the end is a conversation about your code. Turn up understanding
it.

## Rules

Work alone. Talking about ideas is fine, sharing code isn't. Nobody has a fixed
scenario to share constants for anyway.

Don't modify `auv_interfaces`. Our grading simulator is built against those exact
message definitions, so changing them means your controller can't talk to it.
`q1_pinger/validate.sh` hashes them and will tell you if you have.

Submit one repo, one branch. Run `q1_pinger/validate.sh` before you do; it
checks that Q1 builds and runs, which is the part we can't grade if it's broken.

## Stuck?

Ask on the group. Setup problems especially aren't part of what we're measuring,
and we'd rather spend five minutes unblocking you than have you lose a day to a
Docker flag. Post the exact command and the exact error.

## Grading

| | metric |
|---|---|
| Q1 | fraction of private seeds where you hold station on the pinger |
| Q2 | gates passed in order, minus collisions, time as tiebreak |
| Q3 | mAP on a held-out test set, within a CPU latency budget |

All scored automatically. Top scorers get a short interview, which is where the
report and your debugging story matter.
