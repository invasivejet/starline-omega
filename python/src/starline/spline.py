"""Spline track: centerline C(s), curvature κ(s), arc-length parameterization."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SplineSample:
    """Point on track at arc-length s."""

    s: float
    position: np.ndarray  # shape (3,)
    tangent: np.ndarray   # unit tangent
    curvature: float      # κ(s)


class SplineTrack:
    """Closed Catmull-Rom spline through 3D waypoints with precomputed arc-length table."""

    def __init__(self, waypoints: np.ndarray, samples_per_segment: int = 32):
        wp = np.asarray(waypoints, dtype=np.float64)
        if wp.ndim != 2 or wp.shape[1] != 3 or wp.shape[0] < 4:
            raise ValueError("waypoints must be shape (N, 3) with N >= 4")
        self._wp = wp
        self._n_seg = wp.shape[0]
        self._spc = int(samples_per_segment)
        self._build_tables()

    @classmethod
    def oval(cls, radius: float = 200.0, height: float = 0.0, n: int = 12) -> "SplineTrack":
        t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
        pts = np.column_stack(
            [radius * np.cos(t), np.full(n, height), radius * np.sin(t)]
        )
        return cls(pts)

    def _catmull(self, p0, p1, p2, p3, u: float) -> np.ndarray:
        u2 = u * u
        u3 = u2 * u
        return 0.5 * (
            (2.0 * p1)
            + (-p0 + p2) * u
            + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * u2
            + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * u3
        )

    def _build_tables(self) -> None:
        dense: list[np.ndarray] = []
        for i in range(self._n_seg):
            p0 = self._wp[(i - 1) % self._n_seg]
            p1 = self._wp[i]
            p2 = self._wp[(i + 1) % self._n_seg]
            p3 = self._wp[(i + 2) % self._n_seg]
            for k in range(self._spc):
                u = k / self._spc
                dense.append(self._catmull(p0, p1, p2, p3, u))
        pts = np.array(dense, dtype=np.float64)
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        s_tab = np.concatenate([[0.0], np.cumsum(seg)])
        self._pts = pts
        self._s_tab = s_tab
        self.length = float(s_tab[-1])

    def _interp_index(self, s: float) -> tuple[int, float]:
        s = float(s) % self.length
        idx = int(np.searchsorted(self._s_tab, s, side="right") - 1)
        idx = max(0, min(idx, len(self._s_tab) - 2))
        s0 = self._s_tab[idx]
        s1 = self._s_tab[idx + 1]
        t = 0.0 if s1 <= s0 else (s - s0) / (s1 - s0)
        return idx, t

    def position(self, s: float) -> np.ndarray:
        idx, t = self._interp_index(s)
        return (1.0 - t) * self._pts[idx] + t * self._pts[idx + 1]

    def tangent(self, s: float, eps: float = 0.5) -> np.ndarray:
        p_fwd = self.position(s + eps)
        p_bwd = self.position(s - eps)
        tan = p_fwd - p_bwd
        n = np.linalg.norm(tan)
        if n < 1e-12:
            return np.array([1.0, 0.0, 0.0])
        return tan / n

    def curvature(self, s: float, eps: float = 1.0) -> float:
        """κ ≈ |dT/ds| from finite differences on unit tangent."""
        t0 = self.tangent(s - eps)
        t1 = self.tangent(s + eps)
        dt = t1 - t0
        kappa = np.linalg.norm(dt) / max(2.0 * eps, 1e-9)
        return float(kappa)

    def sample(self, s: float) -> SplineSample:
        return SplineSample(
            s=float(s) % self.length,
            position=self.position(s),
            tangent=self.tangent(s),
            curvature=self.curvature(s),
        )
