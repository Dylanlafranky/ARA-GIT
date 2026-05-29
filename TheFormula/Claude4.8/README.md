# ARA → ENSO: can the geometry forecast?

A documented chain of tests asking whether the ARA "layered-sand / pyramid"
geometry can *forecast* El Niño–Southern Oscillation (ENSO), not just classify it.
Built and validated cold on real NOAA data, with every step's reasoning,
method, result, and honest limit recorded.

**Headline:** the geometry produces a genuine, walk-forward-validated ENSO
forecast at ~6 months lead, with the driver-below carrying the skill and the
three-body rebound carrying the amplitude. Skill does not decay monotonically —
it *recurs* at ~27 months with decaying amplitude, and the recurrence period is
set by a second interannual band in the ocean (the quasi-biennial mode), not by
the fitted oscillation. Two claims that looked promising on a single window did
not survive rolling validation and are marked as such.

---

## 1. Why we tested this

The ARA framework characterises oscillating systems by Accumulation/Release
Asymmetry on a sphere: latitude = the build/release shape of the wave, longitude
= phase, depth = rate. Its stated, validated strength is *classification*. The
open question was whether the same geometry can *forecast* — specifically whether
the "layered sand" picture (nested counter-rotating coupled oscillators, each
layer driven by the one below, with a wobble from sitting in the gap between two
grains) predicts events on data it has never seen.

ENSO was chosen because it is the cleanest test bed: it has a canonical *driver
below* the surface — equatorial-Pacific Warm Water Volume (WWV), the recharge-
oscillator variable that physically leads sea-surface temperature. The geometry
maps onto ENSO directly:

| geometry | ENSO variable |
|---|---|
| apex grain (the measured coarse sand) | NINO 3.4 sea-surface temperature |
| base grain — warm | western WWV (warm pool) |
| base grain — cool | eastern WWV |
| the "fine sand below" driving the grain | sub-surface heat content / WWV |
| the wobble between two contacts | the recharge–discharge beat = events |

The guiding prediction from the geometry: **a grain cannot forecast itself; its
future lives in the layer below it.** That is the thing the chain tests.

---

## 2. The chain of action (each step: question → method → result)

The decisive metric throughout is **skill vs climatology on held-out data**.
Beating *persistence* is the weak baseline (cleared by mere mean reversion);
beating *climatology* (the long-run mean, which knows nothing about the current
state) is the real bar for genuine event forecasting.

**Step 1 — Can the grain forecast itself?**
Method: fit NINO(t+h) from NINO(t) alone (latitude/depth only), pre-2017 train.
Result: ≈ climatology (skill +0.01 at 12 mo). A single coordinate carries no
event information — exactly what the geometry predicts. *Confirmed.*

**Step 2 — Does the layer below carry forecast skill?**
Method: add WWV (the recharge driver) as the second coordinate. WWV leads NINO
by ~6 months (corr +0.50 at 6-mo lead vs +0.11 at zero lag — a clean lead).
Result: skill over climatology lifts at every lead 3–18 mo (e.g. +0.01 → +0.19
at 12 mo on the fixed split). *The conjugate coordinate carries the events.*

**Step 3 — Is the amplitude a nonlinear "beat" (grain × driver)?**
Method: add the product term. Result: no holdout lift. The relational
information is in the *linear* coupling, not a nonlinear product. *Rejected.*

**Step 4 — Is the warm/cool relation (zonal tilt) an independent coordinate?**
Method: warm and cool WWV anti-correlate (−0.36, they oppose as warm/cool should);
test whether their difference (the tilt R) adds skill beyond their sum.
Result: identical holdout score to the sum. The relation is real *anatomy* but
*forecast-redundant* — the eastern grain ≈ the NINO region (1-mo lead) and the
western signal is already in the sum. *Rejected as a forecast coordinate.*

