# STARLINE Ω — Lightweight State Encoding

Minimal structure to **auto-encode** runtime state into composable
**physical · chemical · geometric** packets — without breaking the frozen loop.

---

## Design principle

One entity, three layers, one wire vector:

```
Runtime (PlayerState + track sample)
    → encode()  → EnginePacket (typed)
    → flatten() → WireVector (fixed float32[N])
    → unflatten() → EnginePacket
    → decode()  → presentation / network / AI / telemetry
```

**Encode is lossless for sacred variables.**  
**Decode never re-integrates physics** (server authority preserved).

---

## Three layers (ontology)

| layer | domain | owns | sacred / primary |
|-------|--------|------|------------------|
| **G** | geometry | arc position, κ, S, topology | `S`, `κ`, `s_norm` |
| **P** | physics | kinematics along spline | `v` |
| **C** | chemistry | order, disorder, resonance, phase | `c`, `φ` |
| **H** | harmonic | ensemble sync (session) | `R` |
| **Ψ** | perception | audio/visual projection | derived only |

Loop order is fixed:

```
G + P → S → C → φ → H → Ψ
```

New game systems **declare a layer** and may only **read below, write their slot**.

---

## Packet types

### `GeometricPacket` (G)

| field | unit |
|-------|------|
| `s_norm` | dimensionless [0,1) |
| `kappa` | 1/length |
| `kappa_ahead` | 1/length |
| `S` | dimensionless |
| `curve_error` | 1/length |
| `topology` | enum string |

### `PhysicalPacket` (P)

| field | unit |
|-------|------|
| `v`, `a`, `jerk`, `v_eff` | length/timeⁿ |

### `ChemicalPacket` (C)

| field | unit |
|-------|------|
| `c` | dimensionless |
| `instability` | dimensionless |
| `resonance` | dimensionless field Ψ |
| `phi` | radians |
| `noise` | dimensionless |

### `HarmonicPacket` (H)

| field | unit |
|-------|------|
| `R` | dimensionless |

### `FlowPacket` (identity)

| field | source |
|-------|--------|
| `value` | ℱ(v,S,c,φ,R,κ) |
| `state` | hysteresis flow machine |

### `TrackLattice` (static score)

Discretized track: `s_norm[]`, `kappa[]`, `topology_code[]` — for procedural gen / AI / analysis.

---

## Wire layout (N = 20)

Fixed index map for Roblox attributes, UDP, parquet, ML:

| idx | field |
|-----|-------|
| 0–5 | G: s_norm, κ, κ_ahead, S, curve_err, topology_code |
| 6–9 | P: v, a, jerk, v_eff |
| 10–14 | C: c, I, Ψ, φ, noise |
| 15 | H: R |
| 16–17 | Flow: value, state_code |
| 18–19 | reserved |

---

## Composition rules (full game engine)

| future system | layer | allowed |
|---------------|-------|---------|
| spline / track authoring | G (static `TrackLattice`) | define κ rhythm |
| motion integrator | P | write v, a, jerk |
| smoothness | G | write S |
| coherence / resonance | C | write c, Ψ; read G,P |
| phase sync | C, H | write φ; read P |
| audio / VFX | Ψ | read-only encode |
| UI / HUD | Ψ | read-only |
| telemetry | all | read-only |
| AI / procedural tracks | G lattice | optimize ℱ along lattice |
| inventory / RPG | **forbidden** unless reducible to packets above |

---

## Autoencode API (Python)

```python
from starline.packets import encode_packet, EnginePacket, WIRE_SIZE

pkt = encode_packet(player, track_length, k0, k1, R, psi, topology, flow)
wire = pkt.to_wire()          # list[float] length WIRE_SIZE
back = EnginePacket.from_wire(wire)
```

Roblox: mirror `Packets.lua` with same index map.

---

## Build-out path

1. **Now** — packets + wire + tests  
2. **Tuning** — sweep writes `TrackLattice` + telemetry reads packets  
3. **Studio** — replicate `wire` as attributes or Buffer  
4. **Content** — tracks = `TrackLattice` + topology tags  
5. **AI** — train on wire sequences; loss = coherence emergence, not retention  

---

## Soul constraint (encoding edition)

Every new field must map to **(G, P, C, H)** or be rejected.
If it cannot flatten into the wire map, it does not ship.
