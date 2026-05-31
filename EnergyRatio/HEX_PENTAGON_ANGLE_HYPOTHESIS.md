# Hypothesis — the Hexagon→Pentagon angle band as the space↔time dial

**Status: TESTED → NOT SUPPORTED (31 May 2026).** Principled and elegant, but the data said no — see
"Test result" below. Kept on record because the *geometry* (60° hexagon = space, 72° pentagon = time)
is still a clean framing, and because honest negatives are part of the value.

> **TEST RESULT (31 May 2026):** Measured the octave rung-to-rung lock-angle (1:2 phase) on five real
> systems spanning a wide ARA range. The strong-locking ones — **Solar (ARA~1.73, PLV 0.73) 63.2°,
> Golden star (~2.0, PLV 0.78) 63.3°, Cepheid (~2.4, PLV 0.99) 62.7°** — all pin at **~63°** and do
> **NOT** climb toward the pentagon (72°) as ARA rises. The angle is **roughly constant ~63°**, not an
> ARA dial. (ECG 55.6°/PLV 0.26; ENSO weak/ignore.) So the "offset-from-60 ∝ ARA" claim is not
> supported: strong locks park near the hexagon end (~63°) flat across very different ARAs. Caveats: the
> auto-ARA measure in that run was buggy (so no clean correlation computed), but the angle being *flat*
> across systems of clearly different ARA is enough to reject the climb. The consistent ~63° is itself a
> real (mildly curious) value — between hex 60° and pent 72°, ≈ arctan 2 = 63.4° — possibly coincidental.
> Script: `/tmp/hexpent_test.py` (port to EnergyRatio if revisited).
>
> **REFRAME THAT PARTLY LANDED (gate-angle = energy-ratio):** Dylan re-read the angle not as the
> space↔time dial but as the *gate opening* / per-cycle energy-shed rate (~60 rigid/static → 72 = max
> time, near time singularity). Checked against the 4 golden stars' independently-measured leanness:
> **corr(lock-angle, R21 leanness) = +0.93** (angle vs 2nd-mode ratio only +0.47). So the angle is NOT
> noise — it tracks the energy-ratio (R21): steeper gate (→72°) = more shed; balanced (~63°) = leaner.
> KIC4064484 at 72° has the highest R21 (0.118). This SUPPORTS the gate-angle=energy-ratio reading.
> **HEAVY caveats:** n=4 (r=0.93 borderline, ~p0.07); and lock-angle (φ21 phase) & R21 (φ21 amplitude)
> are the two Fourier params of the SAME 2nd harmonic, which are *known to co-vary* in pulsating-star
> Fourier sequences — so this may be a standard stellar relation re-read through the framework lens
> (consistent, not necessarily new). NET: the space↔time *dial* stays dead; but "angle ↔ energy-shed
> rate (R21)" is real-and-suggestive (n=4). Ties to the BEESWAX (π−3)/π gate idea. Script: `/tmp` inline.
>
> **EXPANDED TEST (n=6 strong lockers — solar + 4 golden RRc stars + Cepheid):** the "constant ~63°"
> also broke. Angles **spread 62.7°→72.0°** (mean 65.6°, std 3.3°): Solar 63.2, KIC5520878 63.3,
> KIC4064484 **72.0**, KIC8832417 64.3, KIC9453114 67.8, Cepheid 62.7. So it is **not a single constant
> either.** They loosely sit near Platonic angles (icosa 63.4 ×3, pentagon 72.0 ×1, tetra ~70.5 ×1) and
> KIC4064484 hitting 72.0° (pentagon) exactly is eye-catching — BUT with 5 candidate angles spanning
> 54–72° any value is auto-"near" one (multiple-comparisons), and 4 *same-type* golden stars scattering
> 63→72° looks like measurement variation, not a polyhedral law. **Net: no clean lock-angle structure —
> not a dial, not a single constant, not convincingly polyhedral.** "Shape up from a pyramid" (discrete
> polyhedral angles) tested → not supported on this evidence. Curiosities kept: a golden star on 72°
> (pentagon), a loose cluster near the icosahedral 63.4°. Script: `/tmp/poly_test.py`.

## The claim

When a real signal is split into octave rungs and you measure the **phase at which one rung locks to
the next** (the rung-to-rung handover phase), that angle should live in the band:

- **60° = 360/6 = the hexagon** — 6-fold, tiles the plane, rational, *locks*. The **space pole**
  (same rational/space pole as the bee honeycomb).
- **72° = 360/5 = the pentagon** — 5-fold, where φ lives (φ = 2·cos 36°, and 36° is the pentagon
  half-angle; the space↔time shear is 36°, so 2×36 = 72). The **time / golden pole** (the golden star).

