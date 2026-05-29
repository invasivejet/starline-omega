"""8-byte bitpacked perceptual state — Phase IV compression."""

from __future__ import annotations

import struct
from typing import Sequence

PACKED_SIZE = 8
V_MAX = 200.0
TWO_PI = 6.283185307179586


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _q10(x: float) -> int:
    return int(round(_clamp(x, 0.0, 1.0) * 1023))


def _q12_unit(x: float, scale: float) -> int:
    return int(round(_clamp(x / scale, 0.0, 1.0) * 4095))


def pack_perceptual(
    *,
    v: float,
    smoothness: float,
    coherence: float,
    phase: float,
    sync_R: float,
    flow_code: int = 0,
    topology_code: int = 15,
    v_max: float = V_MAX,
) -> bytes:
    """Pack perceptual core into 8 bytes (little-endian uint64 subset)."""
    ci = _q10(coherence)
    si = _q10(smoothness)
    vi = _q12_unit(v, v_max)
    phii = _q12_unit(phase % TWO_PI, TWO_PI)
    ri = _q10(sync_R)
    fi = int(flow_code) & 3
    ti = int(topology_code) & 15

    val = (
        ci
        | (si << 10)
        | (vi << 20)
        | (phii << 32)
        | (ri << 44)
        | (fi << 54)
        | (ti << 56)
    )
    return struct.pack("<Q", val & 0xFFFFFFFFFFFFFFFF)


def unpack_perceptual(data: bytes, *, v_max: float = V_MAX) -> dict[str, float | int]:
    if len(data) < PACKED_SIZE:
        data = data + b"\x00" * (PACKED_SIZE - len(data))
    (val,) = struct.unpack("<Q", data[:PACKED_SIZE])
    ci = val & 0x3FF
    si = (val >> 10) & 0x3FF
    vi = (val >> 20) & 0xFFF
    phii = (val >> 32) & 0xFFF
    ri = (val >> 44) & 0x3FF
    fi = (val >> 54) & 0x3
    ti = (val >> 56) & 0xF
    return {
        "coherence": ci / 1023.0,
        "smoothness": si / 1023.0,
        "v": vi / 4095.0 * v_max,
        "phase": phii / 4095.0 * TWO_PI,
        "sync_R": ri / 1023.0,
        "flow_code": fi,
        "topology_code": ti,
    }


def pack_from_wire(wire: Sequence[float], *, v_max: float = V_MAX) -> bytes:
    """Pack from full wire[20] layout (docs/ENCODING.md indices 1-based in Lua)."""
    w = list(wire)
    if len(w) < 18:
        w = w + [0.0] * (18 - len(w))
    return pack_perceptual(
        v=float(w[6]),
        smoothness=float(w[3]),
        coherence=float(w[10]),
        phase=float(w[13]),
        sync_R=float(w[15]),
        flow_code=int(w[17]),
        topology_code=int(w[5]) if w[5] < 255 else 15,
        v_max=v_max,
    )


def wire_from_packed(data: bytes, template_wire: Sequence[float] | None = None) -> list[float]:
    """Expand packed core into wire[20], preserving G slots from template if given."""
    p = unpack_perceptual(data)
    w = list(template_wire) if template_wire else [0.0] * 20
    while len(w) < 20:
        w.append(0.0)
    w[3] = float(p["smoothness"])
    w[5] = float(p["topology_code"])
    w[6] = float(p["v"])
    w[10] = float(p["coherence"])
    w[13] = float(p["phase"])
    w[15] = float(p["sync_R"])
    w[17] = float(p["flow_code"])
    return w
