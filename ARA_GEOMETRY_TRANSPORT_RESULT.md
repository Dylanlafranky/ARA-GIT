# ARA Geometry Transport Test - 2026-05-21

## Why this test was run

After the ARA-rung coordinate and shape-kernel experiments, the next question was:

> Can the current ARA geometry map be used to predict, rather than only describe?

The working interpretation was:

```text
raw data
  -> ARA state geometry
  -> transport energy through rung/coupling paths
  -> decode the future observable
```

This document records the first strict-causal attempt at that pipeline.

## Files

State geometry extractor:

- `TheFormula/ara_state_geometry.py`
- `TheFormula/ara_state_geometry_data.js`
- `TheFormula/ara_state_geometry_viz.html`

Prediction/transport test:

- `TheFormula/ara_geometry_transport_test.py`
- `TheFormula/ara_geometry_transport_data.js`

## State Geometry Result

The state extractor is not a predictor. It reads the current/latest map:

- rung coordinate
- per-rung ARA
- position = `coordinate + ARA / 2`
- occupancy/energy
- phase
- accumulate vs release state
- within-subsystem distances
- cross-subsystem coupling candidates
- vertical ARA matches

### ENSO snapshot

Common NINO/SOI/PDO overlap, anchor: `2025-12-01`.
Base: `2.0`.
Home period: `47` months.

| Subsystem | Center position | Center ARA | Total energy | Top occupancy rungs |
|---|---:|---:|---:|---|
| NINO | 5.695 | 1.093 | 2.066 | k5, k4, k6 |
| SOI | 5.811 | 1.121 | 4.169 | k5, k6, k7 |
| PDO | 4.783 | 1.137 | 4.496 | k3, k7, k4 |

Subsystem center distances:

| Pair | Position distance | ARA gap |
|---|---:|---:|
| NINO <-> SOI | 0.116 | 0.029 |
| NINO <-> PDO | 0.912 | 0.044 |
| SOI <-> PDO | 1.028 | 0.015 |

The strongest cross candidate was:

```text
NINO k5 <-> SOI k5
kind: mirror_or_destructive_candidate
path score: 0.3916
```

Interpretation: the geometry map finds the expected tight NINO/SOI relationship, and it reads that relationship as mirror/anti-phase rather than simple same-direction reinforcement. PDO sits roughly one rung-distance away from the NINO/SOI center.

### Solar snapshot

Anchor: `2026-04-01`.
Home period: `132` months.
Measured system-ARA base used by this extractor: `1.062724`.

Top occupancy rungs:

| Rung | Period months | ARA | Position | State |
|---|---:|---:|---:|---|
| k82 | 146.72 | 1.015 | 82.508 | release |
| k79 | 122.24 | 1.105 | 79.552 | release |
| k85 | 176.09 | 0.975 | 85.487 | accumulate |

Interpretation: this gives a readable current solar state, but the very tight measured base is measurement-conditioned. It should not be quoted as a universal solar constant without rechecking raw-cycle measurement definitions.

### Raw MIT ECG snapshot

Record: MIT-BIH Normal Sinus Rhythm `16265`, channel 0.
Anchor: `1500` seconds.
Base: `phi`, home-relative offsets around the measured heartbeat period.

Top occupancy rungs:

| Rung | Period samples | ARA | Position | Occupancy | State |
|---|---:|---:|---:|---:|---|
| offset-2 | 30.18 | 1.144 | -1.428 | 0.367 | accumulate |
| offset-1 | 48.82 | 0.848 | -0.576 | 0.307 | release |
| offset+0 | 79.00 | 1.889 | 0.945 | 0.130 | accumulate |

Interpretation: raw ECG carries substantial occupancy below the heartbeat rung. This supports the visual diagnosis from the ECG shape-kernel test: a simple broad accumulate/release shape mostly tracks mean/envelope and is not enough to hit the PQRST waveform. Raw ECG likely needs beat-aligned, multi-feature geometry before prediction is meaningful.

## Strict-Causal Geometry Transport Test

Target: ENSO/NINO3.4 anomaly.
Feeders included: SOI and PDO.

Protocol:

- At each rolling origin `t`, build an ARA geometry snapshot from data up to `t`.
- For horizon `h`, train only on past anchors `s` where `s + h < t`.
- Predict `NINO[t+h]`.
- Compare to persistence and causal lag-ridge.

Leakage guard from the artifact:

```text
At origin t, ridge training uses only anchors s with s + horizon < t.
```

Sample:

| Field | Value |
|---|---|
| Data span | 1951-01-01 to 2025-12-01 |
| Test origins start | 2006-10-01 |
| Longest-horizon last origin | 2020-12-01 |
| Base | 2.0 |
| Home period | 47 months |
| Rungs | k3, k4, k5, k6, k7 |
| Minimum training examples | 96 |

Models tested:

| Model | Meaning |
|---|---|
| deterministic_self_transport | Current NINO plus unfit ARA shape self-drive |
| nino_geometry_ridge | Ridge on NINO-only geometry transport features |
| compact_transport_ridge | Ridge on self-drive plus SOI/PDO coupling primitives |
| wide_geometry_ridge | Ridge on compact primitives plus per-rung ARA/phase/occupancy |
| lag_ridge | Ridge on causal NINO lags and slopes |
| lag_plus_* | Lag features plus each geometry feature family |

