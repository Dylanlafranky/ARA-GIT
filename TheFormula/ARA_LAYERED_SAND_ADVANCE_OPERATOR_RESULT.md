# ARA Layered Sand Advance Operator Result

Run date: 2026-05-26

## Purpose

Test the next proposed fix:

```text
current layered-contact state
-> advance the measured sphere / terrain-arrival state by the forecast horizon
-> read the terrain before it reaches the measurement point
```

Script:

```bash
python TheFormula/ara_layered_sand_advance_operator_test.py
```

Visualizer updated:

```text
TheFormula/ara_layered_sand_formula_adjustable_viz.html
```

## Leakage Guard

Strict advance variants use only origin-time raw spin packets already stored by the formula diagnostic. They do not read future NINO/SOI/PDO values, do not average historical neighbours, and do not use a lag ridge or native-value decoder.

The `future_origin_shift_oracle` line is included only as a red leakage diagnostic. It reads the later origin's fixed `Formula` value, so it is not a forecast.

## Main Results

2017+ holdout, 6/12/24-month focus rows:

| Model | MAE | Corr | Corr with current | Direction | Amp ratio |
|---|---:|---:|---:|---:|---:|
| Fixed `Formula` | 0.856 | -0.005 | +0.978 | 0.505 | 0.143 |
| `Formula_Fitted` | 0.741 | +0.018 | -0.050 | 0.720 | 0.905 |
| `Advance_Phase_Read` | 0.701 | +0.149 | -0.154 | 0.720 | 0.877 |
| `Advance_Layer_Roll` | 0.857 | -0.113 | -0.002 | 0.720 | 1.011 |
| `Advance_Layer_Roll_Fast` | 0.828 | -0.128 | +0.038 | 0.774 | 1.078 |
| `Advance_Lower_Terrain_Base` | 0.696 | -0.127 | -0.252 | 0.731 | 0.805 |
| `future_origin_shift_oracle` | 0.131 | +0.983 | +0.032 | 0.962 | 0.980 |

## Interpretation

The audit corrected the earlier read of the shifted-shape result. The fixed `Formula` is extremely correlated with current NINO (`corr_with_current +0.978`), so the horizon-sized best-lag match is mostly a future-current leakage diagnostic:

```text
Formula(t + h) matches truth(t + h)
```

That means the formula is drawing the current terrain state cleanly, but not yet predicting the future terrain arrival state.

The best strict advance in this pass is `Advance_Phase_Read`. It improves holdout MAE from `0.741` to `0.701` and correlation from `+0.018` to `+0.149` versus the fitted formula, without increasing current-correlation. This suggests that part of the offset is real phase/longitude arrival.

The lower-layer roll variants preserve amplitude, but their correlations are negative. That means they are rolling far enough, but often choosing the wrong route/direction.

## Updated Bottleneck

The problem is no longer just "under-roll." The sharper bottleneck is:

```text
origin lower-spin state
-> correct future roll/contact direction
```

The lower spheres should determine roll direction in the theory, but the first deterministic contact-advance rule is not selecting that direction reliably.

## Output Files

- `TheFormula/ara_layered_sand_advance_operator_test.py`
- `TheFormula/ara_layered_sand_advance_operator_result.json`
- `TheFormula/ara_layered_sand_advance_operator_result.js`
- `TheFormula/ara_layered_sand_formula_adjustable_viz.html`
