# T326–T327 independent Phi circle-train follow-up

**Date:** 2 August 2026  
**Originator of ARA/Phi geometry:** Dylan La Franchi  
**Formalisation, computation and boundary audit:** Codex  
**Joint independent validation:** **PASS, 89/89 checks**

## Answer first

The first two external applications of the frozen T325 Phi circle-train
operator did **not** reproduce its full pattern.

| test | ordered identity | child/local winner | parent winner | order test | specificity | verdict |
|---|---|---|---|---:|---:|---|
| T326 Landrein plants | 196 plants, 7,507 events | `1/e` | `8/21` | `p=0.198080` | broken-lineage `p=0.447855` | **NOT REPLICATED** |
| T326 Cyanella | 130 plants, 684 binned events | not adjudicable | not adjudicable | — | 22.5° bins | **INCONCLUSIVE — RESOLUTION** |
| T327 flume thalweg | 33 slices, one deepest-point path | persistence | persistence | `p=0.550945` | Phi rank `16/41` | **NOT SUPPORTED** |

The exact ridge-centred circle-train derivation remains valid mathematics for
the declared construction. What failed here is the empirical generalisation
that the same fixed Phi increment is the privileged ordered carrier in these
independent physical records.

## Why these tests are stronger than a visual resemblance

Both tests froze the complete ARA operator before endpoint calculation:

1. keep the native ordered identity;
2. map one complete cycle or lateral support to ARA `0..2`;
3. use the fixed Phi increment `2/phi^2`;
4. select one orientation for a complete path, never a favourable sign per
   event;
5. compare with persistence, `1/3`, `1/e`, `3/8`, `8/21`, `2/5`, silver and
   ridge controls;
6. test real order against 10,000 permutations;
7. retain lineage/path controls and Fibonacci-lag return fingerprints;
8. do not smooth, interpolate, Fourier-process or rotate after inspection.

T327's initial protocol contained a pre-endpoint formula/text contradiction
about sign selection. Version 1 was preserved as aborted. Version 2 corrected
only that formula so the sign is fixed once for the whole path; all sources,
candidates, controls and verdict gates remained unchanged.

## T326 — independent plants

### Primary source

Landrein et al. ordered Arabidopsis angular data, Zenodo record
`10.5281/zenodo.20040331`, accompanying paper `10.1093/jxb/eru482`.

The eight genotype/condition cohorts supplied 196 usable plants and 7,507
events. Raw angular positions were also checked against the authors' published
divergence series: all 75 available plant/file comparisons reconstructed with
zero best-direction MAE.

### Frozen findings

- child winner: `1/e`;
- parent winner: `8/21`;
- observed Phi parent-order loss: `0.481923` ARA;
- shuffled median: `0.490311`, 95% interval `0.471005–0.510083`;
- lower-tail order p-value: `0.198080`;
- adjacent compensation ratio: `0.716925`;
- compensation versus within-lineage order shuffle: `p=0.035096`;
- compensation versus broken lineage: `p=0.447855`;
- Fibonacci-return winner: `1/e`.

The compensation result is therefore a short-range ordering property, not
evidence that the proposed carrier is specific to the original plant lineage.

Phi minus `3/8` plant-level bootstrap contrasts did not isolate exact Phi:

- child median difference `+0.002735` ARA, 95% interval approximately
  `0.000000–0.004167` (positive favours `3/8`);
- parent median difference `+0.005722`, 95% interval
  `−0.013242–0.024612`.

### Resolution control

The Cyanella archive (`10.5281/zenodo.14989473`) records 22.5-degree bins.
Exact Phi and `3/8` differ by only 2.508 degrees in this representation, so
the archive is retained as a useful coarse control but cannot decide between
the constants.

## T327 — downstream flume thalweg and controls

### Primary source

Li, Xu, Bai and Lu, Dryad `10.5061/dryad.4xgxd25hg`, accompanying paper
`10.1029/2023JF007387`. The public `Bed-topography.xlsx` workbook contains the
source geometry used here.

The valid uninterrupted bend sequence has 33 cross-sections at
`10,15,...,170 degrees`, each with 41 measured bed points. The minimum bed
elevation in each slice defines the thalweg. Sorting every slice by elevation
creates 40 additional downstream paths with identical order, sample count and
lateral support.

### Frozen findings

- local winner: persistence;
- parent winner: persistence;
- Phi parent loss: `0.471736` ARA;
- shuffled-order median: `0.464910`, 95% interval
  `0.354235–0.566365`;
- lower-tail order p-value: `0.550945`;
- reversed-order loss: `0.444687`;
- thalweg Phi rank among 41 paths: `16/41`;
- control-path Phi median: `0.480439`;
- return-profile winner: `3/8`;
- free diagnostic increment: `0.0184`, close to persistence rather than Phi.

The median raw lateral neighbour spacing was `0.022067` ARA. Phi and `8/21`
differ by only `0.002027` in one step, but their phase separation exceeds the
raw grain at horizon 13 and remains separated at horizon 21. Exact one-step
constant identification is unresolved; the failed ordered parent path is not.

## What changes, and what does not

### Retained

- the exact mathematics of the declared ridge-centred Phi circle train;
- T325 as an observed within-source child/parent scale split;
- `3/8` as a useful nearby finite-grid candidate;
- the ARA-first method of separating local children, cumulative parents,
  source order and lineage/path specificity.

### Not currently supported

- that `2/phi^2` is a universal ordered physical handover increment;
- that the T325 `3/8` child / Phi parent split generalises across plant data;
- that a physical thalweg is privileged by the frozen Phi carrier;
- that Fibonacci-return agreement alone identifies Phi.

### Next scientific requirement

A future positive claim needs a new, independently timestamped dataset where
event order, lineage, ARA support, direction, and resolution are genuinely
measured. The operator should remain frozen. Retuning it to the `1/e`, `8/21`,
`3/8`, or persistence winners observed here would define a new hypothesis,
not rescue T325.

## Reproduction files

- `T326_PHI_CIRCLE_TRAIN_INDEPENDENT_PLANTS_PROTOCOL_v1_FROZEN.md`
- `t326_phi_circle_train_independent_plants.py`
- `T326_PHI_CIRCLE_TRAIN_INDEPENDENT_PLANTS_RESULTS.json`
- `../hydraulics/T327_PHI_CIRCLE_TRAIN_THALWEG_PROTOCOL_v2_FROZEN.md`
- `../hydraulics/t327_phi_circle_train_thalweg.py`
- `../hydraulics/T327_PHI_CIRCLE_TRAIN_THALWEG_RESULTS.json`
- `validate_t326_t327_phi_circle_train.py`
- `T326_T327_PHI_CIRCLE_TRAIN_VALIDATION.json`
