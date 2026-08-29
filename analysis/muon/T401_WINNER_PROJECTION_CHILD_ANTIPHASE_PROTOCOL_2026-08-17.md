# T401 — Winner-projection test for the apparent child anti-phase band

**Frozen before execution:** 2026-08-17  
**Status at freeze:** protocol only; no T401 result had been calculated or viewed.

## Question

T400 plotted only the most populated local-ARA bin from each deterministic split. The resulting mode histogram had no winner in the interval (1.25\leq x<1.50), even though the primary split's full histogram contained weight there. T401 asks whether that missing-winner band is:

1. an occupied but non-dominant ridge/saddle hidden by winner-only projection;
2. a volatile handover region;
3. a reflected anti-phase branch; or
4. an ordinary consequence of sparse sampling, binning and `argmax` selection.

The test does **not** assume that an empty mode bin is an empty physical state.

## Who / What / When / Where / Why / How

- **Who:** the same COHERENT 2022 CsI delayed-child identity used in T400, evaluated separately for beam-coincident C events and anti-coincident AC control events.
- **What:** every split's complete weighted distribution on the child coordinate, rather than only its winning bin. Occupancy, dominance, volatility, continuous modes and mirrored-bin exchange are measured separately.
- **When:** each split derives its delayed-child interval from its calibration-only records. The expected interval is near T400's (0.569\text{–}1.383\,\mu s), but it is recalculated without holdout access.
- **Where:** the frozen local child coordinate
  \[
  x_C=2\frac{x_P-x_P(L)}{x_P(R)-x_P(L)}\in[0,2],
  \]
  with primary attention on (1.25\leq x_C<1.50) and the reflection (x_C\mapsto2-x_C).
- **Why:** to test the proposed survivor/winner-selection interpretation before assigning the unselected band to a hidden child Phase B.
- **How:** 200 deterministic calibration/holdout splits, complete C and AC bin distributions, weighted KDE modes, a sampling-only mode null, and a predeclared mirrored-pair comparison against all alternative pairings.

## Identity and rung boundary

This is a **local child-rung test** inside the delayed population window. It does not change medium or physical identity from T400. The parent coordinate defines the boundaries; the child coordinate expands only the interval between branch equality (L) and the delayed-rate return (R).

The eight fixed local bins have centres

\[
0.125,\ 0.375,\ 0.625,\ 0.875,\ 1.125,\ 1.375,\ 1.625,\ 1.875.
\]

The candidate band is the bin centred at (1.375). Its immediate neighbours are (1.125) and (1.625).

## Frozen sample and separation rule

- Split salts: 400–599 inclusive.
- Calibration fraction: 70% by the existing T400 content-bound hash rule.
- Holdout fraction: 30%.
- Each split fits only its calibration records, freezes its child window and event-membership rule, then scores its untouched holdout records.
- C and AC use the same frozen scoring denominator.
- Overlapping deterministic splits are **resampling stability probes**, not 200 independent experiments.

## Measurements

For source (s\in\{C,AC\}), split (r), and bin (j), let (w_{r,s,j}) be the summed delayed-membership weight and

\[
p_{r,s,j}=\frac{w_{r,s,j}}{\sum_k w_{r,s,k}}.
\]

### 1. Occupancy, dominance and volatility

- Occupancy: (O_{s,j}=\operatorname{mean}_r p_{r,s,j}).
- Dominance: (D_{s,j}=\Pr_r(j=\arg\max_k p_{r,s,k})).
- Volatility: (V_{s,j}=\operatorname{sd}_r(p_{r,s,j})/O_{s,j}).
- Candidate occupancy ratio:
  \[
  Q_O=\frac{O_{C,1.375}}{(O_{C,1.125}+O_{C,1.625})/2}.
  \]
- Candidate volatility ratio:
  \[
  Q_V=\frac{V_{C,1.375}}{\operatorname{median}_j V_{C,j}}.
  \]

The band is labelled **quiet** if (Q_V\leq0.80), **turbulent** if (Q_V\geq1.20), and **intermediate** otherwise. This label is descriptive and is not itself an anti-phase claim.

### 2. Continuous mode

For each split and source, a weighted Gaussian KDE is evaluated on (0\leq x_C\leq2) with frozen bandwidth (h=0.15). Its maximum is the continuous mode. This tests whether the apparent band survives removal of the eight-bin boundary.

### 3. Sampling-only winner null

The pooled C occupancy supplies multinomial bin probabilities. The median weighted effective sample size

\[
N_{eff}=\frac{(\sum_i w_i)^2}{\sum_i w_i^2}
\]

sets the frozen sampling size. Fifty thousand simulated 200-split experiments produce the probability of observing no candidate-band winner. This is a diagnostic null because the real splits overlap and event weights are not literal independent counts.

### 4. Reflected-pair exchange

To avoid closure-induced correlations from the constant-sum distribution, each split is first transformed with the centred log ratio (CLR). The predeclared reflection pairs are

\[
(0.125,1.875),\ (0.375,1.625),\ (0.625,1.375),\ (0.875,1.125).
\]

For each pair, Spearman correlation is calculated across splits. The reflection-exchange score is the mean negative correlation:

\[
E_{reflection}=\operatorname{mean}_{pairs}(-\rho).
\]

The exact reflected mapping is ranked against all (4!=24) lower-to-upper pairings. The same calculation is performed on AC. Total lower-half versus upper-half anticorrelation is excluded as evidence because normalization forces it.

## Frozen gates

### G1 — occupied but non-dominant

Pass if (Q_O\geq0.50) and candidate binned dominance (D_{C,1.375}\leq0.01).

### G2 — continuous missing-winner persistence

Pass if no more than 5% of C KDE modes fall in (1.25\leq x_C<1.50).

### G3 — beyond the sampling/argmax null

Pass if the simulated probability of zero candidate winners across 200 splits is below 0.05. Failure means sparse winner selection is sufficient to explain the visual gap.

### G4 — reflected exchange

Pass if:

- at least three of four reflected CLR correlations are negative;
- (E_{reflection}\geq0.20); and
- the exact reflection ranks in the top 3 of 24 mappings.

### G5 — signal exceeds the AC control

Pass if the C reflection score exceeds AC by at least 0.10 and the exact reflection mapping ranks better for C than for AC.

## Verdict ladder

1. **INDIRECT CHILD ANTI-PHASE SHADOW SUPPORTED** — G1 through G5 pass.
2. **STRUCTURED WINNER SHADOW; ANTI-PHASE NOT IDENTIFIED** — G1 through G3 pass, but G4 or G5 fails.
3. **OCCUPIED BAND; WINNER SELECTION EXPLAINS THE GAP** — G1 and G2 pass, but G3 fails.
4. **NO STABLE MISSING-WINNER BAND** — G1 or G2 fails.

## Required outputs

- Per-split C and AC bin distributions.
- Per-bin occupancy, dominance and volatility.
- Per-split binned and KDE modes.
- Mirrored-pair and all-permutation scores.
- Sampling-null mode frequencies.
- A labelled static figure and a portable technical HTML report.
- Machine-readable results plus a validator.

## Boundaries

- This test can detect a statistical projection shadow; it cannot directly label an individual event as a neutrino or hidden physical wave.
- Reflected exchange would be evidence for the proposed ARA relation, not proof that the missing band is literally a new particle or unmeasured field.
- The candidate interval came from inspecting T400 and is therefore a registered follow-up, not an independent discovery sample.
- The sampling null is heuristic; the source-level control and future independent data remain necessary.
