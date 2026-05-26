# ARA Rotating Terrain Slice Result

**Date:** 2026-05-26

This test responds to the correction that the contact-triangle script was still matching current feature states rather than actually rotating terrain under a fixed water slice.

The model now tests:

```text
fixed water slice at origin t
-> estimate which terrain patch rotates under it by t+h
-> look up older terrain patches at that arriving coordinate
-> read the historical level/direction
```

It tests two lookup styles:

```text
surface lookup:
  match estimated arriving patch to older origin-surface patches
  read candidate.current as terrain height

arrival lookup:
  match estimated arriving patch to older completed target patches
  read candidate.actual as terrain height
```

## Files

- `TheFormula/ara_rotating_terrain_slice_model.py`
- `TheFormula/ara_rotating_terrain_slice_result.json`
- `TheFormula/ara_rotating_terrain_slice_result.js`
- `TheFormula/ara_rotating_terrain_slice_viz.html`

## Leakage Guard

This is strict-causal:

- Current rows estimate the arriving `t+h` patch only from current-origin sphere/wobble/spin values and the known horizon.
- Candidate target patches are used only when candidate target `s+h` is before the current origin `t`.
- Candidate origin-surface patches are used only when candidate origin is before current origin `t`.
- No decoder, lag ridge, future geometry oracle, smoothing, or visual shift is used.
- Non-ready rows fall back to persistence.

## Key Result

Across 6/12/24 months, all rows:

| Model | MAE | Corr | Turn | Direction | Large-direction |
|---|---:|---:|---:|---:|---:|
| Persistence | 0.896 | +0.003 | 0.007 | 0.000 | 0.000 |
| Wobble surface analog | 0.608 | +0.218 | 0.773 | 0.779 | 0.834 |
| Sphere nested-2 level | 0.762 | -0.008 | 0.336 | 0.335 | 0.346 |
| Surface wobble level | 0.768 | -0.009 | 0.368 | 0.371 | 0.386 |
| Surface parity level | 0.771 | -0.006 | 0.357 | 0.360 | 0.382 |
| Arrival parity level | 0.778 | -0.028 | 0.336 | 0.335 | 0.341 |
| Arrival parity delta | 0.924 | -0.006 | 0.168 | 0.166 | 0.148 |

Ready-only 6/12/24 focus:

| Model | MAE | Corr | Turn | Direction | Large-direction |
|---|---:|---:|---:|---:|---:|
| Persistence | 0.970 | -0.013 | 0.009 | 0.000 | 0.000 |
| Wobble surface analog | 0.596 | +0.335 | 0.776 | 0.785 | 0.838 |
| Sphere nested-2 level | 0.649 | +0.061 | 0.754 | 0.762 | 0.799 |
| Surface clock level | 0.680 | -0.003 | 0.748 | 0.757 | 0.810 |
| Surface wobble level | 0.675 | +0.017 | 0.756 | 0.764 | 0.810 |
| Surface parity level | 0.684 | +0.008 | 0.739 | 0.747 | 0.811 |
| Arrival parity level | 0.686 | -0.066 | 0.753 | 0.761 | 0.787 |

## Interpretation

This is a better mechanical version of the user's idea than the contact-triangle test, but it still does not beat the current terrain/wobble lookup.

The positive read:

```text
The rotating-surface lookup preserves direction on ready rows.
Surface wobble reaches ready direction 0.764 and large-direction 0.810.
That is close to sphere_nested2 large-direction 0.799 and wobble large-direction 0.838.
```

The negative read:

```text
The hand-built rotation estimate loses level/correlation.
Surface wobble MAE 0.675 is worse than sphere_nested2 MAE 0.649
and worse than wobble surface MAE 0.596.
```

So the strict conclusion is:

```text
The fixed-slice / rotating-terrain framing is now testable,
but this first hand-coded rotation operator is not accurate enough.
```

## Physical Read

The good sign is that the rotating-surface version does not collapse; it keeps high turn/direction skill on the ready subset. That means the arriving-terrain picture is not nonsense.

The problem is that we are not estimating the arriving coordinate precisely enough. The terrain/wobble analog still works better because it directly matches the current local terrain signature. The rotating model asks a harder question:

```text
Where will the terrain patch be after the sphere rolls?
```

Right now that roll is hand-coded from wobble, lower spin, parity, and upper gate. The numbers say that rule is only approximate.

## Next Improvement

The next clean step is not another hand-tuned rotation. It should learn or infer the rotation operator from past terrain motion while staying causal:

```text
past origin patch -> past next patch
fit rotation/transport on completed history only
apply learned rotation to current patch
then sample the historical surface map
```

That would preserve the correct topology:

```text
fixed slice
moving terrain
lower layers inducing roll
upper terrain arriving slowly
```

but stop pretending we can guess the sphere's 3D roll from one hand-built formula.

