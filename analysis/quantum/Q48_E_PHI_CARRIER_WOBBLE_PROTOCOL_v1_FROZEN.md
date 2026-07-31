# Q48 — \(1/e \leftrightarrow (2-\phi)\) carrier-wobble protocol v1

> **CONSTRUCT INVALID FOR THE INTENDED CLAIM — 30 July 2026.**
> Context compacted before execution and the test was run without renewed
> fidelity confirmation. This protocol measured the complete circle's
> **internal parent-to-parent turning amount**. Dylan intended the
> **external/meta vector carrying the entire rotating circle forward through
> time**. Retain this as a proxy-method artifact only. Its result is not
> evidence for or against the intended ARA time-vector claim.

**Frozen:** 30 July 2026, before the Q39 development-half parent cycles were
extracted or scored  
**Pre-run correction:** the first draft said “cyclically rotate” in G3.
That preserves nearly all local temporal ordering and is therefore not a
valid order-destroying null. Before any Q48 result was calculated, G3 was
corrected to independently permute each lineage's event order.  
**Ledger:** T308  
**Status:** retrospective, ARA-native test on an already opened deterministic
quantum simulator  
**Originating proposal:** Dylan La Franchi

## Question

Does the larger movement of the complete ARA⁹ connected identity behave as an
ordered wave inside the narrow carrier interval

\[
\boxed{
L=\frac1e
\quad\longleftrightarrow\quad
R=2-\phi=\phi^{-2}
}
\]

with \(3/8\) acting as the interval's near-ridge triangulation landmark?

This is distinct from:

- the internal `7.5 / 15` child/parent cadence;
- the rejected Q47 claim that every complete parent cycle advances by a
  fixed Phi-sized step;
- merely noticing that one three-of-four quadrant reversal averages to
  approximately `3/8`.

The proposed object is the **ordered parent-movement coordinate itself**.
If it is a wave between the two neighboring landmarks, consecutive
parent-to-parent movement readings must traverse the interval in time. A
single isolated reading inside the interval is not a wobble.

## ARA coordinate

The source movement observable is inherited unchanged from Q47. For complete
parent cycle \(r\) and its four ordered internal quadrant anchors,

\[
\delta_{r,q}
=
\frac{1}{2\pi}
\cos^{-1}
\left(
\left\langle U_{r,q},U_{r+1,q}\right\rangle_F
\right),
\]

where \(U_{r,q}\) is the normalized complete connected \(3\times3\) matrix at
quadrant \(q\). The equal parent reading is

\[
\bar\delta_r
=
\frac{\delta_{r,1}+\delta_{r,2}+\delta_{r,3}+\delta_{r,4}}4.
\]

This is a movement amount in full turns, not an absolute spatial angle.
Time order supplies the forward or return direction:

\[
\Delta\bar\delta_r=\bar\delta_{r+1}-\bar\delta_r.
\]

Inside the proposed carrier, remap without fitting:

\[
\boxed{
x_r
=
2\,
\frac{\bar\delta_r-L}{R-L}
}
\]

so \(L\mapsto0\), \(R\mapsto2\), and the exact local ridge is \(x=1\).

The proposed triangulation point satisfies

\[
x(3/8)
=
2\,
\frac{3/8-1/e}{(2-\phi)-1/e}
=1.010971271\ldots.
\]

Thus `3/8` is only `0.01097` local ARA units above the exact ridge. That
near-equality is an arithmetic property of the selected landmarks and earns
no empirical evidence by itself.

## Source and newly opened population

Reuse the public Q39 `pure_strongmax` deterministic simulator:

- DOI: `10.5281/zenodo.16753415`;
- connected matrices:
  `public_data/q39_information3_strongmax/q39_connected_cache.npy`;
- scalar closure and source metadata:
  `public_data/q39_information3_strongmax/q39_derived_cache.npz`;
- `100` seeds, `500` time slices, `66` observable pairs.

