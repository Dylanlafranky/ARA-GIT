# ARA Plain Energy-Input Wavefront Result

**Date:** 2026-05-25

This is the no-lag follow-up to the topographic wavefront formula test.

The point was to remove the lag/inertia native-unit predictor and ask whether ARA geometry plus energy input can move the forecast by itself:

```text
lower rungs = faster spinning feeder spheres
home rung = the larger sphere / visible ENSO wavefront
upper rungs = reservoir / envelope constraint
turbulence = opposed spin and roughness loss
prediction = current value + ARA energy-work delta
```

## Formula Tested

The no-lag energy input formula was:

```text
lower_signed_spin =
    0.50 * micro_impulse
  + 0.25 * micro_density * sign(micro_impulse)
  + 0.25 * squash(aligned_pressure - opposed_pressure)

home_wave =
    0.65 * wavefront
  + 0.35 * curvature

route =
    0.45 * lower_signed_spin
  + 0.35 * home_wave
  + 0.20 * surface_slope

effective_work =
    route * reservoir_gate * boundary_gate * friction_gate

unit_delta =
    sqrt(h / home_period) * effective_work
```

Models compared:

```text
persistence        = current value
ara_energy_raw     = current + fixed ARA unit_delta
ara_energy_scaled  = current + past-only scalar calibration of unit_delta
ara_energy_decoder = current + past-only ARA-only energy/terrain decoder
```

## Files

- `TheFormula/ara_plain_energy_input_wavefront_test.py`
- `TheFormula/ara_plain_energy_input_wavefront_result.json`
- `TheFormula/ara_plain_energy_input_wavefront_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- every ARA terrain component at origin `t` uses only `data[:t]`.
- raw ARA energy-flow uses no fitted future data.
- scale and decoder calibration at origin `t` use only previous records whose targets are already known.
- no lag-only/native lag feature block is used by any ARA model in this script.

## Main Result

The no-lag ARA energy formula is **not yet a strong point predictor**, but it has clearer turn/boundary signal than a stationary persistence forecast.

Across 6/12/24 months:

| Model | MAE | Corr | Turn acc | Transition MAE |
|---|---:|---:|---:|---:|
| `persistence` | `0.946` | `-0.004` | `0.004` | `1.270` |
| `ara_energy_raw` | `0.961` | `-0.008` | `0.475` | `1.282` |
| `ara_energy_scaled` | `0.961` | `-0.011` | `0.467` | `1.286` |
| `ara_energy_decoder` | `1.021` | `+0.046` | `0.514` | `1.314` |

The raw ARA energy formula massively improves turn direction over persistence because it actually moves. But it does not improve MAE. The learned ARA-only decoder slightly improves correlation while worsening MAE, which suggests amplitude/work conversion is still miscalibrated.

The cleanest local lift was at 6 months:

| Model | MAE | Corr | Turn acc |
|---|---:|---:|---:|
| `persistence` | `0.779` | `+0.337` | `0.000` |
| `ara_energy_decoder` | `0.772` | `+0.397` | `0.553` |

So there is a short-horizon window where ARA-only geometry/energy beats persistence on MAE, correlation, and turn accuracy.

## Raw Formula Risk Scores

6/12/24-month focus AUCs:

| Raw formula score | Boundary crossing | ENSO transition | High persistence error |
|---|---:|---:|---:|
| `ara_unit_delta` | `+0.453` | `+0.492` | `+0.479` |
| `ara_energy_input_score` | `+0.594` | `+0.457` | `+0.484` |
| `ara_effective_work_score` | `+0.453` | `+0.492` | `+0.479` |
| `ara_turbulence_loss_score` | `+0.585` | `+0.452` | `+0.461` |

The standout is boundary ranking:

```text
ara_energy_input_score -> boundary AUC +0.594 across 6/12/24
12m boundary AUC       -> +0.673
24m boundary AUC       -> +0.624
```

That supports the narrower claim that lower-rung energy input carries boundary/turn pressure. It does not yet decode exact future NINO amplitude.

## Interpretation

This result fits the "smaller spheres spinning the larger sphere" idea better than the lag-backed test did, but only in the route/risk channel:

```text
supported:
  lower-spin energy input helps indicate turn/boundary pressure
  ARA-only motion can improve 6-month prediction versus persistence
  ARA-only direction is much more active than persistence

not yet supported:
  ARA-only energy input solves native-unit amplitude
  scalar calibration is enough
  free ARA-only decoding is stable at 12/24 months
```

The corrected formula direction is:

```text
current state = anchor
lower spin pressure = feeder impulse
upper reservoir = boundary/event gate
ARA route = direction and turn pressure
native amplitude = still needs a better work-to-value decoder
```

So yes: this is possible to test without lag, and the first no-lag result is promising for geometry/turn/boundary information, not yet for exact value prediction.

## Follow-Up: Raw Watershed Slice

The raw-data follow-up is recorded in `ARA_RAW_WATERSHED_SLICE_RESULT.md`.

It removes the smoothed/bandpass rung terrain entirely and uses raw water-slice features: current raw NINO, raw lower-offset tributary differences, raw upper-offset terrain arrival, ARA channel/ridge position, and phi-valley pull. This is the strongest terrain branch so far. Across 6/12/24 months, the past-only raw watershed decoder reaches MAE `0.628` versus persistence `0.896`, corr `+0.241` versus `+0.003`, and turn accuracy `0.791` versus `0.007`. The fixed raw formula alone still does not beat persistence on MAE, so the symbolic work-to-value rule is still missing.
