# Vertical ARA long-chain dyadic reconstruction — result

**Date:** 1 August 2026  
**Source:** Pandey et al., Zenodo `10.5281/zenodo.15102957`  
**Registered protocol:**
`FROZEN_PROTOCOL_VERTICAL_ARA_DYADIC_CHAIN_2026-08-01.md`  
**Verdict:** **NOT SUPPORTED for the registered Phi-specific long-chain
placement**; a real scale-dependent temporal-order effect is present, but it
is not stable across the broken-lineage control, fixed targets and holdout

## Technical summary

The public bubble tracks were long enough to follow one recorded identity
through five dyadic temporal levels: 1, 2, 4, 8 and 16-frame children closing
2, 4, 8, 16 and 32-frame parents. The final analysis retained `125`
calibration roots, `172` evaluation roots and `40` strict-holdout roots.

Evaluation trajectories became closer to Phi as the window grew. Mean direct
Phi loss fell by `0.166028`, with a whole-video 95% interval
`[-0.230093, -0.116381]`; the five-level slope was also negative
(`-0.029897`, interval `[-0.041302, -0.016917]`). This was not merely the
result of having more vectors: the real ordering improved more than a
within-root step permutation.

The registered interpretation nevertheless failed. Broken lineages improved
at least as much as the real lineages, the strict holdout showed only a weak
directional decrease, and Phi was not the best fixed target at the coarsest
evaluation level. The evaluation free target was `1.374419`, and
`sqrt(2)` had lower mean loss (`0.235358`) than both `1.5` (`0.242887`) and
Phi (`0.261103`). Holdout moved differently: its free target was `1.638332`
and Phi had the lowest fixed-target mean loss (`0.252813`). This split
instability is inconsistent with one universal Phi handover in this
centroid-trajectory representation.

The cleanest retained finding is therefore narrower: **coarse temporal vector
aggregation changes and often narrows child-magnitude asymmetry, and observed
time order matters in evaluation, but the limiting coordinate is
condition-dependent rather than Phi-specific.**

## What was measured

One inference root was one tracker ID at 33 exactly consecutive 50-fps frames,

\[
P_0\to P_1\to\cdots\to P_{32}.
\]

At level \(\ell\), each child spanned \(h_\ell=2^\ell\) frames:

\[
A_\ell=P_{h_\ell}-P_0,
\qquad
B_\ell=P_{2h_\ell}-P_{h_\ell}.
\]

The tested asymmetry was

\[
r_\ell=
\frac{\max(\lVert A_\ell\rVert,\lVert B_\ell\rVert)}
     {\min(\lVert A_\ell\rVert,\lVert B_\ell\rVert)},
\]

with direct target loss

\[
L_{\tau,\ell}=
\left|\log\left(r_\ell/\tau\right)\right|.
\]

The exact identity \(A_\ell+B_\ell=P_{2h_\ell}-P_0\) was treated as
bookkeeping, not evidence. Phi was never used to construct or correct the raw
ratios.

## Coverage

| Split | Complete roots | Contributing videos |
|---|---:|---:|
| Calibration | 125 | 4 |
| Evaluation | 172 | 10 |
| Strict holdout | 40 | 4 |

One feasible evaluation chain was excluded from the registered path because a
nested child displacement was below the previously frozen `0.0005 m`
resolution floor. The holdout exceeded the registered minimum of 20 roots and
three videos.

No uninterrupted track reached 64 steps, so the experiment cannot say whether
a sixth dyadic level would behave differently.

## The fitted target does not converge monotonically

The free target is the geometric median of the direct ratios at each level. A
stable hidden handover should approach a common value across increasing
levels and repeat across source splits. It did neither.

| Child span (frames) | Calibration | Evaluation | Holdout |
|---:|---:|---:|---:|
| 1 | 1.824096 | 1.663596 | 1.469814 |
| 2 | 1.503894 | 1.393481 | 1.406844 |
| 4 | 1.317301 | 1.346243 | 1.555122 |
| 8 | 1.391081 | 1.303683 | 1.441212 |
| 16 | 1.499867 | 1.374419 | 1.638332 |

The sequence oscillates with level and differs materially by experimental
condition. Calibration ends almost exactly at `1.5`; evaluation ends below
`sqrt(2)`; holdout ends close to Phi. The longer chain therefore exposes
structure, but not one universal numerical destination.

## Evaluation convergence is real but not same-lineage-specific

