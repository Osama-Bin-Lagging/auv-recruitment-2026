"""Simulator node. Provided complete -- you do not need to modify this.

Wraps pinger_sim.py and exposes it over ROS 2:

    publishes   /auv/state       VehicleState     60 Hz
                /auv/hydrophone  HydrophoneFix    60 Hz (mostly invalid)
                /auv/episode     EpisodeStatus     5 Hz
    subscribes  /auv/cmd         VelocityCommand

Two timing modes, selected by the `mode` parameter:

  realtime  (default, what you develop against)
      Steps on a wall-clock timer using the most recent command received. If
      your controller is slow, commands go stale -- exactly like a real robot.

  lockstep  (what grading uses)
      Publishes state, then waits for a command whose header.frame_id matches
      the step number before advancing. This makes an episode a pure function
      of (seed, controller), so your score does not depend on how busy the
      grading machine was. Set header.frame_id to the step you are answering
      and your controller works unchanged in both modes.
"""

from __future__ import annotations

import threading

import rclpy
import rclpy.executors
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy

from auv_interfaces.msg import EpisodeStatus, HydrophoneFix, VehicleState, VelocityCommand
from auv_sim.pinger_sim import CAPTURE_RADIUS, DT, HOLD_REQUIRED, PingerSim

# Sensor data: best-effort, depth 1. A stale bearing is worse than no bearing,
# so we never want the middleware replaying old fixes.
SENSOR_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1,
)
# Commands: reliable. A silently dropped command is indistinguishable from a
# controller bug, which makes debugging miserable.
COMMAND_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10,
)


class SimNode(Node):
    def __init__(self):
        super().__init__("auv_sim")

        self.declare_parameter("seed", 0)
        self.declare_parameter("mode", "realtime")
        self.declare_parameter("command_timeout", 0.5)

        self.seed = int(self.get_parameter("seed").value)
        self.mode = str(self.get_parameter("mode").value)
        self.command_timeout = float(self.get_parameter("command_timeout").value)

        self.sim = PingerSim(self.seed)

        self.pub_state = self.create_publisher(VehicleState, "/auv/state", SENSOR_QOS)
        self.pub_fix = self.create_publisher(HydrophoneFix, "/auv/hydrophone", SENSOR_QOS)
        self.pub_ep = self.create_publisher(EpisodeStatus, "/auv/episode", 10)
        self.create_subscription(VelocityCommand, "/auv/cmd", self._on_cmd, COMMAND_QOS)

        self._cmd = (0.0, 0.0, 0.0)
        self._cmd_step = -1
        self._cmd_event = threading.Event()
        self.missed_deadlines = 0
        self._tick = 0

        self.get_logger().info(
            f"sim ready: seed={self.seed} mode={self.mode} "
            f"capture={CAPTURE_RADIUS}m hold={HOLD_REQUIRED}s"
        )

    def _on_cmd(self, msg: VelocityCommand):
        try:
            step = int(msg.header.frame_id)
        except (TypeError, ValueError):
            step = -1
        self._cmd = (float(msg.vx), float(msg.vy), float(msg.heading))
        self._cmd_step = step
        self._cmd_event.set()

    def _publish(self):
        now = self.get_clock().now().to_msg()
        obs = self.sim.observe()

        st = VehicleState()
        st.header.stamp = now
        st.header.frame_id = str(obs.step)
        st.x, st.y = obs.x, obs.y
        st.vx, st.vy = obs.vx, obs.vy
        st.heading = obs.heading
        st.sim_time = obs.t
        st.step = obs.step
        self.pub_state.publish(st)

        fx = HydrophoneFix()
        fx.header.stamp = now
        fx.header.frame_id = str(obs.step)
        fx.valid = obs.bearing is not None
        fx.bearing = float(obs.bearing) if obs.bearing is not None else 0.0
        self.pub_fix.publish(fx)

        self._tick += 1
        if self._tick % 12 == 0:  # ~5 Hz
            ep = EpisodeStatus()
            ep.header.stamp = now
            ep.active = not self.sim.done
            ep.success = self.sim.success
            ep.hold_time = obs.hold_time
            ep.hold_required = HOLD_REQUIRED
            ep.elapsed = obs.t
            self.pub_ep.publish(ep)

        return obs

    def _await_command(self, step: int):
        if self.mode != "lockstep":
            return self._cmd
        self._cmd_event.clear()
        while self._cmd_event.wait(self.command_timeout):
            self._cmd_event.clear()
            if self._cmd_step == step:
                return self._cmd
        # No answer in time: coast. Counted and reported -- keeping up matters.
        self.missed_deadlines += 1
        return (0.0, 0.0, 0.0)

    def run(self):
        """Run the episode to completion and return the result.

        Wrapped in a context guard: in realtime mode an episode lasts up to
        200 s of wall clock, so Ctrl-C mid-run is the normal way candidates
        will stop it. Without this, shutdown races the publish loop and dumps
        an RCLError traceback over a perfectly healthy run.
        """
        next_wall = self.get_clock().now().nanoseconds / 1e9
        while not self.sim.done and rclpy.ok():
            try:
                obs = self._publish()
            except Exception:
                if not rclpy.ok():
                    break          # shutting down; not an error
                raise
            vx, vy, heading = self._await_command(obs.step)
            self.sim.step(vx, vy, heading)

            if self.mode != "lockstep":
                # Pace to wall clock so the GUI/logs look like real time.
                next_wall += DT
                sleep = next_wall - self.get_clock().now().nanoseconds / 1e9
                if sleep > 0:
                    self.get_clock().sleep_for(rclpy.duration.Duration(seconds=sleep))
        return self.sim.result()


def main():
    rclpy.init()
    node = SimNode()
    # An explicit executor rather than rclpy.spin in a daemon thread: the
    # daemon thread is still inside spin() when the process exits, which
    # aborts (SIGABRT) after a perfectly good episode. We need to be able to
    # stop it deterministically before tearing the node down.
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(node)
    spin = threading.Thread(target=executor.spin, daemon=True)
    spin.start()
    try:
        try:
            r = node.run()
        except KeyboardInterrupt:
            node.get_logger().info("interrupted")
            return
        node.get_logger().info(
            f"episode over: success={r.success} reached={r.reached} "
            f"t={r.time_to_success} rms={r.station_rms} missed={node.missed_deadlines}"
        )
        # Machine-readable line for the grader.
        print(f"RESULT seed={r.seed} success={r.success} reached={r.reached} "
              f"t_success={r.time_to_success} station_rms={r.station_rms} "
              f"path={r.path_length:.1f} fixes={r.n_fixes} "
              f"missed_deadlines={node.missed_deadlines}", flush=True)
    finally:
        executor.shutdown()
        spin.join(timeout=2.0)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
