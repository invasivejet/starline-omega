"""Track as musical-geometric score (not just a polyline)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .spline import SplineTrack


@dataclass
class ResonanceZone:
    """Arc-length interval with boosted coherence/audio (chorus/drop)."""
    s_start: float
    s_end: float
    label: str = "resonance"
    boost: float = 0.15


@dataclass
class TorsionEvent:
    """Modulation point — rapid curvature change."""
    s: float
    label: str = "modulation"


@dataclass
class TrackScore:
    """Playable musical topology metadata."""

    name: str = "untitled"
    # straight segments: low |κ| sustain
    sustain_threshold: float = 0.002
    # percussion density proxy from |κ| rhythm
    percussion_kappa_scale: float = 0.05
    resonance_zones: list[ResonanceZone] = field(default_factory=list)
    torsion_events: list[TorsionEvent] = field(default_factory=list)

    def resonance_boost_at(self, s: float) -> float:
        boost = 0.0
        for z in self.resonance_zones:
            if z.s_start <= s <= z.s_end or (
                z.s_end < z.s_start and (s >= z.s_start or s <= z.s_end)
            ):
                boost = max(boost, z.boost)
        return boost

    @classmethod
    def from_track_analysis(cls, track: SplineTrack, name: str = "analyzed") -> "TrackScore":
        """Auto-label resonance zones where |κ| is locally low (harmonic sustain)."""
        n = 256
        ss = np.linspace(0.0, track.length, n, endpoint=False)
        kappas = np.array([track.curvature(float(s)) for s in ss])
        sustain = kappas < np.quantile(kappas, 0.25)
        zones: list[ResonanceZone] = []
        i = 0
        while i < n:
            if sustain[i]:
                j = i
                while j < n and sustain[j]:
                    j += 1
                if j - i >= 8:
                    zones.append(
                        ResonanceZone(
                            s_start=float(ss[i]),
                            s_end=float(ss[j - 1]),
                            label="sustain",
                            boost=0.1,
                        )
                    )
                i = j
            else:
                i += 1
        # torsion: sharp curvature changes
        dk = np.abs(np.diff(kappas))
        torsions = [
            TorsionEvent(s=float(ss[idx]), label="torsion")
            for idx in np.argsort(dk)[-5:]
        ]
        return cls(name=name, resonance_zones=zones, torsion_events=torsions)
