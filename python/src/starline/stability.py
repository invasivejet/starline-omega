"""Numerical stability envelopes — stable range vs hard clamp."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .config import EngineConfig
from .player import PlayerState


@dataclass(frozen=True)
class VariableEnvelope:
    stable_min: float
    stable_max: float
    hard_min: float
    hard_max: float

    def clamp(self, x: float) -> float:
        return max(self.hard_min, min(self.hard_max, x))

    def in_stable_band(self, x: float) -> bool:
        return self.stable_min <= x <= self.stable_max


# Default envelopes (docs/RIGOR.md)
VELOCITY = VariableEnvelope(0.0, 120.0, 0.0, 200.0)
COHERENCE = VariableEnvelope(0.0, 1.0, 0.0, 1.0)
SYNC_R = VariableEnvelope(0.0, 1.0, 0.0, 1.0)
SMOOTHNESS = VariableEnvelope(0.0, 1.0, 0.0, 1.0)
JERK = VariableEnvelope(-8.0, 8.0, -20.0, 20.0)
PHASE = VariableEnvelope(-math.tau, math.tau, -1e6, 1e6)


def apply_stability(p: PlayerState, cfg: EngineConfig) -> None:
    """Hard-clamp sacred variables after integration."""
    p.v = VELOCITY.clamp(p.v)
    if p.v > cfg.max_speed_hard:
        p.v = cfg.max_speed_hard
    p.coherence = COHERENCE.clamp(p.coherence)
    p.smoothness = SMOOTHNESS.clamp(p.smoothness)
    p.jerk = JERK.clamp(p.jerk)
    p.phase = p.phase % math.tau
