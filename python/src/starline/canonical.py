"""Canonical engine identity: Flow = ℱ(v, S, c, φ, R, κ)."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class FlowField:
    """Scalar summary + components of the coupled perceptual-geometric system."""

    value: float
    kinematic: float
    geometric: float
    energetic: float
    harmonic: float
    curvature: float

    def as_dict(self) -> dict[str, float]:
        return {
            "flow": self.value,
            "kinematic": self.kinematic,
            "geometric": self.geometric,
            "energetic": self.energetic,
            "harmonic": self.harmonic,
            "curvature": self.curvature,
        }


def compute_flow(
    v: float,
    S: float,
    c: float,
    phi: float,
    R: float,
    kappa: float,
    *,
    v_ref: float = 80.0,
    kappa_scale: float = 0.05,
) -> FlowField:
    """ℱ(v, S, c, φ, R, κ) — the engine's core identity."""
    kinematic = min(1.0, max(0.0, v / max(v_ref, 1e-6)))
    geometric = S
    energetic = c
    harmonic = R * (0.5 + 0.5 * math.cos(phi))  # phase-aware sync
    curvature = 1.0 / (1.0 + abs(kappa) * kappa_scale)

    value = (energetic * geometric * harmonic) ** 0.5 * (0.5 + 0.5 * kinematic) * curvature
    value = max(0.0, min(1.0, value))

    return FlowField(
        value=value,
        kinematic=kinematic,
        geometric=geometric,
        energetic=energetic,
        harmonic=harmonic,
        curvature=curvature,
    )
