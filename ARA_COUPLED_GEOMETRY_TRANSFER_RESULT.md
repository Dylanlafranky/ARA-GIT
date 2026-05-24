# ARA Coupled Geometry Transfer Result - 2026-05-23

## Why this test was run

The working question was:

> If two systems share the same ARA relation class, can a smaller/faster paired system provide usable time-geometry for a larger/slower paired system?

The immediate target was ENSO, because ENSO is not a single free oscillator. It is a coupled anti-phase pair: NINO and SOI / Walker circulation. That means the right cross-scale comparison should also be a paired anti-phase system, not an uncoupled one. Nasal-cycle dominance is a natural biological candidate because right and left nostril airflow alternate dominance over time.

This document records three connected checks:

1. ECG R-R temporal geometry versus Solar cycles as a one-peak control.
2. Nasal-cycle coupled geometry versus ENSO coupled geometry.
3. Nasal-to-ENSO transfer prediction using ARA and midpoint matching.

## Files

ECG/Solar temporal geometry:

- `TheFormula/ara_ecg_solar_temporal_geometry_test.py`
- `TheFormula/ara_ecg_solar_temporal_geometry_result.json`
- `TheFormula/ara_ecg_solar_temporal_geometry_result.js`

Nasal/ENSO coupled geometry:

- `TheFormula/ara_nasal_enso_coupled_geometry_test.py`
- `TheFormula/ara_nasal_enso_coupled_geometry_result.json`
- `TheFormula/ara_nasal_enso_coupled_geometry_result.js`

Nasal-to-ENSO transfer prediction:

- `TheFormula/ara_nasal_to_enso_prediction_test.py`
- `TheFormula/ara_nasal_to_enso_prediction_result.json`
- `TheFormula/ara_nasal_to_enso_prediction_result.js`

Nasal data source:

- Figshare dataset DOI: `https://doi.org/10.6084/m9.figshare.3807564`
- PLOS paper: `https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0162918`
- Cached files: `TheFormula/data_cache/nasal_sbj1.txt` through `nasal_sbj33.txt`

Other data:

- Solar monthly total sunspots: `F:\SystemFormulaFolder\SILSO_Solar\SN_m_tot_V2.0.csv`
- ECG BIDMC cached signal: `TheFormula/data_cache/bidmc_01_Signals.csv`
- ENSO NINO/SOI sources are handled inside the scripts, with train-only scaling.

## Leakage Guard

The tests were designed to avoid using future target information to tune the result.

- Chronological train/test splits were made before scoring held-out templates.
- NINO/SOI scaling was fitted on the ENSO train split only.
- ENSO-own, NINO-only, and SOI-only templates were built from train data only.
- Period estimates and zero-crossing phase clocks were built from train data only.
- Linear decoders were fitted on train origins only.
- Phase shifts were learned on training templates only.
- The nasal template is external source-domain data.
- Test origins are strictly after the split.
- Symmetric smoothing in the initial nasal-to-ENSO version was replaced with causal smoothing for the corrected prediction run.

## 1. ECG R-R Versus Solar

The primary ECG representation was the R-R interval temporal envelope, not the raw PQRST waveform. Solar cycles were extracted from SILSO monthly total sunspot data.

| Quantity | Value |
|---|---:|
| Solar cycles | 24 |
| Solar train/test | 16 / 8 |
| ECG R-R cycles | 55 |
| ECG R-R train/test | 38 / 17 |

Primary R-R versus Solar result:

| Metric | Value |
|---|---:|
| Train direct correlation | +0.828 |
| Train shifted correlation | +0.927 |
| Test direct correlation | +0.754 |
| Test with train shift | +0.891 |
| Fourier distance, train | 8.4456 |
| Fourier distance, test | 8.0127 |
| Null rank, train | 7 / 9 |
| Random piecewise specificity | 6.8% |

Raw ECG beat waveform versus Solar was weak:

| Metric | Value |
|---|---:|
| Test shifted correlation | +0.090 |

Conclusion:

