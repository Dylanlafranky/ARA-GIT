# Frozen protocol: Vertical ARA octave-to-Phi projection

**Frozen:** 1 August 2026, before calculation  
**Source:** Zenodo `10.5281/zenodo.15102957`  
**Status:** confirmatory reuse of the existing bubble archive, not a new external holdout

## Question

The preceding test found that accumulated centroid displacement grows at
approximately the octave factor `2` when the temporal span doubles. Dylan then
proposed that Phi may not replace that octave. Instead, Phi may be what a child
cut sees when the octave-sized parent anti-phase is directionally projected
into the child's available quadrant.

The exact frozen relation is

\[
2\cos 36^\circ=\phi.
\]

This test therefore keeps `2` as the parent octave and tests `36 degrees` as a
cross-rung projection angle. It does not fit Phi to the radial scale.

## Roots and rungs

Reuse the non-overlapping `33`-position roots and existing split assignments
from the dyadic bubble analysis. For each root and level
\(\ell\in\{0,1,2,3\}\), let

\[
n_\ell=2^{\ell+1},
\]

and form

\[
A_\ell=\sum_{j=0}^{n_\ell-1}\Delta z_j,
\qquad
B_\ell=\sum_{j=n_\ell}^{2n_\ell-1}\Delta z_j,
\qquad
P_\ell=A_\ell+B_\ell.
\]

`A` is the same-origin child, `B` its complementary child/anti-phase over the
next equal span, and `P` their doubled-span parent.

Exclude a root only when an observed `A`, `B` or `P` magnitude is below the
already frozen spatial-resolution threshold. Controls may be missing without
removing an otherwise eligible observed root.

## Primary coordinate

Measure the folded angle between the same-origin child and its parent:

\[
\theta_{A,\ell}
=
\arccos\left(
\frac{|A_\ell\cdot P_\ell|}{|A_\ell||P_\ell|}
\right),
\qquad 0\leq\theta_{A,\ell}\leq90^\circ.
\]

The equivalent ARA diameter projection is

\[
x_{A,\ell}=2\cos\theta_{A,\ell}.
\]

The Phi hypothesis predicts

\[
\theta_A=36^\circ
\quad\Longleftrightarrow\quad
x_A=\phi.
\]

The signed cosine is also retained. A negative sign distinguishes a `144
degree` anti-directional relation from a direct `36 degree` relation; folding
must not erase that diagnostic.

The complementary `B`-to-parent angle is reported as a symmetric secondary
coordinate. It cannot replace the frozen `A` primary result.

## Important algebraic boundary

The scalar remainder

\[
2-x_A
\]

equals `2-Phi` whenever `x_A=Phi`. It is an algebraic mirror of the same
projection, not independent confirmation. Likewise, `2-Phi = 0.381966...` and
`3/8 = 0.375` remain numerically distinct; this test may report their
difference but may not treat them as identical.

## Frozen angle targets

Every target receives the identical root loss

\[
L_t
=
\sqrt{\frac14\sum_{\ell=0}^{3}(\theta_{A,\ell}-t)^2}.
\]

Targets:

| Label | Angle | ARA projection `2 cos(angle)` |
|---|---:|---:|
| direct | 0 degrees | 2 |
| thirty | 30 degrees | sqrt(3) |
| Phi projection | 36 degrees | Phi |
| diagonal | 45 degrees | sqrt(2) |
| Phi complement | 54 degrees | `2 cos 54 degrees` |
| ridge-half | 60 degrees | 1 |
| perpendicular | 90 degrees | 0 |

The free root angle is the arithmetic mean of its four folded angles, which
minimizes the registered squared angular loss. Split summaries report the
median free root angle.

## Controls

1. **Phase-scrambled complement.** Preserve each observed `A` and the magnitude
   of its observed `B`, but rotate `B` by deterministic uniformly distributed
   angles. Average the loss over `64` frozen hash-seeded rotations per root.
   This preserves the vector-addition geometry that can itself pull `P=A+B`
   toward `A` while destroying the measured phase relationship.
2. **Broken complement.** Replace every `B` with the corresponding `B` from the
   next eligible root in the same video and level. This preserves level,
   condition and approximate scale while breaking the direct child pair.
3. **Complement symmetry.** Report the observed `B`-to-parent result separately
   to determine whether a Phi-scale angle is specific to the same-origin child
   or shared by both children.

## Inference

- Unit: one non-overlapping root.
- Uncertainty: `5,000` whole-video cluster bootstrap samples.
- Fixed-target comparisons are paired within root.
- Evaluation: `V08-V28`.
- Directional confirmation: `V29-V35`; it is not pristine because this archive
  has already informed earlier bubble tests.
- Calibration is descriptive only.

## Registered gates

### Gate 1: Phi target specificity

`36 degrees` must have lower mean `A` loss than every other fixed target in
evaluation and confirmation. Every evaluation paired Phi-minus-control 95%
whole-video interval must be below zero.

### Gate 2: real phase relation

Observed Phi loss must be lower than both phase-scrambled and broken-complement
Phi loss in evaluation, with both 95% intervals below zero. Both point
differences must remain negative in confirmation.

### Gate 3: cross-rung recurrence

At every one of the four levels, `36 degrees` must be the closest fixed target
to the evaluation mean folded angle and to the confirmation mean folded angle.

### Gate 4: free-angle proximity

The evaluation and confirmation median free root angles must each be closer to
`36 degrees` than to any other frozen target.

All four gates are required for support of the octave-to-Phi projection in this
coordinate.

## Interpretation boundary

- A failure rejects this specific centroid-direction projection; it does not
  reject every possible boundary, circumference or phase-handover coordinate.
- A win against fixed targets without control wins is geometric proximity, not
  evidence of a preserved physical handover.
- Because `P=A+B`, a small child-parent angle can arise from vector addition
  alone. The phase-scramble control is therefore decisive.

