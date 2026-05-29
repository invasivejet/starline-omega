#!/usr/bin/env python3
"""Local headless runtime — full engine loop without Roblox.

Mirrors production: fixed sim tick, replicate cadence, wire packets, economy ℛ.
Use for tuning, CI smoke, and offline field research.

  python scripts/headless_play.py --profile smooth --seconds 30
  python scripts/headless_play.py --profile chaotic --wire-log output/session.jsonl
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "src"))

from starline import CoherentMotionEngine, EngineConfig, SplineTrack
from starline.economy import EconomyState, integrate_resonance, try_unlock
from starline.engine import ControlInput
from starline.flow import FlowStateMachine
from starline.packets import encode_packet
from starline.telemetry import Telemetry
def profile_control(name: str):
    if name == "chaotic":

        def ctrl(_pid: int, t: float) -> ControlInput:
            steer = 1.0 if int(t * 28) % 2 == 0 else -1.0
            brake = 0.4 if int(t * 9) % 3 == 0 else 0.0
            return ControlInput(throttle=1.0, brake=brake, steer=steer)

        return ctrl

    def smooth(_pid: int, t: float) -> ControlInput:
        return ControlInput(throttle=0.75, brake=0.0, steer=0.12 * math.sin(t * 0.5))

    return smooth


def main() -> int:
    ap = argparse.ArgumentParser(description="STARLINE local headless play")
    ap.add_argument("--profile", choices=("smooth", "chaotic"), default="smooth")
    ap.add_argument("--seconds", type=float, default=20.0)
    ap.add_argument("--wire-log", type=str, default="")
    ap.add_argument("--hud-hz", type=float, default=4.0)
    args = ap.parse_args()

    cfg = EngineConfig()
    track = SplineTrack.oval(radius=150.0, n=12)
    eng = CoherentMotionEngine(track=track, config=cfg, telemetry=Telemetry())
    eng.add_player(0, 0.0)

    econ = EconomyState()
    fsm = FlowStateMachine()
    ctrl_fn = profile_control(args.profile)

    replicate_interval = 1.0 / 20.0
    rep_accum = 0.0
    hud_accum = 0.0
    hud_interval = 1.0 / max(args.hud_hz, 0.1)

    wire_fp = None
    if args.wire_log:
        Path(args.wire_log).parent.mkdir(parents=True, exist_ok=True)
        wire_fp = open(args.wire_log, "w", encoding="utf-8")

    max_steps = int(args.seconds / cfg.sim_dt)
    frame = 0
    snaps = []
    fs = fsm.update(0.0, 0.0, cfg)
    print(
        f"[starline] local headless | profile={args.profile} | "
        f"sim={1/cfg.sim_dt:.0f}Hz | steps={max_steps} (~{args.seconds}s)"
    )
    print("-" * 60)

    while frame < max_steps:
        steps = 1
        for _ in range(steps):
            eng.set_control(0, ctrl_fn(0, eng.time))
            snaps = eng.step(cfg.sim_dt)
            if not snaps:
                continue
            s = snaps[0]
            fs = fsm.update(s.coherence, s.sync_R, cfg)
            integrate_resonance(
                econ,
                dt=cfg.sim_dt,
                coherence=s.coherence,
                smoothness=s.smoothness,
                resonance_field=s.resonance,
                flow_state=fs.value,
                sync_R=s.sync_R,
                cfg=cfg,
            )

        rep_accum += cfg.sim_dt
        hud_accum += cfg.sim_dt
        frame += 1

        if rep_accum >= replicate_interval and snaps:
            rep_accum = 0.0
            s = snaps[0]
            p = eng.players[0]
            pkt = encode_packet(
                p,
                track.length,
                track.curvature(p.s),
                track.curvature(p.s + 8),
                s.sync_R,
                s.resonance,
                s.input_noise,
                flow_state=fs.value,
            )
            if wire_fp:
                wire_fp.write(
                    json.dumps(
                        {"t": round(eng.time, 4), "wire": pkt.to_wire(), "flow": fs.value}
                    )
                    + "\n"
                )

        if hud_accum >= hud_interval and snaps:
            hud_accum = 0.0
            s = snaps[0]
            print(
                f"t={eng.time:5.1f}s  c={s.coherence:.3f}  S={s.smoothness:.3f}  "
                f"Ψ={s.resonance:.3f}  ℛ={econ.resonance:6.1f}  flow={fs.value:10s}  v_eff={s.v_eff:5.1f}"
            )

    if try_unlock(econ, "circuit", 40.0):
        print("[economy] circuit unlocked (ℛ spent)")
    else:
        print(f"[economy] circuit locked — need 40 ℛ, have {econ.resonance:.1f}")

    summary = eng.telemetry.summary() if eng.telemetry else {}
    report = {
        "profile": args.profile,
        "seconds_sim": frame * cfg.sim_dt,
        "steps": frame,
        "economy": econ.to_dict(),
        "telemetry": summary,
    }
    out = Path("output/headless_session.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print("-" * 60)
    print(f"Wrote {out}")
    if wire_fp:
        wire_fp.close()
        print(f"Wire log: {args.wire_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
