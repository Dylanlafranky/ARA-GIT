# ARA Lower-Sphere Roll Selector Result

**Date:** 2026-05-26

This test follows the correction:

```text
the lower spheres determine the roll and direction of the sphere being measured
```

The previous roll-displacement test restored amplitude, but selected roll modes from broad state similarity. This version selects completed roll displacements using lower-sphere spin/torque patterns first, then applies that displacement and reads deterministic fractal ARA terrain.

## Files

- `TheFormula/ara_lower_sphere_roll_selector.py`
- `TheFormula/ara_lower_sphere_roll_selector_result.json`
- `TheFormula/ara_lower_sphere_roll_selector_result.js`
- `TheFormula/ara_lower_sphere_roll_selector_viz.html`

## Selector Variants

```text
lower_core_top1:
  nearest completed lower-spin pattern supplies roll displacement directly

lower_core_mode_top1:
  lower-spin patterns vote a coarse mode, then nearest displacement inside that mode is used

lower_gate_top1:
  lower_core plus raw lower-spin torque/pressure/topology-arrival gates

lower_gate_mode_top1:
  lower_gate version of coarse mode selection

lower_gate_weighted:
  weighted same-mode displacement after lower_gate mode selection
```

The important distinction is top-1 lower-spin displacement versus coarse mode voting.

## Leakage Guard

This is strict-causal:

- Roll mode selection uses only current-origin lower-sphere spin/torque features.
- Candidate roll displacements are eligible only when candidate target is before current origin `t`.
- The selected displacement is applied before deterministic fractal terrain reading.
- No lag ridge, native-value decoder, future geometry oracle, smoothing, or visual shift is used.
- Non-ready rows fall back to persistence.

## Key Result

Ready-only 6/12/24 focus:

| Model | MAE | Corr | Direction | Amplitude ratio |
|---|---:|---:|---:|---:|
| Wobble surface analog | 0.557 | +0.376 | 0.824 | 0.764 |
| Raw address top-1 | 0.600 | +0.361 | 0.807 | 0.841 |
| Fractal phi force | 0.623 | +0.326 | 0.778 | 0.831 |
| Previous broad mode top-1 | 0.919 | +0.082 | 0.660 | 0.998 |
| Lower core top-1 | 0.744 | +0.194 | 0.753 | 0.929 |
| Lower gate top-1 | 0.812 | +0.122 | 0.730 | 1.000 |
| Lower core mode top-1 | 0.951 | +0.007 | 0.648 | 1.107 |

## Interpretation

The correction is supported, but not fully solved.

Compared with the previous broad-state roll selector:

```text
mode_top1_fractal:
  MAE 0.919, corr +0.082, direction 0.660, amplitude 0.998

lower_core_top1:
  MAE 0.744, corr +0.194, direction 0.753, amplitude 0.929
```

So lower-sphere information is a much better roll selector than generic state similarity. It keeps most of the restored amplitude while improving the route.

The mode-vote versions are worse:

```text
lower_core_mode_top1:
  MAE 0.951, corr +0.007, direction 0.648
```

That means the lower-sphere pattern should probably select the displacement directly, not via an overcoarse mode bin.

## Strict Read

This does not beat raw top-1 or wobble yet:

```text
raw top-1:
  MAE 0.600, corr +0.361, direction 0.807

lower core top-1:
  MAE 0.744, corr +0.194, direction 0.753
```

But it clearly improves the failed displacement branch. The bottleneck is now narrower:

```text
lower spheres are the right place to choose roll,
but the current lower-spin feature/address match is still too crude.
```

## Next Step

The next version should not classify broad modes. It should learn a lower-sphere contact map:

```text
lower spin gear mesh
-> roll axis / direction / depth
-> raw top-1 terrain address
-> fractal terrain packet as gate/explanation
```

The best current architecture is:

```text
lower spheres select roll displacement
raw top-1 reads terrain
fractal ARA bands explain/gate the basin
wobble checks the local contact patch
```
