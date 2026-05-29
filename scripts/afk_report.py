#!/usr/bin/env python3
"""AFK vs active earning report — realistic ℛ/min comparison."""

from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "src"))

from starline import CoherentMotionEngine, EngineConfig, SplineTrack
from starline.afk import AfkSession, compute_autopilot_control
from starline.economy import EconomyState, integrate_resonance
from starline.engine import ControlInput
from starline.flow import FlowStateMachine


@dataclass
class EarnReport:
    mode: str
    seconds: float
    resonance_total: float
    resonance_per_min: float
    mean_coherence: float
    mean_smoothness: float
    flow_dwell_frac: float
    afk_session_earned: float = 0.0


def _afk_control(track: SplineTrack, p: object, cfg: EngineConfig) -> ControlInput:
    ds = cfg.anticipation_ds + cfg.anticipation_speed_scale * max(getattr(p, "v_eff", 0.0), 0.0)
    k_ahead = track.curvature(p.s + ds)
    return compute_autopilot_control(track.curvature(p.s), k_ahead, p.v, cfg)


def run_mode(mode: str, seconds: float, cfg: EngineConfig, *, warmup: float = 25.0) -> EarnReport:
    track = SplineTrack.oval(radius=150.0, n=12)
    eng = CoherentMotionEngine(track=track, config=cfg)
    eng.add_player(0)
    econ = EconomyState()
    afk = AfkSession(enabled=(mode == "afk"))
    fsm = FlowStateMachine()
    total = warmup + seconds
    steps = int(total / cfg.sim_dt)
    warmup_steps = int(warmup / cfg.sim_dt)
    coh, sm = [], []
    flow_ticks = 0
    measure_ticks = 0
    r_at_measure = 0.0

    for i in range(steps):
        t = i * cfg.sim_dt
        p = eng.players[0]
        if mode == "afk":
            eng.set_control(0, _afk_control(track, p, cfg))
        elif mode == "active":
            eng.set_control(
                0,
                ControlInput(throttle=0.72, brake=0.0, steer=0.08 * math.sin(t * 0.45)),
            )
        else:
            eng.set_control(0, ControlInput(throttle=0.0, brake=1.0, steer=0.0))

        snap = eng.step(cfg.sim_dt)[0]
        fs = fsm.update(snap.coherence, snap.sync_R, cfg)
        if i == warmup_steps:
            r_at_measure = econ.resonance
        integrate_resonance(
            econ,
            dt=cfg.sim_dt,
            coherence=snap.coherence,
            smoothness=snap.smoothness,
            resonance_field=snap.resonance,
            flow_state=fs.value,
            sync_R=snap.sync_R,
            velocity=snap.v,
            cfg=cfg,
            afk=afk,
        )
        if i >= warmup_steps:
            measure_ticks += 1
            if fs.value == "flow":
                flow_ticks += 1
            coh.append(snap.coherence)
            sm.append(snap.smoothness)

    earned = econ.resonance - r_at_measure
    return EarnReport(
        mode=mode,
        seconds=seconds,
        resonance_total=earned,
        resonance_per_min=earned / max(seconds / 60.0, 1e-6),
        mean_coherence=sum(coh) / len(coh),
        mean_smoothness=sum(sm) / len(sm),
        flow_dwell_frac=flow_ticks / max(measure_ticks, 1),
        afk_session_earned=afk.earned_session,
    )


def main() -> int:
    cfg = EngineConfig()
    duration = 90.0
    warmup = 25.0
    active = run_mode("active", duration, cfg, warmup=warmup)
    afk = run_mode("afk", duration, cfg, warmup=warmup)
    idle = run_mode("idle", duration, cfg, warmup=warmup)

    ratio = afk.resonance_per_min / max(active.resonance_per_min, 1e-6)
    report = {
        "duration_seconds": duration,
        "warmup_seconds": warmup,
        "config": {
            "afk_earn_multiplier": cfg.afk_earn_multiplier,
            "afk_session_cap": cfg.afk_session_cap,
            "afk_coherence_cap": cfg.afk_coherence_cap,
        },
        "modes": [asdict(active), asdict(afk), asdict(idle)],
        "analysis": {
            "afk_vs_active_rate_ratio": ratio,
            "idle_earn_negligible": idle.resonance_per_min < 1.0,
            "recommendation": (
                "AFK cruise is realistic: earns meaningful but sub-active ℛ."
                if 0.25 < ratio < 0.55
                else "Tune AfkEarnMultiplier — ratio outside 0.25–0.55 band."
            ),
        },
    }

    out_json = Path("output/afk_report.json")
    out_md = Path("output/afk_report.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2))

    md = [
        "# AFK Cruise — Final Report",
        "",
        f"Measure window: **{duration:.0f}s** after **{warmup:.0f}s** warmup per mode.",
        "",
        "## Earnings (Resonance ℛ = in-game cash)",
        "",
        f"| mode | ℛ total | ℛ/min | mean c | mean S | flow dwell |",
        f"|------|---------|-------|--------|--------|------------|",
    ]
    for r in (active, afk, idle):
        md.append(
            f"| {r.mode} | {r.resonance_total:.1f} | {r.resonance_per_min:.1f} | "
            f"{r.mean_coherence:.2f} | {r.mean_smoothness:.2f} | {r.flow_dwell_frac:.1%} |"
        )
    md.extend(
        [
            "",
            f"**AFK / active rate ratio:** {ratio:.2%}",
            "",
            f"**Verdict:** {report['analysis']['recommendation']}",
            "",
            "## Rules (realistic)",
            "",
            "- No separate cash — only ℛ (resonance ledger)",
            "- AFK uses server autopilot; earn ∝ actual Ψ·S quality",
            f"- Session AFK cap: {cfg.afk_session_cap} ℛ",
            "- No flow bonus while AFK",
            f"- Coherence soft-capped at {cfg.afk_coherence_cap} for earn quality",
            "",
            "## Steps to use in game",
            "",
            "1. `rojo serve` → Play",
            "2. Drive until c > 0.4",
            "3. Press **F** — AFK CRUISE on HUD",
            "4. ℛ accrues slower than active; cap stops infinite idle",
            "5. Press **F** again to resume manual driving for flow + full rate",
            "",
            "See `docs/AFK_MODE.md`.",
        ]
    )
    out_md.write_text("\n".join(md) + "\n")
    print(json.dumps(report, indent=2))
    print(f"\nWrote {out_json} and {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
