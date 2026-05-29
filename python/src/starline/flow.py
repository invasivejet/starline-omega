"""Flow-state classification with hysteresis (perceptual stability)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .config import EngineConfig


class FlowState(str, Enum):
    UNSTABLE = "unstable"
    STABLE = "stable"
    RESONANT = "resonant"
    FLOW = "flow"


@dataclass(frozen=True)
class FlowThresholds:
    """Legacy instant thresholds (tests / telemetry without state)."""

    stable_c: float = 0.4
    resonant_c: float = 0.7
    flow_c: float = 0.9
    flow_R: float = 0.8

    @classmethod
    def from_config(cls, cfg: EngineConfig) -> "FlowThresholds":
        return cls(
            stable_c=cfg.flow_stable_c,
            resonant_c=cfg.flow_resonant_c,
            flow_c=cfg.flow_enter_flow_c,
            flow_R=cfg.flow_enter_flow_R,
        )


def classify_flow(c: float, R: float, th: FlowThresholds | None = None) -> FlowState:
    """Instant classification (no memory). Prefer FlowStateMachine in runtime."""
    th = th or FlowThresholds()
    if c > th.flow_c and R > th.flow_R:
        return FlowState.FLOW
    if c > th.resonant_c:
        return FlowState.RESONANT
    if c > th.stable_c:
        return FlowState.STABLE
    return FlowState.UNSTABLE


@dataclass
class FlowStateMachine:
    """Hysteresis — prevents musical/VFX flicker."""

    state: FlowState = FlowState.UNSTABLE

    def update(self, c: float, R: float, cfg: EngineConfig) -> FlowState:
        s = self.state
        if s == FlowState.FLOW:
            if c < cfg.flow_exit_flow_c or R < cfg.flow_exit_flow_R:
                s = FlowState.RESONANT if c >= cfg.flow_exit_resonant_c else FlowState.STABLE
        elif s == FlowState.RESONANT:
            if c > cfg.flow_enter_flow_c and R > cfg.flow_enter_flow_R:
                s = FlowState.FLOW
            elif c < cfg.flow_exit_resonant_c:
                s = FlowState.STABLE if c >= cfg.flow_exit_stable_c else FlowState.UNSTABLE
        elif s == FlowState.STABLE:
            if c > cfg.flow_enter_flow_c and R > cfg.flow_enter_flow_R:
                s = FlowState.FLOW
            elif c > cfg.flow_enter_resonant_c:
                s = FlowState.RESONANT
            elif c < cfg.flow_exit_stable_c:
                s = FlowState.UNSTABLE
        else:  # UNSTABLE
            if c > cfg.flow_enter_flow_c and R > cfg.flow_enter_flow_R:
                s = FlowState.FLOW
            elif c > cfg.flow_enter_resonant_c:
                s = FlowState.RESONANT
            elif c > cfg.flow_enter_stable_c:
                s = FlowState.STABLE
        self.state = s
        return s
