# ARA Layered Sand Correlation Search Result

Run date: 2026-05-26

## Purpose

Search the layered-sand formula and advance variables for the highest correlation to truth, without using future values inside each prediction.

Script:

```bash
python TheFormula/ara_layered_sand_correlation_search.py
```

## Guardrail

Tuning variables against truth is calibration. To keep the leakage boundary clean:

- variables were fit on pre-2017 ENSO 6/12/24-month rows only;
- 2017+ rows were held out from the optimizer;
- each prediction still uses only origin-time spin packets and current ARA/contact coordinates;
- the objective was correlation only, not MAE.

## Holdout Results

2017+ holdout, 6/12/24-month focus rows:

| Family | Train corr | Holdout corr | Holdout MAE | Direction | Amp ratio |
|---|---:|---:|---:|---:|---:|
| `Formula_Adjustable` | +0.333 | +0.046 | 0.668 | 0.785 | 0.703 |
| `Advance_Phase_Read` | +0.330 | **+0.204** | **0.632** | **0.806** | 0.699 |
| `Advance_Layer_Roll` | +0.241 | +0.032 | 1.010 | 0.602 | 0.947 |
| `Advance_Layer_Roll_Fast` | +0.344 | +0.052 | 0.709 | **0.806** | 0.869 |
| `Advance_Lower_Terrain_Base` | +0.334 | -0.152 | 1.518 | 0.484 | 1.481 |
| `Combined_Advance` | +0.283 | -0.041 | 2.730 | 0.473 | 2.422 |

The best non-leaky holdout correlation was `Advance_Phase_Read` at `+0.204`.

By horizon for that best family:

| Horizon | Holdout corr | MAE | Direction | Amp ratio |
|---:|---:|---:|---:|---:|
| 6m | +0.461 | 0.527 | 0.735 | 0.933 |
| 12m | +0.105 | 0.665 | 0.844 | 0.668 |
| 24m | -0.067 | 0.723 | 0.852 | 0.591 |

## Best Correlation Settings

Best family:

```text
Advance_Phase_Read
```

Key advance setting:

```text
phase_read_gain = 0.64
```

Formula settings that changed materially from the previous fitted constants:

```text
lower_speed     5.1758  (previous fitted 7.6958)
terrain_spill   0.7721  (previous fitted 1.1321)
roll_to_phase   0.0000  (previous fitted 56.1819)
upper_pressure  2.8388  (previous fitted 2.4788)
```

Most other constants stayed at or near the prior fitted solution.

## Interpretation

The leakage diagnostic remains far above the strict result, so we have not recreated the future-origin shift without leakage.

The best strict correlation result again points to phase/longitude arrival, not heavier layer-roll displacement. The roll variants can preserve amplitude, but they do not generalise correlation; they still choose the wrong route too often.

This suggests the next non-leaky route should focus on:

```text
lower-spin/contact state -> phase/longitude arrival correction
```

rather than adding more raw roll distance.

## Manual Screenshot Preset

A later manually tuned visual preset was also scored separately. Because it was chosen while looking at the truth line, it should be treated as in-sample/manual calibration, not as an independent holdout result.

Settings:

```text
floor_drive       1.66
lower_speed       0.22
contact_transfer  0.95
second_contact    0.82
wobble            1.05
own_spin          0.68
terrain_pull      1.59
terrain_spill     0.06
roll_to_ara       1.99
roll_to_phase     234.00
phase_terrain     3.27
ara_terrain       1.40
upper_pressure    1.76
upper_grip        1.67
upper_brake       1.65
measured_roll     3.01
```

Scores:

| Split | MAE | Corr | Corr with current | Direction | Amp ratio |
|---|---:|---:|---:|---:|---:|
| all 6/12/24 | 0.879 | +0.127 | +0.589 | 0.570 | 0.648 |
| pre-2017 | 0.910 | +0.057 | +0.612 | 0.545 | 0.615 |
| 2017+ | 0.815 | +0.260 | +0.552 | 0.624 | 0.716 |

By 2017+ horizon:

| Horizon | Corr | MAE |
|---:|---:|---:|
| 6m | +0.411 | 0.708 |
| 12m | +0.072 | 0.889 |
| 24m | +0.303 | 0.860 |

This preset is now available in the visualiser as `Load manual preset`.

## Wavecycle Screenshot Preset

The later 12-month "freeze and shift back by one measured wavecycle" visual preset was also checked:

```text
floor_drive       1.08
lower_speed       2.58
contact_transfer  0.77
second_contact    0.60
wobble            0.42
own_spin          0.72
terrain_pull      0.90
terrain_spill     0.23
roll_to_ara       0.30
roll_to_phase     360.00
phase_terrain     1.14
ara_terrain       0.39
upper_pressure    2.86
upper_grip        0.24
upper_brake       0.74
measured_roll     1.00
```

For a 12-month forecast:

| Shift rule | Meaning | All-row corr | Holdout corr |
|---|---|---:|---:|
| unshifted forecast | `Formula(t)` vs truth at `t+12m` | -0.060 | -0.142 |
| causal prior-cycle shift | `Formula(t-12m)` vs truth at `t+12m` | -0.267 | -0.390 |
| future-origin shift | `Formula(t+12m)` vs truth at `t+12m` | +0.992 | +0.995 |

That shows the problem sharply: the perfect one-wave shift uses the future-origin formula value and is therefore leakage. The causal prior-cycle version does not reproduce it.

This preset is available in the visualiser as `Load wavecycle preset`. The visualiser also now exposes:

```text
WAVE: Causal prior shift
LEAKAGE DIAG: Adjustable future shift
```

so the two shift directions can be compared directly for any slider configuration.

## Output Files

- `TheFormula/ara_layered_sand_correlation_search.py`
- `TheFormula/ara_layered_sand_correlation_search_result.json`
- `TheFormula/ara_layered_sand_correlation_search_result.js`
- `TheFormula/ara_layered_sand_formula_adjustable_viz.html`
