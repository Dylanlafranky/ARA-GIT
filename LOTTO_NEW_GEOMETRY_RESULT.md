# Lotto re-test with the corrected octave geometry — null confirmed

**Date:** 30 May 2026
**Data:** Australian Saturday Lotto (TattsLotto), 6-of-45, 150 real draws (2023-06-03 → 2026-05-02), fetched from public draw history. Real data only.
**Script:** `TheFormula/lotto_new_geometry_test.py`
**Status:** Re-run of the original lotto test (`archive/numbered_tests/243BL10_lotto_prediction.py`) using the post-30-May octave/φ split instead of the old φ-as-spacing framing. Result is the same: **no out-of-sample signal.**

## Why we re-ran it

The original lotto test concluded randomness is a perfect shock absorber (ARA = 1.0) and that the only positive number (mirror × recency, +16.3%) was **not statistically significant** (z ≈ +1.64). Since then the geometry was corrected: rung spacing is the **octave** (×2) and **φ is the handover/coupling timing** (golden duty 0.39/0.61), not the spacing. Dylan asked whether the better geometry, applied properly, finds anything the old framing missed.

Three approaches were applied, all strictly causally:

1. **Octave ladder + φ-handover** — each number's recency gap is placed on a doubling ladder; re-appearance is scored by nearness to the golden-duty handover point (0.618) within its octave band.
2. **Mirror through singularity** — score the octave/φ ranking, then take the mirror partners (number n ↔ 46−n, the ARA mirror 2−A reflected onto the 1–45 range).
3. **Two-rulers / meta-ARA** — blend an octave/structure ruler (occupancy) with a φ/handover ruler (golden-duty recency) at golden duty (0.382 / 0.618).

## Strict-causal protocol (all 7 points enforced)

Features for each target draw use **only** draws strictly before it; no full-dataset statistic; 100 rolling out-of-sample holdouts; baselines = random Monte-Carlo (4000 reps) + most-frequent persistence; correlation and hit-rate lead, not MAE; nothing tuned on the test outcomes.

## Result

Random Monte-Carlo reference: **0.798 matches/draw** (sd 0.079), matching the analytic 6×6/45 = 0.800.

| strategy | matches/draw | z vs random | score-corr | ≥1 hit % |
|---|---|---|---|---|
| random (control) | 0.730 | −0.86 | −0.008 | 60.0 |
| most_frequent (persistence) | 0.790 | −0.11 | −0.010 | 61.0 |
| octave + φ handover | 0.800 | +0.02 | +0.010 | 60.0 |
| mirror thru singularity | 0.740 | −0.74 | −0.008 | 57.0 |
| two-ruler / meta-ARA | 0.820 | +0.27 | +0.002 | 63.0 |

Every strategy sits within ±1σ of pure chance. The best (two-ruler, z = +0.27) is noise. Score-vs-actual correlations are all ≈ 0. **The corrected octave/φ geometry does not predict lottery numbers** — exactly as the framework expects of a system at the irrationality singularity.

## Reading it in framework terms

This is a **confirmation, not a failure.** A fair lottery is the cleanest physical realisation of ARA = 1.0 — a perfect shock absorber with no engine, no storer, no coupling to lean on. There is no octave ladder to climb because there is no pump (rung 0) generating structure; there is no φ-handover because nothing hands energy between rungs. The geometry is built to describe systems that *store and transfer* energy in time. A lottery does neither, so the geometry correctly returns nothing. Even the mirror-through-singularity move — which gave the old framing its one tantalising +16.3% — collapses to noise here (z = −0.74) once tested causally across many holdouts rather than on a single split.

The earlier +16.3% was always inside the noise band; this multi-holdout run makes that explicit. Randomness remains the structure, not a barrier hiding one.

## Appendix A — anti-phase flip (does "worse than random" hide a usable signal?)

The mirror strategy scored *below* random (z = −0.74). If a ruler reliably picked the **wrong** numbers, flipping it (bet the bottom 6 instead of the top 6) should pick the **right** ones — that is exactly how real anti-phase coupling works (eTNO perturber, Walker-circulation SOI partner). So we tested the flip.

| strategy | matches/draw | z vs random |
|---|---|---|
| mirror thru singularity | 0.740 | −0.74 |
| mirror thru singularity **[ANTI-PHASE]** | 0.840 | +0.52 |
| octave+φ **[ANTI-PHASE]** | 0.800 | +0.02 |
| two-ruler / meta-ARA **[ANTI-PHASE]** | 0.830 | +0.40 |

The flip turns the negative into a positive — but it fails the stability check, which is what separates a real anti-phase lock from noise. A true anti-phase partner is anti-phase in *every* stretch of data. Split-half on the mirror flip:

- first 50 draws: **0.96** matches/draw (above random)
- second 50 draws: **0.72** matches/draw (below random)

It wins in one half and loses in the other — a coin that came up heads early, not a steady lock. The +0.52 overall is the lucky first half carrying it, and is inside the noise band anyway (≈ +2 needed for significance). Anti-phase prediction needs a **pump** setting a steady phase to sit opposite to; a fair lottery has no pump, so each draw's "phase" is freshly random and "the opposite of random" is just random again.

## Appendix B — the gravity / physical-machine lens (where lottery prediction has actually worked)

This is the one lens with a real precedent: lottery prediction *has* succeeded historically when a machine was physically biased (a worn, heavier, or out-of-round ball; an air-mix quirk). That bias is a concrete, testable claim — and unlike the framework rulers, it does **not** need a pump. A biased ball leaves a *persistent* fingerprint. Script `lotto_gravity.py` tested for it directly.

| test | what a real bias would show | result (150 draws) | reading |
|---|---|---|---|
| Fairness (χ² of per-ball counts) | lumpy, p < 0.05 | χ² = 32.1, **p = 0.91** | flat / fair |
| **Persistence** (hot balls stay hot, half vs half) | strong **positive** r | **r = −0.08** | no worn ball |
| Hot-ball carry (bet 1st-half hot 6 on 2nd half) | beats 0.80 random | 0.76 / draw | slightly *worse* |
| Gravity momentum (draw-sum lag-1 autocorr) | positive carryover | r = −0.14 | no memory |
| Centroid drift (gravity pulling a region) | slope ≠ 0, mean ≠ 23 | mean 22.9, slope −0.006 | centred, no drift |

The decisive one is **persistence**. Every historical biased-machine win showed up as the *same* balls staying hot over time. Here the first-half hot balls are essentially uncorrelated with the second-half hot balls (r = −0.08), and betting them does slightly *worse* than chance. The machine is fair. This matches the original 1,989-draw finding (frequency landscape flat, z = −0.19) and is exactly what modern lotteries engineer for by rotating multiple certified ball sets and machines between draws.

So the gravity lens is the strongest place this *could* have been wrong — and the data closes it. No physical bias, no momentum, no drift. Combined with the null geometry result and the failed anti-phase flip, the conclusion holds from every angle tested: **a fair lottery is structureless because the fairness is the structure.**

## Files
- `TheFormula/lotto_new_geometry_test.py` — the causal multi-holdout test
- `TheFormula/lotto_data/saturday-lotto.csv` — 150 real draws
- `archive/numbered_tests/243BL10_lotto_prediction.py` — the original test
- `framework_memory/project_randomness_lotto.md` — prior lotto findings (Claim 55, ledger T54–T59)
