# ENSO 12-month turning-point problem — three nulls (10 June 2026)

Dylan + Claude. Strict-causal, real NOAA NINO3.4 + WWV (PMEL/NOAA). Context: the φ-rung energy-pump
forecast (`PHI_RUNG_PUMP_FORECAST_UPGRADE.md`) lifts ENSO h=12 corr from geometry **+0.278 → +0.340**, but
the plot shows a real **amplitude-direction / grouping problem**: the φ-pumped amplitude is *unbraked* — it
pushes hard in whatever direction the wave is already going, so where the opposing wave should already be
winning, the forecast overshoots "down" past where it should have turned. The good amplitude is sometimes
aimed the wrong way. This file records the attempts to fix the **turning point** — all three failed.

## The question
The forecast has momentum (amplitude) but no **brake** — nothing telling it *when to stop and reverse*.
Where does the turning information live? Tested three mechanisms for the reversal.

## Null 1 — anti-phase internal energy-brake (HURT: +0.340 → +0.295)
**Idea (Dylan):** measure the energy of the current wave vs the opposing/anti-phase wave; let the forecast
travel "down" only as far as its own energy beats the opposing energy; flip at the crossover.
**Build:** per launch, causally decompose NINO into its dominant wave + nearest anti-phase neighbour (top-2
spectral peaks fit on history only), project both to t+h, brake the pump push by `1−2·E_opp/(E_cur+E_opp)`,
flipping when opposing energy wins.
**Result:** corr **+0.295**, *worse* than the unbraked pump (+0.340). The brake **flipped ~49 % of launches**
— a coin toss. The two-band decomposition cannot reliably tell when the anti-phase wave is winning, so it
reverses the pump for no reason and scrambles direction. **The opposing wave isn't cleanly identifiable from
NINO's own spectrum at the moment we need it.** File: `ENERGY_BRAKE_enso_h12.png`.

## Null 2 — vertical-ARA fast-rung preview (NO LEAD: +0.276 vs geom +0.278)
**Idea (Dylan):** the sub-cycle and the main form are the *same shape stretched by a rung* (×φ); the fast
sub-wave is a sped-up preview, so its turn *now* telegraphs the main wave's turn *later*, delayed by the
φ-stretch. Turning info comes from **down a rung**, not from an anti-phase partner.
**Build:** causal bandpass (lfilter, past-only) into fast band (12–30 mo) and slow engine band (30–90 mo);
cross-correlate for a lead; feed fast band as a leading input to the h=12 forecast.
**Result:**
- Best fast-vs-slow match is at **lag 0** (simultaneous, *no lead*) and **negative (−0.47)** — the fast band
  is anti-phase with the slow one but moves at the *same time*. No head start = nothing to forecast from.
- Period ratio **3.9, not φ (1.618)** — they are *not* "the same shape one rung apart."
- As a predictor: **+0.276 vs geometry +0.278** — zero lift (WWV still the only helper, +0.31).
**The faster rung does not lead the slower one in ENSO; vertical-ARA gives no predictive preview here.**

## Null 3 — 0.25 / 1.75 ARA rails as the flip points (FLIPS NOT THERE)
**Idea (Dylan):** each sub-cycle has a floor (0.25) and ceiling (1.75) on its ARA; when a swing nears a rail
it can't push further, so it turns. The rails are the *why* of the reversal.
**Build:** on the dominant engine band, find all extrema (= flips), compute each flip's accumulation/release
duration ratio (local ARA), and check where they cluster.
**Result:** median flip-ARA **~1.17**, scattered. **0 % near 0.25, 0 % near 1.0, 0 % near φ, 7 % near 1.75.**
The turns are **not pinned to the rails.** (Consistent with the residence-law note that **0.25 is *avoided*** —
this is the first direct test of the 0.25/1.75 rails as flip points, and it comes back null for ENSO.)

## The one real signal (why all three failed)
The fast and slow bands are **anti-phase but simultaneous** (−0.47 at lag 0). They fight each other *at the
same moment* — no faster rung gets a head start. That is the **concentration meta-rule** showing up: ENSO's
energy is *spread*, so there is no clean leading sub-rung whose turn previews the main turn. The turning
point can't be extracted from NINO's own internal structure (spectral partner, faster rung, or ARA rail).

**The only thing with genuine lead-time is the external reservoir (WWV)** — which is exactly why the WWV pump
is the only lever that has ever lifted the forecast. If a turning-point brake is to work, it must be measured
against a *real external feeder that genuinely leads* (e.g. IOD, the cleanest anti-phase one), not an internal
partner.

## Status
- All three are clean **nulls for ENSO**, recorded so we don't re-chase them. Dylan predicted each would fail
  ("I don't think it'll work… but we should try" / "wrong thing we are chasing but we need to rule it out").
- Live direction: test the brake against a **real leading feeder** (IOD), or treat the grouping problem as
  **external** (only feeders carry the turn-timing), not internal.
- The φ-rung pump (+0.340) remains the universal-recipe number; the full IOD+PDO+WWV feeder stitch remains the
  stronger ENSO forecaster at long range (+0.47 @ 24 mo).
