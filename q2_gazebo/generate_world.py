#!/usr/bin/env python3
# Generates a Gazebo Fortress course as one self-contained .sdf.
#   python3 generate_world.py --out course.sdf            random course
#   python3 generate_world.py --seed 42 --out c.sdf       repeat one course
#   python3 generate_world.py --seed 42 --answer          gate ground truth

from __future__ import annotations

import argparse
import math
import random

DEV_SEED_MAX = 1_000_000   # grading seeds sit above this

CAMERA_SDF = """        <sensor name="front_camera" type="camera">
          <pose>0.45 0 0 0 0 0</pose>
          <update_rate>20</update_rate>
          <topic>auv/camera</topic>
          <camera>
            <horizontal_fov>1.3</horizontal_fov>
            <image><width>640</width><height>480</height></image>
            <clip><near>0.1</near><far>60</far></clip>
          </camera>
        </sensor>

"""

SENSORS_PLUGIN_SDF = """    <plugin filename="ignition-gazebo-sensors-system"
            name="ignition::gazebo::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>
"""

POOL_W, POOL_L, POOL_D = 40.0, 60.0, 12.0   # metres: width (x), length (y), depth (z)
GATE_WIDTH = 2.0   # narrow enough that approach angle matters
GATE_HEIGHT = 2.4
POST_R = 0.08


def gate_sdf(idx: int, x: float, y: float, z: float, yaw: float) -> str:
    half = GATE_WIDTH / 2.0
    parts = []
    for side, colour, rgba in (
        (-half, "red", "0.8 0.1 0.1 1"),
        (half, "blue", "0.1 0.2 0.9 1"),
    ):
        parts.append(f"""
      <link name="post_{colour}">
        <pose>{side} 0 0 0 0 0</pose>
        <collision name="c"><geometry><cylinder>
          <radius>{POST_R}</radius><length>{GATE_HEIGHT}</length>
        </cylinder></geometry></collision>
        <visual name="v"><geometry><cylinder>
          <radius>{POST_R}</radius><length>{GATE_HEIGHT}</length>
        </cylinder></geometry>
          <material>
            <ambient>{rgba}</ambient><diffuse>{rgba}</diffuse>
          </material>
        </visual>
      </link>""")

    parts.append(f"""
      <link name="crossbar">
        <pose>0 0 {GATE_HEIGHT/2} 0 1.5708 0</pose>
        <visual name="v"><geometry><cylinder>
          <radius>{POST_R*0.7}</radius><length>{GATE_WIDTH}</length>
        </cylinder></geometry>
          <material>
            <ambient>0.9 0.9 0.1 1</ambient><diffuse>0.9 0.9 0.1 1</diffuse>
          </material>
        </visual>
      </link>""")

    return f"""
    <model name="gate_{idx}">
      <static>true</static>
      <pose>{x:.3f} {y:.3f} {z:.3f} 0 0 {yaw:.4f}</pose>{''.join(parts)}
    </model>"""


def obstacle_sdf(idx: int, x: float, y: float, z: float, r: float) -> str:
    return f"""
    <model name="obstacle_{idx}">
      <static>true</static>
      <pose>{x:.3f} {y:.3f} {z:.3f} 0 0 0</pose>
      <link name="body">
        <collision name="c"><geometry><sphere><radius>{r:.2f}</radius></sphere></geometry></collision>
        <visual name="v"><geometry><sphere><radius>{r:.2f}</radius></sphere></geometry>
          <material>
            <ambient>0.25 0.35 0.3 1</ambient><diffuse>0.25 0.35 0.3 1</diffuse>
          </material>
        </visual>
      </link>
    </model>"""


