# Q59 Cross-Rung Pentagonal Twist Protocol v1 — Frozen

**Frozen:** 1 August 2026, Australia/Brisbane, before Q59 angular target calculation.

## Question

Q58 found that parent/child connected-correlation magnitude is a curved
function of local ARA position rather than one constant Phi multiplier. Q59
tests the directional version of Dylan's follow-up geometry:

> Each spherical slice remains circular, while the cross-rung edge twists
> around the parent as a pentagonal screw.

At the same local ARA coordinate, does the Q42 parent-cadence correlation
direction differ from the child-cadence direction by either one pentagon edge
step,

\[
T_1=72^\circ,
\]

or the same-phase pentagon diagonal,

\[
T_2=144^\circ?
\]

The greedy archive is calibration-only: it may choose between `72°` and
`144°` and establish the handedness convention. The Landmax archive remains
the untouched replication archive.

## Sources and fixed tier identities

Reuse the two local public-data caches already verified for Q42 and Q58:

- calibration archive:
  `q40_return_flow_inhomo_v1_greedy/q40_derived_cache.npz` and
  `q40_connected_cache.npy`;
- untouched replication archive:
  `q41b_cadence_strand_inhomo_v1_landmax/q41b_derived_cache.npz` and
  `q41b_connected_cache.npy`;
- source DOI: `10.5281/zenodo.16753415`;
- branch: `c2_2local connectivity`;
- 100 seeds, 66 pair identities and 500 samples per archive.

The tier and phase definitions stay fixed:

- child: Q42 `two_turn_7_5` cadence family;
- parent: Q42 `one_turn_15` cadence family;
- Phase A: Q42 qualifying positive/increasing half-wave;
- Phase B: the immediately following qualifying negative/decreasing
  half-wave.

This remains a seed-balanced population-level cross-tier comparison. It does
not assert individual parent/child genealogy between different pair
identities.

## Fixed local ARA coordinates

Use development samples `0..249` and the already frozen Q42 coordinate

\[
h(t)=\sqrt[3]{|\det C(t)|},
\qquad
x(t)=2\frac{h(t)-h_{05}}{h_{95}-h_{05}}.
\]

Evaluate the complete fixed interior grid

\[
\boxed{x\in\{0.2,0.4,0.6,0.8,1.0,1.2,1.4,1.6,1.8\}}.
\]

Use the same Q42/Q58 cycle eligibility, family classification, monotone-run
interpolation and no-extrapolation rules. Interpolate every element of the
unnormalised connected-correlation matrix `C` at every crossed grid point.

## Directional coordinate

For two nonzero matrices at the same seed, phase and local coordinate, define
the full Frobenius angle

\[
\alpha(C_P,C_C)
=
\cos^{-1}\!\left(
\frac{\langle C_P,C_C\rangle_F}
     {\lVert C_P\rVert_F\lVert C_C\rVert_F}
\right)
\in[0^\circ,180^\circ].
\]

This is the primary directional measure. Multiplying either matrix by a
positive scalar changes its magnitude but not this angle. Applying the same
orthogonal basis change to both matrices also leaves the angle unchanged.

The source matrices are Bell-diagonal: off-diagonal entries are exactly zero
and `Cxx=Cyy` in the source caches. The signed secondary coordinate therefore
uses the fixed Frobenius-preserving plane

\[
u=\frac{C_{xx}+C_{yy}}{\sqrt2},
\qquad
v=C_{zz},
\]

and the directed child-to-parent angle

\[
\delta
=
\operatorname{atan2}
\left(u_Cv_P-v_Cu_P,\;u_Cu_P+v_Cv_P\right)
\in(-180^\circ,180^\circ].
\]

The unsigned primary is not allowed to inherit a sign or singular-vector
orientation chosen to favour a target.

## Frozen aggregation

For each archive, seed, pair, cadence family, phase and grid coordinate:

1. take the elementwise median interpolated matrix across eligible cycles;
2. take the elementwise median across pairs within the same archive, seed,
   family, phase and coordinate, giving pair identities equal weight;
3. retain only cells with both fixed cadence families and nonzero matrix
   norms; and
4. calculate the same-phase parent/child angles `A→A` and `B→B`.

Also calculate wrong-phase controls `parent A → child B` and
`parent B → child A` at the same coordinate. Archive/grid summaries are the
median across matched seed angles. Uncertainty uses seed-cluster bootstrap.

## Calibration lock

