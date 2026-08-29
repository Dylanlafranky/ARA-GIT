# T402 — Whole-shape child relation test

**Frozen before execution:** 2026-08-17  
**Status at freeze:** protocol only; no T402 result had been calculated or viewed.

## Question

T401 rejected the narrow claim that the local child bin centred at 1.375 is a stable missing state. Its full-distribution plots nevertheless showed a broader shape: a lower child crest, a ridge-region handover, and an upper return. T402 tests that complete relation rather than another isolated bin.

The test asks whether the shape is:

1. stable across fresh deterministic calibration/holdout partitions;
2. genuinely two-sided rather than one skewed lobe;
3. specific to beam-coincident C records rather than shared timing/background structure;
4. approximately reflected across the local ARA ridge; and
5. robust to bin count, KDE bandwidth, and phase-shift controls.

## Who / What / When / Where / Why / How

- **Who:** the same COHERENT 2022 CsI delayed-child identity used in T400–T401, with beam-coincident C records and anti-coincident AC control records kept separate.
- **What:** the whole weighted child distribution and the source-specific difference \(d(x)=p_C(x)-p_{AC}(x)\). The primary features are the lower crest, ridge/saddle, upper return, and the sign change of \(d\).
- **When:** every partition fits its population cut from calibration-only records, freezes the cut, and applies it unchanged to untouched holdout events. Fresh salts 600–999 are used.
- **Where:** the existing local child ARA coordinate \(x_C\in[0,2]\) between calibration-only branch equality \(L\) and delayed-rate return \(R\). No medium, physical identity, or rung is changed.
- **Why:** the old winner gap was an `argmax` artifact, but that does not decide whether the broader two-sided relation is real. T402 separates the whole shape from that failed narrow interpretation.
- **How:** complete C and AC distributions over 400 fresh partitions, split-wise lobe contrasts, continuous KDE topology, static reflection tests, all reflected-pair permutations, cyclic source-alignment controls, and bin/bandwidth sensitivity.

## Identity and rung boundary

This remains a **local child-rung cut inside the delayed population window**. The parent population defines the interval boundaries. T402 does not reinterpret the interval as a new particle, a new medium, or a direct individual-neutrino tag.

The frozen primary eight-bin centres are

\[
0.125,\ 0.375,\ 0.625,\ 0.875,\ 1.125,\ 1.375,\ 1.625,\ 1.875.
\]

For the raw C shape:

- lower lobe: \(0.50\le x_C<1.00\);
- ridge/saddle: \(1.00\le x_C<1.50\);
- upper lobe: \(1.50\le x_C\le2.00\).

For the source-difference axis, all four bins below and all four bins above the ridge are retained. The outer bins are therefore not silently discarded when reflection is tested.

## Frozen sample and separation rule

- Split salts: 600–999 inclusive.
- Calibration fraction: 70% under the unchanged T400 content-bound hash rule.
- Holdout fraction: 30%.
- Each split fits only calibration records, freezes its child window and membership rule, then scores untouched holdout records.
- C and AC use the same fitted scoring denominator and the same local coordinate.
- Overlapping deterministic partitions are resampling stability probes, not independent experiments.

## Measurements

For split \(r\), source \(s\in\{C,AC\}\), and bin \(j\), let

\[
p_{r,s,j}=\frac{w_{r,s,j}}{\sum_k w_{r,s,k}},
\qquad
d_{r,j}=p_{r,C,j}-p_{r,AC,j}.
\]

### 1. Raw two-sided C shape

Define

\[
L_{r,C}=\overline p_{r,C,[0.5,1.0)}-\overline p_{r,C,[1.0,1.5)},
\]

\[
U_{r,C}=\overline p_{r,C,[1.5,2.0]}-\overline p_{r,C,[1.0,1.5)}.
\]

Both positive means the ridge/saddle lies below both flanking lobes. AC receives the same measurements.

### 2. Source-specific differential axis

The aggregate differential is

\[
\bar d_j=\operatorname{mean}_r d_{r,j}.
\]

The registered ARA-oriented pattern is positive C excess below the ridge and negative C-minus-AC excess above it. This is not assumed to prove physical anti-phase; it is the shape being tested.

### 3. Continuous topology

For each source and split, weighted Gaussian KDEs are calculated on \(0\le x_C\le2\). The mean source difference is evaluated at frozen bandwidths

\[
h\in\{0.10,0.15,0.20,0.25\}.
\]

