# 09 — Phase-flow, analog-flow & lag-hybrid predictors

**Thread:** Decompose ENSO forecasting into geometry-state flow + a lag/inertia carrier, and honestly benchmark every variant against a lag-ridge baseline. Dates 24–25 May 2026. This is the best-documented thread (one `*_RESULT.md` per test).

## Model logic / idea
Architecture: `raw signal → ARA mapper → geometry state S(t) → flow operator → S(t+h) → decoder → NINO3.4`. The thread iterates the **flow operator** (whole-state analog → targeted analog → phase-only ridge → regime/velocity phase flow → lag+phase hybrid → trust-gate → energy/work decomposition → risk/uncertainty layer) while keeping the decoder fixed. All branches are strict-causal and leak-guarded (`S(t)` from `data[:t]`; transition pairs `s+h<t`; decoders on anchors `a<t`; oracle branches flagged diagnostic-only).

## Systems tested
ENSO (NINO 3.4 + SOI/PDO coupling) at horizons 1/3/6/12/24/60 months.

## Key results (from the `*_RESULT.md` docs)
- **Lag ridge wins MAE at every horizon.** Across the 6/12/24-mo band: lag MAE `0.623`, corr `+0.283`.
- **ARA phase flow carries real shape/timing signal, especially at 24 mo**, where phase-only beats lag on *correlation* (`+0.347` vs `+0.167`) but loses MAE (`0.762` vs `0.617`).
- **Oracle ceilings are high** (future-geometry decoder corr `+0.765` @24mo, `+0.669` @12mo), confirming the architecture — but the strict analog flow operator estimates future geometry too bluntly to reach it. Analog-flow underperforms persistence at most horizons.
- **Predict the clock hand first:** phase-only is the best strict ARA branch; energy/rung/coupling should *gate amplitude*, not be co-predicted. Strongest oracle fields: `nino_phase` (+0.622), `soi_phase` (+0.608).
- **Hybrids/free gates damage the forecast** (coupling-gate hybrid: MAE `1.379`, corr `−0.156`). Trust-gate selectors just pick lag everywhere.
- **What survives = ARA as a diagnostic channel:** phase/lag *disagreement* flags a much riskier lag window at 24 mo (lag wrong-rate `0.467` vs `0.128`); energy-route *alignment* separates clean vs risky work states; boundary/event risk is rankable (AUC `+0.757` @6mo). First uncertainty-interval calibration **undercovers** (coverage `0.544`) and is not yet usable.

## What was NOT tested / open
A constrained (bounded, monotonic) gate instead of a free learned one; conformal/bucketed interval calibration; the multi-rung feeder block did not improve 6/12-mo prediction. `ARA_MAPPING_ATLAS_RESULT.md` shelves prediction to rebuild a diagnostic ARA atlas (234 nodes; over-2 audit flags 45 legacy catalogue nodes; galactic-φ and ATP-rotor priors corrected to "archived, not measured").

## Key files
- `ARA_PHASE_FLOW_RESULT.md` + `ara_phase_flow_predictor.py` — phase-first flow operators
- `ARA_LAG_PHASE_HYBRID_RESULT.md` + `ara_lag_phase_hybrid_predictor.py` — hybrid (lag still wins)
- `ARA_PHASE_TRUST_GATE_DIAGNOSTIC_RESULT.md` — ARA as risk/warning channel
- `ARA_TRANSITION_RISK_AND_UNCERTAINTY_RESULT.md` — risk ranking + (uncalibrated) intervals
- `ARA_MAPPING_ATLAS_RESULT.md` — diagnostic atlas rebuild
