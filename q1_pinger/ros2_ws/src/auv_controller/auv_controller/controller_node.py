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

MAX_SPEED = 1.5


def wrap_pi(a: float) -> float:
    return (a + math.pi) % (2.0 * math.pi) - math.pi


class ControllerNode(Node):
    def __init__(self):
        super().__init__("auv_controller")

        self.declare_parameter("approach_speed", MAX_SPEED)

        self.pub = self.create_publisher(VelocityCommand, "/auv/cmd", 10)
        self.create_subscription(VehicleState, "/auv/state", self.on_state, SENSOR_QOS)
        self.create_subscription(HydrophoneFix, "/auv/hydrophone", self.on_fix, SENSOR_QOS)
        self.create_subscription(EpisodeStatus, "/auv/episode", self.on_episode, 10)

        # (position when heard, world-frame bearing) for every fix so far.
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
            self.get_logger().info(f"held station, done at t={msg.elapsed:.1f}s")

    def on_state(self, msg: VehicleState):
        self.state = msg
        vx, vy, heading = self.compute_control(msg)
        self.publish(vx, vy, heading, msg.step)

    def compute_control(self, state: VehicleState) -> tuple[float, float, float]:
        # TODO: yours. Returns world-frame (vx, vy) in m/s and a desired heading.
        # What follows drives at the last known bearing and never stops. Run it
        # and watch what happens when it arrives.
        if not self.fixes:
            return 0.0, 0.0, state.heading

        _, bearing = self.fixes[-1]
        speed = float(self.get_parameter("approach_speed").value)
        return speed * math.cos(bearing), speed * math.sin(bearing), bearing

    def publish(self, vx: float, vy: float, heading: float, step: int):
        msg = VelocityCommand()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = str(step)   # pairs the command with its step
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
