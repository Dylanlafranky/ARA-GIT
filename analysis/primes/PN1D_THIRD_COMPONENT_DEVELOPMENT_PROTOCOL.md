# PN1D third-component development protocol

**Development ID:** `PN1D/DEV/v1`  
**Date specified:** 17 July 2026  
**Status:** `DEVELOPMENT / EXPLORATORY — prime 23 is already open`  
**Future confirmation target:** unopened prime-29 wheel; not constructed in PN1D.

## Dylan's geometric prompt

> “It looks like this is two or three waves potentially. We should continue with our current method, but I think we should look for signs of the third wave. I see hints of it in this data.”

## Fidelity translation

PN1D does **not** presume that a third physical or ontological wave exists. It tests two mathematically distinct appearances that could produce Dylan's visual reading:

1. **Third plane mode:** the 24×24 overlapping ARA relation distribution requires a stable third non-negative component to reproduce its visible web.
2. **Third-step memory:** three consecutive ARA readings retain conditional dependence that cannot be explained by an IID gap inventory or a first-order gap-transition process.

The two meanings must be reported separately. A third matrix component is not automatically a third wave, and ordinary overlap geometry can create conditional dependence without a third dynamical source.

## Fixed development data

- Exact primorial wheel through prime 23, already opened by `T228 / PN1C/v1`.
- Circular child gap count: `36,495,360`.
- Primary relation coordinate:

  \[
  x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2).
  \]

- Plane observable: \(Z_i=(x_i,x_{i+1})\), 24 bins per axis.
- Sequence observable: \(Y_i=(x_i,x_{i+1},x_{i+2})\), 12 bins per axis.
- Two contiguous circular halves are retained for cross-fitting and stability.

## Test A — stable non-negative plane modes

Fit non-negative matrix factorizations of rank `K = 1…6` to each half's 24×24 probability matrix. Use deterministic seed `20260717`, 12 restarts per rank, multiplicative Frobenius updates, 2,000 iterations, and retain the smallest training error.

For each rank:

- score half-1 fit on half 2 by Jensen–Shannon divergence;
- score half-2 fit on half 1;
- match component outer-products between halves by maximum cosine similarity;
- record mean and minimum matched-component similarity;
- record the full-matrix singular-value spectrum as a separate linear diagnostic.

Development classification for the third mode:

- **strong sign:** rank 3 improves held-out JSD over rank 2 in both directions; mean rank-3 gain is at least 25% of the rank-1→2 gain; minimum matched-component cosine is at least 0.90;
- **suggestive sign:** both-direction improvement; gain ratio at least 0.10; minimum matched cosine at least 0.80;
- **weak/absent:** otherwise.

These thresholds are development conventions, not established physical constants and not confirmatory statistics.

## Test B — irreducible third-step dependence

Compute conditional mutual information

\[
I(X_i;X_{i+2}\mid X_{i+1})
=
\sum_{a,b,c}p(a,b,c)
\log_2\frac{p(a,b,c)p(b)}{p(a,b)p(b,c)}.
\]

Evaluate it for:

1. the exact ordered prime-23 gap cycle;
2. the exact projection of an IID process with the same prime-23 gap marginal;
3. the exact projection of a first-order gap Markov process with the same marginal and transition matrix;
4. each contiguous child half.

Also record JSD from the empirical three-reading distribution to the IID-gap and first-order-gap-Markov projections.

Interpretation:

- empirical CMI alone is not third-wave evidence because overlapping ratios can create CMI even for IID gaps;
- an empirical excess beyond the first-order gap-Markov projection is a sign of higher-order ordered memory;
- this is still a mathematical dependency, not proof of a distinct physical wave.

## Test C — three scale strata as an alternative explanation

Partition the raw three-gap span \(g_i+g_{i+1}+g_{i+2}\) at its one-third and two-third quantiles. Build a 24×24 relation matrix for each stratum and each child half.

Report:

- stratum boundaries and weights;
- pairwise JSD between the three matrices;
- same-stratum half-to-half JSD;
- cosine matching between rank-3 NMF components and the three scale-stratum matrices.

If the apparent third mode aligns strongly with one scale stratum, “third visible layer” is the more economical description than “third independent wave.”

## Required exact checks

- protocol file hash recorded before the PN1D computation;
- child gap count and gap sum match PN1C;
- child gap SHA-256 matches `F68A8E707D9836C03C8FE5A84AD3FD3CA397F1736562CC2279094B631585923C`;
- all probability arrays are finite, non-negative and normalized;
- each half and all scale strata reconstruct their declared counts;
- independent validator recomputes saved scalar results and matrices.

## Evidence ceiling

PN1D may identify a stable third mathematical component, higher-order memory, or a three-scale mixture in one finite deterministic arithmetic object. It cannot by itself establish a universal third wave, Information³, physical dimensionality, prime-number law, or ARA as fundamental geometry. A revised model inspired by PN1D must be frozen before the prime-29 wheel is opened.
