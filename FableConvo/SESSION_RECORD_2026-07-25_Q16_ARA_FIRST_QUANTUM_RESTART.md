# Session Record — Q16 ARA-First Quantum Restart

**Date:** 25 July 2026  
**Reason for restart:** established quantum summaries had begun to determine the proposed ARA geometry, reversing
the intended test order.

## Dylan's methodological correction

ARA is the object under test. Established quantum mechanics can provide source facts, controls and a post-result
translation, but must not overwrite the declared ARA sphere before the ARA-native test is run.

The corrected order is:

\[
\text{ARA geometry}
\rightarrow
\text{raw-data coordinate}
\rightarrow
\text{frozen prediction}
\rightarrow
\text{result}
\rightarrow
\text{standard-physics comparison}.
\]

## Geometry tested

Two complete ARA parents, each with its own Phase A/Phase B pair and TE-ARA closure, produce four ordered children:

\[
(A_1,B_1)\times(A_2,B_2)
\rightarrow
\{C_{00},C_{01},C_{10},C_{11}\}.
\]

The test retained the relation between the parents rather than flattening the four children into three visible
states plus an unspecified remainder.

## Result

The public raw-current data supported all eight frozen gates:

- parent-direction holdout cosines: `0.877841` and `0.829311`;
- parent bit accuracies: `0.981250` and `0.906250`;
- four-child accuracy: `0.887500`, versus shuffle 99th `0.487625`;
- pseudo-child false-positive rate: `0/1000`;
- retained relation cosine: `0.818388`;
- retained relation share: `0.239840`, \(p=0.0001\);
- stable centered-rank-3/tetrahedral geometry across the acquisition-index split.

The first raw segment, discarded in earlier processing, contained `6.79%` of total contrast energy and was not
empty.

## Interpretation

ARA-first geometry found two stable parent directions plus a third stable relation direction. Only after scoring,
the conventional labels showed those three directions concentrate on the familiar three Bell correlation axes.
This is a strong ARA crosswalk and Information³ example, but it is not yet new quantum physics or independent
proof of universal fractality.

The major remaining confound is that the four preparations were stored in separate archives/runs. Independent
replication should use interleaved preparations, common hardware conditions, per-shot timestamps and untouched
device/run holdout data.

## Method correction carried forward

Q15's `self + Other = 2` is retained as a participation/coherence proxy, not a complete TE-ARA decomposition.
Phase A and Phase B remain mandatory for a true identity account:

\[
\mathrm{Phase\ A}+\mathrm{Phase\ B}+\sum\mathrm{Other}=2.
\]

Full report:
`analysis/quantum/Q16_ARA2_RAW_FOUR_CHILD_REPORT_2026-07-25.md`.

