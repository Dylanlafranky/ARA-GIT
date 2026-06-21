# 19 — Frozen-sphere mold-then-roll (14-06-26)

**Thread:** Two strict-causal tests of "the wave IS the topography" — mold each system's sphere once on the first 63%, freeze the shape, and let its designed spin + wobble roll the forecast forward. Dated 13 June 2026. An honest negative.

**Model logic / idea:** The observed waveform at time *t* is the cross-section of the sphere the trajectory is currently riding (not a ball on a separate static landscape). Mold the shape to the training 63%, **freeze** it (kills the window-sensitivity that made the earlier morphed-sphere edge non-robust), and keep the motion: spin is driven by the rung below feeding energy up. Two feeder regimes — *Nested-Blind* (feeder rolled on its own frozen sphere, nothing observed in test) and *Driver-Fed* (feeder observed). Implementation = a frozen phase-portrait terrain on (value, causal slope), binned by phase, carrying the ARA rise/fall asymmetry; one frozen terrain + a couple of coupling numbers, same model at every horizon.

**Systems tested:** ENSO/NINO3.4 (+ WWV warm-water-volume as the below-driver).

**What was tested:**
- `frozen_sphere_nested_predictor.py` — Test 1: nested NINO3.4 ← WWV, with a decisive linear-recharge control.
- `frozen_sphere_fractal_selfcontained_predictor.py` — Test 2: drop the external feeder; the signal's own octave sub-waves are the below-system (self-contained vertical-ARA / φ-handover).

**Key results (net: honest negative on VALUE):**
- **Test 1 (nested NINO←WWV):** short horizons go to AR/linear (h=3 AR +0.83 vs sphere +0.66). Long horizons: the below-driver carries it past the AR wall (driver-fed +0.39/+0.32 at h=12/24 vs AR +0.10/+0.13), and feeder split appears only past 6mo (fed > blind > pure, as designed). **But the decisive control — a plain linear recharge regression (NINO + WWV + WWV[t-6]) — matches or beats the sphere (+0.42/+0.28).** So the long-horizon win is the feeder, not the geometry. Architectural positive: the sphere ~ties the linear model using one frozen model + 2 coupling numbers at all horizons (leaner, as Dylan predicted), it just doesn't beat it.
- **Test 2 (self-contained sub-waves):** **loses to AR at EVERY horizon**, including the long end Dylan predicted it would win. φ-handover coupling came out near-inert (coupled ≈ uncoupled to 3dp — the second time the inter-rung push went to ~zero). Structural reason: long-horizon skill lives in the slow rungs, which persist — exactly what AR already models.
- **Verdict:** mold-then-freeze-then-roll is a legitimate leak-free vehicle and the below-driven spin works as designed, but on VALUE it rides the feeder, not the geometry — the same value-ceiling as the whole framework. The demonstrated edge is direction + confidence.

**What was NOT tested / open:** Direction + confidence outputs from this frozen vehicle (the right next target, given value goes to regression). Dylan's logged predictions partly held (driver-fed > blind, leaner ✓; beats AR only long and not vs linear ✗; self-contained-beats-AR-long ✗).

**Key files:**
- `FROZEN_SPHERE_MOLD_THEN_ROLL_RESULT.md` — both tests, controls, and verdict (headline doc).
- `frozen_sphere_nested_predictor.py`
- `frozen_sphere_fractal_selfcontained_predictor.py`
