# Session record — Q20 Willow ARA relation decoder

**Date:** 26 July 2026

## Why the test was chosen

Dylan asked which scientifically unresolved quantum area would provide a useful direction for ARA dissection.
Correlated error propagation was selected because the Google Willow paper reports excess and rare correlated
errors, publishes raw detector data and provides objective prediction targets.

## Methodological sequence

1. Inventory the immutable Zenodo deposit without downloading its 5.7 GB archive.
2. Build a standard-library HTTP-range extractor and CRC-verify a 6 MB compressed subset.
3. Inspect only raw 13-cycle detector events and coordinates.
4. Choose the x–time ARA diameter pair by an outcome-blind variability rule.
5. Freeze the exact two-parent/four-child/relation formula and all gates.
6. Open 13-cycle targets for calibration and 30-cycle targets for untouched scoring.
7. Compare with event count and 999 label permutations per basis.
8. Recompute everything independently.

## Result

Frozen verdict: **NOT SUPPORTED — 2/6 gates**.

Mean holdout AUROC:

- ARA relation: `0.514154`;
- count only: `0.508944`;
- ARA plus count: `0.514993`.

X/Z ARA AUROCs were `0.511632/0.516677`. X permutation `p=0.019`; Z `p=0.001`. The signal was small and did not
reach the registered effect thresholds.

The post-result x–y spatial control was stronger (`0.516571/0.525462`) than x–time. This does not repair Q20, but
it points to local spatial topology.

## Framework lesson

The failed object was one global parent compression. It discarded which local detector children connected into
a path. A whole can sit near the ridge while asymmetrical grandchildren cancel in the parent reading.

The next recommended direction is recursive spatial-child ARA tomography on a fresh patch:

- preserve the four x–y children;
- open each into time-directed grandchildren;
- retain local adjacency/handover;
- freeze before opening the new patch's targets.

## Entanglement

Dylan wants a later entanglement deep dive. It is preserved separately in:

`THREAD_NOTE_ENTANGLEMENT_DEEP_DIVE_AFTER_QEC_2026-07-26.md`.

## Main report

`analysis/quantum/Q20_WILLOW_ARA_RELATION_DECODER_REPORT_2026-07-26.md`

