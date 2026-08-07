# Setup

**Read this first. Setup is not part of what we're testing — if you get stuck,
ask on the group and we will help you.** Nobody is being marked on their ability
to install Docker.

Budget about 45 minutes, most of it downloading.

---

## 1. Install Docker

- **Windows** — Docker Desktop, with the WSL 2 backend (its installer offers
  this; accept it).
- **macOS** — Docker Desktop. Works on both Intel and Apple Silicon; you do not
  need to know which you have.
- **Linux** — Docker Engine from your distro, plus the `docker` group so you can
  run it without `sudo`.

Check it works:

```bash
docker run --rm hello-world
```

## 2. Give Docker enough memory

Docker Desktop → Settings → Resources. **At least 6 GB of RAM**, more if you
have it. Gazebo will misbehave in obscure ways below this, and you will waste an
evening on it.

Linux users can skip this — Docker uses the host's memory directly.

## 3. Pull the image

```bash
docker pull ghcr.io/<org>/auv-recruitment:2026
```

About 4 GB. It contains ROS 2 Humble, Gazebo Fortress, and the ROS–Gazebo
bridge, already built for both Intel and Apple Silicon — Docker picks the right
one automatically.

## 4. Fork the assignment

**Fork it — do not just clone it.** Your fork is what you submit, and your
commit history there is how we see how you worked.

1. Open the assignment repo on GitHub and click **Fork** (top right).
2. Clone *your fork*:

   ```bash
   git clone https://github.com/<your-username>/auv-recruitment-2026.git
   cd auv-recruitment-2026
   ```

   It is **about 330 MB** — most of that is the Q3 training images. On a slow
   connection this takes a while; it is not stuck.
3. Commit as you go. A single "final commit" at the deadline tells us nothing;
   twenty small commits tell us how you attacked the problem.

Keep your fork **public** so we can read it at the deadline, or add us as
collaborators if you would rather it stayed private.

If we push a fix or clarification during the week, pull it in:

```bash
git remote add upstream https://github.com/<org>/auv-recruitment-2026.git
git pull upstream main
```

## 5. Start the container

```bash
docker run -it --rm \
  -p 6080:6080 \
  -v "$PWD":/work \
  ghcr.io/<org>/auv-recruitment:2026
```

`-v "$PWD":/work` mounts this folder inside the container, so **edit files in
your normal editor on your own machine** and run them inside the container. Your
work is not trapped in the container and does not vanish when it stops.

## 6. See the simulator

Q2 needs a GUI. Inside the container:

```bash
/start-gui.sh
```

Then open **http://localhost:6080/vnc.html** in your browser and click Connect.
No password.

That's a full Linux desktop in a browser tab — no XQuartz on macOS, no X server
on Windows.

---

## Checking it all works

```bash
# inside the container
cd /work/q1_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --merge-install
source install/setup.bash
ros2 launch auv_sim pinger.launch.py seed:=<your_roll_number>
```

You should see `sim ready` and `controller up`, then the vehicle chasing the
pinger. If you see both lines, your environment is correct and you can start.

For Q2:

```bash
cd /work/q2_gazebo
python3 generate_world.py --seed <your_roll_number> --out course.sdf
ign gazebo -r course.sdf      # after /start-gui.sh, view it in the browser
```

---

## Things that go wrong

**"Cannot connect to the Docker daemon"** — Docker Desktop isn't running. Start
it and wait for the whale icon to stop animating.

**Gazebo starts then dies immediately** — almost always memory. See step 2.

**The browser tab is black** — Gazebo takes 10–20 seconds to paint the first
frame over software rendering. Give it a moment before assuming it's broken.

**Everything is slow on an old laptop** — run headless (`ign gazebo -s -r`,
no GUI) while developing and only open the browser view when you need to look at
something. Headless is much lighter.

**`ros2 run` says "No executable found"** — you edited a `setup.py` and dropped
its entry point, or you forgot `source install/setup.bash` after building.

**Your changes aren't taking effect** — Python nodes are installed at build
time, not symlinked. Re-run `colcon build` after editing, or build once with
`--symlink-install` so edits apply immediately.

---

## Learning ROS 2 and Gazebo

You are not expected to know either already. See **[LEARNING.md](LEARNING.md)**
for the short path — organised by what each question needs, so you are not
reading tutorials you will not use.

## Still stuck?

Ask. Post the exact command and the exact error. Genuinely — the point of this
assignment is the robotics, and we would much rather unblock you in five minutes
than have you lose a day to a Docker flag.
