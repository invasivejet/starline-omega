from starline.economy import EconomyState, integrate_resonance, try_unlock


def test_resonance_integrates_when_coherent():
    e = EconomyState()
    r0 = e.resonance
    integrate_resonance(
        e,
        dt=0.1,
        coherence=0.8,
        smoothness=0.9,
        resonance_field=0.7,
        flow_state="resonant",
        sync_R=0.5,
    )
    assert e.resonance > r0


def test_unlock_spends_resonance():
    e = EconomyState(resonance=50.0)
    assert try_unlock(e, "circuit", 40.0)
    assert "circuit" in e.unlocks
    assert e.resonance == 10.0
