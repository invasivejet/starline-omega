# STARLINE Ω — Performance & self-host

## Architecture (high performance)

| layer | rate | mechanism |
|-------|------|-----------|
| Simulation | **60 Hz** fixed | `SimClock` accumulator, max 4 catch-up steps/frame |
| Control uplink | **30 Hz** | client fires only on change |
| State downlink | **20 Hz** | `UnreliableRemoteEvent` + wire[20] (drops OK) |
| Presentation | **render** | `ClientState` interpolates between packets |
| Economy attr | **5 Hz** | `StarlineResonance` only when Δ > 0.05 |
| Trail VFX | **15 Hz** | client presentation |
| Camera FOV | **60 Hz** | client presentation |

**Removed:** 15+ `SetAttribute` calls per player per frame (major replication CPU win).

Server still sets **HumanoidRootPart** CFrame each sim step (authoritative motion). Clients read **coherence/audio** from `State` replicate.

---

## Self-host checklist (Roblox)

1. `rojo serve` → Studio → **Publish** private experience (you own the place).
2. **Game Settings → Security**: enable Studio API access if testing DataStore.
3. **Game Settings → Physics**: default; no heavy parts on track.
4. **Server tab** (when live): prefer dedicated servers for 8+ players.
5. Assign `SoundService.StarlineMusic` SoundId once.

No VPS required for the Roblox prototype.

---

## Studio perf settings

- Keep `StarlineWaypoints` parts **non-colliding**, anchored.
- `TrackVisualSamples = 96` in Config (lower if GPU-bound).
- Avoid extra scripts in `Heartbeat`; STARLINE uses one server connection.
- Test with **MicroProfiler** (Ctrl+Alt+F6) — server time in `StarlineServer`.

---

## Config knobs (`Config.lua`)

```lua
Config.SimHz = 60
Config.ReplicateHz = 20      -- raise to 30 if HUD feels laggy
Config.ControlHz = 30
Config.MaxSimStepsPerFrame = 4
Config.TrackVisualSamples = 96
```

Lowering `ReplicateHz` saves bandwidth for mobile; raising improves HUD/audio responsiveness.

---

## Python reference

Same math, offline tuning — not in the live hot path:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
python scripts/tuning_sweep.py
```

---

## Invariants under perf mode

- Server remains authoritative for `c`, `φ`, `R`, position.
- Clients do not integrate coherence locally.
- `State` payload is perceptual; sim never trusts client wire uplink.
