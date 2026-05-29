"""Geometric economy — ℛ as time-integral of coherent energy (projection layer)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .afk import AfkSession
from .config import EngineConfig


@dataclass
class EconomyState:
    resonance: float = 0.0
    peak: float = 0.0
    unlocks: set[str] = field(default_factory=lambda: {"oval"})
    coherence_integral: float = 0.0

    def to_dict(self) -> dict:
        return {
            "resonance": self.resonance,
            "peak": self.peak,
            "unlocks": sorted(self.unlocks),
            "coherence_integral": self.coherence_integral,
        }


def energy_increment(
    *,
    psi: float,
    smoothness: float,
    coherence: float,
    sync_R: float,
    dt: float,
    cfg: EngineConfig,
    afk: AfkSession | None = None,
    velocity: float = 0.0,
) -> float:
    """dℛ = k · Ψ · S · c^γ · (1 + λ·R₊) · dt — single projection of sim state."""
    c_min = cfg.afk_min_coherence if afk and afk.enabled else cfg.resonance_c_min
    if coherence < c_min:
        return 0.0
    if afk and afk.enabled and velocity < cfg.afk_min_velocity:
        return 0.0

    c_eff = min(coherence, cfg.afk_coherence_cap) if afk and afk.enabled else coherence
    c_eff = max(0.0, min(1.0, c_eff))
    gamma = max(cfg.resonance_coherence_gamma, 1.01)
    r_plus = max(0.0, sync_R)
    sync_term = 1.0 + cfg.resonance_sync_lambda * r_plus
    return (
        cfg.resonance_earn_k
        * max(0.0, psi)
        * max(0.0, smoothness)
        * (c_eff**gamma)
        * sync_term
        * dt
    )


def integrate_resonance(
    econ: EconomyState,
    *,
    dt: float,
    coherence: float,
    smoothness: float,
    resonance_field: float,
    flow_state: str,
    sync_R: float,
    velocity: float = 0.0,
    cfg: EngineConfig | None = None,
    afk: AfkSession | None = None,
) -> float:
    """Integrate ℛ on server tick. flow_state kept for telemetry only."""
    _ = flow_state
    cfg = cfg or EngineConfig()
    econ.coherence_integral += max(0.0, coherence) * dt

    dR = energy_increment(
        psi=resonance_field,
        smoothness=smoothness,
        coherence=coherence,
        sync_R=sync_R,
        dt=dt,
        cfg=cfg,
        afk=afk,
        velocity=velocity,
    )

    if afk and afk.enabled:
        cap = max(0.0, cfg.afk_session_cap - afk.earned_session)
        if cap <= 0.0:
            dR = 0.0
        else:
            dR = min(dR, cap)
            afk.earned_session += dR

    econ.resonance += dR
    econ.peak = max(econ.peak, econ.resonance)
    return econ.resonance


def resonance_efficiency(econ: EconomyState) -> float:
    """ℛ per unit coherence-time — closed-loop metric."""
    if econ.coherence_integral <= 1e-9:
        return 0.0
    return econ.resonance / econ.coherence_integral


def try_unlock(econ: EconomyState, track_id: str, cost: float) -> bool:
    if track_id in econ.unlocks:
        return True
    if econ.resonance < cost:
        return False
    econ.resonance -= cost
    econ.unlocks.add(track_id)
    return True
