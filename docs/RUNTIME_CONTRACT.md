# STARLINE Ω — Frozen runtime contract

**Phase I status: LOCKED.** Changes to items below are **physics-engine changes**, not gameplay tweaks.

---

## Sacred variables (server truth @ 60 Hz)

| symbol | field | layer |
|--------|-------|-------|
| `v` | velocity | P |
| `S` | smoothness | G |
| `c` | coherence | C |
| `φ` | phase | C |
| `R` | sync_R | H |

Derived (never authoritative on client): `v_eff`, `Ψ`, flow state, ℛ, audio stems.

---

## Frozen loop (do not bypass)

```
Motion → Smoothness → Coherence → Phase → Perception
```

---

## Tick contract

| parameter | value | module |
|-----------|-------|--------|
| Sim rate | 60 Hz | `Config.SimHz` / `sim_dt` |
| Max catch-up | 0.25 s | `MaxSimCatchupSec` |
| Max steps/frame | 4 | `MaxSimStepsPerFrame` |
| Replicate | 20 Hz | `ReplicateHz` |
| Control uplink | 30 Hz | `ControlHz` |

---

## Economy projection (server only)

```
dℛ = k · Ψ · S · c^γ · (1 + λ·R₊) · dt     when c ≥ c_min
```

| coeff | config key |
|-------|------------|
| `k` | `ResonanceEarnK` |
| `γ` | `ResonanceCoherenceGamma` |
| `λ` | `ResonanceSyncLambda` |

AFK = constrained motion → lower `S`, `c_eff = min(c, 0.72)`. **Not** a parallel currency rail.

---

## Wire contract

| form | size | use |
|------|------|-----|
| `wire[20]` float | 80 B | reference / debug |
| `wire_pack` | 8 B | 20 Hz downlink (perceptual core) |
| delta-wire | variable | slow-field deltas between keyframes |

Index map: [ENCODING.md](ENCODING.md). Packed layout: [WIRE_PACK.md](WIRE_PACK.md).

---

## Authority

| action | owner |
|--------|-------|
| Integrate physics | Server `Engine.step` |
| Integrate ℛ | Server `EconomyField.integrate` |
| Pack state | Server `StateReplicator` / `WirePack` |
| Interpolate | Client `ClientState` |
| Audio render | Client `MusicController` @ packet rate |
| Purchases | Server `EconomyField.spend` + DataStore |

Clients **never** integrate ℛ or coherence.

---

## Change control

Before modifying frozen items, run:

```bash
python scripts/coherence_loop.py
python scripts/field_report.py
pytest -q
```

Reject changes that break:

- `chaotic → ~0 ℛ`
- `smooth > chaotic` efficiency
- `∂c/∂noise < 0` globally
- AFK rate < intentional rate (same energy equation)

---

## Dynamical loop (closed instrument)

```
geometry → motion → smoothness → coherence → sync → ℛ → perception → adaptation → geometry
```

See [ARCHITECTURE.md](ARCHITECTURE.md), [TRACK_COMPOSITION.md](TRACK_COMPOSITION.md).
