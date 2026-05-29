#!/usr/bin/env python3
"""Export TrackLattice JSON for a spline (oval or waypoint file)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "src"))

import numpy as np

from starline import SplineTrack
from starline.packets import TopologyCode
from starline.topology import analyze_track_topology


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Export track lattice JSON")
    p.add_argument("--oval", action="store_true", help="Default oval track")
    p.add_argument("--radius", type=float, default=150.0)
    p.add_argument("--nodes", type=int, default=128)
    p.add_argument("--name", default="oval")
    p.add_argument("-o", "--output", default="output/track_lattice.json")
    args = p.parse_args()

    if args.oval:
        track = SplineTrack.oval(radius=args.radius, n=12)
    else:
        track = SplineTrack.oval(radius=args.radius, n=12)

    n = args.nodes
    L = track.length
    s_norm = np.linspace(0, 1, n, endpoint=False)
    kappa = np.array([track.curvature(float(s * L)) for s in s_norm])

    segs = analyze_track_topology(track, n=n)
    topo = np.full(n, int(TopologyCode.UNKNOWN), dtype=np.int32)
    for seg in segs:
        for i, sn in enumerate(s_norm):
            if seg.s_norm_start <= sn <= seg.s_norm_end:
                topo[i] = int(TopologyCode[seg.topology.name])

    payload = {
        "name": args.name,
        "length": L,
        "nodes": n,
        "s_norm": s_norm.tolist(),
        "kappa": kappa.tolist(),
        "topology_code": topo.tolist(),
        "segments": [
            {
                "topology": seg.topology.value,
                "s_start": seg.s_start,
                "s_end": seg.s_end,
                "s_norm_start": seg.s_norm_start,
                "s_norm_end": seg.s_norm_end,
            }
            for seg in segs
        ],
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {out} ({n} nodes, length={L:.1f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
