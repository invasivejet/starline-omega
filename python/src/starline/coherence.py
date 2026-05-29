"""Coherence system — sacred variable c with rigor constraints."""

from __future__ import annotations

from .config import EngineConfig
from .player import PlayerState


def update_coherence(
    p: PlayerState,
    cfg: EngineConfig,
    dt: float,
    smoothness: float,
    instability: float,
    *,
    resonance: float = 0.0,
    noise: float = 0.0,
) -> float:
    """Δc = α·S·(1−c)^p·(½+½·Ψ_res)·dt − β·I·dt − λ·noise·dt.

    - Asymptotic (1−c)^p prevents saturation.
    - Resonance Ψ_res ∈ [0,1] modulates gain (field, not buff).
    - Noise penalty enforces ∂c/∂noise < 0 (no false reward).
    """
    c = p.coherence
    pwr = max(cfg.coherence_power, 1.01)
    res_mod = 0.5 + 0.5 * max(0.0, min(1.0, resonance))
    gain = cfg.alpha * smoothness * ((1.0 - c) ** pwr) * res_mod * dt
    loss = cfg.beta * instability * dt
    noise_loss = cfg.noise_penalty * max(0.0, noise) * dt
    p.coherence = c + gain - loss - noise_loss
    p.clamp_coherence()
    return p.coherence