Only the greedy archive may choose the pentagonal route. From the 18 greedy
archive cell medians (two phases by nine coordinates), choose

\[
T\in\{72^\circ,144^\circ\}
\]

by the smaller mean absolute unsigned angular error. A tie selects `72°`.

After `T` is selected, compare four signed screw models on the same 18 greedy
cell medians:

- co-rotating positive: `(A,B)=(+T,+T)`;
- co-rotating negative: `(A,B)=(-T,-T)`;
- counter-rotating A-positive: `(A,B)=(+T,-T)`;
- counter-rotating B-positive: `(A,B)=(-T,+T)`.

Choose the model with the smallest mean circular absolute error, resolving
ties in the listed order. Save and hash this calibration lock before loading
or scoring the Landmax archive. No Landmax result may alter `T`, handedness,
tolerance or support gates.

## Named controls and tolerance

Compare the replicated angles with this fixed landmark set:

\[
0^\circ,60^\circ,72^\circ,90^\circ,108^\circ,120^\circ,
137.507764^\circ,144^\circ,180^\circ.
\]

These represent identical, hexagonal edge, pentagonal edge, perpendicular,
pentagon interior, hexagonal diagonal, golden angle, pentagon diagonal and
inverted directions respectively.

The frozen pentagonal equivalence band is

\[
\boxed{|\alpha-T|\leq8^\circ}.
\]

## Untouched replication gate

The pentagonal cross-rung twist receives **strict support** only if all of the
following hold on Landmax:

1. each phase has at least seven of nine fixed coordinate medians inside
   `T ± 8°`;
2. each phase has mean absolute unsigned error at most `8°`;
3. `T` is the nearest named landmark to each phase's whole-grid median;
4. the locked signed screw model has combined 18-cell mean circular error at
   most `10°`, with at least 14 of 18 cells within `10°`;
5. greedy-versus-Landmax mean absolute difference of unsigned cell medians is
   at most `10°` in each phase;
6. same-phase combined unsigned error is smaller than wrong-phase combined
   error; and
7. a 1,999-draw family-label permutation null gives a one-sided
   no-worse-than-null probability at most `0.01` for Landmax's combined
   unsigned target error.

Report every component even when the strict conjunction fails. Do not rescue
a failure by changing targets, using one favourable phase/coordinate, taking
an absolute signed angle after inspection, or fitting a smooth curve.

## Uncertainty, null and robustness

- Use 10,000 seed-cluster bootstrap draws for every archive/phase/grid median
  and whole-grid phase median.
- For the family-label null, permute fixed parent/child labels across
  pair-level profiles within each Landmax seed while preserving family
  counts. Recompute the complete seed and archive aggregation.
- Report the angle between elementwise-median matrices as the primary.
- Registered robustness: compute seed angles after using elementwise means
  across cycles and pairs. This robustness result cannot replace the primary.
- Report the effective two-coordinate equality (`Cxx=Cyy`), off-diagonal
  maximum, seed counts, lineage counts, crossing counts, missing cells,
  minimum norms and interpolation checks.

## Data gate

The test is valid only if:

- raw `closure` and `connected` caches are present for both archives;
- Q42 eligibility and cadence classification reproduce;
- source off-diagonal magnitude is at most `1e-12` and
  `max|Cxx-Cyy| ≤ 1e-12`;
- at least 50 matched seeds remain per archive/phase/grid cell; and
- all compared matrix norms are finite and greater than `1e-12`.

If these conditions fail, record `NOT TESTABLE ON Q42` rather than replacing
the directional coordinate post hoc.

## Required artifacts and validation

- Hash this protocol before angular target calculation.
- Save and hash the greedy calibration lock before Landmax scoring.
- Independently recompute sampled interpolations, angles, summaries,
  bootstrap intervals, null statistics and all gates.
- Save crossing-level, pair-level, seed-level and grid-summary records.
- Produce a static figure with the two phase curves, target and all named
  controls, plus a signed-handness panel and target-error comparison.
- Inspect the rendered figure before interpretation.

## Claim boundary

A pass would support a pentagon-angle population relation between the already
identified Q42 cadence families at matched local ARA coordinates in these two
public simulator archives. It would not establish literal pentagonal spatial
edges, individual lineage genealogy, universal Phi geometry, an energy law or
a new quantum law. A fail rejects this exact connected-correlation directional
translation without rejecting every possible geometric cross-rung handover.
