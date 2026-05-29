"""STARLINE Ω — Coherent Motion Engine.

The game engine is a symplectic perception–geometry kernel:

    Flow = ℱ(v, S, c, φ, R, κ)

    INPUT → MOTION → SMOOTHNESS → COHERENCE → PHASE → PERCEPTION

See docs/GAME_ENGINE.md for the complete idea.
"""

from .canonical import FlowField, compute_flow
from .config import EngineConfig
from .economy import EconomyState, integrate_resonance, try_unlock
from .engine import CoherentMotionEngine, ControlInput, PresentSnapshot, StepSnapshot
from .flow import FlowState, FlowStateMachine, classify_flow
from .hex_lattice import (
    loop_seal_manifest,
    schrodinger_from_flow,
)
from .packets import EnginePacket, TrackLattice, WIRE_SIZE, encode_packet
from .player import PlayerState
from .spline import SplineTrack

__version__ = "0.1.0"

__all__ = [
    # identity
    "compute_flow",
    "FlowField",
    "WIRE_SIZE",
    # kernel
    "EngineConfig",
    "CoherentMotionEngine",
    "ControlInput",
    "StepSnapshot",
    "PresentSnapshot",
    "PlayerState",
    "SplineTrack",
    # flow & economy
    "FlowState",
    "FlowStateMachine",
    "classify_flow",
    "EconomyState",
    "integrate_resonance",
    "try_unlock",
    # encoding
    "EnginePacket",
    "TrackLattice",
    "encode_packet",
    "loop_seal_manifest",
    "schrodinger_from_flow",
]
