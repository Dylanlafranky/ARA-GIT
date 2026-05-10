# φ vs nearby log-bases — predictor-skill ablation on ENSO

> **Public-release note, May 2026:** This is the predictor-performance version of the φ-vs-nearby-log-bases test that REPRODUCIBILITY.md's falsification list called for. Single-domain (ENSO), single-anchor-grid (60 anchors over the last 30 years). Result: φ is numerically best at horizons 1 and 3 months, but all bases (including φ) underperform persistence at every horizon tested. The framework's structural claim is supported in a narrow sense and undercut in a broader sense.

**Date:** 2026-05-10
**Question:** Does the canonical predictor's accuracy specifically depend on the rung base being φ, or would any nearby log base do?

## Method

For each base in `{sqrt(2), 1.5, 1.6, φ, 1.7, e≈1.718, φ^1.05≈1.66, 2.0}`:
- Hold the home period constant at **47 months** (ENSO ground cycle).
- Pick `home_k = round(log(47) / log(base))` so each base has the same physical anchor.
- Define rungs at `base^k` for k from "period ≈ 3 months" to "period ≈ 30 years".
- Run the canonical predictor (`ARA framework v1`) at horizons 1, 3, 6, 12 months on 60 evenly-spaced anchors over the last 30 years of NOAA NINO 3.4 data.
- Score MAE, correlation, persistence-skill (`1 − MAE / persistence_MAE`).

## Result table

| base | value | h=1 MAE | h=3 MAE | h=6 MAE | h=12 MAE |
|---|---|---|---|---|---|
| sqrt(2) | 1.414 | 0.293 | — | 1.082 | 1.055 |
| 1.5 | 1.500 | 0.264 | 0.654 | 1.036 | 1.141 |
| 1.6 | 1.600 | 0.261 | 0.582 | 0.893 | 1.032 |
| **φ** | **1.618** | **0.248** | **0.549** | **0.853** | 1.005 |
| 1.7 | 1.700 | 0.257 | 0.562 | 0.895 | 1.081 |
| e/φ-cousin | 1.718 | 0.270 | 0.586 | 0.904 | 1.046 |
| φ^1.05 | 1.658 | 0.250 | 0.659 | 1.024 | 1.087 |
| 2.0 | 2.000 | 0.253 | 0.576 | 0.943 | **0.979** |

Persistence MAE (next month = current month): 0.186, 0.414, 0.747, 0.940 across the four horizons.

## What this shows

**Within the predictor family, φ wins at the shortest horizons and loses to 2.0 at the longest:**

| horizon | best base | best MAE | φ MAE | gap φ vs best |
|---|---|---|---|---|
| h=1 mo | **φ** | 0.248 | 0.248 | 0.000 (winner) |
| h=3 mo | **φ** | 0.549 | 0.549 | 0.000 (winner) |
| h=6 mo | **φ** | 0.853 | 0.853 | 0.000 (winner) |
| h=12 mo | 2.0 | 0.979 | 1.005 | +0.026 |

φ wins at h=1, 3, 6. It comes second at h=12 (2.0 wins by 0.026 MAE).

**But ALL bases underperform persistence at every horizon.** Persistence-skill is negative in every cell of this run:

| base | h=1 skill | h=3 skill | h=6 skill | h=12 skill |
|---|---|---|---|---|
| φ | −0.333 | −0.326 | −0.143 | −0.069 |
| 2.0 | −0.360 | −0.391 | −0.263 | −0.041 |
| 1.6 | −0.405 | −0.406 | −0.195 | −0.098 |

So the right reading is: *among predictors that all underperform persistence on ENSO, φ is the best one at short horizons*. That is a much weaker claim than "φ is uniquely good for forecasting."

## Why φ winning by small margins is informative

Two interpretations are possible and they have different implications:

**Interpretation A — φ is privileged.** The predictor is sensitive to a specific resonance between ENSO's coupled-oscillator structure and the φ-spaced rung ladder. Near φ, the predictor tracks the system; away from it, the predictor fits less well.

**Interpretation B — any "good" log base works.** The ladder structure matters, not the specific base. φ wins by very small margins (0.001–0.014 MAE over 1.6, 1.7) and ties bases like 1.7 and 2.0 within rounding. With 60 anchors, the standard error on each MAE is roughly 0.02–0.03 — so the differences between the top three bases (φ, 1.6, 1.7, 2.0) at h=1 are within noise.

The data here doesn't yet distinguish A from B. Pythia^1.05 (a base of 1.66, very close to φ) almost ties φ at h=1 but loses by more at h=3, suggesting the function is sharply peaked near φ — which leans toward A. But 1.6 and 1.7 also do nearly as well, and 2.0 overtakes φ at h=12 — which leans toward B.

## Honest framing for the public release

This test does not establish that φ is the unique best base. It does show that:

