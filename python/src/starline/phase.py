"""Phase synchronization layer (multiplayer)."""

from __future__ import annotations

import cmath

from .config import EngineConfig
from .player import PlayerState


def update_phase(p: PlayerState, cfg: EngineConfig, dt: float) -> float:
    p.phase = (p.phase + p.v * dt * cfg.omega) % (2.0 * 3.141592653589793)
    return p.phase


def sync_order_parameter(phases: list[float]) -> float:
    """R = | Σ exp(i·phase_j) / N | ∈ [0, 1]."""
    if not phases:
        return 0.0
    z = sum(cmath.exp(1j * ph) for ph in phases) / len(phases)
    return float(abs(z))


def slipstream_drag_factor(R: float, cfg: EngineConfig) -> float:
    """High sync → reduced effective drag."""
    return max(0.0, 1.0 - cfg.sync_slipstream * R)
