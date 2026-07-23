# PN38 — Child-Fill Resolution Sensitivity Protocol v1 (Frozen)

**Protocol date:** 2026-07-23 (Australia/Brisbane)  
**Status:** frozen before the resolution-sensitivity result  
**Source population:** the complete PN37 child field over `[4,000,000,000, 4,001,000,000)`

## Question

PN37 divided the native child ARA coordinate `[0,2]` into 160 equal bins. The resulting mean bin share of `0.625%` is compulsory because `1/160 = 0.00625`; it is not a discovered ARA landmark. This test asks whether the **departures from compulsory fill** retain a common shape when the same child field is measured at several resolutions.

## Frozen resolutions

Use exactly:

`80, 120, 160, 180, 320, 360` equal bins on `[0,2]`.

All divide a common 2,880-bin accumulator, so every reported histogram is an exact aggregation of one pass through the same child relations. No interpolation is used to construct the histograms.

## Native child coordinate

For every parent prime `p` and every lower prime gate `q <= sqrt(p)`:

\[
A_q(p)=2\frac{p\bmod q}{q}.
\]

The bin index at resolution `B` is:

\[
j_B(p,q)=\left\lfloor B\frac{p\bmod q}{q}\right\rfloor,
\qquad 0\le j_B<B.
\]

## Two baselines

### 1. Simple equal-fill baseline

Every bin has expected share `1/B`, hence expected occupancy on a second `0–2` ruler:

\[
\bar x_B=\frac{2}{B}.
\]

This value is imposed by the resolution and must not be interpreted as a discovered physical constant.

### 2. Exact gate-conditioned baseline

For each gate `q`, distribute its eligible-parent count uniformly over the valid nonzero residues `1,...,q-1`, map those residues through the same ARA bin rule, and sum the expected bin counts over gates. This retains the discrete geometry, the absence of residue zero, and the changing number of eligible parents at the largest gates.

The primary residual is:

\[
r_{B,j}=\frac{O_{B,j}-E_{B,j}}{E_{B,j}},
\]

where `O` is observed and `E` is the exact gate-conditioned expectation.

## Frozen diagnostics

For every resolution report:

1. compulsory mean share `1/B` and compulsory mean occupancy `2/B`;
2. observed occupancy range `2 O_j/N`;
3. total-variation distance from simple uniform fill;
4. total-variation distance from the exact gate-conditioned baseline;
5. RMS and maximum absolute gate-conditioned relative residual;
6. residual mirror correlation under `A -> 2-A` and the symmetric residual-energy share;
7. correlation of gate-conditioned residuals between the first and second consecutive halves of the parent-prime interval.

For cross-resolution shape comparison, repeat each bin residual across its exact subcells on the common 2,880-cell ruler and calculate the pairwise Pearson correlations. These comparisons are descriptive and are not independent tests because all resolutions use the same relations.

## Interpretation

- If only the mean changes as `2/B`, the earlier `0.625%` observation was purely a partition identity.
- A candidate nested or grandchild structure requires residual shape that is directionally stable across several resolutions **and** recurs across the two consecutive parent halves after subtracting the exact gate-conditioned baseline.
- Statistical detectability alone is insufficient because the child field contains hundreds of millions of relations. Effect size and cross-half stability control interpretation.
- This is a post-hoc structural sensitivity analysis, not a prime prediction test.

## Required checks

1. every resolution contains the same total observed child count;
2. every exact expected histogram sums to that total within floating tolerance;
3. aggregating the 2,880-bin accumulator reproduces every requested resolution exactly;
4. the two parent-half histograms sum exactly to the whole histogram;
5. the reported simple mean occupancy equals `2/B`.

