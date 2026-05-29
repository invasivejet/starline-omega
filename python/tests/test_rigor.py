"""Final engine rigor: units, stability, hysteresis, noise, resonance field, ticks."""

import numpy as np

from starline import CoherentMotionEngine, EngineConfig, SplineTrack
from starline.canonical import compute_flow
from starline.coherence import update_coherence
from starline.engine import ControlInput
from starline.flow import FlowState, FlowStateMachine, classify_flow
from starline.input_noise import input_noise
from starline.latency import DEFAULT_LATENCY
from starline.player import PlayerState
from starline.readability import is_readable, visual_complexity
from starline.resonance import resonance_field
from starline.stability import COHERENCE, VELOCITY, apply_stability
from starline.topology import TopologyClass, analyze_track_topology
from starline.units import normalize_arc_length


def test_canonical_units_normalize_s():
    assert 0.0 <= normalize_arc_length(50.0, 100.0) < 1.0
    assert abs(normalize_arc_length(100.0, 100.0) - 0.0) < 1e-9


def test_stability_envelopes_clamp():
    p = PlayerState()
    p.v = 500.0
    p.jerk = 100.0
    apply_stability(p, EngineConfig(max_speed_hard=200.0))
    assert p.v <= 200.0
    assert abs(p.jerk) <= 20.0
    assert COHERENCE.in_stable_band(p.coherence)
    assert VELOCITY.stable_max == 120.0


def test_no_false_reward_noise_reduces_coherence():
    p = PlayerState()
    p.coherence = 0.5
    p.steer = 1.0
    p.steer_prev = -1.0
    p.jerk = 15.0
    cfg = EngineConfig()
    noise = input_noise(p, cfg)
    c0 = p.coherence
    update_coherence(p, cfg, 0.1, smoothness=1.0, instability=0.0, resonance=0.8, noise=noise)
    c_noisy = p.coherence
    p.coherence = c0
    update_coherence(p, cfg, 0.1, smoothness=1.0, instability=0.0, resonance=0.8, noise=0.0)
    c_clean = p.coherence
    assert c_noisy < c_clean


def test_resonance_field_bounded_not_buff():
    p = PlayerState()
    p.smoothness = 0.9
    p.curve_error = 0.01
    p.steer = 0.2
    psi = resonance_field(p, 0.01, 0.02, 0.8, EngineConfig())
    assert 0.0 <= psi <= 1.0


def test_flow_hysteresis_prevents_flicker():
    cfg = EngineConfig()
    fsm = FlowStateMachine()
    fsm.update(0.95, 0.9, cfg)
    assert fsm.state == FlowState.FLOW
    fsm.update(0.87, 0.8, cfg)  # below enter but above exit
    assert fsm.state == FlowState.FLOW
    fsm.update(0.80, 0.7, cfg)
    assert fsm.state != FlowState.FLOW


def test_simulation_vs_presentation_ticks():
    eng = CoherentMotionEngine(track=SplineTrack.oval())
    eng.add_player(0)
    eng.set_control(0, ControlInput(throttle=0.7))
    eng.fixed_update(1 / 30)
    pres = eng.present()
    assert len(pres) == 1
    assert 0.0 <= pres[0].alpha <= 1.0


def test_canonical_flow_identity():
    ff = compute_flow(60, 0.8, 0.7, 1.0, 0.6, 0.02)
    assert 0.0 <= ff.value <= 1.0
    assert ff.energetic == 0.7


def test_topology_analysis():
    segs = analyze_track_topology(SplineTrack.oval(), n=128)
    assert len(segs) > 0
    assert segs[0].topology in TopologyClass


def test_readability_budget():
    c_low = visual_complexity(trail_segments=10, ui_elements=2)
    c_high = visual_complexity(trail_segments=64, ui_elements=12, vfx_intensity=1.0)
    assert is_readable(c_low)
    assert not is_readable(c_high) or c_high >= c_low


def test_latency_budget_targets():
    assert DEFAULT_LATENCY.input_to_motion_ms == 50.0
