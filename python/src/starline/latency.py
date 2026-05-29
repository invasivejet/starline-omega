"""Perceptual latency budgets (ms)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LatencyBudget:
    input_to_motion_ms: float = 50.0
    motion_to_audio_ms: float = 30.0
    camera_lag_ms: float = 80.0

    def check(self, *, input_ms: float, audio_ms: float, camera_ms: float) -> dict[str, bool]:
        return {
            "input_to_motion": input_ms <= self.input_to_motion_ms,
            "motion_to_audio": audio_ms <= self.motion_to_audio_ms,
            "camera_lag": camera_ms <= self.camera_lag_ms,
        }


DEFAULT_LATENCY = LatencyBudget()
