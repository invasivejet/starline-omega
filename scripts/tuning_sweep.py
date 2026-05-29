#!/usr/bin/env python3
"""Compare smooth vs chaotic profiles — tuning bench for coherence pacing."""

from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "src"))

from starline import CoherentMotionEngine, EngineConfig, SplineTrack
from starline.engine import ControlInput
from starline.flow import FlowState
from starline.telemetry import Telemetry


@dataclass
class ProfileResult:
    profile: str
    steps: int
    coherence_mean: float
    coherence_p50: float
    coherence_p90: float
    coherence_final: float
    time_to_stable_s: float | None
    time_to_resonant_s: float | None
    time_to_flow_s: float | None
    flow_dwell_frac: float
    noise_mean: float
    instability_mean: float
    steering_entropy: float
    resonance_mean: float


def _run_profile(
    name: str,
    cfg: EngineConfig,
    steps: int,
    dt: float,
    control_fn,
) -> ProfileResult:
    track = SplineTrack.oval(radius=150.0, n=12)
    tel = Telemetry()
    eng = CoherentMotionEngine(track=track, config=cfg, telemetry=tel)
    eng.add_player(0, 0.0)

    coh_series: list[float] = []
    t_stable: float | None = None
    t_resonant: float | None = None
    t_flow: float | None = None
    noise_acc: list[float] = []
    inst_acc: list[float] = []
    res_acc: list[float] = []

    for i in range(steps):
        eng.set_control(0, control_fn(0, eng.time))
        snap = eng.step(dt)[0]
        t = i * dt
        coh_series.append(snap.coherence)
        noise_acc.append(snap.input_noise)
        inst_acc.append(snap.instability)
        res_acc.append(snap.resonance)

        fs = snap.flow_state
        if t_stable is None and fs in ("stable", "resonant", "flow"):
            t_stable = t
        if t_resonant is None and fs in ("resonant", "flow"):
            t_resonant = t
        if t_flow is None and fs == "flow":
            t_flow = t

    coh = sorted(coh_series)
    n = len(coh)
    summary = tel.summary()

    return ProfileResult(
        profile=name,
        steps=steps,
        coherence_mean=sum(coh_series) / n,
        coherence_p50=coh[n // 2],
        coherence_p90=coh[int(0.9 * (n - 1))],
        coherence_final=coh_series[-1],
        time_to_stable_s=t_stable,
        time_to_resonant_s=t_resonant,
        time_to_flow_s=t_flow,
        flow_dwell_frac=summary["flow_dwell_fraction"].get("flow", 0.0),
        noise_mean=sum(noise_acc) / n,
        instability_mean=sum(inst_acc) / n,
        steering_entropy=summary["steering_entropy"],
        resonance_mean=sum(res_acc) / n,
    )


def smooth_ctrl(_pid: int, t: float) -> ControlInput:
    return ControlInput(throttle=0.75, brake=0.0, steer=0.12 * math.sin(t * 0.5))


def chaotic_ctrl(_pid: int, t: float) -> ControlInput:
    steer = 1.0 if int(t * 28) % 2 == 0 else -1.0
    brake = 0.4 if int(t * 9) % 3 == 0 else 0.0
    return ControlInput(throttle=1.0, brake=brake, steer=steer)


def recommend(cfg_results: list[ProfileResult]) -> list[str]:
    smooth = next(r for r in cfg_results if r.profile == "smooth")
    chaos = next(r for r in cfg_results if r.profile == "chaotic")
    notes: list[str] = []
    if smooth.coherence_final > 0.95:
        notes.append("Coherence saturates too fast on smooth input — raise coherence_power or lower alpha.")
    if chaos.coherence_final >= smooth.coherence_final * 0.85:
        notes.append("Chaotic input keeps too much coherence — raise noise_penalty or beta.")
    if smooth.time_to_resonant_s is not None and smooth.time_to_resonant_s < 2.0:
        notes.append("Resonant arrives very quickly — consider lowering alpha slightly.")
    if chaos.noise_mean < smooth.noise_mean * 1.5:
        notes.append("Noise metric may not separate profiles — check noise weights.")
    if not notes:
        notes.append("Profiles separate well at current coefficients.")
    return notes


def main() -> int:
    cfg = EngineConfig()
    steps = 600
    dt = 1.0 / 60.0

    results = [
        _run_profile("smooth", cfg, steps, dt, smooth_ctrl),
        _run_profile("chaotic", cfg, steps, dt, chaotic_ctrl),
    ]
    notes = recommend(results)

    report = {
        "config": {
            "alpha": cfg.alpha,
            "beta": cfg.beta,
            "coherence_power": cfg.coherence_power,
            "noise_penalty": cfg.noise_penalty,
        },
        "profiles": [asdict(r) for r in results],
        "recommendations": notes,
        "status": "TUNING_SWEEP",
    }

    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "tuning_sweep.json"
    md_path = out_dir / "tuning_sweep.md"

    json_path.write_text(json.dumps(report, indent=2))

    lines = [
        "# STARLINE tuning sweep",
        "",
        f"- **smooth** final c = {results[0].coherence_final:.3f}, flow dwell = {results[0].flow_dwell_frac:.1%}",
        f"- **chaotic** final c = {results[1].coherence_final:.3f}, noise mean = {results[1].noise_mean:.3f}",
        "",
        "## Recommendations",
        "",
    ]
    for n in notes:
        lines.append(f"- {n}")
    md_path.write_text("\n".join(lines) + "\n")

    print(json.dumps(report, indent=2))
    print(f"\nWrote {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
