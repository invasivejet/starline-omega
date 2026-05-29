# STARLINE Ω — Production architecture

**Status:** authoritative boundaries for sim, replication, presentation, and economy.

---

## Four layers (strict separation)

```
┌──────────────────────────────┐
│ 1. SIMULATION (server, 60Hz) │  ← truth: v, S, c, φ, R, κ
└────────────┬─────────────────┘
             ↓
┌──────────────────────────────┐
│ 2. STATE REDUCTION (20Hz)    │  ← wire / delta-wire snapshot
└────────────┬─────────────────┘
             ↓
┌──────────────────────────────┐
│ 3. CLIENT PRESENTATION       │  ← interpolate, audio, HUD, VFX
└────────────┬─────────────────┘
             ↓
┌──────────────────────────────┐
│ 4. ECONOMY (projection)      │  ← ℛ = ∫ energy(state) dt  (server only)
└──────────────────────────────┘
```

Economy is **not** a gameplay system. It is the time integral of coherent motion energy.

---

## Three truths

1. **Geometry evolves** — `(v, S, c, φ, R)` from deterministic server sim.
2. **Everything else is a projection** — audio, VFX, HUD, ℛ.
3. **Clients never compute truth** — interpolate and render only.

Frozen loop (never bypass):

```
Motion → Smoothness → Coherence → Phase → Audio/Visual
```

---

## Authority map

| concern | owner | rate |
|---------|--------|------|
| Physics / coherence | Server `Engine.step` | 60 Hz |
| ℛ ledger | Server `EconomyField.integrate` | 60 Hz (same tick) |
| Wire snapshot | Server `StateReplicator` | 20 Hz |
| AFK control | Server `AfkPilot` (motion only) | 60 Hz |
| Interpolation | Client `ClientState` | render |
| Audio stems | Client `MusicController` | 20 Hz from packet |
| Purchases / unlocks | Server + DataStore | event |

---

## Economy (energy functional)

```
dℛ = k · Ψ · S · c^γ · (1 + λ·R₊) · dt     when c ≥ c_min
```

| symbol | config | role |
|--------|--------|------|
| `k` | `ResonanceEarnK` | scale |
| `γ` | `ResonanceCoherenceGamma` | rewards high coherence nonlinearly |
| `λ` | `ResonanceSyncLambda` | multiplayer amplification |
| `Ψ` | `state.resonance` | geometry + sync field |
| `R₊` | `max(0, R)` | sync order parameter |

**AFK** is not a separate economy. Autopilot produces lower `S` and capped effective `c`; same integral applies. Session cap is anti-bot only.

---

## Networking

- Uplink: control @ 30 Hz (`RemoteEvent`)
- Downlink: `UnreliableRemoteEvent` @ 20 Hz
- **Delta-wire:** slow fields sent as deltas; keyframe full wire every N ticks
- **SimClock:** accumulator capped at `MaxSimCatchupSec` (0.25s) — no teleport storms

See [ENCODING.md](ENCODING.md), [WIRE_PACK.md](WIRE_PACK.md), [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md), [PERFORMANCE.md](PERFORMANCE.md).

## Phase roadmap (current)

| phase | focus | tool |
|-------|--------|------|
| I | Lock runtime contract | [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) |
| II | Measure emergence | `scripts/field_report.py` |
| III | Compose tracks | [TRACK_COMPOSITION.md](TRACK_COMPOSITION.md) |
| IV | Compress wire | `WirePack` 8 B @ 20 Hz |
| V | Perception (stems, camera) | audio @ packet rate |

---

## Closed experimental loop

```
PLAY → MEASURE → TUNE → REPLAY → COMPARE
```

Tool: `python scripts/coherence_loop.py`

Metric:

```
efficiency = ℛ / ∫ c dt
```

Run three profiles (chaotic / normal / smooth) and compare ℛ/min, AFK vs active.

---

## What not to add (until loop closes)

- New currencies or RPG stats
- Parallel AFK reward tables
- Client-side ℛ estimation
- Per-frame audio logic disconnected from state packets

---

## File map

| layer | Roblox | Python |
|-------|--------|--------|
| Sim | `Engine.lua`, `MotionCore.lua`, … | `engine.py` |
| Reduce | `StateReplicator.lua`, `WireDelta.lua` | `packets.py` |
| Present | `ClientState.lua`, `MusicController.lua` | — |
| Economy | `EconomyField.lua` | `economy.py` |
| Clock | `SimClock.lua` | `ticks.py` |
| Measure | `TelemetrySink.lua` | `telemetry.py`, `coherence_loop.py` |
