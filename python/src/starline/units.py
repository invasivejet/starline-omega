"""Canonical units — prevent tuning ambiguity at scale."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CanonicalUnits:
    """Engine-wide unit contract (see docs/RIGOR.md)."""

    # arc-length along spline (world units, e.g. studs)
    arc_length: str = "arc_length"
    velocity: str = "arc_length / second"
    acceleration: str = "arc_length / second²"
    curvature: str = "inverse arc_length"
    phase: str = "radians"
    coherence: str = "dimensionless"
    sync_R: str = "dimensionless"
    smoothness: str = "dimensionless"


CANONICAL = CanonicalUnits()


def normalize_arc_length(s: float, track_length: float) -> float:
    """s_norm ∈ [0, 1) — canonical display / telemetry coordinate."""
    if track_length <= 0.0:
        return 0.0
    return (s % track_length) / track_length


def denormalize_arc_length(s_norm: float, track_length: float) -> float:
    return (s_norm % 1.0) * track_length
