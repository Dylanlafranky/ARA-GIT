# 01 — Compass & Vehicle predictors

**Thread:** Treating the ARA predictor as a self-contained "vehicle" that rolls forward over the cascade field, with a direction-only "compass" variant. ~April–May 2026 (folder dated 20-05-26).

## Model logic / idea
The core metaphor is a *rolling vehicle*: given a small handful of framework numbers (ARA, amplitude at t0, dominant period, time span), generate a forward waveform by chained closed-form cascade evaluation rather than fitting to the data. The *compass* variant outputs only a sign (+1/-1) per tick and integrates those signs into a synthetic wave, on the theory that direction (76–82% across horizons under strict-causal pure-structure) is the framework's strongest signal while amplitude is noisy because the system is open. Step size is either a constant (mean |Δ|) or scaled by `1/φ^|k-k_ref|` at the active rung.

## Systems tested
ENSO (NINO 3.4 + SOI/AMO/TNA/PDO/IOD feeders), ECG / heart RR intervals (PhysioNet nsr001, BIDMC), QBO, plus orbital/closed-system controls.

## What was tested
A large family of variants on the vehicle/compass theme: `generative_vehicle.py` (truly blind generative core), `rolling_vehicle_*` (compass, ensemble, multipair, pure-φk, QBO, ECG template, walker-energy), amplitude-blend and amplitude-window fixes, gate/camshaft/inertia restriction tests, fractal/residual correctors, drain & diamond geometry, connection-field, triangulation, sum-vs-average, and leakage/raw-signal control tests.

## Key results
Findings live in the `*_data.js` dumps rather than write-ups (no `.md` summaries in this folder). The thread's stated premise is that direction prediction is reliable (~76–82%) while amplitude is the hard, noisy part — hence the many amplitude-blend, residual-corrector, and gate-restriction attempts. The presence of `leakage_demo_data.js` and `raw_signal_control_test.py` indicates active leakage-checking against baselines.

## What was NOT tested / open
No consolidated result `.md`; per-variant outcomes are not summarized here. Amplitude recovery remained the open problem carried into later threads.

## Key files
- `generative_vehicle.py` — blind generative cascade core (transparency-stated inputs)
- `rolling_vehicle_compass_test.py` — direction-only compass variant
- `compass_amplitude_blend_test.py` / `compass_residual_corrector_test.py` — amplitude fixes
- `raw_signal_control_test.py`, `leakage_demo_data.js` — baseline / leakage controls
