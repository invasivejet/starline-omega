# Bitpacked perceptual wire (8 bytes)

Low-dimensional world-state for 20 Hz downlink. Full `wire[20]` remains the reference decode path for tooling.

## Layout (60 bits used, 8 bytes LE)

| field | bits | quantize |
|-------|------|----------|
| `c` | 10 | `round(c · 1023)` |
| `S` | 10 | `round(S · 1023)` |
| `v` | 12 | `round(v/v_max · 4095)`, `v_max=200` |
| `φ` | 12 | `round(φ/2π · 4095)` |
| `R` | 10 | `round(R · 1023)` |
| flow | 2 | `state_code & 3` |
| topology | 4 | `topology_code & 15` |

**Bandwidth:** 8 B × 20 Hz = **160 B/s** per player (perceptual core only).

Position / κ_ahead remain on keyframes or full wire when `keyframe=true`.

## API

Python: `starline.wire_pack.pack_perceptual` / `unpack_perceptual` / `pack_from_wire`

Lua: `WirePack.encode(wire)` → `buffer` (8 bytes)

## Migration

1. Server sends `payload.packed` + optional full `wire` on keyframes.
2. Client `ClientState` prefers `WirePack.decode(packed)` when present.
3. Telemetry and headless tools keep using `wire[20]`.
