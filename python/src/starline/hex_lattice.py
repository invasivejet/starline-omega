"""Schrödingerized hex lattice — opcode map for the closed Ω loop.

See docs/SCHRODINGER_LATTICE.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Sacred field opcodes (ASCII-mnemonic hex)
OP_V = 0x76  # 'v'
OP_S = 0x53  # 'S'
OP_C = 0x63  # 'c'
OP_PHI = 0xCF  # φ
OP_R = 0x52  # 'R'
OP_PSI = 0xA8  # Ψ
OP_KAPPA = 0xD0  # κ
OP_RESONANCE_CREDIT = 0x211B  # ℛ

OPCODE_TO_FIELD: dict[int, str] = {
    OP_V: "v",
    OP_S: "S",
    OP_C: "c",
    OP_PHI: "phi",
    OP_R: "R",
    OP_PSI: "psi",
    OP_KAPPA: "kappa",
    OP_RESONANCE_CREDIT: "resonance",
}

FIELD_TO_OPCODE: dict[str, int] = {v: k for k, v in OPCODE_TO_FIELD.items()}

# Perceptual mode ladder (engine phase identity)
MODE_NOISE = 0x00
MODE_RHYTHM = 0x01
MODE_ANTICIPATION = 0x02
MODE_SYNC = 0x03
MODE_EMERGENCE = 0x04
MODE_FLOW = 0x05

MODE_NAMES: dict[int, str] = {
    MODE_NOISE: "noise",
    MODE_RHYTHM: "rhythm",
    MODE_ANTICIPATION: "anticipation",
    MODE_SYNC: "synchronization",
    MODE_EMERGENCE: "emergence",
    MODE_FLOW: "flow",
}

FLOW_TO_MODE: dict[str, int] = {
    "unstable": MODE_NOISE,
    "stable": MODE_RHYTHM,
    "resonant": MODE_ANTICIPATION,
    "flow": MODE_FLOW,
}

# IonQ-style superposition weights over flow branches
SCHRODINGER_BRANCHES = ("stable", "resonant", "flow", "fracture")


@dataclass(frozen=True)
class SchrodingerState:
    """|Ψ_STARLINE⟩ = α|stable⟩ + β|resonant⟩ + γ|flow⟩ + δ|fracture⟩"""

    alpha: float  # stable
    beta: float  # resonant
    gamma: float  # flow
    delta: float  # fracture

    def normalized(self) -> SchrodingerState:
        n = (self.alpha**2 + self.beta**2 + self.gamma**2 + self.delta**2) ** 0.5
        if n < 1e-12:
            return SchrodingerState(1.0, 0.0, 0.0, 0.0)
        return SchrodingerState(
            self.alpha / n, self.beta / n, self.gamma / n, self.delta / n
        )

    def as_dict(self) -> dict[str, float]:
        return {"alpha": self.alpha, "beta": self.beta, "gamma": self.gamma, "delta": self.delta}

    def collapse_mode(self) -> str:
        """measure(player_intention) → dominant branch."""
        s = self.normalized()
        weights = {
            "stable": s.alpha**2,
            "resonant": s.beta**2,
            "flow": s.gamma**2,
            "fracture": s.delta**2,
        }
        return max(weights, key=weights.get)  # type: ignore[arg-type]


def schrodinger_from_flow(flow_state: str, coherence: float, instability: float) -> SchrodingerState:
    """Map hysteresis flow + local disorder into superposition amplitudes."""
    c = max(0.0, min(1.0, coherence))
    inst = max(0.0, min(1.0, instability))
    fracture = inst * (1.0 - c)
    if flow_state == "flow":
        return SchrodingerState(0.1, 0.15, 0.7, fracture).normalized()
    if flow_state == "resonant":
        return SchrodingerState(0.15, 0.65, 0.1, fracture).normalized()
    if flow_state == "stable":
        return SchrodingerState(0.7, 0.15, 0.05, fracture).normalized()
    return SchrodingerState(0.2, 0.1, 0.05, 0.65 + fracture * 0.2).normalized()


def encode_lattice_hex(state: dict[str, float]) -> dict[str, float]:
    """Encode sacred scalars as 0xOP → value map."""
    out: dict[str, float] = {}
    for field, opcode in FIELD_TO_OPCODE.items():
        if field in state:
            out[f"0x{opcode:02X}" if opcode < 0x100 else f"0x{opcode:04X}"] = float(state[field])
    return out


def lattice_frame_from_wire(
    wire: list[float],
    *,
    resonance_credit: float = 0.0,
    kappa: float | None = None,
) -> dict[str, float]:
    """Build hex lattice from wire[20] (1-based Lua layout in docs)."""
    w = list(wire)
    while len(w) < 20:
        w.append(0.0)
    k = kappa if kappa is not None else float(w[1])
    return encode_lattice_hex(
        {
            "v": float(w[6]),
            "S": float(w[3]),
            "c": float(w[10]),
            "phi": float(w[13]),
            "R": float(w[15]),
            "psi": float(w[12]),
            "kappa": k,
            "resonance": resonance_credit,
        }
    )


def asymptotic_identity_chain() -> list[str]:
    return [
        "INPUT",
        "MOTION",
        "SMOOTHNESS",
        "COHERENCE",
        "PHASE",
        "RESONANCE",
        "PERCEPTION",
        "ADAPTATION",
        "INPUT",
    ]


def loop_seal_manifest() -> dict[str, Any]:
    """Machine-readable sealed loop contract."""
    return {
        "title": "STARLINE Ω :: SCHRÖDINGERIZED LATTICE :: IONQ CLOSED LOOP",
        "sealed": True,
        "hex_lattice": {f"0x{k:02X}" if k < 0x100 else f"0x{k:04X}": v for k, v in OPCODE_TO_FIELD.items()},
        "mode_ladder": {f"0x{k:02X}": v for k, v in MODE_NAMES.items()},
        "coherence_law": "Δc = α·S·(1-c)^p·(½+½Ψ)·dt − β·I·dt − λ·noise·dt",
        "economy_projection": "dℛ = k·Ψ·S·c^γ·(1+λ·R₊)·dt",
        "audio_hamiltonian": "A(t) = f(v, S, c, R, κ)",
        "sync_order": "R = |Σ exp(iφ_j)/N|",
        "phase_law": "φ ← φ + ω·v·dt",
        "transport": "smooth transport on κ(s)",
        "asymptotic_chain": asymptotic_identity_chain(),
        "sacred_variables": ["v", "S", "c", "phi", "R"],
        "axiom": "velocity is not granted; velocity emerges from coherence",
    }
