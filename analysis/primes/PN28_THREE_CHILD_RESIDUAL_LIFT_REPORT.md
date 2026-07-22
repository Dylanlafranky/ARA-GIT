# PN28 three-child residual lift — result

**Date:** 22 July 2026  
**Status:** **negative result for a superseded mixed-units interpretation; not a test of the corrected relational method**

> **Interpretive amendment, 22 July 2026:** After this test, Dylan clarified that every rung must first be converted
> to its own relational ARA coordinate. PN28 instead rounded a dimensionless ARA displacement and added it directly
> to an integer candidate. Within some child classes this became a constant offset (for example, Phase A `3`
> became `N+24`). That is not the intended framework operation. PN28 remains useful evidence against that flattened
> bridge, but its negative result must not be cited against the fully relational three-rung proposal. PN29 tests the
> corrected `/2` then `/2` coordinate transport without adding ARA units to integers.

## Plain-language result

The proposed refinement kept the successful PN27 base candidate and added only the collapsed residual from all three child pairs:

\[
\widehat P_1(N)
=\widehat P_0(N)
+\operatorname{round}\left(4[R_{\rm child}(N)-1]\right),
\]

where

\[
\widehat P_0(N)=N+a_*(N)+2b_*(N)+1.
\]

The factor 4 is the declared two rung doublings. Rounding was performed once, to the nearest integer with exact half cases away from zero. No prime label, parity repair, nearby search, or second attempt entered the predictor.

The 35 example reproduced exactly:

\[
R_{\rm child}(35)=1.0343776,
\qquad
4(R-1)=0.1375105,
\]

which rounds to zero, leaving

\[
35+5+2(9)+1=59.
\]

However, the rule did not transfer successfully across fresh anchors.

## Primary result: 30,000 odd anchors

| Method | Exact one-shot prime hits | Hit rate |
|---|---:|---:|
| Frozen PN27 base | 2,759 | 9.197% |
| Three-child residual correction | 1,374 | 4.580% |

The correction changed 48.76% of candidates and reduced the hit rate by **4.617 percentage points**, approximately a **50.2% relative loss**. Its paired 95% interval was `-4.897 to -4.336 percentage points`.

The corrected rule gained 263 primes that the base missed, but lost 1,648 primes that the base had already hit.

## Result by scale

| Scale | Base | Corrected | Difference |
|---|---:|---:|---:|
| Around 83 million | 11.61% | 5.70% | -5.91 pp |
| Around 83 billion | 8.19% | 4.01% | -4.18 pp |
| Around 830 billion | 7.79% | 4.03% | -3.76 pp |

The result was negative at every scale.

## Relation-broken control

The residual adjustments were permuted within each scale while preserving their exact distribution. Those relation-broken corrections averaged a 6.784% prime rate, substantially above the actual relation-preserving result of 4.580%.

The one-sided test for the declared positive direction returned `p=1.0`. Thus the exact attachment of each residual to its own anchor was actively worse than assigning the same residual values randomly.

## Why it failed

Two clear mechanisms account for most of the loss.

### 1. Odd adjustments broke prime parity

The PN27 base candidate from an odd anchor is odd. Adjustments `-3`, `-1`, or `+1` changed it to an even number. Those groups produced no primes.

Overall, only 81.33% of corrected candidates remained odd.

### 2. The `-2` correction reversed useful child avoidance

The strongest example is the Phase A `3` branch:

- PN27 used `N+26`, which moves a multiple of 3 to `2 mod 3`;
- PN28 assigned `k=-2`, producing `N+24`;
- because 24 is divisible by 3, every resulting candidate remained divisible by 3.

All 4,403 odd anchors in this branch received `-2`. The base found 584 primes; the corrected rule found zero.

The Phase A `9` branch also fell to zero because its `-1` or `-3` corrections changed odd base candidates to even numbers.

## Secondary even-anchor result

The PN27 base preserves even parity, so its 30,000 even-anchor candidates contained no primes. PN28's odd residual adjustments converted 19.12% of corrected candidates to odd and found 548 primes, a 1.827% hit rate.

This does not rescue the primary rule. It simply confirms that an odd adjustment can act as a parity crossing when the base begins even—the same operation that damages an odd prime candidate.

## Interpretation for ARA

This result does **not** show that combining all three child pairs is useless. It shows that the particular collapse law

\[
k=\operatorname{round}[4(R_{\rm child}-1)]
\]

is not a valid upward transport rule for prime candidates.

The signed residual is dominated by exact-divisor and parity structure. Doubling it uniformly across two rungs treats every displacement as if it had the same meaning after a scale change. In this dataset it frequently reverses the modular protection already captured by the base child.

The useful scientific conclusion is therefore:

> The three-child state may be descriptive, but its signed mean cannot be transported upward through two simple doublings and rounded as a direct integer correction.

Any later refinement must be frozen as a new test. PN28 itself remains a clear negative result.

## Audit trail

- Frozen protocol: `PN28_THREE_CHILD_RESIDUAL_LIFT_PROTOCOL_v1_FROZEN.md`
- Protocol manifest: `PN28_PROTOCOL_FREEZE_MANIFEST.json`
- Blind predictions: `PN28_THREE_CHILD_RESIDUAL_LIFT_FROZEN_PREDICTIONS.csv`
- Target freeze: `PN28_TARGET_FREEZE_MANIFEST.json`
- Scored rows: `PN28_THREE_CHILD_RESIDUAL_LIFT_VALIDATED_ROWS.csv`
- Results: `PN28_THREE_CHILD_RESIDUAL_LIFT_RESULTS.json`
- Independent validation: `PN28_THREE_CHILD_RESIDUAL_LIFT_VALIDATION.json`
- Executed notebook: `PN28_THREE_CHILD_RESIDUAL_LIFT_REPRODUCIBILITY.ipynb`
