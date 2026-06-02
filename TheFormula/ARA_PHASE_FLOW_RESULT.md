# ARA Phase Flow Result

**Date:** 2026-05-24

This test follows the targeted geometry-flow result and tests the three focused phase operators directly:

1. clean phase-only flow.
2. regime-gated phase flow.
3. velocity-aware phase flow.

All branches decode with the same phase-only decoder:

```text
future NINO/SOI phase -> NINO3.4
```

so score differences come from the flow operator, not from changing the decoder.

## Files

- `TheFormula/ara_phase_flow_predictor.py`
- `TheFormula/ara_phase_flow_predictor_result.json`
- `TheFormula/ara_phase_flow_predictor_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- `S(t)`, velocity, acceleration, raw sign, and trend inputs use only anchors `<= t`.
- transition models use only completed pairs `s+h<t`.
- regime thresholds are computed only from the current transition-training set.
- decoders use only geometry anchors `a<t`.
- oracle phase decoder uses actual `S(t+h)` and is diagnostic only.

## Main Result

The phase-flow operators improve on the earlier full-state analog flow, but lag ridge still wins overall.

Across the key 6/12/24 month transition band:

| Model | Mean MAE | Mean corr | Mean direction | Read |
|---|---:|---:|---:|---|
| `phase_clean_flow_decoder` | `0.764` | `+0.137` | `0.725` | phase-only flow is useful but incomplete |
| `phase_regime_gated_flow_decoder` | `0.743` | `+0.085` | `0.730` | best phase MAE across 6/12/24 |
| `phase_velocity_flow_decoder` | `0.778` | `+0.177` | `0.716` | best simple phase correlation across 6/12/24 |
| `phase_regime_velocity_flow_decoder` | `0.768` | `+0.211` | `0.691` | best ARA phase correlation across 6/12/24 |
| `raw_analog_baseline` | `0.817` | `-0.041` | `0.704` | worse shape correlation than phase flow |
| `lag_ridge` | `0.623` | `+0.283` | `0.767` | still best strict forecast overall |
| `oracle_phase_decoder` | `0.526` | `+0.664` | `0.832` | diagnostic ceiling remains high |

## Horizon Read

At 6 months, regime gating helps most:

```text
phase_regime_gated_flow_decoder
MAE 0.643
corr +0.465
direction 0.735
```

This comes close to lag ridge correlation at 6 months:

```text
lag_ridge
MAE 0.602
corr +0.477
direction 0.691
```

At 12 months, velocity helps most:

```text
phase_velocity_flow_decoder
MAE 0.790
corr +0.175
direction 0.788
```

Lag still wins:

```text
lag_ridge
MAE 0.649
corr +0.205
direction 0.818
```

At 24 months, regime plus velocity gives the strongest geometry-shape result:

```text
phase_regime_velocity_flow_decoder
MAE 0.718
corr +0.347
direction 0.774
```

This beats lag ridge on correlation at 24 months:

```text
lag_ridge
MAE 0.617
corr +0.167
direction 0.790
```

but lag still wins MAE.

## Interpretation

This is the best evidence so far that the flow operator should be phase-first.

The pattern is not one-size-fits-all:

```text
6 months  -> regime matters most
12 months -> velocity matters most
24 months -> regime + velocity matters most
```

That suggests the transport law is horizon/regime-specific. A single global phase update is still too blunt.

The working model now looks like:

```text
phase flow sets the shape/timing
lag/inertia sets much of the native amplitude
ARA energy/rung/coupling should gate the amplitude decoder
```

The next clean step is therefore not another pure phase predictor. It is a hybrid:

```text
lag ridge = inertial amplitude prior
phase flow = geometry timing/turn prior
ARA coupling/energy = amplitude gate
```

That would fit the result: lag wins MAE, phase flow improves shape correlation at 24 months, and oracle phase still has a much higher ceiling.
