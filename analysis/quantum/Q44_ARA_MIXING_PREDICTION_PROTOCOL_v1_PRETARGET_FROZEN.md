# Q44 compact ARA mixing prediction

Date frozen: 2026-07-28 (Australia/Brisbane)

Test ID: `Q44-ARA-MIXING-PREDICTION-v1`

Status at authorship: **pre-target frozen**. The target file named below has
not been downloaded, extracted, numerically inspected or used to alter this
protocol.

## Question

Can the compact ARA mixing equation learned only from the target archive's
development half predict the held-out fourth connected-matrix identity?

\[
\widehat C_4
=
C_3
+
\widehat\alpha_g\,D
+
\widehat\beta_g\,O,
\]

where:

\[
D=C_1-C_2,
\]

\[
V=C_3-C_2,
\qquad
O=V-\operatorname{proj}_{D}(V),
\]

and \(g=(\text{cadence family},q_4)\) is fixed from the visible scalar
quadrant path.

ARA translation:

- \(C_3\): most recent visible whole;
- \(D\): visible child diameter/relation;
- \(\alpha_g D\): predicted movement along that relation;
- \(O\): visible perpendicular `Other`;
- \(\beta_g O\): predicted retained perpendicular contribution;
- \(\widehat C_4\): next whole identity.

The equation is fixed. Only the scalar coefficients \(\alpha_g,\beta_g\)
are estimated from the target's development half.

## Development-stage selection

Before target selection, four grouping variants of the same equation were
compared on the already-open Q40 greedy and Q41B landmax archives. The
`family_quadrant` version had the lowest mean seed-balanced error among the
mixing variants:

| Method | Greedy error | Landmax error |
|---|---:|---:|
| family×quadrant ARA mixing | 0.28986 | 0.31997 |
| family×quadrant diameter only | 0.31394 | 0.34680 |
| pooled affine | 0.38174 | 0.35828 |
| family×quadrant affine | 0.20188 | 0.19815 |

Selection artifact:
`Q44_DEVELOPMENT_MIXING_OPERATOR_SELECTION.json`.

The more flexible grouped affine comparator is retained. Its earlier
advantage is not hidden and Q44 does not require ARA to beat it.

## Frozen target

- Zenodo DOI: `10.5281/zenodo.16753415`;
- file: `unnati_submit_12_inhomo_v1_mimic.hdf5.zip`;
- deposited MD5: `08b2eaa89268952f7e197eecb2ea9610`;
- branch: `c2_2local connectivity`;
- 12 qubits, 66 two-qubit identities, 100 trials, 500 samples;
- target choice reason: same inhomogeneous-v1 system family and sampling
  contract as Q40/Q41B, but a distinct ordering identity not previously used
  anywhere in the repository search.

The target was selected by repository and Zenodo metadata only.

## Frozen coordinate and eligibility

Unchanged from Q40–Q43:

1. Use samples `0..249` for all development quantities.
2. Normalize the scalar connected-closure path using development-only
   centre, radius and flow scale.
3. Label the four sign quadrants of closure level and closure flow.
4. Require direction coherence at least `0.80`.
5. Require minimum development quadrant occupancy at least `0.05`.
6. Classify cadence as:
   - two-turn `7.5`;
   - one-turn `15`;
   - other;
   using the unchanged Q42 rules.
7. Extract complete four-quadrant windows with at least two samples per
   quadrant.

The scalar path is visible for window localization. Q44 therefore predicts
the hidden connected-matrix identity conditional on the observed scalar
trajectory; it is not a time-ahead forecast of when the quadrant occurs.

## Frozen coefficient fit

For every complete development window (`0..248`), calculate:

\[
Y=C_4-C_3.
\]

For each group \(g=(\text{family},q_4)\), fit the two scalar coefficients by
unregularized least squares over all matrix entries:

\[
(\widehat\alpha_g,\widehat\beta_g)
=
\arg\min_{\alpha,\beta}
\sum_{i\in g}
\left\|
Y_i-\alpha D_i-\beta O_i
\right\|_F^2.
\]

Use a Moore–Penrose inverse with `rcond=1e-12`. A group must contain at
least `25` development cycles. If any evaluation group lacks that
development support, Q44 is ineligible rather than silently pooled.

No coefficient is fixed to `0.5`, Phi or any Q43 post-result value.

## Prediction sealing

For evaluation samples `250..498`:

1. identify complete windows from the visible scalar path;
2. calculate only \(C_1,C_2,C_3,D,O\);
3. create every ARA and baseline prediction;
4. save target indices, visible inputs, coefficients and predictions;
5. calculate and print SHA-256 of the closed prediction artifact;
6. only then read the target \(C_4\) matrices and score.

The prediction artifact must not contain actual fourth matrices.

## Frozen comparators

1. **Diameter only**
   \[
   C_3+\widehat\alpha_gD.
   \]
   This is the direct ablation of retained `Other`.
2. **Persistence**
   \[
   C_3.
   \]
3. **Forward relation**
   \[
   C_3+D.
   \]
4. **Reverse relation**
   \[
   C_3-D.
   \]
5. **Local linear continuation**
   \[
   2C_3-C_2.
   \]
6. **Pooled development affine**
   \[
   aC_1+bC_2+cC_3.
   \]
7. **Family×quadrant development affine**, the stronger flexible control.

Both affine comparators use development samples only.

## Metrics and aggregation

For each cycle report:

- Frobenius error divided by the lineage development median matrix norm;
- NRMSE divided by target norm;
- cosine similarity;
- determinant-closure error;
- predicted versus actual sign relative to the forward relation.

Aggregate cycles to lineage means, then lineage means to seed means. Report
seed-balanced means and 20,000-draw seed-cluster bootstrap intervals.

For lower-is-better metrics, ARA advantage over a comparator is:

\[
\text{comparator error}-\text{ARA error}.
\]

## Frozen adequacy gates

- at least `80` represented seeds;
- at least `1,000` evaluation cycles;
- all scored groups have at least `25` development cycles;
- all prediction arrays finite;
- prediction artifact saved and hashed before target scoring.

Failure of an adequacy gate produces `INCONCLUSIVE — ELIGIBILITY`.

## Frozen support gates

Conditional on adequacy:

1. seed-balanced ARA scaled error at most `0.40`;
2. seed-balanced ARA cosine at least `0.85`;
3. ARA beats diameter-only by at least `0.01` scaled-error units and the
   95% seed-bootstrap interval for the advantage is wholly above zero;
4. ARA beats pooled affine on scaled error and the 95% seed-bootstrap
   interval for the advantage is wholly above zero.

If all four pass: `SUPPORTED — COMPACT ARA MIXING PREDICTION`.

If the absolute gates pass but one comparison gate fails:
`PARTIAL — PREDICTIVE SHAPE, NO DISTINCT MIXING ADVANTAGE`.

Otherwise: `NOT SUPPORTED — COMPACT ARA MIXING PREDICTION`.

The family×quadrant affine result is an explicitly reported upper
comparator, not a support gate.

## Claim boundary

Q44 can test whether a compact identity–diameter–Other equation predicts an
unseen fourth connected-matrix identity on one public simulator archive.

It cannot establish:

- a universal physical mixing law;
- a hidden quantum particle or field;
- universal TE-ARA conservation;
- quantum-gravity unification;
- superiority to unrestricted statistical learning; or
- time-ahead forecasting of the scalar quadrant occurrence.

