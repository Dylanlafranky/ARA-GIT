# ARA Raw Watershed-Slice Result

**Date:** 2026-05-25

This test implements the watershed version of ARA using the raw ENSO data directly.

The point was to avoid smoothing the terrain:

```text
no bandpass
no z-score
no rolling averages
no smoothed curve fitting
no lag-ridge/native lag feature block
```

Instead, it treats each time point as a raw water slice:

```text
water slice = current raw NINO value
ARA channel = raw NINO mapped into a 0..2 channel coordinate
phi valley = preferred low-energy route inside the channel
tributaries = raw lower-offset NINO/SOI/PDO finite differences
slow terrain arrival = raw upper-offset NINO/SOI/PDO finite differences
ridges = ARA/ENSO boundary proximity
```

## Formula Tested

The raw watershed formula was:

```text
channel_ara =
    1 + tanh(raw_NINO / 1.5)

phi_valley_pull =
    squash((phi - channel_ara) / phi)

tributary_flow =
    raw lower-offset NINO
  + anti-phase raw lower-offset SOI
  + raw lower-offset PDO

slow_terrain_arrival =
    raw upper-offset NINO
  + anti-phase raw upper-offset SOI
  + raw upper-offset PDO

raw_flow =
    home_flow
  + tributary_flow
  + slow_terrain_arrival
  + phi_valley_pull

unit_delta =
    sqrt(h / home_period) * gated(raw_flow)
```

Models compared:

```text
persistence              = current value
raw_watershed_formula    = current + fixed raw watershed unit_delta
raw_watershed_scaled     = current + past-only scalar calibration of unit_delta
raw_watershed_decoder    = current + past-only raw watershed decoder
```

## Files

- `TheFormula/ara_raw_watershed_slice_test.py`
- `TheFormula/ara_raw_watershed_slice_result.json`
- `TheFormula/ara_raw_watershed_slice_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- every raw terrain feature at origin `t` uses only samples `<= t`.
- raw watershed flow uses a fixed formula, not future fitting.
- optional scale/decoder checks at origin `t` train only on previous records whose targets are already known.
- there is no bandpass, z-score, rolling smoothing, or lag-ridge/native lag feature block.

## Main Result

This is the strongest version of the terrain idea so far.

Across 6/12/24 months:

| Model | MAE | Corr | Turn acc | Transition MAE |
|---|---:|---:|---:|---:|
| `persistence` | `0.896` | `+0.003` | `0.007` | `1.187` |
| `raw_watershed_formula` | `0.934` | `+0.020` | `0.415` | `1.228` |
| `raw_watershed_scaled` | `0.849` | `-0.014` | `0.589` | `1.043` |
| `raw_watershed_decoder` | `0.628` | `+0.241` | `0.791` | `0.691` |

The fixed raw formula still over/under-pushes amplitude, but it improves turn activity. The past-only raw watershed decoder is much stronger: it improves MAE, correlation, turn accuracy, and transition MAE over persistence across the 6/12/24 focus window.

By horizon:

| Horizon | Best raw watershed MAE | Persistence MAE | Best corr | Persistence corr |
|---:|---:|---:|---:|---:|
| `3m` | `0.366` | `0.478` | `+0.822` | `+0.743` |
| `6m` | `0.555` | `0.737` | `+0.521` | `+0.351` |
| `12m` | `0.655` | `0.925` | `+0.230` | `-0.067` |
| `18m` | `0.659` | `1.010` | `+0.194` | `-0.145` |
| `24m` | `0.675` | `1.027` | `-0.028` | `-0.274` |

## Raw Formula Risk Scores

6/12/24-month focus AUCs:

| Raw score | Boundary crossing | ENSO transition | Large move | High persistence error |
|---|---:|---:|---:|---:|
| `raw_flow` | `+0.449` | `+0.554` | `+0.519` | `+0.581` |
| `raw_abs_flow` | `+0.390` | `+0.515` | `+0.531` | `+0.613` |
| `tributary_pressure` | `+0.383` | `+0.495` | `+0.507` | `+0.594` |
| `boundary_pressure` | `+0.253` | `+0.545` | `+0.542` | `+0.601` |
| `slow_terrain_arrival` | `+0.486` | `+0.554` | `+0.532` | `+0.612` |
| `turbulence` | `+0.541` | `+0.483` | `+0.453` | `+0.413` |

The raw risk scores are not clean boundary-crossing detectors yet. Their better signal is high-error / large-move / transition pressure. The decoder is learning how to combine the raw terrain terms more effectively than the fixed formula.

## Interpretation

The user hypothesis was:

```text
The modified/smoothed data skews the natural terrain.
Prediction should measure a raw water slice moving through raw terrain.
```

This test supports that direction.

Supported:

```text
raw watershed slices carry much stronger forecast signal than the smoothed/bandpass terrain formula
past-only raw terrain decoding improves 3-24 month ENSO prediction over persistence
turn/transition shape is much better when the raw jagged terrain is preserved
```

Not solved yet:

```text
the fixed closed-form watershed equation still does not beat persistence on MAE
the decoder is learned, so the exact symbolic work-to-value rule is still missing
boundary-pressure score is mis-specified for direct boundary-crossing ranking
we still need controls to prove this is not just a raw finite-difference predictor in ARA clothing
```

The next clean test should compare:

```text
raw watershed decoder
raw finite-difference control without ARA channel/phi/ridge terms
shuffled tributary control
wrong-rung tributary control
smoothed watershed decoder
```

That will tell us how much of the lift comes from preserving raw terrain, and how much specifically comes from the ARA watershed architecture.

## Correction

The follow-up `ARA_RAW_WATERSHED_LOWER_SPIN_RESULT.md` corrects the mechanism wording in this first raw watershed pass.

In this file, `slow_terrain_arrival` treated upper-period finite differences too directly. The intended model is:

```text
lower rungs = fast tributary torque that spins/turns the current terrain
upper rungs = sea/backpressure/envelope, much weaker as a direct spinner
```

The corrected lower-spin run preserves the raw-terrain decoder gain while aligning the formula with that interpretation.
