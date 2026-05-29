# AFK Cruise — realistic passive earning

There is no separate “cash” currency. **AFK earns Resonance ℛ** — the same geometric ledger as active play, at a **reduced, capped rate**.

## Design (realistic, invariant-safe)

| rule | why |
|------|-----|
| ℛ only from `Ψ · S` while `c > 0.4` | no false reward |
| AFK uses **autopilot** (server-side steer/throttle) | still on the manifold |
| Quality × `AfkEarnMultiplier` (1.65) on base `Ψ·S` term | ~40% active ℛ/min in sim; no flow bonus |
| **No flow-state bonus** while AFK | flow requires human anticipation |
| Coherence **soft-capped** at 0.72 while AFK | can't idle to perfect sync |
| Session AFK cap **250 ℛ** | anti-bot, realistic “background cruise” |
| Must keep `v > 8` | must actually be driving |

HUD shows ℛ as your balance. AFK portion tracked as `StarlineAfkEarned` (session).

## Player controls

| key | action |
|-----|--------|
| **F** | toggle AFK Cruise on/off |

When AFK is on, server drives; client input ignored for sim (you can still use U/1/2).

## Formula (same energy projection as active)

```
dℛ = k · Ψ · S · c_eff^γ · (1 + λ·R₊) · dt
c_eff = min(c, 0.72)   while AFK
```

AFK is **constrained motion** (autopilot), not a parallel economy. Lower `S` and capped `c_eff` emerge from control. Session cap 250 ℛ is anti-bot only.

## Steps to tune

1. `python scripts/afk_report.py` — compare ℛ/min active vs AFK  
2. Adjust `AfkEarnMultiplier`, `AfkSessionCap` in `Config.lua` / `config.py`  
3. Playtest in Studio: toggle **F**, wait 2 min, compare ℛ rate  
