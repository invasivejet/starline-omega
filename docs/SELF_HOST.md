# Self-host STARLINE Ω (minimal path)

> Performance profile: see **[PERFORMANCE.md](PERFORMANCE.md)** — 60 Hz sim, 20 Hz state replicate, no per-frame attribute spam.

Build from what exists: Python reference + Rojo → your Roblox experience. No extra infra required for the prototype.

---

## Tier 0 — Local loop (today)

**One command (test drive):**

```bash
cd starline
./scripts/test_drive.sh         # full validation + Studio steps
./scripts/local_run.sh --rojo   # or: rojo serve after validation
```

See **[TEST_DRIVE.md](TEST_DRIVE.md)** for the final checklist.

**Full guide:** [LOCAL_RUN.md](LOCAL_RUN.md)

Roblox: `rojo serve` → Studio → Connect → **Play** (F5).

You self-host the **simulation authority** on your machine; Roblox hosts the place when you publish.

---

## Tier 1 — Your private Roblox place

1. Open Studio with synced project.
2. **File → Publish to Roblox** → create experience (private/unlisted).
3. Assign `SoundService.StarlineMusic.SoundId` (loop).
4. Optional: `Workspace/StarlineWaypoints` parts for a custom track.
5. **Game Settings → Security**: keep server authoritative scripts; disable client physics hacks.

No VPS needed — Roblox is the runtime host; you own the place + assets.

---

## Tier 2 — Repo / CI (already minimal)

```bash
# .github/workflows/ci.yml runs pytest on push
git remote add origin <your-repo>
git push
```

Self-hosted CI = your GitHub/GitLab runner or default GitHub Actions (already in repo).

---

## Tier 3 — Optional data plane (when tuning is stable)

| need | minimal self-host |
|------|-------------------|
| Telemetry JSON | `scripts/sim_report.py` → `output/`; extend server to `HttpService:PostAsync` your endpoint |
| Tuning sweeps | `scripts/tuning_sweep.py` (add when ready) on cron |
| Track lattices | `scripts/lattice_export.py` → JSON in repo or S3 |
| ML / analysis | Read `EnginePacket.to_wire()` parquet — Python only |

Skip Kubernetes until you have live players and a clear data contract (`docs/ENCODING.md` wire map).

---

## Tier 4 — “Full” self-host (later)

Only if you outgrow Roblox as sole runtime:

- **Dedicated sim server** running `CoherentMotionEngine` (Python) — same wire format as Studio.
- Roblox becomes **thin client** (render + input); server validates wire packets.

Not recommended until Phase 1 tuning is done on Roblox.

---

## Minimal build-out order

1. Publish private place + audio asset  
2. Tune coeffs (`Config.lua` ↔ `config.py`)  
3. Wire `Packets.lua` attributes on server  
4. One custom track + `TrackLattice` export  
5. Optional telemetry POST to your URL  
6. Geometric economy (see `ECONOMY.md`) — session then DataStore  

---

## Scripts (local tuning)

```bash
python scripts/tuning_sweep.py    # → output/tuning_sweep.json
python scripts/lattice_export.py --oval -o output/track_lattice.json
```

## Studio economy / tracks

| key | action |
|-----|--------|
| **B** | garage (buy / equip rides) |
| **F** | AFK cruise toggle |
| **U** | unlock `circuit` (40 ℛ) |
| **1** | select oval track |
| **2** | select circuit (if unlocked) |

Closed measurement loop (headless):

```bash
python scripts/coherence_loop.py   # → output/coherence_loop.md
```

Create `Workspace/StarlineWaypointsCircuit` with ≥4 parts for the paid track layout.

Enable **Game Settings → Security → Enable Studio Access to API Services** to test DataStore in Studio (otherwise ℛ is session-only in Studio).

---

## Checklist before calling it “hosted”

- [ ] Private experience published  
- [ ] `StarlineServer` runs without errors in Output  
- [ ] Coherence / flow attributes update while driving  
- [ ] Music responds to `StarlineCoherence`  
- [ ] 2-player test: `StarlineSyncR` moves together when aligned  
