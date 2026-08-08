from __future__ import annotations

import threading

import rclpy
import rclpy.executors
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy

from auv_interfaces.msg import EpisodeStatus, HydrophoneFix, VehicleState, VelocityCommand
from auv_sim.pinger_sim import CAPTURE_RADIUS, DT, HOLD_REQUIRED, PingerSim

# Depth 1 best-effort: a stale bearing is worse than no bearing.
SENSOR_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1,
)
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
        self.declare_parameter("trace_file", "")

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

        path = str(self.get_parameter("trace_file").value)
        self._trace = open(path, "w") if path else None
        if self._trace:
            self._trace.write("t,x,y,heading,valid,bearing,hold_time\n")

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
        if self._tick % 12 == 0:
            ep = EpisodeStatus()
            ep.header.stamp = now
            ep.active = not self.sim.done
            ep.success = self.sim.success
            ep.hold_time = obs.hold_time
            ep.hold_required = HOLD_REQUIRED
            ep.elapsed = obs.t
            self.pub_ep.publish(ep)

        if self._trace:
            b = obs.bearing
            self._trace.write(
                f"{obs.t:.3f},{obs.x:.4f},{obs.y:.4f},{obs.heading:.4f},"
                f"{int(b is not None)},{b if b is not None else 0.0:.5f},"
                f"{obs.hold_time:.3f}\n")
        return obs

    def _await_command(self, step: int):
        if self.mode != "lockstep":
            return self._cmd
        self._cmd_event.clear()
        while self._cmd_event.wait(self.command_timeout):
            self._cmd_event.clear()
            if self._cmd_step == step:
                return self._cmd
        self.missed_deadlines += 1
        return (0.0, 0.0, 0.0)

    def run(self):
        next_wall = self.get_clock().now().nanoseconds / 1e9
        while not self.sim.done and rclpy.ok():
            try:
                obs = self._publish()
            except Exception:
                if not rclpy.ok():
                    break
                raise
            vx, vy, heading = self._await_command(obs.step)
            self.sim.step(vx, vy, heading)

            if self.mode != "lockstep":
                next_wall += DT
                sleep = next_wall - self.get_clock().now().nanoseconds / 1e9
                if sleep > 0:
                    self.get_clock().sleep_for(rclpy.duration.Duration(seconds=sleep))

        if self._trace:
            # Pinger position lands in the trace only now the episode is over.
            self._trace.write(f"# pinger {self.sim.pinger[0]:.4f} {self.sim.pinger[1]:.4f}\n")
            self._trace.write(f"# capture_radius {CAPTURE_RADIUS}\n")
            self._trace.close()
            self._trace = None
        return self.sim.result()


def main():
    rclpy.init()
    node = SimNode()
    # Explicit executor rather than spin() in a daemon thread, so it can be
    # stopped before teardown instead of aborting at process exit.
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
