#!/usr/bin/env python3
"""Print STARLINE Ω engine identity — the final kernel contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "src"))

from starline import (
    WIRE_SIZE,
    CoherentMotionEngine,
    EngineConfig,
    SplineTrack,
    compute_flow,
    encode_packet,
)
from starline.hex_lattice import lattice_frame_from_wire, loop_seal_manifest, schrodinger_from_flow
from starline.wire_pack import PACKED_SIZE, pack_from_wire
from starline.engine import ControlInput


def main() -> int:
    cfg = EngineConfig()
    track = SplineTrack.oval(radius=120.0, n=10)
    eng = CoherentMotionEngine(track=track, config=cfg)
    eng.add_player(0)
    eng.set_control(0, ControlInput(throttle=0.6))

    for _ in range(120):
        snaps = eng.step(cfg.sim_dt)
    s = snaps[0]
    p = eng.players[0]
    ff = compute_flow(p.v, s.smoothness, s.coherence, p.phase, s.sync_R, track.curvature(p.s))
    pkt = encode_packet(
        p, track.length, track.curvature(p.s), track.curvature(p.s + 5),
        s.sync_R, s.resonance, s.input_noise, flow_state=s.flow_state,
    )

    wire = pkt.to_wire()
    seal = loop_seal_manifest()
    psi = schrodinger_from_flow(s.flow_state, s.coherence, s.instability)

    manifest = {
        "name": "STARLINE Ω",
        "subtitle": "SCHRODINGERIZED LATTICE :: IONQ CLOSED LOOP",
        "kind": "coherent_motion_engine",
        "sealed": True,
        "lightweight": {
            "sacred_variables": ["v", "S", "c", "phi", "R"],
            "wire_floats": WIRE_SIZE,
            "wire_pack_bytes": PACKED_SIZE,
            "frozen_loop": "Motion→Smoothness→Coherence→Phase→Perception",
            "python_deps": ["numpy"],
        },
        "identity": {
            "flow_equation": "Flow = F(v, S, c, phi, R, kappa)",
            "audio_law": "A(t) = f(v, S, c, R, kappa)",
            "economy": "dR = k*Psi*S*c^gamma*(1+lambda*R+)*dt",
            "axiom": seal["axiom"],
        },
        "schrodinger_lattice": seal,
        "hex_frame": lattice_frame_from_wire(wire, resonance_credit=s.resonance),
        "schrodinger_state": psi.as_dict(),
        "sample_tick": {
            "flow": ff.as_dict(),
            "wire": pkt.to_wire(),
            "flow_state": s.flow_state,
            "coherence": s.coherence,
        },
        "docs": {
            "north_star": "docs/GAME_ENGINE.md",
            "invariants": "docs/INVARIANTS.md",
            "local_run": "docs/LOCAL_RUN.md",
        },
    }

    print(json.dumps(manifest, indent=2))
    out = Path("output/engine_manifest.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2))
    print(f"\nWrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