```text
ECG R-R temporal envelopes and Solar cycles share a strong one-peak
accumulate/release shape after time scaling, but this is not specific against
simple one-peak nulls. Raw ECG PQRST waveform does not transfer.
```

The useful lesson is that the matching geometry is the temporal envelope, not the raw local waveform.

## 2. Nasal Cycle Versus ENSO Coupled Geometry

Definitions:

```text
nasal_laterality = (right_airflow - left_airflow) / (right_airflow + left_airflow)
enso_laterality  = (zNINO - zSOI) / (abs(zNINO) + abs(zSOI))
```

Two shapes were tested:

- Dominance interval template: each dominance half-cycle is sign-normalized and time-rescaled.
- Signed full coupled-cycle template: positive half plus negative half are kept as a full anti-phase cycle.

### Dominance Interval Template

| Metric | Value |
|---|---:|
| Nasal intervals, train/test | 263 / 132 |
| ENSO intervals, train/test | 27 / 13 |
| Train direct correlation | +0.990 |
| Train shifted correlation | +0.991 |
| Test direct correlation | +0.994 |
| Test with train shift | +0.992 |
| Fourier distance, train | 1.9148 |
| Fourier distance, test | 11.704 |
| Null rank | 1 / 9 |
| Random specificity | 99.8% |

Verdict:

```text
strong_specific_coupled_geometry_match
```

### Signed Full Coupled-Cycle Template

| Metric | Value |
|---|---:|
| Nasal signed cycles, train/test | 203 / 113 |
| ENSO signed cycles, train/test | 25 / 11 |
| Train direct correlation | +0.994 |
| Train shifted correlation | +0.994 |
| Test direct correlation | +0.980 |
| Test with train shift | +0.980 |
| Fourier distance, train | 0.9397 |
| Fourier distance, test | 8.273 |
| Null rank | 1 / 9 |
| Random specificity | 100.0% |

Verdict:

```text
strong_specific_coupled_geometry_match
```

### Ablations

| Representation | Coupled NINO/SOI | NINO-only | SOI-only inverted |
|---|---:|---:|---:|
| Dominance interval | +0.992 | +0.985 | +0.958 |
| Signed full cycle | +0.980 | +0.962 | +0.972 |

Shuffled-partner and subject-level checks were more mixed:

| Check | Result |
|---|---:|
| Actual interval percentile versus shuffled | 97.5 |
| Actual signed percentile versus shuffled | 27.5 |
| Subject-level signed score mean | +0.886 |
| Subject-level signed score median | +0.915 |
| Subject-level signed score p05 / p95 | +0.682 / +0.978 |
| Pooled shuffled signed mean / median | +0.884 / +0.929 |

Conclusion:

```text
Paired anti-phase systems share ARA coupled geometry across scale.
Dominance-interval geometry is the strongest evidence.
The full signed-cycle match is high but less specific once sign alternation is preserved.
```

This is important for interpretation. A paired anti-phase null is not automatically a disproof of the framework; under this framing it is the ARA relation class being tested. The statistical question is narrower: does the observed system carry more structure than a generic paired anti-phase alternator?

## 3. Nasal-To-ENSO Transfer Prediction

The prediction test asked whether external nasal coupled geometry can forecast held-out ENSO coupled laterality.

Target:

```text
ENSO coupled LI = (zNINO - zSOI) / (abs(zNINO) + abs(zSOI))
```

Split:

| Field | Value |
|---|---|
| Data span | 1951-01-01 to 2025-12-01 |
| Split date | 2003-07-01 |
| Total months | 900 |
| Nasal subjects | 33 |
| Nasal signed cycles | 316 |
| ENSO train cycles | 25 |
| NINO train cycles | 24 |
| SOI train cycles | 25 |

Models included:

- `nasal_template`
- `enso_own_template`
- `nino_only_template`
- `soi_only_template`
- `nasal_ara_matched_template`
- `ar_current`
- `persistence`

The ARA-matched version selected or weighted nasal source cycles by matching:

