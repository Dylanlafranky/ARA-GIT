# Q44A sparse-group ARA mixing prediction

Date frozen: 2026-07-28 (Australia/Brisbane)

Test ID: `Q44A-SPARSE-GROUP-ARA-MIXING-v1`

Status at authorship: **post-eligibility, pre-score frozen**. Q44 stopped
because three cadence-family × quadrant groups had fewer than 25 development
cycles. No Q44 prediction artifact was written and no evaluation fourth matrix
was read or scored.

## What may inform this amendment

Only the following target information has been inspected:

- source schema and quality-control samples;
- scalar closure paths used to establish eligibility;
- samples `0..249`, including development fourth matrices;
- evaluation window counts and their visible cadence/quadrant labels;
- evaluation first, second and third matrices where the Q44 loop reached them.

No evaluation fourth matrix has been accessed.

## Frozen repair

Keep the Q44 equation unchanged:

\[
\widehat C_4
=
C_3+\widehat\alpha D+\widehat\beta O,
\]

\[
D=C_1-C_2,
\qquad
O=(C_3-C_2)-\operatorname{proj}_{D}(C_3-C_2).
\]

Fit two development-only coefficient tables:

1. cadence-family × fourth-quadrant;
2. fourth-quadrant only.

For an evaluation group:

- use its family × quadrant coefficients when that group has at least `25`
  development cycles;
- otherwise use the corresponding quadrant-only coefficients;
- require the selected fallback group to have at least `25` development
  cycles or declare the test ineligible.

This is a deterministic support fallback. It cannot inspect errors, cosine,
targets or any evaluation fourth matrix.

Apply the identical fallback to the grouped affine upper comparator. The pooled
affine comparator remains pooled.

## Prediction seal, metrics and gates

All Q44 prediction-sealing rules, evaluation samples, comparators, metrics,
aggregation, bootstrap, adequacy gates, support gates and claim boundaries are
unchanged.

In particular:

1. identify evaluation windows from the visible scalar path;
2. calculate only \(C_1,C_2,C_3,D,O\);
3. save all predictions and metadata;
4. print SHA-256 of the sealed artifact;
5. only then read and score evaluation \(C_4\).

The result must report which groups used the quadrant-only fallback.

## Interpretation boundary

Q44A is a prospective held-out fourth-state prediction after a
development-support repair. It is not as strong as an untouched-target
replication of a fully specified sparse-group rule, so any supported result
must retain the label **prospective after eligibility amendment**.
