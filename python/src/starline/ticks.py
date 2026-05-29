"""Simulation (fixed) vs presentation (interpolated) ticks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class SimClock:
    """Fixed simulation timestep accumulator with catch-up cap."""

    sim_dt: float = 1.0 / 60.0
    max_steps: int = 4
    max_catchup_sec: float = 0.25
    accumulator: float = 0.0
    sim_time: float = 0.0

    def consume(self, frame_dt: float) -> int:
        """Add frame_dt; return number of fixed steps to run."""
        self.accumulator += frame_dt
        if self.accumulator > self.max_catchup_sec:
            self.accumulator = self.max_catchup_sec
        n = 0
        while self.accumulator >= self.sim_dt and n < self.max_steps:
            self.accumulator -= self.sim_dt
            self.sim_time += self.sim_dt
            n += 1
        if n >= self.max_steps:
            self.accumulator = 0.0
        return n

    @property
    def alpha(self) -> float:
        """Interpolation factor [0,1] for presentation between sim states."""
        if self.sim_dt <= 0.0:
            return 0.0
        return self.accumulator / self.sim_dt


@dataclass
class PresentationBuffer:
    """Hold previous/current sim snapshots for interpolation."""

    prev: dict[int, Any] = field(default_factory=dict)
    curr: dict[int, Any] = field(default_factory=dict)

    def advance(self, snapshots: list[Any]) -> None:
        self.prev = self.curr
        self.curr = {s.player_id: s for s in snapshots}

    def interpolate_scalar(self, pid: int, name: str, alpha: float) -> float:
        if pid not in self.curr:
            return 0.0
        if pid not in self.prev:
            return float(getattr(self.curr[pid], name))
        a = float(getattr(self.prev[pid], name))
        b = float(getattr(self.curr[pid], name))
        return a + (b - a) * alpha

    def interpolate_position(self, pid: int, alpha: float) -> np.ndarray | None:
        if pid not in self.curr:
            return None
        if pid not in self.prev:
            return np.asarray(self.curr[pid].position, dtype=np.float64)
        p0 = np.asarray(self.prev[pid].position, dtype=np.float64)
        p1 = np.asarray(self.curr[pid].position, dtype=np.float64)
        return p0 + (p1 - p0) * alpha