- last completed ENSO coupled-cycle ARA
- midpoint fraction
- current distance from balance
- current sign
- elapsed time since last zero crossing

It then decoded with train-only linear features:

```text
[raw_ara_matched_prediction, current_LI, last_ARA, midpoint_fraction]
```

### Corrected Forecast Summary

MAE is on the ENSO coupled laterality index.

| Horizon | Best MAE model | Best MAE | Best correlation model | Best corr | Persistence MAE |
|---:|---|---:|---|---:|---:|
| 1 month | persistence | 0.119 | nasal_ara_matched_template | +0.971 | 0.119 |
| 3 months | persistence | 0.334 | nasal_ara_matched_template | +0.815 | 0.334 |
| 6 months | soi_only_template | 0.603 | nasal_ara_matched_template | +0.455 | 0.613 |
| 12 months | nasal_ara_matched_template | 0.739 | nasal_ara_matched_template | +0.201 | 0.946 |
| 18 months | nasal_template | 0.721 | nasal_template | +0.244 | 1.053 |
| 24 months | soi_only_template | 0.709 | soi_only_template | +0.355 | 1.087 |

ARA-matched details:

| Horizon | ARA-matched MAE | ARA-matched corr | Lift vs persistence | Raw ARA-matched MAE | Raw ARA-matched corr |
|---:|---:|---:|---:|---:|---:|
| 1 month | 0.131 | +0.971 | -0.012 | 0.625 | +0.316 |
| 3 months | 0.367 | +0.815 | -0.033 | 0.697 | +0.213 |
| 6 months | 0.625 | +0.455 | -0.012 | 0.787 | +0.029 |
| 12 months | 0.739 | +0.201 | +0.207 | 0.854 | -0.106 |
| 18 months | 0.743 | +0.155 | +0.310 | -- | -- |
| 24 months | 0.760 | +0.024 | +0.327 | -- | -- |

Conclusion:

```text
ARA/midpoint matching helps the phase clock and is strongest at the
12-month transition window. Short horizons remain persistence-dominated.
Longer horizons benefit from template/mean-reversion, but ARA-matching is
not yet a universal point-prediction operator.
```

## Interpretation

The current state of the idea is:

```text
shared ARA relation class: supported for paired anti-phase geometry
external shape transfer: useful as a transition/phase prior
exact value prediction: not solved
```

The geometry map is not empty. It identifies a meaningful coupled-pair class across very different systems. But the forward projection is still missing enough local state to become a clean predictor.

The likely missing pieces are:

- causal phase/rung clock
- local amplitude gate
- feeder energy state
- coupling strength
- location inside the coupled triangle rather than only the two-system pair
- a cleaner distinction between generic anti-phase geometry and system-specific trajectory

## Current Claim Wording

Careful public claim:

> ARA coupled geometry appears to identify a shared paired anti-phase relation across scale. Nasal dominance cycles and ENSO NINO/SOI dynamics show strong dominance-interval and signed-cycle shape agreement under strict train/test controls. As a forecast prior, the external nasal template helps most around the 12-month transition window, but it does not yet replace persistence or local ENSO/SOI predictors at all horizons.

Do not claim:

> Nasal breathing predicts ENSO.

Do not claim:

> This proves a universal prediction law.

The stronger, still-open test is:

```text
find ARA and midpoint in a smaller coupled pair
match it to the larger coupled pair's current ARA and midpoint
transfer the phase/transition prior
then let local feeder and amplitude state decode the observable
```

That is the next clean version of the framework rather than the current result.

---

## Follow-Up: 12-Month Future Geometry-State Predictor - 2026-05-23

The next clean test was run in `TheFormula/ara_enso_12m_geometry_state_predictor_test.py`.

Output:

- `TheFormula/ara_enso_12m_geometry_state_predictor_result.json`
- `TheFormula/ara_enso_12m_geometry_state_predictor_result.js`

Question:

```text
Can 12-month correlation improve if we predict future ENSO geometry state first,
then decode the value?
```

