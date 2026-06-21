# 05 — Gear & Universal Cascade

**Thread:** Gear-mechanics view of coupled rungs, built up into a single system-agnostic "Universal Cascade" forecaster. Folder dated 20-05-26.

## Model logic / idea
Treat coupled φ-rungs as meshed gears: a matched anti-phase pair (e.g. NINO↔SOI) has gear ratio 1 (same rung, equal amplitudes); cross-rung coupling transfers power by the gear ratio. The `UniversalCascade` predictor encodes three reusable framework innovations with **no per-system tuning**: (1) ARA-asymmetric tension (engines linear, consumers log), (2) three-way φ²/2φ Space-Time-Rationality coupling, (3) 1/φ³ momentum feedback. Later "universal cascade" variants add a quarter-flip (geometry inversion through a singularity), snapback, and half-φ ARA-rung coordinate schemes.

## Systems tested
ENSO (NINO 3.4 with SOI/PDO chain, ARA≈2 harmonic) and ECG / heart (AV-node coupler, multi-subject, ARA≈φ engine). Same architecture, different inputs.

## What was tested
`gear_test1/2/3` (same-rung amplitude, cross-rung power, within-system power), `gear_test_av_node_coupler` / `gear_av_multi_subject`, gear cascade chained/full/predictive-blind on NINO; `universal_cascade_predictor.py` plus variants: snapback, quarter-flip (ENSO + ECG), v2_honest (+patternB), v3, φ_k amplitude, half-φ ARA rungs; `ara_rung_coordinate` tests; cascade residual analysis with visualizers.

## Key results
No `.md` summaries; outputs in `*_data.js`/`*_data.py` viz feeds and HTML visualizers. The naming carries the honesty trail: `universal_cascade_v2_honest.py` and `_patternB` mark a re-derivation after an earlier version was found wanting, and `cascade_residual_analysis.py` exists to inspect what the cascade leaves unexplained. `gear_predictive_nino_blind.py` is the blind-forecast variant.

## What was NOT tested / open
Per-variant forecast skill vs baselines is not summarized here. The quarter-flip / singularity-inversion idea is implemented but its validation is carried forward (singularity-flip remained an open conjecture in later notes).

## Key files
- `universal_cascade_predictor.py` — system-agnostic gear cascade (3 framework innovations)
- `gear_test1_same_rung_amplitude.py` — gear-ratio-1 matched-pair check
- `universal_cascade_v2_honest.py` — re-derived honest version
- `universal_cascade_quarter_flip_test.py` / `_ecg.py` — singularity quarter-flip
- `cascade_residual_analysis.py` — residual diagnostics
