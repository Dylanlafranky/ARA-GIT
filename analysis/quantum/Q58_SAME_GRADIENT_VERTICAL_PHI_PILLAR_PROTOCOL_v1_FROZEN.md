# Q58 Same-Gradient Vertical Phi-Pillar Protocol v1 — Frozen

**Frozen:** 31 July 2026, Australia/Brisbane, before Q58 target-ratio calculation.

## Question

When a Q42 parent-cadence lineage and child-cadence lineage occupy the same
local ARA gradient coordinate, is their perpendicular, unnormalised connected
magnitude separated by the golden ratio?

The primary same-phase predictions are

\[
R_A(x)=\frac{M_{P,A}(x)}{M_{C,A}(x)}\approx\phi,
\qquad
R_B(x)=\frac{M_{P,B}(x)}{M_{C,B}(x)}\approx\phi.
\]

This is the corrected interpretation of “parent Phase A to child Phase A at
the exact same gradient,” rather than comparing different ARA positions such
as parent `1.8` with child `1.2`.

## Sources and fixed tier identities

Reuse the two local public-data caches already verified for Q42:

- `q40_return_flow_inhomo_v1_greedy/q40_derived_cache.npz` and
  `q40_connected_cache.npy`;
- `q41b_cadence_strand_inhomo_v1_landmax/q41b_derived_cache.npz` and
  `q41b_connected_cache.npy`;
- source DOI: `10.5281/zenodo.16753415`;
- branch: `c2_2local connectivity`;
- 100 seeds, 66 pair identities, 500 samples per archive.

The tier definitions remain exactly those established in Q42:

- child: Q42 `two_turn_7_5` cadence family;
- parent: Q42 `one_turn_15` cadence family;
- Phase A: Q42 qualifying positive/increasing half-wave;
- Phase B: the immediately following Q42 qualifying negative/decreasing
  half-wave.

Cadence family is assigned at the seed/pair lineage level. Q58 therefore
tests population-level cross-tier scaling after equal pair weighting; it does
not claim that an individual parent event is the genealogical parent of an
individual child event.

## Fixed local ARA coordinates

For each seed/pair lineage, use development samples `0..249` only. Let

\[
h(t)=\sqrt[3]{|\det C(t)|},
\]

where \(C(t)\) is the already stored connected-correlation matrix. Let
\(h_{05}\) and \(h_{95}\) be the development fifth and ninety-fifth
percentiles and retain the Q42 coordinate

\[
x(t)=2\frac{h(t)-h_{05}}{h_{95}-h_{05}}.
\]

Q58 evaluates the complete fixed interior grid

\[
\boxed{x\in\{0.2,0.4,0.6,0.8,1.0,1.2,1.4,1.6,1.8\}}.
\]

No coordinate may be selected or removed according to its distance from
\(\phi\). Endpoints `0` and `2` are excluded to reduce percentile-anchor and
overshoot sensitivity.

## Perpendicular unnormalised magnitude

Holding \(x\) fixed also fixes \(h\) within one lineage by construction.
Using \(h\) again as the vertical measure would therefore be circular. Q58
instead measures the full unnormalised connected-matrix magnitude

\[
m(t)=\|C(t)\|_F.
\]

The determinant-based coordinate and Frobenius magnitude are related but not
identical: matrices with the same \(|\det C|\) can have different singular
value distributions and different \(\|C\|_F\). Consequently, neither
\(M_P/M_C=1\) nor \(M_P/M_C=\phi\) is forced by the coordinate definition.

For every qualifying Q42 Phase-A and Phase-B half-wave, interpolate \(m(t)\)
at each crossed grid coordinate. A run is monotone in the Q42 closure
coordinate by construction; repeated zero-change samples are collapsed to
one coordinate before interpolation. No extrapolation is permitted.

## Frozen aggregation

For each archive, seed, pair, cadence family, phase and grid coordinate:

1. take the median interpolated magnitude across eligible cycles;
2. take the median across pairs within the same archive, seed, family, phase
   and coordinate, giving each pair equal weight;
3. retain only archive/seed/phase/coordinate cells containing both fixed
   cadence families; and
4. calculate the directed vertical ratio

\[
R_s(x)=\frac{M_{\mathrm{one\_turn\_15},s}(x)}
             {M_{\mathrm{two\_turn\_7.5},s}(x)},
\qquad s\in\{A,B\}.
\]

Do not replace this with `max/min`; parent-over-child direction is part of the
hypothesis.

Archive medians and seed-cluster bootstrap intervals are calculated
separately before any pooled descriptive summary.

## Predeclared landmarks, tolerance and support gate

Compare every grid-cell archive median with

\[
1,\sqrt2,1.5,\phi,\sqrt3,2.
\]

Reuse the T322/Q57 golden-equivalence band

\[
\boxed{|R-\phi|\leq0.08}.
\]

The Q58 Phi-pillar claim receives **strict support** only if all of the
following hold:

1. for each archive and each phase, at least seven of the nine fixed grid
   coordinates lie inside the Phi band;
2. for each archive and each phase, the mean absolute Phi error across all
   nine coordinates is at most `0.08`;
3. for each archive and each phase, Phi is the nearest named landmark to the
   median across all seed-by-coordinate ratios;
4. parent-over-child direction holds at at least eight of nine archive-median
   coordinates in each archive and phase; and
5. the mean absolute greedy-versus-landmax difference across the grid is at
   most `0.08` for both phases.

Report partial criteria, but a failure of any strict condition is not rescued
by selecting a favourable coordinate or phase after calculation.

## Controls and uncertainty

- 10,000 seed-cluster bootstrap replicates for every archive/phase/grid
  median and for each archive/phase whole-grid median.
- Wrong-phase controls: parent A / child B and parent B / child A at the same
  coordinate.
- Direction control: report child/parent reciprocals without using them to
  rescue the registered direction.
- Family-label null: within each archive and seed, permute the parent/child
  family labels across pair-level profiles while preserving family counts;
  compare the observed whole-grid absolute Phi error with 9,999 permutations.
- Report seed counts, lineage counts, crossing counts, missing cells, and
  denominator minima.
- Repeat the complete calculation with connected spectral norm
  \(\|C\|_2\) as a registered robustness measure. It cannot replace the
  Frobenius-norm primary result.

## Data gate

The primary test is valid only if:

- the raw `closure` and `connected` caches are present for both archives;
- Q42 eligibility and cadence classification can be reproduced;
- at least 50 seeds per archive have both cadence families at every reported
  primary grid coordinate; and
- all child denominators are finite and greater than `1e-12`.

If these conditions fail, record `NOT TESTABLE ON Q42` rather than substituting
normalized duration, normalized ARA position, or another post-hoc magnitude.

## Required validation and artifacts

- Hash this protocol before target calculation.
- Independently recompute sampled source records and all published summaries.
- Verify the coordinate interpolation reproduces direct values at exact grid
  hits and never extrapolates.
- Verify no target grid coordinate was removed.
- Save crossing-level, pair-level, seed-level and grid-summary records.
- Produce a static figure showing both phases and archives over the full fixed
  grid, with Phi and other named landmarks visible.
- Inspect the rendered figure before interpretation.

## Claim boundary

A pass would support a Phi-like population-level vertical magnitude relation
between the already identified Q42 cadence families at matched ARA gradient
positions. It would not establish individual parent-child genealogy,
universal Phi scaling, literal energy transfer, or a new quantum law. A fail
rejects this exact same-gradient Frobenius-magnitude translation without
rejecting every possible ARA cross-scale handover.
