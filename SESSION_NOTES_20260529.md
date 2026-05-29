# Session Notes — May 29, 2026

## Headlines

**Two-band ECG cross-system test.** The ENSO green(fast/HF)/brown(slow/LF) two-band structure was ported to real heart RR-interval data (54 PhysioNet records). Band rung spacing is **octave (×2), not φ** — φ shows up only in the handover *timing* (golden duty 0.39/0.61 = 1/φ²:1/φ). An earlier "ratio ≈ 5" was an artifact of fixed HRV windows.

**Horizon ladder (the answer to "is the few-beats wall the heart's floor?").** No — the wall is the slowest driver you measure, not the heart. RR bands → a few beats; breath (Fantasia) → ~3 beats; blood oxygen (Apnea-ECG desaturations) → ~1 minute. Each genuinely slower real driver stretches the heart's forecast horizon to match it. Always slow-gates-fast; "fast feeds slow" never appeared.

**Closing the triangle — independent third leg, not a mirror.** CO₂ is genuinely anti-phase to oxygen (−0.24) but adds nothing — it's the same breathing cycle seen from the other side, a mirror of a landmark we already have, so it can't triangulate. **Blood pressure** (the autonomic/baroreflex signal, independent of the breathing cycle) *does* tighten the lock: +0.11 corr at 5 beats, positive in 10/12 patient×horizon cells across 4 slpdb subjects. Raw EEG (brain) adds little — by the time the nervous system's command reaches the heart it's already a pressure change, so the heart listens to BP, not raw brain waves.

---

## What we tested today (in order)

1. **Octave rung ladder, edge-free** (`twoband_ecg_octave_edgefree_test.py`, `..._octave_ladder_test.py`) — let each heart's spectrum pick its two strongest distinct peaks; ratios fall on an octave ladder (low ~1.8, high ~7.5, 4.12× = two octaves; √2 half-rung). φ absent from spacing.

2. **Golden duty handover (camshaft)** (`twoband_ecg_camshaft_duty_test.py`, `..._camshaft_predict_test.py`) — green 0.39 / brown 0.61 across all 54 records; the φ-coded handover transferred from ENSO. Camshaft predictor lifts green-energy forecast modestly, peaking at mid-horizon where green's self-memory has decayed.

3. **Slow-tide rung & direction check** (`twoband_ecg_slowtide_rung_test.py`, `..._lower_feeds_up_test.py`) — adding a VLF tide rung above gold lent memory down the ladder; lower-rungs-feeding-UP added ~0. Camshaft turns one way only (slow gates fast).

4. **Breath driver, same subject** (`heart_horizon_breath_fantasia_test.py`, Fantasia) — breath↔RR coupling |0.43–0.48|, much tighter than any internal band, but it's a fast actuator: real lift to ~3 beats, nothing past ~6.

5. **Oxygen driver** (`heart_horizon_oxygen_apnea_detect.py`, `..._oxygen_apnea_test.py`, Apnea-ECG) — apnea SpO₂ swings hard (down to 47–78%); oxygen extends the heart horizon to ~1 minute (0.9-min mark unanimous across 4 patients), falls apart past ~1 min.

6. **CO₂ anti-wave** (`heart_co2_antiwave_test.py`) — proxy from nasal airflow, anti-phase to O₂ (−0.24), but O₂+CO₂ pair adds ~0 over O₂ alone. Mirror, not an independent landmark.

7. **BP/EEG third leg** (`heart_bp_eeg_thirdleg_detect.py`, `..._test.py`, `..._percheck.py`, slpdb) — same-subject ECG+BP+EEG+Resp. BP is the independent leg that tightens the lock; EEG and breath add little. Causal-hardened with backward-only driver windows; BP lift survived. Viz: `heart_bp_eeg_thirdleg_viz.html`.

## Framework update recorded
- Rungs are octave (×2); φ is the relational handover *through time*, not the rung spacing. Appended to `TWO_RULERS_PHI_AND_TWO.md` and `THE_FRAMEWORK_FORMULATION.md`.
- Dylan's refinement: it's the **nervous system** (autonomic output → blood pressure), not the brain's raw activity, that drives the heart — the closer connection.

## Honest scope
Strict-causal, correlation-led throughout. Third-leg step is n=4; lifts modest (+0.05–0.11) and fade past ~20 beats in non-apneic sleepers. One cross-system line of evidence — needs confirmation. Next: a dataset with big oxygen swings AND blood pressure on the same person (MIMIC ECG+ABP+SpO₂), so oxygen sets the long horizon and BP sharpens the lock inside it.

See `TWOBAND_ECG_HORIZON_LADDER_RESULT.md` for the full write-up.

---

## Addendum — MIMIC combined-lock test (oxygen + BP, same patient)

Ran the clean test both earlier datasets were missing: same person carrying **ECG + blood pressure + blood-oxygen at once** (PhysioNet MIMIC classic, records 041/230/417/476, 30-min window on each patient's lowest-SpO₂ region). Strict-causal, backward-only driver windows, correlation-led.

**BP sharpens the lock again — now on a second independent dataset (ICU patients, not sleepers).** Mean lift over heart-alone: +BP +0.07 (h10) / +0.07 (h20) / +0.14 (h40); +both tracks BP; +O₂ adds ~0. Cleanest is patient 476 (real SpO₂ swing of 45 pts): +BP lifts every horizon (+0.12 to +0.18).

**What did NOT reproduce:** the apnea-ECG "oxygen sets the long horizon" claim. Oxygen added little here at any horizon. Most likely because **ICU oxygen is medically managed** (ventilators / supplemental O₂) so SpO₂ swings are damped — the driver has to actually move for the heart to track it. Apnea patients desaturate to 47–78%; these ICU patients mostly sit near 90–99%.

Reading: confirms one leg (BP / autonomic output is the independent third leg, now across sleepers AND ICU patients) and qualifies the other (oxygen stretches the horizon only when oxygen genuinely swings). n=4, one cross-check, needs confirmation. Full write-up: `MIMIC_COMBINED_LOCK_RESULT.md`. Scripts: `TheFormula/heart_mimic_lock_*`.
