# ARA Layered Sand Parameter Search Result

Run date: 2026-05-26

## Purpose

Fit the `Formula_Adjustable` constants for the single layered-sand formula, then check whether those constants survive outside the calibration window.

This is calibration, not proof. The optimizer sees truth on the training rows.

Training split:

- system: ENSO
- horizons: 6, 12, 24 months
- training origins: before `2017-01-01`
- holdout origins: `2017-01-01` onward

Script:

```bash
python TheFormula/ara_layered_sand_parameter_search.py
```

Visualizer:

```text
TheFormula/ara_layered_sand_formula_adjustable_viz.html
```

The visualizer now opens `Formula_Adjustable` with these fitted constants by default. Use `Reset base Formula` to return to the original fixed constants.

## Best Constants

| Variable | Value |
|---|---:|
| `floor_drive` | 3.606545 |
| `lower_speed` | 7.695839 |
| `contact_transfer` | 1.610237 |
| `second_contact` | 0.722503 |
| `wobble` | 0.443672 |
| `own_spin` | 0.048800 |
| `terrain_pull` | 0.627898 |
| `terrain_spill` | 1.132071 |
| `roll_to_ara` | 1.992629 |
| `roll_to_phase` | 56.181894 |
| `phase_terrain` | 1.420526 |
| `ara_terrain` | 3.239170 |
| `upper_pressure` | 2.478783 |
| `upper_grip` | 0.607152 |
| `upper_brake` | 0.889367 |
| `measured_roll` | 5.417008 |

## Main Scores

| Split | Formula | MAE | Corr | Direction | Amp ratio |
|---|---|---:|---:|---:|---:|
| Train pre-2017 focus | base | 0.885 | +0.029 | 0.534 | 0.158 |
| Train pre-2017 focus | fitted | 0.685 | +0.229 | 0.759 | 0.985 |
| Holdout 2017+ focus | base | 0.856 | -0.005 | 0.505 | 0.143 |
| Holdout 2017+ focus | fitted | 0.741 | +0.018 | 0.720 | 0.905 |
| All focus | base | 0.876 | +0.020 | 0.525 | 0.154 |
| All focus | fitted | 0.703 | +0.164 | 0.746 | 0.962 |
| All horizons | base | 0.812 | +0.133 | 0.541 | 0.163 |
| All horizons | fitted | 0.732 | +0.081 | 0.711 | 1.009 |

## Holdout By Horizon

| Horizon | MAE | Corr | Direction | Amp ratio |
|---:|---:|---:|---:|---:|
| 6m | 0.689 | -0.236 | 0.647 | 1.044 |
| 12m | 0.707 | +0.292 | 0.750 | 0.924 |
| 24m | 0.841 | -0.091 | 0.778 | 0.798 |

## Interpretation

The fitted constants do what we wanted mechanically: they restore amplitude and turn accuracy without using persistence, lag, smoothing, legacy wobble, or raw-address lookup as formula inputs.

The best signal is:

- amplitude ratio moves from about `0.15` to about `0.96` on the 6/12/24 focus set
- direction improves from `0.525` to `0.746`
- holdout direction remains high at `0.720`
- 12-month holdout correlation is positive at `+0.292`

The caution is also clear:

- 6m and 24m holdout correlations are weak/negative
- the fitted constants drive large raw ARA displacement before boundary clamping, so the formula is often slamming into the recursive terrain bounds
- this is calibrated on ENSO only

So this is a useful fitted candidate, not a universal constant set yet. The next test is to freeze these constants and apply them to another time split and another system.

## Output Files

- `TheFormula/ara_layered_sand_parameter_search.py`
- `TheFormula/ara_layered_sand_parameter_search_result.json`
- `TheFormula/ara_layered_sand_parameter_search_result.js`
- `TheFormula/ara_layered_sand_formula_adjustable_viz.html`

