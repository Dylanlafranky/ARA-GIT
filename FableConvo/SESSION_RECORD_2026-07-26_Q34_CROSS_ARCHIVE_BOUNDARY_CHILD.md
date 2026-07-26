# Session Record — Q34 Cross-Archive Boundary-Child Replication

**Date:** 26 July 2026  
**Ledger:** T289  
**Status:** CROSS-ARCHIVE BOUNDARY-CHILD FLOW NOT REPLICATED

## User direction and methodological boundary

After Q33B passed inside the already-open random-ordering simulator, Dylan
agreed to move the exact ARA-first route to a fresh public archive. The
geometry was not to be rewritten around established quantum expectations or
target outcomes.

Dylan also supplied a separate musing:

> Entanglement may connect lattice points across a singularity, with a
> non-closing or irrational relation travelling around the unobserved side
> and reconnecting boundary points. It appears to blink out locally because
> it stops having rational relations with its surroundings.

That idea was recorded in
`THREAD_NOTE_ENTANGLEMENT_DEEP_DIVE_AFTER_QEC_2026-07-26.md`. It was not
included in Q34's features, controls or gates.

## Frozen target

The source was selected and frozen before numerical values were downloaded:

- Akhouri, Shandera and Henry public simulator archive;
- DOI `10.5281/zenodo.16753415`;
- `unnati_submit_12_pure_greedy.hdf5.zip`;
- deposited MD5 `c1cf77ccff486e3786d73ba47f8674f1`.

The target retains Q33B's 12-qubit pure-state family but changes interaction
ordering from random to greedy. Repository search found no earlier numerical
use of this greedy archive.

## Frozen ARA route

The Q33B geometry remained invariant:

\[
2+(1+0.5)=3.5.
\]

The complete child was projected from `1` locally to `0.5` in the parent
frame. This coefficient was not estimated from target energy or closure.

After an eligible high-side source release, the lower-starting endpoint child
was selected from current information only. Its next-slice normalized
determinant-closure flow was the primary outcome.

Source eligibility, development/evaluation partitions, deterministic
one-in-sixteen sample, sibling/topology/seed/time controls, cluster bootstrap
and all gates were copied unchanged from Q33B.

## Result

All eligibility gates passed:

- `16,001` evaluation events;
- `200` branch/seed strata;
- at least `15,085` paired control events.

| Route | Median flow | Mean flow | Positive fraction |
|---|---:|---:|---:|
| Exact boundary child | +0.00736 | +0.03577 | 54.21% |
| Sibling | +0.01461 | +0.02148 | 51.93% |
| Topology | +0.00203 | +0.03008 | 53.48% |
| Seed | +0.00340 | +0.04382 | 57.24% |
| Time | +0.01088 | +0.05735 | 60.09% |

The exact route retained a positive median in both branches:

- `c2`: median `+0.01095`, positive `53.15%`;
- `c4`: median `+0.00485`, positive `56.98%`.

But it missed the frozen `55%` pooled positive-flow floor. Its paired median
advantage was negative against sibling, seed and time. The sibling
cluster-bootstrap probability was `0.750`; time was `0.8185`.

Against Q33B:

- exact median fell from `+0.04143` to `+0.00736`;
- positive fraction fell from `63.64%` to `54.21%`;
- attenuation was `9.43` percentage points.

## Interpretation

The result is not featureless. A weak inward direction survives and the exact
route is `2.27` percentage points more often positive than its sibling.
However, the frozen claim was that the same directed route would retain its
advantage across the archive change. It did not.

Therefore:

- Q33B remains a supported within-source result;
- the unchanged route is not network-ordering invariant;
- Q34 is a clean negative replication;
- a network-identity or coupling-orientation coordinate is a plausible new
  hypothesis only, requiring a newly frozen test;
- Q34 cannot be retroactively rescued by that possibility.

This does not test or reject universal ARA, entanglement, Phase B, hardware
quantum behaviour or the cosmological \(\varphi^{3.5}\) claim.

## Independent validation

The validator did not import the primary analysis. It:

- verified every frozen file and cache hash;
- rebuilt 64 deterministic evaluation events;
- reconstructed 319 available exact/control transitions from raw public
  density matrices;
- reproduced route selection, starting positions and next flows;
- recomputed every eligibility and routing gate;
- reproduced the non-replication verdict.

Validation passed `12/12`.

## Artifacts

- `analysis/quantum/Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_FIDELITY_v1.md`
- `analysis/quantum/Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_PROTOCOL_v1_FROZEN.md`
- `analysis/quantum/q34_cross_archive_boundary_child_test.py`
- `analysis/quantum/Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_RESULTS.json`
- `analysis/quantum/Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_TRIALS.csv`
- `analysis/quantum/Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_GEOMETRY.png`
- `analysis/quantum/Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_REPORT_2026-07-26.md`
- `analysis/quantum/Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_NOTEBOOK.ipynb`
- `analysis/quantum/q34_validate_cross_archive_boundary_child.py`
- `analysis/quantum/Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_VALIDATION.json`

The source archive, extracted HDF5, caches and deterministic gzip event table
are Git-ignored because of size and regenerated by the checksum-locked runner.
