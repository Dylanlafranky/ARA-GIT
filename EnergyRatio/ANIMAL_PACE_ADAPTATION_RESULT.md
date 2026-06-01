# Pace ↔ Adaptation across the rungs (virus → whale) — 1 June 2026

Test of Dylan's idea: **more time-based (faster life-cycle) ⇒ faster adaptation.** Compiled published
allometric / molecular-evolution values (REAL literature, order-of-magnitude where noted) for ~21 entities
from RNA viruses to the blue whale. Script: `EnergyRatio/animal_atlas.py`.

## THE KEY FIX (Dylan): match equivalent WHOLE waves
First pass compared the animal's HEARTBEAT to the virus's whole replication cycle — **wrong rungs.** A
heartbeat is the animal's *cell-level* sub-clock ("just a cell's shape"); the animal's own whole-organism
cycle is **life/death = lifespan/generation.** Rule: to compare across the ladder, use the cycle that is
*the whole of that thing* (its full life wave), not a sub-ripple. The heartbeat clock gave a FAKE **−0.62**
(viruses' hour-long replication looked "slower" than a 0.1 s heartbeat → inverted, artifact, discarded).

## What HELD (rung-matched: life/death clock for all)
- **Life-pace ↔ adaptation, whole span virus→whale: corr +0.62.** Within animals (lifespan clock): **+0.81.**
  Faster life-cycle ⇒ faster adaptation — **Dylan's claim confirmed once the rungs are matched.**
- Slope: log(evo-rate) ≈ **+0.61 · log(life-pace)**.
- (Heartbeat-clock within-animals read +0.91, but only because heartbeat co-scales with lifespan via
  Kleiber; the lifespan clock is the rung-correct version, +0.81.)
- **Kleiber** recovered (heart-pace ~ mass^−0.27 ≈ −0.25 wall; coincidence-flagged). **Endo/ecto** split
  holds: at equal size mammals/birds +0.12 dex faster than size predicts, reptiles/fish −0.32 slower.

## The one remaining caveat — copy-fidelity is a second knob
Within microbes/viruses alone, pace↔adapt corr is **−0.15** (none): E.coli divides fastest (20 min) yet
evolves slowly (5e-9) due to DNA proofreading (high fidelity); RNA viruses adapt fast because of *sloppy*
copying (~1e-4/site), not raw cycle speed. So adaptation ≈ **life-pace × copy-fidelity**: pace is the
dominant cross-rung term (gives the +0.62) but fidelity modulates within a rung. Refines, doesn't break.

## Honest status
Real cross-rung result, but largely re-derives known biology (generation-time ↔ evolutionary-rate;
metabolic theory of evolution — Gillooly, Martin & Palumbi). Framework's contribution = the equivalent-
whole-wave (rung-matching) rule that fixed the comparison + the space↔time/pace organizing axis. n small,
several evo-rates order-of-magnitude. **Mapping/ already holds a 234-node 3D ARA atlas** (nodes placed by
period/ARA/Action-π; already includes Hare, Lynx, Cell Cycle); animals/viruses can be added there by their
WHOLE-life period — but ARA per species would be estimated (no waveform), so don't fabricate ARA into the
curated atlas.
