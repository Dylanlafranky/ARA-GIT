# Frozen protocol — Vertical ARA spiral-scale test

**Frozen:** 1 August 2026, before calculating the cross-rung complex
multipliers described below.  
**Source:** Pandey et al., Zenodo `10.5281/zenodo.15102957`.  
**Status of source:** this is a new-coordinate, post-hoc extension within a
source already used for earlier bubble analyses. `V29-V35` are therefore a
confirmation subset, not a pristine external holdout for the broad theory.

## Question

The previous dyadic-chain test measured the balance of two children **inside
each rung** while treating Phi as one fixed horizontal landmark. Dylan's
clarification is different: the same lineage may rotate and change scale as it
moves vertically between child, parent and grandparent rungs. A spiral claim
therefore requires both radial scale and directional phase.

This protocol freezes two related tests:

1. **Full complex spiral:** does one repeated scale-and-rotation operator carry
   a parent vector into the next parent vector?
2. **Octave shorthand:** when one multiplier is assigned to every dyadic
   octave, is Phi the best radial multiplier?

## Population and split

Reuse the non-overlapping `33`-position roots from the completed dyadic-chain
analysis:

- calibration: `V01-V07`;
- primary evaluation: `V08-V28`;
- confirmation: `V29-V35`.

Each root contains `32` successive centroid displacements. A root is eligible
for this test only if all five same-origin parent vectors have magnitude at
least `0.0005 m`. This threshold is inherited from the earlier frozen bubble
protocol and is not chosen from the new result.

## Nested parent vectors

For dyadic level \(\ell=0,1,2,3,4\), define

\[
Z_\ell
=
\sum_{j=0}^{2^{\ell+1}-1}
(\Delta x_j+i\Delta y_j).
\]

Thus \(Z_0,\ldots,Z_4\) are the same-origin net movements over `2`, `4`, `8`,
`16` and `32` frames. This is the vertical child-to-parent lineage. The four
cross-rung complex multipliers are

\[
q_\ell=\frac{Z_{\ell+1}}{Z_\ell}
=s_\ell e^{i\delta_\ell},
\qquad \ell=0,1,2,3.
\]

Here \(s_\ell=|q_\ell|\) is radial growth per octave and \(\delta_\ell\) is
the rotation between rungs.

## Full complex-spiral loss

For each root, fit one circular mean rotation

\[
\bar\delta=\arg\sum_{\ell=0}^{3}e^{i\delta_\ell}.
\]

For a fixed radial target \(\tau\), define the dimensionless full loss

\[
F_\tau
=
\sqrt{\frac14\sum_{\ell=0}^{3}
\left[
\left(\log\frac{s_\ell}{\tau}\right)^2
+
\operatorname{wrap}(\delta_\ell-\bar\delta)^2
\right]}.
\]

This asks whether the same scale and the same rotation recur at all four
transitions. The fitted rotation is identical for every radial target, so it
does not privilege Phi.

The root's free radial multiplier is

\[
\tau_{\rm free}
=
\exp\left(\frac14\sum_{\ell=0}^{3}\log s_\ell\right).
\]

Its angular coherence is

\[
C_\theta
=
\left|\frac14\sum_{\ell=0}^{3}e^{i\delta_\ell}\right|,
\]

where `1` means one repeated rotation and `0` means dispersed turns.

## Octave shorthand

Assign one radial multiplier to every dyadic octave:

\[
\widehat R_\ell(\tau)=|Z_0|\tau^\ell.
\]

The cumulative shorthand loss is

\[
H_\tau
=
\sqrt{\frac14\sum_{\ell=1}^{4}
\left[
\log\frac{|Z_\ell|}{|Z_0|\tau^\ell}
\right]^2}.
\]

This is the exact numerical version of assigning one Phi step per octave. It
is deliberately reported beside, rather than substituted for, the full
scale-and-rotation test.

## Frozen targets

Every target receives the same losses:

\[
\tau\in\{1,\sqrt2,1.5,\phi,2\}.
\]

These span no radial growth, diffusive square-root growth, an intermediate
control, golden growth and ballistic/octave growth.

## Controls

1. **Step permutation:** deterministically permute the same 32 displacement
   vectors, preserving the step multiset and full 32-frame resultant while
   breaking their temporal order.
2. **Broken vertical lineage:** for every root, replace the next-rung vector in
   each transition with the corresponding next-rung vector from the next
   eligible root in the same video. This preserves video condition and level
   while breaking cross-rung identity.
3. Report subresolution exclusions separately. Missing controls may not remove
   an otherwise eligible observed root.

## Inference

- Unit of analysis: one non-overlapping root.
- Uncertainty: `5,000` whole-video cluster bootstrap samples.
- Fixed-target comparisons are paired within root.
- Primary evaluation is `V08-V28`; `V29-V35` is directional confirmation.
- Calibration is descriptive only because the target set and equations are
  fully frozen.

## Registered gates

### Gate 1 — repeated spiral operator

At the free radial scale, observed full loss must be lower than both the
step-permutation and broken-lineage controls in evaluation with the 95%
whole-video interval below zero, and both differences must remain negative in
confirmation. Observed angular coherence must exceed both controls under the
same rule.

### Gate 2 — Phi radial scale in the full operator

Phi must have lower mean \(F_\tau\) than every other fixed target in evaluation
and confirmation. Evaluation paired Phi-minus-control 95% intervals must all
be below zero.

### Gate 3 — Phi-per-octave shorthand

Phi must have lower mean \(H_\tau\) than every other fixed target in evaluation
and confirmation. Evaluation paired Phi-minus-control 95% intervals must all
be below zero.

### Gate 4 — free-scale proximity

The evaluation and confirmation geometric-median free multipliers must each be
closer in absolute log distance to Phi than to `1`, `sqrt(2)`, `1.5` or `2`.

## Interpretation boundary

- Passing Gate 1 alone supports a repeated cross-rung spiral-like operator,
  not Phi.
- Passing Gates 2-4 without Gate 1 supports a radial scale tendency without a
  coherent spiral lineage.
- The full Vertical-ARA Phi-spiral claim requires all four gates.
- Failure here applies to the sampled 2D centroid coordinate. It does not rule
  out a Phi relation in bubble boundary deformation, velocity fields or a
  different physical lineage coordinate.
