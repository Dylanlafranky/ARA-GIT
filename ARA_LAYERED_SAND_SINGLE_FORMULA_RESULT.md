# ARA Layered Sand Single Formula Result

Run date: 2026-05-26

## What Changed

This pass separates the work cleanly:

- `Formula` is one deterministic layered-sand formula.
- `Formula_Adjustable` is a copy of the same formula with exposed constants for the HTML visualiser.
- `BASELINE: Persistence` is labelled as a baseline only.
- `LEGACY: Wobble` and `LEGACY: Raw top-1` are labelled as old comparison overlays only.

None of the baseline or legacy overlays are used inside `Formula` or `Formula_Adjustable`.

## Moving Parts And Variables

| Scenario part | Variable | Formula role |
|---|---|---|
| Moving floor | `D0` | Raw spin at `HOME / phi^4`; starts the cascade. |
| Layer spin | `Si` | Own spin of floor/fine/medium/coarse/measured layers from raw NINO, anti-phase SOI, and PDO finite differences. |
| Opposite rolling contact | `Qi = (-1)^i` | Each layer rolls opposite the layer below it. |
| Two lower contacts | `CiA, CiB` | Each layer receives the propagated lower contact plus an adjacent lower raw spin. |
| Wobble | `Wi = CiA - CiB` | Unequal lower contacts create lateral/twist wobble. |
| Lower speed transfer | `Ri = sqrt(Pi / Pi-1)` | Faster lower layers transfer more frequent motion upward. |
| Recursive terrain | `Ti(ARA, phase)` | Every sphere is read through recursive ARA bands and phase terrain. |
| Upper downward pressure | `U` | Upper layers increase grip and brake/compress the transfer. |
| Measured sphere roll | `M` | Final ARA and phase displacement of the measured sphere under the fixed reading point. |

## Formula Skeleton

For each layer:

```text
contact_i = mix(propagated_lower_i, adjacent_lower_i)
wobble_i = propagated_lower_i - adjacent_lower_i
roll_i = (-1)^i * contact_transfer * lower_speed * speed_ratio_i * contact_i
roll_i += own_spin * Si
roll_i += wobble_gain * wobble_i
terrain_i = Ti(ARA_i + roll_to_ara * roll_i.forward, phase_i)
roll_i.forward += terrain_pull * terrain_i.slope
```

For the measured sphere:

```text
delta_ara   = measured_roll * roll_to_ara   * final_roll_vector
delta_phase = floor_phase_motion + measured_roll * roll_to_phase * final_roll_vector
arrival     = current_sphere_coordinate + (delta_ara, delta_phase)
prediction  = terrain_to_native_value(T_measured(arrival))
```

There is no current carry / persistence blend in this formula.

## Current Result

Across the 6/12/24-month focus window:

| Model | MAE | Corr | Direction | Amp ratio |
|---|---:|---:|---:|---:|
| `BASELINE: Persistence` | 0.896 | +0.003 | 0.000 | 0.000 |
| `LEGACY: Wobble` | 0.608 | +0.218 | 0.779 | 0.732 |
| `LEGACY: Raw top-1` | 0.795 | +0.091 | 0.288 | 0.510 |
| `Formula` | 0.879 | +0.015 | 0.523 | 0.158 |

The fixed `Formula` is still under-amplified, but it is now one formula and it is no longer secretly borrowing persistence, wobble, raw top-1, or lag.

## Files

- `TheFormula/ara_layered_sand_single_formula.py`
- `TheFormula/ara_layered_sand_single_formula_result.json`
- `TheFormula/ara_layered_sand_single_formula_result.js`
- `TheFormula/ara_layered_sand_formula_adjustable_viz.html`

