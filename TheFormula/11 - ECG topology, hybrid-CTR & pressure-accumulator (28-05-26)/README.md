# 11 — ECG topology, hybrid-CTR & pressure-accumulator (28-05-26)

**Thread:** ECG/heart geometry — self-consistency of the ARA topology, a hybrid CTR-topology predictor, and a pressure-accumulator model. Single session, 28 May 2026.

**Model logic / idea:** Treat the heart's RR/ECG signal as a topology on the ARA sphere and check whether the geometry is internally self-consistent (does the same topology fall out under frame offsets / rotations / spin stand-ins?). Two predictor styles were built on top: a "hybrid CTR + topology" readout, and a "pressure-accumulator" model that treats the system as charging and releasing pressure (overlaid on the raw signal for inspection).

**Systems tested:** ECG / heart (RR intervals). This thread is single-system, fine-grain heart geometry.

**What was tested:**
- `ara_ecg_topology_self_consistency_test.py` — does the ECG topology read consistently?
- `ara_hybrid_ctr_topology_predictor.py` — hybrid CTR + topology predictor (result `.js`/`.json` + visualiser).
- `ara_pressure_accumulator_test.py` — pressure-accumulator model, with overlay HTML.
- `ara_frozen_phase_shift_audit.py` — audit of frozen phase-shift / frame-offset effects.
- `ara_terrain_spin_standin_test.py` — terrain/spin stand-in to probe sphere-rotation sensitivity.

**Key results:** This folder holds the raw test scripts, JSON results, and HTML/JS visualisers; there are no UPPERCASE `*_RESULT.md` write-ups summarising final numbers (the synthesis for the heart work lands in folder 12's `TWO_SYSTEM_ABSTRACT_COMPARISON.md`). The artefacts here are diagnostic: frame-offset analysis, frozen-phase-shift audit, and sphere-rotation results, indicating the session was probing whether the ECG topology is robust to the geometric frame chosen.

**What was NOT tested / open:** No standalone results doc was written for this stage, so headline correlations are not recorded in-folder. The pressure-accumulator and hybrid-CTR predictors are exploratory (visual overlays, not benchmarked against strong baselines here).

**Key files:**
- `ara_ecg_topology_self_consistency_test.py`
- `ara_hybrid_ctr_topology_predictor.py`
- `ara_pressure_accumulator_test.py`
- `ara_frozen_phase_shift_audit.py`
- `ara_terrain_spin_standin_test.py`
