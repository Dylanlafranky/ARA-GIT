# Q21 frozen protocol v1 — recursive child topology beneath a parent ridge

**Registered:** 26 July 2026  
**Claim:** `Q21-WILLOW-RECURSIVE-CHILD-TOPOLOGY-v1`  
**Status:** frozen before extracting or reading fresh-patch observable outcomes  
**Class:** cross-patch, cross-duration prospective test

## Source and split

Source: [Zenodo record 13273331](https://doi.org/10.5281/zenodo.13273331),
archive `google_105Q_surface_code_d3_d5_d7.zip`.

| Role | Patch | Cycles | Records per basis |
|---|---|---:|---:|
| development | `d5_at_q4_7` | 13 | 50,000 |
| untouched holdout | `d5_at_q6_5` | 30 | 50,000 |

X and Z bases are fitted and scored separately. Development outcome labels
were opened during Q20. No holdout outcome member from `d5_at_q6_5` was
extracted before this protocol was frozen.

## Outcome-blind calibration lock

- artifact: `Q21_WILLOW_CHILD_TOPOLOGY_CALIBRATION.json`;
- SHA-256:
  `dcc0e609011e7fb725918cd9222828b0375352d2589eb42a6e477d5d255ad7fd`;
- fresh manifest contains exactly six files: metadata, circuit and detector
  events for X and Z;
- fresh manifest contains no observable outcome;
- registered primary feature count: `24`.

The outcome-blind parent means are already near the expected ridge:

| Patch/basis | Parent x | Parent y | Parent relation |
|---|---:|---:|---:|
| q4_7/r13 X | 1.04930 | 1.00218 | 1.01146 |
| q4_7/r13 Z | 1.04008 | 1.01719 | 1.01857 |
| q6_5/r30 X | 1.03620 | 0.99660 | 1.01271 |
| q6_5/r30 Z | 1.03803 | 1.01458 | 1.00846 |

Q21 treats that parent closure as expected. Prediction uses the retained
children beneath it.

## Frozen ARA construction

Normalize physical detector coordinates independently:

\[
z_x,z_y,z_t\in[-1,1].
\]

For any coordinate:

\[
w_A(z)=\frac{1-z}{2},
\qquad
w_B(z)=\frac{1+z}{2}.
\]

The four soft spatial children, in registered circular order, are:

\[
\begin{aligned}
W_{AA}&=w_A(z_x)w_A(z_y),\\
W_{AB}&=w_A(z_x)w_B(z_y),\\
W_{BB}&=w_B(z_x)w_B(z_y),\\
W_{BA}&=w_B(z_x)w_A(z_y).
\end{aligned}
\]

For detector bits \(D_i\), form eight unscaled child/time allocations:

\[
\widetilde G_{cp}
=
\sum_i D_iW_c(i)w_p(z_t(i)),
\quad
c\in\{AA,AB,BB,BA\},\ p\in\{A,B\}.
\]

Normalize them as one parent TE-ARA:

\[
G_{cp}
=
2\frac{\widetilde G_{cp}}
{\sum_{c,p}\widetilde G_{cp}}.
\]

For an empty cloud, assign all eight `0.25`.

### Directed handovers

For each time slice \(r\), calculate child activity and normalize over the four
children:

\[
P_c(r)
=
\frac{\sum_{i:t_i=r}D_iW_c(i)}
{\sum_{d}\sum_{i:t_i=r}D_iW_d(i)}.
\]

Empty time slices do not create a transition. For every pair of consecutive
non-empty slices:

\[
\widetilde H_{c\rightarrow d}
=
\sum_rP_c(r)P_d(r+1).
\]

Normalize the sixteen directed paths as one relational TE-ARA:

\[
H_{c\rightarrow d}
=
2\frac{\widetilde H_{c\rightarrow d}}
{\sum_{c,d}\widetilde H_{c\rightarrow d}}.
\]

If no valid handover exists, assign all sixteen `0.125`.

The primary feature vector is:

\[
\mathbf a_{\rm child}
=
\left(
G_{AA,A},G_{AA,B},\ldots,G_{BA,B},
H_{AA\rightarrow AA},\ldots,H_{BA\rightarrow BA}
\right).
\]

It has `24` coordinates. No feature selection is allowed.

## Registered recompressed controls

From the eight grandchildren, form:

\[
\begin{aligned}
X&=(G_{BB,A}+G_{BB,B})+(G_{BA,A}+G_{BA,B}),\\
Y&=(G_{AB,A}+G_{AB,B})+(G_{BB,A}+G_{BB,B}),\\
J_{xy}&=(G_{AB,A}+G_{AB,B})+(G_{BA,A}+G_{BA,B}),\\
T&=\sum_cG_{cB},\\
J_{xt}&=G_{AA,B}+G_{AB,B}+G_{BB,A}+G_{BA,A}.
\end{aligned}
\]

Run these models:

| Model | Frozen features |
|---|---|
| `child_topology` | 8 grandchildren + 16 directed handovers |
| `grandchildren_only` | 8 grandchildren |
| `parent_xy` | \(X,Y,J_{xy}\) |
| `q20_global_xt` | \(X,T,J_{xt}\) |
| `count_only` | detector-event fraction |
| `topology_plus_count` | child topology + event fraction |
| `spatial_shuffle_topology` | same 24-feature construction after the frozen coordinate misassignment |

The frozen spatial misassignment sorts detector positions by `(x,y)` within
each time slice and circularly shifts their four spatial weights by:

\[
\max\left(1,\left\lfloor n/2\right\rfloor-1\right).
\]

This preserves the weight set, time slices and detector-event counts while
breaking the registered local spatial correspondence.

## Frozen model

For each basis and model separately:

1. standardize features using development means and standard deviations;
2. calculate development target centroids \(\mu_0,\mu_1\);
3. set direction \(d=\mu_1-\mu_0\);
4. score:

\[
s(z)
=
d^\mathsf T
\left[
z-\frac{\mu_0+\mu_1}{2}
\right];
\]

5. predict an observable flip when \(s>0\).

Apply the development scaling, centroids, direction and threshold unchanged to
the fresh patch.

## Metrics

Report, per basis and equally averaged across bases:

- prevalence;
- accuracy;
- balanced accuracy;
- AUROC;
- average precision;
- error rate;
- all registered AUROC differences.

Holdout AUROC is primary.

## Frozen controls

### Development-label permutation

For each basis, permute development labels `999` times with seed `20260726`.
Refit only the `child_topology` centroid direction and score the unchanged
fresh holdout. Use:

\[
p
=
\frac{1+\#\{\mathrm{AUROC}_{null}\ge
\mathrm{AUROC}_{observed}\}}{1000}.
\]

