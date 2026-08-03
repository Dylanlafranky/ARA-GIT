# T335 frozen protocol — river/thalweg Irrationality Di-ARA

**Frozen:** 3 August 2026, before calculating any T335 endpoint, quadrant,
null or holdout result  
**Test ID:** `T335-RIVER-IRRATIONALITY-DI-ARA-v1`  
**Status:** confirmatory reuse of an already-open public river-flume archive  
**Source:** `source_bedrock_bends/Bed-topography.xlsx`, inherited from T327

## Question

Does the ordered downstream river geometry support the same typed Di-ARA
coordinate recovered in T333 and T334:

1. radial contraction versus expansion;
2. reverse versus forward turning;
3. the four mixed sectors `Ab`, `aB`, `Ba`, `bA`; and
4. reciprocal radial closure about the local `1.0` ridge?

The primary domain-level test uses all 41 source-defined elevation-rank paths.
Rank 1, the minimum-bed path, is the declared thalweg. Ranks 2 through 41 are
matched non-thalweg controls through the same 33 cross-sections.

This test does **not** target Phi, `1/e`, `3/8` or any other fixed constant.
It tests the Irrationality Di-ARA geometry, of which Phi is only one possible
typed landmark or route.

## Eligible source record

T327 established the following fixed extraction before T335:

- 33 bend cross-sections at angles `10,15,...,170` degrees;
- 41 measured bed positions per cross-section;
- stable within-section elevation ranks `1,...,41`;
- no exact-rank ambiguity requiring the T327 tie branch;
- rank 1 is the thalweg and ranks 2–41 are matched controls.

T335 reuses this extraction without smoothing, interpolation, Fourier
processing, fitted trajectories or target-dependent rotation.

## Native downstream complex relation

For elevation-rank path `r`, write its measured planform position at retained
section `k` as

\[
p_{r,k}=x_{r,k}+i y_{r,k}.
\]

The downstream displacement is

\[
v_{r,k}=p_{r,k+1}-p_{r,k}.
\]

For consecutive non-zero displacements, define the same-lineage quotient

\[
q_{r,k}=\frac{v_{r,k+1}}{v_{r,k}}
=s_{r,k}e^{i\delta_{r,k}},
\]

where

- `s=|q|` is the change in downstream step magnitude;
- `delta=arg(q)` in `(-pi,pi]` is the signed turn between the two steps.

This yields 31 quotient events per rank and `41 × 31 = 1,271` primary events.
The event is assigned to the middle source section shared by its two steps.

The planform cut is primary because the flume bend gives a physically declared
two-dimensional downstream path. Bed elevation remains in the rank definition
and is not mixed into the complex units after extraction.

## Exact ARA coordinates

No radial carrier is fitted. Consecutive steps at the same magnitude have
`s=1`, the natural same-rung ridge.

Map the positive scale ratio to the open ARA diameter by

\[
X=\frac{2s}{1+s}.
\]

Then

\[
s<1\Rightarrow X<1,
\qquad
s=1\Rightarrow X=1,
\qquad
s>1\Rightarrow X>1,
\]

and exact reciprocal inversion obeys

\[
X(1/s)=2-X(s).
\]

Map signed turning to the perpendicular ARA diameter by

\[
Y=1+\frac{\delta}{\pi}.
\]

Thus `delta<0` is below its ridge, `delta=0` is the no-turn ridge, and
`delta>0` is above its ridge. Values within `1e-12` of either ridge are
reported as boundaries and are not assigned by convenience.

The frozen sector labels are

\[
\begin{array}{c|c}
Ba & Ab\\
\hline
bA & aB
\end{array}
\]

or explicitly:

| Radial side | Turn side | Di-ARA sector |
|---|---|---|
| contraction (`X<1`) | forward (`Y>1`) | `Ba` |
| expansion (`X>1`) | forward (`Y>1`) | `Ab` |
| contraction (`X<1`) | reverse (`Y<1`) | `bA` |
| expansion (`X>1`) | reverse (`Y<1`) | `aB` |

Axis orientation and capitalization are relational labels for this declared
chart, not permanent properties of water or bed points.

## Frozen downstream splits

The 31 middle-section angles are `15,20,...,165` degrees.

- calibration: `15–60` degrees inclusive (`10` events per path);
- evaluation: `65–110` degrees inclusive (`10` events per path);
- untouched holdout: `115–165` degrees inclusive (`11` events per path).

