# Frozen protocol — Vertical ARA long-chain dyadic reconstruction

**Frozen:** 1 August 2026, after a lineage-length feasibility count and before
calculating any dyadic ratio, Phi distance, target ranking, convergence slope,
or control result  
**Domain:** tracked quasi-two-dimensional fluidized-bed bubbles  
**Source:** Pandey et al., Zenodo `10.5281/zenodo.15102957`  
**Status at freeze:** proposed test; source schema, track continuity and the
number of eligible chains are known, but the registered outcomes are not

## Question

Does a longer uninterrupted observation of one bubble identity reveal a
same-lineage handover ratio that becomes progressively more Phi-like as raw
one-frame children are reconstructed into coarser temporal parents?

This is the empirical version of the earlier illustrative child-reconstruction
diagram. Phi is **not** inserted as a latent endpoint or correction constant.
The raw centroid trajectory alone generates every tested ratio.

## Feasibility information allowed before freezing

The source contains no uninterrupted 64-step track, so a 64-step parent cannot
be tested. It does contain the following non-overlapping 32-step roots:

| Split | Roots | Videos with roots |
|---|---:|---:|
| Calibration | 125 | 4 |
| Evaluation | 173 | 10 |
| Strict holdout | 40 | 4 |

All of these roots pass the previously registered `0.0005 m` child-displacement
resolution rule at at least half the nodes of every level. These are lineage
and resolution counts only; no target-specific quantity was inspected.

## Eligible chain and fixed split

An inference root is one tracker-assigned ID observed at 33 exactly consecutive
50-fps frames:

\[
P_0\to P_1\to\cdots\to P_{32}.
\]

Within each uninterrupted segment, roots start at the segment's first frame and
then every 32 frames. These non-overlapping roots are the inference population.
Every possible sliding 32-step root may be reported descriptively but cannot
change the verdict.

The existing source split is retained:

- **calibration:** `V01`–`V07`, amplitude `0.0`;
- **evaluation:** `V08`–`V28`, amplitudes `0.25`–`0.75`;
- **strict holdout:** `V29`–`V35`, amplitude `1.0`.

## Dyadic child-to-parent reconstruction

For temporal level \(\ell\in\{0,1,2,3,4\}\), one child spans
\(h_\ell=2^\ell\) frames. Along the registered nested path beginning at
\(P_0\), define the two child displacement vectors

\[
A_\ell=P_{h_\ell}-P_0,
\qquad
B_\ell=P_{2h_\ell}-P_{h_\ell}.
\]

The parent vector is

\[
V_{\ell+1}=A_\ell+B_\ell=P_{2h_\ell}-P_0.
\]

That vector identity is algebraically exact and is **not** evidence for ARA,
Phi or fractality. The empirical quantity is the independently measured
asymmetry between the two child magnitudes:

\[
r_\ell=
\frac{\max(\lVert A_\ell\rVert,\lVert B_\ell\rVert)}
     {\min(\lVert A_\ell\rVert,\lVert B_\ell\rVert)}
\ge 1.
\]

The five levels compare children spanning 1, 2, 4, 8 and 16 frames, closing
parents spanning 2, 4, 8, 16 and 32 frames. This is one nested same-origin path,
so every root contributes exactly one ratio per level. It avoids giving finer
levels extra weight merely because they contain more nodes.

Both children at a tested level must move at least `0.0005 m`. A root must have
all five registered nested-path ratios to enter the primary analysis.

## Direct target loss

For a fixed target \(\tau\), the direct scale-free loss is

\[
L_{\tau,\ell}=\left|\log\left(\frac{r_\ell}{\tau}\right)\right|.
\]

The fixed targets are

\[
1,\qquad \sqrt2,\qquad 1.5,\qquad \varphi,\qquad 2.
\]

At each level, the free target is the geometric median of the observed ratios,
equivalently

\[
\tau^*_{\ell}
=
\exp\!\left[\operatorname{median}(\log r_\ell)\right].
\]

Free targets are descriptive when calculated on evaluation or holdout. Only
calibration-derived free targets may be used as frozen competitors.

The golden self-similarity residual

\[
G_\ell=
\left|
\log\left(
\frac{(1+1/r_\ell)}{r_\ell}
\right)
\right|
\]

may be reported as a geometric crosswalk. Its minimum is algebraically Phi, so
it cannot count as independent Phi-placement evidence.

