# ARA Cross-Rung Spin Transfer Result

**Date:** 2026-05-25

This test checks the subtler version of the feeder theory:

```text
lower/faster rungs feed by spin, phase pressure, and crossover timing
home rung carries the visible ENSO cycle state
upper/slower rungs hold reservoir/envelope constraints
```

This is different from the previous multi-rung feeder ablation, which tested lower rungs as direct value/amplitude feature blocks.

## Files

- `TheFormula/ara_cross_rung_spin_transfer_test.py`
- `TheFormula/ara_cross_rung_spin_transfer_result.json`
- `TheFormula/ara_cross_rung_spin_transfer_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- every feature at origin `t` uses only `data[:t]`.
- base lag prediction at origin `t` uses only anchors `s` where `s+h<t`.
- risk, amplitude, and time-to-transition models train only on previous records whose required outcomes would already be known.
- the first run exposed a training-window bug and was discarded; this result is from the corrected run with pre-test records available for causal training.

## Faster-Spin Claim

Supported.

Mean absolute phase-turn rate over the held-out test origins:

| Signal | Lower rungs | Home rung | Upper rungs | Monotonic? |
|---|---:|---:|---:|---|
| NINO | `0.3368` | `0.2015` | `0.1081` | yes |
| SOI | `0.5060` | `0.1445` | `0.1203` | yes |
| PDO | `0.4974` | `0.1683` | `0.0736` | yes |

This directly supports the basic geometry claim:

```text
lower/faster rungs spin faster than home,
and home spins faster than upper/slower rungs.
```

## Timing And Boundary-Risk Claim

Mixed.

Across the 6/12/24-month focus window:

| Feature group | Boundary AUC | Boundary top lift | Amplitude corr | Time-to-transition corr |
|---|---:|---:|---:|---:|
| `lag_only` | `+0.478` | `0.884` | `+0.383` | `-0.076` |
| `lag_plus_lower_spin` | `+0.443` | `0.884` | `+0.431` | `-0.040` |
| `lag_plus_upper_envelope` | `+0.549` | `1.112` | `+0.400` | `-0.183` |
| `lag_plus_alignment` | `+0.446` | `0.794` | `+0.404` | `-0.110` |
| `lag_plus_all_spin_transfer` | `+0.500` | `1.079` | `+0.416` | `-0.151` |

Lower spin does **not** cleanly improve boundary-risk ranking. It does improve amplitude-size correlation and time-to-transition MAE:

```text
time-to-transition MAE:
lag_only              5.162
lag_plus_lower_spin   4.972
lag_plus_alignment    4.619
```

But the time-to-transition correlations remain negative, so this is not a solved timing model.

## Upper Envelope Claim

Partly supported.

The upper/envelope feature group is the best boundary-risk model in the 6/12/24 focus window:

```text
boundary AUC:
lag_only                 +0.478
lag_plus_lower_spin      +0.443
lag_plus_upper_envelope  +0.549
```

At 24 months specifically:

```text
boundary AUC:
lag_only                 +0.480
lag_plus_upper_envelope  +0.546

ENSO class-transition AUC:
lag_only                 +0.443
lag_plus_upper_envelope  +0.582
```

This fits the idea that upper/slower rungs carry more of the event envelope or reservoir constraint than the lower rungs do.

## Orientation Claim

Partly supported for turn-risk, not for MAE.

Across 6/12/24 months:

| Subset | n | Lag MAE | Lag turn failure | Boundary rate | Home phase-turn rate | Mean time-to-transition |
|---|---:|---:|---:|---:|---:|---:|
| pressure aligned positive | `139` | `0.966` | `0.793` | `0.547` | `0.007` | `4.872` |
| pressure opposed negative | `108` | `0.931` | `0.842` | `0.583` | `0.046` | `6.521` |
| top aligned pressure quartile | `63` | `0.960` | `0.762` | `0.555` | `0.016` | `5.111` |
| bottom opposed pressure quartile | `63` | `0.894` | `0.857` | `0.573` | `0.080` | `5.943` |

Opposition predicts more turn failure and more home phase-turn events, but not worse MAE. So orientation looks like a transfer-cleanliness / timing-risk variable rather than an amplitude-error variable.

## Interpretation

This result salvages part of the objection, but not all of it.

Supported:

```text
lower rungs really do spin faster
upper rungs look more useful for boundary/event envelope
alignment/opposition carries turn/timing-risk information
```

Not supported yet:

```text
lower spin cleanly improves boundary transition prediction
lower spin solves time-to-transition
alignment/opposition explains amplitude error
all spin-transfer features should be bundled into one larger model
```

The corrected framework statement should be:

```text
Lower rungs are faster spin channels.
In this ENSO test, their direct lower-spin feature block does not yet improve boundary-risk ranking.
Upper rungs carry clearer event-envelope signal.
Orientation/opposition marks turn-risk and phase-turn pressure.
```

The next version should test lower spin as a narrow residual/risk feature:

```text
central = lag forecast
event envelope = upper reservoir
turn-risk = lower/home opposition and phase pressure
timing correction = small, monotonic, bucketed by upper envelope state
```

Do not bundle all spin features together yet; the all-feature model usually dilutes the useful signals.

## Follow-Up

The topographic wavefront follow-up is recorded in `ARA_TOPOGRAPHIC_WAVEFRONT_FORMULA_RESULT.md`. It formalizes this interpretation as a terrain-flow equation. The first formula has turn/direction signal, but it overcorrects amplitude and is not yet a successful point predictor.
