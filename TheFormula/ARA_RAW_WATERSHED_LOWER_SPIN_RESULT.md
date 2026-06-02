# ARA Raw Watershed Lower-Spin Result

**Date:** 2026-05-25

This is the corrected raw watershed test after the conceptual clarification:

```text
tributaries / lower rungs = fast small systems that spin/turn the current sphere
current sphere = the terrain frame the water slice experiences
upper rungs / sea = slow backpressure and envelope, not the main turning engine
```

The previous raw watershed test treated upper-period finite differences too much like direct "slow terrain arrival." This version demotes upper periods to weak sea/backpressure gates and makes lower-spin torque the main topology-arrival term.

## Formula Tested

```text
lower_spin_torque =
    frequency-weighted lower-offset NINO
  + anti-phase lower-offset SOI
  + lower-offset PDO

topology_arrival =
    0.75 * lower_spin_torque
  + 0.20 * lower/home alignment
  + 0.05 * home_inertia

sea_backpressure =
    weak upper-offset NINO/SOI/PDO term

raw_flow =
    0.60 * topology_arrival
  + 0.18 * phi_valley_pull
  + 0.14 * home_inertia
  + 0.08 * sea_backpressure
```

Then:

```text
unit_delta = sqrt(h / home_period) * gated(raw_flow)
```

## Files

- `TheFormula/ara_raw_watershed_lower_spin_test.py`
- `TheFormula/ara_raw_watershed_lower_spin_result.json`
- `TheFormula/ara_raw_watershed_lower_spin_result.js`
- `TheFormula/ara_raw_watershed_lower_spin_viz.html`

## Leakage Guard

For origin `t` and horizon `h`:

- every raw feature at origin `t` uses only samples `<= t`.
- no bandpass, z-score, rolling smoothing, or lag-ridge/native lag feature block is used.
- raw lower-spin flow uses a fixed formula, not future fitting.
- optional scale/decoder checks at origin `t` train only on previous records whose targets are already known.

## Main Result

The corrected lower-spin version is essentially as strong as the previous raw watershed decoder, but better aligned with the intended mechanism.

Across 6/12/24 months:

| Model | MAE | Corr | Turn acc | Transition MAE |
|---|---:|---:|---:|---:|
| `persistence` | `0.896` | `+0.003` | `0.007` | `1.187` |
| `lower_spin_formula` | `0.937` | `+0.024` | `0.397` | `1.230` |
| `lower_spin_scaled` | `0.876` | `-0.021` | `0.599` | `1.078` |
| `lower_spin_decoder` | `0.633` | `+0.241` | `0.783` | `0.703` |

The fixed lower-spin formula still does not solve amplitude, but it improves turn activity. The past-only lower-spin decoder remains much stronger than persistence and close to the previous raw watershed decoder (`0.633` MAE here vs `0.628` before).

## Mechanism Check

6/12/24-month focus AUCs:

| Raw score | Boundary crossing | ENSO transition | Large move | High persistence error |
|---|---:|---:|---:|---:|
| `lower_spin_torque` | `+0.437` | `+0.568` | `+0.520` | `+0.627` |
| `lower_spin_pressure` | `+0.385` | `+0.492` | `+0.501` | `+0.588` |
| `topology_arrival` | `+0.423` | `+0.564` | `+0.525` | `+0.628` |
| `sea_backpressure` | `+0.495` | `+0.555` | `+0.545` | `+0.602` |
| `boundary_gate` | `+0.260` | `+0.549` | `+0.535` | `+0.586` |
| `turbulence` | `+0.543` | `+0.482` | `+0.448` | `+0.421` |
| `raw_flow` | `+0.447` | `+0.550` | `+0.514` | `+0.574` |

This is more consistent with the revised model:

```text
lower_spin_torque and topology_arrival rank transition/high-error pressure
sea_backpressure has signal, but behaves like a slower envelope/backpressure
boundary_gate is not yet correctly oriented for direct boundary-crossing prediction
```

## Interpretation

This supports the correction:

```text
The lower systems are not just tributary values.
They are fast spin/torque inputs that turn the sphere/topology underneath the water slice.
The upper systems are more like sea level/backpressure: they can affect the river, but they are not the main spinner.
```

What remains unsolved:

```text
the fixed symbolic lower-spin formula still over/under-pushes amplitude
boundary-crossing geometry is mis-specified
we still need controls against generic raw finite-difference predictors
```

The next fair control should compare:

```text
corrected lower-spin ARA decoder
raw finite-difference control without ARA channel/phi/ridge terms
wrong-rung lower-spin control
shuffled tributary control
upper-heavy mistaken model
```

That will tell us whether the gain comes from the lower-spin ARA architecture specifically.
