# Planet X by empty-rung hunt — does the rung ladder point at the hidden planet?

**Date:** 2026-05-29
**Status:** Exploratory, honest null-tested. Real orbital data (IAU/JPL standard semi-major axes). One line of evidence.
**Question (Dylan):** The framework says systems sit on a geometric rung ladder. Take the orbits we *can* see (the known planets), read the ladder, and let the geometry point at where a hidden planet (Planet Nine / "Planet X") should sit. This is the framework's signature "reverse inference" move — reconstruct the unmeasured from the measured.

## Short version

- **The ladder does point at the Planet Nine region — but it's a *soft* prediction, shared with the old Titius–Bode law, not a razor-sharp framework-only hit.** Be upfront about that.
- **Whether you use an octave ladder (×2) or a φ ladder (×1.618), projecting past Neptune/Pluto lands the next body at a few hundred AU**, overlapping the published Planet Nine estimate (~380–800 AU):
  - **Octave ladder:** rung 8 = **367 AU**, rung 9 = **777 AU**. The central modern estimate (Brown & Batygin 2021, a ≈ 380 AU) sits almost exactly on octave rung 8.
  - **φ ladder:** rung 13 = **463 AU**, rung 14 = **740 AU**. Sedna (506 AU) and 2012 VP113 (263 AU) fall on/near nearby rungs.
- **Honest null test: the octave (base-2) ladder is the *cleanest*, not φ.** With a fill penalty (charging for empty rungs), base 2 fills every rung perfectly (no gaps) and wins; φ leaves one empty rung and a smaller best-fit base (1.38) only "wins" by overfitting with many empty rungs. **This is consistent with the framework's own corrected stance: rungs are octave-spaced (×2); φ is the timing handover *through* the ladder, not the spacing *of* the ladder.** Same lesson as the solar predictor-base test.

## Data

Authoritative semi-major axes (AU), IAU/JPL standard values:
Mercury 0.387, Venus 0.723, Earth 1.000, Mars 1.524, Ceres 2.766, Jupiter 5.203, Saturn 9.555, Uranus 19.218, Neptune 30.110, Pluto 39.482.
Detached objects (the real Planet Nine evidence population): 2012 VP113 a ≈ 263 AU, Sedna a ≈ 506 AU.
Planet Nine published estimate: a ≈ 380–800 AU (Batygin & Brown 2016 ~700 AU; Brown & Batygin 2021 refined ~380 AU central).

## The ladders

**Consecutive spacing is geometric with ratio ≈ 1.6–1.9** (roughly φ to φ^1.3 per step):
Mercury→Venus 1.87×, Venus→Earth 1.38×, Earth→Mars 1.52×, Mars→Ceres 1.82×, Ceres→Jupiter 1.88×, Jupiter→Saturn 1.84×, Saturn→Uranus 2.01×, Uranus→Neptune 1.57×, Neptune→Pluto 1.31×. This is the classic Titius–Bode-type geometric regularity.

**Octave ladder (×2), every rung filled — no gaps:**

| octave rung | ladder AU | bodies |
|---|---|---|
| −1 | 0.43 | Mercury |
| 0 | 0.92 | Venus, Earth |
| 1 | 1.94 | Mars, Ceres |
| 2 | 4.10 | Jupiter |
| 3 | 8.67 | Saturn |
| 4 | 18.34 | Uranus |
| 5 | 38.80 | Neptune, Pluto |
| **8 (project)** | **367** | **← Planet Nine central estimate (~380 AU)** |
| 9 (project) | 777 | ← upper Planet Nine estimate |

**φ ladder (×1.618), refit base 1.597, one empty rung (rung 4):**

| φ rung | body | actual AU | ladder AU |
|---|---|---|---|
| −2…+2 | Mercury…Ceres | — | within ~10% |
| 3 | Jupiter | 5.20 | 4.30 |
| 5 | Saturn | 9.55 | 10.95 |
| 6 | Uranus | 19.22 | 17.49 |
| 7 | Neptune | 30.11 | 27.94 |
| 8 | Pluto | 39.48 | 44.61 |
| 12 (project) | (2012 VP113 ≈ 263) | — | 290 |
| 13 (project) | **Planet Nine** | — | **463** |
| 14 (project) | (Sedna ≈ 506) | — | 740 |

## Verdict

The empty-rung hunt **works in the weak sense**: the visible ladder, extended outward, places the next solar-system body in the **~370–780 AU band, squarely on the published Planet Nine estimate.** The octave version is especially tidy — Planet Nine's central modern estimate (~380 AU) lands almost exactly on octave rung 8.

But the **honest caveat dominates**: any geometric spacing law (Titius–Bode included) with ratio ~1.6–2, anchored on the outer planets, points to roughly the same place. So this is *consistent with* the framework but does **not** distinguish it from the 250-year-old empirical law. The genuinely framework-aligned finding here is structural, not predictive: **base 2 (octave) is the most parsimonious rung spacing — φ is not — which matches the corrected framework (octave rungs, φ-timed handover) and the earlier solar predictor-base result.**

## What would make this a *real* framework test (not done here)

The actual Planet Nine evidence is **orbital-angle clustering** of the detached objects (aligned perihelia / arguments), not their semi-major axes. The framework's distinctive claim is **matched-rung anti-phase coupling** — so the sharp test is whether the framework's coupling structure reproduces the *angular* clustering and points to the same perturber, the way SOI/PDO matched-rung anti-phase coupling worked for ENSO. That is the natural next step if we want a Planet-Nine result that only the framework could produce.

## Honest scope / caveats
- Semi-major-axis ladder is the *weakest* form of the test; shared with Titius–Bode.
- Continuous best-fit base (1.38) has lowest raw RMS but only by overfitting (many empty rungs, fill 0.67) — rejected by the fill penalty.
- Ceres fills the classic "missing planet at the belt" rung, so this ladder does **not** reproduce the historic Titius–Bode gap as an empty rung.
- No strict-causal forecast here — this is a static geometric-spacing test, not a time-series prediction.

## Files
- `TheFormula/planetx_rungs.py` — first-pass ladder + base null test
- `TheFormula/planetx_rungs2.py` — fair fit with fill penalty, consecutive ratios, octave + φ outward projection
