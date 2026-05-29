"""State-driven audio field mapping.

Perceptual law (frozen invariant):

    A(t) = f(v, S, c, R, κ)

No arbitrary soundtrack switching — all channels derive from sacred variables.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import EngineConfig
from .flow import FlowState
from .player import PlayerState
from .spline import SplineTrack


@dataclass
class AudioField:
    tempo: float
    dissonance: float
    harmony: float
    percussion: float
    richness: float
    flow_state: str


def compute_audio(
    p: PlayerState,
    cfg: EngineConfig,
    track: SplineTrack,
    sync_R: float,
    *,
    flow_state: FlowState | None = None,
) -> AudioField:
    """A(t) = f(v, S, c, R, κ) with hysteresis flow-state modulation."""
    v = p.v
    S = p.smoothness
    c = p.coherence
    R = sync_R
    kappa = track.curvature(p.s)

    tempo = cfg.base_tempo + v * cfg.tempo_per_speed
    # failure = desynchronization: low c, low S
    dissonance = (
        (1.0 - c) * cfg.dissonance_from_coherence
        + (1.0 - S) * 0.35
    )
    harmony = c * S * (0.35 + 0.65 * R) * cfg.harmony_from_sync
    percussion = min(1.0, abs(kappa) * 0.05 + (1.0 - S) * 0.1)
    richness = c * S

    fs = flow_state if flow_state is not None else FlowState.UNSTABLE
    if flow_state is None:
        if c > cfg.flow_enter_flow_c and R > cfg.flow_enter_flow_R:
            fs = FlowState.FLOW
        elif c > cfg.flow_enter_resonant_c:
            fs = FlowState.RESONANT
        elif c > cfg.flow_enter_stable_c:
            fs = FlowState.STABLE
    if fs == FlowState.FLOW:
        harmony *= 1.15
        dissonance *= 0.85
    elif fs == FlowState.UNSTABLE:
        dissonance = min(1.0, dissonance * 1.25)
        harmony *= 0.7

    return AudioField(
        tempo=tempo,
        dissonance=min(1.0, dissonance),
        harmony=min(1.0, harmony),
        percussion=percussion,
        richness=richness,
        flow_state=fs.value,
    )
