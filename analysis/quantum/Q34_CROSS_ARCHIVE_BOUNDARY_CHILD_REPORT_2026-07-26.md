# Q34 — Untouched Cross-Archive Boundary-Child Replication

**Date:** 26 July 2026  
**Ledger:** T289  
**Frozen verdict:** **CROSS-ARCHIVE BOUNDARY-CHILD FLOW NOT REPLICATED**  
**Independent raw-HDF5 validation:** **PASS**

## Result first

Q34 moved the Q33B ARA-first route to a public quantum-simulator archive that
had not previously been used in the numerical work. The ARA geometry,
selection rule, development/evaluation split, controls and pass/fail gates were
frozen before the target archive was downloaded.

The target changed from a random interaction ordering to a greedy interaction
ordering while retaining the same 12-qubit pure-state family.

The exact route still moved inward weakly:

- evaluation median normalized closure flow: `+0.00736`;
- evaluation mean flow: `+0.03577`;
- positive next flow: `54.21%`;
- positive median in both `c2` and `c4`;
- development positive fraction: `55.44%`.

However, the frozen replication gates did not all pass:

- the exact positive fraction missed the declared `55%` floor;
- the sibling advantage was not stable under paired median or cluster
  bootstrap;
- topology, seed and time controls were not all beaten by the required
  margins.

Therefore the stronger Q33B boundary-child effect does **not** generalize
unchanged from random to greedy network ordering.

## What was held fixed

The structural route remained:

\[
\underbrace{2}_{\substack{\text{complete}\\\text{same-rung span}}}
+
\left(
\underbrace{1}_{\substack{\text{current-rung}\\\text{contribution}}}
+
\underbrace{\frac12}_{\substack{\text{one complete child}\\
\text{projected one rung up}}}
\right)
=
\underbrace{\frac72}_{\text{declared ARA route}}.
\]

The `0.5` coefficient was structural and was never fitted to energy or closure
data. It generated the same directed rule used by Q33B: after a high-side
source releases, select the source endpoint child with the smaller starting
normalized closure.

For every relation:

\[
\underbrace{z_c(t)}_{\substack{\text{starting}\\\text{closure position}}}
=
\frac{
\underbrace{h_c(t)}_{|\det C_c(t)|^{1/3}}
}{
\underbrace{Q_{0.95}^{dev}(h_c)}_{\text{frozen child reference}}
},
\qquad
\underbrace{g_c(t)}_{\substack{\text{next-slice}\\\text{closure flow}}}
=
\frac{h_c(t+1)-h_c(t)}{Q_{0.95}^{dev}(h_c)}.
\]

Starting \(z\) selected the route. The unseen next-slice \(g\) was the scored
outcome.

## Public target and evidence seal

- Source: Akhouri, Shandera and Henry public simulator archive,
  DOI `10.5281/zenodo.16753415`.
- Frozen file: `unnati_submit_12_pure_greedy.hdf5.zip`.
- Deposited MD5: `c1cf77ccff486e3786d73ba47f8674f1`.
- Extracted HDF5 SHA-256:
  `830a4cb9baf3e8e8f70a81611ba7af97b90654b48de37674fa1a530ac3deb45d`.
- Protocol SHA-256:
  `56963274392d0c1f4b1c9c0cfe2ece700d25f20b43c9136b881bbde39baeae1e`.
- Fidelity SHA-256:
  `f480e7fc7bcdbc7a69ad0a3b921552c9c8fad84e9e2e96c438f714f2373bda98`.

The target contains:

- 2 connectivity branches;
- 100 unitary seeds per branch;
- 500 time slices;
- 66 pair relations per slice.

Data-quality checks found:

- maximum trace error `2.49e-5`;
- maximum Hermiticity error `0`;
- minimum sampled eigenvalue `-4.44e-7`;
- no sampled PSD failures at the frozen `-1e-6` tolerance;
- exactly diagonal connected-correlation matrices in the sampled data.

## Evaluation results

### Route flow

