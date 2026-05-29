# Running STARLINE Ω locally

Two runtimes share one engine contract (`config.py` ↔ `Config.lua`, wire packet layout).

```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL DEVELOPMENT                                          │
├─────────────────────────────────────────────────────────────┤
│  A. Headless (Python)     — tuning, CI, field research       │
│  B. Roblox Studio (Rojo)  — feel, audio, economy, publish  │
│  C. Telemetry sink (opt)  — HTTP JSONL on localhost:8765   │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick start (one command)

```bash
cd starline
./scripts/local_run.sh          # venv + tests + headless 15s
./scripts/local_run.sh --rojo   # + rojo serve in background
./scripts/local_run.sh --full   # + telemetry server
```

Requires: **Python 3.10+**, optional **Rojo** for Studio sync.

---

## A. Headless runtime (no Roblox)

The authoritative **reference sim** on your machine:

```bash
source .venv/bin/activate   # created by local_run.sh
python scripts/headless_play.py --profile smooth --seconds 30
python scripts/headless_play.py --profile chaotic --wire-log output/wires.jsonl
```

What it runs:

| step | rate | same as live |
|------|------|--------------|
| Sim | 60 Hz fixed | `SimClock` / server |
| Replicate | 20 Hz | wire log lines |
| Economy ℛ | per tick | `economy.py` |
| HUD | 4 Hz terminal | Studio HUD |

Outputs:

| file | content |
|------|---------|
| `output/headless_session.json` | telemetry + ℛ summary |
| `output/wires_*.jsonl` | wire[20] time series |

Use this for **tuning** before opening Studio.

---

## B. Roblox Studio (interactive)

### First-time setup

```bash
# Install Rojo: https://rojo.space/docs/install
cd starline
rojo serve
```

1. Open **Roblox Studio** → install **Rojo plugin**
2. **Connect** to `localhost:34872` (default)
3. **Play** (F5)

### Verify

Output window:

```text
[Starline] perf server | sim 60 Hz | replicate 20 Hz | state UnreliableRemoteEvent ...
```

HUD top-left: ℛ, c, flow, track.

### Local Studio settings

| setting | value |
|---------|--------|
| Game Settings → Security → Studio API | ON (DataStore tests) |
| `SoundService.StarlineMusic` | your loop SoundId |
| `Workspace.StarlineWaypoints` | optional ≥4 parts |
| `Workspace.StarlineWaypointsCircuit` | optional circuit layout |

### Controls

| key | action |
|-----|--------|
| WASD | drive |
| U | unlock circuit (40 ℛ) |
| 1 / 2 | oval / circuit |

---

## C. Local telemetry server (optional)

Terminal 1:

```bash
python scripts/telemetry_server.py --port 8765
```

Writes: `output/telemetry_live.jsonl`

For future Studio HTTP POST (published experience + HTTP enabled), set URL to `http://127.0.0.1:8765/telemetry`.

Headless sessions already write `output/headless_session.json` without HTTP.

---

## Config parity

Keep Python and Lua in sync:

```bash
python scripts/sync_config_check.py
```

Run in CI via `./scripts/dev.sh`.

---

## Full local plan (checklist)

| # | task | command / doc |
|---|------|----------------|
| 1 | Install deps | `./scripts/local_run.sh` |
| 2 | Tune coeffs | `tuning_sweep.py` → edit `config.py` + `Config.lua` |
| 3 | Headless validate | `headless_play.py --profile smooth` |
| 4 | Studio feel | `rojo serve` → Play |
| 5 | Audio asset | assign SoundId |
| 6 | Circuit track | waypoints in `StarlineWaypointsCircuit` |
| 7 | Publish | `docs/PUBLISH.md` |

---

## Two-machine workflow (recommended)

| machine activity | runtime |
|------------------|---------|
| Coding / tuning / CI | **Headless Python** |
| Feel / VFX / audio / MP | **Roblox Studio** |
| Live ops | **Published Roblox place** (self-hosted) |

You do **not** need a VPS until you run a custom backend outside Roblox.

---

## Troubleshooting

| issue | fix |
|-------|-----|
| `rojo: command not found` | install Rojo or manual copy `roblox/README.md` |
| No HUD in Studio | check `StarlineHud` in StarterPlayerScripts (Rojo sync) |
| ℛ always 0 | drive with c > 0.4 (smooth throttle) |
| DataStore not saving in Studio | enable Studio API services |
| Config drift CI fail | sync `Alpha`, `CoherencePower`, etc. both files |

---

## Related docs

- [SELF_HOST.md](SELF_HOST.md) — hosting model
- [PUBLISH.md](PUBLISH.md) — go live on Roblox
- [PERFORMANCE.md](PERFORMANCE.md) — tick rates
- [ENGINE.md](ENGINE.md) — equations
