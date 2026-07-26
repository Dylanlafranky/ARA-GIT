# Q21 Willow recursive child topology beneath the parent ridge

**Recorded:** 26 July 2026  
**Claim:** `Q21-WILLOW-RECURSIVE-CHILD-TOPOLOGY-v1`  
**Frozen verdict:** **NOT SUPPORTED — 2/8 gates passed**  
**Validation:** **PASS — 95/95 checks**

## Answer first

Q21 confirmed the geometric premise that motivated the test: when all local
detector children are recompressed, the parent coordinates sit close to the
`1.0` ridge even though the children retain substantial local variation.

The registered twenty-four-coordinate child construction did **not**, however,
predict untouched logical outcomes well enough across detector patches. It
produced mean holdout AUROC `0.512172`, below the `0.55` gate and slightly below
the recompressed spatial parent (`0.513420`).

This rejects the sufficiency of:

> eight child/time grandchildren plus sixteen aggregate adjacent-time
> child-to-child handovers, fitted on `q4_7/r13` and transported unchanged to
> `q6_5/r30`.

It does not reject the parent-ridge rule or the full ARA framework.

## The ARA correction tested

The governing correction supplied before the fresh outcomes were opened was:

> Averaging the entire detector sphere can let local child asymmetries cancel
> at the parent `1.0` ridge. This is the same whole-versus-children effect seen
> heavily in the LLM work.

Q21 therefore did not demand a non-ridge parent. It retained:

- four soft spatial children: `AA, AB, BB, BA`;
- two time grandchildren inside each spatial child;
- all sixteen directed handovers between spatial children on consecutive
  non-empty time slices.

The eight grandchildren sum to one TE-ARA `2`. The sixteen handover
allocations separately sum to one relational TE-ARA `2`.

## Outcome-blind parent check

Before extracting any fresh-patch target:

| Patch/basis | Parent x | Parent y | Parent relation |
|---|---:|---:|---:|
| q4_7/r13 X | 1.04930 | 1.00218 | 1.01146 |
| q4_7/r13 Z | 1.04008 | 1.01719 | 1.01857 |
| q6_5/r30 X | 1.03620 | 0.99660 | 1.01271 |
| q6_5/r30 Z | 1.03803 | 1.01458 | 1.00846 |

The parent closure is real in this construction. It is a coarse-grained
reading, not evidence that every child is locally balanced.

## Frozen prospective boundary

- development: `d5_at_q4_7/r13`, already opened during Q20;
- holdout: untouched `d5_at_q6_5/r30`;
- bases: X and Z, fitted separately;
- records: 50,000 per basis and split;
- protocol frozen before the two `q6_5` outcome members were extracted;
- protocol SHA-256:
  `bd26fa2e70c1e4ddbb4e5d768b6099cb6caaea3c96ab1ce3cac545d6575cd24d`.

Every model used the same frozen equal-prior nearest-centroid rule.

## Holdout results

### Equal-basis mean

| Model | AUROC |
|---|---:|
| child topology: 8 grandchildren + 16 handovers | 0.512172 |
| grandchildren only | 0.512371 |
| recompressed spatial parent | **0.513420** |
| Q20-style global x–time parent | 0.506218 |
| event count only | 0.506055 |
| topology plus event count | 0.512532 |
| spatially misassigned topology | 0.503705 |

### By basis

| Model | X AUROC | Z AUROC |
|---|---:|---:|
| child topology | 0.507656 | 0.516688 |
| grandchildren only | 0.507030 | 0.517712 |
| recompressed spatial parent | 0.506324 | **0.520516** |
| Q20 global x–time | 0.501032 | 0.511405 |
| event count | 0.502493 | 0.509617 |
| topology plus count | 0.507746 | 0.517318 |
| spatially misassigned topology | 0.495648 | 0.511761 |

Permutation p-values for the primary child topology were:

- X: `0.126`;
- Z: `0.006`.

Z therefore contains a development-oriented relation that survives the fresh
patch better than random development-label directions. X does not. Because
the claim required both bases and a material advantage over controls, the
Z-only result cannot support Q21.

## Frozen AUROC differences

| Comparison | Mean difference | Required |
|---|---:|---:|
| child topology − spatial parent | -0.001248 | ≥ +0.010 |
| child topology − Q20 global x–time | +0.005954 | ≥ +0.010 |
| topology plus count − count | +0.006477 | ≥ +0.010 |
| child topology − spatial shuffle | +0.008467 | ≥ +0.010 |
| full topology − grandchildren only | -0.000199 | no gate |

The local coordinate assignment matters descriptively: scrambling it removed
most of the small signal. The registered effect nevertheless missed its
minimum size, and the handover block added no mean holdout benefit beyond the
grandchildren.

