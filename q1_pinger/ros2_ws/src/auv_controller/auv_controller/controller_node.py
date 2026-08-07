"""Your controller. This is the file you are graded on.

THE TASK
    An acoustic pinger sits somewhere in the arena. Your hydrophone reports the
    BEARING to it -- which direction it is in, relative to your heading -- about
    every 2 seconds, with noise, dropped pings, and one window where the pinger
    goes silent entirely.

    Reach the pinger and HOLD STATION within 1 m of it for 5 continuous seconds.
    Leaving that radius resets the hold timer to zero.

    You are never told how far away it is. There is no range field in
    HydrophoneFix and there will not be one. That is the whole problem, and it
    is worth sitting with before you write any code: a bearing tells you which
    way to go, but not when to stop.

WHAT YOU SUBSCRIBE TO
    /auv/state       VehicleState    60 Hz  your own position, velocity, heading
    /auv/hydrophone  HydrophoneFix   60 Hz  but `valid` is true only on a ping
    /auv/episode     EpisodeStatus    5 Hz  how long you have held so far

WHAT YOU PUBLISH
    /auv/cmd         VelocityCommand        world-frame velocity + heading

    Set header.frame_id to the `step` of the VehicleState you are answering.
    Grading runs the simulator in lockstep and uses it to pair your command
    with the right step; unmatched commands mean that step coasts, and it is
    counted against you.

HINTS THAT ARE NOT SPOILERS
    * Your own position and velocity ARE known. Only the pinger's is not.
    * A bearing taken from one place is a ray. Two rays taken from DIFFERENT
      places are not parallel.
    * Velocity is world-frame and holonomic -- you can move sideways freely
      without turning. Think about what that lets you do.
    * `valid` is false on most steps. Decide deliberately what to do between
      fixes; doing nothing and repeating the last thing are both choices, and
      they are not the same choice.

RUN IT FIRST
    The stub below drives at the last known bearing at full speed. It will
    reach the pinger on essentially every seed and hold station on none of
    them. Watch what happens when it arrives -- understanding exactly why it
    fails is most of this problem.
"""

from __future__ import annotations

import math

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy

from auv_interfaces.msg import EpisodeStatus, HydrophoneFix, VehicleState, VelocityCommand

SENSOR_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1,
)

MAX_SPEED = 1.5  # m/s -- the simulator clamps to this


def wrap_pi(a: float) -> float:
    return (a + math.pi) % (2.0 * math.pi) - math.pi


class ControllerNode(Node):
    def __init__(self):
        super().__init__("auv_controller")

        # Put tuning in parameters, not constants in the source. You will
        # change these a lot, and we can sweep them without editing your code.
        self.declare_parameter("approach_speed", MAX_SPEED)

        self.pub = self.create_publisher(VelocityCommand, "/auv/cmd", 10)
        self.create_subscription(VehicleState, "/auv/state", self.on_state, SENSOR_QOS)
        self.create_subscription(HydrophoneFix, "/auv/hydrophone", self.on_fix, SENSOR_QOS)
        self.create_subscription(EpisodeStatus, "/auv/episode", self.on_episode, 10)

        # Every fix so far, as (position when heard, world-frame bearing).
        # You will probably want this. What you do with it is the question.
        self.fixes: list[tuple[np.ndarray, float]] = []
        self.state: VehicleState | None = None

        self.get_logger().info("controller up")

    def on_fix(self, msg: HydrophoneFix):
        if not msg.valid or self.state is None:
            return
        s = self.state
        self.fixes.append((np.array([s.x, s.y]), wrap_pi(s.heading + msg.bearing)))

    def on_episode(self, msg: EpisodeStatus):
        if msg.success:
            self.get_logger().info(f"held station -- done at t={msg.elapsed:.1f}s")

    def on_state(self, msg: VehicleState):
        self.state = msg
        vx, vy, heading = self.compute_control(msg)
        self.publish(vx, vy, heading, msg.step)

    # --- the part you write --------------------------------------------------

    def compute_control(self, state: VehicleState) -> tuple[float, float, float]:
        """Return (vx, vy, desired_heading). Velocity is world-frame, in m/s.

        TODO: this is yours.
        """
        if not self.fixes:
            return 0.0, 0.0, state.heading

        _, bearing = self.fixes[-1]
        speed = float(self.get_parameter("approach_speed").value)
        return speed * math.cos(bearing), speed * math.sin(bearing), bearing

    # --- plumbing ------------------------------------------------------------

    def publish(self, vx: float, vy: float, heading: float, step: int):
        msg = VelocityCommand()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = str(step)   # pairs this command with its step
        msg.vx = float(vx)
        msg.vy = float(vy)
        msg.heading = float(heading)
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
