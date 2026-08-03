# T328 post-result return sensitivity audit

**Date:** 2 August 2026  
**Status:** validation-only; not a frozen verdict gate

The frozen test asked which candidate had the lowest mean Fibonacci-return
error. After that result was known, this audit applied the existing
whole-video cluster bootstrap to the paired return differences.

| Comparison (Phi minus rival) | Evaluation mean | Evaluation 95% | Holdout mean | Holdout 95% |
|---|---:|---:|---:|---:|
| `8/21` | -0.005487 | -0.005906 to -0.005141 | -0.005760 | -0.006338 to -0.004868 |
| persistence | -0.009957 | -0.024073 to 0.009224 | -0.046202 | -0.178983 to 0.001313 |

Negative values favour Phi. Phi is a stable numerical return winner over
`8/21`, but its intervals against persistence cross zero. Combined with the
failed directional-resolution gate, this audit does not establish exact-Phi
recovery and does not change the frozen `PARTIAL / MIXED` verdict.

## Shape check across every lag 1-21

The ideal Phi carrier predicts return distances `-0.472136`,
`-1.708204`, `-4.180340`,
`-7.888544`, `-14.068884` and
`-23.957428` at the registered Fibonacci lags.
Those values shrink toward zero.

The observed evaluation means at those lags were
`0.126486, 0.147805, 0.155314, 0.167894,
0.177475, 0.189238`; holdout was
`0.198213, 0.193860, 0.205760, 0.224806,
0.218154, 0.218303`. Evaluation's smallest nontrivial
return over all lags `2..21` occurred at lag `2`; holdout's occurred at lag
`3`. There is no observed concentration of near-returns at the larger
Fibonacci lags. Thus "Phi won the frozen return MAE" is a template-ranking
fact, not evidence that the bubbles visibly executed Fibonacci near-closures.