Target:

```text
ENSO coupled laterality index
LI = (zNINO - zSOI) / (abs(zNINO) + abs(zSOI))
```

Protocol:

- Train origins before `2003-07-01`.
- Heldout origins after `2003-07-01`.
- Horizon fixed at 12 months.
- Future state variables predicted first: sign, turn, delta direction, phase, ARA, midpoint, magnitude.
- Decoder calibrated on predicted state variables from an inner chronological train/calibration split.
- Heldout actual future states used only for state-metric scoring.

Result:

| Model | MAE | Corr | Turn accuracy |
|---|---:|---:|---:|
| persistence | 0.946 | -0.077 | 0.450 |
| AR current | 0.761 | -0.077 | 0.550 |
| old nasal ARA/midpoint template | **0.739** | +0.201 | 0.461 |
| lag-only ridge | 0.797 | **+0.205** | 0.558 |
| future-state full decoder | 0.999 | +0.174 | 0.492 |
| future-state local decoder | 0.991 | +0.198 | 0.519 |
| inner-calibrated stacked blend | 0.869 | -0.027 | 0.419 |

Future-state diagnostics:

| State model | Future sign accuracy | Future turn accuracy | Future abs corr | Phase mean abs cycle error |
|---|---:|---:|---:|---:|
| full with nasal/ARA priors | 0.477 | 0.585 | +0.104 | 0.156 |
| local only | 0.469 | 0.597 | +0.113 | 0.154 |

Conclusion:

```text
Predicting future state first did not raise 12-month correlation.
The bottleneck is not the final decoder; it is future sign/magnitude.
```

The phase estimate is not terrible, and turn classification is modestly above chance. But future sign accuracy is below chance and future magnitude correlation is only about `+0.10`. That prevents the decoded value from reaching high correlation.

The old ARA/midpoint nasal template remains the best MAE model at 12 months. Lag-only ridge narrowly has the best correlation (`+0.205` vs `+0.201`), but both are far from the desired `+0.7`.

Updated interpretation:

> ARA/midpoint matching helps with transition distance, but it does not yet solve future dominance side or amplitude. To reach high correlation, the framework needs a better causal feeder/amplitude state, not just a better phase geometry decoder.

---

## Follow-Up: Delayed Below-Rung Feeder Amplitude - 2026-05-23

Dylan's next correction was:

> The below systems should record incoming energy first. Because that energy needs time to feed upward, sample the faster systems earlier by their rung distance, use the ARA shape for the future transition, then estimate amplitude from the extra feeder energy.

This was tested in `TheFormula/ara_enso_12m_feeder_amplitude_test.py`.

Output:

- `TheFormula/ara_enso_12m_feeder_amplitude_result.json`
- `TheFormula/ara_enso_12m_feeder_amplitude_result.js`

Delay rule:

```text
delay(period) = period * log(home_period / period) / log(base)
feeder_sample = origin + horizon - delay(period)
```

Only `feeder_sample <= origin` was allowed. Each feeder sample used a causal bandpass through that sample only. The test used lower/faster periods:

```text
3, 4, 6, 8, 12, 16, 24 months
```

and tested both base-2 and phi distance clocks.

### Result

| Model | MAE | Corr | Turn accuracy |
|---|---:|---:|---:|
| persistence | 0.946 | -0.077 | 0.450 |
| old nasal ARA/midpoint template | 0.739 | +0.201 | 0.461 |
| lag-only ridge | 0.797 | +0.205 | 0.558 |
| full-detail feeder direct control | 1.034 | +0.127 | 0.543 |
| full-detail feeder sign/amplitude | 0.860 | +0.089 | 0.554 |
| aggregate feeder direct control | 0.852 | +0.207 | 0.539 |
| aggregate feeder sign/amplitude | 0.721 | +0.241 | 0.585 |
| aggregate feeder sign/amplitude, alpha selected inside train only | **0.666** | **+0.354** | **0.593** |

