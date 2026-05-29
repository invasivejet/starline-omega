from starline import CoherentMotionEngine, EngineConfig, SplineTrack
from starline.economy import EconomyState
from starline.engine import ControlInput
from starline.vehicles import motion_config_for, try_unlock_vehicle


def test_vehicle_preset_changes_max_speed():
    base = EngineConfig()
    moto = motion_config_for("sakura_r1", base)
    assert moto.max_speed < base.max_speed or moto.steering_gain > base.steering_gain


def test_unlock_vehicle_spends_resonance():
    econ = EconomyState(resonance=100.0, unlocks={"oval", "urban_pulse"})
    assert try_unlock_vehicle(econ, "brooklyn_volt")
    assert "brooklyn_volt" in econ.unlocks
    assert econ.resonance == 72.0


def test_different_vehicles_feel_different():
    track = SplineTrack.oval()
    steps = 400
    dt = 1 / 60

    def final_speed(vehicle_id: str) -> float:
        cfg = motion_config_for(vehicle_id)
        eng = CoherentMotionEngine(track=track, config=cfg)
        eng.add_player(0)
        for _ in range(steps):
            eng.set_control(0, ControlInput(throttle=0.8, steer=0.06))
            s = eng.step(dt)[0]
        return s.v

    gt = final_speed("rhein_gt")
    ebike = final_speed("brooklyn_volt")
    assert gt > ebike
