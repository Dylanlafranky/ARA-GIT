# ARA Fixed Sphere Atlas Rotation Result

Run date: 2026-05-26

## Purpose

Test the intended sphere-terrain mechanism without the future-origin leakage:

```text
known current/cutoff pose
-> rotate to a future sphere address
-> read the fixed atlas terrain at that address
-> score against truth afterward
```

Script:

```bash
python TheFormula/ara_fixed_sphere_atlas_rotation_predictor.py
```

Visualizer:

```text
TheFormula/ara_fixed_sphere_atlas_rotation_viz.html
```

## Leakage Guard

- The atlas reader only sees terrain samples dated at or before the prediction origin/cutoff.
- The primary terrain read is raw top-1 nearest atlas address, not averaged neighbours.
- The rolling-origin branch may use the current observed state at the forecast origin, but not any future-origin row.
- The closed-cutoff branch seeds once at the cutoff and reads only the pre-cutoff atlas.
- Truth is used only after prediction for scoring and plotting.

## Important Atlas Limitation

The existing `ara_sphere_atlas_data.json` is not a dense recursive sphere.

It is a mapped point-cloud of already visited historical terrain points:

```text
date -> ARA latitude, phase longitude, wobble displacement, observed value
```

So this test can do a valid fixed-atlas lookup, but it cannot yet do the full requested operation:

```text
longitude/latitude -> ARA band -> sub-ARA -> sub-sub-ARA -> filled terrain value everywhere
```

When the rotated future address lands between known atlas points, this script reads the nearest old visited point. That is valid and non-leaky, but it is not the full dense ARA globe.

## Main Rolling-Origin Results

| Horizon | Model | MAE | Corr |
|---:|---|---:|---:|
| 3m | persistence | 0.478 | +0.743 |
| 3m | formula pose -> atlas top-1 | **0.470** | +0.740 |
| 6m | persistence | **0.737** | **+0.351** |
| 6m | formula pose -> atlas top-1 | 0.773 | +0.251 |
| 12m | persistence | 0.925 | +0.067 |
| 12m | clock wobble -> atlas top-1 | **0.879** | -0.084 |
| 18m | persistence | 1.010 | -0.145 |
| 18m | clock wobble -> atlas top-1 | **0.934** | -0.125 |
| 24m | persistence | 1.027 | -0.274 |
| 24m | formula pose -> atlas top-1 | **0.948** | -0.308 |

The atlas read sometimes improves MAE at longer horizons, but it does not recover the high shifted-line correlation.

## Closed-Cutoff Results

All post-cutoff months through 2025-12:

| Cutoff | Best atlas branch by MAE | MAE | Corr | Persistence MAE |
|---|---|---:|---:|---:|
| 2010 | formula pose -> atlas top-1 | **1.237** | -0.276 | 1.505 |
| 2015 | clock flat -> atlas top-1 | 0.891 | -0.236 | **0.863** |
| 2017 | formula pose -> atlas top-1 | 0.653 | -0.119 | **0.630** |
| 2020 | manual pose -> atlas top-1 | **0.790** | -0.200 | 1.023 |

This confirms the earlier lesson: once future-origin rows are removed, the perfect terrain shape is gone. The fixed atlas can sometimes beat a flat cutoff persistence on MAE, but it is not yet a solved predictor.

## Interpretation

This test is the first clean implementation of the exact atlas-rotation idea using the atlas we already had.

The result is not futile, but it is clarifying:

```text
The prior shifted visual match supports "current terrain can be mapped strongly."
This fixed-atlas test shows the current atlas is not dense enough, and the roll/pose operator is not precise enough, to forecast that terrain cleanly.
```

The existing sphere atlas is good as a visual and diagnostic terrain memory. It is not yet the dense ARA/sub-ARA/sub-sub-ARA surface the theory requires.

## Next Required Correction

Do not build another unrelated predictor. Extend the current atlas into two explicit layers:

```text
1. Observed terrain point-cloud:
   raw historical visited coordinates and observed values.

2. Filled recursive terrain grid:
   every coordinate has ARA band, sub-ARA address, local phi valley,
   ridge distance, spillover direction, and boundary pressure.
```

Then the predictor should:

```text
current pose
-> lower-sphere roll vector
-> future coordinate
-> read dense recursive terrain metadata
-> only use historical raw points to calibrate value response, not to define whether terrain exists
```

That is the version matching the intended globe model.

## Output Files

- `TheFormula/ara_fixed_sphere_atlas_rotation_predictor.py`
- `TheFormula/ara_fixed_sphere_atlas_rotation_result.json`
- `TheFormula/ara_fixed_sphere_atlas_rotation_result.js`
- `TheFormula/ara_fixed_sphere_atlas_rotation_viz.html`
