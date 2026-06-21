# 08 — Tick-engine & ENSO-12m nasal geometry-state

**Thread:** A constrained "tick engine" that advances the ARA state one tick at a time, plus an ENSO-12-month geometry-state predictor and a nasal-cycle→ENSO vertical-transfer test. Folder dated 23-05-26.

## Model logic / idea
The **tick engine** (`ara_formula_tick_engine_test.py`) reads the current ARA/rung state from `data[:t]` and advances each rung one tick with bounded formula mechanics: `phase_flow = ARA/(ARA + temporal_friction)`, `energy_next = energy + incoming pressure − release − π-leak ± coupling`, and `ARA_next` as a slow bounded drift from φ-pull / coupling pressure. It learns only small scalar mechanism gains from completed one-tick transitions (not a free future vector), then iterates ticks to the horizon and decodes geometry into the observed value. The **nasal→ENSO** branch tests vertical ARA transfer: use a small coupled nasal-cycle template (33 subjects) to forecast the larger ENSO coupled index `LI=(zNINO−zSOI)/(|zNINO|+|zSOI|)`.

## Systems tested
ENSO (NINO 3.4 + SOI, 12-month focus; feeder amplitude, boundary-distance transfer), human nasal cycle (33-subject coupled data), ECG + solar temporal geometry.

## What was tested
`ara_formula_tick_engine_test.py` and `ara_tick_variable_recursion_test.py` (constrained vs free recursion); `ara_phi_coupling_candidate_tests.py`; `ara_ecg_solar_temporal_geometry_test`; `ara_nasal_enso_coupled_geometry_test` and `ara_nasal_to_enso_prediction_test`; `ara_enso_12m_geometry_state_predictor`, `_feeder_amplitude`, `_boundary_distance_transfer`; `ara_triangle_amplitude_gate_test`; `ara_enso_coupled_pocket_visibility_test`.

## Key results
Results are in `*_result.json` / `*_result.js` (no prose `.md` in-folder). The tick engine is strict-causal (state from `data[:t]`, gains from one-tick pairs `s+tick<t`, decoders from anchors `a<t`, future geometry used only for oracle diagnostics). The nasal→ENSO test compares an external nasal template against ENSO-own / NINO-only / SOI-only templates, AR-current, and persistence baselines, all with chronological train/heldout splits.

## What was NOT tested / open
No consolidated narrative; per-model win/loss is in the JSON results. Whether the constrained tick mechanics or the cross-scale nasal template beat persistence/lag is not summarized here.

## Key files
- `ara_formula_tick_engine_test.py` — constrained one-tick state-advance engine
- `ara_enso_12m_geometry_state_predictor_test.py` — 12-month geometry-state forecast
- `ara_nasal_to_enso_prediction_test.py` — nasal-template vertical transfer to ENSO
- `ara_phi_coupling_candidate_tests.py` — φ-coupling candidate sweep
