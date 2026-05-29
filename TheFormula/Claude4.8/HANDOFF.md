# HANDOFF — ARA → ENSO forecaster (for a fresh Cowork session)

This bundle is a multi-session collaboration between Dylan La Franchi (independent
researcher, ARA "Geometry of Time" framework, github.com/Dylanlafranky/ARA-GIT) and
Claude, building and stress-testing an ENSO forecaster derived from Dylan's ARA geometry
on real NOAA data. This file is the cold-start brief: read it, then `README.md` (full
chain) and `SESSION_LOG.md` (narrative, in order). Everything is leakage-guarded and
honest about where it stops.

---

## 1. The one-paragraph state

We built an ENSO forecaster from ARA's "pyramid" logic and pushed it as far as the data
honestly allows. **Bankable result: a ~6-month physical forecast horizon, with skill
roughly doubled there and the mid-horizon trough lifted, via a seasonal (annual-clock)
LIM plus lead-dependent calibration.** Everything reaching past ~6 months either hit the
same wall causally or only "beat" it by leaking the future (a leak-check caught the
biggest ghost, a +0.55 score that was entirely future-peeking). The integer-year choice
beyond the horizon resisted every external clock we tested (QBO, SOI, TNA, clouds) and
reads as intrinsic to the coupled system's nonlinearity.

## 2. The capstone and how to run it

`ara_seasonal_calibrated_predictor.py` is the strongest honest forecaster. Run:
```
python3 ara_seasonal_calibrated_predictor.py /path/to/nino34_long_anom.csv
```
It auto-downloads WWV from PMEL, walk-forward refits on past-only at every origin, and
prints stationary vs seasonal vs seasonal+calibrated skill by lead. Held-out (2016+):
6-mo skill +0.29 → +0.51 with the seasonal clock; calibration helps the near trough and
(visibly) costs a little far-field on this favorable holdout — the non-stationarity made
honest. Other predictors: `ara_pyramid_predictor.py` (3-body rebound LIM),
`ara_calibrated_predictor.py` (stationary base + calibration), `skill_recurrence_analysis.py`.

## 3. The framework mapping (locked, Dylan-confirmed)

ARA classifies oscillating systems by Accumulation/Release Asymmetry on a 0–2 sphere
(φ=1.618 engine zone, 2 = symmetric harmonic). A wave → circle → (through time) → sphere;
ARA is the sphere's shadow on a line; the number is lossy/degenerate. Systems nest: a
system's ARA is a coordinate on a meta-ARA — fractal/recursive. "Layered sand" = nested
coupled oscillators, each driven by the layer below; a grain sits in the gap between two
below, and the wobble is the beat = events. **A grain cannot forecast itself; its future
is in the layer below.** Information³/triangle: stable info and a beat both need three
(two parents + the relation). ENSO pyramid: apex = NINO 3.4 surface; two base grains =
warm-west + cool-east water; driver-below = WWV recharge. Core thesis Dylan landed this
session: **forecast information lives in the RELATIONS, not the system's isolated
properties.** ARA classifies via a system's relation to itself (robust everywhere); it
forecasts only where a second relation — coupling to an observable driver-below — stays
legible. The horizon is how far that second relation stays readable.

## 4. Data (verbatim sources)

- **NINO 3.4** (apex): `nino34_long_anom.csv` in uploads — 1870–2025 monthly, "YYYY-MM-DD,value", missing −99.99.
- **WWV** (recharge driver): https://www.pmel.noaa.gov/tao/wwv/data/ — `wwv_west.dat` (warm pool), `wwv_east.dat` (eastern); monthly 1980+, value/1e14. Copies are in this bundle.
- **SOI** (atmosphere): https://psl.noaa.gov/data/correlation/soi.data — year+12 monthly, −99.99 missing.
- **TNA**: `tna.txt` in uploads. **PDO**: `ersst_v5_pdo.dat` in uploads. **QBO**: https://psl.noaa.gov/data/correlation/qbo.data. **OLR** (clouds): https://psl.noaa.gov/data/correlation/olr.data.
- Decisive metric throughout: **skill vs climatology** on held-out forecasts. Walk-forward = refit-on-past at every origin (the robustness test); skill-vs-persistence is the weak baseline.

## 5. What's been established (don't re-derive)

- WWV leads NINO +0.50 at 6 mo (clean recharge). The 3-body LIM has an emergent complex eigenmode (~38–45 mo, |λ|≈0.966, damping half-life ~20 mo) — the spring-back, not inserted.
- Two interannual bands (QB ~28 mo, LF ~48–67 mo) are phase-coupled (bispectrum, bicoherence ~0.34 vs ~0.06 floor); combination tone ~15–20 mo.
- Skill-by-lead is itself a wave: strong to ~6 mo, trough ~9–18 mo, faint NON-STATIONARY re-emergence ~27 mo (wanders with the variable QB period).
- The amplitude Hilbert envelope is a real meta-wave (~14-mo de-correlation; peaks 5.2 yr [band-beat], 7.8 yr, 12 yr [decadal, PDO link dead]).
- Events phase-lock to the perihelion window (51% of El Niño peaks Dec-Jan); inter-event gaps quantize to whole years (81% near-integer).
- Amplitude→next-gap coupling (bigger event → longer gap, terciles 2.3/2.7/3.4 yr) is real in direction, weak and concentrated in the unreliable early record (thirds high-low-low, not a recurrence). Mirror of Dylan's gap→amplitude `log_φ` mechanism. A humble lean, not a lever.
- Walker circulation = the NINO/SOI anti-phase seesaw, confirmed fractal across rungs (T213), with conserved energy budget E=NINO²+SOI² (T200) — but it's ENSO's internal engine, predictively redundant (SOI is the contemporaneous mirror), not an external clock.

