# 02 — Cross-system ENSO forecasting & Formula v4

**Thread:** Maturing the framework into a clean "Formula v4" and testing cross-system transfer (can one system's geometry predict another's). Folder dated 20-05-26.

## Model logic / idea
`formula_v4.py` formalizes the mature claim: *a wave is energy moving through time-geometry*. ARA + framework geometry give the **shape** (`wave_shape(phase, ARA)`, normalized to [-1,1]); **energy** is a separate log-scale slider for amplitude; multi-scale is the same wave at φ-scaled time-rulers. Accumulation/release fractions are derived from ARA itself. The cross-system branch tests whether a smaller, faster system's cycle shape (e.g. ECG, heart RR) can serve as a template to forecast a larger one (ENSO), matched by relative prominence rather than substance.

## Systems tested
ENSO (NINO 3.4 with SOI/PDO/IOD/AMO/TNA/QBO/annual feeders), ECG / heart RR (PhysioNet nsr001), solar, hurricane (HURDAT2/ACE), CO₂, calcium ("rosetta"), plus cross-subject reproducibility.

## What was tested
`formula_v4` family (v4, v4_1, v4b, clean); ENSO feeder stacks (`enso_with_feeders`, `enso_three_feeders`, `enso_feeders_v2`); cross-domain `heart_predicts_enso_*` and `ecg_predicts_enso/ecg_template_for_enso`; direction-prediction, rolling-window causal, horizon-extension (with solar), reverse-inference, dynamic rung assignment, ensemble/combined/holistic predictors.

## Key results
Numbers are in `*_data.js`; no `.md` summaries here. The `heart_predicts_enso_matched.py` docstring records a key methodological catch (2026-05-03): prior cross-domain tests wrongly compared a big ENSO peak to the *average* heart cycle — fixed to prominence-to-prominence matching. `rolling_window_causal_test.py` and `direction_prediction_v2.py` signal the move toward strict-causal, direction-first scoring that dominates later threads.

## What was NOT tested / open
No consolidated result doc. Whether matched-prominence cross-domain templates actually capture ENSO amplitude is left to the data dumps rather than summarized.

## Key files
- `formula_v4.py` / `formula_v4_clean.py` — mature shape×energy formulation
- `enso_three_feeders.py`, `enso_with_feeders.py` — ENSO feeder topology
- `heart_predicts_enso_matched.py` — prominence-matched cross-domain test (with leak catch)
- `rolling_window_causal_test.py`, `direction_prediction_v2.py` — strict-causal direction scoring
