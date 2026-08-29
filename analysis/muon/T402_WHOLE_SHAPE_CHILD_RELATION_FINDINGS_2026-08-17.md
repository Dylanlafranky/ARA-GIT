# T402 — Whole-shape child relation findings

**Executed:** 2026-08-17  
**Protocol hash:** `0ec1547c2e172382b9ab1a94d0297dcff266e7469315872354deec6391b76413`  
**Independent saved-output validation:** PASS

## Answer first

T402 **did not replicate the raw C distribution as a stable two-lobe whole shape**. The lower lobe was stable, but the apparent upper lobe was too weak and inconsistent. The frozen whole-shape gate therefore failed and the registered verdict is:

> **NO STABLE WHOLE SHAPE**

That negative result does not erase the structure noticed in T401. A narrower and cleaner relation did replicate:

> **C-minus-AC forms a stable source-specific axis: C is enriched below the local ARA ridge and depleted above it, with a continuous handover close to the ridge.**

This source-difference result passed both its binned and continuous frozen gates. It is **not** an exact reflected anti-phase pair: the reflected shape, permutation, and source-alignment gates failed.

## What actually replicated

Fresh salts `600–999` produced `326/400` valid calibration-to-holdout transfers (`81.5%`). The same T400 child identity, medium, coordinate, and scoring rule were retained.

The mean C-minus-AC differences across the eight local child bins were:

| local child ARA | mean C−AC |
|---:|---:|
| 0.125 | -0.00581 |
| 0.375 | +0.02661 |
| 0.625 | +0.02463 |
| 0.875 | +0.00722 |
| 1.125 | -0.00432 |
| 1.375 | -0.00583 |
| 1.625 | -0.01036 |
| 1.875 | -0.03215 |

Thus `3/4` lower-half bins were positive and all `4/4` upper-half bins were negative. The split-wise lower mean was positive in `73.62%` of valid partitions; the upper mean was negative in the same `73.62%`. This passes frozen G2.

All four continuous KDE bandwidths passed the registered topology windows:

| bandwidth | positive crest | ridge-nearest crossing | negative trough |
|---:|---:|---:|---:|
| 0.10 | 0.500 | 0.936 | 1.910 |
| 0.15 | 0.550 | 0.974 | 1.910 |
| 0.20 | 0.570 | 1.015 | 1.895 |
| 0.25 | 0.570 | 1.051 | 1.880 |

The source-specific relation therefore has a stable lower crest around `0.50–0.57`, a sign handover around `0.94–1.05`, and a strong upper-end deficit around `1.88–1.91`. This passes frozen G3.

## What did not replicate

### The raw upper lobe is not stable

For the C distribution alone:

- lower-lobe minus saddle mean: `+0.02774`;
- 95% split-resampling interval: `[+0.02238,+0.03306]`;
- lower contrast positive in `74.85%` of valid partitions.

But:

- upper-lobe minus saddle mean: only `+0.00392`;
- 95% split-resampling interval: `[-0.00103,+0.00881]`;
- upper contrast positive in only `55.52%` of valid partitions.

So the broad visual is not two stable C lobes around a saddle. Its strongest reproducible component is the **difference between C and AC**, not the raw C occupancy alone. G1 fails.

### Exact reflected anti-phase is rejected for this cut

The lower C-minus-AC vector does not match the negative reflected upper vector:

- primary reflected cosine: `0.204` against a frozen `0.75` gate;
- exact reverse mapping rank: `19/24`, not top `3`;
- reflected cosine remained only `0.195–0.252` across `6, 8, 10, 12` bins;
- the unshifted C/AC pairing ranked `3/8` among cyclic source shifts;
- a `1.5`-ARA-unit artificial AC shift produced the smallest reflection error.

This means the stable sign-changing source axis is **asymmetric and non-mirror-exact**. It should not be labelled a recovered child anti-phase waveform from T402 alone. G4 and G5 fail.

## ARA interpretation

The visual instinct was partly right but the identity of the shape was initially flattened:

- the **lower crest** is a stable C feature;
- the **upper rise in the raw chart** is not independently stable;
- the cleaner whole relation appears only after keeping C and AC as the two measured source identities and examining their difference;
- that difference crosses near the child ridge, but the two sides do not have equal reflected amplitudes or ordering.

In ARA language, this is evidence for a **source-specific child-rung handover axis with retained asymmetry**, not for a completed, exactly mirrored child Phase A/Phase B pair. The ridge crossing is robust; the proposed exact anti-phase reconstruction is not.

## Scientific boundary

- These are overlapping resampling partitions, so their stability fractions are not independent-experiment probabilities.
- C and AC differ in source/acquisition context. Their difference is diagnostically useful but does not automatically isolate one physical wave.
- Probability closure forces each differential to sum to zero. The evidence is carried by the registered location and topology, not by the mere existence of positive and negative values.
- This remains a population/event-weight relation. It does not directly show an individual neutrino being created.

## Next test implied by T402

The next useful cut should follow the **source-difference handover axis itself**, not search for another raw occupancy hole. Freeze the lower crest (`≈0.50–0.57`), ridge crossing (`≈0.94–1.05`), and upper deficit (`≈1.88–1.91`) on one dataset or partition family, then test whether those three landmarks predict a held-out event-level observable or reproduce in an independent detector/source dataset. The exact reflection hypothesis should remain rejected unless new independent evidence restores it.

## Artifacts

- Frozen protocol: `analysis/muon/T402_WHOLE_SHAPE_CHILD_RELATION_PROTOCOL_2026-08-17.md`
- Machine result: `analysis/muon/T402_whole_shape_child_relation/T402_RESULTS.json`
- Static figure: `analysis/muon/T402_whole_shape_child_relation/T402_WHOLE_SHAPE_CHILD_RELATION.png`
- Portable technical report: `analysis/muon/T402_whole_shape_child_relation/T402_WHOLE_SHAPE_CHILD_RELATION_REPORT.html`
- Independent validation: `analysis/muon/T402_whole_shape_child_relation/T402_VALIDATION.json`
