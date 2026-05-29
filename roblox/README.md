# Roblox MVP install

## Option A — Rojo (recommended)

From repo root:

```bash
rojo serve
```

Connect Roblox Studio plugin to `default.project.json`, then Play.

## Option B — manual copy

1. Copy `Starline/` → `ReplicatedStorage/Starline`
2. Copy `ServerScriptService/StarlineServer.server.lua` → `ServerScriptService`
3. Copy `StarterPlayerScripts/StarlineClient.client.lua` → `StarterPlayer.StarterPlayerScripts`

## Optional track authoring

Create `Workspace/StarlineWaypoints` and add `Part` instances as waypoints (≥ 4).
Otherwise the server spawns a default oval.

## Attributes replicated per player

| attribute | meaning |
|-----------|---------|
| `StarlineS` | arc position |
| `StarlineV` | speed |
| `StarlineCoherence` | 0..1 |
| `StarlineSyncR` | phase sync order parameter |
| `StarlineTempo` | audio mapping |
| `StarlineHarmony` | audio mapping |
| `StarlineDissonance` | audio mapping |
| `StarlineFlowState` | hysteresis flow (stable / resonant / flow) |
| `StarlineResonance` | geometric economy ledger ℛ (session) |
| `StarlineResonanceField` | Ψ at current tick |

Wire audio into SoundService. Economy: see `docs/ECONOMY.md` and `EconomyField.lua`.

## Self-host

See `docs/SELF_HOST.md` and `docs/PUBLISH.md`.

**Performance:** `StateUnreliable` @ 20 Hz + client interpolation (`ClientState.lua`).

## Controls

| key | action |
|-----|--------|
| U | unlock circuit (40 ℛ) |
| 1 / 2 | oval / circuit track |
