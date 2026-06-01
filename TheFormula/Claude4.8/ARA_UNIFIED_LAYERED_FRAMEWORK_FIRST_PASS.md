# Unified Layered ARA Framework: First Strict-Causal Pass

## Purpose

This test turns the layered-sand interpretation into one declared ARA operator
and applies the same operator family to Solar, ENSO, and ECG data.

The script is:

`ara_unified_layered_framework_test.py`

The machine-readable result is:

`ara_unified_layered_framework_result.json`

This is a first mathematical skeleton, not a claim that the full recursive
sphere topology has been solved.

## Scenario Terms

The measured system is one sphere or sand layer in a layered contact stack.

| Scenario element | Formula term |
| --- | --- |
| Smaller fast spheres beneath the measured layer | `lower_torque` |
| Alternating roll direction between touching layers | orientation parity flip |
| Two or more uneven lower contacts | `contact_wobble` |
| Measured sphere's current rotation | `own_spin` |
| Recursive ARA, sub-ARA, and sub-sub-ARA terrain | `terrain_slope` |
| Boundary resistance around the current local terrain cell | `ridge_pressure` |
| Slower larger spheres above the measured layer | `upper_pressure` |

## Declared Equation

Let `phi = (1 + sqrt(5)) / 2`.

```text
roll_t = (
    phi^-1 * lower_torque_t
  + phi^-2 * own_spin_t
  + phi^-3 * contact_wobble_t
  + phi^-2 * terrain_slope_t
  - phi^-2 * upper_pressure_t
) / (
    1 + ridge_pressure_t + abs(upper_pressure_t) / phi
)
```

The recursive terrain reader divides the filled `0..2` ARA interval into
progressively smaller cells. At each depth, the local pull points toward the
nearest in-bounds phi valley. Deeper terrain contributes logarithmically less:

```text
weight(depth) = phi^-(depth + 1)
```

The fixed native-unit forecast is:

```text
forecast_(t+h) =
    observed_t
  + train_scale_h * roll_t * sqrt(h / home_period)
```

`train_scale_h` only converts dimensionless roll into native units. It is
calculated on the training segment without using held-out targets.

## Leakage Boundary

All features at origin `t` use raw observations from `t` or earlier. The test
does not use future-origin shifting, future samples, historical-neighbour
averaging, smoothed targets, or a lookup of the true future terrain address.

The fixed forecast carries `observed_t` forward as the current water level. It
does not contain a lag predictor. The diagnostic `home_ar` and `home_plus_ara`
models do contain explicitly labeled causal home lags.

The chronological split is target-safe:

```text
training origins: origin + horizon < cutoff
test origins:     origin >= cutoff
```

## Inputs

The operator is shared. Each system declares its observable contacts.

| System | Measured layer | Lower fast contacts | Upper slow pressure |
| --- | --- | --- | --- |
| Solar | monthly sunspot number | 3-month and 11-month raw sunspot micro-spin | 264-month sunspot envelope |
| ENSO | NINO3.4 | SOI, WWV west, WWV east, IOD | PDO |
| ECG | RR interval | blood-pressure fast feeder, respiration | EEG slow pressure |

Solar currently derives its lower and upper channels from the same raw
sunspot series. ENSO and ECG have independently observed feeder channels.

## Held-Out Results

Each entry is `correlation / MAE`.

### Solar

| Horizon | Persistence | Fixed ARA roll | ARA roll readout | Home AR | Home + ARA |
| --- | --- | --- | --- | --- | --- |
| 12 months | `0.729 / 40.126` | `0.643 / 49.036` | `0.767 / 36.823` | `0.859 / 27.534` | `0.863 / 27.492` |
| 48 months | `-0.431 / 104.206` | `-0.296 / 123.632` | `-0.469 / 91.071` | `0.750 / 37.015` | `0.760 / 36.445` |
| 132 months | `0.678 / 42.606` | `0.542 / 59.546` | `0.682 / 41.200` | `0.653 / 42.907` | `0.676 / 42.017` |

### ENSO

| Horizon | Persistence | Fixed ARA roll | ARA roll readout | Home AR | Home + ARA |
| --- | --- | --- | --- | --- | --- |
| 3 months | `0.766 / 0.501` | `0.695 / 0.591` | `0.814 / 0.452` | `0.844 / 0.391` | `0.855 / 0.375` |
| 6 months | `0.378 / 0.798` | `0.311 / 0.935` | `0.481 / 0.727` | `0.583 / 0.581` | `0.611 / 0.558` |
| 12 months | `-0.040 / 0.997` | `-0.018 / 1.248` | `0.082 / 0.925` | `0.249 / 0.676` | `0.290 / 0.680` |
| 24 months | `-0.338 / 1.168` | `-0.209 / 1.464` | `-0.209 / 1.092` | `0.261 / 0.659` | `0.257 / 0.783` |

### ECG

| Horizon | Persistence | Fixed ARA roll | ARA roll readout | Home AR | Home + ARA |
| --- | --- | --- | --- | --- | --- |
| 1 beat | `0.897 / 19.750` | `0.874 / 33.807` | `0.905 / 19.948` | `0.898 / 19.488` | `0.902 / 19.368` |
| 8 beats | `0.490 / 66.547` | `0.306 / 105.467` | `0.485 / 61.815` | `0.412 / 52.953` | `0.445 / 52.068` |
| 13 beats | `0.458 / 67.061` | `0.313 / 102.079` | `0.469 / 61.419` | `0.404 / 53.318` | `0.419 / 53.435` |

## Interpretation

The first fixed roll equation does not yet beat persistence. Its fixed weights
and one-step displacement rule are too crude to serve as the final predictor.

However, the ARA term block is not empty:

* Its train-only ARA readout beats persistence at useful Solar, ENSO, and ECG
  horizons.
* Solar `home_plus_ara` slightly improves the already strong causal home model.
* ENSO `home_plus_ara` improves the home model at 3, 6, and 12 months.
* ECG ARA terms preserve useful longer-horizon state, but the current contact
  assignment does not improve the home model consistently.

This supports a narrower conclusion: the declared layered terms expose
predictive state across systems, but the universal roll advance rule is not
yet calibrated well enough to replace a learned causal readout.

## Next Mathematical Step

The next test should keep this leakage boundary and replace the single scalar
roll with an explicit 3D orientation update:

```text
omega_t = [forward_roll, lateral_wobble, twist]
pose_(t+1) = rotate(pose_t, omega_t)
terrain_(t+1) = read_recursive_ARA_grid(pose_(t+1))
```

The lower contact spheres should select the direction of `omega_t`. The upper
layer should change grip and braking. The terrain reader should affect the
route inside local bounds. This is the missing bridge between the useful ARA
state block and the desired sphere-coordinate prediction.
