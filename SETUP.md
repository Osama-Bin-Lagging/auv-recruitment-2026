# Setup

Read this first. Setup isn't part of what we're testing, so if it fights you, ask
on the group and we'll sort it out. Nobody's being marked on installing Docker.

Budget about 45 minutes, mostly downloading.

## 1. Docker

- **Windows** — Docker Desktop with the WSL 2 backend. The installer offers it;
  accept.
- **macOS** — Docker Desktop. Works on Intel and Apple Silicon, and you don't
  need to know which you have.
- **Linux** — Docker Engine from your distro, plus your user in the `docker`
  group so you don't need `sudo`.

Check:

```bash
docker run --rm hello-world
```

## 2. Give Docker memory

Docker Desktop → Settings → Resources → at least 6 GB of RAM, more if you have
it. Below that Gazebo fails in confusing ways and you'll lose an evening to it.

Linux users skip this; Docker uses host memory directly.

## 3. Pull the image

```bash
docker pull ghcr.io/osama-bin-lagging/auv-recruitment:2026
```

About 4 GB. ROS 2 Humble, Gazebo Fortress and the ROS–Gazebo bridge, built for
both Intel and Apple Silicon. Docker picks the right one.

## 4. Fork the repo

Fork it, don't just clone it. Your fork is what you submit, and the commit
history there is how we see how you worked.

1. Click **Fork** on GitHub.
2. Clone your fork:

   ```bash
   git clone https://github.com/<your-username>/auv-recruitment-2026.git
   cd auv-recruitment-2026
   ```

   It's about 330 MB, mostly Q3 training images. On a slow connection this takes
   a while; it isn't stuck.

3. Commit as you go. One giant commit at the deadline tells us nothing.

Keep your fork public so we can read it, or add us as collaborators if you'd
rather it stayed private.

If we push a fix during the week:

```bash
git remote add upstream https://github.com/Osama-Bin-Lagging/auv-recruitment-2026.git
git pull upstream main
```

## 5. Start the container

```bash
docker run -it --rm \
  -p 6080:6080 \
  -v "$PWD":/work \
  ghcr.io/osama-bin-lagging/auv-recruitment:2026
```

The `-v` mounts this folder into the container, so edit files in your normal
editor on your own machine and run them inside. Nothing is trapped in the
container and nothing vanishes when it stops.

## 6. See the simulator

Q2 needs a GUI. Inside the container:

```bash
/start-gui.sh
```

Then open **http://localhost:6080/vnc.html** and click Connect. No password.

That's a Linux desktop in a browser tab, which saves you XQuartz on macOS and an
X server on Windows.

## Check it works

```bash
# inside the container
cd /work/q1_pinger/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --merge-install
source install/setup.bash
ros2 launch auv_sim pinger.launch.py seed:=<your_roll_number>
```

You should see `sim ready` and `controller up`, then the vehicle chasing the
pinger. Both lines means your environment is fine.

For Q2:

```bash
cd /work/q2_gazebo
python3 generate_world.py --seed <your_roll_number> --out course.sdf
ign gazebo -r course.sdf      # run /start-gui.sh first, then use the browser
```

## When it breaks

**"Cannot connect to the Docker daemon"** — Docker Desktop isn't running.

**Gazebo starts then dies** — almost always memory. See step 2.

**Browser tab is black** — Gazebo takes 10–20 seconds to draw the first frame
under software rendering. Wait before assuming it's broken.

**Everything is slow** — develop headless (`ign gazebo -s -r`) and only open the
browser view when you need to look at something. It's much lighter.

**`ros2 run` says "No executable found"** — you either broke an entry point in
`setup.py` or forgot `source install/setup.bash` after building.

**Your edits do nothing** — Python nodes get copied at build time, not
symlinked. Re-run `colcon build`, or build once with `--symlink-install`.

## Learning ROS 2 and Gazebo

You're not expected to know either. [LEARNING.md](LEARNING.md) is the short way
through the docs, organised by what each question needs.

## Still stuck

Ask, and post the exact command and the exact error. The point of this is the
robotics, not the tooling.
