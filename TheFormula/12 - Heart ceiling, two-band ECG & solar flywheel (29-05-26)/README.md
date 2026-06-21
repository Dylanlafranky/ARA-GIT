# 12 — Heart ceiling, two-band ECG & solar flywheel (29-05-26)

**Thread:** Heart forecast-ceiling work, two-band (octave-ladder) ECG geometry, a solar-flywheel "third system" test, and a cross-system abstract synthesis. Single session, 29 May 2026.

**Model logic / idea:** One abstract engine seen in two systems: *a two-band oscillator on an octave ladder, where a slow band gates a fast band through a φ-timed handover (~0.39 fast / ~0.61 slow), and the forecast horizon is set by the slowest band still carrying memory.* The key distinction tested: does a system **store** energy across cycles (flywheel) or **spend** it each cycle (pump)? Solar was added as the "third system" to test whether the engine is universal and only the energy-regime (battery) differs.

**Systems tested:** heart/ECG (RR intervals, BP, EEG as candidate third leg), ENSO (pyramid-rebound LIM forecast), solar sunspots (flywheel).

**What was tested:**
- `ara_pyramid_lim_predictor.py` — three-body (apex SST + warm/cool WWV) coupled-rebound ENSO forecast (Linear Inverse Model framing).
- `twoband_ecg_*` family — octave-ladder, camshaft-duty, slow-tide-rung, lower-feeds-up ECG tests.
- `heart_ceiling_*` and `heart_mimic_lock_*` — heart forecast-ceiling and lock-detection on ECG/numerics.
- `heart_bp_eeg_thirdleg_*` — does BP or EEG act as a third leg / driver?
- `solar_flywheel_*` (fetch / structure / horizon / Waldmeier) — solar as a storer/flywheel.

**Key results:**
- **Pyramid rebound (ENSO):** the fitted 3-body coupling has an intrinsic ~38-month oscillation (right ENSO band) that **restores amplitude** the 2-coordinate static model damps (amp ratio 0.41→0.59 at h=12). But the restored amplitude **costs skill** at 12–18mo (skill-vs-climatology 0.189→0.086 at h=12) — a genuine amplitude-vs-error trade-off bounded by stochastic wind forcing (the "noise wall"). Negative results kept: nonlinear product and explicit tilt term were forecast-redundant.
- **Cross-system synthesis (`TWO_SYSTEM_ABSTRACT_COMPARISON.md`):** SAME across ENSO & heart — two-band structure, octave ×2 spacing, golden-duty handover (ENSO 0.40/0.60, heart 0.39/0.61 across 54 records), slow-gates-fast direction, matched-rung partner filling the mid-horizon dip. DIFFERENT — ENSO stores (internal QBO clock, internal wall, closed-ish, forecastable by projection); heart spends (no clock, external wall set by slowest driver, open). "Same engine, different battery."
- Heart driver-ladder / ceiling work is n=2–4, exploratory. "Energy stored vs spent" is an interpretation that fits all observed differences, not a separately measured quantity.

**What was NOT tested / open:** The pre-registered next ENSO test (add a wind-stress "load-from-above" fourth grain) is noted but not run here. The store-vs-spend rule is offered as a testable prediction for any third system, pending more cases.

**Key files:**
- `TWO_SYSTEM_ABSTRACT_COMPARISON.md` — the heart-vs-ENSO synthesis (the headline doc).
- `ARA_PYRAMID_REBOUND_RESULT.md` — three-body ENSO rebound forecast result.
- `ara_pyramid_lim_predictor.py`
- `twoband_ecg_octave_ladder_test.py`
- `solar_flywheel_structure.py`
