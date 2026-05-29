# MIMIC combined-lock test — oxygen for the long horizon, blood pressure for the lock, same patient

**Date:** 2026-05-29
**Status:** Exploratory cross-check. Strict-causal, correlation-led. Small-n (4 ICU patients). One more independent line of evidence — needs confirmation.
**Data:** PhysioNet MIMIC classic (`mimicdb`) — same-patient ECG + arterial blood pressure (ABP) + blood-oxygen (SpO₂), simultaneous. Records 041, 230, 417, 476. For each patient a 30-minute window was placed over the patient's lowest-SpO₂ region (where oxygen is most likely to swing).
**Scripts:** `TheFormula/heart_mimic_lock_detect_numerics.py`, `..._detect_ecg.py`, `..._forecast.py`, `..._verify.py`. Data: `heart_mimic_lock_result.json` / `.js`.

## Why this test

The slpdb third-leg result (BP sharpens the heart forecast) was n=4 sleepers with no big oxygen swings. The apnea-ECG result (oxygen stretches the horizon to ~1 minute) was a different dataset with no blood pressure. This test goes after the clean case both earlier tests were missing: **big oxygen swings AND blood pressure on the same person**, so oxygen could set the long horizon while BP sharpens the lock inside it.

## Method (strict-causal)

- Per-beat RR intervals from the ECG channel (XQRS detector), filtered 300–2000 ms.
- SpO₂ and mean ABP sampled per beat from **backward-only** windows of the 1 Hz numerics (no peeking ahead).
- Train on the first half, test on the second half. Standardize on train statistics only. Linear forecast `lstsq`. Score = correlation of predicted vs actual RR at horizons 5/10/20/40/80 beats.
- Four models compared on identical features-plus-extras: heart-only, +O₂, +BP, +both. Lift is measured against heart-only (apples to apples). Persistence floor reported separately in `..._verify.py`.

## Result (mean lift over heart-only, 4 patients)

| horizon (beats) | +O₂ | +BP | +both |
|---|---|---|---|
| 5  | −0.028 | **+0.014** | +0.002 |
| 10 | +0.006 | **+0.072** | +0.061 |
| 20 | −0.023 | **+0.072** | +0.058 |
| 40 | −0.001 | **+0.138** | +0.123 |
| 80 | +0.015 | +0.001 | +0.015 |

**Blood pressure sharpens the lock again — now on a second, independent dataset (ICU patients, not sleepers).** It is the only leg that lifts the forecast consistently across the mid-horizons (10–40 beats). The combined model tracks BP; oxygen adds almost nothing on top of it.

The cleanest single patient is **476**, the one with a genuine large oxygen swing (SpO₂ ranged 45 points across the window). There, +BP lifts every horizon: +0.117 (h5), +0.152 (h10), +0.182 (h20), +0.130 (h40), +0.049 (h80) — and +O₂ alone still only adds ~+0.01. So even where oxygen swings hardest, BP carries the lock.

## What did NOT reproduce, and the honest reading

The apnea-ECG claim — *oxygen sets the long horizon* — **did not show up in MIMIC.** Oxygen added little at any horizon, including h80 (~1 minute at these heart rates). The most likely reason is medical: **ICU oxygen is actively managed** (ventilators, supplemental O₂), so SpO₂ swings are damped compared with the violent natural desaturations of free-breathing apnea patients. The driver has to actually move for the heart to track it. Apnea patients desaturate to 47–78%; these ICU patients mostly sit near 90–99% with small excursions, and 476 is the only one with a real dip.

So this test confirms one leg and qualifies the other:
- **Confirmed (2nd dataset): BP / autonomic-baroreflex output is the independent leg that tightens the heart's forecast.** This now holds across sleepers (slpdb) and ICU patients (mimicdb).
- **Qualified: oxygen extends the horizon only when oxygen actually swings.** In medically-managed patients it is too flat to ride. The apnea-ECG horizon stretch likely needed the big natural desaturations to appear.

## Honest scope / caveats

- n = 4 patients, one 30-minute window each. Lifts are modest (+0.05 to +0.14 corr) and this is a single cross-check, not a confirmation.
- Strict-causal: train/test split, backward-only driver windows, standardize on train, persistence floor reported. No leakage found.
- A stronger future test would select windows by SpO₂ *variance* (not just low mean) across many more patients, or use the MIMIC-III matched waveform subset for patients with documented apnea/weaning events where oxygen genuinely swings while BP is also recorded.

## Files
- `TheFormula/heart_mimic_lock_detect_numerics.py` — find each patient's oxygen-swing window, cache SpO₂ + ABPmean
- `TheFormula/heart_mimic_lock_detect_ecg.py` — RR per beat from ECG, sample drivers per beat (backward windows)
- `TheFormula/heart_mimic_lock_forecast.py` — strict-causal forecast, four models, correlation-led
- `TheFormula/heart_mimic_lock_verify.py` — persistence-floor check
- `TheFormula/heart_mimic_lock_result.json` / `.js` — result data
