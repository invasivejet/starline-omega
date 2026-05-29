"""1D motion along spline arc-length s."""

from __future__ import annotations

from .config import EngineConfig
from .player import PlayerState


def update_velocity(
    p: PlayerState,
    cfg: EngineConfig,
    dt: float,
    drag_scale: float = 1.0,
) -> None:
    """v = v + throttle*accel - brake*decel; drag; clamp."""
    thrust = p.throttle * cfg.throttle_accel - p.brake * cfg.brake_decel
    p.a = thrust
    p.v = p.v + p.a * dt
    p.v = p.v - cfg.drag * drag_scale * p.v * dt
    p.v = max(0.0, min(cfg.max_speed, p.v))


def advance_arc_length(
    p: PlayerState,
    cfg: EngineConfig,
    dt: float,
    track_length: float,
) -> None:
    """s += v_eff * dt with resonance feedback."""
    p.v_eff = p.effective_speed(cfg)
    p.s = (p.s + p.v_eff * dt) % track_length


def update_jerk(p: PlayerState, dt: float) -> None:
    if dt <= 0.0:
        p.jerk = 0.0
        return
    p.jerk = (p.a - p.a_prev) / dt
    p.a_prev = p.a
