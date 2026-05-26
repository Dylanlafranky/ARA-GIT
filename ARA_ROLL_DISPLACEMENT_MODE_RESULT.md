# ARA Roll Displacement Mode Result

**Date:** 2026-05-26

This test addresses the persistence/delay problem in the fractal terrain reader.

The previous reader could interpret the filled terrain, but its future-pose step still landed too close to the current patch. This version learns completed roll displacements instead of predicting the final coordinate directly:

```text
current sphere address
-> classify historical roll mode from completed past cases
-> apply same-mode roll displacement
-> read fractal terrain at the advanced coordinate
```

## Files

- `TheFormula/ara_roll_displacement_mode_predictor.py`
- `TheFormula/ara_roll_displacement_mode_predictor_result.json`
- `TheFormula/ara_roll_displacement_mode_predictor_result.js`
- `TheFormula/ara_roll_displacement_mode_viz.html`

## Leakage Guard

This is strict-causal:

- Candidate roll displacements are eligible only when the candidate target is before current origin `t`.
- The model predicts and applies roll displacement components, not final future native values.
- Mode locking prevents averaging incompatible roll directions before applying displacement.
- The terrain read is deterministic fractal ARA terrain.
- No lag ridge, native-value decoder, future geometry oracle, smoothing, or visual shift is used.
- Non-ready rows fall back to persistence.

## Key Result

Ready-only 6/12/24 focus:

| Model | MAE | Corr | Direction | Amplitude ratio |
|---|---:|---:|---:|---:|
| Wobble surface analog | 0.557 | +0.376 | 0.824 | 0.764 |
| Raw address top-1 | 0.600 | +0.361 | 0.807 | 0.841 |
| Fractal phi force | 0.623 | +0.326 | 0.778 | 0.831 |
| Mode top-1 fractal | 0.919 | +0.082 | 0.660 | 0.998 |
| Mode weighted fractal | 0.919 | +0.114 | 0.663 | 0.961 |
| Mode top-1 arrival | 1.063 | +0.063 | 0.660 | 1.163 |

## Interpretation

This test cleanly separates two failure modes.

The previous fractal reader was too current-like:

```text
fractal_phi_force amplitude ratio: 0.831
```

The displacement-mode reader is not too current-like:

```text
mode_top1_fractal amplitude ratio: 0.998
```

So the delay/persistence problem can be removed by applying explicit roll displacement. But the coarse mode classifier picks the wrong route too often:

```text
mode_top1_fractal MAE 0.919, corr +0.082
raw top-1          MAE 0.600, corr +0.361
```

The useful conclusion is not that displacement mode solved the predictor. It did not. The useful conclusion is narrower:

```text
Under-moving is one problem.
Wrong roll-mode selection is the next problem.
```

## Physical Read

This matches the sphere intuition:

```text
If the sphere barely rolls, the forecast looks delayed/persistent.
If the sphere rolls the wrong way, amplitude returns but the path is wrong.
```

The first problem was conservative coordinate prediction. This test fixes that mechanically. The second problem is choosing the correct contact/roll mode.

## Next Step

The next model should keep explicit displacement, but improve mode selection:

```text
1. Use raw top-1/wobble terrain as the route teacher.
2. Predict roll mode as a risk/classification problem, not a nearest-neighbour vote.
3. Let contact parity, spillover, and boundary pressure select among roll modes.
4. Only then apply the displacement and read the fractal terrain.
```

That keeps the insight:

```text
prediction needs an address advancer
```

without pretending the first coarse roll-mode selector is good enough.
