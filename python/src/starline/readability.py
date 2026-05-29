"""Readability principle: C_visual < C_readability."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadabilityBudget:
    """Maximum perceptual complexity before flow cognition breaks."""

    max_visual_complexity: float = 0.65
    max_ui_elements: int = 6
    max_particle_layers: int = 2
    max_trail_segments: int = 32


def visual_complexity(
    *,
    trail_segments: int = 0,
    particle_layers: int = 0,
    ui_elements: int = 0,
    vfx_intensity: float = 0.0,
    budget: ReadabilityBudget | None = None,
) -> float:
    """C_visual — normalized complexity score ∈ [0, 1+]."""
    b = budget or ReadabilityBudget()
    trail = min(1.0, trail_segments / max(b.max_trail_segments, 1))
    particles = min(1.0, particle_layers / max(b.max_particle_layers, 1))
    ui = min(1.0, ui_elements / max(b.max_ui_elements, 1))
    return 0.35 * trail + 0.25 * particles + 0.2 * ui + 0.2 * max(0.0, min(1.0, vfx_intensity))


def is_readable(C_visual: float, budget: ReadabilityBudget | None = None) -> bool:
    b = budget or ReadabilityBudget()
    return C_visual < b.max_visual_complexity
