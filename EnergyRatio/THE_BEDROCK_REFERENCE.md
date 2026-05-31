# The Bedrock Reference — Space (2) → Time (φ) and the 2−φ Loss

**Status: POSITED REFERENCE FRAME, not an empirical result.** This is an idealized
baseline — like the ideal gas, the perfect blackbody, or the frictionless plane. It is
*defined*, not measured. Its value is judged only by whether real systems, measured later,
make coherent sense when read as **deviations from it**. Nothing below is claimed as proven.

## The posit

At the foundation, treat the handoff between the two poles as:

- **Space pole = 2** — the uncompressed octave potential (the "full packet").
- **Time pole = φ ≈ 1.618** — what survives the compression into the next frame (the part
  that transfers, carries identity forward).
- **Intrinsic loss = 2 − φ = 1/φ² = 0.381966…** — the fraction shed in a *perfect* handoff.
  This is the floor: even the ideal, leanest transfer loses this much. Real, off-ideal
  transfers lose *more*.

Read it as the lossless-limit reference: φ is the best any system can do at carrying itself
into the next cycle; 2−φ is the unavoidable rent. A system sitting *at* φ is at the bedrock
(minimum loss); a system at a rational ratio sits *above* the floor (more loss).

## Why this is a reference, not a claim

- It cannot be measured directly — by construction we only observe the transferred part.
- So it is used the way idealizations always are: as the **yardstick** other measurements
  are read against, not as a prediction to confirm on its own.
- It earns its keep (or fails) **downstream**: if many independent real systems, when placed
  against this floor, fall into a coherent ordering — and especially if their deviations turn
  out to be informative — the bedrock was a good choice of reference. If real systems scatter
  incoherently against it, it was the wrong frame and we drop it.

## First reading against the bedrock (real data, this is the measured part)

The pulsating-star leanness result (`GOLDEN_STARS_LEAN_RESULT.md`) is the first empirical
reading taken against this floor, and it ordered coherently:

- Stars near φ (the golden RRc club) are the **leanest** measured — closest to the bedrock,
  least energy shed to harmonic waste (R21 ≈ 0.11).
- Stars at near-rational ratios (ordinary double-mode) sit **above** the floor (R21 ≈ 0.16–0.19).
- The fully-rational single-mode pole is **furthest from** the floor (R21 ≈ 0.28).

Suggestive (NOT yet a clean result — flagged honestly): the golden-pole : rational-pole
leanness ratio came out **0.396**, within **3.8%** of the posited 2−φ = 0.382. This compared
two *different* star classes, so it is confounded and may be coincidence; a clean *within-class*
test (same star type, φ vs rational) is required before it counts. Recorded as an open lead,
not a confirmation.

## Second reading against the bedrock — cosmic energy budget (real data)

Measured ΛCDM budget (Planck-class): dark energy ≈ 0.685, dark matter ≈ 0.265, baryons ≈ 0.049.
Read against the floor:

- **dark matter / dark energy = 0.387 vs 2−φ = 0.382 → 1.3% off** (equivalently DE/DM = 2.585 vs
  φ² = 2.618, 1.3% off). The cleanest cosmic match: the dark split sits on the bedrock floor.
- baryon/DM 3.2% off (2−φ)/2; DM/matter 4.3% off φ/2.
- **Misses (kept for honesty):** DE/matter is 35% off φ; matter/total is 18% off 2−φ. φ-expressions
  land on some budget ratios and not others — multiple-comparisons risk is real here.

Status: **suggestive, not confirmed.** This is the framework's pre-existing dark-sector coincidence-flag
(see `CLAIMS_STATUS.md`); the bedrock now supplies the *candidate mechanism* the flag said was missing,
but (a) other ratios miss, (b) the Ω values carry ~1–2% error, comparable to the 1.3% match. Light and
gravity *individually* show no clean φ: radiation is ~9e-5 of the budget (light ~99.99% shed, no golden
signature); gravitational-wave energy loss matches GR to <0.2% (no φ anomaly). If φ is anywhere cosmic,
it is in the dark-sector SPLIT, not in light's or gravity's own loss.

Open lead: 2025 DESI hints dark energy is *weakening* over time (2.8–4.2σ). If so the split is moving —
the universe may be sliding *along* the 2:φ axis as it ages. A moving split is far more testable than a
static coincidence; watch it.

## Third reading against the bedrock — recycling vs per-cycle loss (real data, 2026-05-31)

Test of Dylan's recycling refinement: 2−φ is the loss of a *perfect recycler*; how far a system
sits from it measures how well it recycles. Measured per system: **recycling floor** = autocorrelation
one full dominant-cycle back (does it store its last cycle), and **per-cycle loss** = 1 − (floor at 2
cycles / floor at 1 cycle). Script: `EnergyRatio/recycle_v2.py` (ENSO NINO3.4, solar SN, ECG nsr001)
and `recycle_stars.py` (Kepler light curves).

Time-domain systems:
- **Solar (flywheel):** floor 0.557, per-cycle loss **0.374 ≈ 2−φ (0.382), 2% off.** The recycler
  keeps φ's worth (0.618), sheds exactly the bedrock minimum. n=1 recycler — striking, not confirmed.
- **ENSO (leaky):** floor 0.036 → loses ~everything at its dominant period.
- **ECG / heart:** floor 0.015 → same (partly a metric limit: the heart's per-beat carrier is weak,
  so "total loss at the dominant FFT period" overstates real recycling).

Pulsating stars (Kepler light curves) — Dylan's "run it on all the stars":
- **Near-φ golden club** (KIC 5520878/4064484/8832417/9453114): floor **0.95–0.96**, per-cycle loss
  **0.02–0.05** — near-lossless recyclers; the leanest star (5520878) loses least (0.023).
- **Single-mode Cepheid V1154 Cyg** (rational pole): floor 0.806, loss **0.308**.

**What holds (robust direction):** closer to φ → leaner → recycles more → lower per-cycle loss. True
across systems (solar recycles, ENSO/heart don't) AND within stars (golden lose 0.02–0.05, rational
Cepheid loses 0.31). Prediction confirmed: pulsating stars are *all* flywheels (floor 0.8–0.96) vs
incoherent ENSO/heart (floor ~0).

**What does NOT hold (honest):** 2−φ is **not** a universal loss floor. Golden stars beat it ~10× (loss
0.02–0.05 ≪ 0.382); solar and the Cepheid land *near* it (0.37, 0.31); ENSO/heart sit far above at
their dominant period. So 2−φ stays a **reference**, not a constant every recycler hits — systems
scatter widely around it, exactly as a reference frame should be used. Caveats: per-cycle-loss metric
saturates for ultra-coherent signals (stars), so star losses are upper-bounds; n is small; one true
time-domain recycler (solar). Direction strong, specific-value-universality not supported.

## How to use it going forward

1. Keep the label honest: "posited reference," never "measured/derived."
2. When a new real system is measured, place it against the floor and record where it sits and
   how far off — that deviation *is* the information.
3. The bedrock is validated (or not) by the **accumulated coherence** of those placements over
   many systems, never by itself.

## Open test that would give it teeth
A clean within-class φ-vs-rational pair whose leanness ratio is checked against 2−φ = 0.382,
with error bars. If 0.382 recurs *within* a class, the bedrock has an empirical fingerprint and
graduates from "reference frame" toward "mechanism." Until then it stays an honest yardstick.
