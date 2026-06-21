# ARA Wobble Terrain Arrival Result

**Date:** 2026-05-25

This test follows the correction that the water slice is not just seeing the same terrain come back around a flat circle. The current sphere wobbles in a local 3-axis frame, and the lower subsystems feeding it also have their own wobble.

## Model

The local terrain frame is mapped as:

```text
x = downstream / topology-arrival tilt
y = lateral bank / ridge-channel tilt
z = vertical sea/backpressure / lift-sink tilt
torsion = coupled lower-spin / sea twist of the local surface
```

The analog search matches:

```text
current 3-axis terrain position
recent 3m/6m wobble velocity
local curvature
lower subsystem spin from NINO, anti-phase SOI, PDO
spin torsion and boundary/turbulence state
```

## Leakage Guard

For origin `t` and horizon `h`:

- every wobble feature at `t` uses only raw samples `<= t`.
- older analog states are eligible only when their own future target `s+h` is already before the current origin `t`.
- no decoder, lag ridge, future geometry oracle, smoothing, z-score transform, or visual shift is used for scores.

## Files

- `TheFormula/ara_wobble_terrain_arrival_predictor.py`
- `TheFormula/ara_wobble_terrain_arrival_result.json`
- `TheFormula/ara_wobble_terrain_arrival_result.js`
- `TheFormula/ara_wobble_terrain_arrival_viz.html`

## Main Result

Across 6/12/24 months:

| Model | MAE | Corr | Turn acc | Transition MAE |
|---|---:|---:|---:|---:|
| `persistence` | `0.896` | `+0.003` | `0.007` | `1.187` |
| `terrain_level_analog` | `0.614` | `+0.212` | `0.760` | `0.691` |
| `wobble_level_analog` | `0.611` | `+0.209` | `0.780` | `0.659` |
| `wobble_delta_analog` | `0.803` | `+0.003` | `0.682` | `0.918` |
| `wobble_surface_analog` | `0.608` | `+0.218` | `0.773` | `0.658` |

The wobble-aware branches improve transition-window MAE and turn accuracy versus the simple terrain baseline in this run, but they do not improve correlation enough yet. This is consistent with wobble being a real contact/turn structure while the current distance metric is still over-constraining the analogue search.

## Interpretation

The corrected picture is:

```text
The formula maps the local terrain being experienced by the water slice.
The terrain returns because the sphere rotates.
But the returning terrain is altered by 3-axis wobble, lower-subsystem wobble, and surface erosion.
```

The first wobble implementation supports that idea mainly in the boundary/turn channel:

```text
simple terrain level = better broad shape/correlation
wobble surface = better transition contact and turn behaviour
```

The next fair step is a constrained blend:

```text
broad returning terrain level
+ bounded wobble correction only near transition/contact windows
```

That would treat wobble as a contact/terrain-arrival modifier rather than letting it dominate the whole analog distance.