| Route | Events | Median \(g\) | Mean \(g\) | Positive fraction | Median start \(z\) |
|---|---:|---:|---:|---:|---:|
| Exact boundary child | 16,001 | +0.00736 | +0.03577 | 54.21% | 0.1720 |
| Sibling | 16,001 | +0.01461 | +0.02148 | 51.93% | 0.8741 |
| Topology | 16,001 | +0.00203 | +0.03008 | 53.48% | 0.1085 |
| Seed `+37` | 15,085 | +0.00340 | +0.04382 | 57.24% | 0.0766 |
| Time `+137` | 15,667 | +0.01088 | +0.05735 | 60.09% | 0.1449 |

The exact route was `+2.27` percentage points more often positive than its
sibling, but the sibling had the larger marginal median. Seed and time
controls were more often positive than the exact route.

### Paired comparisons

| Comparator | Median exact-minus-comparator | Cluster mean difference | Bootstrap \(P(\text{exact}>\text{control})\) |
|---|---:|---:|---:|
| Sibling | -0.01122 | +0.01103 | 0.7500 |
| Topology | +0.00162 | +0.03101 | 1.0000 |
| Seed | -0.00465 | +0.01241 | 0.9900 |
| Time | -0.00316 | +0.00491 | 0.8185 |

Event-weighted paired means and equal-stratum cluster means are different
estimands. The frozen protocol required both the paired-median and
cluster-bootstrap gates, so a positive cluster mean could not rescue a failed
paired median.

### Branches

| Branch | Events | Median exact flow | Exact positive fraction |
|---|---:|---:|---:|
| `c2` | 11,584 | +0.01095 | 53.15% |
| `c4` | 4,417 | +0.00485 | 56.98% |

Both medians were positive, but only `c4` cleared `55%`.

## Comparison with Q33B

| Quantity | Q33B random ordering | Q34 greedy ordering | Change |
|---|---:|---:|---:|
| Exact median flow | +0.04143 | +0.00736 | -0.03407 |
| Exact positive fraction | 63.64% | 54.21% | -9.43 pp |

Q34 therefore rejects the claim that the unchanged local
boundary-child-selection rule is invariant to this network-ordering change.

It does **not** reject every possible ARA account of the greedy network. A
post-result possibility is that greedy construction changes the relevant
identity, coupling orientation or boundary definition. That is a new
hypothesis and cannot be used to relabel Q34 as a success.

## Independent validation

The independent validator:

- did not import the primary Q34/Q33B analysis;
- verified all frozen source and cache hashes;
- reconstructed 64 deterministic evaluation events;
- rebuilt 319 available exact/control route transitions from raw density
  matrices in the public HDF5;
- reproduced route selection, normalized flows and starting positions;
- recomputed every eligibility and routing gate;
- reproduced the frozen non-replication verdict.

All 12 validator checks passed.

## Interpretation in ARA and established language

| ARA reading | Established analytical reading |
|---|---|
| The same declared route retains a weak inward tendency. | Exact median flow remains positive in both branches. |
| The route is not identity-invariant across the archive change. | The Q33B effect attenuates substantially under greedy ordering. |
| Nearby children and alternate contexts carry comparable or stronger flow. | Sibling/seed/time controls defeat required paired or frequency gates. |
| The geometry may require a network-identity coordinate. | Any topology-conditioned revision must be newly frozen and tested. |

The result is scientifically useful because it separates a real residual
pattern from a stronger universal claim. Q33B remains a positive
within-archive result; Q34 establishes its present generalization boundary.

## Reproduction

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q34_cross_archive_boundary_child_test.py' run

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q34_validate_cross_archive_boundary_child.py'
```

Primary artifacts:

- `Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_FIDELITY_v1.md`
- `Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_PROTOCOL_v1_FROZEN.md`
- `Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_RESULTS.json`
- `Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_TRIALS.csv`
- `Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_GEOMETRY.png`
- `Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_NOTEBOOK.ipynb`
- `Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_VALIDATION.json`

The source archive, extracted HDF5, derived caches and deterministic gzip event
table are deliberately Git-ignored because of size. They are reproduced by the
checksum-locked runner.
