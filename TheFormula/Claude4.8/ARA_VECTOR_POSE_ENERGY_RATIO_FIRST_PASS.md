# ARA Vector Pose + EnergyRatio: First Strict-Causal Pass

## Why This Test Exists

The scalar layered equation exposed useful held-out state across Solar, ENSO,
and ECG, but its direct forecast under-moved. This test uses the new
`EnergyRatio/` notes and the reproducible geometry in `3D models/` to advance a
real point on a sphere rather than multiplying one scalar roll.

The script is:

`ara_vector_pose_energy_ratio_test.py`

The machine-readable results are:

`ara_vector_pose_energy_ratio_result.json`

## What Was Carried Forward

From `EnergyRatio/`:

* Systems differ in how much cycle identity they retain.
* Recycling and shedding should affect how much existing spin survives.
* `2 - phi` is the one-pass bedrock shed landmark before recycling is counted,
  not a universal measured net-loss constant.
* The global recycling metric is diagnostic. A forecast requires an
  origin-safe local estimate.

From `3D models/`:

* The measured sphere uses `ARA = z + 1`, so `z=-1..1` maps to `ARA=0..2`.
* The paired time axis is the space axis rotated by `36 degrees`.
* `phi = 2 cos(36 degrees)` is exact mathematics.
* Faster lower shells act as feeders; matched-rung pairs can be anti-phase;
  slower upper shells act as modulation or pressure.

The viewers remain conceptual visualizations. Their amplitudes, node values,
and motion speeds are not silently treated as empirical constants.

## Vector Equation

The local roll is split into three components:

```text
forward = phi^-1 * lower_torque
lateral = phi^-3 * contact_wobble
twist   = phi^-2 * (local_recycling * own_spin - upper_pressure)
```

For each future tick:

```text
terrain_force =
    recursive_ARA_slope(space_axis)
  + phi^-1 * recursive_ARA_slope(time_axis)

contact_direction =
    rotate_in_local_tangent_plane([forward, lateral], twist)

pose_(t+1) =
    roll_on_sphere(
        pose_t,
        contact_direction / brake + phi^-2 * terrain_force
    )
```

The future native reading is obtained by reading the arrived `z` coordinate
and applying the inverse of the fixed `ARA = 1 + tanh(z_native / 2)` mapping.

## Leakage Boundary

The direct pose formula uses only values observed at or before the forecast
origin. It does not use:

* a future-origin shift;
* future samples;
* target smoothing;
* historical future-coordinate lookup;
* nearest-neighbour target averaging;
* a decoder fitted on held-out truth.

`local_recycling` is calculated causally:

```text
abs(corr(recent trailing block, trailing block one declared period earlier))
```

This differs from the full-record EnergyRatio diagnostic in `recycle_v2.py`.
The full-record diagnostic is useful evidence, but it cannot be injected into
an operational forecast without leakage.

The current pose prototype uses local recycling conservatively as retained-spin
efficiency. A same-junction repeated-recycling shortcut was tested:

```text
B = 2 - phi
effective_loss = B * (1 - rho) / (1 - rho * B)
```

The ablation did not improve direct forecasts. More importantly, the shortcut is
mechanically incomplete: the corrected framework routes recyclable diverted flow
through smaller, faster lower-rung reservoirs before some energy works upward again.
A two-rung-down path may be required for same-spin return. See:

```text
../../EnergyRatio/ARA_CROSS_RUNG_RECYCLING_MODEL.md
```

## Results

Entries are `correlation / MAE / direction accuracy`.

### Direct Pose Formula

| System | Horizon | Persistence | Direct 3D pose |
| --- | ---: | --- | --- |
| Solar | 12 months | `0.729 / 40.126 / 0.000` | `0.613 / 52.258 / 0.547` |
| ENSO | 6 months | `0.378 / 0.798 / 0.000` | `0.361 / 0.821 / 0.514` |
| ECG | 3 beats | `0.681 / 44.756 / 0.023` | `0.695 / 44.534 / 0.465` |
| ECG | 5 beats | `0.567 / 56.707 / 0.015` | `0.573 / 55.323 / 0.504` |
| ECG | 8 beats | `0.490 / 66.547 / 0.026` | `0.436 / 67.541 / 0.445` |

The direct vector formula is not a universal winner. It does, however,
substantially improve the scalar fixed-roll ECG amplitude behavior. The 3D
advance is doing real work rather than reproducing the scalar under-movement.

### Train-Only Pose Diagnostics

| System | Horizon | Home AR | Home + pose |
| --- | ---: | --- | --- |
| Solar | 12 months | `0.859 / 27.600 / 0.794` | `0.863 / 27.512 / 0.805` |
| ENSO | 3 months | `0.844 / 0.393 / 0.665` | `0.828 / 0.405 / 0.674` |
| ECG | 5 beats | `0.535 / 48.515 / 0.693` | `0.565 / 47.375 / 0.707` |
| ECG | 8 beats | `0.412 / 52.953 / 0.736` | `0.519 / 51.089 / 0.739` |
| ECG | 13 beats | `0.404 / 53.318 / 0.707` | `0.477 / 52.697 / 0.708` |

The pose packet adds useful held-out ECG state, especially at 8 beats. It is
not consistently useful for ENSO when combined with home lags. That matches
the data limitation: ENSO is represented by one measured surface coordinate
plus feeder indices, while the framework claim expects a genuinely
multi-dimensional spatial topology.

## Honest Interpretation

This test supports three narrow conclusions:

1. EnergyRatio belongs in the prediction architecture as retained-spin
   efficiency, but it must be measured locally and causally.
2. The 3D sphere convention can be turned into an operational future pose
   advance without using future truth.
3. The arrived 3D pose exposes additional predictive ECG state.

It does not establish:

* a universal `2 - phi` loss law;
* a solved universal ARA predictor;
* that the conceptual 3D viewer motion is measured physical motion;
* that one NINO index is enough to reconstruct the full ENSO topology.

## Next Test

The best next test is a multi-coordinate ENSO topology rather than another
single-line correction:

```text
surface coordinates: NINO regions, SOI, WWV west/east
slow upper shell:     PDO
optional feeder:      IOD
target:               direction first, exact NINO value second
```

Each coordinate should be advanced jointly on its own sphere shell, with the
declared anti-phase and feeder edges. That directly tests the saved framework
claim: full 3D topology plus time evolution should predict direction better
than a one-dimensional target with appended features.
