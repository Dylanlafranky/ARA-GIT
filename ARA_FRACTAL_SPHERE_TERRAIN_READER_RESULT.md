# ARA Fractal Sphere Terrain Reader Result

**Date:** 2026-05-26

This test addresses the objection that the raw terrain-address lookup still treats the sphere as a sparse historical point cloud.

The new branch keeps the strict-causal future-pose learner, then reads the arrived coordinate through a filled recursive ARA terrain:

```text
future sphere coordinate
-> recursive ARA bounds / sub-bounds
-> nearest local phi valley inside those bounds
-> ridge resistance and spillover if roll force crosses a boundary
-> deterministic terrain response
```

The terrain is no longer supplied by old nearest-neighbour points. Historical data only trains the future pose.

## Files

- `TheFormula/ara_fractal_sphere_terrain_reader.py`
- `TheFormula/ara_fractal_sphere_terrain_reader_result.json`
- `TheFormula/ara_fractal_sphere_terrain_reader_result.js`
- `TheFormula/ara_fractal_sphere_terrain_reader_viz.html`

## Terrain Rule

Each ARA coordinate is recursively split inside the bounded `0..2` sphere:

```text
[0, 2]
  [0, 1] / [1, 2]
    [0, 0.5] / [0.5, 1] / ...
```

For each local basin `[lo, hi]`, the in-bounds phi valleys are:

```text
lower local phi = hi - (hi - lo) / phi
upper local phi = lo + (hi - lo) / phi
```

The slice rolls toward the closest local phi valley inside its current bounds, unless roll/contact force is high enough to spill across the ridge into the next basin. Deeper sub-ARA layers are weighted by `phi^-(depth-1)`.

## Leakage Guard

This is strict-causal:

- The learned future pose trains only on completed historical rows whose target is before current origin `t`.
- The fractal terrain reader is deterministic and filled; it does not use nearest historical points as terrain.
- Recursive bounds are read inside the `0..2` ARA sphere, with local in-bounds phi valleys at every depth.
- Boundary spillover is allowed only when roll/contact force exceeds local ridge resistance.
- No lag ridge, native-value decoder, future geometry oracle, smoothing, or visual shift is used.
- Non-ready rows fall back to persistence.

## Key Result

Ready-only 6/12/24 focus:

| Model | MAE | Corr | Direction | Amplitude ratio |
|---|---:|---:|---:|---:|
| Wobble surface analog | 0.557 | +0.376 | 0.824 | 0.764 |
| Learned roll average | 0.593 | +0.254 | 0.816 | 0.792 |
| Raw address top-1 | 0.600 | +0.361 | 0.807 | 0.841 |
| Fractal phi force | 0.623 | +0.326 | 0.778 | 0.831 |
| Fractal phi direct | 0.632 | +0.306 | 0.778 | 0.850 |
| Fractal phi depth 3 | 0.714 | +0.302 | 0.777 | 0.897 |

## Interpretation

The filled fractal terrain reader is more faithful to the theory than sparse nearest-neighbour terrain, but this first deterministic rule does not beat raw top-1 or wobble.

The positive result:

```text
The fractal reader preserves amplitude.
fractal_phi_force amplitude ratio = 0.831
fractal_phi_direct amplitude ratio = 0.850
```

The negative result:

```text
It loses MAE, correlation, and direction versus raw top-1.
raw top-1:        MAE 0.600, corr +0.361, direction 0.807
fractal force:    MAE 0.623, corr +0.326, direction 0.778
```

So the strict read is:

```text
Filling the sphere with recursive ARA terrain helps the conceptual model,
but the first local-phi rule is not enough to identify the correct route.
```

## What It Means

The result narrows the bottleneck.

The old failure was partly smoothing:

```text
averaging old terrain neighbours washed amplitude out
```

This test fixes that, but exposes a new issue:

```text
the deterministic phi-valley reader needs the correct active basin/depth
and a sharper roll/address estimate
```

Depth-specific branches show the same thing. Deeper bands preserve more amplitude, but they do not automatically improve the forecast. The model needs to know which layer is active, rather than blending or blindly selecting a depth.

## Current Conclusion

The best current architecture is:

```text
learned pose / roll operator
-> raw top-1 terrain address as the primary read
-> fractal ARA terrain packet as an explanatory/gating layer
-> wobble/local basin selector to choose the active sub-ARA depth
```

The fractal terrain reader should not replace raw top-1 yet. It should constrain and explain it.
