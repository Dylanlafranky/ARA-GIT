# Two-band ECG cross-system test → horizon ladder → independent third leg

**Date:** 2026-05-29
**Status:** Exploratory cross-system test. Multiple independent lines, all strict-causal and correlation-led. Small-n on the third-leg step (4 subjects). Needs confirmation.
**Data:** PhysioNet only — normal-sinus-rhythm-rr-interval-database (54 records), Fantasia (RESP+ECG), Apnea-ECG (ECG+SpO2+resp), MIT-BIH Polysomnographic / slpdb (ECG+BP+EEG+Resp).
**Scripts:** `TheFormula/twoband_ecg_*`, `TheFormula/heart_horizon_*`, `TheFormula/heart_co2_antiwave_test.py`, `TheFormula/heart_bp_eeg_thirdleg_*`. Viz: `TheFormula/heart_bp_eeg_thirdleg_viz.html`.

## 1. Porting the ENSO two-band structure to the heart

The ENSO green(fast/HF) / brown(slow/LF) two-band structure was abstracted and run on real RR-interval data. Three ENSO signatures were tested for cross-system reproduction:

- **Octave band spacing (×2) — HOLDS.** Edge-free (no fixed HRV windows; each heart's spectrum picks its two strongest distinct peaks): ratios fall on an **octave ladder**. Two families, low ~1.8 and high ~7.5, separated by 4.12× = exactly two octaves; √2 appears as the half-rung (geometric midpoint between octave rungs). **φ does not appear in the band spacing.** An earlier "ratio ≈ 5" was a measurement artifact of forcing peaks into fixed HF/LF windows — no heart actually sits near 5.
- **Golden duty handover (camshaft) — HOLDS.** Fraction of time each band's amplitude dominates: green 0.39 / brown 0.61 across all 54 records — dead-on 1/φ² : 1/φ. ENSO was 0.40/0.60. This is the φ-coded piece, and it lives in the *handover timing*, not the rung positions.
- **Murk-point at home/φ^1.75 — FAILS (system-specific).** Heart HF/LF are stochastic/broadband, not quasi-periodic clocks like ENSO's QBO, so the deterministic forecast-shadow horizon does not transfer.

**Reading:** band *geometry* (rung spacing) is the system's own structure and is octave (×2); the φ-coded *handover duty* is the universal piece that transferred. φ lives in the relational timing through time, not in where the rungs sit.

## 2. Horizon ladder — the answer to "is the few-beats wall the floor?"

No. The wall was the slowest driver we were looking at, not the heart.

| driver measured | forecast horizon reached |
|---|---|
| RR internal bands only | a few beats |
| breath (Fantasia, same subject) | ~3 beats (seconds) |
| blood oxygen (Apnea-ECG, big desaturations) | ~1 minute |

Each genuinely slower real driver stretches the heart's horizon to match its own timescale. **The forecast horizon is set by the slowest real driver you can measure, not by the fast system itself.** Direction is always slow-gates-fast (the slow band lends memory to the fast one, peaking at the horizon where the fast system's self-memory has decayed). "Fast accumulates into slow" (up the ladder) has not appeared in any test.

Breath has the *tightest coupling* to the heart (|corr| 0.43–0.48, far above any internal RR band) but it is a *fast* actuator — it helps only ~3 beats out. Oxygen is the slower setpoint and buys ~1 minute.

## 3. Closing the triangle — the third leg must be independent, not a mirror

Oxygen alone gives a lean, not a lock (one landmark). Two candidates for the third leg were tested:

- **CO₂ anti-wave — does NOT close the triangle.** A CO₂ proxy built from nasal airflow came out genuinely anti-phase to oxygen (corr −0.24), but adding the O₂+CO₂ pair to the forecast added ~0 over oxygen alone. Reason: CO₂ and O₂ are two faces of the *same* breathing cycle, carrying the same apnea information. A mirror of a landmark you already have cannot triangulate.
- **Blood pressure — DOES tighten the lock.** Found the same-subject-all-legs dataset (slpdb: ECG + BP + EEG + Resp, simultaneous). Strict-causal RR forecast with backward-only driver windows, lift over heart-alone, mean across 4 subjects:
  - **+BP (autonomic/baroreflex): +0.11 (h5) / +0.07 (h10) / +0.05 (h20)** — positive in 10 of 12 patient×horizon cells; predictions non-degenerate.
  - +breath (slpdb Resp, no apnea here): ~0.
  - +brain (EEG delta+beta log-power per beat): near 0 short, hurts long; adds nothing on top of BP.

**Reading (refines Dylan's triangle):** the leg that locks is the *independent upstream* driver, and the proximate one is **blood pressure** — the autonomic command made physical via the baroreflex. Raw EEG is one fractal level further up and too weakly/indirectly coupled per-beat; by the time the nervous system's command reaches the heart it has already become a pressure change. So the lock comes from the autonomic *output* (BP), not the brain's raw electrical activity, and not the anti-phase mirror (CO₂).

## Honest scope / caveats

- Strict-causal throughout: train first half / test second half, drivers sampled from past-only (backward) windows, benchmarked vs persistence, correlation-led. The backward-window hardening dropped the BP lift modestly but it stayed positive.
- Third-leg step is n=4 sleepers; lifts are real but modest (+0.05–0.11 corr) and fade past ~20 beats in these non-apneic subjects (no big slow swings to ride).
- This is one cross-system line of evidence. The clean next test is a dataset with big oxygen swings (apnea) **and** blood pressure on the same person (e.g. MIMIC ECG+ABP+SpO₂), so oxygen sets the long horizon and BP sharpens the lock inside it.

## Files
- `TheFormula/twoband_ecg_octave_edgefree_test.py`, `..._octave_ladder_test.py` — octave rung result
- `TheFormula/twoband_ecg_camshaft_duty_test.py`, `..._camshaft_predict_test.py` — golden duty handover
- `TheFormula/twoband_ecg_slowtide_rung_test.py`, `..._lower_feeds_up_test.py` — slow-tide rung / direction check
- `TheFormula/heart_horizon_breath_fantasia_test.py` — breath driver
- `TheFormula/heart_horizon_oxygen_apnea_detect.py`, `..._oxygen_apnea_test.py` — oxygen driver
- `TheFormula/heart_co2_antiwave_test.py` — CO₂ mirror (does not triangulate)
- `TheFormula/heart_bp_eeg_thirdleg_detect.py`, `..._thirdleg_test.py`, `..._thirdleg_percheck.py` — BP/EEG third leg
- `TheFormula/heart_bp_eeg_thirdleg_result.json` / `.js`, `heart_bp_eeg_thirdleg_viz.html` — result data + visualization
