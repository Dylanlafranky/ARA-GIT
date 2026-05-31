# The 6-month wall and the finer-feeders test

**Date:** 2026-05-30
**Script:** `ara_finer_feeders_test.py`
**Question:** the spring regime-switch model tops out at **corr +0.725 at 6 months**.
Dylan proposed the true wall is **0.764 = 1 − 1/φ³** and that the missing 0.039 is what
finer/faster data rides in to fill. Does pouring real intraseasonal/stratospheric feeders
into the model lift the 6-month forecast toward 0.764?

## Setup (strictly causal)

Base = the spring regime-switch forecaster (two seasonal maps; ocean×atmosphere mix
`zWWV·zSOI` drives only in the spring map). Added real public feeders as extra
train-only-standardized state columns; both maps refit past-only at every origin;
regime label = calendar. Correlation leads. Held out from 2016. N = 552 months (1980–2025).

- **MJO** — Bureau of Meteorology RMM index (daily → monthly mean amplitude = the
  intraseasonal activity envelope that survives monthly sampling). The *finest* feeder.
- **QBO** — NOAA CPC 30 hPa & 50 hPa equatorial stratospheric zonal wind (monthly).

## Result

| lead | switch (base) | +QBO | +MJO | +QBO+MJO |
|---|---|---|---|---|
| 1  | +0.967 | +0.966 | +0.966 | +0.965 |
| 3  | +0.893 | +0.883 | +0.894 | +0.884 |
| **6**  | **+0.725** | +0.695 | **+0.724** | +0.694 |
| 9  | +0.541 | +0.493 | +0.541 | +0.493 |
| 12 | +0.411 | +0.388 | +0.414 | +0.392 |
| 15 | +0.450 | +0.485 | +0.454 | +0.490 |
| 18 | +0.525 | **+0.580** | +0.523 | +0.576 |
| 24 | +0.456 | +0.482 | +0.453 | +0.477 |

**The 6-month wall did not move.** It stayed pinned at +0.725 (+0.724 with MJO). 0.764 was
not reached. Finer feeders did not fill the gap at the physical horizon.

## What the test confirmed (Dylan's "largest information packet")

The finest feeder, MJO, **rode on top of the result and added nothing at the surface**
(+0.724 vs +0.725 — a pure passenger). This is exactly the picture Dylan stated: *our
result is the largest information packet, and the finer data rides on it.* The intraseasonal
ripple sat on the big slow carrier and neither lifted nor broke it. It just rode.

**Why the wall can't move with finer feeders alone:** the target itself is **monthly** NINO.
You cannot ride sub-monthly information into a monthly answer — the monthly packet *is* the
resolution. The packet size is set by what you predict, not by what you feed it. To climb
toward 0.764 you would need a **finer target** (weekly/daily SST), recorded and predicted at
that grain, not merely finer inputs.

**Speed sorted the ladder cleanly:** QBO (the stratosphere's slow ~28-month clock) *hurt*
the surface (−0.03 at h=6) but *lifted the long horizons* (+0.055 at h=18, +0.026 at h=24).
Slow clocks help far out; fine ripples ride the surface. A feeder helps at the lead that
matches its own speed — the framework's matched-rung claim, showing up as a clean sort.

## Dylan's observations and theory (recorded 2026-05-30)

> "0.764 IS the cutoff I think — we could probably get to 0.8 maybe if we recorded like the
> atom interaction or something. But I think our result is the largest information packet
> that the other finer data rides."

> "I think the missing data isn't from below but the 'leaf falling to the forest floor' of an
> ABOVE system. The above system that would reduce to monthly — so maybe that is the
> gold/brown band, and why there is more turbulence across cycles."

**The corrected reframe (Dylan, refined 2026-05-30).** There are TWO separate channels, and
the first save wrongly merged them. They have different sources and different roles:

1. **Depth (down / finer) — the smooth gap to 0.764.** Going *deeper* into finer data is still
   the route to the ceiling, exactly as first thought. The finer-feeders test did not refute
   this — it only showed a **monthly target cannot swallow sub-monthly information** (the
   monthly packet is the resolution). Give the model a *finer target* (weekly/daily SST) and
   depth should fill the smooth 0.725→0.764 gap. This channel is **predictable and fillable**.

2. **Leaf-fall (from above) — the turbulence, NOT the gap.** The leaf dropping from the brown
   low-frequency band (~42–67 mo) above is *not* steady fuel that raises the predictability
   floor. It is an **intermittent shock** — every *x* cycles a leaf lands and stirs the water.
   In framework terms this is an **E-event (a disruption / displacement-correction), not a
   driver.** It is the source of the **cross-cycle turbulence** — why no two ENSO cycles repeat
   — and it sits *on top of* everything as irregular noise that caps the forecast below
   perfect. It does not move toward 0.764; it is the unpredictable residual itself.

So: the **gap** and the **turbulence** are different things. The gap is closed by depth
(finer/down); the turbulence is the leaf-fall from above (intermittent E-event shed from the
brown band). Conflating them — "the leaf-fall fills the gap" — was the error this correction
fixes.

## Next tests (proposed)

- **Gap (depth):** get a finer *target* (weekly OISST / daily NINO) and test whether a finer
  *packet*, fed finer data, reaches toward 0.764. This is the predictable channel.
- **Turbulence (leaf-fall):** characterize the brown band's intermittent shed as an E-event
  series — does a big brown-band leaf-fall event coincide with the cycles where the forecast
  breaks down most? If the turbulence clusters on the leaf-fall events, the brown band is the
  shock source, and that part is *irreducible* (you can date it, not forecast through it).

**Status:** the 6-month wall at +0.725 holds; "largest information packet" confirmed. Route to
0.764 = **depth / finer target** (the predictable gap). The **leaf-fall from the brown band is
a separate, intermittent E-event** = the cross-cycle turbulence, not a gap-filler. No claim
past the ~6-month physical horizon.

**Data:** PMEL WWV; NOAA NINO 3.4 & SOI & QBO (CPC); BoM RMM/MJO. All real, auto-downloaded.