The ARA transform and sector boundaries contain no fitted parameters.
Calibration may fit only the descriptive reciprocal amplitude below.

## Reciprocal endpoints

Within a declared population and split, define

\[
s_- = \operatorname{median}(s\mid s<1),
\qquad
s_+ = \operatorname{median}(s\mid s>1),
\]

and reciprocal product

\[
P=s_-s_+.
\]

The implied reciprocal amplitude is

\[
\widehat\alpha=
\exp\left[
\frac{
\operatorname{median}(\log s\mid s>1)
-\operatorname{median}(\log s\mid s<1)}{2}
\right].
\]

Fit `alpha_cal` from the pooled 41-path calibration field only. For any
candidate `alpha`, the endpoint loss is

\[
L(\alpha)=\frac12\left(
|\log s_-+\log\alpha|
+|\log s_+-\log\alpha|
\right).
\]

Lower is better. No fixed numerical constant competes in T335.

## Controls

### 1. Downstream step-order null

For each of 1,000 deterministic draws, independently permute the 32 observed
displacement vectors within every rank path, preserving each path's exact
step multiset and total resultant while breaking downstream adjacency.
Recalculate quotient events and evaluation/holdout losses to frozen
`alpha_cal`.

### 2. Reversed downstream direction

Reverse each path using `-v[::-1]`. Report the sector reflection and endpoint
loss. This is a directional audit, not an independent null and not a gate by
itself.

### 3. Broken rank lineage

For each split event, use the denominator step from rank `r` and the numerator
step from the next cyclic elevation rank:

\[
q^{\mathrm{broken}}_{r,k}
=\frac{v_{r+1,k+1}}{v_{r,k}},
\]

with rank 41 wrapping to rank 1. This preserves cross-section timing and the
rank population while breaking same-path child-to-parent continuity.

### 4. Matched non-thalweg paths

Score the rank-1 thalweg separately against the 40 downstream-ordered rank
controls. These ranks are controls from one river archive, not 40 independent
rivers.

## Registered gates

### G0 — integrity

Source/protocol hashes, source shape, position reconstruction, event counts,
split counts and saved calculations must pass an independent validator.

### G1 — field four-sector coordinate

All four sectors must occur in evaluation and holdout across the 41-path
field, and each must contain at least 5% of non-boundary events in each split.

### G2 — thalweg sector coverage

The thalweg must occupy all four sectors across its pooled 31 events and at
least three sectors separately in evaluation and holdout.

### G3 — reciprocal closure

For the pooled 41-path field, `P` must lie in `[0.90,1.10]` in evaluation and
holdout. For the small thalweg record, pooled `P` must lie in `[0.80,1.20]`
and split values must each lie in `[0.75,1.25]`.

### G4 — calibration transfer

The field's implied evaluation and holdout amplitudes must each be within 10%
log-relative distance of frozen `alpha_cal`.

### G5 — recorded downstream order

The observed pooled-field endpoint loss must beat at least 95% of the 1,000
step-order nulls in evaluation and holdout separately.

### G6 — intact rank lineage

Observed pooled-field endpoint loss must be lower than the broken-lineage loss
in evaluation and holdout.

### G7 — thalweg specificity

The thalweg endpoint loss must be below the median of the 40 control paths in
evaluation and holdout, and must rank in the best 10% (`rank <= 4/41`) in at
least one of the two untouched splits.

## Verdicts

- `G1` supports a usable river-field Di-ARA coordinate.
- `G1+G3+G4` supports a transferable reciprocal Irrationality Di-ARA radial
  organisation in the sampled field.
- `G1–G6` supports an ordered, same-lineage field mechanism rather than only
  a geometric classification.
- `G2+G3+G7` supports special thalweg expression.
- The full river/thalweg claim requires `G0–G7`.

Failure of order or lineage gates cannot be rescued by four occupied sectors
or reciprocal bookkeeping alone.

## Interpretation boundaries

1. The source archive was opened in T327, so T335 is confirmatory reuse, not a
   pristine discovery archive.
2. The quotient construction is ARA-native but reciprocal pairing can arise
   partly from stationary step-size variation; order and lineage controls are
   therefore load-bearing.
3. The flume's global bend can bias signed turning. Matched rank paths and
   sector shares must reveal that rather than silently rotating the axes.
4. Elevation rank tracks geometric features, not persistent water parcels.
5. Passing does not establish Phi, a universal constant, or the complete ARA
   ontology. Failing identifies where the typed Di-ARA does not transfer.
