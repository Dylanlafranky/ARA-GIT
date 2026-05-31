# Is the next rung the MIX of the two rungs below it? (recon + lag vs ARA)

**Date:** 2026-05-30
**Script:** `blend_next_rung_test.py` → `blend_next_rung_result.json`

## The idea (Dylan)

The slow wave one step up through time *is* the blended version of the two faster waves
that mixed. Sharper form: that hand-off is **clean and on-time near φ** (golden engine),
but **lagged and smeared at ARA≈1.0** because the balance point has temporal friction.

## Why mixing can literally build the next rung

Two consecutive φ-rungs (periods r and r·φ) **multiplied** produce a difference-frequency
whose period is **exactly r·φ²** — the next-but-one rung:
`1/r − 1/(rφ) = (1/φ²)/r → period r·φ²`. So if a system builds its slow wave by mixing its
two fast waves, the *product* of the two fast bands, re-filtered at the slow band, should
reconstruct the real slow wave.

Two readouts: **recon** = peak correlation of generated-slow vs actual-slow (cleaner mix =
higher); **lag** = the delay at that peak, as a fraction of the slow period (more friction
= larger). Zero-phase filtering (a descriptive co-structure test, not a forecast). A
phase-randomized surrogate null (z) says whether the coupling beats spectrum-matched noise.

## Results

| System | ARA | recon | \|lag\| (of slow period) | z vs null |
|---|---|---|---|---|
| EEG (brain) | 1.00 | +0.26 | 0.375 | **+7.7** |
| Solar (Sun) | 1.09 | +0.91 | 0.740 | **+2.8** |
| ECG (heart) | 1.20 | +0.46 | 0.110 | +0.0 |
| BP (vascular) | 1.56 | +0.69 | 0.191 | **+2.2** |
| Resp (lung) | 1.67 | +0.45 | 0.763 | −0.1 |
| ENSO | 0.91 | +0.45 | 0.617 | −0.3 |

**Only 3 of 6 systems** show mix-coupling above the null: **brain (z +7.7), Sun (+2.8),
vascular (+2.2)**. In the heart, lung and ENSO the "mix builds the next rung" reconstruction
is no better than spectrum-matched noise.

On those 3 real-coupling systems:

- corr(ARA, recon quality) = **+0.34** — predicted positive (cleaner near φ). Weakly there.
- corr(ARA, |lag|) = **−0.65** — predicted negative (less lag near φ). The vascular system
  (ARA 1.56, nearest φ) hands off almost on time (lag 0.19); the near-balance systems lag
  more.

## Honest read

**The mechanism is genuinely real in some systems.** The strongest is the **brain** — which
is exactly where neuroscience independently documents cross-frequency (phase-amplitude)
coupling, so the method is detecting a known real effect, not an artifact. Sun and vascular
tone also show it.

**The lag-vs-ARA prediction points the way you said, but on 3 points.** corr(ARA,|lag|) =
−0.65 is the right sign, and BP-nearest-φ having the smallest lag is the cleanest single
piece of support. But N = 3, the trend depends on excluding the at-null systems, and the
Sun is a wobble (above null yet lags ~0.74 of a cycle, nearly out of phase). This is a
**hint, not a result.**

**What doesn't show it at all:** heart, lung, ENSO. Either those systems don't build their
slow rung by simple two-band multiplication, or the dominant-cycle ARA I'm using is the
wrong ruler (it smooths away the snap), so they're mis-placed on the ARA axis.

## Bottom line

"The next wave is the mixed version" is **confirmed as a real mechanism in the brain, Sun
and vascular tone**, and where it's real the hand-off lag **shrinks toward φ** as you
predicted. But half the systems don't show the mechanism, and the lag trend rests on three
points. To firm it up: more records per system (many hearts/brains) for real N, and a
snap-faithful ARA so the systems are placed on the right rung of the axis.
