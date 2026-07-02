# Driven Triple-Pendulum — an ARA Reading

**Status:** exploratory, real data, n=1 driven triple run. Companion to `PENDULUM_ARA_RESULT.md` (undriven).
**Data:** dynamicslab MultiArm-Pendulum (Zenodo 10.5281/zenodo.6633719). Driven run `TripleDataWithControl_1` (cart driven back-and-forth, 70 s, 10 kHz). Cart drive trace from `SingleDataWithControl_1` (the only file that recorded the cart channel). Undriven `run1` (`pend_triple`) is the control.
**Visualised:** `pendulum_viz/pendulum_driven_dashboard.html`.

## Method — reverse-inference (the undriven system is the control)

The triple driven file records **only the arm angles**, not the cart channel (the docs claim the cart was recorded, but it isn't in these files). So we do **not** measure the drive directly. Instead: we already know the free-swing behaviour exactly (1.333 s common mode, bottom-rung dominance, ~2.5× decay, arm-2-carrier / 1-3 anti-phase). We run the **same battery** on the driven run and read the **deviations** — those deviations *are* the drive's fingerprint, recovered from the arms alone. Where arm-1 stops being its clean free-swing self, that departure is the cart's hand. (Dylan's framing.)

## What the drive did (driven vs undriven control)

1. **Entrainment — the drive imposes a new clock.** Free, every arm runs at the natural **1.33 s** common mode. Driven, every arm locks to a shared **1.56 s** — the cart's imposed period, recovered purely from the entrained arms (no cart channel needed). The external clock overrides the system's natural clock and controls its timing down the whole chain. (Ties to the ridge/clock rule: a clock = whatever imposes controlled timing on an identity; here the cart is that clock.)

2. **Kept alive — sustained vs decaying envelope.** Free envelope decays ~**2.5×** over the record (the system settling toward the 1.0 ridge — dying). Driven envelope is nearly flat (~**1.2×**): decay ratios 2.26/2.32/2.55 → **1.17/1.22/1.29** (arms 1/2/3). Energy in lets it keep handing over instead of running down. The "death wave" (system-scale release) is largely cancelled by the drive.

3. **Chaos regularized — order propagates to the bottom.** Clock-likeness per arm 0.91/0.98/**0.77** → 0.96/0.96/**0.95**. The chaotic bottom arm becomes clock-like; the cart's rhythm reaches all the way down.

4. **Synchronized, and the carrier backbone strengthens.** corr(arm1,arm3) **+0.67 → +0.99**; partial corr(1,3|2) **−0.36 → −0.61**. The shared external clock pulls the chain together, and the undriven structural finding (arm-2 = shared carrier, ends anti-phase once it's removed) is **robust to driving** — it strengthens. (Partial-corr flip = common carrier, not proven mediation.)

5. **Leadership migrates UP toward the drive entry.** Who-turns-first share: free arm1/arm2/arm3 = 45/11/45 → driven **50/15/35**. The drive enters at the top, so leadership shifts up-chain — partially reversing the free bottom-rung dominance.

6. **Irreversibility concentrates at the bottom.** Time-reversal asymmetry (derivative skew; 0 = reversible): free ~±0.03 all arms → driven arm-3 = **−0.095** (largest). The injected energy's throughput signature shows most at the deepest arm.

## The real drive (single-pendulum file, ground truth)

The single driven file *does* carry the cart: a **2.13 s** cart oscillation, amplitude ~5 cm, **slightly asymmetric** (rise/fall 0.92 — not a pure sinusoid, the ARA-relevant signature). The arm entrains to it (drive→arm-1 amplitude gain ~1.5, near anti-phase). This confirms the back-out logic on a case where the cart is visible.

## The cart is one more rung of the same ladder (ground-truth transfer)

Tested directly: the **single-pendulum file records the real cart**, so the true `cart→arm1` transfer can be measured and laid against the triple's chain steps (`arm1→arm2`, `arm2→arm3`), each at its own drive fundamental.

**At the drive fundamental the three steps are indistinguishable** — gain ~1.1–1.3× (gentle per-rung amplification), phase ≈ 0° (each rung moves in phase with the one above), coherence = 1.00:

| step | gain @ f₀ | phase @ f₀ | coherence |
|---|---|---|---|
| cart→arm1 (real cart) | 1.07 | −0.3° | 1.00 |
| arm1→arm2 | 1.24 | +2.1° | 1.00 |
| arm2→arm3 | 1.29 | +2.3° | 1.00 |

So at the entrained driving frequency, **the cart behaves as one more rung** — Dylan's "tell the cart by a rung" confirmed with ground truth. (Caveat: cart gain is mixed units m→rad, so the gain *number* isn't strictly comparable; the robust matches are phase ≈ 0° and coherence = 1.0.)

**The harmonic tail is where rung identity lives.** At 2×/3× f₀ the per-step phases scatter (cart→arm1 −27°/−171°, arm1→arm2 +37°/+36°, arm2→arm3 +171°/+175°) and the broadband transfer-shape correlations are weak (+0.09 to +0.36). So the steps are identical *at the fundamental* (entrainment makes the chain self-similar there) and divergent *in the harmonics* (the growing harmonic spray down the chain — the anti-correlated per-rung transform). **Fundamental = "same ladder"; tail = "which rung."** This reconciles the self-similar spectra (shared fundamental) with the earlier finding that the per-rung transform isn't a clean repeat (it's a repeat only at f₀). Visualised in `pendulum_driven_dashboard.html` §7 (gain/phase/coherence vs f/f₀ + harmonic fan-out).

## Honest fences

- **n = 1 driven triple run** (`TripleDataWithControl_1` is the only one). The double has two driven runs (`DoubleDataWithControl_1/2`) for a simpler-chain cross-check if wanted.
- **Rise/fall *duration* ARA stayed ~symmetric even driven** (~1.0). The asymmetry/irreversibility the drive injects is subtle and shows up in the **derivative-skew** measure (concentrated at arm-3), not in swing-duration asymmetry. So the drive's signature is mainly entrainment / sustain / sync / leadership-shift, not strong waveform asymmetry.
- The triple drive frequency (1.56 s) differs from the single file's (2.13 s) — each run had its own cart driving, so the single is a *method* check, not the same forcing.
- Standard techniques (FFT, Hilbert phase, partial correlation, cross-correlation) used as instruments; the ARA contribution is the organising read (external clock, sustain = kept-handing-over vs die, leadership toward the forced end, carrier robustness). φ not invoked anywhere.