**Step 5 — Does the three-body coupled rebound restore amplitude?**
Method: fit the coupled rate system (a Linear Inverse Model) on
state = [temperature, warm, cool]; forecast = M^h · state. The rebound
(Newton's-third-law spring-back) is the off-diagonal coupling.
Result: the fitted system has an intrinsic damped oscillation at **38 months
(3.2 yr) — emergent, not inserted** — matching ENSO's period. Integrating it
forward **restores amplitude** (amp ratio 0.41 → 0.59 at 12 mo). At 6 mo this is
nearly free (better amplitude, ~equal skill). *Mechanism confirmed.*

**Step 6 — Does the skill survive honest rolling validation?**
Method: walk-forward — refit on strictly-past data at every origin (2008–2025,
~210 forecasts) and forecast forward.
Result: **6-month skill survives** (≈ +0.25 vs climatology, robust). **12-month
skill does NOT** (negative). The earlier +0.19 at 12 mo was inflated by the
single 2017+ window containing one big El Niño. *Honest horizon ≈ 6 months.*
This corrected an overstated earlier claim.

**Step 7 — Does an asymmetric "compression" term fix the cool-phase bias?**
Motivation: the linear rebound over-predicts the cool phase by ~+0.9 °C
("ups when there should be downs") — a symmetric spring on an asymmetric system
(ENSO skewness +0.46). Method: add a piecewise/quadratic loading term from the
existing grains. Result: small, consistent improvement; does not extend the
horizon or close the cool bias. The specific "cool-loads-slower" direction was
*not* supported — the free fit preferred cool-reverts-faster. *Marginal.*

**Step 8 — Does skill recur at long lead?** (a pre-registered prediction)
Method: walk-forward skill across leads 1–54 months. Result: skill is
**non-monotonic** — it troughs near 12–19 mo and **re-emerges**, peaking near
**27 mo**, then again faintly near 53 mo, with amplitudes **decaying ~×0.27 per
ring** (a damped-oscillation envelope). The 27-mo re-emergence and the ~×0.27
decay were predicted in advance. *Confirmed (third ring at the noise floor).*

**Step 9 — Why does skill recur at 27 mo, not the 38-mo fitted period?**
Method: 156-year NINO power spectrum. Result: ENSO has **two interannual bands
of comparable power** — a quasi-biennial band at ~28 mo and a low-frequency band
at ~42–67 mo (QB/LF power ratio 0.97). The fitted 38-mo mode is a single-mode
*average* of the two. The skill recurrence (27 mo) locks to the **quasi-biennial
band** (28 mo), not the fitted mode. *Two mechanisms, two features:* damping sets
the ring **amplitude** decay; the second wave sets the recurrence **spacing**.

---

## 3. Results summary

Walk-forward skill vs climatology (refit-on-past, 2008–2025):

| model rung | adds | 6-mo skill | 12-mo skill |
|---|---|---|---|
| grain alone | temperature forecasts itself | +0.12 | −0.01 |
| + driver below | warm-water recharge | **+0.25** | +0.02 |
| + rebound (3-body) | warm+cool coupled, 3.2-yr spring | +0.23 | −0.13 |
| + compression | asymmetric loading | +0.24 | −0.10 |

Skill recurrence (forecast correlation peaks): 0.96 @ 1 mo → 0.27 @ 27 mo →
0.07 @ 53 mo (≈ ×0.27 per ring; third ring at the noise floor).

Spectrum: quasi-biennial ~28 mo and low-frequency ~42–67 mo, near-equal power.

---

## 4. Honest verdict

- **Validated:** a 6-month ENSO forecast over climatology from the ARA pyramid
  geometry, driver-below carrying skill, three-body rebound carrying amplitude.
- **Resolved:** the geometry *describes/generates* in three coordinates (the
  pyramid anatomy + the emergent 3.2-yr oscillation) but the minimum-error point
  *forecast* is effectively two-dimensional. Same classification-vs-forecast
  boundary the wider ARA corpus keeps landing on.
- **The amplitude wall is noise, not a missing coordinate:** the exact peak size
  of each event is set partly by stochastic wind forcing unknowable at forecast
  time, so a deterministic point forecast must under-shoot amplitude.
- **Skill recurs and decays**, exactly as predicted from the oscillation, and the
  recurrence period traces a *real* second band in the ocean (quasi-biennial).

## 5. What is NOT proven (live threads)

- That the 27-mo recurrence *is* the quasi-biennial mode rather than landing in
  its neighbourhood — strong alignment, unproven mechanism. Test: put the second
  timescale in the model and show the rings follow it when moved.
- That the two spectral bands are a *coupled anti-phase pair* (the power notch at
  ~38 mo at their mean, and a candidate combination tone near ~20 mo, are
  suggestive). A plain spectrum cannot distinguish a coupled pair from
  independent neighbours. Test: **bispectrum** for three-way phase coupling.
- The "low-ARA snap" label for the damping envelope is a description, not a
  computed ARA.
- Single system (ENSO), one ocean record. Generality untested.

## 6. Next step (planned)

Use the two bands as an **anti-phase canceller** — noise-cancelling-headphone
logic in frequency space: if the bands are a coupled pair, project the prediction
onto the predictable combination and let the anti-phase component cancel the part
that currently shows up as cool-phase bias and amplitude error, leaving a cleaner
forecast. (Requires the bispectrum check first to confirm coupling.)

## 7. Reproduce

```
python ara_pyramid_predictor.py nino34_long_anom.csv      # 3-body forecast + eigen-oscillation + scoreboard
python skill_recurrence_analysis.py nino34_long_anom.csv  # walk-forward skill-by-lead + spectrum (two bands)
```
WWV west/east auto-download from PMEL. NINO 3.4 monthly anomaly CSV required
(see SOURCES.md).

## 8. Extending the chain (steps 10-14)

**Step 10 — Is the amplitude its own wave?** The Hilbert envelope of the band-passed
signal is a real meta-wave, ~2x slower than the signal (14-mo de-correlation), with
structure at 5.2 yr (the beat of the two coupled bands), 7.8 yr, and 12 yr. A crude
rolling-std proxy had missed it; the proper envelope is genuinely slower.

**Step 11 — Are the two bands a coupled pair?** Bispectrum: yes. The quasi-biennial
(~28 mo) and low-frequency (~48-67 mo) bands phase-couple to a combination tone near
15-20 mo, bicoherence ~0.34 against a ~0.06 floor. Coupling is real but moderate.

**Step 12 — Anti-phase canceller (noise-cancelling logic).** A VAR(2) "two-band"
model improved the skill metric but by extra DAMPING, not cancellation: it held one
~45-mo mode (not two), barely moved the cool-phase bias, and its skill gain was the
hedge-toward-mean artifact. The mechanism was not realised. *Rejected as cancellation.*

**Step 13 — Complex-demodulation loop (read pair → pin phase → propagate).** The
LEAK-CHECK was decisive: the non-causal version scored +0.55 (corr 0.80) and was
ENTIRELY leakage — the causal version collapsed to worse-than-climatology. Cause:
the present phase of a wave cannot be measured without its future (filter endpoint
problem). The best causal instantiation of the loop remains the state-space LIM.

**Step 14 — Ride the skill-wave (lead-dependent calibration).** Learn per-lead
shrinkage on early origins, apply causally on later ones. Result: the trough
self-harm is removed (12-mo skill −0.07 → +0.07; 15-mo −0.08 → +0.05) by shrinking
to climatology where the model is blind. But the ~27-mo re-emergence is NON-
STATIONARY (it wanders with the variable quasi-biennial period), so calibrating to it
is unreliable and even hurts (21-24 mo). *Honest envelope: real skill to ~6 mo,
calibrated humility through the 9-18 mo trough, no bankable far-field claim.*
Implemented in `ara_calibrated_predictor.py`.

### Standing conclusion after steps 10-14
The legible horizon is ~6 months (recharge lead), with a well-calibrated humble
decay through the trough. Every scheme that tried to reach past it either hit the
same wall causally or only "beat" it by leaking the future. The recurrence is real
but its phase wanders, so it is describable, not bankable. The open lead: the missing
coupled system that might pin the wandering quasi-biennial phase and close the
triad (next investigation — candidate: the stratospheric QBO, a regular ~28-mo
oscillation suspiciously close to the ENSO quasi-biennial band).

## 9. Extending the chain (steps 15-20): the seasonal clock and the rejected drivers

After the calibration, the search turned to the missing coupled system that might pin
the wandering quasi-biennial phase and close the triad. Candidates were tested by the
same rule — does it genuinely lead, controlling for what we already know?

**Rejected external clocks (4 for 4).** SOI (atmosphere): contemporaneous at lag 0-1,
a coupled partner in the surface layer, not a driver below. TNA (Atlantic): weak, no
clean lead. QBO (stratosphere): period matches almost exactly (28.4 vs ~28 mo) but
phase-locking value 0.14 vs 0.30 surrogate threshold, p=0.54 — same period, independent
phase, NOT coupled. Clouds (OLR): contemporaneous with the surface; the apparent +0.44
lead on the recharge collapses to -0.09 once NINO is controlled for — a surface proxy.

**The one clock that worked — and it wasn't hidden.** Events phase-lock hard to the
calendar: 51% of El Niño peaks fall in the Dec-Jan perihelion window, and inter-event
gaps are quantized to whole years (81% within 0.3 yr of an integer). Putting the annual
clock back as a first-harmonic seasonal LIM is the largest honest gain in the project:
6-month skill roughly doubles and the trough lifts with real skill. Crucially, the
*calendar label* beats feeding in the raw orbital insolation — equatorial insolation is
semiannual (equinox-driven) while ENSO's lock is annual (asymmetric monsoon/continental
cycle), so the label, by integrating many annually-phase-locked subsystems in their true
phases, is a richer relational coordinate than any single physical driver it bundles.

