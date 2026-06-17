# Frozen-Sphere "Mold-Then-Roll" prediction — honest negative (13 June 2026)

**Dylan La Franchi & Claude.** Two strict-causal tests of Dylan's epiphany that **the wave
*is* the topography**: mold each system's sphere ONCE on the first 63% (golden 1/φ split),
**freeze the shape**, and let the sphere keep its **designed motion** (spin + wobble) roll the
forecast forward. Headline metric = **correlation** (per the project rule). Builds directly on
`../Retrodiction/RIVER_LANDSCAPE_AND_THALWEG_RESULT.md` and `MORPHED_SPHERE_MODEL_AND_QUOTES.md`.

**Net result: the geometry does not beat the right baselines on VALUE in either test.** The one
real long-horizon lift comes from an *external* below-system (WWV), and a plain linear regression
captures it just as well. This is the same value-ceiling documented across the framework
("same map, not same position"; geometry's edge is direction + confidence, not the number).

---

## The model under test (Dylan's words, operationalised)
- **Wave = topography.** The observed waveform at time *t* is the cross-section of the sphere the
  trajectory is currently riding — not a ball on a separate static landscape.
- **Mold once, freeze.** Shape is fit to the actual ups/downs of the training 63%, then locked. No
  re-molding, no wobble-tuning on the test window (this kills the window-sensitivity that made the
  earlier G3 morphed-sphere edge non-robust).
- **Motion continues.** The frozen sphere keeps spinning + wobbling; the **spin of the target is
  driven by the rung BELOW** feeding energy up (WWV recharge → NINO).
- **Two feeder regimes:** *Nested-Blind* (feeder rolled on its own frozen sphere, nothing in test
  observed) and *Driver-Fed* (feeder observed in test).

**Implementation:** each sphere = a frozen phase-portrait terrain on (value, causal trailing-slope),
binned by phase, carrying the ARA rise/fall asymmetry = the molded wave-shape. One ARA step =
phase advance (spin) + relax to the cycle wall (the 1.0 sink / banks 0–2 as snap edges) + a push
from the rung below. Lean: one frozen terrain + a couple of coupling numbers, the **same model at
every horizon** (vs a baseline refit per horizon).

---

## Test 1 — Nested NINO3.4 ← WWV   (`frozen_sphere_nested_predictor.py`)
Real NOAA NINO3.4 anomaly + PMEL warm-water-volume, 1980–2025 overlap (552 mo, train 341 / test 211).
Measured coupling: **WWV leads NINO 6 months at the level** (train corr +0.582) — the recharge oscillator.

| horizon | pure sphere | nested-blind | driver-fed | AR(6) | persistence | **linear recharge** |
|---|---|---|---|---|---|---|
| 3 mo  | +0.66 | +0.53 | +0.53 | **+0.83** | +0.76 | +0.84 |
| 6 mo  | +0.35 | +0.38 | +0.38 | **+0.51** | +0.37 | +0.53 |
| 12 mo | +0.04 | +0.19 | +0.39 | +0.10 | −0.09 | **+0.42** |
| 24 mo | −0.16 | +0.09 | **+0.32** | +0.13 | −0.29 | +0.28 |

Readings:
- **Short horizons (h=3,6): AR/linear win.** The smooth single-rung sphere can't track the fine wiggle.
- **Long horizons (h=12,24): the below-driver carries it past the AR wall** — driver-fed +0.39/+0.32 vs
  AR +0.10/+0.13. Feeder split appears only past the 6-mo lead, as it should (fed > blind > pure).
- **Decisive control:** a plain **linear recharge regression** (`NINO + WWV + WWV[t-6]`) gets +0.42/+0.28
  at 12/24 — **matches or beats** the sphere. ⇒ the long-horizon win is the **feeder, not the geometry**.
- **Honest architectural positive (Dylan's prediction):** the sphere ~ties the linear model on value using
  ONE frozen model + 2 coupling numbers at all horizons, while the linear baseline refits per horizon —
  leaner, as predicted. It just doesn't *beat* it.

Result JSON: `frozen_sphere_nested_NINO_WWV_result.json`.

## Test 2 — Self-contained fractal sub-waves   (`frozen_sphere_fractal_selfcontained_predictor.py`)
Dylan's follow-on: drop the external feeder; the signal's own octave **sub-waves** are the below-system,
and a fast sub-wave **completing its cycle** hands over to the slower wave (self-contained vertical-ARA /
"the river"). Causal octave decomposition = trailing-MA cascade (exact reconstruction, no filtfilt leak).
Real NINO3.4 1870–2025 (1872 mo, train 1157 / test 715).

| horizon | fractal sub-waves | + φ-handover coupling | AR(6) | persistence |
|---|---|---|---|---|
| 3 mo  | +0.62 | +0.61 | **+0.81** | +0.77 |
| 6 mo  | +0.34 | +0.34 | **+0.51** | +0.40 |
| 12 mo | −0.08 | −0.08 | +0.06 | −0.08 |
| 24 mo | −0.11 | −0.11 | **+0.27** | −0.27 |

Readings:
- **Loses to AR at EVERY horizon**, including the long end Dylan predicted it would win.
- **φ-handover coupling came out near-inert** (coupled ≈ uncoupled to 3 dp) — the second time the inter-rung
  push went to ~zero. Flagged rather than tuned-until-it-wins.
- **Structural reason (not just wiring):** long-horizon skill lives in the **slow rungs**, which persist —
  exactly what AR already models (AR strengthens to +0.27 at h=24 = ENSO's ~4-yr recurrence). Fast sub-waves
  give only short-lived leads, so "fast completion predicts the far future" fights itself. From a signal's
  **own past**, the geometry does not beat AR on value.

Result JSON: `frozen_sphere_fractal_selfcontained_result.json`.

---

## Verdict
- **Mold-then-freeze-then-roll is a legitimate, leak-free vehicle**, and the below-driven spin mechanism
  works as designed (nested-blind genuinely forecasts the feeder and still beats pure NINO memory at h=12).
- **But on VALUE it rides the feeder, not the geometry.** External below-system (WWV) → real long-horizon
  skill, but a linear recharge regression matches it; self-contained sub-waves → loses to AR everywhere.
- **Same ceiling as the whole framework:** value goes to memory/regression; the framework's demonstrated
  edge is **direction + confidence** (prior morphed-sphere rollout: direction +0.40→+0.68; φ-thalweg
  calm-lane confidence). Those are the right next targets for this frozen vehicle — not value.
- **Honesty notes:** correlation-led; strict-causal (train-only stats, causal-only slope/decomposition, no
  zero-phase filters, NINO future never read, feeder blind in nested mode); two predictions logged before
  running — Dylan's "beats AR, driver-fed more accurate, leaner compute" **partly held** (driver-fed > blind,
  leaner ✓; beats AR only long, and not vs linear ✗); his "self-contained beats AR long-run" **did not hold**.

## Files
- `frozen_sphere_nested_predictor.py` — Test 1 (nested NINO←WWV), with the decisive linear control.
- `frozen_sphere_fractal_selfcontained_predictor.py` — Test 2 (self-contained octave sub-waves).
- `frozen_sphere_nested_NINO_WWV_result.json`, `frozen_sphere_fractal_selfcontained_result.json`.