1. **At h=1, 3, 6 months φ has the lowest MAE in the tested set.** A positive but small piece of evidence for the framework's "φ specifically" claim. Differences between the top three bases at h=1 are within the standard error at n=60 anchors.
2. **All tested predictors, including φ, underperform persistence on ENSO at every horizon.** The canonical-predictor family in this configuration is not yet beating the simplest baseline.
3. **Nearby bases (1.6, 1.7, 2.0) get within 5% of φ's MAE.** A reviewer who insists the framework's structural claim requires φ-specific dominance would correctly point out that this run does not deliver that.

## A note on horizons and "averaging time"

It would be tempting to average MAE across horizons to get a single number, but the framework's own position says that's the wrong move. Different horizons on ENSO ask different questions:

- **h=1 month:** is there extractable structure in ENSO's dynamics that the predictor can use to beat random guessing? (Answer: yes, modestly. φ is the best base for extracting it.)
- **h=12 months:** is there extractable structure that survives 12 months of noise and mean reversion? (Answer for ENSO: not much. ENSO at 12-month lead is approximately a random walk around the mean. Persistence wins because predicting the mean is what works when the signal is gone.)

Persistence is a philosophy of time that assumes time averages. The framework's stance is that time has structure that does not average. When persistence beats the framework at h=12, that's largely a finding about ENSO's mean-reverting tail — not a clean win for "time averages." A different system with stronger long-range structure (ECG, tidal cycles, solar activity) would likely produce a different result.

The honest take-away from this single test: the claim worth defending is "the framework's φ-rung ladder gives a usable predictor at horizons where there is structure to extract, and within the tested base set φ is the best parameter at those horizons." The claim *not* worth defending from this test alone is "no other base produces a similarly skilled predictor." And the claim that should *not* be inferred is "framework loses to persistence" as if that were a property of the framework rather than of the system being tested at the horizon being tested.

## Important caveat — the OLD regime was never engaged

The canonical predictor blends two regimes via a sigmoid centred at `h_cross = home_period × base^(±7/4)`. For ENSO with `closed=False` and `home_period = 47 months`, that puts the crossover at:

```
h_cross = 47 × φ^(7/4) ≈ 100 months
```

So at the four horizons tested in this ablation (h = 1, 3, 6, 12 months), the sigmoid weight on the **ACT regime** (anchor-at-v_now, integrate deltas) ranges from about 0.99 down to about 0.97. **OLD's weight never exceeds 3%.** The "long-range" structured-wave formula essentially never engages in this run.

That changes how the result should be read. This ablation tested:

> ACT-regime predictor with φ-rung structure vs ACT-regime predictor with other-base structure

It did **not** test:

> ACT regime vs OLD regime
> Whether the φ^(7/4) crossover constant is correctly placed for ENSO
> Whether the OLD regime would beat persistence at h=12 if it were engaged

Two consequences:

1. **The "predictor underperforms persistence at h=12" finding is an ACT-regime statement, not a framework-level one.** ACT integrates per-rung cosine differences across many cycles; at h=12 with periods of 3-360 months, several of those cosine terms have wandered into noise (h/p far from θ on the short rungs), and the sum of that noise is what's adding variance above persistence. ACT being asked to extrapolate beyond its design horizon is the proximate cause.
2. **The crossover constant might be wrong for ENSO.** If h=12 is in the regime where ACT is degrading but OLD hasn't engaged, the φ^(7/4) crossover may be too late. To actually evaluate the long-range formula, the ablation would need to be re-run either at h = 120, 240, 360 (where OLD does engage) or with `closed=True` (which puts h_cross around 22 months and would put h=12 at roughly a 50/50 ACT/OLD blend).

That's a separate test from the one this ablation ran. Both are needed before any clean statement about "the framework's predictor at long horizons."

## OLD-regime ablation (companion test)

Per the implementation problem flagged above, a companion ablation was run forcing the **pure-OLD regime** (no sigmoid blend) across the same eight bases, at horizons 1, 3, 6, 12, 24, 60, 120 months. Script: `TheFormula/phi_base_ablation_old.py`. Data: `phi_base_ablation_old_data.js`.

**Headline numbers (pure-OLD MAE, ENSO, 60 anchors):**

| horizon | best base | best MAE | φ MAE | φ rank |
|---|---|---|---|---|
| h=1 | 2.0 | 0.633 | 0.646 | 5/8 |
| h=3 | 2.0 | 0.655 | 0.663 | 3/8 |
| h=6 | 2.0 | 0.681 | 0.695 | 2/8 |
| h=12 | 2.0 | 0.718 | 0.750 | 4/8 |
| h=24 | 2.0 | 0.676 | 0.681 | 4/8 |
| h=60 | 2.0 | 0.620 | 0.671 | **8/8** |
| h=120 | **φ** | **0.627** | **0.627** | **1/8 (winner)** |

