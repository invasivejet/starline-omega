from starline import CoherentMotionEngine, EngineConfig, SplineTrack
from starline.afk import AfkSession, compute_autopilot_control
from starline.economy import EconomyState, integrate_resonance
from starline.engine import ControlInput


def test_afk_earns_less_than_active():
    cfg = EngineConfig()
    track = SplineTrack.oval()
    steps = 300
    dt = cfg.sim_dt

    def run(afk_enabled: bool) -> float:
        eng = CoherentMotionEngine(track=track, config=cfg)
        eng.add_player(0)
        econ = EconomyState()
        afk = AfkSession(enabled=afk_enabled)
        for i in range(steps):
            if afk_enabled:
                p = eng.players[0]
                ctrl = compute_autopilot_control(
                    track.curvature(p.s),
                    track.curvature(p.s + 10),
                    p.v,
                    cfg,
                )
                eng.set_control(0, ctrl)
            else:
                eng.set_control(0, ControlInput(throttle=0.75, steer=0.1))
            s = eng.step(dt)[0]
            integrate_resonance(
                econ,
                dt=dt,
                coherence=s.coherence,
                smoothness=s.smoothness,
                resonance_field=s.resonance,
                flow_state=s.flow_state,
                sync_R=s.sync_R,
                velocity=s.v,
                cfg=cfg,
                afk=afk,
            )
        return econ.resonance

    assert run(True) < run(False)


def test_afk_session_cap():
    cfg = EngineConfig(afk_session_cap=5.0)
    econ = EconomyState()
    afk = AfkSession(enabled=True)
    for _ in range(500):
        integrate_resonance(
            econ,
            dt=0.1,
            coherence=0.8,
            smoothness=0.9,
            resonance_field=0.9,
            flow_state="resonant",
            sync_R=0.0,
            velocity=50.0,
            cfg=cfg,
            afk=afk,
        )
    assert afk.earned_session <= 5.0 + 0.01
