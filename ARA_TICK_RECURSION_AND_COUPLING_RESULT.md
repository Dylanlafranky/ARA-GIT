# ARA Tick Recursion And Coupling Candidate Result - 2026-05-23

## Why this test was run

After the geometry transport and temporal-friction tests, the next question was:

> Can the formula run forward on its own required variables one tick at a time, then decode the future observable?

This was the stricter version of the "direct variables" idea. Instead of regressing the final value directly, predict the future geometry/energy state first, then decode the observable from that projected state.

This document also records the separate phi-coupling candidate checks that looked for clean examples of two systems near phi coupling and relaxing toward balance.

## Files

Tick formula engine:

- `TheFormula/ara_formula_tick_engine_test.py`
- `TheFormula/ara_formula_tick_engine_data.js`
- `TheFormula/ara_formula_tick_engine_viz.html`

Tick variable recursion:

- `TheFormula/ara_tick_variable_recursion_test.py`
- `TheFormula/ara_tick_variable_recursion_data.js`

Phi-coupling candidates:

- `TheFormula/ara_phi_coupling_candidate_tests.py`
- `TheFormula/ara_phi_coupling_candidate_results.json`
- `TheFormula/ara_phi_coupling_candidate_results.js`

## Leakage Guard

The two tick tests used the same no-leakage structure:

- At origin `t`, state/variable snapshots use only data up to `t`.
- One-tick transition training uses only completed pairs where `s + tick < t`.
- Decoders use only past geometry anchors.
- Direct controls use only anchors with completed future labels before the current origin.
- Oracle future geometry/variables are diagnostic only and are not forecast models.

The phi-coupling candidate tests used train-only thresholds, train-only lag fitting, and held-out later windows for reported metrics.

## What "Direct Variables" Means

The visualizer label `direct_value_required_variables` is a control, not the formula.

It means:

```text
current required ARA/formula variables
  -> direct ridge regression
  -> future value delta
```

That is closer to a teleporter than a vehicle. It is strict-causal, but it bypasses the framework's intended rule:

```text
current variables
  -> future variables
  -> future value
```

So `direct_value_required_variables` is useful as a benchmark for "how much information is already in the current variables," but it should not be treated as the clean formula.

## 1. Strict Formula Tick Engine

The constrained tick engine used hand-specified formula mechanics plus causal scalar gains:

- ARA flow
- energy in / release
- pi-leak / coupling
- slow ARA drift
- causal decoder from projected geometry

Main non-oracle result:

| Dataset | Useful horizons | Limitation |
|---|---|---|
| ENSO | learned tick only barely beats persistence at 24 months (`0.987` vs `1.010`) | lag ridge wins at all horizons |
| Solar | learned tick is strong at 24 and 60 months (`35.080` vs persistence `57.859`; `47.709` vs `97.387`) | loses at 6, 12, and 132 months |
| ECG RR | constrained formula tick loses to persistence at all tested horizons | direct/lag controls remain stronger |

This means the hand-lawful tick mechanics are not empty, especially on Solar mid-horizons, but they are not yet a general forward operator.

## 2. Tick Variable Recursion

The universal variable-recursion test predicted geometry/energy variables forward one tick at a time, then decoded.

Energy variables mattered. The `tick_variables_energy_decoder` results:

| Dataset | Horizon | MAE | Persistence MAE | Corr |
|---|---:|---:|---:|---:|
| ENSO | 1 month | 0.200 | 0.217 | +0.950 |
| ENSO | 3 months | 0.413 | 0.472 | +0.780 |
| ENSO | 6 months | 0.635 | 0.745 | +0.332 |
| ENSO | 12 months | 0.713 | 0.913 | +0.057 |
| ENSO | 24 months | 0.764 | 1.010 | +0.134 |
| ENSO | 60 months | 0.790 | 0.857 | +0.082 |
| Solar | 6 months | 24.733 | 28.039 | +0.896 |
| Solar | 24 months | 45.295 | 57.859 | +0.678 |
| Solar | 60 months | 49.218 | 97.387 | +0.590 |
| ECG RR | 6 seconds | 64.137 | 73.575 | +0.866 |

