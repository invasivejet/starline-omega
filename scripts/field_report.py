#!/usr/bin/env python3
"""
Phase II — emergence field report.

Measures:
  A. spatial coherence mean(c | s_norm bin)
  B. multiplayer sync R(t) stability
  C. exploit surfaces + noise–coherence invariant
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
from starline.telemetry import Telemetry
from starline.track_score import TrackScore


@dataclass
class ProfileResult:
    name: str
    resonance: float
    efficiency: float
    telemetry: dict


def _afk_ctrl(track: SplineTrack, p: object, cfg: EngineConfig) -> ControlInput:
    ds = cfg.anticipation_ds + cfg.anticipation_speed_scale * max(getattr(p, "v_eff", 0.0), 0.0)
    ka = track.curvature(p.s + ds)
    return compute_autopilot_control(track.curvature(p.s), ka, p.v, cfg)


def run_profile(
    name: str,
    seconds: float,
    cfg: EngineConfig,
    *,
    players: int = 1,
    control_fn=None,
) -> ProfileResult:
    track = SplineTrack.oval(radius=150.0, n=12)
    score = TrackScore.from_track_analysis(track, name="oval")
    tel = Telemetry(segment_bins=16)
    eng = CoherentMotionEngine(track=track, config=cfg, track_score=score, telemetry=tel)
    econ = EconomyState()
    afk = AfkSession(enabled=(name == "afk"))
    steps = int(seconds / cfg.sim_dt)

    for pid in range(players):
        eng.add_player(pid, track.length * pid / max(players, 1))

    for i in range(steps):
        t = i * cfg.sim_dt
        for pid in eng.players:
            if control_fn:
                ctrl = control_fn(pid, t, eng, track, cfg, afk)
            elif name == "oscillatory_spam":
                ctrl = ControlInput(
                    throttle=0.6,
                    brake=0.0,
                    steer=0.95 * math.sin(t * 8.0 + pid),
                )
            elif name == "brake_pulse":
                ctrl = ControlInput(
                    throttle=0.5,
                    brake=1.0 if math.sin(t * 6.0) > 0.7 else 0.0,
                    steer=0.1,
                )
            elif name == "afk":
                p = eng.players[pid]
                ctrl = _afk_ctrl(track, p, cfg)
            elif name == "smooth":
                ctrl = ControlInput(throttle=0.72, brake=0.0, steer=0.06 * math.sin(t * 0.4 + pid))
            else:
                ctrl = ControlInput(throttle=0.65, brake=0.0, steer=0.2 * math.sin(t * 1.1))
            eng.set_control(pid, ctrl)

        snaps = eng.step(cfg.sim_dt)
        for s in snaps:
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
                afk=afk if s.player_id == 0 else None,
            )

    return ProfileResult(
        name=name,
        resonance=econ.resonance,
        efficiency=resonance_efficiency(econ),
        telemetry=tel.summary(),
    )


def main() -> int:
    cfg = EngineConfig()
    duration = 45.0

    profiles = [
        run_profile("smooth", duration, cfg),
        run_profile("oscillatory_spam", duration, cfg),
        run_profile("brake_pulse", duration, cfg),
        run_profile("afk", duration, cfg),
        run_profile("duo_sync", duration, cfg, players=2),
    ]

    smooth = profiles[0]
    spam = profiles[1]
    invariant_ok = spam.telemetry.get("noise_coherence_corr", 0) <= 0.05 or spam.resonance < smooth.resonance * 0.5

    report = {
        "duration_seconds": duration,
        "profiles": [asdict(p) for p in profiles],
        "analysis": {
            "spatial_legibility": smooth.telemetry.get("spatial_profile", {}),
            "duo_sync": profiles[4].telemetry.get("sync_stability", {}),
            "exploit_spam_resonance_ratio": spam.resonance / max(smooth.resonance, 1e-6),
            "noise_invariant_holds": invariant_ok,
            "verdict": (
                "Field shows spatial coherence structure; exploits suppressed."
                if invariant_ok
                else "Review noise penalty — spam may be productive."
            ),
        },
    }

    out_json = Path("output/field_report.json")
    out_md = Path("output/field_report.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2))

    md = [
        "# Field emergence report (Phase II)",
        "",
        f"Duration: **{duration:.0f}s** per profile.",
        "",
        "## A. Spatial coherence `mean(c | s_norm bin)` — smooth profile",
        "",
        "| bin | mean c |",
        "|-----|--------|",
    ]
    for k, v in sorted(report["analysis"]["spatial_legibility"].items()):
        md.append(f"| {k} | {v:.3f} |")

    md.extend(
        [
            "",
            "## B. Multiplayer sync (2 players)",
            "",
            f"```json\n{json.dumps(report['analysis']['duo_sync'], indent=2)}\n```",
            "",
            "## C. Exploit surfaces",
            "",
            "| profile | ℛ | efficiency | noise↔c corr |",
            "|---------|---|------------|--------------|",
        ]
    )
    for p in profiles:
        md.append(
            f"| {p.name} | {p.resonance:.2f} | {p.efficiency:.4f} | "
            f"{p.telemetry.get('noise_coherence_corr', 0):.3f} |"
        )
    md.extend(
        [
            "",
            f"**Spam / smooth ℛ ratio:** {report['analysis']['exploit_spam_resonance_ratio']:.2%}",
            "",
            f"**Verdict:** {report['analysis']['verdict']}",
            "",
            "Contract: [RUNTIME_CONTRACT.md](../docs/RUNTIME_CONTRACT.md)",
        ]
    )
    out_md.write_text("\n".join(md) + "\n")
    print(json.dumps(report["analysis"], indent=2))
    print(f"\nWrote {out_json} and {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
