# STARLINE Ω — The Game Engine (final idea)

**One sentence:** A **coherent motion engine** where players harmonize with the geometry of a track — and the world sings back.

This is not a racing game engine. It is not a physics engine. It is a **symplectic perception–geometry kernel** with a thin playable shell.

---

## Is it lightweight?

**Yes — by design.**

| measure | STARLINE Ω | typical “game engine” |
|---------|------------|------------------------|
| Sacred state variables | **5** (`v`, `S`, `c`, `φ`, `R`) | dozens–hundreds |
| Wire packet | **20 floats** | bespoke netcode + components |
| Core loop depth | **5 stages** (frozen) | open-ended systems |
| Reference + Roblox kernel | **~3.5k LOC** (py+lua) | millions |
| Dependencies (Python) | **numpy only** | engines, physics, ECS |
| Progression model | **ℛ on manifold** | currencies, stats, trees |

Lightweight does **not** mean shallow. It means **no redundant ontology** — every feature must reduce to geometry, coherence, or perception.

What you are **not** carrying:

- Full 3D rigid-body physics  
- Terrain / open world  
- Inventory RPG layers  
- Arbitrary gameplay scripting VM  
- Asset pipeline / editor (Roblox *is* the shell for now)  

What you **are** carrying:

- Spline geometry as the world  
- Coherence as the only “health”  
- Music as state projection  
- Economy as integrated resonance  
- Multiplayer as phase synchronization  

That is an **instrument**, not a platform — and instruments are lightweight by nature.

---

## The engine identity (canonical)

Everything is this coupled field:

```
Flow = ℱ(v, S, c, φ, R, κ)
```

| symbol | layer | meaning |
|--------|-------|---------|
| `κ`, `s` | **Geometry** | the score — curvature rhythm on a 1D manifold |
| `v`, `a` | **Physics** | motion along arc-length only |
| `S`, `c`, `Ψ` | **Chemistry** | order vs disorder on the path |
| `φ`, `R` | **Harmonic** | phase topology + ensemble sync |
| `A(t)` | **Perception** | audio/visual = `f(v,S,c,R,κ)` |

**Frozen pipeline (never bypass):**

```
INPUT → MOTION → SMOOTHNESS → COHERENCE → PHASE → PERCEPTION
```

---

## Architectural layers (how to think about it)

```
┌─────────────────────────────────────────────────────────────┐
│  PLAYABLE SHELL (Roblox today)                              │
│  HUD · trails · camera · DataStore · track unlock           │
├─────────────────────────────────────────────────────────────┤
│  PERCEPTION                                                 │
│  audio stems · VFX · readability budget                     │
├─────────────────────────────────────────────────────────────┤
│  KERNEL (authoritative)                                     │
│  Engine · FlowStateMachine · ResonanceField · Economy ℛ     │
├─────────────────────────────────────────────────────────────┤
│  ENCODING                                                   │
│  G/P/C/H packets · wire[20] · TrackLattice                  │
├─────────────────────────────────────────────────────────────┤
│  RUNTIME                                                    │
│  Python headless │ Roblox server 60Hz │ client interp 20Hz  │
└─────────────────────────────────────────────────────────────┘
```

Downstream manifestations (cars, skins, UGC tracks, AI) are **projections of the kernel** — not parallel game designs.

---

## What “the game” actually is

Players do not “win a race.” They:

1. **Read** upcoming curvature (geometry)  
2. **Align** steering with anticipation (smoothness)  
3. **Maintain** coherence (energetic order)  
4. **Sync** with others on the same manifold (harmonic)  
5. **Hear** the state they are creating (perception)  

**Velocity is not granted. It emerges from coherence.**

**Music is not decoration. It is the perceptual render of state-space.**

Failure feels like **falling out of sync** — not like losing HP.

Progression is **ℛ (resonance)** earned on the manifold — unlocking new topological scores (tracks), not buying power.

---

## Track = musical topology (content model)

Tracks are not maps. They are **scores**:

| topology class | gameplay role |
|----------------|---------------|
| `sustain` | build coherence |
| `pulse` | rhythmic κ — percussion |
| `fracture` | instability challenge |
| `spiral` | sync corridor |
| `silence` | recovery |

Authored as waypoints + `TrackLattice` JSON. Procedural/AI generation = optimize ℱ along a lattice later.

---

## Runtime map (local → live)

| mode | command | role |
|------|---------|------|
| **Headless** | `headless_play.py` | truth for tuning |
| **Studio** | `rojo serve` | human feel |
| **Published** | Roblox place | self-hosted live game |
| **Telemetry** | `telemetry_server.py` | field research |

See [LOCAL_RUN.md](LOCAL_RUN.md).

---

## Performance contract (lightweight + fast)

| tick | rate |
|------|------|
| Simulation | 60 Hz fixed |
| State replicate | 20 Hz unreliable + interpolate |
| Control | 30 Hz on change |
| Economy attribute | 5 Hz |

No per-frame attribute spam. One wire vector per replicate.

See [PERFORMANCE.md](PERFORMANCE.md).

---

## What “build out” means from here

The engine **exists**. Next work is **instrument-making**, not feature sprawl:

1. Tune coefficients (`tuning_sweep.py`)  
2. Author 1–3 tracks with distinct topology  
3. Layer audio stems on `A(t)`  
4. Playtest published place  
5. Telemetry → adjust lattice  

Forbidden without geometric reduction:

- nitro, XP, generic currencies  
- combat, loot, skill trees  
- open-world traversal  

---

## Document map (constitution)

| doc | role |
|-----|------|
| **GAME_ENGINE.md** (this file) | north star |
| [INVARIANTS.md](INVARIANTS.md) | frozen rules |
| [ENGINE.md](ENGINE.md) | equations |
| [RIGOR.md](RIGOR.md) | units, hysteresis, soul |
| [ENCODING.md](ENCODING.md) | packets |
| [ECONOMY.md](ECONOMY.md) | ℛ ledger |
| [LOCAL_RUN.md](LOCAL_RUN.md) | how to run locally |

---

## The final thing (remember this)

STARLINE Ω is a **coherent motion system** packaged as a playable experience.

The engine's job is not to simulate more reality.

Its job is to make **synchronization with geometry** the deepest, most legible, most beautiful verb in the game.

Everything else is optional shell.