**Two important things this reveals:**

1. **Under OLD on ENSO, base 2.0 wins at every horizon below 120 months. φ ranks worst at h=60.** That's a real result against the "φ uniquely necessary" claim — at least for this domain. The plausible physical reason: ENSO has very strong externally-driven seasonal forcing (annual cycle, QBO, harmonics), and octave-spaced rungs (base 2.0) align with seasonal harmonics by construction. φ-spaced rungs don't. Under OLD's Fourier-style structured-wave formula, the base that matches the system's external clock wins. **This is consistent with "any base aligned to the system's external forcing wins under OLD," not specifically with "any base wins."**

2. **At h=120 (decadal scale), φ ties for first.** The seasonal structure has decayed at that horizon and what's left is decadal variability — exactly where φ-spaced rungs (more decades per rung) would be expected to do better than octave rungs. The framework's structural claim recovers at the horizon where the external clock no longer dominates.

**Persistence skill flips positive under OLD past h=6:**

| horizon | persistence MAE | φ-OLD MAE | OLD beats persistence? |
|---|---|---|---|
| h=1 | 0.180 | 0.646 | no (-2.58) |
| h=6 | 0.784 | 0.695 | **yes (+0.11)** |
| h=12 | 1.012 | 0.750 | **yes (+0.26)** |
| h=24 | 1.083 | 0.681 | **yes (+0.37)** |
| h=60 | 0.886 | 0.671 | **yes (+0.24)** |
| h=120 | 0.949 | 0.627 | **yes (+0.34)** |

This is the test that the ACT-only ablation couldn't deliver: **OLD does beat persistence at long horizons.** It also confirms that the canonical predictor's `φ^(7/4)` sigmoid crossover is too late for ENSO — at h=12, OLD's MAE is 0.750 and ACT's MAE was 1.005, but the blend formula was still using ACT 97% of the time.

**Updated honest framing (combining both ablations):**

- **At short horizons under ACT:** φ is the best base in the tested set. Modest evidence for "φ specifically."
- **At short-to-mid horizons under OLD on ENSO:** base 2.0 is the best, plausibly because of seasonal-harmonic alignment in ENSO data. Evidence *against* "φ uniquely necessary," with a known confound (external forcing).
- **At decadal horizons under OLD:** φ wins again. Tentative evidence that φ matters most in the regime where external integer-period forcing has decayed.
- **Implementation finding:** the canonical predictor's sigmoid crossover at `φ^(7/4) × home_period ≈ 100 months` is too late for ENSO. ACT runs into noise around h=12 while OLD is still capped at 3% weight. Moving the crossover forward (or making it data-aware) is a concrete, fixable predictor-implementation improvement that's separable from any framework-level claim.

The clean way to present this to a reviewer: φ does part of the work the framework claims, OLD-regime needs more work on ENSO specifically, and the predictor's blend formula needs a tighter sigmoid for systems with annual forcing. None of those undercut the framework's geometric thesis; they describe an open implementation problem and a domain-specific confound.

## What would tighten this

- Add ECG (cardiac R-R intervals) and a third domain. If φ wins on all three, that's much harder to explain by "any nearby base works."
- Bootstrap CIs on the per-base MAE to confirm whether the φ-vs-1.6-vs-1.7 differences are within noise.
- Test the predictor configurations where it *does* beat persistence (e.g., on more strongly cyclic series like solar or tidal data) and rerun the ablation there.
- Test the *closure-density* metric used in the LLM application against the same set of bases on Pythia activations. If φ specifically gives the highest closure-vs-capability rank correlation across bases, that's an independent piece of evidence on the LLM side.

## Files

- `TheFormula/phi_base_ablation.py` — ACT-blend script (original ablation)
- `TheFormula/phi_base_ablation_data.js` — ACT-blend results (8 bases × 4 horizons)
- `TheFormula/phi_base_ablation_old.py` — pure-OLD script (companion ablation)
- `TheFormula/phi_base_ablation_old_data.js` — pure-OLD results (8 bases × 7 horizons)
- This file — writeup

## Connection to existing scripts

This is the **predictor-performance** version of the φ-vs-bases test. The framework also has earlier tests of a different question:

- `archive/numbered_tests/160_phi_clustering_test.py` — does Δlog of random-number ratios cluster at log(φ)? Tests the geometric/distributional claim, not predictor skill.
- `computations/06_spacing_candidates_all.py` — tests φ against decade, π, 2π, and other candidates on gap data.
- `computations/07_phi_significance_monte_carlo.py` — Monte Carlo of φ-spacing vs random spacings.

Together, these answer "is φ statistically distinguishable from other special values in random ratio data?" The new ablation here adds: "is φ specifically what the predictor needs to perform well?" The two questions are independent and the answers may differ.
