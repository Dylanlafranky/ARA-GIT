# Q34 Fidelity Packet — Cross-Archive Boundary-Child Replication

**Registered:** 26 July 2026, before downloading or opening the target archive
**Ledger:** T289
**Source family:** Akhouri, Shandera and Henry public quantum-network simulator
**Target archive:** `unnati_submit_12_pure_greedy.hdf5.zip`
**Target archive MD5:** `c1cf77ccff486e3786d73ba47f8674f1`

## Purpose

Q33B supported an ARA-first boundary-child closure-flow route on the
`12_pure_random` archive. Q34 asks whether the identical rule survives when
the network identity changes from random to greedy connectivity while qubit
count and pure initial-condition family remain fixed.

This is a cross-archive replication, not a new geometry search.

## What remains frozen from Q33B

The ARA route remains

\[
\underbrace{2}_{\text{complete same-rung span}}
+
\left(
\underbrace{1}_{\text{current-rung contribution}}
+
\underbrace{\frac12}_{\text{single boundary child one octave up}}
\right)
=3.5.
\]

- `0.5` is structural and is never estimated from energy.
- The source releases from the high/`2` side.
- Of the two exact endpoint children, the lower starting normalized closure
  coordinate is the boundary child.
- The next-slice normalized determinant-closure movement is the primary flow
  outcome.
- Sibling, topology, seed and time controls all use the same lower-of-two
  selection.
- Development/evaluation partitions, deterministic sampling, shifts,
  bootstrap procedure and every numerical gate remain unchanged.

## Why `pure_greedy` was selected

The archive was selected using metadata only:

- same `12`-qubit scale as Q33B;
- same pure initial-condition family;
- different deposited network ordering/connectivity identity;
- complete archive publicly listed before selection;
- no target numerical density-matrix, connectivity or outcome value had been
  opened in this project before registration.

This isolates network-identity generalization more cleanly than simultaneously
changing qubit count or initial-state family.

## Source lock

- DOI: `10.5281/zenodo.16753415`
- archive: `unnati_submit_12_pure_greedy.hdf5.zip`
- deposited MD5: `c1cf77ccff486e3786d73ba47f8674f1`
- listed compressed size: approximately `224.2 MB`
- target branches: deposited `c2` and `c4` two-local connectivity branches
- target seeds: all deposited seeds `0..99`
- target times: all deposited times `0..499`

Archive structure may be inspected after registration solely to locate the
deposited branch/seed/order paths. No outcome-dependent eligibility or metric
change is allowed.

## Evidence tiers

Q34 can support:

1. cross-archive replication of the directed boundary-child closure-flow
   consequence inside the simulator family;
2. stability across a changed connectivity rule.

Q34 cannot establish:

- hardware quantum behavior;
- a universal singularity;
- entanglement;
- Phase B;
- literal energy conservation;
- the cosmological \(\varphi^{3.5}\) ratio;
- a numerical derivation of the fixed `3.5` coordinate.

## Separation from the entanglement musing

Dylan's same-day idea that entanglement could be an out-of-cut relation across
a singularity boundary was recorded separately. It supplies no Q34 feature,
gate, control or interpretation. Q34 tests only the already-frozen Q33B
boundary-child flow rule.