Negative endpoint change means the 32-frame parent is closer to Phi than the
2-frame parent.

| Reading | Evaluation mean | 95% video-cluster interval | Holdout mean |
|---|---:|---:|---:|
| Real endpoint change | -0.166028 | [-0.230093, -0.116381] | -0.032828 |
| Real five-level slope | -0.029897 | [-0.041302, -0.016917] | -0.011670 |
| Real − permuted endpoint change | -0.152838 | [-0.243509, -0.051301] | +0.109184 |
| Real − broken-lineage endpoint change | +0.038025 | [-0.043778, +0.095930] | +0.035120 |

The real evaluation ordering beats the permutation control, which shows that
observed temporal order contributes to the scale effect. It does not beat the
broken-lineage control: pairing child halves from different same-video roots
produces at least as much apparent Phi convergence. Holdout also reverses the
real-versus-permutation endpoint comparison. These failures prevent the
effect from being assigned to a persistent same-identity Phi handover.

## Phi is not the coarsest evaluation target

Mean direct losses at the 16-frame-child / 32-frame-parent level were:

| Target | Evaluation mean loss | Holdout mean loss |
|---|---:|---:|
| 1 | 0.379960 | 0.536735 |
| sqrt(2) | **0.235358** | 0.285964 |
| 1.5 | 0.242887 | 0.265628 |
| Phi | 0.261103 | **0.252813** |
| 2 | 0.374035 | 0.293438 |

On evaluation, Phi's paired mean loss exceeded `sqrt(2)` by `0.025745` and
`1.5` by `0.018216`; the latter difference had a 95% interval entirely above
zero `[0.001477, 0.029208]`. In holdout, Phi beat all fixed competitors by
mean, but that opposite selection is precisely the instability the frozen
split was designed to reveal.

The secondary concentration test also failed to replicate. The log-ratio MAD
fell from `0.330635` to `0.208667` in evaluation, but rose from `0.192709` to
`0.218047` in holdout.

## Whole-tree robustness

Using every sibling node inside each 32-step root, rather than only the
registered same-origin path, also showed a broad coarse-scale narrowing. Mean
within-root median Phi loss moved from `0.300652` at level 0 to `0.261103` at
level 4 in evaluation, and from `0.317796` to `0.252813` in holdout. The path
between those endpoints was non-monotone in both splits.

Because the coarsest level contains only one sibling pair, its whole-tree and
registered-path values coincide. This robustness check supports a general
scale effect but supplies no missing Phi specificity.

## What this means for the ARA thread

The user's observation that a longer chain can make a relation more visible
was productive. Compared with the earlier two-step temporal test, the dyadic
construction reveals how the ratio changes as child displacements are folded
into larger parents. It also shows why a short local cut can be misleading:
the inferred coordinate varies substantially with temporal scale and source
condition.

What the data do **not** support is the stronger claim that increasing temporal
distance reconstructs one Phi handover. The improvement toward Phi in the
evaluation split is better understood as part of a broader scale-dependent
narrowing because:

1. broken lineages show the same or stronger endpoint improvement;
2. the best direct target changes from calibration to evaluation to holdout;
3. the free target oscillates rather than converging monotonically; and
4. concentration fails to repeat in holdout.

This does not reject Vertical ARA as a same-lineage or cross-scale concept. It
rejects this specific Phi placement in 2D tracked bubble-centroid movement.

## Validation and reproducibility

An independent validator, without importing the analysis runner, recomputed:

- all fixed-target losses;
- all root endpoint changes and slopes;
- free targets at every split and level;
- coarsest paired target comparisons;
- three raw-trajectory spot checks directly from source CSVs; and
- the time-reversal whole-tree invariant.

It passed with zero numerical discrepancies. The reversal maximum absolute
error was exactly `0.0`.

Reproduction:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'analysis\vertical_ara_bubbles\work\run_vertical_ara_dyadic_chain.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'analysis\vertical_ara_bubbles\work\validate_vertical_ara_dyadic_chain.py'
```

Retained artifacts:

- `results/dyadic_chain_summary.json`
- `results/dyadic_chain_level_summary.csv`
- `results/dyadic_chain_root_levels.csv`
- `results/dyadic_chain_validation.json`
- `work/audit_dyadic_chain_feasibility.py`
- `work/run_vertical_ara_dyadic_chain.py`
- `work/validate_vertical_ara_dyadic_chain.py`