## Gates

Passed:

1. construction and source integrity;
2. adding topology was not more than `0.01` worse than count in either basis.

Failed:

1. AUROC at least `0.55` in both bases;
2. mean child-topology gain over the spatial parent at least `0.01`;
3. mean gain over Q20 global x–time at least `0.01`;
4. permutation `p<=0.01` in both bases;
5. topology-plus-count gain over count at least `0.01`;
6. gain over spatially misassigned topology at least `0.01`.

Verdict: **NOT SUPPORTED**.

## What the children were doing

This section is post-result diagnostic guidance, not a frozen success.

The fitted directions were organized around opposite spatial children:

- X was led by positive `AB_A/AB_B` against negative `BA_A/BA_B`;
- Z was led by positive `AA_A/AA_B` against negative `BB_A/BB_B`;
- Z handovers were similarly led by `AA→AA` against `BB→BB`.

That is recognizably quadrant-like, but the exact orientation was not stable
enough across patches to make a useful prediction.

The transport loss was large:

| Basis | Development topology AUROC | Fresh holdout AUROC |
|---|---:|---:|
| X | 0.553064 | 0.507656 |
| Z | 0.582540 | 0.516688 |

The recompressed Z spatial parent fell from `0.610744` to `0.520516`. The main
failure is therefore not simply insufficient dimensionality. It is failure of
the learned orientation to transport across patch and duration.

## ARA interpretation

The test separates three statements:

1. **Parent ridge closure:** supported inside the registered construction.
   Local asymmetries can recompress near the parent `1.0`.
2. **Local spatial information exists:** weakly suggested. Registered geometry
   beat its misassigned-coordinate control by `0.008467`, but below the frozen
   effect gate.
3. **This local decomposition predicts across patches:** not supported.

The failed handover block is important. Multiplying aggregate child shares at
adjacent time slices is not yet the same as preserving an actual local path.
Several unrelated detector events can occupy the same children and create the
same aggregate handover. Q21 retained more coordinates, but it did not retain
which individual detector relation continued.

## Corrected next discrimination: the omitted vertical wave

After the frozen result, Dylan identified a more precise omission.

Q21 opened Tier 4 and retained sideways Tier-3 child handovers, but did not
calculate the cross-scale ARA wave between the Tier-4 grandchildren and the
Tier-1 whole/meta relation.

The hierarchy used here is:

| Tier | Q21 identity |
|---|---|
| 1 | whole/meta relation \(J\) |
| 2 | parent diameters \(X,Y\) |
| 3 | spatial children \(AA,AB,BB,BA\) |
| 4 | each spatial child's time A/B grandchildren |

Thus Q21 separated the levels but omitted their vertical coupling. That is a
cleaner candidate explanation for why the Tier-1 spatial parent generalized
slightly better than the isolated Tier-4 coordinates.

The corrected Q22 direction is:

1. define the native ARA relation from every local Tier-4 time-wave coordinate
   back to Tier-1 \(J\);
2. preserve both orientation and the reflected `2-x` counterpart;
3. freeze the cross-rung construction without fresh outcomes;
4. use untouched patch `d5_at_q6_9`, fitting its r13 records and scoring r30;
5. compare vertical Tier4↔Tier1 ARA with Tier 1 alone, Tier 4 alone, Q21
   topology, event count and cross-rung shuffles.

This tests the proposed wave **between scales**, rather than simply adding more
detail within the lower scale.

## Reproduction

From `analysis/quantum`, using Python with NumPy:

```powershell
python q21_zenodo_range_extract.py --stage geometry
python q21_willow_child_topology_calibrate.py
```

Verify the frozen protocol hash, then:

```powershell
python q21_zenodo_range_extract.py --stage outcomes
python q21_willow_recursive_child_topology_test.py
python q21_willow_recursive_child_topology_validate.py
```

The source subsets are ignored by Git. Every extracted member is CRC-checked
against the immutable ZIP central directory.

## Evidence files

- fidelity packet:
  `Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_FIDELITY_v1.md`;
- frozen protocol:
  `Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_PROTOCOL_v1_FROZEN.md`;
- outcome-blind calibration:
  `Q21_WILLOW_CHILD_TOPOLOGY_CALIBRATION.json`;
- result:
  `Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_RESULTS.json`;
- metrics:
  `Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_METRICS.csv`;
- controls:
  `Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_CONTROLS.csv`;
- bounded projections:
  `Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_PROJECTIONS.csv`;
- independent validation:
  `Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_VALIDATION.json`.

The validator independently re-parsed the raw source, reconstructed all
registered coordinates, refitted all seven models, reran all `1,998`
permutations and passed `95/95` comparisons.
