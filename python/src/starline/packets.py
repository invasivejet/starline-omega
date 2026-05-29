"""Lightweight physical · chemical · geometric packet encoding.

Deterministic auto-encode/decode for networking, telemetry, AI, and tooling.
See docs/ENCODING.md for the wire layout and composition rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

import numpy as np

from .canonical import FlowField, compute_flow
from .flow import FlowState
from .player import PlayerState
from .topology import TopologyClass
from .units import normalize_arc_length

WIRE_SIZE = 20
_WIRE_VERSION = 1.0  # slot 19 reserved; version tag optional later


class TopologyCode(IntEnum):
    SUSTAIN = 0
    PULSE = 1
    FRACTURE = 2
    SPIRAL = 3
    SILENCE = 4
    UNKNOWN = 255


class FlowStateCode(IntEnum):
    UNSTABLE = 0
    STABLE = 1
    RESONANT = 2
    FLOW = 3


_TOPOLOGY_TO_CODE = {
    TopologyClass.SUSTAIN: TopologyCode.SUSTAIN,
    TopologyClass.PULSE: TopologyCode.PULSE,
    TopologyClass.FRACTURE: TopologyCode.FRACTURE,
    TopologyClass.SPIRAL: TopologyCode.SPIRAL,
    TopologyClass.SILENCE: TopologyCode.SILENCE,
}

_FLOW_TO_CODE = {fs: FlowStateCode[fs.name] for fs in FlowState}


def topology_to_code(topology: TopologyClass | str | None) -> int:
    if topology is None:
        return int(TopologyCode.UNKNOWN)
    if isinstance(topology, str):
        try:
            topology = TopologyClass(topology)
        except ValueError:
            return int(TopologyCode.UNKNOWN)
    return int(_TOPOLOGY_TO_CODE.get(topology, TopologyCode.UNKNOWN))


def code_to_topology(code: int) -> str:
    try:
        return TopologyClass(TopologyCode(code).name.lower()).value
    except (ValueError, KeyError):
        return TopologyClass.SUSTAIN.value


def flow_to_code(state: FlowState | str) -> int:
    if isinstance(state, str):
        try:
            state = FlowState(state)
        except ValueError:
            return int(FlowStateCode.UNSTABLE)
    return int(_FLOW_TO_CODE.get(state, FlowStateCode.UNSTABLE))


def code_to_flow(code: int) -> str:
    try:
        return FlowState(FlowStateCode(code).name.lower()).value
    except (ValueError, KeyError):
        return FlowState.UNSTABLE.value


@dataclass(frozen=True)
class GeometricPacket:
    """G — differential geometry along the track."""

    s_norm: float
    kappa: float
    kappa_ahead: float
    smoothness: float
    curve_error: float
    topology_code: int = int(TopologyCode.UNKNOWN)


@dataclass(frozen=True)
class PhysicalPacket:
    """P — kinematics along arc-length."""

    v: float
    a: float
    jerk: float
    v_eff: float


@dataclass(frozen=True)
class ChemicalPacket:
    """C — energetic order / disorder."""

    coherence: float
    instability: float
    resonance: float
    phase: float
    noise: float


@dataclass(frozen=True)
class HarmonicPacket:
    """H — ensemble synchronization."""

    sync_R: float


@dataclass(frozen=True)
class FlowPacket:
    """ℱ — coupled identity summary."""

    value: float
    state_code: int

    @property
    def state(self) -> str:
        return code_to_flow(self.state_code)


@dataclass(frozen=True)
class EnginePacket:
    """Full encoded state — one sim tick."""

    geometric: GeometricPacket
    physical: PhysicalPacket
    chemical: ChemicalPacket
    harmonic: HarmonicPacket
    flow: FlowPacket
    wire_version: float = _WIRE_VERSION

    def to_wire(self) -> list[float]:
        g, p, c, h, f = self.geometric, self.physical, self.chemical, self.harmonic, self.flow
        return [
            g.s_norm,
            g.kappa,
            g.kappa_ahead,
            g.smoothness,
            g.curve_error,
            float(g.topology_code),
            p.v,
            p.a,
            p.jerk,
            p.v_eff,
            c.coherence,
            c.instability,
            c.resonance,
            c.phase,
            c.noise,
            h.sync_R,
            f.value,
            float(f.state_code),
            0.0,
            self.wire_version,
        ]

    @classmethod
    def from_wire(cls, wire: list[float] | np.ndarray) -> "EnginePacket":
        w = list(wire)
        if len(w) < WIRE_SIZE:
            w = w + [0.0] * (WIRE_SIZE - len(w))
        return cls(
            geometric=GeometricPacket(
                s_norm=w[0],
                kappa=w[1],
                kappa_ahead=w[2],
                smoothness=w[3],
                curve_error=w[4],
                topology_code=int(w[5]),
            ),
            physical=PhysicalPacket(v=w[6], a=w[7], jerk=w[8], v_eff=w[9]),
            chemical=ChemicalPacket(
                coherence=w[10],
                instability=w[11],
                resonance=w[12],
                phase=w[13],
                noise=w[14],
            ),
            harmonic=HarmonicPacket(sync_R=w[15]),
            flow=FlowPacket(value=w[16], state_code=int(w[17])),
            wire_version=w[19] if len(w) > 19 else _WIRE_VERSION,
        )

    def as_dict(self) -> dict[str, Any]:
        g, p, c, h, f = self.geometric, self.physical, self.chemical, self.harmonic, self.flow
        return {
            "geometric": {
                "s_norm": g.s_norm,
                "kappa": g.kappa,
                "kappa_ahead": g.kappa_ahead,
                "S": g.smoothness,
                "curve_error": g.curve_error,
                "topology": code_to_topology(g.topology_code),
            },
            "physical": {"v": p.v, "a": p.a, "jerk": p.jerk, "v_eff": p.v_eff},
            "chemical": {
                "c": c.coherence,
                "instability": c.instability,
                "resonance": c.resonance,
                "phi": c.phase,
                "noise": c.noise,
            },
            "harmonic": {"R": h.sync_R},
            "flow": {"value": f.value, "state": f.state},
        }


@dataclass(frozen=True)
class TrackLattice:
    """Static geometric score — discretized track for gen / AI / analysis."""

    name: str
    s_norm: np.ndarray
    kappa: np.ndarray
    topology_code: np.ndarray

    @classmethod
    def from_track(
        cls,
        s_norm_nodes: np.ndarray,
        kappa: np.ndarray,
        topology_codes: np.ndarray,
        name: str = "track",
    ) -> "TrackLattice":
        return cls(
            name=name,
            s_norm=np.asarray(s_norm_nodes, dtype=np.float64),
            kappa=np.asarray(kappa, dtype=np.float64),
            topology_code=np.asarray(topology_codes, dtype=np.uint8),
        )

    def to_wire_matrix(self) -> np.ndarray:
        """Shape (N, 3): s_norm, kappa, topology_code."""
        return np.column_stack([self.s_norm, self.kappa, self.topology_code.astype(np.float64)])

    def sample_at(self, s_norm: float) -> tuple[float, float, int]:
        """Nearest-node sample."""
        if len(self.s_norm) == 0:
            return 0.0, 0.0, int(TopologyCode.UNKNOWN)
        idx = int(np.argmin(np.abs(self.s_norm - s_norm)))
        return float(self.kappa[idx]), float(self.s_norm[idx]), int(self.topology_code[idx])


def encode_packet(
    p: PlayerState,
    track_length: float,
    kappa: float,
    kappa_ahead: float,
    sync_R: float,
    resonance: float,
    noise: float,
    *,
    topology: TopologyClass | str | None = None,
    flow_state: FlowState | str = FlowState.UNSTABLE,
) -> EnginePacket:
    """Auto-encode runtime player + local geometry into layered packets."""
    s_norm = normalize_arc_length(p.s, track_length)
    ff: FlowField = compute_flow(
        p.v, p.smoothness, p.coherence, p.phase, sync_R, kappa
    )
    return EnginePacket(
        geometric=GeometricPacket(
            s_norm=s_norm,
            kappa=kappa,
            kappa_ahead=kappa_ahead,
            smoothness=p.smoothness,
            curve_error=p.curve_error,
            topology_code=topology_to_code(topology),
        ),
        physical=PhysicalPacket(
            v=p.v,
            a=p.a,
            jerk=p.jerk,
            v_eff=p.v_eff,
        ),
        chemical=ChemicalPacket(
            coherence=p.coherence,
            instability=p.instability,
            resonance=resonance,
            phase=p.phase,
            noise=noise,
        ),
        harmonic=HarmonicPacket(sync_R=sync_R),
        flow=FlowPacket(
            value=ff.value,
            state_code=flow_to_code(flow_state),
        ),
    )


def decode_perceptual(pkt: EnginePacket) -> dict[str, float]:
    """Ψ projection hints — client/audio reads wire, does not integrate sim."""
    g, p, c, h = pkt.geometric, pkt.physical, pkt.chemical, pkt.harmonic
    return {
        "tempo_norm": min(1.0, p.v / 120.0),
        "dissonance": min(1.0, (1.0 - c.coherence) + (1.0 - g.smoothness) * 0.35),
        "harmony": c.coherence * g.smoothness * (0.35 + 0.65 * h.sync_R),
        "richness": c.coherence * g.smoothness,
        "flow": pkt.flow.value,
    }
