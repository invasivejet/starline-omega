# Test drive — final checklist

Run this before Studio. One command:

```bash
cd starline
chmod +x scripts/test_drive.sh
./scripts/test_drive.sh
```

All six steps must pass. Then open Studio.

---

## Studio (interactive test drive)

### Prerequisites

| tool | install |
|------|---------|
| Python 3.10+ | system |
| Rojo 7+ | [rojo.space/docs/install](https://rojo.space/docs/install) |
| Roblox Studio | Windows or via Roblox Studio for Linux docs |

### Steps

**Terminal:**

```bash
cd starline
rojo serve
```

**Studio:**

1. New **Baseplate** or empty place  
2. **Rojo** plugin → **Connect** → `localhost:34872`  
3. **Home → Game Settings → Security** → ✅ **Enable Studio Access to API Services**  
4. **Play** (F5)

### Success signals

| signal | what you see |
|--------|----------------|
| Server boot | Output: `[Starline] perf server \| sim 60 Hz \| replicate 20 Hz ...` |
| Bootstrap | `[Starline] Test-drive bootstrap ready` |
| Track | Blue **glowing beams** forming an oval (`StarlineTrackVisual`) |
| HUD | Top-left: ℛ, coherence, flow, ride name |
| Motion | Character slides along track when holding **W** |
| Economy | ℛ increases while driving smoothly |

### Controls

| key | action |
|-----|--------|
| W / S | throttle / brake |
| A / D | steer |
| B | garage (buy / equip rides) |
| F | AFK cruise |
| U | unlock circuit (40 ℛ) |
| 1 | oval track |
| 2 | circuit track |

---

## Headless (no Studio)

```bash
python scripts/headless_play.py --profile smooth --seconds 60
```

Watch **c** and **ℛ** rise in the terminal.

---

## Publish (friends can play)

1. Studio → **File → Publish to Roblox** → Private / Unlisted  
2. Optional: assign `SoundService.StarlineMusic.SoundId` to a loop  
3. Share experience link  

See [PUBLISH.md](PUBLISH.md).

---

## Troubleshooting

| problem | fix |
|---------|-----|
| No Rojo connect | `rojo serve` running? Firewall allow 34872? |
| No track visible | Check Output for errors; ensure `StarlineServer` loaded |
| ℛ stays 0 | Drive with **W** until c > 0.4; check coherence on HUD |
| Character doesn't move | Server script must run; check `StarlineServer` in ServerScriptService |
| DataStore errors in Studio | Enable API Services (see above) |

---

## Repo

https://github.com/invasivejet/starline-omega

```
[ Ω LOOP SEALED ]
```
