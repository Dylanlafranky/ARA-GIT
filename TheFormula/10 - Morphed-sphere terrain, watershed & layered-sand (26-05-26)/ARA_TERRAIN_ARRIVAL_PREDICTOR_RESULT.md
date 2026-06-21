# ARA Terrain Arrival Predictor Result

**Date:** 2026-05-25

This test follows the phase-delay audit result:

```text
The lower-spin raw watershed formula reconstructs the current/origin terrain slice well,
but it does not by itself advance that terrain to the forecast date.
```

So this script treats the lower-spin formula as a **terrain extractor**, not a decoder. It then asks whether older, already-completed terrain states can tell us what the terrain looks like when it arrives at the future horizon.

## Files

- `TheFormula/ara_terrain_arrival_predictor.py`
- `TheFormula/ara_terrain_arrival_predictor_result.json`
- `TheFormula/ara_terrain_arrival_predictor_result.js`
- `TheFormula/ara_terrain_arrival_predictor_viz.html`

## Leakage Guard

For origin `t` and horizon `h`:

- every terrain feature at `t` uses only raw samples `<= t`.
- analog neighbors are eligible only when their own target `s+h` is already before the current origin `t`.
- no decoder, lag ridge, future geometry oracle, smoothing, z-score transform, or visual shift is used for scores.
- the visualizer is target-date aligned only.

The central causal rule is:

```text
current raw data <= t
-> lower-spin terrain signature S(t)
-> search older completed signatures S(s), where s+h < t
-> average what those older terrains looked like at s+h
-> forecast t+h
```

## Models Tested

| Model | Meaning |
|---|---|
| `persistence` | current NINO value held forward |
| `lower_spin_formula` | current lower-spin terrain slice pushed by the fixed symbolic flow |
| `terrain_delta_analog` | current value plus weighted future deltas from older similar terrain signatures |
| `terrain_level_analog` | weighted future level reached by older similar terrain signatures |
| `terrain_erosion_analog` | delta analog plus fixed symbolic correction for current-vs-neighbor terrain flow |

## Main Result

Across 6/12/24 months:

| Model | MAE | Corr | Turn acc | Transition MAE |
|---|---:|---:|---:|---:|
| `persistence` | `0.896` | `+0.003` | `0.007` | `1.187` |
| `lower_spin_formula` | `0.937` | `+0.024` | `0.397` | `1.230` |
| `terrain_delta_analog` | `0.690` | `+0.079` | `0.724` | `0.803` |
| `terrain_level_analog` | `0.602` | `+0.275` | `0.769` | `0.674` |
| `terrain_erosion_analog` | `0.689` | `+0.082` | `0.727` | `0.802` |

This is the first no-decoder terrain-arrival branch in this series that cleanly beats persistence across the focus horizons.

## Horizon Detail

`terrain_level_analog` by horizon:

| Horizon | MAE | Corr | Turn acc | Transition MAE |
|---:|---:|---:|---:|---:|
| 3m | `0.431` | `+0.758` | `0.677` | `0.473` |
| 6m | `0.561` | `+0.474` | `0.745` | `0.636` |
| 12m | `0.614` | `+0.199` | `0.792` | `0.679` |
| 18m | `0.639` | `+0.131` | `0.777` | `0.719` |
| 24m | `0.631` | `+0.152` | `0.772` | `0.708` |

## Interpretation

This supports the topology reading more strongly than the direct fixed formula:

```text
The formula draws the terrain we are experiencing now.
The arrival predictor asks which older terrains resemble this one,
then uses their already-observed future terrain as the returning surface.
```

In plain terms: lag is effective because a similar surface keeps coming back around. The ARA terrain signature improves on crude persistence by choosing more similar returning surfaces instead of simply assuming the current value persists.

The best branch here is `terrain_level_analog`, not the symbolic erosion correction. That suggests the immediate useful object is the **returned terrain level** from similar completed states, while the current erosion/work correction is still under-specified.

## Remaining Controls

This is a good result, but it still needs controls:

```text
ARA terrain signature analog
vs raw finite-difference analog without ARA/ridge/phi terms
vs shuffled terrain signature
vs wrong-rung terrain signature
vs simple seasonal/ENSO-phase analog
```

The key question now is whether the gain comes specifically from the ARA lower-spin terrain signature, or from generic analog recurrence on raw ENSO data.
