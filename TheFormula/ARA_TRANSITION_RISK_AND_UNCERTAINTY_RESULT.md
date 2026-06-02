# ARA Transition Risk And Uncertainty Result

**Date:** 2026-05-25

This test stops forcing ARA to be a point predictor. It keeps:

```text
lag ridge = central native-unit forecast / carried energy
ARA phase-flow = route, timing, boundary geometry
energy-work features = risk and uncertainty layer
```

The question is:

```text
Can ARA/work geometry identify when lag is likely to be wrong, when a boundary/event state is likely, and how wide the forecast interval should be?
```

## Files

- `TheFormula/ara_transition_risk_and_uncertainty_model.py`
- `TheFormula/ara_transition_risk_and_uncertainty_result.json`
- `TheFormula/ara_transition_risk_and_uncertainty_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- base lag and phase predictions use strict-causal training pairs `s+h<t`.
- all risk inputs are known at origin `t`.
- risk/interval models train only on previous records whose `target_anchor < t`.
- high-error thresholds and interval calibration are estimated from that same past-only set.

## Main Result

The risk layer has useful signal, especially for high lag error and boundary/event warnings, but the interval-width calibration is not solved.

6/12/24-month focus window:

| Target | n | Event rate | AUC | Brier | Top-quartile lift |
|---|---:|---:|---:|---:|---:|
| `lag_abs_error_high` | `92` | `0.265` | `+0.595` | `0.229` | `1.541` |
| `lag_turn_failure` | `92` | `0.192` | `+0.551` | `0.209` | `1.717` |
| `boundary_crossing` | `92` | `0.587` | `+0.668` | `0.261` | `1.240` |
| `enso_class_transition` | `92` | `0.668` | `+0.523` | `0.367` | `1.012` |

The strongest individual horizon result is the 6-month high-error warning:

```text
lag_abs_error_high at 6m:
AUC       +0.845
top lift   2.400
Brier      0.102
```

Boundary/event-state risk is the most consistent target:

```text
boundary_crossing AUC:
6m   +0.757
12m  +0.644
24m  +0.604
```

## Interval Result

The first risk-calibrated interval is too narrow.

6/12/24-month focus window:

| Interval | Coverage | Mean half-width |
|---|---:|---:|
| past quantile baseline | `0.772` | `0.943` |
| risk-width model | `0.544` | `0.663` |

The risk-width model has weak positive width/error correlation:

```text
width/error corr = +0.153
```

So it is ranking some uncertainty, but it shrinks too aggressively and loses coverage. This should not be used as a forecast interval yet.

## Horizon Notes

At 24 months, the model is not good at high-error risk, but it becomes more useful for class-transition risk:

```text
24m lag_abs_error_high AUC     +0.304
24m lag_turn_failure AUC       +0.580
24m boundary_crossing AUC      +0.604
24m enso_class_transition AUC  +0.684
```

This fits the emerging pattern: ARA is not strongest as an amplitude-error engine at 24 months, but it does carry transition/boundary information.

## Interpretation

This is the best current architecture:

```text
lag = central forecast
ARA/work = risk layer
boundary/event probability = useful
interval width = not calibrated yet
```

The strict result is:

```text
ARA geometry and energy-work features can rank some lag-risk and boundary-risk windows.
They should not replace lag as the point forecast.
The uncertainty layer needs conformal or bucketed calibration before it is usable.
```

The next refinement should keep the point forecast fixed and improve only the uncertainty layer:

```text
central = lag prediction
risk = P(lag high-error / turn failure / event state)
interval = conformal width from past records in the same risk bucket
```

That would avoid the failure mode in this run, where the interval model learned to make widths sharper but not honest enough.

Follow-up note: the multi-rung feeder ablation is recorded in `ARA_MULTIRUNG_FEEDER_ABLATION_RESULT.md`. It found that the current direct lower-phi feeder feature block does not improve 6/12-month prediction and is not yet a clean explanation for medium-horizon gains.
