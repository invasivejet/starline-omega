# STARLINE Ω — Final Engine Rigor

Operational rigor, perceptual calibration, mathematical consistency.
Companion to `INVARIANTS.md` and `ENGINE.md`.

---

## 1. Canonical units

| quantity | symbol | unit | notes |
|----------|--------|------|-------|
| arc-length | `s` | world units along spline | display: `s_norm = s / L ∈ [0,1)` |
| velocity | `v` | arc-length / second | |
| acceleration | `a` | arc-length / second² | |
| curvature | `κ` | inverse arc-length | |
| phase | `φ` | radians | |
| sync order | `R` | dimensionless | ∈ [0,1] |
| coherence | `c` | dimensionless | ∈ [0,1] |
| smoothness | `S` | dimensionless | ∈ [0,1] |

Implementation: `starline/units.py`.

---

## 2. Numerical stability envelopes

Every variable has **stable range** (design target) and **hard clamp** (never exceed).

| variable | stable | hard clamp |
|----------|--------|------------|
| `v` | 0–120 | 0–200 |
| `c` | 0–1 | [0,1] strict |
| `R` | 0–1 | [0,1] strict |
| `S` | 0–1 | [0,1] strict |
| `jerk` | < 8 | < 20 |
| `φ` | ℝ | wrapped mod 2π |

Implementation: `starline/stability.py`.

---

## 3. Simulation vs presentation tick

```
Simulation   = fixed Δt_sim  (deterministic)
Presentation = interpolated render frame
```

Coherence, sync, and audio timing use **simulation state only**.
Visuals/camera may interpolate between `t−Δt` and `t`.

Implementation: `starline/ticks.py`, `engine.fixed_update()` / `engine.present()`.

---

## 4. Readability principle

Player must perceive curvature intention, velocity consequence, coherence, and sync opportunity in **one glance**.

Formal bound:

```
C_visual < C_readability_max
```

Implementation: `starline/readability.py` (complexity budget for VFX/UI).

---

## 5. No false reward

```
∂c/∂noise < 0   always
```

Incoherent motion, random steering, exploit oscillation, and input spam must **never** raise coherence.

Implementation: `input_noise.py` + noise penalty in `coherence.py`.

---

## 6. Resonance is a field, not a buff

Resonance is **continuous geometric alignment** from curvature, anticipation, smoothness, and sync — not nitro, not collectible multiplier.

```
resonance(s, t) ∈ [0, 1]   — modulates gain multiplicatively
```

Implementation: `starline/resonance.py`.

---

## 7. Flow-state hysteresis

Sharp thresholds flicker. Each state has **enter** and **exit** thresholds.

| state | enter (example) | exit (example) |
|-------|-----------------|----------------|
| flow | c>0.92, R>0.85 | c<0.85 or R<0.75 |
| resonant | c>0.72 | c<0.65 |
| stable | c>0.45 | c<0.38 |

Implementation: `FlowStateMachine` in `starline/flow.py`.

---

## 8. Track topology classes

| class | purpose |
|-------|---------|
| `sustain` | long coherence build |
| `pulse` | rhythmic curvature |
| `fracture` | instability challenge |
| `spiral` | synchronization corridor |
| `silence` | low-information recovery |

Tracks are **musical topology compositions**.

Implementation: `starline/topology.py`.

---

## 9. Latency budgets

| path | max |
|------|-----|
| input → motion | 50 ms |
| motion → audio | 30 ms |
| camera lag | 80 ms |

Exceeding breaks: *“the world sings with my motion.”*

Implementation: `starline/latency.py` (targets + validation hooks).

---

## 10. Camera philosophy

Camera is **geometric intuition assistance**:

- reveal curvature anticipation
- reinforce smoothness
- amplify coherence perception

Never: excessive shake, obscured geometry, over-cut cinematics.

Documented for Roblox client; config in `latency.py` / client README.

---

## 11. Telemetry as field research

Not vanity analytics — measuring **emergent coordination structures**:

- coherence by track segment (`s_norm` bins)
- sync formation maps
- resonance chain durations
- steering entropy
- musical-state (flow) occupancy

Implementation: `starline/telemetry.py`.

---

## 12. Soul constraint

Every feature must answer:

> Does this increase the player’s perception of coherent motion?

If not: remove it.

---

## 13. Canonical engine identity

The coupled perceptual-geometric system:

```
Flow = ℱ(v, S, c, φ, R, κ)
```

Graphics, cars, tracks, networking, economy, AI are **downstream manifestations** of this flow field.

Implementation: `starline/canonical.py`.