**Relational reading.** The recurring lesson: forecast information lives in the
*relations* (recharge lead, band coupling, the annual integrator), not in any system's
isolated properties. ARA classifies via a system's relation to itself across time
(robust everywhere); it forecasts only where a second relation — coupling to an
observable driver-below — stays legible. Same framework, two relations; the horizon is
how far the second stays readable.

**Amplitude-period coupling (the integer-year question).** Bigger events tend to be
followed by longer gaps (terciles 2.3 / 2.7 / 3.4 yr) — a nonlinearity a linear LIM
cannot represent, and the mirror of the gap->amplitude `log_φ` mechanism in the Time
Machine work. But it is weak in the reliable record and concentrated in the sparse early
data; thirds run high-low-low, not the high-low-high a recurrence would need. Most
parsimoniously the tail of one large early disturbance settling, plus poorer old data —
not a recurring lever. Sign-stable, magnitude weak: a humble lean, not a wall-breaker.

**Standing horizon.** Unchanged at ~6 months physical, now with roughly double the skill
there and a lifted trough. The integer-year choice past the horizon resists every
external clock tested and looks intrinsic to the coupled system's nonlinearity.

## 10. Files

- `ara_seasonal_calibrated_predictor.py` — CAPSTONE: seasonal (annual clock) LIM +
  lead-dependent calibration; the strongest honest forecaster (prints stationary vs
  seasonal vs seasonal+calibrated so the calibration tradeoff stays visible)
- `ara_pyramid_predictor.py` — the three-body coupled rebound forecaster
- `ara_calibrated_predictor.py` — LIM + lead-dependent skill-wave calibration (stationary base)
- `skill_recurrence_analysis.py` — walk-forward skill recurrence + spectrum
- `SOURCES.md` — data provenance
- `SESSION_LOG.md` — narrative log of the full session, in order
- `results/` — computed curves (skill-by-lead, layer ladder, spectrum)
- `ARA_PYRAMID_REBOUND_RESULT.md` — the step-5 result writeup (with step-6 correction)