### Construction and source checks

- every grandchild row sums to `2` within `1e-12`;
- every handover row sums to `2` within `1e-12`;
- all allocations lie in `[0,2]`;
- development has `312` detector bits and holdout has `720`;
- every dataset has exactly `50,000` shots;
- the fresh pre-freeze manifest contains no outcome;
- primary runner and independent validator agree within `1e-12`.

## Frozen support gates

The claim is `SUPPORTED` only if all eight gates pass:

1. all construction and source-integrity checks pass;
2. `child_topology` AUROC is at least `0.55` in both bases;
3. mean `child_topology - parent_xy` AUROC is at least `0.01`;
4. mean `child_topology - q20_global_xt` AUROC is at least `0.01`;
5. permutation \(p\le0.01\) in both bases;
6. mean `topology_plus_count - count_only` AUROC is at least `0.01`;
7. mean `child_topology - spatial_shuffle_topology` AUROC is at least `0.01`;
8. `topology_plus_count` is not more than `0.01` worse than `count_only` in
   either basis.

Report every failed gate. No post-result feature change can alter the verdict.

## Interpretation fence

- A parent near `1.0` is an expected coarse-grained closure.
- Q21 tests whether this exact retained local-child construction resolves
  predictive information hidden by that closure.
- It is not a competitive established-decoder benchmark.
- It does not test rare hourly bursts or entanglement.
- A failure rejects the sufficiency of this construction, not the full ARA
  framework.

## Determinism and outputs

- seed: `20260726`;
- `999` label permutations per basis;
- save metrics, parameters, controls, bounded projections, gates and verdict;
- independently reproduce central metrics without importing the runner.