For each bandwidth, record:

- the strongest positive crest;
- the strongest negative trough;
- the zero crossing nearest the ARA ridge.

### 4. Static mean-shape reflection

Let \(\bar d_L\) be the four-bin lower-half vector and \(\bar d_U\) the four-bin upper-half vector. Exact reflected opposition compares

\[
\bar d_L
\quad\text{with}\quad
-\operatorname{reverse}(\bar d_U).
\]

Cosine similarity is recorded. The exact reverse ordering is ranked against all \(4!=24\) assignments of upper bins to lower bins. This is a **static mean-shape** test. It is not the across-partition dynamic exchange test that failed in T401.

### 5. Alignment and sensitivity controls

- AC is circularly shifted by each of the eight bin offsets before recalculating the differential reflection error. The unshifted C/AC alignment is ranked against these controls.
- The broad sign/reflection pattern is repeated with 6, 8, 10, and 12 equal-width bins.
- Continuous crest, crossing, and trough locations are repeated at all four frozen KDE bandwidths.
- Resampling intervals quantify stability over overlapping partitions and are not reported as independent-experiment confidence intervals.

## Frozen gates

### G1 — raw whole shape

Pass if:

- mean \(L_C>0\) and its 95% split-resampling interval is above zero;
- mean \(U_C>0\) and its 95% split-resampling interval is above zero; and
- at least 60% of valid splits have each contrast positive.

### G2 — source-specific two-sided difference

Pass if:

- at least three of four aggregate lower-half bins have \(\bar d_j>0\);
- at least three of four aggregate upper-half bins have \(\bar d_j<0\);
- the split-wise mean lower difference is positive in at least 65% of valid splits; and
- the split-wise mean upper difference is negative in at least 65% of valid splits.

### G3 — continuous topology

Pass if at least three of four bandwidths jointly place:

- the strongest positive crest in \(0.40\le x_C\le1.00\);
- the zero crossing nearest the ridge in \(0.85\le x_C\le1.30\); and
- the strongest negative trough in \(1.35\le x_C\le2.00\).

### G4 — exact static reflection

Pass if:

- the primary eight-bin reflected cosine is at least 0.75;
- the exact reverse mapping ranks in the top 3 of 24 assignments; and
- reflected cosine is at least 0.65 for at least three of the four bin-count sensitivities.

### G5 — correct source alignment

For every cyclic AC shift, calculate the normalized reflection error

\[
E=\frac{\|\bar d_L+\operatorname{reverse}(\bar d_U)\|_2}{\|\bar d\|_2}.
\]

Pass if the unshifted source pairing ranks in the best two of eight shifts and the C lower-lobe-versus-saddle contrast exceeds AC in at least 70% of valid splits.

## Verdict ladder

1. **SOURCE-SPECIFIC TWO-SIDED CHILD RELATION WITH STATIC REFLECTION SUPPORTED** — G1 through G5 pass.
2. **SOURCE-SPECIFIC TWO-SIDED CHILD RELATION; EXACT ANTI-PHASE NOT IDENTIFIED** — G1 through G3 pass, but G4 or G5 fails.
3. **BINNED TWO-SIDED SOURCE RELATION; CONTINUOUS TOPOLOGY UNRESOLVED** — G1 and G2 pass, but G3 fails.
4. **COMMON TWO-SIDED SHAPE; SOURCE-SPECIFIC RELATION NOT IDENTIFIED** — G1 passes but G2 fails.
5. **NO STABLE WHOLE SHAPE** — G1 fails.

## Required outputs

- Per-split C and AC eight-bin distributions and lobe contrasts.
- Aggregate bin summaries and C-minus-AC differential.
- KDE topology at four bandwidths.
- Exact and alternative reflection mappings.
- Cyclic AC-alignment controls.
- Bin-count sensitivity table.
- Labelled static figure, portable technical HTML report, machine-readable results, and validator.

## Boundaries

- T402 tests a statistical whole-shape relation in the saved COHERENT records. It cannot directly show a neutrino being created in an individual muon decay.
- C and AC differ in source identity but also in acquisition context; subtraction does not automatically isolate one physical component.
- Closure forces each C-minus-AC differential distribution to sum to zero. Therefore a generic positive/negative split is not enough; location, topology, reflection ordering, source alignment, and robustness controls are all required.
- The broad shape was noticed in T401, so T402 is a registered follow-up rather than a fully independent discovery test.
