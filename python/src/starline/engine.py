"""Coherent Motion Engine — deterministic sim + interpolated presentation."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .audio import AudioField, compute_audio
from .canonical import FlowField, compute_flow
from .config import EngineConfig
from .coherence import update_coherence
from .flow import FlowStateMachine
from .input_noise import input_noise
from .motion import advance_arc_length, update_jerk, update_velocity
from .phase import slipstream_drag_factor, sync_order_parameter, update_phase
from .player import PlayerState
from .resonance import resonance_field
from .smoothness import anticipatory_kappa, instability, smoothness_score
from .spline import SplineTrack
from .stability import apply_stability
from .telemetry import Telemetry
from .ticks import PresentationBuffer, SimClock
from .topology import TopologyClass, analyze_track_topology
from .track_score import TrackScore
from .units import normalize_arc_length


@dataclass
class ControlInput:
    throttle: float = 0.0
    brake: float = 0.0
    steer: float = 0.0


@dataclass
class StepSnapshot:
    """Per simulation tick — authoritative state."""

    player_id: int
    s: float
    s_norm: float
    v: float
    v_eff: float
    coherence: float
    phase: float
    smoothness: float
    instability: float
    position: np.ndarray
    audio: AudioField
    sync_R: float = 0.0
    flow_state: str = "unstable"
    resonance: float = 0.0
    input_noise: float = 0.0
    flow_field: FlowField | None = None


@dataclass
class PresentSnapshot:
    """Interpolated presentation frame (non-authoritative)."""

    player_id: int
    s: float
    s_norm: float
    v: float
    coherence: float
    position: np.ndarray
    flow_state: str
    flow_value: float
    alpha: float


@dataclass
class CoherentMotionEngine:
    """Motion → Smoothness → Coherence → Phase → Audio/Visual."""

    track: SplineTrack
    config: EngineConfig = field(default_factory=EngineConfig)
    track_score: TrackScore | None = None
    telemetry: Telemetry | None = None
    players: dict[int, PlayerState] = field(default_factory=dict)
    flow_machines: dict[int, FlowStateMachine] = field(default_factory=dict)
    time: float = 0.0

    sim_clock: SimClock = field(default_factory=SimClock)
    presentation: PresentationBuffer = field(default_factory=PresentationBuffer)
    topology_segments: list = field(default_factory=list)

    def __post_init__(self) -> None:
        self.sim_clock.sim_dt = self.config.sim_dt
        if not self.topology_segments:
            self.topology_segments = analyze_track_topology(self.track)

    def add_player(self, player_id: int, s0: float = 0.0) -> PlayerState:
        p = PlayerState()
        p.reset(s0)
        p.position = self.track.position(s0)
        self.players[player_id] = p
        self.flow_machines[player_id] = FlowStateMachine()
        return p

    def remove_player(self, player_id: int) -> None:
        self.players.pop(player_id, None)
        self.flow_machines.pop(player_id, None)

    def set_control(self, player_id: int, ctrl: ControlInput) -> None:
        p = self.players[player_id]
        p.throttle = max(0.0, min(1.0, ctrl.throttle))
        p.brake = max(0.0, min(1.0, ctrl.brake))
        p.steer = max(-1.0, min(1.0, ctrl.steer))

    def sync_R(self) -> float:
        phases = [p.phase for p in self.players.values()]
        return sync_order_parameter(phases)

    def _topology_at(self, s: float) -> TopologyClass | None:
        for seg in self.topology_segments:
            if seg.s_start <= s <= seg.s_end:
                return seg.topology
        return None

    def step(self, dt: float) -> list[StepSnapshot]:
        """Fixed simulation tick — deterministic."""
        if dt <= 0.0 or not self.players:
            return []

        cfg = self.config
        R = self.sync_R()
        drag_scale = slipstream_drag_factor(R, cfg)
        L = self.track.length
        out: list[StepSnapshot] = []

        for pid, p in self.players.items():
            update_velocity(p, cfg, dt, drag_scale=drag_scale)
            update_jerk(p, dt)

            k0, k1 = anticipatory_kappa(self.track, p.s, p.v_eff, cfg)
            S = smoothness_score(p, cfg, k0, kappa_ahead=k1)
            inst = instability(p, cfg)
            noise = input_noise(p, cfg)

            psi = resonance_field(p, k0, k1, R, cfg)
            topo = self._topology_at(p.s)
            if topo == TopologyClass.SUSTAIN or topo == TopologyClass.SILENCE:
                psi = min(1.0, psi * 1.05)
            elif topo == TopologyClass.FRACTURE:
                psi *= 0.92

            update_coherence(p, cfg, dt, S, inst, resonance=psi, noise=noise)
            update_phase(p, cfg, dt)
            advance_arc_length(p, cfg, dt, L)
            p.position = self.track.position(p.s)
            apply_stability(p, cfg)

            fsm = self.flow_machines[pid]
            fs = fsm.update(p.coherence, R, cfg)

            ff = compute_flow(p.v, S, p.coherence, p.phase, R, k0)
            audio = compute_audio(p, cfg, self.track, R, flow_state=fs)

            s_norm = normalize_arc_length(p.s, L)

            if self.telemetry is not None:
                self.telemetry.record(
                    s=p.s,
                    s_norm=s_norm,
                    c=p.coherence,
                    S=S,
                    I=inst,
                    R=R,
                    steer=p.steer,
                    kappa=k0,
                    resonance=psi,
                    noise=noise,
                    flow_state=fs.value,
                    topology=topo.value if topo else None,
                )

            out.append(
                StepSnapshot(
                    player_id=pid,
                    s=p.s,
                    s_norm=s_norm,
                    v=p.v,
                    v_eff=p.v_eff,
                    coherence=p.coherence,
                    phase=p.phase,
                    smoothness=S,
                    instability=inst,
                    position=p.position.copy(),
                    audio=audio,
                    sync_R=R,
                    flow_state=fs.value,
                    resonance=psi,
                    input_noise=noise,
                    flow_field=ff,
                )
            )

        self.presentation.advance(out)
        self.time += dt
        return out

    def fixed_update(self, frame_dt: float) -> list[StepSnapshot]:
        """Consume variable frame_dt; run N fixed sim steps."""
        n = self.sim_clock.consume(frame_dt)
        last: list[StepSnapshot] = []
        for _ in range(n):
            last = self.step(self.sim_clock.sim_dt)
        return last

    def present(self, alpha: float | None = None) -> list[PresentSnapshot]:
        """Interpolated presentation snapshots."""
        a = self.sim_clock.alpha if alpha is None else alpha
        out: list[PresentSnapshot] = []
        L = self.track.length
        for pid in self.presentation.curr:
            pos = self.presentation.interpolate_position(pid, a)
            if pos is None:
                pos = np.zeros(3)
            out.append(
                PresentSnapshot(
                    player_id=pid,
                    s=self.presentation.interpolate_scalar(pid, "s", a),
                    s_norm=normalize_arc_length(
                        self.presentation.interpolate_scalar(pid, "s", a), L
                    ),
                    v=self.presentation.interpolate_scalar(pid, "v", a),
                    coherence=self.presentation.interpolate_scalar(pid, "coherence", a),
                    position=pos,
                    flow_state=getattr(self.presentation.curr[pid], "flow_state", "unstable"),
                    flow_value=(
                        self.presentation.curr[pid].flow_field.value
                        if self.presentation.curr[pid].flow_field
                        else 0.0
                    ),
                    alpha=a,
                )
            )
        return out

    def simulate(
        self,
        n_steps: int,
        dt: float,
        control_fn,
    ) -> list[list[StepSnapshot]]:
        history: list[list[StepSnapshot]] = []
        for _ in range(n_steps):
            for pid in self.players:
                self.set_control(pid, control_fn(pid, self.time))
            history.append(self.step(dt))
        return history
