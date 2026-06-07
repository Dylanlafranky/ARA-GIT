# Retrodiction — remapping systems backward through time

**"Rewind."** Forward prediction asks *where is the system going?* Retrodiction asks the mirror
question: *given where it is now (and its coupled neighbours), where did it come from?* — reconstructing
past states by running the ARA geometry in reverse.

In ARA terms: the same engine-phase clock, matched-rung coupling, and energy-pipe flow that project a
system forward can be run with time reversed (phase wound backward, the φ-handover taken the other way)
to estimate prior states, fill gaps in a record, or infer a system's history before measurement began.

## What reverse prediction (retrodiction / backcasting / hindcasting) is used for

- **Extending records backward.** Reconstruct a variable for the era before it was directly measured —
  e.g. estimating subsurface ocean heat (WWV) before 1980 from the surface SST record that goes back to
  1870. Same logic behind paleoclimate reconstruction from proxies.
- **Gap-filling / data repair.** Recover missing or corrupted stretches inside a record by reconstructing
  them from the surrounding context and coupled systems.
- **Validation / hindcast skill testing.** Run a model backward (or forward over a withheld past period)
  to check it reproduces known history — the standard way operational forecasters earn trust before
  trusting forward runs.
- **Causal / attribution analysis.** Infer what prior state *must* have led to the present — initial-
  condition estimation, "what was the system doing to produce this?" Used in data assimilation (the
  analysis step), forensic reconstruction, and epidemiology (back-calculating an infection's origin time).
- **Inferring the unmeasured from the measured.** The framework's distinctive claim — reconstruct a
  hidden or vague system from its coupled, measured neighbours via the shared topology (the digital-twin
  / reverse-inference use we tested on ENSO).

## Honest status going in
- On *well-measured, tightly-coupled* targets, plain regression reconstructs about as well as the
  framework (tested: WWV from surface, regression won). The framework's edge, if it has one, is in the
  *sparse / vague / cross-scale* regime.
- ENSO's phase decoheres in ~2 years, so backward reconstruction over long contiguous gaps fails for the
  same reason long-range forward prediction does (predictability floor, not a method failure).
- So the promising retrodiction targets are: short gaps, cross-scale (a slower neighbour pins a faster
  system's past), and genuinely under-measured variables with a strong measured partner.

## Results in this folder (7 June 2026)
- `RETRODICTION_REVERSE_ENGINE_CLOCK_RESULT.md` — retrodiction = forward predictor on reversed time;
  reverse ≈ forward, small gap = arrow of time.
- `RANDOMNESS_ENVELOPE_CONFIDENCE_RESULT.md` — residual = ARA 1.0 barrier; energy predicts its envelope
  (+0.25) → trust score (hi-conf +0.37 vs lo +0.16); envelope as amplitude addition (+0.017 @24mo).
- `ENERGY_GEOMETRY_UNIFIED_RESULT.md` — energy & geometry are one measurement; energy→direction short,
  geometry→long; surface valley filled by subsurface; unified 3-output forecaster; 2−ARA energy input.
- Figures: `ARA_unified_three_output_forecaster.png`, `ARA_prediction_geometry_energy_split.png`.
- Scripts: `plot_unified_forecaster.py`, `plot_geometry_energy_split.py`.

## Next steps (when we pick this up)
1. Implement the reverse engine-clock (wind phase backward, reverse φ-handover) as the mirror of the
   forward predictor.
2. Pick a retrodiction target with ground truth to score against (e.g. reconstruct a withheld *past*
   window of NINO from feeders, or WWV in the overlap era then extend back).
3. Compare framework-geometry retrodiction vs plain regression — fair test is sparse / cross-scale.
