# Q20 Willow ARA relation-decoder report

**Date:** 26 July 2026  
**Claim:** `Q20-WILLOW-ARA-RELATION-v1`  
**Frozen verdict:** **NOT SUPPORTED — 2/6 gates passed**  
**Independent validation:** **PASS**

## Plain-language result

Q20 asked whether one complete detector cloud could be compressed into:

1. its position on a physical x diameter;
2. its position on a time diameter;
3. the aligned-versus-crossed relation of those two parents;

and still predict the logical-observable flip in a longer, untouched experiment.

The answer is **no, not sufficiently**. The three ARA coordinates contained a small repeatable signal above the
number of detector events, but they were only slightly better than chance and did not pass the frozen prediction
gates.

This rejects the sufficiency of the **single global x–time ARA compression** for this endpoint. It does not reject
the wider ARA framework or the use of recursively decompressed local ARA geometry.

## Frozen ARA object

For every raw detector event, the physical x and cycle/time coordinates were each treated as a `0–2` diameter.
Their gradient mixing produced four Tier-3 children:

\[
C_{AA},\quad C_{AB},\quad C_{BA},\quad C_{BB}.
\]

The three parent/relation coordinates were:

\[
X=2(C_{BA}+C_{BB}),\qquad
T=2(C_{AB}+C_{BB}),\qquad
J=2(C_{AB}+C_{BA}).
\]

The x–time pair was selected before opening any target bit. It had the largest outcome-blind relation variation
on the 13-cycle development records. The prediction direction was then calibrated on those 13-cycle targets and
applied unchanged to 30-cycle holdout records.

Total event fill was kept separate as a control.

## Holdout results

### By basis

| Basis | Model | AUROC | Balanced accuracy | Accuracy | Permutation p |
|---|---|---:|---:|---:|---:|
| X | ARA relation | 0.511632 | 0.505283 | 0.506400 | 0.019 |
| X | count only | 0.505112 | 0.502749 | 0.501200 | — |
| X | ARA + count | 0.510814 | 0.505879 | 0.505100 | — |
| Z | ARA relation | 0.516677 | 0.508732 | 0.514380 | 0.001 |
| Z | count only | 0.512776 | 0.508601 | 0.507020 | — |
| Z | ARA + count | 0.519171 | 0.510728 | 0.513320 | — |

### Equal-basis averages

| Model | AUROC | Balanced accuracy | Accuracy |
|---|---:|---:|---:|
| ARA relation | 0.514154 | 0.507007 | 0.510390 |
| count only | 0.508944 | 0.505675 | 0.504110 |
| ARA + count | 0.514993 | 0.508304 | 0.509210 |

The mean ARA relation advantage over event count was:

\[
0.514154-0.508944=0.005210.
\]

That is real enough to inspect but less than the frozen `0.01` improvement gate and far below useful decoding
performance.

## Frozen gates

| Gate | Result |
|---|---|
| source and construction integrity | PASS |
| ARA AUROC at least 0.55 in both bases | FAIL |
| mean ARA minus count AUROC at least 0.01 | FAIL |
| permutation p at most 0.01 in both bases | FAIL — X was 0.019 |
| mean ARA+count minus count AUROC at least 0.01 | FAIL |
| ARA+count no more than 0.01 worse than count in either basis | PASS |

Verdict: **NOT SUPPORTED**.

## Important secondary observation

The outcome-blind selection rule chose x–time because that pair moved most strongly in raw development. After the
primary result was saved, the two registered secondary cuts were scored:

| Basis | x–y AUROC | y–time AUROC | primary x–time AUROC |
|---|---:|---:|---:|
| X | **0.516571** | 0.512952 | 0.511632 |
| Z | **0.525462** | 0.514912 | 0.516677 |

The spatial x–y cut carried more outcome information than the more dynamically variable x–time cut. This is
post-result and cannot repair Q20. It supplies a concrete direction for a new test.

In ARA language: the loudest moving relation was not the relation that best distinguished the parent outcome.
The missing information appears more spatially local.

## Scientific interpretation

A logical observable flip is not determined by the average location of the detector cloud. The arrangement of
local events matters. Opposing local paths can produce nearly the same global `1.0` parent reading while carrying
different topology underneath.

That is also an ARA-consistent failure mode: Q20 measured the parent whole and allowed its children to cancel
inside one compressed coordinate. It did not preserve which neighbouring children connected into a path.

The appropriate next step is therefore not to tune this failed global score. It is to decompress the detector
cloud one rung further.

## Recommended Q21 direction

**Recursive spatial-child ARA tomography**

1. Treat x and y as the two parent diameters for the spatial detector sphere.
2. Preserve the first four children separately rather than immediately recombining them into three global
   coordinates.
3. Decompress each spatial child into local time-directed grandchildren.
4. Preserve which local children touch or hand over across time.
5. Freeze that construction before extracting targets from a different distance-5 patch.
6. Compare against event count, the failed Q20 global compression and coordinate/label controls.

The question for Dylan's geometry is now precise:

> When a whole detector cloud reads near the ridge, which local child-to-child connections distinguish a harmless
> cancellation from a path that changes the parent observable?

That is the valley Q20 exposed. It is not asking for another global landmark; it is asking which local cuts must
remain uncompressed.

## Boundaries

- Q20 did not test a full established decoder.
- It did not isolate the rare approximately hourly Willow error bursts.
- It used one patch from one public deposit.
- The secondary x–y result is post-result guidance, not a new frozen success.
- No conclusion about entanglement follows from Q20.

## Reproduction and evidence

- source DOI: <https://doi.org/10.5281/zenodo.13273331>
- dataset audit: `Q20_WILLOW_ARA_DATASET_AUDIT_2026-07-26.md`
- fidelity: `Q20_WILLOW_ARA_RELATION_DECODER_FIDELITY_v1.md`
- frozen protocol: `Q20_WILLOW_ARA_RELATION_DECODER_PROTOCOL_v1_FROZEN.md`
- frozen protocol SHA-256:
  `3a55824116968450d43f64770933059c4ce00b0a873a7302b417111986118d6f`
- results: `Q20_WILLOW_ARA_RELATION_DECODER_RESULTS.json`
- metrics: `Q20_WILLOW_ARA_RELATION_DECODER_METRICS.csv`
- controls: `Q20_WILLOW_ARA_RELATION_DECODER_CONTROLS.csv`
- bounded projections: `Q20_WILLOW_ARA_RELATION_DECODER_PROJECTIONS.csv`
- independent validation: `Q20_WILLOW_ARA_RELATION_DECODER_VALIDATION.json`

The independent validator re-parsed the raw b8 members, reconstructed the ARA coordinates, refitted all three
models, reran all 1,998 permutations and reproduced every central metric and p-value exactly.

