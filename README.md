# AUV-IITB Recruitment Assignment 2026

A week of work, about **2 hours a day**. Two questions are required, one is
optional.

| | question | time | what it tests |
|---|---|---|---|
| **Q1** | [Find the Pinger](q1_pinger/) | ~5 h, days 1–4 | ROS 2, and estimating something you cannot directly observe |
| **Q2** | [Fly the Course](q2_gazebo/) | ~5 h, days 5–7 | Gazebo, the ROS↔sim bridge, and path planning |
| **Q3** | [Gate Detection](q3_detection/) | ~4 h, optional | underwater computer vision, on real footage from our pool |

Start with **[SETUP.md](SETUP.md)** — budget about 45 minutes, mostly
downloading. New to ROS 2 or Gazebo? **[LEARNING.md](LEARNING.md)** is the short
path through the docs.

**Fork this repository and work in your fork.** That fork is your submission.

---

## What we're actually looking for

We are not testing whether you already know ROS 2. Most of you will not, and
that is fine — it is learnable in a few days, and we will teach it properly once
you are on the team.

We are looking for people who **debug well**. Both required questions are built
so that the obvious first attempt gets you most of the way and then visibly
fails. Working out *why* it fails is the assignment. That is also why each
question asks for a paragraph on what went wrong: we would rather read about a
failure you understood than a success you cannot explain.

## About AI

Use it. Everyone will, and pretending otherwise would just reward whoever hides
it best.

It will not get you very far here, for a structural reason rather than a moral
one. Every question is randomised from **your roll number**, so no two people
have the same problem, and grading uses seeds and data you have never seen. A
model can write you a controller; it cannot tell you why yours overshoots on
*your* pinger, because it has never run your simulator.

The interview at the end is a conversation about your code. Bring an
understanding of it.

## Rules

- **Work alone.** Discussing ideas is fine; sharing code is not. Since everyone
  has a different seed, shared constants will not work anyway.
- **Do not modify `auv_interfaces`.** Our grading simulator is built against
  those exact message definitions. Change them and your controller cannot talk
  to it. `validate.sh` checks this.
- **Submit one GitHub repo**, one branch. Run `validate.sh` before you submit.

## Getting stuck

Ask on the group. Setup problems in particular are not part of what we are
measuring, and we would much rather unblock you in five minutes than have you
lose a day to a Docker flag.

Post the exact command and the exact error.

## Grading

| | metric |
|---|---|
| Q1 | fraction of private seeds where you hold station over the pinger |
| Q2 | gates passed in order, minus collisions, time as tiebreak |
| Q3 | mAP on a held-out test set, subject to a CPU latency budget |

All three are scored automatically. **Top scorers are invited to a short
interview**, which is where your report and your debugging story matter.
