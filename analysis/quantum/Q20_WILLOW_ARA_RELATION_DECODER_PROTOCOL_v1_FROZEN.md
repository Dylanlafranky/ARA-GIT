# Q20 frozen protocol v1 — Willow ARA relation decoder

**Registered:** 26 July 2026  
**Claim:** `Q20-WILLOW-ARA-RELATION-v1`  
**Status:** frozen before opening any `obs_flips_actual.b8` member  
**Class:** exploratory same-patch cross-duration prediction; independent replication required

## Source and split

Source: [Zenodo record 13273331](https://doi.org/10.5281/zenodo.13273331), archive
`google_105Q_surface_code_d3_d5_d7.zip`, patch `d5_at_q4_7`.

| Split | Cycles | Use |
|---|---:|---|
| development | 13 | freeze raw geometry; then calibrate prediction orientation and threshold |
| holdout | 30 | untouched scoring only |

X and Z bases are fitted and scored separately. Each basis contains 50,000 shots in each split.

The outcome is the one-bit `obs_flips_actual.b8` target. A Q20 decoding error is:

\[
\widehat y\ne y_{\rm actual}.
\]

No existing decoder prediction enters Q20.

## Frozen outcome-blind diameter selection

The geometry-calibration artifact was created without reading an outcome file:

- artifact: `Q20_WILLOW_ARA_GEOMETRY_CALIBRATION.json`;
- SHA-256: `29449fd5c5a27c87c2a0966afbcaaa0b20b28f480ca952c0bfc44d5071e0ed4e`;
- selected diameter pair: physical `x` and cycle/time `t`.

The selection rule was the largest pooled development standard deviation of the crossed-versus-aligned relation
coordinate among `x–y`, `x–time` and `y–time`.

## Frozen ARA construction

For each detector \(i\), independently normalize its selected coordinates to:

\[
z_x(i),z_t(i)\in[-1,1].
\]

The two gradient weights along either diameter are:

\[
w_A(z)=\frac{1-z}{2},
\qquad
w_B(z)=\frac{1+z}{2}.
\]

For shot detector bits \(D_i\in\{0,1\}\), form four Tier-3 allocations:

\[
\begin{aligned}
C_{AA}&=\frac{\sum_iD_iw_A(z_x(i))w_A(z_t(i))}{\sum_iD_i},\\
C_{AB}&=\frac{\sum_iD_iw_A(z_x(i))w_B(z_t(i))}{\sum_iD_i},\\
C_{BA}&=\frac{\sum_iD_iw_B(z_x(i))w_A(z_t(i))}{\sum_iD_i},\\
C_{BB}&=\frac{\sum_iD_iw_B(z_x(i))w_B(z_t(i))}{\sum_iD_i}.
\end{aligned}
\]

They satisfy:

\[
C_{AA}+C_{AB}+C_{BA}+C_{BB}=1.
\]

For an empty event cloud, assign all four allocations `0.25`, meaning no directional evidence and a ridge reading.

The frozen information-lock coordinates on the ARA `0–2` scale are:

\[
\underbrace{X}_{\text{x parent}}
=2(C_{BA}+C_{BB}),
\]

\[
\underbrace{T}_{\text{time parent}}
=2(C_{AB}+C_{BB}),
\]

\[
\underbrace{J}_{\text{crossed relation}}
=2(C_{AB}+C_{BA}).
\]

Their opposite allocations are respectively `2-X`, `2-T` and `2-J`. The primary ARA vector is:

\[
\mathbf a=(X,T,J).
\]

The separate amplitude/control coordinate is:

\[
F=\frac{\sum_iD_i}{N_{\rm detectors}}.
\]

`F` is not treated as a fourth relation child.

## Frozen development calibration

For each basis separately:

1. standardize each feature using only its 13-cycle development mean and standard deviation;
2. for a feature vector \(\mathbf z\), calculate the two development target centroids
   \(\boldsymbol\mu_0,\boldsymbol\mu_1\);
3. define the equal-prior nearest-centroid direction:

\[
\mathbf d=\boldsymbol\mu_1-\boldsymbol\mu_0;
\]

4. define the signed score:

\[
s(\mathbf z)
=
\mathbf d^\mathsf T
\left[
\mathbf z-\frac{\boldsymbol\mu_0+\boldsymbol\mu_1}{2}
\right];
\]

5. predict an observable flip when \(s>0\).

Apply the frozen development scaling, centroids, direction and zero threshold to the 30-cycle holdout.

Run three registered models:

| Model | Features |
|---|---|
| `ARA_relation` | \(X,T,J\) |
| `count_only` | \(F\) |
| `ARA_plus_count` | \(X,T,J,F\) |

No coefficient optimization, nonlinear classifier or holdout retuning is allowed.

## Frozen metrics

For development and holdout, separately by basis and averaged equally across bases:

1. target prevalence;
2. accuracy;
3. balanced accuracy;
4. AUROC;
5. average precision;
6. model error rate;
7. `ARA_relation - count_only` AUROC difference;
8. `ARA_plus_count - count_only` AUROC difference.

The primary comparison uses holdout AUROC because it evaluates the rank ordering without changing the frozen
threshold. Balanced accuracy tests the frozen threshold directly.

## Frozen controls

### Development-label permutation

For each basis, permute the 13-cycle target labels `999` times with seed `20260726`. Refit only the registered
nearest-centroid direction and apply it to the unchanged 30-cycle ARA features and unchanged holdout labels.

The one-sided empirical p-value is:

\[
p=\frac{1+\#\{\mathrm{AUROC}_{null}\ge\mathrm{AUROC}_{observed}\}}{1000}.
\]

### Secondary diameter controls

After the primary result is written, repeat the same registered calculation for `x–y` and `y–time`. These are
descriptive controls. They cannot replace or repair the outcome-blind primary `x–time` selection.

### Construction checks

- all four child allocations are finite and sum to one within `1e-12`;
- all ARA coordinates lie in `[0,2]` within `1e-12`;
- r13 contains 312 detector bits per shot and r30 contains 720;
- every split contains exactly 50,000 shots;
- each target file contains exactly one byte-aligned bit per shot;
- the primary test and validator reproduce identical central metrics within `1e-12`.

## Frozen primary gates

`Q20-WILLOW-ARA-RELATION-v1` is `SUPPORTED` only if all gates pass:

1. every construction and source-integrity check passes;
2. `ARA_relation` holdout AUROC is at least `0.55` in both X and Z;
3. mean-basis `ARA_relation` AUROC exceeds `count_only` by at least `0.01`;
4. `ARA_relation` permutation p-value is at most `0.01` in both X and Z;
5. mean-basis `ARA_plus_count` AUROC exceeds `count_only` by at least `0.01`;
6. `ARA_plus_count` is not more than `0.01` AUROC worse than `count_only` in either basis.

Report every failed gate. A strong descriptive pattern cannot change the frozen verdict.

## Tier-energy rule

The child allocations above are fractions at the parent measurement boundary. They reconstruct the parent ARA
coordinates and are not added as independent local TE-ARA totals. If a later test opens a child as its own
identity, it is renormalized locally to TE-ARA `2`, while its maximum capacity relative to the current parent is
halved for each completed downward tier.

Q20 performs prediction, not a physical or measurement-space ablation. Therefore the half-capacity rule is
preserved in the construction but is not turned into an unsupported energy-removal gate.

## Interpretation fence

- First interpret the frozen ARA result.
- Then restore established quantum names and compare with conventional decoding concepts.
- Q20 cannot claim competitive decoder performance without an established-decoder benchmark.
- Q20 cannot claim the cause of rare correlated bursts from this ordinary-record subset.
- Same-patch cross-duration success remains exploratory until another patch, processor or deposit replicates it.

## Determinism and outputs

- seed: `20260726`;
- `999` label permutations per basis;
- save metrics, model parameters, permutation controls, secondary-diameter controls and verdict;
- save a bounded per-shot projection sample rather than all raw shot rows;
- an independent validator must recompute the central result without importing the primary runner.

