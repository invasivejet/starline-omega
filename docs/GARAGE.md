# Garage — buy & formulate rides

Spend **ℛ (resonance)** at the garage. There is no separate car currency.

Vehicles are **fictional names** inspired by real marques (European cars, Japanese motorcycles, regional e-bikes). We do not use trademarked logos or model names in-game.

## Categories (representation mix)

| category | examples | inspired character |
|----------|----------|-------------------|
| **Starter** | Urban Pulse | Free balanced coil |
| **European cars** | Rhein GT, Bavaria Touring, Alpine Line | BMW-class GT, touring, sports sedan |
| **Japanese motorcycles** | Sakura R1, Kiso Ninety, Kanjo Drift | Yamaha / Kawasaki sport, canyon bike |
| **Japanese e-bikes** | Kyoto Flux, Edo Line | Commuter / river-path assist |
| **European e-bikes** | Amsterdam Cruise, Alp Volt | Dutch upright, alpine trekking |
| **American e-bikes** | Brooklyn Volt, Sierra Glide | City snap, west-coast glide |

## Stats = engine coefficients (INVARIANT-safe)

Purchasing a vehicle changes **handling on the spline**, not RPG stats:

| coefficient | player feel |
|-------------|-------------|
| `MaxSpeed` / `Drag` | top-end envelope |
| `SteeringGain` / `CurveWeight` | corner aggression |
| `ThrottleAccel` / `BrakeDecel` | punch vs stability |
| `Gamma` | coherence → effective speed coupling |
| `Anticipation*` / `NoisePenalty` | forgiveness vs mastery |

Velocity still **emerges from coherence** — no pay-to-win raw `v` boosts.

## Controls

| key | action |
|-----|--------|
| **B** | open / close garage |
| Buy | spend ℛ (server authoritative) |
| Equip | rebuild sim with vehicle preset |

HUD shows active ride name.

## Files

- `roblox/Starline/VehicleCatalog.lua` — full roster + coef tables
- `roblox/Starline/VehicleGarage.lua` — unlock / equip / list
- `roblox/Starline/MotionConfig.lua` — merge preset onto `Config`
- `roblox/StarterPlayerScripts/GarageShop.client.lua` — shop UI
- `python/src/starline/vehicles.py` — headless mirror + tests

## Persistence

`EconomyStore` saves `vehicleUnlocks` and `activeVehicle` with ℛ and track unlocks.
