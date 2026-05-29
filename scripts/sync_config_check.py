#!/usr/bin/env python3
"""Verify Python config.py keys match Roblox Config.lua (local CI guard)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / "python" / "src" / "starline" / "config.py"
LUA = ROOT / "roblox" / "Starline" / "Config.lua"

# (python_field, lua_name)
PAIRS = [
    ("alpha", "Alpha"),
    ("beta", "Beta"),
    ("coherence_power", "CoherencePower"),
    ("gamma", "Gamma"),
    ("drag", "Drag"),
    ("max_speed", "MaxSpeed"),
    ("noise_penalty", "NoisePenalty"),
    ("resonance_earn_k", "ResonanceEarnK"),
    ("resonance_coherence_gamma", "ResonanceCoherenceGamma"),
    ("resonance_sync_lambda", "ResonanceSyncLambda"),
    ("max_sim_catchup_sec", "MaxSimCatchupSec"),
]


def parse_lua_values(text: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for name, _ in PAIRS:
        pass
    for lua_name, _ in [(b, a) for a, b in PAIRS]:
        m = re.search(rf"Config\.{lua_name}\s*=\s*([0-9.]+)", text)
        if m:
            out[lua_name] = float(m.group(1))
    return out


def parse_py_values(text: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for py_name, _ in PAIRS:
        m = re.search(rf"{py_name}:\s*float\s*=\s*([0-9.]+)", text)
        if m:
            out[py_name] = float(m.group(1))
    return out


def main() -> int:
    py_text = PY.read_text()
    lua_text = LUA.read_text()
    errors = []
    for py_name, lua_name in PAIRS:
        pm = re.search(rf"^\s*{re.escape(py_name)}:\s*float\s*=\s*([0-9.]+)", py_text, re.MULTILINE)
        lm = re.search(rf"Config\.{re.escape(lua_name)}\s*=\s*([0-9.]+)", lua_text)
        if not pm or not lm:
            errors.append(f"missing {py_name}/{lua_name}")
            continue
        pv, lv = float(pm.group(1)), float(lm.group(1))
        if abs(pv - lv) > 1e-6:
            errors.append(f"{py_name}: python={pv} lua={lv}")
    if errors:
        print("Config drift detected:")
        for e in errors:
            print(" ", e)
        return 1
    print("Config.lua ↔ config.py: OK (", len(PAIRS), "coefficients)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
