"""Smoothness engine: jerk + curvature alignment."""

from __future__ import annotations

import math

from .config import EngineConfig
from .player import PlayerState
from .spline import SplineTrack


def steering_response(p: PlayerState, cfg: EngineConfig, kappa: float) -> float:
    """Steering maps to a target curvature response (geometry feel)."""
    target = p.steer * cfg.steering_gain * max(abs(kappa), 1e-6)
    p.steering_response = target
    return target


def curve_error(p: PlayerState, kappa: float, steer_resp: float) -> float:
    p.curve_error = abs(kappa - steer_resp)
    return p.curve_error


def anticipatory_kappa(
    track: SplineTrack,
    s: float,
    v_eff: float,
    cfg: EngineConfig,
) -> tuple[float, float]:
    """κ_now and κ_ahead = κ(s + Δs) for predictive smoothness."""
    ds = cfg.anticipation_ds + cfg.anticipation_speed_scale * max(v_eff, 0.0)
    k0 = track.curvature(s)
    k1 = track.curvature(s + ds)
    return k0, k1


def smoothness_score(
    p: PlayerState,
    cfg: EngineConfig,
    kappa: float,
    kappa_ahead: float | None = None,
) -> float:
    """S = exp(- (w_j*|jerk| + w_c*curve_error)).

    If kappa_ahead provided, blend reactive + anticipatory alignment.
    """
    w_a = cfg.anticipation_blend if kappa_ahead is not None else 0.0
    k_eff = (1.0 - w_a) * kappa + w_a * float(kappa_ahead) if kappa_ahead is not None else kappa

    steer_resp = steering_response(p, cfg, k_eff)
    cerr = curve_error(p, kappa, steer_resp)
    if kappa_ahead is not None and w_a > 0.0:
        steer_a = steering_response(p, cfg, kappa_ahead)
        cerr = (1.0 - w_a) * cerr + w_a * curve_error(p, kappa_ahead, steer_a)

    penalty = cfg.jerk_weight * abs(p.jerk) + cfg.curve_weight * cerr
    p.smoothness = math.exp(-penalty)
    return p.smoothness


def instability(p: PlayerState, cfg: EngineConfig) -> float:
    """Sudden steering / braking spikes."""
    dsteer = abs(p.steer - p.steer_prev)
    p.steer_prev = p.steer
    inst = (
        cfg.steer_instability_weight * dsteer
        + cfg.brake_instability_weight * p.brake
    )
    p.instability = inst
    return inst
