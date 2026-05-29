#!/usr/bin/env python3
"""Headless demo of the Coherent Motion Engine."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "src"))

from starline import CoherentMotionEngine, SplineTrack
from starline.engine import ControlInput


def main() -> int:
    track = SplineTrack.oval(radius=150.0, n=12)
    eng = CoherentMotionEngine(track=track)
    eng.add_player(0, s0=0.0)
    eng.add_player(1, s0=track.length * 0.5)

    def ctrl(pid: int, t: float) -> ControlInput:
        import math

        steer = 0.15 * math.sin(t * 0.5 + pid)
        return ControlInput(throttle=0.75, brake=0.0, steer=steer)

    print(f"track length = {track.length:.1f}")
    for i in range(300):
        for pid in eng.players:
            eng.set_control(pid, ctrl(pid, eng.time))
        snaps = eng.step(1 / 60)
        if i % 60 == 59:
            for s in snaps:
                print(
                    f"  P{s.player_id} v={s.v:.1f} v_eff={s.v_eff:.1f} "
                    f"C={s.coherence:.3f} S={s.smoothness:.3f} R={s.sync_R:.3f} "
                    f"tempo={s.audio.tempo:.1f}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
