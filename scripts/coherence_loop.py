#!/usr/bin/env python3
"""
Closed experimental loop: PLAY → MEASURE → TUNE → REPLAY → COMPARE

Records c(t), S(t), ℛ(t), κ(t) for three driving profiles and reports:
  - ℛ/min
  - efficiency = ℛ / ∫c dt
  - AFK vs active ratio
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "src"))

from starline import CoherentMotionEngine, EngineConfig, SplineTrack
from starline.afk import AfkSession, compute_autopilot_control
from starline.economy import EconomyState, integrate_resonance, resonance_efficiency
from starline.engine import ControlInput


@dataclass
class LoopSample:
    t: float
    c: float
    S: float
    psi: float
    kappa: float
    resonance: float


@dataclass
class LoopReport:
    profile: str
    seconds: float
    resonance_total: float
    resonance_per_min: float
    coherence_integral: float
    efficiency: float
    mean_c: float
    mean_S: float
    samples: int


def _afk_ctrl(track: SplineTrack, p: object, cfg: EngineConfig) -> ControlInput:
    ds = cfg.anticipation_ds + cfg.anticipation_speed_scale * max(getattr(p, "v_eff", 0.0), 0.0)
    ka = track.curvature(p.s + ds)
    return compute_autopilot_control(track.curvature(p.s), ka, p.v, cfg)


def run_profile(profile: str, seconds: float, cfg: EngineConfig) -> tuple[LoopReport, list[LoopSample]]:
    track = SplineTrack.oval(radius=150.0, n=12)
    eng = CoherentMotionEngine(track=track, config=cfg)
    eng.add_player(0)
    econ = EconomyState()
    afk = AfkSession(enabled=(profile == "afk"))
    steps = int(seconds / cfg.sim_dt)
    series: list[LoopSample] = []
    coh, sm = [], []

    for i in range(steps):
        t = i * cfg.sim_dt
        p = eng.players[0]
        if profile == "afk":
            eng.set_control(0, _afk_ctrl(track, p, cfg))
        elif profile == "chaotic":
            eng.set_control(
                0,
                ControlInput(
                    throttle=0.5 + 0.4 * math.sin(t * 3.1),
                    brake=0.2 * (math.sin(t * 5.3) > 0.8 and 1 or 0),
                    steer=0.9 * math.sin(t * 2.7),
                ),
            )
        elif profile == "smooth":
            eng.set_control(
                0,
                ControlInput(throttle=0.72, brake=0.0, steer=0.06 * math.sin(t * 0.42)),
            )
        else:
            eng.set_control(
                0,
                ControlInput(throttle=0.65, brake=0.0, steer=0.15 * math.sin(t * 0.9)),
            )

        snap = eng.step(cfg.sim_dt)[0]
        k0 = track.curvature(snap.s)
        integrate_resonance(
            econ,
            dt=cfg.sim_dt,
            coherence=snap.coherence,
            smoothness=snap.smoothness,
            resonance_field=snap.resonance,
            flow_state=snap.flow_state,
            sync_R=snap.sync_R,
            velocity=snap.v,
            cfg=cfg,
            afk=afk,
        )
        coh.append(snap.coherence)
        sm.append(snap.smoothness)
        if i % 6 == 0:
            series.append(
                LoopSample(
                    t=t,
                    c=snap.coherence,
                    S=snap.smoothness,
                    psi=snap.resonance,
                    kappa=k0,
                    resonance=econ.resonance,
                )
            )

    report = LoopReport(
        profile=profile,
        seconds=seconds,
        resonance_total=econ.resonance,
        resonance_per_min=econ.resonance / max(seconds / 60.0, 1e-6),
        coherence_integral=econ.coherence_integral,
        efficiency=resonance_efficiency(econ),
        mean_c=sum(coh) / max(len(coh), 1),
        mean_S=sum(sm) / max(len(sm), 1),
        samples=len(series),
    )
    return report, series


def main() -> int:
    cfg = EngineConfig()
    duration = 60.0
    profiles = ("chaotic", "normal", "smooth", "afk")
    reports: list[LoopReport] = {}
    series_out: dict[str, list] = {}

    for name in profiles:
        rep, series = run_profile(name, duration, cfg)
        reports[name] = rep
        series_out[name] = [asdict(s) for s in series]

    active_rpm = reports["smooth"].resonance_per_min
    afk_rpm = reports["afk"].resonance_per_min
    ratio = afk_rpm / max(active_rpm, 1e-6)

    out = {
        "duration_seconds": duration,
        "energy_model": "dℛ = k·Ψ·S·c^γ·(1+λR₊)·dt",
        "config": {
            "k": cfg.resonance_earn_k,
            "gamma": cfg.resonance_coherence_gamma,
            "lambda": cfg.resonance_sync_lambda,
        },
        "profiles": {k: asdict(v) for k, v in reports.items()},
        "analysis": {
            "smooth_vs_chaotic_efficiency_ratio": reports["smooth"].efficiency
            / max(reports["chaotic"].efficiency, 1e-6),
            "afk_vs_smooth_rate_ratio": ratio,
            "coherence_closes_loop": reports["smooth"].efficiency
            > reports["chaotic"].efficiency,
        },
        "series": series_out,
    }

    out_json = Path("output/coherence_loop.json")
    out_md = Path("output/coherence_loop.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(out, indent=2))

    md = [
        "# Coherence loop — measurement report",
        "",
        f"Duration: **{duration:.0f}s** per profile.",
        "",
        f"Energy model: `{out['energy_model']}`",
        "",
        "| profile | ℛ | ℛ/min | ∫c·dt | efficiency | mean c | mean S |",
        "|---------|---|-------|-------|------------|--------|--------|",
    ]
    for name in profiles:
        r = reports[name]
        md.append(
            f"| {name} | {r.resonance_total:.2f} | {r.resonance_per_min:.2f} | "
            f"{r.coherence_integral:.1f} | {r.efficiency:.4f} | {r.mean_c:.2f} | {r.mean_S:.2f} |"
        )
    md.extend(
        [
            "",
            f"**Smooth / chaotic efficiency ratio:** {out['analysis']['smooth_vs_chaotic_efficiency_ratio']:.2f}",
            f"**AFK / smooth ℛ rate:** {ratio:.1%}",
            "",
            "Verdict: "
            + (
                "Coherence produces reward — loop closed."
                if out["analysis"]["coherence_closes_loop"]
                else "Tune α, γ, or noise — chaotic earns too much."
            ),
            "",
            "Replay series in `output/coherence_loop.json` → `series`.",
        ]
    )
    out_md.write_text("\n".join(md) + "\n")
    print(json.dumps({k: asdict(v) for k, v in reports.items()}, indent=2))
    print(f"\nWrote {out_json} and {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
