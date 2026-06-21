# 07 — Triangle-balance, causal-flow & phi-distance friction

**Thread:** Three-system (triangle) balance features, a reusable causal-flow forecast operator, and testing the hypothesis that temporal friction equals distance from φ. Folder dated 22-05-26.

## Model logic / idea
Three ideas explored on the strict-causal geometry-transport base from thread 06:
1. **Triangle balance** — a system-neutral feature engine (`ara_triangle_balance_core.py`) over a target/counter/third triad (e.g. NINO / SOI / PDO), capturing how a third system closes or balances a coupled pair.
2. **Causal flow** — turn the retroactively-inferred flow amount `alpha` (`future ≈ current + alpha·(natural_phase_advance − current)`) into a forecast by training alpha only on completed pairs `s+h<t`, asking whether flow is reusable/predictable.
3. **φ-distance friction** — test Dylan's hypothesis that temporal friction ≈ `|ARA − φ|`, so that `flow = ARA/(ARA+friction)` approaches 1 at ARA=φ (the engine peak).

## Systems tested
ENSO (NINO 3.4 + SOI/PDO triad) throughout; the triangle-balance core is written to also accept ECG-derived and solar/planetary triads.

## What was tested
`ara_triangle_balance_enso_test` and `_universal_enso_test`, `ara_counter_balance_enso_test`, `ara_gear_coupled_transition_test`, `ara_geometry_state_transition_test`, `ara_retroactive_flow_test` → `ara_causal_flow_prediction_test`, `ara_temporal_friction_diagnostic` → `ara_causal_friction_prediction_test`, `ara_phi_distance_friction_test` (+ `_bk_fit`), and `ara_temporal_pocket_diagnostic_test`.

## Key results
Outputs in `*_data.js`; scoring branches are explicitly causal (decoder trains on anchors `a<t`, lag baseline on `s+h<t`, retro-correlation sections flagged diagnostic-only). This thread refines the forward-transport operator and tests the φ-distance friction law that feeds the tick-engine of thread 08.

## What was NOT tested / open
No prose result doc in-folder; whether φ-distance friction or causal-flow alpha actually beats the lag baseline is left to the data dumps (thread 09 later concludes lag-ridge remains the best point forecast).

## Key files
- `ara_triangle_balance_core.py` — system-neutral triad feature engine
- `ara_causal_flow_prediction_test.py` — predictable-flow (alpha) forecast test
- `ara_phi_distance_friction_test.py` — friction = |ARA − φ| hypothesis
- `ara_temporal_friction_diagnostic.py` / `ara_temporal_pocket_diagnostic_test.py`
