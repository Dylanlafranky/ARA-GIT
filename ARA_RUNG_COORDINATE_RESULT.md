# ARA Rung Coordinate Test - 2026-05-20

## Hypothesis

Test Dylan's proposal:

> Instead of only phi rungs, try ARA rungs. The system ARA sets the distance between subsystem rungs, and the ARA measured within each rung tells where that subsystem sits inside the rung.

Coordinate used:

```text
position_k = k + ARA_k / 2
distance_to_home = abs(position_k - position_home)
```

The `/2` maps the ARA range onto one rung interval. Values above 2 are allowed to spill past the nominal rung edge rather than being clipped.

## Script And Artifact

- Script: `TheFormula/ara_rung_coordinate_test.py`
- Artifact: `TheFormula/ara_rung_coordinate_data.js`

This run used a dependency-light one-sided EMA bandpass because the local default Python did not have scipy or pandas. Treat it as an exploratory geometry probe, not a canonical benchmark.

## Configurations

1. phi substrate + phi k-distance
2. phi substrate + 2 k-distance
3. phi substrate + ARA-coordinate distance
4. 2 substrate + 2 k-distance
5. 2 substrate + ARA-coordinate distance
6. system-ARA substrate + ARA-coordinate distance
7. 1+system-ARA substrate + ARA-coordinate distance

## ENSO Results

Home period: 47 months.

Measured home ARA: 1.365 +/- 0.017.

| Configuration | h=1 | h=6 | h=12 | h=60 | h=120 |
| --- | ---: | ---: | ---: | ---: | ---: |
| phi substrate + phi k-distance | 0.527 | 0.672 | 0.715 | 0.643 | 0.687 |
| phi substrate + 2 k-distance | 0.515 | 0.662 | 0.723 | 0.647 | 0.691 |
| phi substrate + ARA-coordinate | 0.515 | 0.662 | 0.723 | 0.647 | 0.691 |
| 2 substrate + 2 k-distance | 0.544 | 0.670 | 0.718 | 0.679 | 0.684 |
| 2 substrate + ARA-coordinate | 0.541 | 0.671 | 0.719 | 0.683 | 0.684 |
| system-ARA substrate + ARA-coordinate | 0.493 | 0.662 | 0.743 | 0.646 | 0.689 |
| 1+system-ARA substrate + ARA-coordinate | 0.526 | 0.678 | 0.715 | 0.684 | 0.681 |
| persistence | 0.214 | 0.787 | 0.982 | 0.958 | 0.962 |

Non-persistence winners:

- h=1: system-ARA substrate + ARA-coordinate
- h=6: system-ARA substrate + ARA-coordinate
- h=12: phi substrate + phi k-distance
- h=60: phi substrate + phi k-distance
- h=120: 1+system-ARA substrate + ARA-coordinate

## Solar Results

Home period: 132 months.

Measured home ARA: 0.715 +/- 0.006.

Direct system-ARA substrate had to be clamped to 1.10 because a logarithmic rung base must be greater than 1.

| Configuration | h=6 | h=12 | h=60 | h=132 | h=264 |
| --- | ---: | ---: | ---: | ---: | ---: |
| phi substrate + phi k-distance | 48.689 | 49.598 | 65.431 | 63.506 | 54.004 |
| phi substrate + 2 k-distance | 46.449 | 47.163 | 63.254 | 61.805 | 51.605 |
| phi substrate + ARA-coordinate | 45.913 | 47.056 | 62.344 | 61.689 | 52.234 |
| 2 substrate + 2 k-distance | 49.044 | 50.530 | 70.537 | 53.585 | 48.398 |
| 2 substrate + ARA-coordinate | 48.674 | 50.658 | 70.488 | 52.421 | 48.178 |
| system-ARA substrate + ARA-coordinate | 42.407 | 42.528 | 52.561 | 54.932 | 53.916 |
| 1+system-ARA substrate + ARA-coordinate | 46.411 | 47.994 | 61.764 | 58.095 | 52.326 |
| persistence | 31.420 | 42.487 | 125.860 | 41.667 | 51.520 |

Non-persistence winners:

- h=6: system-ARA substrate + ARA-coordinate
- h=12: system-ARA substrate + ARA-coordinate
- h=60: system-ARA substrate + ARA-coordinate
- h=132: 2 substrate + ARA-coordinate
- h=264: 2 substrate + ARA-coordinate

## Interpretation

This is a promising exploratory signal, not a confirmed result.

The ARA-coordinate idea improved the solar result strongly at short and mid horizons, and the 2-substrate + ARA-coordinate version won the longer solar horizons. ENSO was mixed: ARA-rung coordinates helped at h=1 and tied/near-tied at h=6, but phi remained better at h=12 and h=60.

The next clean test should port this exact coordinate definition into the canonical Butterworth/SOS scripts and compare against the existing `dual_role_predictor_test.py` and `log2_substrate_test.py` artifacts.

## Follow-up - 2026-05-21: State Geometry And Transport

The ARA-coordinate idea was extended into a state map:

```text
position = coordinate + ARA / 2
```

Files:

- `TheFormula/ara_state_geometry.py`
- `TheFormula/ara_state_geometry_data.js`
- `TheFormula/ara_state_geometry_viz.html`
- `TheFormula/ara_geometry_transport_test.py`
- `TheFormula/ara_geometry_transport_data.js`
- `ARA_GEOMETRY_TRANSPORT_RESULT.md`

The state geometry map is useful descriptively:

- ENSO latest snapshot places NINO and SOI close together in ARA-position space: center distance `0.116`.
- The strongest NINO/SOI cross-candidate is same-rung and mirror/destructive: `NINO k5 <-> SOI k5`.
- PDO sits about one rung-distance away from the NINO/SOI center.
- Raw ECG shows large occupancy below the heartbeat rung, supporting the diagnosis that broad shape kernels track envelope/mean more than the PQRST waveform.

The first strict-causal ENSO transport test was mixed:

| Horizon | Persistence MAE | Best geometry-only MAE | Lag-ridge MAE |
|---:|---:|---:|---:|
| 1 month | 0.3837 | 0.3756 | 0.3142 |
| 3 months | 0.6294 | 0.6097 | 0.5137 |
| 6 months | 0.8832 | 0.7548 | 0.6542 |
| 12 months | 0.9946 | 0.8813 | 0.6698 |
| 24 months | 1.1738 | 0.7151 | 0.6324 |
| 60 months | 0.9178 | 0.9050 | 0.6894 |

Conclusion: ARA coordinates/geometry do carry predictive signal over persistence, especially around 6-24 months, but direct value regression from geometry is too blunt. A simple causal lag ridge still wins, and lag+geometry did not cleanly improve the lag baseline.

The next version should predict the future geometry state first, then decode value:

```text
geometry(t) -> geometry(t+h) -> value(t+h)
```
