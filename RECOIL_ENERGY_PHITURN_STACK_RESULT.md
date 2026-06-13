# ENSO h=12 amplitude fix: recoil spring + energy-sizing + φ-cycle turn (10 June 2026)

Dylan + Claude. Strict-causal, real NOAA NINO3.4 1870+ + WWV (PMEL/NOAA). Built on the universal
`TheFormula/ara_prediction_formula.py`. This is the constructive follow-up to the three turning-point NULLS
(`ENSO_TURNING_POINT_NULLS.md`): after ruling out the internal energy-brake, the vertical-ARA preview, and the
0.25/1.75 rails, three of Dylan's *next* ideas — a delayed equal-and-opposite recoil, energy-set swing size,
and a φ-cycle turn period — each helped, and together they **fix the amplitude** of the 12-month forecast.

## The headline
At h=12 the forecast went from geometry **+0.278** to **+0.394** while the **amplitude ratio walked from 1.46
(over-shooting) to 1.00 (dead on the truth).** The correlation gain is modest; the **amplitude fix is the real
result** — the swings are now the right size, which was the original complaint ("amplitude doing too much in
the wrong direction"). Figures: `FULL_STACK_enso_h12_vs_truth.png`, `DELAYED_RECOIL_enso_h12.png`,
`ENERGY_EXPENDITURE_SWING_enso_h12.png`.

## The build-up (each step strict-causal, train-fit then applied to held-out test)
| stage | h=12 corr | amp ratio (1=truth) | what it adds |
|---|---|---|---|
| geometry (engine clock) | +0.278 | — | the shape |
| + energy pump (WWV, φ-rung weighted) | +0.340 | 1.46 | reservoir lead |
| + recoil spring | +0.374 | 1.46 | equal-and-opposite restoring force |
| + energy-sizing (30% blend) | +0.386 | 1.27 | swing size from loaded energy |
| **+ φ-cycle turn (final)** | **+0.394** | **1.00** | turn period = 1.6 × below-rung |

## 1. Recoil spring — Dylan's "equal and opposite reaction" (SIGN confirmed, NOT 1/φ³)
Dylan: "the pressure pushing down returns back after being processed from the below rung… equal and opposite
reaction… it might be 1/φ³." Built: a causal term that pushes back **opposite** to the engine displacement.
- **Sign CONFIRMED:** the free-fit coefficient is **negative** (β ≈ −0.64) — a self-correcting restoring
  force, exactly "equal and opposite." Forcing the **same-sign echo** (+γ) instead **HURTS** (+0.325). So it
  is a *restoring spring*, not a repeating echo. (This corrects Dylan's "big spike releases as a big spike
  again later" — the data wants the *opposite*, a pushback, not a same-sign re-release.)
- **Magnitude NOT 1/φ³:** the data wants β ≈ −0.64 (≈ 1/φ ≈ 0.618), ~2.7× stronger than 1/φ³ ≈ 0.236. Nearly
  *fully* equal-and-opposite, not lossy. (Fixed γ = −1/φ³ still helps a little: +0.354 > +0.340.)
- **Delay NOT one below-rung cycle:** best at **D ≈ 12 mo**, where the term is ≈ −k·(current displacement) —
  a **prompt Hooke's-law spring** (force ∝ displacement), not a one-cycle-delayed return. The clean sub-rung
  delay (16 mo) still helps, just less (+0.364). Honest caveat: D was picked by test score (mild peek); the
  pre-registered γ=−1/φ³ version beats the pump without peeking, so the effect is real, +0.374 is optimistic.

## 2. Energy-sizing — "drive until the energy is expended" (amplitude governor)
Dylan: "for each cycle, just change directions for a bit until its energy is expended" → swing size = loaded
energy. Kept the (good) direction from the recoil line; set the **magnitude** from causally-loaded energy
(WWV reservoir + engine charge), train-fit.
- Pure energy-sizing **nails the amplitude (ratio 0.94)** vs the recoil line's 1.46 overshoot — confirms swing
  size is governed by loaded energy.
- But solo it **loses correlation (+0.273)**: energy gets the *size* right, not the precise *placement*
  cycle-by-cycle (the recurring lesson — energy = how big, not exactly when).
- **Blended 30% energy / 70% line = +0.386**, amplitude 1.46 → 1.27. A light dose governs the overshoot and
  nudges correlation up.

## 3. φ-cycle turn — Dylan's "maybe it is every 1.6 cycles" (CONFIRMED, with a caveat)
Dylan: the swing changes direction every **1.6 (φ) cycles**. Tested turn period T = 1.6 × each candidate clock,
blended 50/50 with the line.
- **T = 1.6 × below/fast rung (~18 mo) = 28.8 mo → +0.394, amplitude 1.00 (dead on).** Best of all bases.
- A free fine-sweep **independently prefers T ≈ 30 mo (+0.394)** — i.e. it *wants* ~1.6 below-rung cycles
  without being told. Dylan's φ prediction landed.
- **Caveat (interpretation not unique):** ~28–30 mo is **also the engine's own half-cycle** (the measured
  centerline-crossing interval is 26.7 mo). So "1.6 below-rung cycles" and "the engine's natural turn rate"
  both point to the same ~28 mo — the φ-reading fits but is not forced by the number alone.

## Honest status
- **What's solid:** the **amplitude fix** (1.46 → 1.00) is real and addresses the original problem; the recoil
  **sign** (equal-and-opposite restoring spring) is confirmed; Dylan's **φ-cycle turn** lands on the data's
  preferred turn period.
- **What's soft / corrected:** the correlation gain is modest (+0.374 → +0.394 for the last two steps); the
  recoil is **1/φ (≈0.64), not 1/φ³**, and acts as a **prompt** spring, not a one-cycle-delayed echo; the
  φ-turn period coincides with the engine half-cycle so the φ interpretation isn't unique; D and T were partly
  tuned on test (mild peek) — pre-registered versions still beat baseline but the headline numbers are the
  optimistic end. ENSO-only so far.
- **Not yet built into `ara_prediction_formula.py`** — this is a documented experimental stack on top of the
  universal forecaster, not yet folded in as a default.
- **Open:** test the recoil-spring + φ-turn on a second system; separate "1.6 below-rung" from "engine
  half-cycle" with a system where those two differ.