Q47 scored only complete cycles beginning in the evaluation half
(`t >= 250`). Q48 applies the already frozen Q39 coordinate and eligibility
rules to the complete available time range `t=0..498`, thereby exposing
development cycles that were not used in Q47's movement score.

No quantum-theory model, Fourier transform, smoother, fitted phase, or
external prime/sieve method may create the carrier.

## Cycle extraction

For every seed and observable pair:

1. use Q39's development-normalized closure coordinate \(u\) and change
   coordinate \(v\);
2. retain Q39's fixed circulation-coherence threshold `>= 0.80` and minimum
   quadrant occupancy `>= 0.05`;
3. extract non-overlapping runs through four consecutive ordered quadrants;
4. require at least two time slices in every quadrant;
5. compare consecutive complete parent cycles within the same
   `(seed, pair)` lineage.

The primary population includes every eligible adjacent-parent event.
Results are also split into development, evaluation-opening, and later
evaluation strata.

## Frozen carrier tests

### G0 — reproduction and geometry

- recover Q47's evaluation-only event count and maximum movement to
  `<= 1e-9`;
- recover all constants and \(x(3/8)\) to `<= 1e-12`;
- all movement readings remain in `[0,0.5]`;
- independently recalculate selected raw events.

G0 is an instrument gate and earns no evidence.

### G1 — carrier occupancy

The proposed interval must contain at least:

- `20` parent-movement events;
- `10` distinct lineages;
- `10` distinct seeds.

This is a minimal adequacy gate for calling the interval a recurring
carrier rather than an isolated seam.

### G2 — ordered traversal

A **carrier run** is a contiguous sequence of at least three consecutive
events from one lineage whose readings all lie in `[L,R]`.

A run is a **full half-traversal** if its local ARA readings reach both
`x <= 0.25` and `x >= 1.75`, crossing the ridge between them in temporal
order. G2 requires at least five full half-traversals across at least five
lineages, with both increasing and decreasing traversal directions present
in the pooled result.

### G3 — time order beats shuffled order

Within each lineage, independently permute the movement sequence `5,000`
times while preserving its marginal values and lineage size. The observed
number of full half-traversals must exceed the `99th` percentile of the
permuted null and must be at least five.

This distinguishes a wave path from a fortunate collection of carrier-like
values.

### G4 — \(3/8\) acts as the empirical ridge

Among carrier events:

- at least `20%` must lie within `0.10` local ARA units of \(x(3/8)\);
- the median local coordinate must lie within `0.20` of the exact ridge
  `x=1`.

This is not a test of the arithmetic fact that `3/8` is near the interval
midpoint. It asks whether measured movement actually uses that neighborhood.

## Verdict

- **Supported in this source:** G0 and all G1–G4 pass.
- **Mixed:** G0 passes and two or three of G1–G4 pass.
- **Not supported:** G0 passes and zero or one of G1–G4 pass.
- **Invalid:** G0 fails.

If G1 fails, the common carrier-wobble claim is not supported in this
source. The result may still leave a rarer seam-only hypothesis
underidentified; that narrower claim must not inherit support from one
post-hoc event.

## Fixed descriptive comparison

Independently of the verdict, classify events by the nearest ideal
four-strand reversal level:

\[
0,\quad\frac18,\quad\frac14,\quad\frac38,\quad\frac12.
\]

This checks the competing explanation that Q47's apparent `3/8` landmark is
a discrete three-of-four closure state rather than a continuously occupied
\(1/e\leftrightarrow(2-\phi)\) carrier.

## Claim boundary

A pass would support an ordered carrier-wave description in this
deterministic quantum simulator and this specific complete-lattice movement
coordinate. It would not prove universal Phi, a physical hidden quantum
medium, hardware behavior, or a universal time vector.

A failure would reject this representation of the carrier in this source.
It would not reject the exact \(1/e\), anti-Phi, and `3/8` arithmetic
relations, nor every possible ARA coordinate.
