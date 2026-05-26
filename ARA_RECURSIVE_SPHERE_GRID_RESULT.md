# ARA Recursive Sphere Grid Result

Run date: 2026-05-26

## Purpose

Correct the sphere-atlas predictor one more step:

```text
Do not use the layered-sand "now formula" as the predictor.
Use the measured sphere coordinate itself.
```

Prediction rule:

```text
current measured sphere coordinate
-> deterministic rotation to the future longitude
-> if a close past recorded coordinate exists, read that raw point
-> otherwise read a filled recursive ARA/sub-ARA/sub-sub-ARA grid
```

Script:

```bash
python TheFormula/ara_recursive_sphere_grid_predictor.py
```

Visualizer:

```text
TheFormula/ara_recursive_sphere_grid_viz.html
```

## Grid Definition

The recursive terrain grid follows the user's diagram:

- whole-axis ARA range is `0..2`;
- root phi valley is `phi = 1.618`;
- root anti-phi counterline is `2 - phi = 0.382`;
- midpoint and band boundaries are black lines;
- every sub-band receives its own local phi and anti-phi lines;
- each deeper level is weighted by `1 / phi^(depth - 1)`;
- energy/water moves toward the weighted local phi valley unless ridge/counter pressure brakes it.

This means there is no blank space:

```text
coordinate -> ARA band -> sub-ARA -> sub-sub-ARA -> deeper address
```

If the historical atlas has no close raw coordinate at the arrived address, the recursive grid still returns terrain.

## Leakage Guard

- No layered-sand `Formula` or `Formula_Adjustable` is used.
- No future-origin row is read.
- No future target value is read until scoring.
- Past recorded coordinate lookup is raw top-1 only, with no averaging.
- If the recorded coordinate is not close enough, the filled recursive grid is used instead.

## Main Results

| Horizon | Model | MAE | Corr |
|---:|---|---:|---:|
| 3m | persistence | 0.478 | +0.743 |
| 3m | grid phi water | **0.469** | **+0.744** |
| 6m | persistence | 0.737 | +0.351 |
| 6m | grid phi water | **0.706** | **+0.355** |
| 12m | persistence | 0.925 | +0.067 |
| 12m | grid phi water | **0.873** | -0.079 |
| 18m | persistence | 1.010 | -0.145 |
| 18m | grid phi water | **0.963** | -0.152 |
| 24m | persistence | 1.027 | -0.274 |
| 24m | recorded top-1 any | **0.956** | -0.343 |

The recursive grid improves MAE versus persistence at 3, 6, 12, and 18 months, but it does not solve correlation/route timing at 12-24 months.

## Interpretation

This is now much closer to the requested mechanism:

```text
The measured sphere has coordinates.
Known historical points are useful when the sphere revisits them.
Unknown coordinates are not empty; they are recursively filled ARA terrain.
```

The result is better than the sparse fixed-atlas reader at short horizons and partially better on MAE, but the main future-route problem remains:

```text
we can read terrain at a coordinate,
but the rotation/arrival address is still too simple.
```

The next correction should keep this recursive grid and replace only the rotation rule:

```text
current coordinate
-> lower-sphere roll / wobble / pressure determines future coordinate
-> recursive grid reads terrain there
```

The key is not to go back to future-origin shifting or current-wave remapping.

## Output Files

- `TheFormula/ara_recursive_sphere_grid_predictor.py`
- `TheFormula/ara_recursive_sphere_grid_result.json`
- `TheFormula/ara_recursive_sphere_grid_result.js`
- `TheFormula/ara_recursive_sphere_grid_viz.html`
