"""Resonance as continuous geometric alignment field — not a buff."""

from __future__ import annotations

from .config import EngineConfig
from .player import PlayerState


def resonance_field(
    p: PlayerState,
    kappa: float,
    kappa_ahead: float,
    sync_R: float,
    cfg: EngineConfig,
) -> float:
    """Ψ_res ∈ [0, 1]: alignment of motion with geometry and ensemble.

    Emerges from curvature anticipation, smoothness, and synchronization.
    Modulates coherence gain multiplicatively — never additive nitro.
    """
    # geometric: how well steering anticipates upcoming curvature
    steer_a = p.steer * cfg.steering_gain * max(abs(kappa_ahead), 1e-6)
    anticip_err = abs(kappa_ahead - steer_a)
    anticip_align = 1.0 / (1.0 + cfg.resonance_kappa_scale * anticip_err)

    # local curvature coupling
    kappa_align = 1.0 / (1.0 + cfg.resonance_kappa_scale * abs(p.curve_error))

    geom = p.smoothness * (0.5 * anticip_align + 0.5 * kappa_align)
    sync = max(0.0, min(1.0, sync_R))

    psi = geom * (cfg.resonance_geom_weight + cfg.resonance_sync_weight * sync)
    return max(0.0, min(1.0, psi))
