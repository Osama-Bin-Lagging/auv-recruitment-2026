"""Bearing-only pinger homing -- standalone simulator.

Single file, numpy only. No pygame, no ROS, no external repo. Kept deliberately
small because a bug in here is a bug in everyone's grade.

THE TASK
    An acoustic pinger sits somewhere in a 2D arena. The vehicle hears only the
    *bearing* to it -- a direction, never a distance -- every couple of seconds,
    with noise, dropped pings, and one silent window. The vehicle must reach the
    pinger and hold station within the capture radius for a continuous period.

WHY IT DISCRIMINATES
    A bearing says which way to go but not when to stop. A controller that
    simply drives along the last bearing reaches the pinger every single time
    and then sails straight past it, oscillating forever. Holding station
    requires recovering range, and range only becomes observable if you move
    laterally: one bearing is a ray, two rays from different places intersect.

    That is not something you can reason out from the problem statement alone --
    you have to run it, watch it overshoot, and work out why.

Everything derives from `seed`, so every candidate gets a different arena and
tuned constants cannot be shared. Grading seeds are disjoint and never
published.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

# --- Vehicle and task constants. Published to candidates. --------------------
MAX_SPEED = 1.5        # m/s
TAU_VEL = 0.5          # s, first-order lag on velocity (thruster response)
TAU_HEADING = 0.4      # s, first-order lag on heading
CAPTURE_RADIUS = 1.0   # m, small relative to MAX_SPEED*PING_INTERVAL overshoot
HOLD_REQUIRED = 5.0    # s, continuous time inside the capture radius
PING_INTERVAL = 2.0    # s
DT = 1.0 / 60.0        # s
TIMEOUT = 200.0        # s


def wrap_pi(a: float) -> float:
    """Wrap an angle into [-pi, pi]."""
    return (a + math.pi) % (2.0 * math.pi) - math.pi


@dataclass
class Observation:
    """What the controller is allowed to see, once per step."""

    t: float
    step: int
    x: float
    y: float
    vx: float
    vy: float
    heading: float
    bearing: float | None   # relative to heading, radians. None = no fix.
    hold_time: float        # continuous seconds inside the capture radius


@dataclass
class Result:
    seed: int
    success: bool
    reached: bool
    time_to_reach: float | None
    time_to_success: float | None
    station_rms: float | None
    path_length: float
    n_fixes: int


class PingerSim:
    """The simulator. Ground truth lives here and is never exposed."""

    def __init__(self, seed: int):
        self.seed = seed
        rng = np.random.default_rng(seed)

        # Pinger somewhere in an annulus around the start: never trivially
        # close, always reachable well inside the timeout.
        r = rng.uniform(25.0, 70.0)
        th = rng.uniform(-math.pi, math.pi)
        self.pinger = np.array([r * math.cos(th), r * math.sin(th)])

        # Sensor character varies per candidate: some get a quiet hydrophone,
        # some get one noisy enough that trusting any single fix is fatal.
        self.bearing_noise = math.radians(rng.uniform(3.0, 9.0))
        self.dropout_prob = rng.uniform(0.05, 0.20)
        self.silent_start = rng.uniform(30.0, 60.0)
        self.silent_end = self.silent_start + rng.uniform(8.0, 15.0)

        self.pos = np.zeros(2)
        self.vel = np.zeros(2)
        self.heading = rng.uniform(-math.pi, math.pi)

        self._rng = np.random.default_rng(seed ^ 0xA5A5)
        self.t = 0.0
        self.step_i = 0
        self._next_ping = 0.0

        self.hold_time = 0.0
        self.success = False
        self.time_to_success: float | None = None
        self.time_to_reach: float | None = None
        self.path_length = 0.0
        self.n_fixes = 0
        self._ranges_after_reach: list[float] = []

    # --- sensing -------------------------------------------------------------

    def range_to_pinger(self) -> float:
        return float(np.linalg.norm(self.pinger - self.pos))

    def _bearing(self) -> float | None:
        """Noisy relative bearing, or None when there is no fix this step.

        None is ambiguous on purpose: "not ping time", "ping dropped" and
        "pinger silent" are indistinguishable, exactly as on real hardware.
        """
        if self.t < self._next_ping:
            return None
        self._next_ping = self.t + PING_INTERVAL

        if self.silent_start <= self.t < self.silent_end:
            return None
        if self._rng.random() < self.dropout_prob:
            return None

        d = self.pinger - self.pos
        true_bearing = math.atan2(d[1], d[0]) - self.heading
        self.n_fixes += 1
        return wrap_pi(true_bearing + self._rng.normal(0.0, self.bearing_noise))

    def observe(self) -> Observation:
        return Observation(
            t=self.t, step=self.step_i,
            x=float(self.pos[0]), y=float(self.pos[1]),
            vx=float(self.vel[0]), vy=float(self.vel[1]),
            heading=self.heading,
            bearing=self._bearing(),
            hold_time=self.hold_time,
        )

    # --- dynamics ------------------------------------------------------------

    def step(self, vx_cmd: float, vy_cmd: float, heading_cmd: float) -> None:
        """Advance one step.

        Velocity is commanded in the WORLD frame and reached through a
        first-order lag; the vehicle is holonomic, as a vectored-thruster AUV
        is in the horizontal plane. Heading is separate and affects only where
        the hydrophone points -- it does not steer the vehicle.
        """
        cmd = np.array([float(vx_cmd), float(vy_cmd)])
        speed = float(np.linalg.norm(cmd))
        if speed > MAX_SPEED:
            cmd *= MAX_SPEED / speed

        self.vel += (cmd - self.vel) * (DT / TAU_VEL)
        self.pos += self.vel * DT
        self.path_length += float(np.linalg.norm(self.vel)) * DT

        self.heading = wrap_pi(
            self.heading + wrap_pi(float(heading_cmd) - self.heading) * (DT / TAU_HEADING)
        )

        self.t += DT
        self.step_i += 1

        rng_now = self.range_to_pinger()
        if self.time_to_reach is not None:
            self._ranges_after_reach.append(rng_now)

        if rng_now <= CAPTURE_RADIUS:
            if self.time_to_reach is None:
                self.time_to_reach = self.t
            self.hold_time += DT
            if self.hold_time >= HOLD_REQUIRED and not self.success:
                self.success = True
                self.time_to_success = self.t
        else:
            # Leaving the radius resets the clock: orbiting is not holding.
            self.hold_time = 0.0

    @property
    def done(self) -> bool:
        return self.success or self.t >= TIMEOUT

    def result(self) -> Result:
        held = self._ranges_after_reach
        return Result(
            seed=self.seed,
            success=self.success,
            reached=self.time_to_reach is not None,
            time_to_reach=self.time_to_reach,
            time_to_success=self.time_to_success,
            station_rms=float(np.sqrt(np.mean(np.square(held)))) if held else None,
            path_length=self.path_length,
            n_fixes=self.n_fixes,
        )


def run_episode(seed: int, controller) -> Result:
    """Run one full episode.

    `controller(obs) -> (vx_cmd, vy_cmd, heading_cmd)`, called once per step.
    This is exactly the signature the ROS 2 controller node wraps.
    """
    sim = PingerSim(seed)
    while not sim.done:
        vx, vy, hd = controller(sim.observe())
        sim.step(vx, vy, hd)
    return sim.result()
