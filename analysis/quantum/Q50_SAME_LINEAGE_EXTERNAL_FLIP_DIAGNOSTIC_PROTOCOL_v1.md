# Q50 — Same-lineage external ARA flip diagnostic

**Date:** 30 July 2026  
**Status:** PREDECLARED POST-Q49 EXPLORATORY DIAGNOSTIC  
**Source status:** Opened by Q49; this cannot be confirmatory evidence.

**Post-run visual-QA amendment:** The original wording compared the crossing
bin with the combined four-flank mean. Visual inspection showed that this can
mislabel monotonic decay as a local pinch. The calculation retains that
original ratio, but the reported pinch verdict additionally requires the
crossing bin to be below the preceding and following means separately. This
tightening was made after the first run and is not a frozen success gate.

## Exact question

Q49 found that the external centreline of complete four-quadrant cycles was
enriched in the declared direction during development and in the exact
half-turn-opposite direction during evaluation.

Q50 asks:

> Does that reversal occur through time inside the same seed/pair lineages,
> or can it be explained by different lineages contributing to the two
> strata?

It also asks whether the observed window contains:

1. a directed `0 → 2` passage;
2. a later `2 → 0` return;
3. a movement pinch near the `1.0` directional ridge.

## Frozen source and grain

- Input: `Q49_EXTERNAL_TIME_VECTOR_EVENTS.csv.gz`
- One row: the central-difference external movement of one complete-cycle
  centre inside one `(seed, pair)` lineage.
- All finite movements are retained. Near-zero movement is not assigned an
  unweighted direction; it contributes proportionally little through the
  movement-weighted coordinate below.
- Primary estimator: algebraic circle centre.
- Sensitivity estimators: point centroid and extrema midpoint.

## Directional ARA coordinate

Let the centre of Q49's declared `1/e → Phi` heading arc define the unit
direction \(\hat{\mathbf e}\). For external displacement divided by that
event's mean fitted-circle radius, \(\mathbf d_i\), define:

\[
B_i =
\frac{\mathbf d_i\cdot\hat{\mathbf e}}
{\|\mathbf d_i\|},
\qquad
x_i=1-B_i.
\]

For an aggregate set \(G\), use the movement-weighted form:

\[
B_G =
\frac{\sum_{i\in G}\mathbf d_i\cdot\hat{\mathbf e}}
{\sum_{i\in G}\|\mathbf d_i\|},
\qquad
x_G=1-B_G.
\]

Interpretation:

- `x = 0`: all resolved movement follows the declared direction;
- `x = 1`: opposing axial movement cancels, or movement is perpendicular;
- `x = 2`: all resolved movement follows the exact half-turn opposite.

This is a new directional ARA cut across the two opposing external
orientations. It is not the local `1/e → Phi` coordinate inside the declared
arc.

## Same-lineage population

A lineage is `(seed, pair_index)`.

The primary fixed-lineage population contains only lineages with:

- at least three finite external events ending before slice `250`;
- at least three finite external events starting at or after slice `250`.

This same set of lineages is used for every time bin, preventing changing
lineage composition from creating the apparent reversal.

## Frozen summaries

### A. Paired lineage reversal

For every fixed lineage, calculate `x_development` and `x_evaluation`.

Record:

- fraction with `x_development < 1` and `x_evaluation > 1`;
- fraction with the opposite pattern;
- median paired change `x_evaluation - x_development`;
- seed-cluster bootstrap 95% interval for the mean paired change;
- movement-weighted circular heading separation between strata.

The half-turn interpretation is descriptively supported when the paired
change is positive, most sign-changing lineages go declared-to-opposite, and
the aggregate heading separation is nearer `0.5` turns than `0` or `0.25`.

### B. Ordered trajectory

Split slices `0–499` into twenty fixed 25-slice bins. Within each bin,
calculate the movement-weighted `x_ext` using only the fixed-lineage
population.

Record:

- every sustained crossing of `x = 1`;
- whether any sequence reaches `x ≤ 0.5`, later `x ≥ 1.5`, and later returns
  to `x ≤ 0.5`;
- the same checks after reversing the pole labels as a bookkeeping
  sensitivity;
- seed-cluster bootstrap intervals for each bin.

A complete `0 → 2 → 0` cycle requires the three ordered regions in that
order. Reaching only the first two is a one-way `0 → 2` passage in the
available observation window.

### C. Ridge-pinch diagnostic

Let the primary crossing bin be the first bin where the trajectory moves
from below `1` to above `1`.

Compare mean relative movement strength in that bin separately with the mean
of the two immediately preceding and the two immediately following available
bins.

A pinch requires the crossing bin to be lower than both the preceding and
following means; this prevents a monotonic relaxation from being mislabeled
as an isolated pinch. A local movement minimum is compatible with a
pinch/crossing. Its absence
does not erase a directional flip, but argues against a stalled singularity
interpretation for this observable.

### D. Robustness and controls

- Repeat A–C with circle, centroid and extrema centre definitions.
- Compare the fixed-lineage trajectory with the unrestricted population.
- Shuffle time bins within each lineage `5,000` times while retaining each
  lineage's movements. Compare the observed early-to-late change with this
  null.
- Report event, lineage and seed counts. No event-level independence claim
  is allowed.

## Interpretation boundary

Q50 can distinguish a within-lineage reversal from a population-composition
artefact and can reveal whether the recorded window contains a return.

It cannot:

- rescue the failed frozen Q49 gates;
- establish a physical quantum singularity;
- establish a universal `0 → 2 → 0` law;
- count as untouched replication.

Any rule learned here must be frozen and tested on a different archive.
