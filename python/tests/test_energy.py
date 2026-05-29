from starline.config import EngineConfig
from starline.economy import EconomyState, energy_increment, integrate_resonance, resonance_efficiency


def test_energy_increases_with_coherence():
    cfg = EngineConfig()
    low = energy_increment(psi=0.8, smoothness=0.9, coherence=0.5, sync_R=0.0, dt=0.1, cfg=cfg)
    high = energy_increment(psi=0.8, smoothness=0.9, coherence=0.9, sync_R=0.0, dt=0.1, cfg=cfg)
    assert high > low


def test_efficiency_metric():
    econ = EconomyState()
    integrate_resonance(
        econ,
        dt=0.1,
        coherence=0.85,
        smoothness=0.9,
        resonance_field=0.75,
        flow_state="resonant",
        sync_R=0.5,
    )
    assert econ.coherence_integral > 0
    assert resonance_efficiency(econ) > 0
