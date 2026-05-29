"""Track topology classes — musical-geometric taxonomy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .spline import SplineTrack


class TopologyClass(str, Enum):
    SUSTAIN = "sustain"
    PULSE = "pulse"
    FRACTURE = "fracture"
    SPIRAL = "spiral"
    SILENCE = "silence"


@dataclass(frozen=True)
class TopologySegment:
    s_start: float
    s_end: float
    topology: TopologyClass
    s_norm_start: float = 0.0
    s_norm_end: float = 0.0


def classify_local_topology(
    kappa: float,
    dkappa: float,
    *,
    sustain_kappa: float = 0.002,
    pulse_dk: float = 0.01,
    fracture_kappa: float = 0.04,
    spiral_kappa: float = 0.02,
) -> TopologyClass:
    """Classify a point from local curvature signals."""
    ak = abs(kappa)
    adk = abs(dkappa)
    if ak < sustain_kappa and adk < pulse_dk * 0.5:
        return TopologyClass.SILENCE if ak < sustain_kappa * 0.25 else TopologyClass.SUSTAIN
    if adk > pulse_dk:
        return TopologyClass.PULSE
    if ak > fracture_kappa:
        return TopologyClass.FRACTURE
    if ak > spiral_kappa and adk > pulse_dk * 0.3:
        return TopologyClass.SPIRAL
    return TopologyClass.SUSTAIN


def analyze_track_topology(track: SplineTrack, n: int = 256) -> list[TopologySegment]:
    """Segment track into topology classes."""
    L = track.length
    ss = np.linspace(0.0, L, n, endpoint=False)
    kappas = np.array([track.curvature(float(s)) for s in ss])
    dk = np.gradient(kappas)

    segments: list[TopologySegment] = []
    i = 0
    while i < n:
        tc = classify_local_topology(float(kappas[i]), float(dk[i]))
        j = i + 1
        while j < n and classify_local_topology(float(kappas[j]), float(dk[j])) == tc:
            j += 1
        if j - i >= 4:
            segments.append(
                TopologySegment(
                    s_start=float(ss[i]),
                    s_end=float(ss[j - 1]),
                    topology=tc,
                    s_norm_start=float(ss[i] / L) if L > 0 else 0.0,
                    s_norm_end=float(ss[j - 1] / L) if L > 0 else 0.0,
                )
            )
        i = j
    return segments
