# ARA Sphere Orientation Roll Result

**Date:** 2026-05-26

This test implements the clarified Earth analogy:

```text
the terrain map is mostly fixed on the sphere
the local water/signal slice is the reading point
prediction means estimating how the sphere will roll/wobble
then sampling the fixed surface patch that arrives under the slice
```

Unlike the previous rotating-terrain script, this version represents pose as an explicit 3D surface vector and roll as a 3D angular vector.

## Files

- `TheFormula/ara_sphere_orientation_roll_predictor.py`
- `TheFormula/ara_sphere_orientation_roll_result.json`
- `TheFormula/ara_sphere_orientation_roll_result.js`
- `TheFormula/ara_sphere_orientation_roll_viz.html`

## Tested Roll Branches

```text
roll_clock_surface:
  home-cycle rotation around the ARA pole axis

roll_wobble_surface:
  clock roll plus local forward/lateral/twist angular components

roll_contact_surface:
  wobble roll plus lower-drive, upper-gate, and parity contact components

roll_learned_surface:
  causal learned map from current pose features to future surface vector,
  then fixed-surface terrain lookup
```

The learned branch is still not a native-value decoder. It predicts future orientation/patch only, then samples the historical fixed terrain surface.

## Leakage Guard

This is strict-causal:

- Hand-built roll variants use only current-origin sphere/wobble/spin values and horizon.
- The learned orientation operator trains only on completed historical rows whose target is before current origin `t`.
- The fixed terrain lookup uses only historical origin patches before current origin `t`.
- No lag ridge, native-value decoder, future geometry oracle, smoothing, or visual shift is used.
- Non-ready rows fall back to persistence.

## Key Result

Across 6/12/24 months, all rows:

| Model | MAE | Corr | Turn | Direction | Large-direction |
|---|---:|---:|---:|---:|---:|
| Persistence | 0.896 | +0.003 | 0.007 | 0.000 | 0.000 |
| Wobble surface analog | 0.608 | +0.218 | 0.773 | 0.779 | 0.834 |
| Sphere nested-2 level | 0.762 | -0.008 | 0.336 | 0.335 | 0.346 |
| Roll clock surface | 0.790 | -0.029 | 0.347 | 0.350 | 0.371 |
| Roll contact surface | 0.788 | -0.026 | 0.354 | 0.357 | 0.376 |
| Roll learned surface | 0.792 | +0.032 | 0.293 | 0.292 | 0.290 |

All-row scoring is conservative because the learned branch needs enough completed roll history and otherwise falls back to persistence.

Ready-only 6/12/24 focus:

| Model | MAE | Corr | Turn | Direction | Large-direction |
|---|---:|---:|---:|---:|---:|
| Persistence | 0.898 | -0.034 | 0.012 | 0.000 | 0.000 |
| Terrain level analog | 0.590 | +0.272 | 0.775 | 0.785 | 0.850 |
| Wobble surface analog | 0.557 | +0.376 | 0.813 | 0.824 | 0.883 |
| Sphere nested-2 level | 0.601 | +0.125 | 0.795 | 0.806 | 0.835 |
| Roll clock surface | 0.680 | -0.081 | 0.763 | 0.773 | 0.840 |
| Roll contact surface | 0.672 | -0.070 | 0.771 | 0.781 | 0.840 |
| Roll learned surface | 0.593 | +0.254 | 0.805 | 0.816 | 0.870 |

## Interpretation

This is the strongest support so far for the clarified orientation model.

The hand-built roll vectors are still too crude. They preserve direction but lose MAE/correlation.

The learned orientation operator is different:

```text
roll_learned_surface beats sphere_nested2_level on ready rows:
  MAE:       0.593 vs 0.601
  corr:     +0.254 vs +0.125
  direction 0.816 vs 0.806
  large-dir 0.870 vs 0.835
```

It still does not beat the current best wobble terrain branch:

```text
wobble_surface_analog:
  MAE 0.557
  corr +0.376
  direction 0.824
  large-dir 0.883
```

So the strict read is:

```text
Explicit sphere orientation is useful.
Learning the roll/pose operator works better than hand-coding it.
But the current learned orientation map is not yet better than direct wobble-terrain matching.
```

## Physical Read

This supports the Earth analogy more than the earlier contact-triangle test:

```text
fixed terrain map + future sphere pose + surface lookup
```

is a better model than:

```text
current feature state + synthetic contact triangle + averaged future values
```

The best current interpretation is:

- Wobble terrain is still the strongest direct local route measurement.
- Sphere orientation learning gives a real future-pose prior.
- The next useful step is to combine them by using learned orientation to choose the arriving terrain patch, then use wobble terrain as the local read of that patch.

## Next Improvement

Do not replace wobble with orientation. Combine them:

```text
1. Learn future orientation from completed past roll.
2. Use that predicted pose to select candidate surface patches.
3. Inside those patches, use wobble/terrain similarity to choose the local basin.
4. Keep contact parity as a gate, not as a full distance metric.
```

That would match the physical story:

```text
the sphere tells us what map area arrives
the wobble tells us what local terrain inside that area is doing
contact parity tells us whether the roll is clean or slipping
```