def vehicle_sdf(start_x: float, start_y: float, start_z: float, start_yaw: float,
                with_camera: bool = False) -> str:
    # Camera is opt-in: it forces rendering, which is slow without a GPU.
    camera_block = CAMERA_SDF if with_camera else ""
    return f"""
    <model name="auv">
      <pose>{start_x:.3f} {start_y:.3f} {start_z:.3f} 0 0 {start_yaw:.4f}</pose>
      <link name="base_link">
        <inertial>
          <mass>20.0</mass>
          <inertia>
            <ixx>0.7</ixx><iyy>1.4</iyy><izz>1.4</izz>
            <ixy>0</ixy><ixz>0</ixz><iyz>0</iyz>
          </inertia>
        </inertial>
        <collision name="c">
          <geometry><box><size>0.9 0.35 0.3</size></box></geometry>
        </collision>
        <visual name="v">
          <geometry><box><size>0.9 0.35 0.3</size></box></geometry>
          <material>
            <ambient>0.95 0.75 0.1 1</ambient><diffuse>0.95 0.75 0.1 1</diffuse>
          </material>
        </visual>

{camera_block}        <sensor name="imu" type="imu">
          <update_rate>50</update_rate>
          <topic>auv/imu</topic>
        </sensor>
      </link>

      <plugin filename="ignition-gazebo-velocity-control-system"
              name="ignition::gazebo::systems::VelocityControl">
        <topic>model/auv/cmd_vel</topic>
      </plugin>
      <plugin filename="ignition-gazebo-odometry-publisher-system"
              name="ignition::gazebo::systems::OdometryPublisher">
        <odom_frame>world</odom_frame>
        <robot_base_frame>auv</robot_base_frame>
        <odom_publish_frequency>30</odom_publish_frequency>
          <!-- 2D by default, which silently reports z as 0.0 -->
        <dimensions>3</dimensions>
      </plugin>
    </model>"""


def build_course(seed: int):
    rng = random.Random(seed)
    n_gates = rng.choice([3, 4, 4, 5])

    start_xy = (rng.uniform(-2, 2), -POOL_L / 2 + 3.0)

    gates = []
    y = -POOL_L / 2 + 10.0
    for i in range(n_gates):
        x = rng.uniform(-POOL_W / 4, POOL_W / 4)
        # Near the start depth: this question is not 3D trajectory planning.
        z = rng.uniform(-5.0, -3.5)
        yaw = rng.uniform(-0.5, 0.5)
        gates.append((x, y, z, yaw))
        y += rng.uniform(9.0, 14.0)

    # On the line between consecutive gates, so every seed blocks a naive
    # straight-line follower rather than only some seeds doing so.
    obstacles = []
    legs = [(start_xy, gates[0][:2])] if gates else []
    legs += [(gates[i][:2], gates[i + 1][:2]) for i in range(len(gates) - 1)]
    for i, (a, b) in enumerate(legs):
        t = rng.uniform(0.35, 0.65)                 # partway along the leg
        cx = a[0] + (b[0] - a[0]) * t
        cy = a[1] + (b[1] - a[1]) * t
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1.0
        px, py = -dy / n, dx / n
        # Keep clear of the gates themselves; a blocked gate is unfair.
        for _attempt in range(24):
            off = rng.uniform(-1.2, 1.2)
            r = rng.uniform(0.6, 1.1)
            ox, oy = cx + px * off, cy + py * off
            oz = rng.uniform(-5.0, -3.5)
            if all(math.hypot(ox - g[0], oy - g[1]) > (GATE_WIDTH + r + 1.0)
                   for g in gates):
                obstacles.append((ox, oy, oz, r))
                break

    start = (start_xy[0], start_xy[1], -4.0, rng.uniform(-0.3, 0.3))
    return gates, obstacles, start


