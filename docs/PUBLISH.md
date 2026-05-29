# Publish STARLINE Ω (self-hosted live game)

## 1. Local validation

```bash
./scripts/dev.sh
rojo serve
```

Studio → Play → verify Output:

```text
[Starline] perf server | sim 60 Hz | replicate 20 Hz | state UnreliableRemoteEvent | control 30 Hz
```

Drive: HUD shows ℛ, c, flow. **U** / **1** / **2** for economy/tracks.

## 2. Assets

| asset | location |
|-------|----------|
| Music loop | `SoundService.StarlineMusic.SoundId` |
| Oval waypoints | `Workspace.StarlineWaypoints` (optional, ≥4 parts) |
| Circuit waypoints | `Workspace.StarlineWaypointsCircuit` (optional) |

## 3. Publish

1. **File → Publish to Roblox** → new experience (start **Private**).
2. **Game Settings → Security** → enable API services if using DataStore in Studio tests.
3. **Avatar** → disable heavy default animations if they fight root CFrame drive.
4. **Servers**: for 8+ players use dedicated servers (Roblox hosting).

## 4. Live tuning

Edit `ReplicatedStorage.Starline.Config` at runtime only for experiments — ship changes via Rojo + republish.

Locked coefficients (current):

- `Alpha = 1.85`, `CoherencePower = 2.5`
- `SimHz = 60`, `ReplicateHz = 20`, `UseUnreliableState = true`

## 5. Post-publish

- Playtest circuit unlock (40 ℛ) on real client latency.
- Watch `StarlineResonance` in leaderstats-style HUD, not Explorer spam.
- Iterate from `output/tuning_sweep.md` if coherence pacing drifts.

Your game URL is the self-hosted surface — no extra VPS until you run a custom backend.