## Forecast Results

MAE in NINO3.4 units.

| Horizon | Persistence | Best geometry-only | Lag ridge | Winner |
|---:|---:|---:|---:|---|
| 1 month | 0.3837 | 0.3756 self-transport | 0.3142 | lag_ridge |
| 3 months | 0.6294 | 0.6097 NINO geometry | 0.5137 | lag_ridge |
| 6 months | 0.8832 | 0.7548 NINO geometry | 0.6542 | lag_ridge |
| 12 months | 0.9946 | 0.8813 NINO geometry | 0.6698 | lag_ridge |
| 24 months | 1.1738 | 0.7151 NINO geometry | 0.6324 | lag_ridge |
| 60 months | 0.9178 | 0.9050 self-transport | 0.6894 | lag_ridge |

## Main Conclusion

The geometry map carries real predictive signal over persistence at several horizons, especially 6 to 24 months.

However, this first transport implementation does **not** beat a simple causal lag model, and adding geometry features on top of the lag model does **not** cleanly improve it.

So the result is:

```text
ARA geometry is useful as state information.
Direct regression from geometry features to future value is too blunt.
The next test should predict future geometry state first, then decode value.
```

This matters because it preserves the central idea while rejecting the easiest implementation. The framework claim should not be "the current geometry transport predictor solves ENSO." The safer claim is:

> ARA state geometry identifies plausible ENSO subsystem structure and contains forecast signal above persistence, but the first strict-causal value-transport test is still weaker than a simple lag baseline.

## Next Test

Instead of:

```text
geometry(t) -> value(t+h)
```

test:

```text
geometry(t) -> geometry(t+h) -> value(t+h)
```

That means predicting future:

- rung phase
- rung occupancy
- ARA position
- accumulate/release state
- coupling state

Then decode the future observable from the projected geometry.

This is closer to the conceptual model: prediction is not merely reading the map; it is moving the system's energy through the map.

---

## Follow-Up: Temporal Friction And Pocket Tests - 2026-05-23

The follow-up tests are recorded in [`ARA_TEMPORAL_FRICTION_RESULT.md`](ARA_TEMPORAL_FRICTION_RESULT.md).

The main lesson is that the future geometry state is decodable, but the forward transport step still needs a better flow law. Retroactive natural-flow tests show that geometry often moves partway from current state toward natural phase advance:

```text
future_geometry ~= current_geometry + alpha * (natural_advance - current_geometry)
```

For ENSO, retroactive alpha averaged about `0.6-0.7`, near `phi - 1 = 0.618`, but it varied by horizon and state. So phi-like flow is a useful baseline, not a complete operator.

### Temporal friction

The working flow equation became:

```text
flow = ARA / (ARA + temporal_friction)
```

The literal test `temporal_friction = |ARA - phi|` was not supported. It makes friction approach zero near phi, which over-advances the state. The better simple version was:

```text
temporal_friction = 1 + |ARA - phi|
```

This improved some ENSO horizons but still did not beat lag or the future-geometry oracle.

The current safer sketch is:

```text
temporal_friction =
    baseline_time_resistance
  + pi_leak_energy
  + system_inefficiency
  + phi_distance_drag
  - resonance_cancellation
```

### Pi-leak split

Earlier notes used "pi-leak" for two related quantities. They should now be separated:

| Quantity | Value | Interpretation |
|---|---:|---|
| `pi - 3` | `0.141592654` | topology strand / geometric non-closure |
| `(pi - 3) / pi` | `0.045070341` | normalized energy leakage through that strand |

The gear-coupled transition diagnostic found a gear-minus-sync signal around `0.045` across horizons, which points to the normalized energy-leak version.

### Temporal pockets

A rolling causal fit of:

```text
temporal_friction = B + k * |ARA - phi|
```

often produced negative `k`. This should not automatically be treated as a bad coefficient. It may mean that phi-distance is being outweighed by resonance cancellation:

```text
positive k = phi-distance behaves like drag
negative k = collision/resonance cancels effective friction
```

The diagnostic result is mixed:

- Solar at the 132-month horizon supported the pocket interpretation: corr(pocket strength, absolute delta) `+0.355`, corr(pocket strength, anti-phase energy) `+0.333`, and strong-pocket movement was `3.41x` weak-pocket movement.
- ECG RR at the 60-second horizon also supported it: corr(pocket strength, next-horizon movement) `+0.477`, and strong-pocket next-horizon movement was `2.71x` weak-pocket movement.
- ENSO mostly did not support it; pocket strength was weakly or negatively related to future movement at most horizons.

So the next operator should not use `k < 0` alone. It should require a compound state:

```text
temporal_pocket =
  negative phi-distance coefficient
  AND anti-phase/contact geometry
  AND release/snap boundary proximity
```

This keeps the core idea alive while preventing the model from calling every negative coefficient a discovery.
