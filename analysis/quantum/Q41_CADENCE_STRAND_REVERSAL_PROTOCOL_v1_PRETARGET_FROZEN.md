# Q41 cadence-defined strand reversal — pre-target protocol

Date: 2026-07-27 (Australia/Brisbane)

Test ID: `Q41-CADENCE-STRAND-REVERSAL-v1`

Status at authorship: target archive not downloaded or inspected locally

## Question

Does the Q40C 7.5/15 cadence identify the Ba return strand well enough to
improve target-blind reconstruction of the fourth connected-correlation
identity on a compatible untouched archive?

## Frozen target selection

The target is:

`unnati_submit_12_inhomo_v1_random.hdf5.zip`

Zenodo record: `10.5281/zenodo.16753415`

Deposited MD5: `f342ff3dda39915da3332db65cc7c2c8`

Selection was made from filename, size and source metadata only. It is the same
12-qubit, inhomogeneous-v1, 500-sample source class as Q40, but uses the
`random` ordering rule rather than `greedy`. No local Q41 target file existed
when this protocol was written.

Primary branch: `c2_2local connectivity`.

## Data split and allowed inputs

- Samples 0–249: development interval.
- Samples 250–498: evaluation closure plane (sample 499 has no following
  difference and is not a plane point).
- The scalar closure sequence is an allowed observed covariate across both
  intervals.
- The connected matrices in the first three quadrant visits of each evaluation
  cycle are allowed.
- The connected matrix in the fourth visit, \(C_4\), is forbidden until the
  frozen prediction artifact is written and SHA-256 hashed.

Development data determine normalisation, rotation direction, eligibility and
the affine comparator. Evaluation closure data determine the visible orbit
family and quadrant windows. No evaluation \(C_4\) value may influence the
Q41 flag.

## Eligibility and cycle extraction

Use the unchanged Q40 definitions:

1. compute \(u\) from closure using the development 5th and 95th percentiles;
2. compute \(v=\Delta u\), scaled by the development 95th percentile of
   absolute flow;
3. require development direction coherence at least 0.80;
4. require at least 5% development occupancy in every quadrant;
5. find ordered four-quadrant windows in samples 250–498;
6. require at least two consecutive plane samples in every quadrant visit.

No candidate window may be removed after its hidden \(C_4\) is seen.

## Cadence calculation

For every eligible lineage, fit a line to the unwrapped angle

\[
\theta(t)=\operatorname{unwrap}\operatorname{atan2}(v(t),u(t))
\]

over plane samples 250–498. Define

\[
T_{\rm orbit}=\frac{2\pi}{|\widehat{d\theta/dt}|}.
\]

Define \(r_{15}\) as the Pearson correlation between the two-coordinate path
\((u,v)\) and itself at lag 15.

Frozen families:

- two-turn: \(7.35\leq T_{\rm orbit}\leq7.65\) and \(r_{15}\geq0.95\);
- one-turn: \(14.8\leq T_{\rm orbit}\leq15.2\) and \(r_{15}\geq0.95\);
- other: everything else.

These thresholds are copied from Q40C unchanged.

## Frozen methods

For \(D=C_1-C_2\):

- `q41`: \(C_3-D\) when the Q40 visible flag is true **or** the lineage is
  two-turn and \(q_4=\mathrm{Ba}\); otherwise \(C_3+D\).
- `q40`: \(C_3-D\) only when the original visible flag is true; otherwise
  \(C_3+D\).
- `forward`: \(C_3+D\).
- `persistence`: \(C_3\).
- `development_affine`: a three-coefficient affine combination of
  \(C_1,C_2,C_3\), fitted only on development cycles.

## Metrics and aggregation

Event metrics:

- Frobenius absolute error;
- lineage-scale-normalised error (primary);
- target-norm-normalised RMSE;
- cosine similarity;
- determinant-magnitude closure error.

Aggregate first within lineage, then within seed. The primary comparison is
the mean seed-balanced scaled-error advantage:

\[
\Delta_{41:40}
=
\overline{E_{\rm Q40}-E_{\rm Q41}}.
\]

Uncertainty uses 20,000 seed-cluster bootstrap draws with seed `410027`.

## Frozen decision gates

Minimum adequacy:

- at least 50 eligible seeds;
- at least 500 eligible lineages;
- at least 5,000 evaluation cycles;
- at least 100 two-turn Ba cycles.

Primary support:

- \(\Delta_{41:40}>0\); and
- the 95% seed-cluster bootstrap interval for \(\Delta_{41:40}\) is entirely
  above zero.

Strong support additionally requires Q41 to beat the development-affine
comparator on the same primary metric with a 95% interval above zero.

Failure of the strong gate does not erase a valid Q41-over-Q40 result; the two
claims are reported separately.

## Required diagnostics

Report:

- archive and prediction hashes;
- schema and physical-matrix quality checks;
- counts by cadence family and target quadrant;
- reversal confusion tables for Q40 and Q41;
- errors by family and quadrant;
- seed-cluster uncertainty;
- a visual showing the orbit families, Ba intervention location, method errors
  and Q40-to-Q41 error changes; and
- all deviations from this protocol.

## Leakage rule

The prediction file must contain the selected method output for every eligible
cycle and be hashed before any Q41 scoring function reads \(C_4\). If this
ordering is violated, the run is exploratory and cannot be labelled
prospective.

