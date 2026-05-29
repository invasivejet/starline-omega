# Track authorship as composition

Tracks are **geometric scores**, not roads. Author by coherence waveform and topology class.

## Topology classes (perceptual roles)

| class | role on manifold |
|-------|------------------|
| **silence** | decompression, reset |
| **sustain** | coherence build |
| **pulse** | rhythmic articulation |
| **fracture** | destabilization |
| **spiral** | synchronization chamber |

## Example arc (sonata form)

```
silence → sustain → pulse → fracture → spiral → resonance release
```

## Tooling

```bash
python scripts/lattice_export.py --oval -o output/track_lattice.json
python scripts/field_report.py          # mean(c | s_norm bin) per track
```

## Validation signals

| metric | healthy track |
|--------|----------------|
| `mean(c \| bin)` | valleys + corridors visible |
| topology dwell | sustain/spiral segments earn more ℛ |
| corner failures | clustered in fracture, not sustain |

See `output/field_report.md` after a run.
