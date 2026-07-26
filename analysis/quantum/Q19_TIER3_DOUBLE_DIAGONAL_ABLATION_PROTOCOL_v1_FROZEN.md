# Q19 frozen protocol v1 — Tier-3 double-diagonal ablation

**Registered:** 26 July 2026  
**Claim:** `Q19-T3-DOUBLE-DIAGONAL-v1`  
**Status:** frozen before Q19 calculation  
**Class:** exploratory same-deposit child-to-parent ablation; independent replication required

## Frozen sources

- Q16 raw ARA records: `Q16_ARA2_RAW_FOUR_CHILD_RECORDS.csv`;
- source SHA-256: `0f7e58b349e5bf3cdda0110a99627134c7a76c69bb0443be8ba1576c4f01e48b`;
- Q16 result: `Q16_ARA2_RAW_FOUR_CHILD_RESULTS.json`;
- Q16-result SHA-256: `30c5b458505ffdb54c9ee1b115ca1518cf6aa8cd185a474da0df5a28bd1ad3a4`;
- Q18 result: `Q18_GROUPED_DIAMETER_RESIDUAL_RESULTS.json`;
- Q18-result SHA-256: `02f18498612b67f28df46695ef054285547a0f5f43c41eb96ad6d2b8fdf59b1d`;
- tier map: `ARA_QUANTUM_FRACTAL_TIER_MAP_2026-07-26.md`;
- tier-map SHA-256: `92f488264def3ef2c13c9d3bf79a0d06db6f74ae90ac25fe50bb6299cd91b113`;
- 4 children, 45 raw ARA cuts, 40 development and 40 holdout records per child.

Only ARA child code, split, record index, cut and `ara_x` enter the primary calculation.

## Frozen tier assignment

- Tier 1: `J`;
- Tier 2: `U`, `V`;
- Tier 3: `C00`, `C01`, `C10`, `C11`.

At Tier 3:

| Child | Parent 1 | Parent 2 |
|---|---|---|
| `C00` | A | A |
| `C01` | A | B |
| `C10` | B | A |
| `C11` | B | B |

## Frozen branch definitions

For development child centroids \(\mu_{ij}^{dev}\), define:

\[
d_{1A}=\mu_{00}^{dev}-\mu_{01}^{dev},
\qquad
d_{1B}=\mu_{10}^{dev}-\mu_{11}^{dev},
\]

\[
d_{2A}=\mu_{00}^{dev}-\mu_{10}^{dev},
\qquad
d_{2B}=\mu_{01}^{dev}-\mu_{11}^{dev}.
\]

The registered branches are:

| Branch | Removed pair | Predicted survivor | Predicted merging triple |
|---|---|---|---|
| `AA` primary | \(d_{1A},d_{2A}\) | `C11` | `C00,C01,C10` |
| `AB` secondary | \(d_{1A},d_{2B}\) | `C10` | `C00,C01,C11` |
| `BA` secondary | \(d_{1B},d_{2A}\) | `C01` | `C00,C10,C11` |
| `BB` secondary | \(d_{1B},d_{2B}\) | `C00` | `C01,C10,C11` |

For each branch, stack its two development diagonal vectors, obtain an order-independent orthonormal basis
\(Q_b\) from singular-value decomposition, and remove their joint span:

\[
x_{i,r}^{(-b)}
=
(x_{i,r}-M^{dev})
-
\underbrace{Q_bQ_b^\mathsf T(x_{i,r}-M^{dev})}_
{\text{both registered Tier-3 diagonal components}}.
\]

The same frozen development centre and basis are applied to holdout.

## Frozen metrics

For each branch:

1. **Development diagonal angle:** acute angle between its two registered vectors.
2. **Holdout merge ratio**
   \[
   R_{\rm merge}
   =
   \frac{
   \sqrt{\frac13\sum_{i\in T}\lVert\mu_i^{hold,res}-\bar\mu_T^{hold,res}\rVert^2}
   }{
   \lVert\mu_s^{hold,res}-\bar\mu_T^{hold,res}\rVert
   },
   \]
   where \(T\) is the predicted merging triple and \(s\) the predicted survivor. Smaller is stronger.
3. **Survivor binary balanced accuracy:** nearest frozen development centroid between the survivor and the
   combined triple, with equal weight on survivor recall and triple recall.
4. **Holdout rank-one energy share:** first singular-value energy divided by all singular-value energy of the
   four centered residual holdout centroids.
5. **Tier-1 `J` holdout retention:** residual `J` norm divided by original holdout `J` norm.
6. **Holdout between-child energy retention:** residual centered-child energy divided by original holdout
   centered-child energy.
7. **Four-child nearest-centroid accuracy:** descriptive only, because the three development centroids are
   forced to merge by construction.

## Frozen primary gates

The primary `AA` branch is `SUPPORTED` only if:

1. the two development diagonals are rank two and meet at an acute angle of at least `15°`;
2. holdout merge ratio is at most `0.50`;
3. holdout survivor binary balanced accuracy is at least `0.80`;
4. holdout rank-one energy share is at least `0.80`;
5. Tier-1 `J` holdout retention is at most `0.75`;
6. holdout between-child energy retention is at most `0.60`;
7. survivor binary accuracy exceeds the `99th` percentile and merge ratio is below the `1st` percentile of
   `9,999` balanced-development-label controls;
8. no more than `1%` of the `9,999` balanced-development-label controls and no more than `5%` of `1,000`
   within-one-development-archive pseudo-diagonal controls pass deterministic gates 1–6.

## Secondary reversible-corner branch

Run deterministic gates 1–6 for `AB`, `BA` and `BB`. Declare `FOUR-CORNER REVERSIBILITY SUPPORTED` only if all
four branches pass gates 1–6. Secondary success cannot repair a failed primary branch.

## Controls

### Balanced development-label control

Pool the 160 development record vectors and randomly repartition them into four balanced pseudo labels of 40.
Construct the `AA` diagonal plane from the pseudo development centroids, but apply it to the original untouched
holdout records with their original ARA child codes. Repeat `9,999` times.

### Within-one-archive pseudo-diagonal control

Select one real development archive, permute its 40 records and split them into four pseudo children of 10.
Construct an `AA` plane from those pseudo centroids and apply it to the original untouched holdout records.
Cycle evenly across source archives for `1,000` repetitions.

Controls use the original holdout child labels only for scoring the preregistered predicted survivor/triple.

## Construction–evidence fence

- The selected three development centroids collapse exactly after removing their two development differences.
- Development residual centroid rank no greater than one is guaranteed.
- A four-class nearest-centroid accuracy loss is therefore guaranteed and is descriptive, not a gate.
- A Walsh `U/V/J` decomposition always exists for four labels and is not evidence.
- Empirical evidence is restricted to untouched holdout contraction, survivor separation, Tier-1 loss,
  rank-one persistence and frozen-control comparison.
- This is a measurement-space ablation, not a physical quantum intervention.

## Conventional comparison quarantine

Established quantum names, Ramsey/Hahn summaries and reconstructed quantum states may be restored only after
the ARA result JSON is written. They cannot alter a branch, orientation, metric, threshold or verdict.

## Determinism and outputs

- seed: `20260726`;
- `9,999` balanced-development-label controls;
- `1,000` within-archive pseudo-diagonal controls;
- save branch metrics, gates, residual projections, controls and verdict;
- an independent validator must recompute all central deterministic metrics without importing the primary test.