The selected ridge alpha was `100.0`, chosen on the inner pre-split calibration window, not on heldout test.

### Interpretation

This is the first follow-up that materially improves both MAE and correlation at the 12-month window.

The result supports the mechanism in a limited form:

```text
future shape prior alone: useful but weak
future state decoder alone: not enough
delayed lower-rung feeder energy: adds real amplitude/sign information
```

It still does not reach the desired `+0.7` correlation. The likely reason is that this test uses only lower-rung information inside NINO/SOI-derived series. It does not include true physical feeder variables such as subsurface warm-water volume, thermocline depth, trade-wind stress, outgoing longwave radiation, or ocean heat content.

Updated next step:

> Keep the ARA/midpoint shape prior and delayed feeder-amplitude architecture, but feed it actual ENSO energy-source variables rather than only lower-rung transforms of NINO/SOI.

---

## Follow-Up: Boundary-Distance Transfer - 2026-05-23

Dylan's next architecture proposal was:

> Locate each subsystem in the architecture, work out rung distance and singularity-boundary crossings, then scale the lower system until the larger system reaches the equivalent point.

This was tested in `TheFormula/ara_enso_12m_boundary_distance_transfer_test.py`.

Output:

- `TheFormula/ara_enso_12m_boundary_distance_transfer_result.json`
- `TheFormula/ara_enso_12m_boundary_distance_transfer_result.js`

Boundary rule:

```text
source_position = log(source_period) / log(base) + source_ara / 2
target_position = log(home_period) / log(base) + target_ara / 2
boundary_count = ceil(abs(target_position - source_position))
attenuation = (1 - pi_leak_energy) ** boundary_count
equivalent_phase = source_phase + 0.5 * (boundary_count % 2)
```

The test used the same strict 12-month ENSO coupled-LI target as the feeder-amplitude test:

```text
LI = (zNINO - zSOI) / (abs(zNINO) + abs(zSOI))
```

Leakage controls:

- Heldout origins were after `2003-07-01`.
- Source feeder sample indices were never later than the forecast origin.
- Causal bandpass state at each feeder sample used only data through that sample.
- Ridge alpha selection, where used, was done inside a pre-split calibration window.

### Result

| Model | MAE | Corr | Turn accuracy |
|---|---:|---:|---:|
| persistence | 0.946 | -0.077 | 0.450 |
| old nasal ARA/midpoint template | 0.739 | +0.201 | 0.461 |
| lag-only ridge | 0.797 | +0.205 | 0.558 |
| aggregate boundary direct value control | **0.688** | +0.263 | **0.636** |
| aggregate boundary sign/amplitude | 0.705 | +0.271 | 0.601 |
| aggregate boundary deterministic shape scale | 0.744 | +0.211 | 0.488 |
| detailed boundary direct value control | 0.834 | **+0.286** | 0.605 |
| detailed boundary sign/amplitude | 0.765 | +0.148 | 0.543 |

Compared with the previous delayed below-rung feeder result:

| Best branch so far | MAE | Corr | Turn accuracy |
|---|---:|---:|---:|
| delayed feeder aggregate sign/amplitude | **0.666** | **+0.354** | 0.593 |
| boundary-distance aggregate direct control | 0.688 | +0.263 | **0.636** |

### Interpretation

The boundary-distance map did not beat the delayed feeder-amplitude branch on exact value prediction. It did, however, improve the old transition prior and produced the highest turn accuracy in this local group.

Careful reading:

```text
rung/boundary distance carries useful transition-direction information
but current boundary coordinates do not yet solve amplitude or future dominance sign
```

This is not a failure of the architecture idea. It is a narrower result:

```text
where the subsystem sits and how many boundaries it crosses matters,
but the current transforms are still using NINO/SOI-derived lower-rung surrogates.
```

The next cleaner version should keep the boundary-distance coordinates, but replace surrogate feeders with real ENSO energy-source variables: warm-water volume, thermocline depth, trade-wind stress, outgoing longwave radiation, and ocean heat content.