Interpretation:

```text
Predicting the required variables first is closer to the framework than
direct value regression, and it often beats persistence. But lag ridge still
wins several horizons, and ECG long horizons degrade badly.
```

The oracle diagnostic is important:

```text
actual future variables -> causal decoder -> value
```

That oracle is very strong across ENSO, Solar, and ECG. So the bottleneck is not "future variables cannot decode the value." The bottleneck is the forward law that moves current variables into their future state.

## 3. Phi-Coupling Candidate Tests

These tests asked where two near-phi systems appear to couple and relax toward balance.

### Solar hemispheres

Data: SILSO extended monthly hemispheric Catalogue B.

Held-out model:

| Metric | Value |
|---|---:|
| MAE | 0.306 |
| Baseline MAE | 0.376 |
| MAE lift | +0.070 |
| Corr | +0.359 |

Event rule:

| Quantity | Value |
|---|---:|
| Supports relative damping | true |
| Supports absolute relaxation | true |
| Fractional toward-balance per cycle | 1.619 |
| Relative damping per cycle | 0.409 |

Interpretation: this is the cleanest candidate in the set. The fractional toward-balance per cycle is strikingly close to phi (`1.618`), but this should be treated as a candidate speed signature, not proof of universal temporal flow.

### Heart and respiration

Held-out model:

| Metric | Value |
|---|---:|
| MAE | 0.167 |
| Baseline MAE | 0.199 |
| MAE lift | +0.032 |
| Corr | -0.041 |

Event rule:

| Quantity | Value |
|---|---:|
| Supports relative damping | true |
| Supports absolute relaxation | false |
| Supports relaxation | false |

Interpretation: weak/mixed. There is some held-out MAE lift, but the relaxation rule itself is not supported cleanly.

### Tides

Held-out model:

| Metric | Value |
|---|---:|
| MAE | 0.262 |
| Baseline MAE | 0.151 |
| Corr | +0.779 |
| Train-only best lag | -48 hours |

Amplitude breathing:

| Quantity | Value |
|---|---:|
| High-gate heldout range mean | 2.264 m |
| Low-gate heldout range mean | 1.412 m |
| Fractional per spring-neap cycle | 0.927 |
| Supports amplitude breathing | true |

Interpretation: the amplitude-breathing part is real, but the tested model does not beat the simpler baseline.

## Main Conclusion

The latest tick tests sharpen the prediction architecture:

```text
future variables are highly decodable
current variables carry useful forecast information
direct variable regression is too teleporter-like
strict formula tick is not strong enough yet
energy-aware tick recursion is the best current framework-shaped step
```

The next clean version should combine:

- causal variable recursion
- coupled-pair ARA/midpoint matching
- local feeder/amplitude state
- a stricter phase clock
- domain-specific coupling gates only when train data supports them

Careful claim:

> The framework's required variables contain useful causal information, and actual future variables decode observables strongly. The unsolved part is the lawful tick operator that moves current variables into future variables without collapsing into direct regression.

## Related Follow-Up: ENSO 12-Month Future-State Decoder

`TheFormula/ara_enso_12m_geometry_state_predictor_test.py` tested whether the same idea would improve the nasal/ENSO 12-month transfer result.

It did not. Future-state decoders produced only `+0.174` to `+0.198` heldout correlation. The old nasal ARA/midpoint template remained best on MAE (`0.739`), and lag-only ridge narrowly won correlation (`+0.205`).

The diagnostic finding is useful:

```text
future phase estimate: modestly useful
future turn estimate: modestly above chance
future sign estimate: below chance
future magnitude estimate: weak
```

So the blocker is specifically future dominance side and amplitude, not simply the lack of a two-stage decoder.
