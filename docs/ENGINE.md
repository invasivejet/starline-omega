# STARLINE Ω — Engine Design

## Permanent truth (post-MVP)

STARLINE Ω is **not fundamentally a racing game**.

It is a **coherent motion system**. Players are rewarded for smoothness, synchronization, anticipation, and harmonic alignment with curvature.

**Velocity is not granted mechanically. Velocity emerges from coherence.**

**Music is not decoration. Music is the perceptual projection of geometric state.**

All future systems must preserve:

```
Motion → Smoothness → Coherence → Phase → Audio/Visual
```

No future feature may bypass this loop. See `INVARIANTS.md` and `RIGOR.md`.

---

## Frozen core loop

```
INPUT → CONTROL → MOTION → SMOOTHNESS → COHERENCE → PHASE → AUDIO/VISUAL
```

Sacred variables only: `v`, `S`, `c`, `φ`, `R` (plus derived kinematics `s`, position).

---

## Equations (reference)

### Motion

```
v ← v + throttle·accel·dt − brake·decel·dt − drag·v·dt
s ← s + v_eff·dt
v_eff = v · (1 + γ · c)
position = C(s)
```

### Smoothness (with anticipation)

```
Δs = ds₀ + k_v · v_eff
κ_ahead = κ(s + Δs)
S = exp(− (w_j·|jerk| + w_c·curve_error(κ, κ_ahead)))
```

### Coherence (anti-saturation)

```
Δc = α · S · (1 − c)^p · dt  −  β · I · dt
c ∈ [0, 1],   p > 1  (default p = 2)
```

Instability `I`: sudden steer changes, brake spikes.

### Flow state (hysteresis)

| state | enter (example) | exit (example) |
|-------|-----------------|----------------|
| flow | c>0.92, R>0.85 | c<0.85 or R<0.75 |
| resonant | c>0.72 | c<0.65 |
| stable | c>0.45 | c<0.38 |

### Canonical identity

```
Flow = ℱ(v, S, c, φ, R, κ)
```

### Resonance field (not a buff)

```
Ψ_res ∈ [0,1]  — modulates Δc gain multiplicatively
```

### No false reward

```
∂c/∂noise < 0  — input noise penalty always applied
```

### Phase sync

```
φ += v · dt · ω
R = | Σ exp(i·φ_j) / N |
```

High `R` → slipstream (lower drag) + resonance boost.

### Audio law

```
A(t) = f(v, S, c, R, κ)
```

| channel | primary drivers |
|---------|-----------------|
| tempo | `v` |
| dissonance | `1−c`, `1−S` (failure = desync) |
| harmony | `c`, `S`, `R` |
| percussion | `|κ|` |
| richness | `c · S` |

Flow state modulates harmony/dissonance — no arbitrary track switches.

### Tracks as scores

Tracks are musical-geometric compositions (`track_score.py`):

- curvature rhythm → percussion density
- low-|κ| zones → harmonic sustain / resonance boost
- sharp Δκ → modulation (torsion events)

---

## Server authority

Authoritative on server: `c`, `φ`, `R`. Clients predict; server wins.

---

## Implementation map

| spec | Python | Roblox |
|------|--------|--------|
| Invariants | `docs/INVARIANTS.md` | (design doc) |
| Config | `config.py` | `Config.lua` |
| Spline | `spline.py` | `SplineTrack.lua` |
| Player | `player.py` | `PlayerState.lua` |
| Motion | `motion.py` | `MotionCore.lua` |
| Smoothness | `smoothness.py` | `Smoothness.lua` |
| Coherence | `coherence.py` | `Coherence.lua` |
| Flow | `flow.py` | `Flow.lua` |
| Phase | `phase.py` | `PhaseSync.lua` |
| Audio | `audio.py` | `AudioField.lua` |
| Track score | `track_score.py` | `TrackScore.lua` |
| Telemetry | `telemetry.py` | (server logs / future) |
| Units / stability | `units.py`, `stability.py` | `Stability.lua` |
| Resonance field | `resonance.py` | `Resonance.lua` |
| Input noise | `input_noise.py` | `InputNoise.lua` |
| Topology | `topology.py` | — |
| Canonical Flow | `canonical.py` | — |
| Sim / present ticks | `ticks.py` | fixed `Config.FixedDt` |
| Rigor spec | `docs/RIGOR.md` | — |
| State encoding | `packets.py`, `docs/ENCODING.md` | `Packets.lua` |
| Engine | `engine.py` | `Engine.lua` |

---

## Tuning discipline (current phase)

The next 80% of quality is **instrument-making**:

- curve feel, response latency
- audio modulation depth
- coherence pacing (`α`, `β`, `p`)
- resonance / flow thresholds

Not more systems.
