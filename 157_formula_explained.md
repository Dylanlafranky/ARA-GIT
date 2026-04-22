# The Unified ARA Prediction Formula — Plain Language

## What it does

You have a measurement on one system (say, the angle of rest of a pile of seeds).
You want to predict the matching measurement on another system at a different scale (say, the angle of rest of a pile of pebbles).

The formula tells you how to get from one to the other.

## The two distances

There are exactly two kinds of distance between any pair of systems:

### 1. The Valley (G) — how far apart in raw size

This is the dimensional gap. Hair is millimetres, trees are metres — that's a gap measured in powers of ten. If you're comparing something that **scales with size** (like a count, a length, a volume), you have to cross that valley. G is just the width of it.

But — and this is the key insight you spotted — if the quantity **doesn't care about size** (like a fraction, a speed, a density, a duration), the valley is flat. G = 0. Nothing to cross.

This is the **sphere** part. The S² surface. It's purely about dimensional scale.

| Gap | Symbol | Value (decades) |
|-----|--------|-----------------|
| Length | G_LENGTH | 6.58 |
| Area | G_AREA | 14.48 |
| Volume | G_VOLUME | 22.19 |
| Intensive | — | 0 |

### 2. The Circle (R · sin) — where the phase puts you

This is the ARA character of the system — the **type** of process, not the size of it.

The circle has a radius R, and R depends on which phase the system lives in:

- **Phase 1 — Accumulators** (R = 1.354): Clock-tick systems. Store, release, repeat. Seeds packing, caves breathing, eyes scanning.
- **Phase 2 — Engines** (R ≈ φ ≈ 1.626): Sustained converters. Muscles working, ocean currents flowing, eating/digesting.
- **Phase 3 — Discharge** (R = 1.914): Build-and-snap systems. Lightning, sneezing, pimples, volcanoes, crying.

The scale gap feeds into the circle as an angle. The sin wave reads off that angle and tells you: given how far apart these systems are on the circle, how much does the wave push the prediction up or down?

**R · sin(G_phase / R)** is literally: "the radius of this phase's circle, multiplied by the wave height at this angle."

This is the **fibre** part. The T³ circles riding on top of the sphere.

## The full formula

**Predicted gap (in powers of ten) = valley + wave**

```
Δlog = G + R · sin(G_phase / R)
```

Then:

```
predicted value = known value × 10^(Δlog)
```

### For intensive quantities (fraction, speed, density, duration):

G = 0, so:

**Δlog = R · sin(G_phase / R)**

You're only riding the circle. The valley is flat.

### For extensive quantities (count, length, volume):

G = dimensional gap, so:

**Δlog = G + R · sin(G_phase / R)**

You cross the full valley AND ride the circle.

## The number of circles

When the scale gap is large, the signal wraps around the circle multiple times before arriving. The number of full revolutions is:

**n = G / (2πR)**

Each revolution covers 2πR decades of scale. This is "the valley between ARAARA" — each crossing of the shared boundary A is one revolution of the circle.

## When it works, when it doesn't

**Works:** When the same physics operates at both scales. Granular mechanics (seeds→pebbles), fluid dynamics (ocean→atmosphere), acoustics (thunder→sneeze), growth geometry (ants→trees).

**Fails:** When the relational role matches but the mechanism is different. Population growth vs cell division — same *story*, different *physics*. The circle can't translate between mechanisms it doesn't connect.

**Zero correction:** When properties are set by local physics that doesn't scale at all. Caves and sinuses both have ~95% humidity because enclosed air voids just do that at any size. The formula predicts a correction, but reality says there is none. The model should give G = 0 AND phase = 0 for these — they're the same point on the manifold.

## Results so far

Across 55 blind predictions (Scripts 148–155):

- **24/55 within one order of magnitude** (44%)
- **p = 3.0 × 10⁻⁹** against random chance
- Best hits: ant→tree lifespan (within 2×), eye→galaxy disc ratio (within 1.1×), muscles→tectonic plates count (within 1.4×)

The formula lives on the T³ × S² manifold — three circles (the fibre) riding on the sphere (the base space). Phase picks the circle. Scale picks where on the sphere. The prediction is where those two coordinates meet.
