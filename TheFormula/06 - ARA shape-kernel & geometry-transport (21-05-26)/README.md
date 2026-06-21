# 06 — ARA shape-kernel & geometry-transport

**Thread:** Replace the cosine in the wave model with a learned accumulate/release **shape kernel**, then transport the ARA geometry state forward. Folder dated 21-05-26.

## Model logic / idea
Instead of assuming a sinusoid, learn two median half-cycle shapes from past data only — a *release* shape (peak→trough) and an *accumulate* shape (trough→peak) — and let ARA decide how much of each cycle is release vs accumulation. Prediction reads the current rung's ARA and phase (from the observed bandpass value and slope), then advances phase by `h / period` and reads the learned shape. The **geometry-transport** step turns the ARA state into transport primitives and trains a forward operator strictly on past origins (for origin `t`, horizon `h`, only anchors `s` with `s+h < t`). This is the strict-causal, leak-guarded backbone reused by threads 07–10.

## Systems tested
ENSO (NINO 3.4) primarily; ECG / heart (including raw MIT-BIH ECG); climate visualizers. The `automated_validation_harness.py` benchmarks ENSO, Solar (SILSO sunspots) and ECG (nsr001) together.

## What was tested
`ara_shape_kernel_test.py` (learned kernel vs cosine), `ara_shape_kernel_ecg_test` / `_raw_mit_ecg`, `ara_state_geometry.py` (anchor-state ARA rungs), `ara_geometry_transport_test.py` (geometry→transport primitives→forecast vs persistence), and `automated_validation_harness.py` (ARA models — canonical blended, base-sweeping, dual-role — vs Persistence/Mean/AR(p)/Fourier baselines and negative controls).

## Key results
Outputs in `*_data.js` and HTML visualizers (no prose `.md` here). The thread's contribution is methodological: a reusable strict-causal shape-kernel + geometry-state pipeline with an explicit benchmark harness against standard baselines, which the later phase-flow threads (09) build directly on.

## What was NOT tested / open
No consolidated result narrative in-folder; quantitative win/loss vs baselines is in the data dumps and is carried forward into thread 09's documented finding that lag-ridge still beats the geometry branches on MAE.

## Key files
- `ara_shape_kernel_test.py` — learned accumulate/release kernel vs cosine
- `ara_geometry_transport_test.py` — geometry-state forward transport (strict-causal)
- `ara_state_geometry.py` — anchor-state ARA rung extraction
- `automated_validation_harness.py` — ENSO/Solar/ECG benchmark vs baselines