def build_world(seed: int, with_camera: bool = False) -> str:
    gates, obstacles, start = build_course(seed)
    sensors_plugin = SENSORS_PLUGIN_SDF if with_camera else ""
    body = "".join(gate_sdf(i, *g) for i, g in enumerate(gates))
    body += "".join(obstacle_sdf(i, *o) for i, o in enumerate(obstacles))
    body += vehicle_sdf(*start, with_camera=with_camera)

    return f"""<?xml version="1.0" ?>
<!-- Generated by generate_world.py, seed {seed}. Do not hand-edit. -->
<sdf version="1.8">
  <world name="course_{seed}">
    <plugin filename="ignition-gazebo-physics-system"
            name="ignition::gazebo::systems::Physics"/>
    <plugin filename="ignition-gazebo-user-commands-system"
            name="ignition::gazebo::systems::UserCommands"/>
    <plugin filename="ignition-gazebo-scene-broadcaster-system"
            name="ignition::gazebo::systems::SceneBroadcaster"/>
{sensors_plugin}    <plugin filename="ignition-gazebo-imu-system"
            name="ignition::gazebo::systems::Imu"/>

    <!-- Neutrally buoyant vehicle under velocity control: no gravity term. -->
    <gravity>0 0 0</gravity>

    <light type="directional" name="sun">
      <cast_shadows>false</cast_shadows>
      <pose>0 0 20 0 0 0</pose>
      <diffuse>0.9 0.95 1.0 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.3 0.2 -0.9</direction>
    </light>

    <scene>
      <ambient>0.5 0.6 0.7 1</ambient>
      <background>0.15 0.35 0.5 1</background>
    </scene>

    <model name="pool_floor">
      <static>true</static>
      <pose>0 0 {-POOL_D} 0 0 0</pose>
      <link name="floor">
        <collision name="c"><geometry><plane><normal>0 0 1</normal>
          <size>{POOL_W} {POOL_L}</size></plane></geometry></collision>
        <visual name="v"><geometry><plane><normal>0 0 1</normal>
          <size>{POOL_W} {POOL_L}</size></plane></geometry>
          <material>
            <ambient>0.2 0.4 0.45 1</ambient><diffuse>0.2 0.4 0.45 1</diffuse>
          </material>
        </visual>
      </link>
    </model>
{body}
  </world>
</sdf>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=None,
                    help="omit for a random course")
    ap.add_argument("--out", default=None)
    ap.add_argument("--with-camera", action="store_true",
                    help="add the forward camera (only needed for the optional part)")
    ap.add_argument("--answer", action="store_true",
                    help="print gate ground truth (grader use only)")
    args = ap.parse_args()
    if args.seed is None:
        args.seed = random.randrange(1, DEV_SEED_MAX)
        print(f"seed {args.seed}  (repeat this course with --seed {args.seed})")

    if args.answer:
        gates, obstacles, start = build_course(args.seed)
        print(f"seed {args.seed}: {len(gates)} gates, {len(obstacles)} obstacles")
        print(f"start: x={start[0]:.2f} y={start[1]:.2f} z={start[2]:.2f} yaw={start[3]:.3f}")
        for i, (x, y, z, yaw) in enumerate(gates):
            print(f"  gate {i}: x={x:7.2f} y={y:7.2f} z={z:6.2f} yaw={yaw:+.3f}")
        return

    world = build_world(args.seed, with_camera=args.with_camera)
    out = args.out or f"course_{args.seed}.sdf"
    with open(out, "w") as f:
        f.write(world)
    print(f"wrote {out} ({len(world)} bytes)")

    # Static data, so a file rather than a topic.
    gates, obstacles, start = build_course(args.seed)
    gpath = out.rsplit(".", 1)[0] + "_gates.yaml"
    with open(gpath, "w") as f:
        f.write(f"# Gate waypoints for seed {args.seed}, in required order.\n")
        f.write(f"# Pass BETWEEN the posts. Gate width {GATE_WIDTH} m.\n")
        f.write(f"start: {{x: {start[0]:.3f}, y: {start[1]:.3f}, z: {start[2]:.3f}, yaw: {start[3]:.4f}}}\n")
        f.write("gates:\n")
        for i, (x, y, z, yaw) in enumerate(gates):
            f.write(f"  - {{id: {i}, x: {x:.3f}, y: {y:.3f}, z: {z:.3f}, yaw: {yaw:.4f}}}\n")
        f.write("# Spherical obstacles. Vehicle half-diagonal is ~0.5 m,\n")
        f.write("# so keep your path at least (radius + 0.5) m from each centre.\n")
        f.write("obstacles:\n")
        for i, (x, y, z, r) in enumerate(obstacles):
            f.write(f"  - {{id: {i}, x: {x:.3f}, y: {y:.3f}, z: {z:.3f}, radius: {r:.2f}}}\n")
    print(f"wrote {gpath} ({len(gates)} gates)")


if __name__ == "__main__":
    main()
