# Geometric economy prototype (symplectic STARLINE)

**Not** a generic Roblox coin shop. Economy = **integrated geometric achievement** reducible to sacred variables and the wire packet.

Soul test: *Does spending/earning change how players perceive coherent motion?* If no → reject.

---

## Principle

There is one ledger: **Resonance** (dimensionless, earned on the manifold).

Economy is a **projection** of simulation energy — not a parallel system.

```
dℛ = k · Ψ · S · c^γ · (1 + λ·R₊) · dt     when c ≥ c_min
```

| symbol | config | meaning |
|--------|--------|---------|
| `ℛ` | — | spendable integral |
| `Ψ` | — | resonance field (geometry + sync) |
| `S` | — | smoothness |
| `c` | — | coherence |
| `γ` | `ResonanceCoherenceGamma` | nonlinear coherence reward |
| `λ` | `ResonanceSyncLambda` | multiplayer amplification |
| `k` | `ResonanceEarnK` | scale |

**Efficiency metric:** `ℛ / ∫ c dt` — run `python scripts/coherence_loop.py`.

**Forbidden:** XP, coins, nitro, energy unrelated to `(v,S,c,φ,R,κ)`.

See [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Earn rules (server authoritative)

Single integrand each sim tick (60 Hz). Flow state is **telemetry only** — not a separate payout.

| condition | effect |
|-----------|--------|
| `c < c_min` | `dℛ = 0` |
| AFK | same formula; `c_eff = min(c, 0.72)` from constrained autopilot |
| AFK session | cap 250 ℛ anti-bot |
| False reward | `∂c/∂noise < 0` in sim — no credit when incoherent |

Spend rules (prototype):

| spend | effect | geometric meaning |
|-------|--------|-------------------|
| Trail palette | cosmetic | readability budget OK |
| Track unlock | access | requires `ℛ` total earned **on that lattice** |
| Vehicle unlock | handling preset | garage — coef overrides only (see [GARAGE.md](GARAGE.md)) |
| Session boost | **none** that adds raw `v` | would break “velocity emerges from c” |

---

## Roblox implementation (minimal)

Module: `Starline/EconomyField.lua`

- Server integrates `dℛ` each fixed tick from attributes / packet.
- `player:SetAttribute("StarlineResonance", ℛ)` (session).
- Optional: `DataStoreService` persist `ℛ`, `flowPeaks`, per-track bests.
- Client shows thin bar: `ℛ` + current `flow_state` — no clutter.

Wire indices used: `Ψ` (13), `S` (4), `c` (11), `R` (16), flow (17–18).

---

## AFK Cruise (passive ℛ)

Press **F** in-game. Server autopilot earns ℛ at ~**42%** of active rate, session cap **250 ℛ**, no flow bonus.

See [AFK_MODE.md](AFK_MODE.md) and `output/afk_report.md`.

---

## Prototype scope (2 weeks)

1. **Session ℛ only** — no marketplace, no DevProducts.  
2. **One spend**: unlock second waypoint track when `ℛ > threshold`.  
3. **Leaderboard**: max `ℱ` (flow value) per track — from wire index 17.  
4. Playtest: earning ℛ must correlate with smooth/sync play, not spam.

---

## Later (if invariant-safe)

- UGC tracks as `TrackLattice` JSON; creator earns ℛ when others achieve flow on it.
- Robux cosmetics **only** skins; never stat boosts.
- Cross-place ℛ via DataStore + signed server validation.

---

## Anti-patterns

- Pay for max speed  
- Loot boxes  
- Daily login currency disconnected from driving  
- Battle pass unrelated to `κ` rhythm  

---

## Success metric

Economy works when players describe progress as:

> “I learned this curve and earned resonance on the spiral.”

Not: “I grinded coins.”
