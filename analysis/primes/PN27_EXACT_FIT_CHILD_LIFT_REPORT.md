# PN27 exact-fit child lift — result

**Date:** 22 July 2026  
**Status:** **partial predictive support; not a decisive prime formula**

## Plain-language result

The exact rule Dylan specified was tested without putting a sieve, known nearby prime, prime gap, or retry loop inside the predictor:

1. Start with a chosen number \(N\).
2. Among `1, 3, 5, 9, 11, 13`, take the largest wave that divides \(N\) exactly as Phase A, \(a\).
3. Take its partner \(b=14-a\) as Phase B.
4. Form the child identity \(a+2b\).
5. Move to the upper reference \(N+a+2b\), then cross by one:

\[
\boxed{\widehat P=N+a+2b+1=N+29-a.}
\]

For the worked example:

\[
35\rightarrow a=5,\ b=9\rightarrow35+5+18+1=59,
\]

and 59 is prime.

On 30,000 fresh odd anchors across three scales, the rule hit a prime exactly on its single candidate **2,703 times**, or **9.010%**.

The mean hit rate over the same anchors using each of the six allowed offsets equally was **8.777%**. The ARA rule's advantage was therefore **+0.233 percentage points**, about **+2.65% relative**. Its normal 95% paired interval was `-0.064 to +0.529 percentage points`, so this comparison still includes no advantage.

A stronger matched control permuted the rule's own offset assignments among anchors while preserving the number of times each offset appeared. The null mean was **8.705%** and the one-sided permutation result was **p = 0.0144**. That is suggestive at the conventional 0.05 level, but it misses the prospectively frozen **p < 0.01** threshold.

The frozen verdict is therefore **partial predictive support**, not strong support.

## Results by scale

| Scale | Anchors | ARA hit rate | Uniform-offset rate | Difference | Fixed `+2` rate |
|---|---:|---:|---:|---:|---:|
| Low, around 73 million | 10,000 | 11.000% | 10.987% | +0.013 pp | 11.020% |
| Middle, around 73 billion | 10,000 | 8.350% | 7.902% | +0.448 pp | 8.050% |
| High, around 730 billion | 10,000 | 7.680% | 7.443% | +0.237 pp | 6.830% |
| **Pooled** | **30,000** | **9.010%** | **8.777%** | **+0.233 pp** | **8.633%** |

The direction versus the uniform-offset control was positive at all three scales, but the low-scale difference was essentially zero. Against fixed `+2`, the ARA rule was slightly worse at the low scale and better at the other two.

## The important child-wave pattern

| Selected Phase A | Paired Phase B | Offset | Share of anchors | ARA hit rate | Uniform-offset rate | Difference |
|---:|---:|---:|---:|---:|---:|---:|
| 13 | 1 | 16 | 7.65% | 9.067% | 7.839% | +1.228 pp |
| 11 | 3 | 18 | 8.56% | 9.031% | 9.342% | -0.311 pp |
| 9 | 5 | 20 | 9.37% | 13.625% | 9.089% | +4.536 pp |
| 5 | 9 | 24 | 15.03% | 11.796% | 9.464% | +2.332 pp |
| 3 | 11 | 26 | 14.80% | 12.362% | 8.774% | +3.588 pp |
| 1 | 13 | 28 | 44.58% | 5.974% | 8.533% | -2.560 pp |

The rule is not behaving uniformly. Its clearest positive structure occurs when `9`, `5`, or `3` is the largest exact-fitting child. The fallback `1↔13` child is selected for almost 45% of anchors and performs poorly enough to erase much of that gain.

There is a straightforward arithmetic reason for at least part of this pattern. When \(N\) is divisible by 9, 5, or 3, the corresponding offset moves the candidate away from divisibility by that same small factor. For example:

- `a=9` gives `N+20`, which is `2 mod 3` when `N` is divisible by 9;
- `a=5` gives `N+24`, which is `4 mod 5` when `N` is divisible by 5;
- `a=3` gives `N+26`, which is `2 mod 3` when `N` is divisible by 3.

Conversely, the `a=1` fallback does not know which larger child is nearest to closure. Its `+28` offset can place the candidate directly onto a multiple of 3, 5, or 7. This explains why the first child layer contains useful information but is incomplete.

## Even-anchor negative control

The unmodified rule adds one of six even offsets. Consequently it preserves parity. All 30,000 even-anchor candidates remained even and none was prime. This was expected and confirms that the eligible one-shot prime population must be odd anchors unless the geometry supplies a separate parity crossing.

## What this supports

The result supports a narrow statement:

> Selecting a one-step offset from the largest exact-fitting member of the declared six-wave child set retained a small amount of information about prime survival on fresh odd anchors.

It also supports Dylan's expectation that one child layer may capture much of a local interaction while still missing another branch: the `3`, `5`, and `9` identities are useful, while the broad `1` fallback is under-resolved.

## What it does not support

- It does not yet predict a prime reliably: approximately 91% of one-shot candidates were composite.
- It did not meet the frozen strong-support threshold.
- The observed advantage can largely be understood as conditional avoidance of small divisors. That is structurally meaningful, but it is not yet new prime mathematics.
- It does not show that the child and parent ridge language uniquely causes the improvement.
- It does not justify altering the rule after seeing these results and counting the alteration as part of PN27.

Any refinement of the `a=1` branch must be declared as a new test on untouched ranges.

## Audit trail

- Frozen protocol: `PN27_EXACT_FIT_CHILD_LIFT_PROTOCOL_v1_FROZEN.md`
- Protocol freeze: `PN27_PROTOCOL_FREEZE_MANIFEST.json`
- Blind predictions: `PN27_EXACT_FIT_CHILD_LIFT_FROZEN_PREDICTIONS.csv`
- Target freeze: `PN27_TARGET_FREEZE_MANIFEST.json`
- Scored rows: `PN27_EXACT_FIT_CHILD_LIFT_VALIDATED_ROWS.csv`
- Machine-readable results: `PN27_EXACT_FIT_CHILD_LIFT_RESULTS.json`
- Independent validation: `PN27_EXACT_FIT_CHILD_LIFT_VALIDATION.json`
- Reproducibility notebook: `PN27_EXACT_FIT_CHILD_LIFT_REPRODUCIBILITY.ipynb`

