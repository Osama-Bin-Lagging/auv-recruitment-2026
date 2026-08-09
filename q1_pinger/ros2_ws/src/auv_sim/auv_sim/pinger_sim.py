from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

MAX_SPEED = 1.5
TAU_VEL = 0.5
TAU_HEADING = 0.4
CAPTURE_RADIUS = 1.0
HOLD_REQUIRED = 5.0
PING_INTERVAL = 2.0
DT = 1.0 / 60.0
TIMEOUT = 200.0

# Random development seeds come from below this; grading seeds sit above it,
# so a candidate can never stumble onto one.
DEV_SEED_MAX = 1_000_000


def wrap_pi(a: float) -> float:
    return (a + math.pi) % (2.0 * math.pi) - math.pi


@dataclass
class Observation:
    t: float
    step: int
    x: float
    y: float
    vx: float
    vy: float
    heading: float
    bearing: float | None
    hold_time: float


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
    def __init__(self, seed: int):
        self.seed = seed
        rng = np.random.default_rng(seed)

        r = rng.uniform(25.0, 70.0)
        th = rng.uniform(-math.pi, math.pi)
        self.pinger = np.array([r * math.cos(th), r * math.sin(th)])

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

    def range_to_pinger(self) -> float:
        return float(np.linalg.norm(self.pinger - self.pos))

    def _bearing(self) -> float | None:
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
        # _bearing() advances the ping schedule, so call this once per step only.
        return Observation(
            t=self.t, step=self.step_i,
            x=float(self.pos[0]), y=float(self.pos[1]),
            vx=float(self.vel[0]), vy=float(self.vel[1]),
            heading=self.heading,
            bearing=self._bearing(),
            hold_time=self.hold_time,
        )

    def step(self, vx_cmd: float, vy_cmd: float, heading_cmd: float) -> None:
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
    sim = PingerSim(seed)
    while not sim.done:
        vx, vy, hd = controller(sim.observe())
        sim.step(vx, vy, hd)
    return sim.result()
