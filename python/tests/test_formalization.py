"""Post-MVP formalization: asymptotic coherence, flow states, audio law."""

import numpy as np

from starline import CoherentMotionEngine, EngineConfig, SplineTrack
from starline.audio import compute_audio
from starline.coherence import update_coherence
from starline.engine import ControlInput
from starline.flow import FlowState, FlowStateMachine, classify_flow
from starline.player import PlayerState
from starline.telemetry import Telemetry
from starline.track_score import TrackScore


def test_coherence_asymptotic_near_ceiling():
    p = PlayerState()
    p.coherence = 0.95
    cfg = EngineConfig(alpha=2.5, coherence_power=2.0)
    update_coherence(p, cfg, 1 / 60, smoothness=1.0, instability=0.0, resonance=0.5, noise=0.0)
    assert p.coherence < 0.99


def test_coherence_power_slower_than_linear_at_high_c():
    cfg = EngineConfig(alpha=2.5, coherence_power=2.0)
    p_lin = PlayerState()
    p_pow = PlayerState()
    p_lin.coherence = p_pow.coherence = 0.85
    update_coherence(
        p_lin, EngineConfig(alpha=2.5, coherence_power=1.0), 0.1, 1.0, 0.0, resonance=0.5, noise=0.0
    )
    update_coherence(p_pow, cfg, 0.1, 1.0, 0.0, resonance=0.5, noise=0.0)
    assert p_pow.coherence < p_lin.coherence


def test_flow_state_thresholds():
    cfg = EngineConfig()
    assert classify_flow(0.3, 1.0) == FlowState.UNSTABLE
    assert classify_flow(0.5, 0.0) == FlowState.STABLE
    assert classify_flow(0.75, 0.0) == FlowState.RESONANT
    fsm = FlowStateMachine()
    assert fsm.update(0.95, 0.9, cfg) == FlowState.FLOW


def test_audio_derives_from_sacred_variables():
    tr = SplineTrack.oval()
    p = PlayerState()
    p.v = 40.0
    p.coherence = 0.8
    p.smoothness = 0.9
    p.s = 10.0
    a = compute_audio(p, EngineConfig(), tr, sync_R=0.7)
    assert a.tempo > EngineConfig().base_tempo
    assert 0.0 <= a.dissonance <= 1.0
    assert a.richness == p.coherence * p.smoothness
    assert a.flow_state in {s.value for s in FlowState}


def test_telemetry_summary():
    tel = Telemetry()
    for _ in range(100):
        tel.record(s=1.0, c=0.6, S=0.7, I=0.1, R=0.5, steer=0.2, kappa=0.01)
    s = tel.summary()
    assert s["ticks"] == 100
    assert "flow_dwell_fraction" in s


def test_track_score_resonance_boost():
    from starline.track_score import ResonanceZone

    score = TrackScore(
        name="test",
        resonance_zones=[ResonanceZone(s_start=5.0, s_end=15.0, boost=0.2)],
    )
    assert score.resonance_boost_at(10.0) == 0.2
    assert score.resonance_boost_at(0.0) == 0.0


def test_engine_exposes_flow_in_snapshot():
    eng = CoherentMotionEngine(track=SplineTrack.oval(), telemetry=Telemetry())
    eng.add_player(0)
    eng.set_control(0, ControlInput(throttle=0.8))
    snap = eng.step(1 / 60)[0]
    assert snap.flow_state in {s.value for s in FlowState}
    assert eng.telemetry is not None
    assert eng.telemetry.ticks >= 1
