# ARA Layered Sand Shape/Timing Diagnostic Result

Run date: 2026-05-26

## Purpose

Test the user's observation:

> Formula itself, the shape is very good, it is just offset.

This diagnostic deliberately does not start with MAE. It checks:

1. Best-lag cross-correlation.
2. Affine remap: `actual ~= a * formula + b`.
3. Peak/trough sequence matching.
4. Phase correction only: freeze constants and allow one global origin-step shift.

Script:

```bash
python TheFormula/ara_layered_sand_shape_timing_diagnostic.py
```

Lag convention:

```text
positive shift = formula is late
positive shift of +8 origin steps = visually shift formula left by 24 months
```

## Best-Lag Cross-Correlation

### Fixed `Formula`

Across 6/12/24-month focus rows:

| Test | Shift | Corr | MAE |
|---|---:|---:|---:|
| zero shift | 0 steps / 0m | +0.020 | 0.876 |
| best shift | +8 steps / +24m | +0.545 | 0.517 |

Holdout 2017+:

| Test | Shift | Corr | MAE | Direction |
|---|---:|---:|---:|---:|
| zero shift | 0 steps / 0m | -0.005 | 0.856 | 0.505 |
| phase only | +8 steps / +24m | +0.527 | 0.514 | 0.812 |

By horizon, all focus rows:

| Horizon | Best shift | Corr | MAE |
|---:|---:|---:|---:|
| 6m | +2 steps / +6m | +0.977 | 0.133 |
| 12m | +4 steps / +12m | +0.978 | 0.129 |
| 24m | +8 steps / +24m | +0.978 | 0.127 |

This is the central result from this diagnostic alone. The fixed formula is not random. It draws almost the same terrain shape after a horizon-sized shift.

Important follow-up correction: the advance-operator audit found that the fixed `Formula` has `corr_with_current +0.978` on 2017+ holdout. So the shifted match is not a valid forecast result by itself. It mostly means:

```text
Formula(t + h) draws the terrain/current state at t + h
```

That is useful as a topology/map diagnostic, but it is future-current leakage if used as a prediction. The strict forecast problem is still to estimate the future terrain-arrival state from origin-time lower-layer spin.

### Fitted `Formula_Adjustable`

Across 6/12/24-month focus rows:

| Test | Shift | Corr | MAE |
|---|---:|---:|---:|
| zero shift | 0 steps / 0m | +0.164 | 0.703 |
| best shift | 0 steps / 0m | +0.164 | 0.703 |

The fitted constants reduce the timing offset, but the remaining broad correlation is weaker than the shifted fixed formula.

## Affine Remap Test

Affine remap fits only:

```text
actual = a * formula + b
```

on pre-2017 training rows, then applies the same `a,b` to 2017+ holdout.

### Fixed `Formula`

No phase shift:

| Split | a | b | Holdout corr | Holdout MAE | Holdout direction |
|---|---:|---:|---:|---:|---:|
| train fit, holdout apply | 0.0316 | 0.0396 | -0.005 | 0.639 | 0.731 |

Affine alone improves MAE/direction, but not correlation. That means zero-shift scale/offset is not the main problem.

With phase correction first:

| Shift | a | b | Holdout corr | Holdout MAE | Holdout direction | Amp ratio |
|---:|---:|---:|---:|---:|---:|---:|
| +8 steps / +24m | 0.6154 | 0.0205 | +0.527 | 0.497 | 0.859 | 0.758 |

Phase correction is doing the real work. Affine remap then cleans the scale.

## Peak/Trough Matching

For fixed `Formula`, peaks/troughs are frequently present in the same sequence, but displaced:

| Horizon | Extrema match rate | Mean offset steps | Mean absolute offset |
|---:|---:|---:|---:|
| 6m | 0.976 | +2.00 | 2.00 |
| 12m | 0.976 | -0.42 | 1.52 |
| 24m | 0.850 | +1.74 | 2.44 |

For fitted `Formula_Adjustable`:

| Horizon | Extrema match rate | Mean offset steps | Mean absolute offset |
|---:|---:|---:|---:|
| 6m | 0.952 | -0.07 | 0.97 |
| 12m | 0.927 | +0.45 | 1.08 |
| 24m | 0.900 | +0.69 | 1.42 |

This supports the terrain-path interpretation: the turning sequence is often present, even when pointwise timing and scaling are wrong.

## Interpretation

The fixed `Formula` is primarily a terrain-shape extractor that is late by roughly one forecast horizon:

```text
6m forecast  -> best formula shift +6m
12m forecast -> best formula shift +12m
24m forecast -> best formula shift +24m
```

That explains why the line looks good but offset. It is drawing the terrain/current state after the fact, not advancing the terrain ahead far enough.

The fitted constants partly force the line into better real-time alignment, improving amplitude and direction, but they do not yet preserve the huge shifted-shape correlation.

## Next Implication

The next formula change should not be another amplitude fit. It should target the missing advance operator:

```text
current layered-contact state
-> roll the measured sphere ahead by exactly the arriving terrain horizon
-> sample the same terrain path before it reaches the measurement point
```

In other words: the topology is being drawn; the time/phase advance is wrong.

## Output Files

- `TheFormula/ara_layered_sand_shape_timing_diagnostic.py`
- `TheFormula/ara_layered_sand_shape_timing_diagnostic_result.json`
- `TheFormula/ara_layered_sand_shape_timing_diagnostic_result.js`
