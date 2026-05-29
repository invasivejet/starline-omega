# STARLINE Ω — Progress & full plan

Last updated: 2026-05-28

## Status: **locally runnable end-to-end**

| phase | item | status |
|-------|------|--------|
| **0** | Engine + invariants + rigor | done |
| **1** | Packet encoding G/P/C/H | done |
| **2** | Perf server 60/20/30 Hz | done |
| **3** | UnreliableRemote + interpolation | done |
| **4** | Economy ℛ + DataStore | done |
| **5** | Track unlock oval/circuit | done |
| **6** | HUD + camera | done |
| **7** | Tuning bench | done |
| **8** | **Local headless runtime** | done |
| **9** | **local_run.sh + LOCAL_RUN.md** | done |
| **10** | Config sync CI | done |
| **11** | Telemetry sink (localhost) | done |
| **12** | Publish guide | done |
| **13** | Playtest / publish | **you** |
| **14** | Audio stems | optional |
| **15** | Custom circuit waypoints | **you** |

---

## Run locally (start here)

```bash
./scripts/local_run.sh          # Python: tests + headless
./scripts/local_run.sh --rojo   # + Rojo for Studio
./scripts/local_run.sh --full   # + telemetry :8765
```

**[LOCAL_RUN.md](LOCAL_RUN.md)** — complete guide.

---

## Two local runtimes

| runtime | command | purpose |
|---------|---------|---------|
| **Headless** | `python scripts/headless_play.py` | tuning, CI, wire logs, ℛ |
| **Roblox** | `rojo serve` → Play | feel, audio, MP, publish |

Same math: `config.py` ↔ `Config.lua` (verified by `sync_config_check.py`).

---

## Outputs

```
output/
  headless_session.json
  tuning_sweep.json
  track_lattice.json
  wires_*.jsonl
  telemetry_live.jsonl   # if telemetry_server running
```

---

## Controls (Studio)

WASD · **U** unlock · **1** oval · **2** circuit

---

## Docs map

| doc | topic |
|-----|--------|
| **[GAME_ENGINE.md](GAME_ENGINE.md)** | **the final engine idea (north star)** |
| [LOCAL_RUN.md](LOCAL_RUN.md) | **how to run on your machine** |
| [SELF_HOST.md](SELF_HOST.md) | hosting model |
| [PUBLISH.md](PUBLISH.md) | go live |
| [PERFORMANCE.md](PERFORMANCE.md) | tick rates |
| [ENGINE.md](ENGINE.md) | equations |
| [ECONOMY.md](ECONOMY.md) | ℛ ledger |
