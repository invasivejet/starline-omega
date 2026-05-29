"""Input noise metric — enforces ∂c/∂noise < 0 (no false reward)."""

from __future__ import annotations

from .config import EngineConfig
from .player import PlayerState


def input_noise(p: PlayerState, cfg: EngineConfig) -> float:
    """Dimensionless noise ∈ [0, ~1+] from incoherent control.

    Captures: rapid steer flips, brake spam, oscillation exploits.
    """
    dsteer = abs(p.steer - p.steer_prev)
    oscillation = dsteer * abs(p.steer)  # exploit: sign-flip spam
    brake_spam = p.brake * dsteer
    jerk_noise = min(1.0, abs(p.jerk) / max(cfg.jerk_noise_scale, 1e-6))
    return (
        cfg.noise_steer_weight * dsteer
        + cfg.noise_oscillation_weight * oscillation
        + cfg.noise_brake_weight * brake_spam
        + cfg.noise_jerk_weight * jerk_noise
    )
