# ARA Targeted Geometry Flow Result

**Date:** 2026-05-24

This test follows the oracle ablation result:

```text
Do not predict all of S(t+h).
Predict the geometry fields that actually decode NINO.
```

The script predicts three nested future-geometry target sets:

1. `phase_only`: future NINO phase and SOI phase.
2. `phase_energy`: phase plus NINO energy/rung, NINO coupling-energy context, and NINO orientation.
3. `selected`: the broader ablation-selected field set.

It also adds geometry velocity and acceleration:

```text
S(t), S(t)-S(t-1), S(t)-S(t-3), S(t)-S(t-12)
plus matching acceleration terms
```

## Files

- `TheFormula/ara_targeted_geometry_flow_predictor.py`
- `TheFormula/ara_targeted_geometry_flow_predictor_result.json`
- `TheFormula/ara_targeted_geometry_flow_predictor_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- `S(t)`, velocity, and acceleration features use only anchors `<= t`.
- transition models use only completed pairs `s+h<t`.
- decoders use only geometry anchors `a<t`.
- oracle decoders use actual `S(t+h)` and are diagnostic only.

## Main Result

The targeted flow is better than the previous whole-state analog flow, but still does not beat lag ridge.

Mean across the key 6/12/24 month transition band:

| Model | Mean MAE | Mean corr | Mean direction | Read |
|---|---:|---:|---:|---|
| `phase_only_ridge_flow_decoder` | `0.747` | `+0.221` | `0.715` | best strict ARA geometry-flow branch |
| `selected_ridge_flow_decoder` | `0.842` | `+0.153` | `0.706` | broader target adds noise |
| `raw_analog_baseline` | `0.817` | `-0.041` | `0.704` | good MAE/turn, poor correlation |
| `lag_ridge` | `0.623` | `+0.283` | `0.767` | still best strict forecast |
| `oracle_phase_only_decoder` | `0.526` | `+0.664` | `0.832` | diagnostic ceiling for phase fields |
| `oracle_selected_decoder` | `0.522` | `+0.738` | `0.826` | diagnostic ceiling for selected fields |

## Horizon Highlights

At 12 months:

| Model | MAE | Corr | Direction |
|---|---:|---:|---:|
| `phase_only_ridge_flow_decoder` | `0.761` | `+0.201` | `0.758` |
| `raw_analog_baseline` | `0.784` | `-0.076` | `0.727` |
| `lag_ridge` | `0.649` | `+0.205` | `0.818` |
| `oracle_phase_only_decoder` | `0.531` | `+0.664` | `0.848` |
| `oracle_selected_decoder` | `0.548` | `+0.702` | `0.803` |

At 24 months:

| Model | MAE | Corr | Direction |
|---|---:|---:|---:|
| `phase_only_ridge_flow_decoder` | `0.738` | `+0.196` | `0.726` |
| `selected_ridge_flow_decoder` | `0.762` | `+0.245` | `0.774` |
| `raw_analog_baseline` | `0.959` | `-0.398` | `0.710` |
| `lag_ridge` | `0.617` | `+0.167` | `0.790` |
| `oracle_selected_decoder` | `0.482` | `+0.793` | `0.823` |

The 24-month result is the most interesting: `selected_ridge_flow_decoder` has better correlation than lag ridge (`+0.245` vs `+0.167`), but lag ridge still wins MAE (`0.617` vs `0.762`).

## What Failed

The analog version still fails:

```text
selected_analog_flow_decoder
6/12/24 mean MAE  = 0.980
6/12/24 mean corr = +0.001
```

So the problem was not only "too many target fields." Nearest-neighbour transition averaging is still too blunt even after target reduction and velocity features.

The broader selected target set also adds noise in strict prediction. The best strict ARA branch is phase-only, not the larger phase+energy target.

## Interpretation

This test narrows the picture:

```text
Full-state analog flow        failed
Targeted analog flow          failed
Targeted ridge phase flow     partially works
Lag ridge                     still best strict forecast
Oracle selected geometry      remains strong
```

The best strict ARA result comes from predicting future NINO/SOI phase only. That suggests the next transport operator should treat phase as the primary flow variable and use energy/rung/coupling as gates or amplitude decoders, not as equally predicted state coordinates.

In plainer terms:

```text
Predict the clock hand first.
Then use ARA energy/rung geometry to decide how strongly that phase becomes native NINO amplitude.
```

That matches the current evidence better than moving the whole geometry state at once.