**Hypothesis:** a system's lock-angle position *within* [60°, 72°] reads out **how space- vs
time-angled it is** — i.e., its ARA. Sit at 60° → tied to the rational/space pole; drift toward 72°
→ tied to the golden/time pole. **Offsetから 60° should rise with ARA** (more time-dominant = higher
ARA = closer to the pentagon).

## Why it's principled
This is the hexagon↔pentagon (6-fold↔5-fold) tension expressed as an angle — the same two poles that
run through the whole framework: hexagon = rational/space/locking (bee, octave ladder), pentagon =
golden/time/non-locking (φ, golden stars). The shear that turns the space octave into time is 36°
(φ = 2cos36°); its double, 72°, is the pentagon. So the band endpoints are not arbitrary — they are the
two regular polygons that tile-vs-don't-tile, i.e. the space and time poles.

## Evidence so far (thin — n=2, weak locks)
Octave-rung phase-lock measured on real series (Hilbert phase of octave-bandpassed rungs, 1:2 relative
phase, middle 80%):

| system | ARA (≈) | lock angle | PLV (lock strength) |
|---|---|---|---|
| ECG (heart RR) | ~1.6 (engine) | 60.7° | 0.29 (moderate) |
| Solar (sunspots) | ~1.73 (donor) | 61.4° | 0.67 (strong) |
| ENSO (NINO) | ~0.82 (consumer) | — | locked weakly (PLV ~0.12), angle unreliable |

Directionally consistent (higher-ARA Solar sits higher than ECG), **but**: only ~0.7° apart, n=2, and
most pairs lock weakly so their angle is untrustworthy. So this is **suggestive at best, not confirmed**.
The measured angles hug 60° (the hexagon/space end); none reach toward 72° yet.

## What would confirm / falsify it
Gather many **strong-locking** octave systems spanning a wide ARA range (consumer <1 → engine φ →
donor 1.75 → harmonic 2) and test whether the lock-angle **climbs monotonically from ~60° toward ~72°
as ARA rises**. Confirm = clear monotonic angle↔ARA relation across the band. Falsify = angle flat, or
uncorrelated with ARA, or locks too weak to read.

## Honest caveats
- n=2 reliable points; 0.7° spread is within noise of a moderate lock.
- Simple octave-bandpass + Hilbert, one operationalization of "rung-to-rung phase."
- "Handover pitch" in the 3D viewer is a *spatial* texture knob; this angle is the *phase-coupling*
  version — related in spirit, not identical.
- Octave-rung locks came out near the rational 60° (hexagon), consistent with octaves being the
  rational/space ladder; the golden/pentagon end may only appear for genuinely time-dominant systems
  (untested).

## Spin-off hypothesis — the ARA / Angle / Loss trade-off triangle (logged 31 May 2026)

Dylan's framing: ARA, gate-angle, and loss (shed-rate, R21) form an **iron triangle** ("pick 2 of 3") —
they are *not* independent; a system slides around inside a constraint, trading one against the others.
Reading: **ARA = the water that makes it through the pipe; Angle = the gate tilt (how time-favoured the
flow is); Loss/R21 = the spill/tension = identity-information handed into the *time* dimension, which
reads as "loss" only from our current-frame vantage** (the couplings sever and move to the next frame).
So "loss" inverts depending on which frame you score from — to us it's loss, to time it's transfer.

**Prediction:** the three quantities lie on a **2-D constraint surface** (pick-2), not a 3-D independent
cloud. Measured edge so far: **angle ↔ loss = +0.93** (one taut side already), and angle ↔ 2nd-mode ratio
(≈ARA proxy) = +0.47.

**Why not tested yet / how to test cleanly:** current data is n=4 golden stars, and 2 of the 3 corners
(angle = φ21 phase, loss = R21 amplitude) come from the *same* 2nd harmonic → their link is partly
definitional, so a "surface" on 4 such points would over-fit. **Proper test:** many systems (dozens)
with ARA, gate-angle, and loss measured *as independently as possible*; check whether they collapse onto
a 2-D surface (constrained trade-off → triangle real) or fill 3-D (independent → no triangle). Falsify =
3-D scatter / no constraint. **Status: OPEN — logged for a future wider-dataset test.**

See `MASTER_PREDICTION_LEDGER.md` (HEXPENT row), memory `project_hex_pentagon_angle.md`,
`ARA_REDERIVED_PRINCIPLES.md` (φ = 2cos36° / pentagon), and the bee-hexagon foil note.