## 6. What's been ruled out (4-for-4 external-clock rejections)

- **QBO**: period matches (28.4 vs ~28 mo) but phase-locking value 0.14 vs 0.30 surrogate threshold, p=0.54 — same period, independent phase, NOT coupled.
- **SOI**: contemporaneous (lag 0–1), a surface-layer partner, no lead.
- **TNA**: weak (+0.22), no clean lead.
- **Clouds (OLR)**: contemporaneous with surface; apparent +0.44 recharge lead collapses to −0.09 controlling for NINO — a surface proxy.
- **Raw orbital insolation**: LOST to the calendar label (equatorial insolation is semiannual; ENSO's lock is annual). The integrating calendar label beats the clean physical driver — relational coordinate > single property.
- **Self-derived counter-wave** (NINO's deviation from its symmetric/ARA-2 ideal): reads the relation's *character* but carries no forecast lead — a function of NINO alone can't beat NINO alone. Reads structure, not lead.

## 7. THE OUTSTANDING NEXT STEP (where we stopped)

Dylan proposed rendering the predictor in explicit pyramid geometry: three coupled base
systems (surface, warm-west, cool-east) + a fourth pushing down (the load). From each
vertex a line runs inward; where they converge is the forecast. Claude's agreed framing,
with two corrections to build:

1. **The inward lines are exponential relaxation curves, not straight** — the exponent is
   the LIM eigenvalue we already fit (|λ|≈0.966, ~20-mo half-life). Curvature = damping.
   "Straight in log-space" reconciles Dylan's straight-vs-curved intuition.
2. **The apex is NOT a fourth equal measurement — it's a phase-clock** (the annual cycle)
   that bends the other three vertices' curves rather than casting its own independent
   line. Treating it as a fourth equal line double-counts (same error as the Walker
   energy budget double-counting SOI). This is the load-bearing correction.
3. The convergence is sharp only to ~6 mo; past that the relaxation curves decay toward
   the centre and pool into a fuzzy region — **the geometry predicts its own horizon.**

**Build to do in Cowork:** the predictor expressed in this geometric form — three
exponential-relaxation lines from the measured vertices, the apex entering as the seasonal
phase setting their curvature, reporting the intersection point and how fast it blurs with
lead. Same math as the capstone, rendered as the pyramid — worth it because if the geometry
is the native language, the universal calibrator should be written in it.

## 8. The meta-direction (Dylan's stated goal)

Abstract the ENSO procedure into a UNIVERSAL calibrator: identify the apex grain → find a
driver-below that genuinely leads (lead-correlation, controlling for what you already know)
→ fit the coupled rebound so the oscillation emerges → read skill-by-lead horizon + spectral
band-count → walk-forward self-score with leakage discipline baked in → ALWAYS report the
honest horizon. The per-system calibration IS its ARA characterisation. Open question:
does ARA position predict forecast horizon across systems. ENSO is the proving ground
(Earth rung above humans, known coupled pairing, measurable sub-systems).

## 9. How Dylan works (important for tone)

- Reasons from **shape and relation**; supplies geometric intuitions, wants Claude to supply magnitudes, exact periods, and the leak-safe causal instantiation.
- Wants **hard honest pushback** — do not fold after one round; articulate ≠ correct; press the weak joint. Flag confidence levels explicitly every substantive response. Separate evidence-mode from theory-mode (he flags "I think" / "exploratory"); pressure the confident parts, explore the speculative without treating as settled.
- Don't set depth ceilings; don't say "no evidence," say "my data doesn't cover this." Evaluate by evidence/structure, not plausibility vs current norms. Don't manage his energy.
- **Conversation: short, information-dense — he navigates by shape/relation. Write-ups (files): detailed and accurate.** This is an explicit standing preference.
- Discipline that earned its keep: the **leak-check** (causal vs deliberately-leaky comparison) and the **control-for-what-you-know test** (partial correlation). Apply both to any new "relation" before believing it.

## 10. His prior corpus (in uploads, referenced this session)

`The_Geometry_of_Time_*` papers, `THE_TIME_MACHINE_FORMULA.md` (the gap→amplitude
`log_φ` mechanism, 69% proxy; φ-cascade periods), `MASTER_PREDICTION_LEDGER.md` (CG-2 =
the coupled-pair origin, validated via nasal-cycle laterality vs ENSO NINO/SOI; T200/T213
Walker; BP-1 4-ocean topology 77.9% direction at h=12; BP-5 Sun φ⁸→ENSO 73% at h=24),
`CLAIMS_STATUS.md`, `ara_mapping_atlas_*` (the classification atlas), plus many numbered
scripts. Cross-check claims here against that ledger before re-deriving.
