# ARA Lag/Phase Hybrid Result

**Date:** 2026-05-25

This test checks the next proposed architecture:

```text
lag ridge = native-unit amplitude / inertia prior
ARA phase flow = timing / turn / shape prior
ARA coupling-energy = amplitude gate
```

The question was:

```text
Does ARA phase/regime geometry improve lag ridge at turns and regime shifts?
```

## Files

- `TheFormula/ara_lag_phase_hybrid_predictor.py`
- `TheFormula/ara_lag_phase_hybrid_predictor_result.json`
- `TheFormula/ara_lag_phase_hybrid_predictor_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- geometry snapshots and velocity/gate features use only anchors `<= t`.
- base lag/phase transition models use only completed pairs `s+h<t`.
- final hybrid weights are trained on an inner past calibration slice.
- calibration predictions for calibration origin `c` use only pairs `s+h<c`.
- oracle phase hybrid is diagnostic only because it uses actual `S(t+h)`.

## Main Result

Lag ridge still wins official MAE at every horizon.

The hybrid does not improve the 6/12/24 month average:

| Model | Mean MAE | Mean corr | Turn acc | ENSO class acc | Transition MAE |
|---|---:|---:|---:|---:|---:|
| `lag_ridge` | `0.623` | `+0.283` | `0.767` | `0.474` | `0.683` |
| `phase_clean_only` | `0.764` | `+0.137` | `0.725` | `0.378` | `0.781` |
| `phase_regime_velocity_only` | `0.768` | `+0.211` | `0.691` | `0.414` | `0.865` |
| `lag_plus_clean_phase` | `0.757` | `+0.053` | `0.696` | `0.410` | `0.799` |
| `lag_plus_regime_velocity_phase` | `0.742` | `+0.111` | `0.686` | `0.415` | `0.800` |
| `lag_plus_phase_coupling_gate` | `1.379` | `-0.156` | `0.565` | `0.304` | `1.491` |
| `raw_analog_baseline` | `0.817` | `-0.041` | `0.704` | `0.385` | `1.039` |

The learned coupling/energy gate is unstable in this form and should not be trusted.

## The Useful Part

At 24 months, the phase branch still contributes shape information:

| Model | MAE | Corr | Turn acc | ENSO class acc | Transition MAE |
|---|---:|---:|---:|---:|---:|
| `lag_ridge` | `0.617` | `+0.167` | `0.790` | `0.484` | `0.653` |
| `phase_regime_velocity_only` | `0.718` | `+0.347` | `0.774` | `0.452` | `0.810` |
| `lag_plus_regime_velocity_phase` | `0.672` | `+0.281` | `0.742` | `0.500` | `0.706` |
| `raw_analog_baseline` | `0.959` | `-0.398` | `0.710` | `0.306` | `1.158` |

So the hybrid moves in the right direction at 24 months:

```text
lag corr:                 +0.167
phase-only corr:          +0.347
lag + phase hybrid corr:  +0.281
```

but it still does not beat lag on MAE or transition MAE.

## What Failed

The simple learned hybrid is too unconstrained.

The coupling/energy gate branch performs badly:

```text
6/12/24 mean MAE  = 1.379
6/12/24 mean corr = -0.156
```

This likely means the gate features are real but too high-dimensional and too easy to overfit when used as a free linear combiner.

The oracle hybrid branch is also not a useful ceiling in this script because the same unstable combiner can misuse even oracle phase. The cleaner oracle ceilings remain in:

- `ARA_ORACLE_GEOMETRY_ABLATION_RESULT.md`
- `ARA_PHASE_FLOW_RESULT.md`

## Interpretation

This is not the hybrid win we wanted.

The stricter reading is:

```text
lag ridge remains the best native-unit amplitude predictor
ARA phase flow carries real 24-month shape/timing signal
free learned gates currently damage the forecast
```

The next hybrid should be constrained rather than fully learned. For example:

```text
lag prediction supplies amplitude
ARA phase flow supplies turn/regime pressure
gate only changes the correction size when phase and lag disagree
```

So instead of:

```text
forecast = learned(lag, phase, gates)
```

the safer next test is:

```text
forecast = lag + gate * clipped_phase_turn_correction
```

where `gate` is bounded and monotonic, not a free ridge model over many coupling features.

Follow-up note: the first trust-gate diagnostic is recorded in `ARA_PHASE_TRUST_GATE_DIAGNOSTIC_RESULT.md`. It found that ARA phase disagreement is not enough to replace lag as the point forecast, but it is a useful 24-month lag-risk warning and transition/boundary signal.