## Primary claims

### 1. Long-chain convergence

For each root, define the endpoint change

\[
\Delta_\varphi=L_{\varphi,4}-L_{\varphi,0}
\]

and the ordinary least-squares slope of \(L_{\varphi,\ell}\) against level
\(\ell=0,\ldots,4\).

The long-chain claim is supported only if:

1. mean \(\Delta_\varphi<0\) in evaluation with a video-cluster bootstrap
   95% interval wholly below zero;
2. the five-level slope is negative under the same evaluation criterion;
3. both effects repeat directionally in strict holdout; and
4. the real-lineage endpoint change is more negative than both registered
   temporal-order and broken-lineage controls in evaluation, with the same
   directional ordering in holdout.

The level-by-level mean need not be perfectly monotone, because the proposal is
a noisy fractal trajectory rather than a noiseless deterministic sequence.

### 2. Phi placement at the coarsest tested parent

At level 4, Phi must have lower mean direct loss than every fixed target in
evaluation and preserve that complete ranking in holdout. The free target and
median losses are reported to show whether a broad nearby optimum, rather than
Phi specifically, explains the result.

### 3. Concentration with scale

As a secondary claim, the across-root median absolute deviation of
\(\log(r_\ell/\varphi)\) should be smaller at level 4 than at level 0 in
evaluation and directionally repeat in holdout. This claim cannot rescue a
failed convergence or placement result.

## Registered controls

### Temporal-order control

For every root, deterministically permute its 32 one-frame displacement vectors
using a hash of video, track ID, start frame and the fixed seed `20260801`.
Reconstruct the five nested ratios from those permuted vectors. This preserves
the exact step-vector multiset and full 32-step resultant while destroying the
observed order and child adjacency.

### Broken-lineage control

Within each video and level, keep \(A_\ell\) from one root but replace
\(B_\ell\) with the corresponding \(B_\ell\) from the next eligible root in a
deterministic cyclic ordering. Videos with only one eligible root are excluded
from this control only. This preserves the level, source condition and child
magnitude distribution while breaking the sibling identity.

### Reversal invariant

Reversing a root in time must leave the **whole-tree multiset** of unordered
magnitude ratios unchanged at every level. The registered same-origin path
will instead begin at the other end of the chain and is not expected to match
node by node. This is a code and symmetry check, not a null model. Any
whole-tree multiset discrepancy is an implementation failure.

## Whole-tree robustness analysis

At each level, calculate every non-overlapping sibling ratio inside the
32-step root, not only the registered same-origin node. Reduce those ratios to
one within-root median loss per level. This whole-tree reading is secondary: it
tests whether the result belongs to the broader reconstructed sphere rather
than to the chosen nested path. It cannot rescue a failed primary path.

## Statistical decisions

- Use all non-overlapping roots for inference and all sliding roots only for
  descriptive shape checks.
- Resample whole source videos for 5,000 cluster-bootstrap draws.
- Report root counts, contributing videos, means, medians, free targets,
  endpoint changes, five-level slopes and 95% intervals.
- Use paired root-level differences for real-versus-permutation comparisons.
- For the broken-lineage comparison, use only roots whose videos contain at
  least two eligible roots.
- The strict holdout remains evaluable only with at least 20 complete roots
  across at least three videos.

## Interpretation gates

**Supports this long-chain Phi placement** only if both primary claims pass:
real same-lineage ratios move toward Phi with temporal scale and Phi is the best
fixed direct target at the coarsest tested level, with the registered controls
and strict holdout behaving as specified.

**Supports scale convergence but not Phi specificity** if distance to Phi falls
but another target is as good or better, the free optimum remains elsewhere,
or the controls converge similarly.

**Does not support this placement** if Phi distance fails to decrease, the
effect does not repeat in holdout, or a non-Phi target wins at level 4.

**Data-insufficient** applies if the post-resolution holdout falls below 20
complete roots or three source videos.

The test concerns one temporal placement of Phi in tracked bubble motion. It
does not by itself confirm or reject Vertical ARA, the full ARA framework, or
Phi in other cross-scale handovers.

## Known measurement boundary

The public files contain segmented contour centroids and tracker-assigned IDs,
not raw camera or pressure fields. A negative result can reject this
centroid-trajectory representation; it cannot exclude a finer handover erased
by sampling, segmentation or tracking.
