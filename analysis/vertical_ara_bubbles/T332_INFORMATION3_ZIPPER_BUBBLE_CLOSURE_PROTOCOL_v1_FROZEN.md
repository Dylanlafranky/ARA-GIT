# T332 frozen protocol — Information³ zipper at bubble-merger closure

**Frozen:** 3 August 2026, after window-feasibility counts only and before any
T332 freedom, contraction, correlation, bootstrap or permutation result was
calculated  
**Source:** Pandey et al., Zenodo `10.5281/zenodo.15102957`  
**Event source:** the 91 T329 merger seams accepted before T332 was proposed  
**Status:** post-result mechanism probe in a previously used archive; not an
independent confirmation

## Question

ARA's Information³ zipper proposal says that two locally distinct relations
can close into one parent identity. At the new parent scale, their previously
free relation should be compressed. Any remaining irregularity should not be
assumed destroyed; it should remain coupled to a later observable.

T332 tests the part of that proposal that this archive can measure:

1. does directional freedom contract at an independently detected merger?;
2. is the contraction stronger than the inherited bubble's immediately prior
   ordinary turn?;
3. does the remaining post-merger freedom retain event-specific information
   about the pre-merger child relation?

The archive contains only three repeated primary merger lineages. It cannot
provide an inferential test of whether the residual reappears in the timing of
the *next merger seam*. That final zipper claim is recorded as unavailable,
not passed.

## Frozen population and feasibility

Reuse all 91 T329-eligible seams without adding, deleting or reweighting an
event using a T332 outcome:

- calibration `V01–V07`: 23;
- evaluation `V08–V28`: 52;
- holdout `V29–V35`: 16.

For every seam, the joining and inherited child each have the final incoming
step `f-1 -> f`, and the inherited parent has two resolved outgoing steps
`f+1 -> f+2 -> f+3`. Every one of those steps exceeds the already frozen
`0.0005 m` displacement floor. Thus all 91 events are eligible for the primary
contraction and residual tests.

The inherited child's preceding ordinary turn additionally requires frame
`f-2`. This leaves 20 calibration, 42 evaluation and 11 holdout events for the
event-specificity control.

## Frozen coordinates

Let `I` be the inherited child, `J` the joining child, and `P` the parent that
retains `I`'s released ID. Define

\[
\theta_I^- = \arg(I_f-I_{f-1}),\qquad
\theta_J^- = \arg(J_f-J_{f-1}),
\]

\[
\theta_P^1 = \arg(P_{f+2}-P_{f+1}),\qquad
\theta_P^2 = \arg(P_{f+3}-P_{f+2}).
\]

Use the origin-independent circular separation

\[
d_\pi(a,b)=
\frac{\left|\operatorname{atan2}(\sin(a-b),\cos(a-b))\right|}{\pi}
\in[0,1].
\]

The two primary freedom readings are

\[
F_{\rm child}=d_\pi(\theta_I^-,\theta_J^-),
\qquad
F_{\rm parent}=d_\pi(\theta_P^1,\theta_P^2).
\]

Both are the angular separation of exactly two observed vectors. The first is
inter-child directional disagreement immediately before closure; the second
is the new parent's directional change immediately after closure.

The frozen zipper contraction is

\[
Z=F_{\rm child}-F_{\rm parent}.
\]

Positive `Z` means that the post-merger parent is directionally less free than
the two-child relation was before merger.

For the ordinary-turn control, when `f-2` exists define

\[
\theta_I^{--}=\arg(I_{f-1}-I_{f-2}),\qquad
F_{\rm ordinary}=d_\pi(\theta_I^{--},\theta_I^-),
\]

\[
E=F_{\rm ordinary}-F_{\rm parent}.
\]

Positive `E` means that the post-merger parent is steadier than the same
lineage's immediately preceding non-merger turn.

## Frozen inference

Use 5,000 whole-video cluster bootstrap resamples with seed `20260803 + 332`.
Report means, medians and 95% percentile intervals for `Z` and `E` separately
in calibration, evaluation and holdout.

For immediate residual inheritance, calculate Spearman correlation between
`F_child` and `F_parent`. Compare the observed evaluation correlation with
5,000 within-video cyclic shifts of `F_parent`; these preserve each video's
marginal freedom distribution while breaking the actual child-parent seam.
Also report a whole-video bootstrap interval for the observed correlation.
Videos containing only one eligible seam cannot supply a non-zero cyclic
shift. Exclude those videos from both the observed and shuffled correlation
for Gate 3, while retaining them for Gates 1 and 2.

The holdout has only 16 events across three videos. It supplies directional
confirmation, not a strict independent replication.

## Frozen gates

### Gate 1 — local contraction

Evaluation mean `Z` must be positive with its 95% whole-video interval above
zero. Holdout mean `Z` must retain the positive sign.

### Gate 2 — event specificity

Evaluation mean `E` must be positive with its 95% whole-video interval above
zero. Holdout mean `E` must retain the positive sign.

### Gate 3 — immediate residual inheritance

Evaluation Spearman correlation must be positive, its whole-video interval
must lie above zero, and the within-video cyclic-shift one-sided probability
must be below `0.05`. Holdout correlation must retain the positive sign.

### Gate 4 — later ordered closure

No pass/fail verdict is permitted. Three repeated merger lineages are too few
for inference about later seam timing or spacing.

## Controls and boundaries

1. **Immediately prior ordinary turn:** tests whether any apparent tightening
   is specific to closure rather than ordinary persistence.
2. **Within-video cyclic residual shuffle:** tests whether pre/post residual
   ranking belongs to the actual seam rather than the archive's marginals.
3. **Reversed ordering:** `d_pi` is deliberately magnitude-only and therefore
   invariant to exchanging its two arguments. Reversal is recorded as
   mathematically non-discriminating; no directional claim is smuggled into
   this test.
4. **No Phi target:** T332 does not score Phi, 3/8, `1/e`, a rational grid or
   any other fixed constant.
5. **No causality claim:** a merger-aligned contraction is descriptive unless
   it also passes the event-specificity control. Even then, the archive does
   not isolate a unique physical cause.
6. **Different observable roles:** `F_child` is inter-child disagreement and
   `F_parent` is intra-parent turning. They share units and two-vector grain,
   but the interpretation must retain this difference.

## Verdict language

- If Gate 1 fails: **not supported — local zipper contraction**.
- If Gate 1 passes but Gate 2 fails: **contraction observed, event specificity
  not supported**.
- If Gates 1 and 2 pass but Gate 3 fails: **closure contraction supported;
  immediate residual inheritance not supported**.
- If Gates 1–3 pass: **closure contraction and immediate residual inheritance
  supported in this archive**.
- Under every outcome: **the full Information³ zipper, including later ordered
  closure, remains unconfirmed** because Gate 4 is unavailable.
