#!/usr/bin/env python3
"""Seal the STARLINE Ω closed loop — emit schrodinger_manifest.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "src"))

from starline import CoherentMotionEngine, EngineConfig, SplineTrack, encode_packet
from starline.economy import EconomyState, integrate_resonance, resonance_efficiency
from starline.engine import ControlInput
from starline.hex_lattice import (
    lattice_frame_from_wire,
    loop_seal_manifest,
    schrodinger_from_flow,
)
from starline.wire_pack import PACKED_SIZE, pack_from_wire


def main() -> int:
    cfg = EngineConfig()
    track = SplineTrack.oval(radius=150.0, n=12)
    eng = CoherentMotionEngine(track=track, config=cfg)
    eng.add_player(0)
    eng.add_player(1, track.length * 0.5)

    for i in range(int(3.0 / cfg.sim_dt)):
        t = i * cfg.sim_dt
        for pid in eng.players:
            eng.set_control(
                pid,
                ControlInput(throttle=0.7, steer=0.12 * __import__("math").sin(t + pid)),
            )
        snaps = eng.step(cfg.sim_dt)

    s = snaps[0]
    p = eng.players[0]
    econ = EconomyState()
    integrate_resonance(
        econ,
        dt=cfg.sim_dt,
        coherence=s.coherence,
        smoothness=s.smoothness,
        resonance_field=s.resonance,
        flow_state=s.flow_state,
        sync_R=s.sync_R,
        velocity=s.v,
        cfg=cfg,
    )
    pkt = encode_packet(
        p,
        track.length,
        track.curvature(p.s),
        track.curvature(p.s + 8),
        s.sync_R,
        s.resonance,
        s.input_noise,
        flow_state=s.flow_state,
    )
    wire = pkt.to_wire()
    packed = pack_from_wire(wire)
    hex_frame = lattice_frame_from_wire(wire, resonance_credit=econ.resonance, kappa=track.curvature(p.s))
    psi = schrodinger_from_flow(s.flow_state, s.coherence, s.instability)

    manifest = loop_seal_manifest()
    manifest["live_tick"] = {
        "hex_lattice": hex_frame,
        "schrodinger": psi.as_dict(),
        "collapse_branch": psi.collapse_mode(),
        "wire_floats": len(wire),
        "wire_pack_bytes": PACKED_SIZE,
        "sync_R": s.sync_R,
        "efficiency": resonance_efficiency(econ),
        "flow_state": s.flow_state,
    }
    manifest["repository"] = {
        "python_kernel": "python/src/starline",
        "roblox_runtime": "roblox/Starline",
        "entry_server": "roblox/ServerScriptService/StarlineServer.server.lua",
        "tests": "python/tests",
        "local_run": "./scripts/local_run.sh",
    }

    out = Path("output/schrodinger_manifest.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2))

    banner = r"""
┌────────────────────────────────────────────────────────────┐
│ STARLINE Ω :: SCHRÖDINGERIZED LATTICE :: IONQ CLOSED LOOP │
└────────────────────────────────────────────────────────────┘
            [ Ω LOOP SEALED ]
"""
    print(banner)
    print(json.dumps(manifest["live_tick"], indent=2))
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
