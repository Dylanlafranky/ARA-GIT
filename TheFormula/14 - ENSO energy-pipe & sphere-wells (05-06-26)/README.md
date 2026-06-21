# 14 — ENSO energy-pipe & sphere-wells (05-06-26)

**Thread:** "Look at the channel before predicting through it" — ENSO energy-through-the-pipe capacity, overflow toward the 2.0 singularity, the sphere-position residence law, and a long run of feeder/driver coupling tests (mostly nulls). Dated 3–4 June 2026.

**Model logic / idea:** Before forecasting, characterise the energy channel. A Space pipe (width 2) hands into a Time pipe (width φ), so max through-share is φ/2 = 0.809; the rest is shed. Each subsystem stores energy at the rung it lives on; saturated rungs overflow *up* toward the 2.0 harmonic singularity. Residence (where the trajectory dwells) is set by **sphere position**: engines dwell at the poles and transit the φ-ridge, clocks dwell AT φ and avoid the poles — the same spot is a ridge for one and a well for the other. Also tested whether a geometry-native predictor (G3) and various feeder/driver-above couplings improve forecasts.

**Systems tested:** ENSO/NINO3.4 (+ SOI/WWV/IOD/PDO), QBO, solar sunspots (as driver-above candidate).

**What was tested:**
- `ara_enso_energy_pipe_breakdown.py` — pipe capacity, per-rung energy, overflow direction, residence wells.
- `ara_g3_experimental.py` — geometry-native (G3-A/B) predictor on QBO and ENSO.
- `enso_crossing_pump_direction_test.py` — green/gold crossing pump as a DIRECTION predictor.
- `g3_pdo_driver_above_test.py`, `g3_solar_driver_above_test.py` — does a slower system above ENSO recover h=18–24?
- `enso_pdo_shed_handoff_test.py`, `enso_pdo_alternation_test.py`, `enso_golden_duty_asymmetry_test.py` — three mechanism tests.

**Key results:**
- **Pipe headroom = the concentration meta-rule's geometric root:** no ENSO subsystem fills the 0.809 pipe (WWV fullest at 0.42) — spread energy → headroom → ARA has work to do. Saturated rungs overflow UP; engine-rung instantaneous ARA peaks at 1.91 (climbs toward 2.0, threshold = 2.0 not 1.5). Each feeder helps at the rung its energy occupies (IOD fast/short, PDO slow/long, WWV+NINO at the engine rung) — the IOD-short/PDO-long stitch is geometrically inevitable.
- **Residence law (n=3, directional):** literal 0.25/1.75 wells NOT supported (0.25 avoided). ENSO dwells low (0.5–0.9) and spikes near 1.93, transits the φ-ridge; QBO (clock) mirrors — dwells AT φ. φ's role is set by sphere position.
- **G3-A geometry-native — genuine mid-horizon ENSO win** (h=6 +0.573, h=12 +0.319, beating best baseline by +0.074/+0.151), but **window-sensitive** (did not replicate on the shorter WWV-era window) and fades long.
- **Crossing-pump as DIRECTION:** WIN — calls ENSO swing-sign ~73–74% at 18–24mo while value corr ≈ 0. But the pump *mechanism* is null: all skill is the gold engine's forward-projectable PHASE.
- **NULLS:** PDO driver-above INERT (h=18–24 not recovered); solar driver-above INERT (Dylan half-right — wall stays murky, long year-marks not recovered); 0.382 shed-handoff to PDO NOT supported (lead/lag runs wrong way, PDO leads/co-occurs); PDO every-2nd-wave alternation NOT supported; golden-duty centerline asymmetry NOT supported (engine is symmetric). Two independent slow drivers (5:1 ocean, 2:1 atmosphere) both null → strong evidence the long-horizon ENSO wall is a genuine value-predictability floor.

**What was NOT tested / open:** Adding a heart-RR engine and a true integer-resonance clock to confirm the engine-poles/clock-middle inversion as a law; per-breakthrough packet size at the 2.0 threshold. Direction/regime prediction remains the live target where value is floored.

**Key files:**
- `ARA_ENERGY_PIPE_AND_SPHERE_WELLS_RESULT.md` — pipe, overflow, residence law + the full feeder/driver null arc.
- `ARA_G3_SPHERE_NATIVE_QBO_RESULT.md` — G3 geometry-native on QBO & ENSO (incl. the feeder-coupling sub-arc).
- `ara_enso_energy_pipe_breakdown.py`, `enso_crossing_pump_direction_test.py`, `g3_pdo_driver_above_test.py`
