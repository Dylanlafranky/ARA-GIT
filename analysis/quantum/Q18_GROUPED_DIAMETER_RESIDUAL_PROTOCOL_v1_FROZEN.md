# Q18 frozen protocol v1 - grouped-diameter residual geometry

**Registered:** 26 July 2026  
**Claim:** `Q18-GROUP-RESIDUAL-v1`  
**Status:** frozen before Q18 calculation  
**Class:** exploratory same-deposit follow-up; independent replication required

## Sources

- Q16 records: `Q16_ARA2_RAW_FOUR_CHILD_RECORDS.csv`;
- Q16 records SHA-256: `0f7e58b349e5bf3cdda0110a99627134c7a76c69bb0443be8ba1576c4f01e48b`;
- Q17 result: `Q17_CHILD_PHASE_PAIR_RESULTS.json`;
- Q17 result SHA-256: `3c599b25f991d00ee190612f3c2cbd11dd76605d3924c77e351a0def4b54478a`;
- four children, 45 raw ARA cuts, 40 development and 40 holdout records per child.

Only ARA child labels, split, record index, raw cut and `ara_x` enter the primary geometry.

## Grouped Phase A/B codes

| Diameter | Phase A group | Phase B group |
|---|---|---|
| `U` | `C00, C01` | `C10, C11` |
| `V` | `C00, C10` | `C01, C11` |
| `J` Coupling ARA | `C00, C11` | `C01, C10` |

The sign is reversible. Phase A/B group membership, not sign naming, carries the geometry.

## Frozen residual operator

Let \(x_{i,r}\in\mathbb R^{45}\) be one raw ARA record, \(\mu_i^{dev}\) its development child centroid and
\(M^{dev}=\frac14\sum_i\mu_i^{dev}\).

For grouped code \(s_g(i)\in\{-1,+1\}\), define

\[
D_g^{dev}=\frac12\sum_i s_g(i)\mu_i^{dev},
\qquad
\hat D_g^{dev}=D_g^{dev}/\lVert D_g^{dev}\rVert.
\]

Removing grouped diameter \(g\) means

\[
x^{(-g)}_{i,r}
=
(x_{i,r}-M^{dev})
-
\left[(x_{i,r}-M^{dev})\cdot\hat D_g^{dev}\right]\hat D_g^{dev}.
\]

This is a mathematical measurement-space projection, not a physical intervention.

Primary removal: `J`. Secondary removals: `U`, `V`.

## Frozen metrics

For removed diameter \(g\):

1. **Holdout leakage**
   \[
   L_g=
   \frac{\lVert D_g^{hold,res}\rVert}{\lVert D_g^{hold,original}\rVert}.
   \]
2. **Remaining-axis development retention**
   \[
   T_h=
   \frac{\lVert D_h^{dev,res}\rVert}{\lVert D_h^{dev,original}\rVert}.
   \]
3. **Remaining-axis persistence**
   \[
   P_h=
   |\cos(D_h^{dev,res},D_h^{hold,res})|.
   \]
4. **Grouped Phase A/B holdout balanced accuracy:** classify holdout records with the frozen residual development
   diameter and midpoint threshold.
5. **Residual rank-two energy share:** fraction of holdout centred-child singular-value energy in its first two
   dimensions.
6. **Remaining-axis independence:** absolute cosine between the two development residual diameters.
7. **Residual four-child recovery:** nearest frozen development centroid in the two remaining residual
   coordinates, scored by four-class balanced accuracy.

## Frozen primary gates

The primary Coupling-ARA removal branch is `SUPPORTED` only if:

1. removed-`J` holdout leakage `<= 0.25`;
2. both remaining-axis development retentions are `>= 0.75`;
3. both remaining-axis holdout persistences are `>= 0.80`;
4. both remaining grouped Phase A/B holdout balanced accuracies are `>= 0.80`;
5. holdout residual rank-two energy share is `>= 0.95`;
6. absolute cosine between the remaining residual axes is `<= 0.80`;
7. residual four-child balanced accuracy is `>= 0.70` and exceeds the `99th` percentile of `9,999` holdout-label
   shuffles;
8. no more than `1%` of `9,999` balanced-label full-pipeline shuffles and no more than `5%` of `1,000`
   within-one-archive pseudo-child controls pass gates 1-7.

## Secondary symmetry branch

Run the same deterministic gates 1-7 after removing `U` and `V`. Report each separately. Declare
`THREE-DIAMETER RESIDUAL SYMMETRY SUPPORTED` only if all three removals pass gates 1-7. Secondary success cannot
repair a failed primary branch.

## Control construction

### Holdout-label classification shuffle

Keep the primary residual coordinates and predictions fixed. Permute the 160 balanced holdout child labels
`9,999` times and recompute four-class balanced accuracy.

### Balanced-label full-pipeline shuffle

Within development and holdout separately, pool the 160 record vectors and independently permute them into four
balanced pseudo-labels of 40 records. Recompute the complete primary-removal pipeline.

### Within-one-archive pseudo-children

Select one real archive, then independently partition its 40 development and 40 holdout records into four
pseudo-children of 10 records. Recompute the complete primary-removal pipeline. Cycle equally across source
archives.

## Construction-evidence fence

- Exact zero development leakage is guaranteed and not a gate.
- Development residual rank no greater than two is guaranteed and not a gate.
- Three grouped Walsh-style contrasts always exist for four labels and are not evidence.
- Evidence is the unchanged holdout geometry and negative-control comparison.

## Conventional comparison quarantine

Established quantum names may be restored only after the ARA result JSON is written. They cannot alter a metric,
threshold, orientation or verdict.

## Determinism and outputs

- seed: `20260726`;
- `9,999` holdout-label shuffles;
- `9,999` full-pipeline balanced-label shuffles;
- `1,000` pseudo-child controls;
- save removal metrics, record coordinates, control results, gates and verdict;
- an independent validator must recompute all central deterministic metrics without importing the primary test.
