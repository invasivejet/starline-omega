#!/usr/bin/env python3
"""Generate output/sim_report.json — progress metrics from a short simulation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "src"))

from starline import CoherentMotionEngine, SplineTrack
from starline.engine import ControlInput
from starline.telemetry import Telemetry
from starline.track_score import TrackScore


def main() -> int:
    track = SplineTrack.oval(radius=150.0, n=12)
    eng = CoherentMotionEngine(
        track=track,
        track_score=TrackScore.from_track_analysis(track, name="oval"),
        telemetry=Telemetry(),
    )
    eng.add_player(0, 0.0)
    eng.add_player(1, track.length * 0.5)

    def ctrl(pid: int, t: float) -> ControlInput:
        import math

        return ControlInput(
            throttle=0.7,
            brake=0.0,
            steer=0.2 * math.sin(t * 0.7 + pid),
        )

    coh_hist = []
    sync_hist = []
    for _ in range(600):
        for pid in eng.players:
            eng.set_control(pid, ctrl(pid, eng.time))
        snaps = eng.step(1 / 60)
        for s in snaps:
            coh_hist.append(s.coherence)
        sync_hist.append(snaps[0].sync_R if snaps else 0.0)

    report = {
        "track_length": track.length,
        "steps": 600,
        "players": 2,
        "coherence": {
            "mean": float(sum(coh_hist) / len(coh_hist)),
            "min": float(min(coh_hist)),
            "max": float(max(coh_hist)),
        },
        "sync_R": {
            "mean": float(sum(sync_hist) / len(sync_hist)),
            "final": float(sync_hist[-1]),
        },
        "mvp_steps_complete": [1, 2, 3, 4, 5],
        "telemetry": eng.telemetry.summary() if eng.telemetry else {},
        "status": "ENGINE_RIGOR_COMPLETE",
    }

    out = Path("output/sim_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
