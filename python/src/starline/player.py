"""Minimal player state struct."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .config import EngineConfig


@dataclass
class PlayerState:
    """Everything the engine tracks per player."""

    s: float = 0.0
    v: float = 0.0
    a: float = 0.0
    jerk: float = 0.0
    phase: float = 0.0
    coherence: float = 0.0

    # control / diagnostics (not in minimal spec but needed for instability)
    steer: float = 0.0
    throttle: float = 0.0
    brake: float = 0.0
    a_prev: float = 0.0
    steer_prev: float = 0.0

    # world projection
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))

    # last-step outputs
    smoothness: float = 0.0
    instability: float = 0.0
    v_eff: float = 0.0
    steering_response: float = 0.0
    curve_error: float = 0.0

    def reset(self, s0: float = 0.0) -> None:
        self.s = s0
        self.v = 0.0
        self.a = 0.0
        self.jerk = 0.0
        self.phase = 0.0
        self.coherence = 0.0
        self.steer = 0.0
        self.throttle = 0.0
        self.brake = 0.0
        self.a_prev = 0.0
        self.steer_prev = 0.0
        self.position = np.zeros(3)
        self.smoothness = 0.0
        self.instability = 0.0
        self.v_eff = 0.0
        self.steering_response = 0.0
        self.curve_error = 0.0

    def clamp_coherence(self) -> None:
        self.coherence = max(0.0, min(1.0, self.coherence))

    def effective_speed(self, cfg: EngineConfig) -> float:
        return self.v * (1.0 + cfg.gamma * self.coherence)
