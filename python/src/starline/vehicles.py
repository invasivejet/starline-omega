"""Garage catalog — fictional marques → motion coefficient presets (Python mirror)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import EngineConfig
from .economy import EconomyState, try_unlock


@dataclass(frozen=True)
class VehicleDef:
    id: str
    display_name: str
    tagline: str
    category: str
    inspired_by: str
    cost: float
    coef: dict[str, float] = field(default_factory=dict)


VEHICLES: tuple[VehicleDef, ...] = (
    VehicleDef("urban_pulse", "Urban Pulse", "City starter", "starter", "Entry urban", 0),
    VehicleDef(
        "rhein_gt",
        "Rhein GT",
        "Autobahn cruiser",
        "europe_car",
        "German grand-tourer (BMW-class)",
        85,
        {"MaxSpeed": 118, "SteeringGain": 0.065, "Drag": 0.12, "Gamma": 0.38},
    ),
    VehicleDef(
        "sakura_r1",
        "Sakura R1",
        "Supersport lean",
        "japan_moto",
        "Japanese sport (Yamaha-class)",
        75,
        {"MaxSpeed": 108, "SteeringGain": 0.105, "CurveWeight": 2.45},
    ),
    VehicleDef(
        "brooklyn_volt",
        "Brooklyn Volt",
        "Borough snap",
        "america_ebike",
        "US city e-bike",
        28,
        {"MaxSpeed": 76, "ThrottleAccel": 96, "SteeringGain": 0.095},
    ),
    VehicleDef(
        "kyoto_flux",
        "Kyoto Flux",
        "Kei-smooth assist",
        "japan_ebike",
        "Japanese commuter e-bike",
        32,
        {"MaxSpeed": 74, "ThrottleAccel": 88},
    ),
    VehicleDef(
        "amsterdam_cruise",
        "Amsterdam Cruise",
        "Dutch upright",
        "europe_ebike",
        "Benelux city e-bike",
        38,
        {"MaxSpeed": 68, "Drag": 0.18, "SteeringGain": 0.088},
    ),
)


def get_vehicle(vehicle_id: str) -> VehicleDef | None:
    for v in VEHICLES:
        if v.id == vehicle_id:
            return v
    return None


def motion_config_for(vehicle_id: str, base: EngineConfig | None = None) -> EngineConfig:
    """Return EngineConfig with vehicle coef overrides applied."""
    base = base or EngineConfig()
    vdef = get_vehicle(vehicle_id)
    if not vdef or not vdef.coef:
        return base
    data = {k: getattr(base, k) for k in base.__dataclass_fields__}
    key_map = {
        "MaxSpeed": "max_speed",
        "SteeringGain": "steering_gain",
        "ThrottleAccel": "throttle_accel",
        "Drag": "drag",
        "Gamma": "gamma",
        "CurveWeight": "curve_weight",
        "BrakeDecel": "brake_decel",
        "MaxSpeedHard": "max_speed_hard",
    }
    for lua_key, val in vdef.coef.items():
        py_key = key_map.get(lua_key, lua_key)
        if py_key in data:
            data[py_key] = val
    return EngineConfig(**data)


def try_unlock_vehicle(econ: EconomyState, vehicle_id: str) -> bool:
    vdef = get_vehicle(vehicle_id)
    if not vdef:
        return False
    if vehicle_id in econ.unlocks:
        return True
    if econ.resonance < vdef.cost:
        return False
    if vdef.cost > 0:
        econ.resonance -= vdef.cost
    econ.unlocks.add(vehicle_id)
    return True
