# ARA Topographic Wavefront Formula Result

**Date:** 2026-05-25

This is the first formal test of the terrain-flow version of ARA:

```text
ARA topology = curved constraint surface
wavefront = current energy path across that surface
lower rungs = micro-wave impulse / texture
upper rungs = envelope / reservoir terrain
friction/turbulence = scattering or resistance from opposition/roughness
prediction = advance the wavefront along the easiest available route
```

## Formula Tested

The first explicit terrain formula was:

```text
terrain_flow =
    0.35 * wavefront
  + 0.30 * surface_slope
  + 0.25 * micro_impulse
  + 0.15 * curvature
  - 0.20 * turbulence
```

With two risk scores:

```text
transition_pressure =
  sigmoid(boundary_proximity
        + positive_surface_slope
        + |terrain_flow|
        + micro_density
        + upper_reservoir
        - turbulence)

boundary_encounter =
  sigmoid(boundary_proximity
        + upper_reservoir
        + positive_surface_slope
        - turbulence)
```

And a strict-causal residual correction:

```text
central = lag prediction
corrected = lag prediction + causal_residual_decoder(terrain terms)
```

## Files

- `TheFormula/ara_topographic_wavefront_formula_test.py`
- `TheFormula/ara_topographic_wavefront_formula_result.json`
- `TheFormula/ara_topographic_wavefront_formula_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- every terrain component at origin `t` uses only `data[:t]`.
- base lag prediction at origin `t` uses only anchors `s` where `s+h<t`.
- residual correction calibration uses only previous records whose targets are already known.
- raw terrain scores are unsupervised formula scores, not fitted on future.

## Main Result

The first terrain-flow formula is **not yet a successful predictor**.

Across 6/12/24 months:

| Model | MAE | Corr | Turn acc | Transition MAE |
|---|---:|---:|---:|---:|
| `lag` | `0.951` | `-0.018` | `0.186` | `1.177` |
| `lag_plus_terrain` | `1.037` | `+0.021` | `0.539` | `1.289` |

The terrain correction improves turn accuracy but worsens MAE and transition MAE. That means the formula is pushing in a direction that is often directionally plausible, but the magnitude/work conversion is too forceful or poorly calibrated.

## Raw Formula Risk Scores

6/12/24-month focus AUCs:

| Raw formula score | Boundary crossing | ENSO transition | Lag turn failure | High lag error |
|---|---:|---:|---:|---:|
| `terrain_flow_score` | `+0.456` | `+0.492` | `+0.491` | `+0.456` |
| `transition_pressure_score` | `+0.475` | `+0.508` | `+0.563` | `+0.406` |
| `turbulence_score` | `+0.509` | `+0.452` | `+0.487` | `+0.478` |
| `boundary_encounter_score` | `+0.502` | `+0.498` | `+0.556` | `+0.389` |

The only useful focus-window signal is modest:

```text
transition_pressure -> lag turn failure AUC +0.563
boundary_encounter  -> lag turn failure AUC +0.556
```

At 3 months, `transition_pressure` strongly ranks ENSO class transitions:

```text
3m transition_pressure -> ENSO transition AUC +0.701
```

But that does not persist cleanly across 6/12/24 months.

## Interpretation

This formalizes the terrain idea, but the first equation is not right yet.

What it suggests:

```text
the terrain formula contains directional information
the residual decoder overcorrects amplitude
boundary-crossing risk is not captured by this terrain pressure yet
turbulence is not yet measuring the right scattering loss
```

The biggest lesson is that the formula should probably predict **direction/turn/risk first**, then use a bounded amplitude decoder:

```text
central = lag
direction_pressure = terrain_flow
risk = transition_pressure
correction = small bounded amount only when terrain and lag disagree
interval_width = calibrated from risk bucket
```

The next version should not use a free residual decoder. It should use a monotonic rule:

```text
if terrain_flow agrees with lag:
    keep lag, raise confidence
if terrain_flow opposes lag:
    keep lag central, widen interval, add small capped correction only near boundary
if transition_pressure is high:
    raise event/turn probability, not raw amplitude
```

So yes, the terrain formulation can be turned into a formula. This run is the first formal equation, and it shows the direction of the next correction: constrain the wavefront advance rather than letting the residual decoder push freely.

## Follow-Up: No-Lag Energy Input

The no-lag follow-up is recorded in `ARA_PLAIN_ENERGY_INPUT_WAVEFRONT_RESULT.md`.

It removes the lag/inertia point forecast and uses only ARA terrain plus lower-rung energy input to move the current state. The result keeps the same basic lesson: the formula has turn/boundary signal, but native-unit amplitude is still not solved. Across 6/12/24 months, raw ARA energy improves turn accuracy over persistence (`0.475` vs `0.004`) but worsens MAE (`0.961` vs `0.946`). Lower-spin energy input ranks boundary crossings better (`AUC +0.594` focus, `+0.673` at 12 months), which supports using it as a feeder/boundary pressure term rather than a free amplitude decoder.
