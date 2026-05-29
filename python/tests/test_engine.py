import numpy as np

from starline import CoherentMotionEngine, EngineConfig, PlayerState, SplineTrack
from starline.engine import ControlInput
from starline.phase import sync_order_parameter


def test_spline_length_positive():
    tr = SplineTrack.oval(radius=100.0, n=8)
    assert tr.length > 0.0
    p0 = tr.position(0.0)
    p1 = tr.position(tr.length * 0.25)
    assert np.linalg.norm(p1 - p0) > 1.0


def test_smooth_driving_raises_coherence():
    tr = SplineTrack.oval()
    eng = CoherentMotionEngine(track=tr)
    eng.add_player(0, s0=0.0)

    def smooth_ctrl(_pid, _t):
        return ControlInput(throttle=0.8, brake=0.0, steer=0.0)

    snaps = eng.simulate(200, dt=1 / 60, control_fn=smooth_ctrl)
    final = snaps[-1][0]
    assert final.coherence > 0.3


def test_chaotic_driving_higher_instability_than_smooth():
    tr = SplineTrack.oval()
    cfg = EngineConfig()
    eng_smooth = CoherentMotionEngine(track=tr, config=cfg)
    eng_chaos = CoherentMotionEngine(track=tr, config=cfg)
    eng_smooth.add_player(0)
    eng_chaos.add_player(0)

    def smooth(_pid, _t):
        return ControlInput(throttle=0.7, steer=0.0)

    def chaos(_pid, t):
        # step steering spikes → high instability
        steer = 1.0 if int(t * 30) % 2 == 0 else -1.0
        return ControlInput(throttle=1.0, brake=0.5 if int(t * 10) % 3 == 0 else 0.0, steer=steer)

    s_snaps = eng_smooth.simulate(180, 1 / 60, smooth)[-1][0]
    c_snaps = eng_chaos.simulate(180, 1 / 60, chaos)[-1][0]
    assert c_snaps.instability > s_snaps.instability


def test_coherence_increases_effective_speed():
    p = PlayerState()
    p.v = 50.0
    p.coherence = 0.8
    cfg = EngineConfig(gamma=0.5)
    assert p.effective_speed(cfg) > p.v


def test_phase_sync_order_parameter():
    assert sync_order_parameter([0.0, 0.0, 0.0]) > 0.99
    assert sync_order_parameter([0.0, np.pi]) < 0.1


def test_multiplayer_sync_R_in_snapshot():
    tr = SplineTrack.oval()
    eng = CoherentMotionEngine(track=tr)
    eng.add_player(0)
    eng.add_player(1)
    eng.set_control(0, ControlInput(throttle=0.5))
    eng.set_control(1, ControlInput(throttle=0.5))
    snap = eng.step(1 / 60)[0]
    assert 0.0 <= snap.sync_R <= 1.0
