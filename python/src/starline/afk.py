"""AFK Cruise — server-side autopilot + realistic ℛ earn rate."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .config import EngineConfig
from .engine import ControlInput


@dataclass
class AfkSession:
    """Per-player AFK bookkeeping."""

    enabled: bool = False
    earned_session: float = 0.0


def afk_quality(coherence: float, smoothness: float, cfg: EngineConfig) -> float:
    """0..1 scaler from actual motion quality (not a flat idle buff)."""
    if coherence < cfg.afk_min_coherence:
        return 0.0
    q = smoothness * min(coherence, cfg.afk_coherence_cap)
    return max(0.0, min(1.0, q))


def afk_earn_scale(quality: float, cfg: EngineConfig) -> float:
    return quality * cfg.afk_earn_multiplier


def afk_cap_remaining(session: AfkSession, cfg: EngineConfig) -> float:
    return max(0.0, cfg.afk_session_cap - session.earned_session)


def compute_autopilot_control(
    kappa: float,
    kappa_ahead: float,
    v: float,
    cfg: EngineConfig,
) -> ControlInput:
    """Gentle cruise: moderate steer + band-limited speed (oval-friendly)."""
    target_steer = max(-1.0, min(1.0, kappa_ahead / cfg.steering_gain))
    throttle = cfg.afk_throttle
    brake = 0.0
    if v < cfg.afk_min_cruise_speed:
        throttle = cfg.afk_throttle
    elif v > cfg.afk_max_cruise_speed:
        over = v - cfg.afk_max_cruise_speed
        throttle = cfg.afk_throttle * max(0.12, 1.0 - over / 25.0)
    if v > cfg.afk_brake_above_speed:
        throttle = 0.0
        brake = cfg.afk_brake
    return ControlInput(throttle=throttle, brake=brake, steer=target_steer)


def apply_afk_coherence_cap(coherence: float, cfg: EngineConfig) -> float:
    """Presentation-only cap for AFK — engine still integrates; economy uses quality."""
    return min(coherence, cfg.afk_coherence_cap)
