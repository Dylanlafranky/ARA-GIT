# ARA Multi-Rung Feeder Ablation Result

**Date:** 2026-05-25

This test isolates whether the apparent medium-horizon cascade signal comes specifically from lower-rung feeder information.

The ablation was:

```text
home_only
home_plus_lower
home_plus_upper
home_plus_lower_upper
home_plus_shuffled_lower
home_plus_nonphi_lower
```

All ARA variants include the same lag/inertia base and the same home-rung NINO/SOI/PDO geometry. The only difference is the added rung block.

## Files

- `TheFormula/ara_multirung_feeder_ablation.py`
- `TheFormula/ara_multirung_feeder_ablation_result.json`
- `TheFormula/ara_multirung_feeder_ablation_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- every feature at anchor `t` uses only `data[:t]`.
- training uses only anchors `s` where `s+h<t`.
- shuffled lower features are drawn only from already-allowed training anchors.
- periods and horizons are fixed before scoring.

## Rung Setup

```text
home period:        47.00 months
lower phi periods:  17.95, 29.05 months
upper phi periods:  76.05, 123.05 months
non-phi lower:      11.75, 23.50 months  (base 2.0)
```

## Main Result

This clean ablation does **not** support the simple lower-phi-feeder claim in its current form.

Across the 6/12/24-month focus window:

| Model | Mean MAE | Mean corr | Turn acc | ENSO class acc | Transition MAE |
|---|---:|---:|---:|---:|---:|
| `lag_ridge` | `0.782` | `+0.216` | `0.686` | `0.404` | `0.802` |
| `home_only` | `0.923` | `+0.095` | `0.680` | `0.357` | `0.909` |
| `home_plus_lower` | `0.959` | `+0.008` | `0.655` | `0.317` | `0.955` |
| `home_plus_upper` | `1.025` | `-0.109` | `0.624` | `0.326` | `1.036` |
| `home_plus_lower_upper` | `0.946` | `-0.005` | `0.655` | `0.341` | `0.951` |
| `home_plus_shuffled_lower` | `0.928` | `+0.075` | `0.688` | `0.353` | `0.939` |
| `home_plus_nonphi_lower` | `0.940` | `+0.053` | `0.664` | `0.391` | `0.902` |

The lag ridge remains the official winner across every scored horizon from 1 to 24 months.

## Hypothesis Checks

### Lower improves 6-12 months?

No.

| Horizon | `home_only` MAE/corr | `home_plus_lower` MAE/corr | Result |
|---|---:|---:|---|
| 6m | `0.822 / +0.225` | `0.825 / +0.046` | lower worsens MAE and corr |
| 12m | `0.842 / +0.152` | `0.894 / +0.035` | lower worsens MAE and corr |

At 6 months, the shuffled-lower control actually beats the real lower block on MAE:

```text
home_plus_lower          MAE 0.825
home_plus_shuffled_lower MAE 0.811
```

That argues against a clean causal lower-feeder gain in this feature construction.

### Upper/envelope improves 22-24 months?

Not by itself.

At 24 months:

| Model | MAE | Corr |
|---|---:|---:|
| `home_only` | `1.104` | `-0.092` |
| `home_plus_upper` | `1.196` | `-0.297` |
| `home_plus_lower_upper` | `0.996` | `+0.001` |
| `lag_ridge` | `0.879` | `+0.032` |

The combined lower+upper block improves over `home_only` at 24 months, but `upper` alone does not, and the combined model still loses to lag ridge.

### Phi lower beats non-phi lower?

No.

The non-phi base-2 lower block beats the phi lower block at 18, 24, and 60 months, and wins the 60-month horizon outright:

```text
60m:
home_plus_nonphi_lower MAE 0.693, corr +0.437
home_plus_lower        MAE 0.821, corr +0.142
home_only              MAE 0.879, corr +0.165
```

This does not prove base-2 is the right lower structure. It says the current phi-lower feature block is not uniquely supported by this ablation.

## Interpretation

This is a useful negative result.

The strict read is:

```text
The current lower-phi feeder block does not explain the medium-horizon gains.
The current upper block does not explain the 24-month envelope on its own.
The 24-month lower+upper lift is real versus home-only, but not enough to beat lag.
The non-phi lower control performing better means this is not yet phi-specific.
```

Possible reasons:

- the rung feature construction is too high-dimensional and overfits.
- lower-feeder timing may need the delayed sampling rule from the earlier feeder-amplitude test.
- lower/upper rungs may need to be used as risk/interval gates, not direct value features.
- the useful cascade effect may live in residual correction after lag, not in one-step ridge over raw feature blocks.

The next clean version should be narrower:

```text
central forecast = lag ridge
test only residual/risk lift from:
  delayed lower phi feeder amplitude
  delayed lower non-phi control
  shuffled delayed lower control
```

For now, this ablation does not justify claiming that lower phi feeders improve 6-12 month ENSO prediction.

Follow-up note: the cross-rung spin-transfer test is recorded in `ARA_CROSS_RUNG_SPIN_TRANSFER_RESULT.md`. It tested the more subtle version where lower rungs feed by faster spin/phase pressure rather than direct amplitude. That test supports the faster-spin claim but still does not show clean lower-spin boundary-risk lift; upper/envelope features carry the clearer event-risk signal in this ENSO setup.
