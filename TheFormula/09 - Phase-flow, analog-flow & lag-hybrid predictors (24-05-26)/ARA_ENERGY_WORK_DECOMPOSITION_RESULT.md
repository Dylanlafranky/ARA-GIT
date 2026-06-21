# ARA Energy/Work Decomposition Result

**Date:** 2026-05-25

This test checks the current physical decomposition:

```text
ARA geometry / phase-flow = route, timing, turn topology
lag ridge = carried energy / inertia memory
work = how energy becomes movement along the route
```

The central new variable is alignment:

```text
alignment = sign(lag energy momentum) == sign(ARA geometry flow)
```

If energy and geometry agree, movement should be cleaner. If they oppose, the system should show more stalls, delayed turns, whipsaws, undershoots, overshoots, or false boundary signals.

## Files

- `TheFormula/ara_energy_work_decomposition_test.py`
- `TheFormula/ara_energy_work_decomposition_result.json`
- `TheFormula/ara_energy_work_decomposition_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- base lag and phase predictions use strict-causal training pairs `s+h<t`.
- all decomposition features are measured at origin `t` or earlier.
- the causal error selector only uses previous records whose `target_anchor < origin_anchor`.
- feature/target correlations are retrospective diagnostics, not forecast inputs.

## Main Result

The decomposition is useful diagnostically, but it does not yet improve the forecast.

Across the 6/12/24-month focus window:

| Model | Mean MAE | Mean corr | Turn acc | ENSO class acc | Transition MAE |
|---|---:|---:|---:|---:|---:|
| `lag_ridge` | `0.623` | `+0.283` | `0.767` | `0.474` | `0.683` |
| `ara_phase` | `0.768` | `+0.211` | `0.691` | `0.414` | `0.865` |
| `work_error_selector` | `0.657` | `+0.184` | `0.756` | `0.449` | `0.722` |

The past-only work/error selector does not beat lag. It picks up some structure, but using it to choose between lag and phase still damages MAE and correlation.

## Alignment Result

Alignment is meaningful for turn cleanliness.

6/12/24-month focus window:

| Subset | n | Lag MAE | ARA MAE | Lag turn | ARA turn | Lag boundary | ARA boundary |
|---|---:|---:|---:|---:|---:|---:|---:|
| aligned energy + geometry | `143` | `0.624` | `0.725` | `0.813` | `0.813` | `0.646` | `0.630` |
| opposing energy + geometry | `53` | `0.635` | `0.891` | `0.634` | `0.366` | `0.577` | `0.419` |
| actual transition windows | `120` | `0.683` | `0.865` | `0.840` | `0.718` | `0.597` | `0.637` |

The strongest version is at 24 months:

| 24-month subset | n | Lag MAE | ARA MAE | Lag turn | ARA turn | Lag boundary | ARA boundary |
|---|---:|---:|---:|---:|---:|---:|---:|
| aligned energy + geometry | `47` | `0.547` | `0.642` | `0.872` | `0.872` | `0.787` | `0.723` |
| opposing energy + geometry | `15` | `0.837` | `0.957` | `0.533` | `0.467` | `0.467` | `0.467` |
| actual transition windows | `44` | `0.653` | `0.810` | `0.841` | `0.864` | `0.705` | `0.750` |

This supports the physical idea that energy-route alignment matters. Opposition does not mean "use ARA instead of lag"; it means the system is in a higher-risk work-conversion state.

## What Failed

The first dissipation/turbulence proxy is not right.

The top quartile by the current dissipation proxy does **not** behave like a worst-error bucket:

```text
6/12/24 high-dissipation top quarter:
lag MAE       0.611
lag turn      0.794
lag boundary  0.730
```

That is better than the all-window lag score on several measures, so this proxy is not measuring "bad work" yet. It may be measuring strong structured motion instead of turbulence.

The direct work/error selector also fails as a forecast improvement:

```text
lag ridge MAE        0.623
work selector MAE    0.657
```

## Feature Clues

The largest diagnostic correlations with lag turn failure in the 6/12/24 focus window were:

| Feature | corr with lag turn failure |
|---|---:|
| `energy_reservoir_proxy` | `-0.313` |
| `energy_raw_amplitude` | `-0.299` |
| `work_energy_aligned_with_phase` | `-0.274` |
| `work_agreement_strength` | `-0.210` |
| `energy_rolling_variance_24` | `-0.203` |
| `geometry_boundary_velocity_phi_3` | `+0.185` |
| `work_alignment_lag_phase` | `-0.178` |
| `work_opposition_lag_phase` | `+0.178` |

The negative signs mean larger reservoir/amplitude/aligned-energy values are associated with fewer lag turn failures. This is consistent with the work idea: aligned available energy makes the route easier to follow.

## Interpretation

This result refines the architecture:

```text
lag remains the point forecast and amplitude carrier
ARA phase remains the route / transition / boundary channel
energy-route alignment is a real risk diagnostic
the current dissipation proxy is not valid
```

The next useful step is not a freer model. It is a cleaner turbulence definition:

```text
bad_work = opposition + low reservoir + boundary approach + weak coupling coherence
```

Then test whether that bucket predicts:

- lag wrong-direction cases,
- lag boundary failures,
- transition undershoots,
- widened uncertainty intervals.

For now, the strict claim is:

```text
ARA geometry appears to capture route/topology.
Lag carries crude energy memory.
Energy-to-route alignment identifies cleaner versus riskier work states.
The energy-to-work conversion rule is not solved yet.
```

Follow-up note: the transition-risk and uncertainty model is recorded in `ARA_TRANSITION_RISK_AND_UNCERTAINTY_RESULT.md`. It found useful risk-ranking signal for lag high-error, turn-failure, and boundary/event warnings, but the first interval-width calibration undercovers and is not yet usable as an honest interval.
