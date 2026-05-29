# STARLINE Ω

**Schrödingerized lattice · IonQ closed loop · coherent motion engine**

Players synchronize with the geometry of a track. The world projects that state as music, light, and speed.

```
┌────────────────────────────────────────────────────────────┐
│ STARLINE Ω :: SCHRÖDINGERIZED LATTICE :: IONQ CLOSED LOOP │
└────────────────────────────────────────────────────────────┘

Flow = ℱ(v, S, c, φ, R, κ)

INPUT → MOTION → SMOOTHNESS → COHERENCE → PHASE → RESONANCE → PERCEPTION → ADAPTATION → INPUT
```

> *velocity is not granted — velocity emerges from coherence*

**[ Ω LOOP SEALED ]** — see [docs/SCHRODINGER_LATTICE.md](docs/SCHRODINGER_LATTICE.md)

---

## What this is

| layer | what |
|-------|------|
| **Kernel** | 5 sacred variables `(v, S, c, φ, R)` + deterministic 60 Hz sim |
| **Economy** | `dℛ = k·Ψ·S·c^γ·(1+λ·R₊)·dt` — projection, not a coin shop |
| **Wire** | `wire[20]` reference + **8-byte** packed perceptual core @ 20 Hz |
| **Hex lattice** | Opcode map `0x76→v`, `0x63→c`, … `0x211B→ℛ` |
| **Roblox** | Thin shell: server authority, client interpolation |

Not a racing game. An **instrument** on an arc-length manifold.

---

## Quick start

```bash
git clone <your-repo-url>
cd starline
./scripts/local_run.sh
python scripts/loop_seal.py          # seal manifest → output/schrodinger_manifest.json
python scripts/coherence_loop.py     # closed measurement loop
rojo serve                           # Studio → Play
```

| doc | purpose |
|-----|---------|
| [SCHRODINGER_LATTICE.md](docs/SCHRODINGER_LATTICE.md) | sealed loop + hex opcodes |
| [RUNTIME_CONTRACT.md](docs/RUNTIME_CONTRACT.md) | frozen physics contract |
| [GAME_ENGINE.md](docs/GAME_ENGINE.md) | north star |
| [LOCAL_RUN.md](docs/LOCAL_RUN.md) | dev setup |
| [PUBLISH.md](docs/PUBLISH.md) | Roblox publish |

---

## Repository layout

```
starline/
  docs/                    # invariants, architecture, lattice
  python/src/starline/     # reference kernel (numpy only)
  roblox/Starline/         # live runtime modules
  roblox/ServerScriptService/
  roblox/StarterPlayerScripts/
  scripts/local_run.sh     # one-command validation
  output/                  # generated reports (gitignored)
```

---

## Primitives (kernel modules)

| Python | Roblox | role |
|--------|--------|------|
| `engine.py` | `Engine.lua` | orchestrator |
| `motion.py` | `MotionCore.lua` | arc-length transport |
| `coherence.py` | `Coherence.lua` | `Δc = S(1-c)^p` |
| `packets.py` | `Packets.lua` | wire[20] |
| `wire_pack.py` | `WirePack.lua` | 8-byte pack |
| `hex_lattice.py` | `HexLattice.lua` | opcode lattice |
| `economy.py` | `EconomyField.lua` | ℛ integral |

---

## Controls (Studio)

WASD · **B** garage · **F** AFK cruise · **U** unlock circuit (40 ℛ) · **1** oval · **2** circuit

---

## License

MIT — see [LICENSE](LICENSE).
