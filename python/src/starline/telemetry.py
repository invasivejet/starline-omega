"""Field research telemetry — emergent coordination structures."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np

from .flow import FlowState


@dataclass
class Telemetry:
    coherence_samples: list[float] = field(default_factory=list)
    smoothness_samples: list[float] = field(default_factory=list)
    instability_samples: list[float] = field(default_factory=list)
    sync_samples: list[float] = field(default_factory=list)
    steer_samples: list[float] = field(default_factory=list)
    resonance_samples: list[float] = field(default_factory=list)
    noise_samples: list[float] = field(default_factory=list)

    # segment bins on s_norm
    coherence_by_segment: dict[int, list[float]] = field(default_factory=lambda: defaultdict(list))
    corner_failures: list[tuple[float, float, float, float]] = field(default_factory=list)

    flow_dwell_ticks: dict[str, int] = field(
        default_factory=lambda: {s.value: 0 for s in FlowState}
    )
    topology_dwell: dict[str, int] = field(default_factory=dict)
    resonance_chain_ticks: int = 0
    _in_resonance_chain: bool = False

    ticks: int = 0
    segment_bins: int = 16

    def record(
        self,
        *,
        s: float,
        s_norm: float = 0.0,
        c: float,
        S: float,
        I: float,
        R: float,
        steer: float,
        kappa: float,
        resonance: float = 0.0,
        noise: float = 0.0,
        flow_state: str = "unstable",
        topology: str | None = None,
    ) -> None:
        self.ticks += 1
        self.coherence_samples.append(c)
        self.smoothness_samples.append(S)
        self.instability_samples.append(I)
        self.sync_samples.append(R)
        self.steer_samples.append(steer)
        self.resonance_samples.append(resonance)
        self.noise_samples.append(noise)

        seg = min(self.segment_bins - 1, int(s_norm * self.segment_bins))
        self.coherence_by_segment[seg].append(c)

        self.flow_dwell_ticks[flow_state] = self.flow_dwell_ticks.get(flow_state, 0) + 1
        if topology:
            self.topology_dwell[topology] = self.topology_dwell.get(topology, 0) + 1

        if resonance > 0.7 and S > 0.6:
            self.resonance_chain_ticks += 1
            self._in_resonance_chain = True
        elif self._in_resonance_chain:
            self._in_resonance_chain = False

        if S < 0.35 or I > 0.5:
            self.corner_failures.append((s, s_norm, S, I))

    def steering_entropy(self) -> float:
        if len(self.steer_samples) < 8:
            return 0.0
        x = np.array(self.steer_samples, dtype=np.float64)
        hist, _ = np.histogram(x, bins=16, range=(-1.0, 1.0), density=True)
        p = hist[hist > 0]
        return float(-(p * np.log(p + 1e-12)).sum())

    def coherence_histogram(self, bins: int = 20) -> tuple[np.ndarray, np.ndarray]:
        if not self.coherence_samples:
            return np.zeros(bins), np.linspace(0, 1, bins + 1)
        c = np.array(self.coherence_samples)
        h, edges = np.histogram(c, bins=bins, range=(0.0, 1.0))
        return h.astype(np.float64), edges

    def segment_coherence_means(self) -> dict[int, float]:
        return {k: float(np.mean(v)) for k, v in self.coherence_by_segment.items() if v}

    def noise_coherence_correlation(self) -> float:
        """Should be negative globally (∂c/∂noise < 0)."""
        if len(self.noise_samples) < 16:
            return 0.0
        n = np.array(self.noise_samples, dtype=np.float64)
        c = np.array(self.coherence_samples[: len(n)], dtype=np.float64)
        if n.std() < 1e-9 or c.std() < 1e-9:
            return 0.0
        return float(np.corrcoef(n, c)[0, 1])

    def sync_stability(self) -> dict[str, float]:
        """Ensemble order parameter statistics."""
        if not self.sync_samples:
            return {"mean": 0.0, "p90": 0.0, "max": 0.0}
        r = np.array(self.sync_samples, dtype=np.float64)
        return {
            "mean": float(r.mean()),
            "p90": float(np.quantile(r, 0.9)),
            "max": float(r.max()),
        }

    def spatial_coherence_profile(self) -> dict[str, float]:
        """mean(c | s_norm bin) — musical legibility of track."""
        out: dict[str, float] = {}
        for seg, vals in sorted(self.coherence_by_segment.items()):
            if vals:
                out[f"bin_{seg:02d}"] = float(np.mean(vals))
        return out

    def summary(self) -> dict:
        c = np.array(self.coherence_samples) if self.coherence_samples else np.array([0.0])
        res = np.array(self.resonance_samples) if self.resonance_samples else np.array([0.0])
        return {
            "ticks": self.ticks,
            "coherence": {
                "mean": float(c.mean()),
                "p50": float(np.quantile(c, 0.5)),
                "p90": float(np.quantile(c, 0.9)),
            },
            "resonance": {"mean": float(res.mean()), "p90": float(np.quantile(res, 0.9))},
            "flow_dwell_fraction": {
                k: v / max(self.ticks, 1) for k, v in self.flow_dwell_ticks.items()
            },
            "topology_dwell_fraction": {
                k: v / max(self.ticks, 1) for k, v in self.topology_dwell.items()
            },
            "resonance_chain_fraction": self.resonance_chain_ticks / max(self.ticks, 1),
            "corner_failure_count": len(self.corner_failures),
            "steering_entropy": self.steering_entropy(),
            "sync_mean": float(np.mean(self.sync_samples)) if self.sync_samples else 0.0,
            "segment_coherence": self.segment_coherence_means(),
            "spatial_profile": self.spatial_coherence_profile(),
            "noise_mean": float(np.mean(self.noise_samples)) if self.noise_samples else 0.0,
            "noise_coherence_corr": self.noise_coherence_correlation(),
            "sync_stability": self.sync_stability(),
        }
