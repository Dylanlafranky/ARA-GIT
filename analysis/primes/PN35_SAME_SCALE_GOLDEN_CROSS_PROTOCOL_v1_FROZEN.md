# PN35 same-scale golden-cross protocol — v1 FROZEN

**Test ID:** `PN35/SAME-SCALE-GOLDEN-CROSS/v1`  
**Declared:** 22 July 2026, before target cells, candidate labels or outcomes are calculated  
**Fidelity:** `PN35_SAME_SCALE_GOLDEN_CROSS_FIDELITY_PACKET_v1_DRAFT.md`

## Question

When the eight structural wheel children and a non-locking golden handover are placed on the same `0–2` parent
circumference, do primes occur preferentially near their registered crossings, with the direction flipping at the
octave singularity?

## Frozen structure

The structural child lanes are

\[
\mathcal R=\{1,7,11,13,17,19,23,29\},
\qquad x_2(r)=r/15.
\]

They pair under `r <-> 30-r`; each pair sums to parent total `2`. Octave rung `k` is `[2^k,2^(k+1))`. For a complete
wheel cell beginning at multiple `c` of `30`, use `t=(c-2^k)/30`, orientation `sigma_k=(-1)^k`, golden step
`alpha_phi=1/phi^2`, crossing `g=(2*sigma_k*alpha_phi*t) mod 2`, and its anti-phase crossing `(g+1) mod 2`.

The candidate crossing distance is circular distance on circumference `2` from `x_2(r)` to the nearer crossing.
No primality operation is permitted in the primary builder.

## Fresh target rungs

Use three adjacent octave-rung pairs:

| Pair | Lower rung | Upper rung | Approximate scale | Seed |
|---:|---:|---:|---:|---:|
| 1 | `k=26` | `k=27` | `6.7e7 -> 2.7e8` | `35001` |
| 2 | `k=36` | `k=37` | `6.9e10 -> 2.7e11` | `35002` |
| 3 | `k=46` | `k=47` | `7.0e13 -> 2.8e14` | `35003` |

In each rung, sample `4,096` complete global modulo-30 cells without replacement using the fixed pair seed plus the
rung index. Retain all eight structural candidates from every sampled cell. The primary file therefore contains
`196,608` sealed candidate rows across `24,576` cells and six rungs.

## Frozen rivals and controls

Repeat the identical score construction for these rotation steps, without fitting:

| Name | Turn per cell |
|---|---:|
| golden | `1/phi^2` |
| exponential | `1/e` |
| rational 3/8 | `3/8` |
| rational 2/5 | `2/5` |
| 36-degree shear | `1/10` |
| pentagon | `1/5` |
| hexagon | `1/6` |
| quadrant | `1/4` |
| triangle | `1/3` |
| anti-phase | `1/2` |
| silver conjugate | `sqrt(2)-1` |

Also score the golden step without the singularity flip. Use `256` fixed circular shifts of the block-to-phase
alignment within each rung as the order-breaking null. These retain every number, prime label, residue lane and score
distribution while breaking the frozen crossing alignment.

## Metrics

1. **Lane-stratified AUC:** Mann–Whitney prime-versus-composite ordering accumulated within each residue lane, so
   finite residue-class differences cannot create the result.
2. **Nearest-two capture:** fraction of all prime candidates lying in the two closest crossing lanes per cell;
   structural null share is `2/8=25%`.
3. Results for all six rungs, all three adjacent-rung pairs, pooled target, first/second sampled halves and eight
   individual lanes.
4. `1,000` rung-stratified block-bootstrap replicates for the primary AUC, Phi-minus-best-rival AUC and
   flip-minus-no-flip AUC.
5. `256` circular-shift null values and exact plus-one permutation p-values.
6. Score-distance quantiles, prime rates in eight predeclared distance octiles, worked closest/farthest events and
   event geometry around the exact `2 -> 0` rung seam.
7. Deterministic primality validation for every candidate plus independent spot checks and synthetic
   signal/no-signal instrument checks.

## Registered endpoints

All five are required for `SUPPORTED`:

- **G1 — pooled preference:** golden lane-stratified AUC is above `0.5`, its 95% block-bootstrap interval is wholly
  above `0.5`, and its shift-null p-value is at most `0.01`.
- **G2 — scale stability:** all three adjacent-rung pairs have AUC above `0.5`, at least five of six individual rungs
  have AUC above `0.5`, and both fixed sampled halves have AUC above `0.5`.
- **G3 — Phi specificity:** golden AUC exceeds every frozen constant rival and the 95% interval for
  `golden - best rival` is wholly above zero.
- **G4 — singularity flip:** the registered flip model exceeds the no-flip golden model, the 95% interval for the
  difference is wholly above zero, and the flip wins in at least two of three rung pairs.
- **G5 — crossing capture:** nearest-two capture exceeds `25%`, its 95% block-bootstrap interval is wholly above
  `25%`, its shift-null p-value is at most `0.01`, and all three rung pairs exceed `25%`.

`SUGGESTIVE` requires G1 plus G2 but failure of specificity, flip or capture. Adequate data with G1 failed is
`NOT SUPPORTED`. Arithmetic, freeze, reconstruction or instrument failure is `INCONCLUSIVE / IMPLEMENTATION FAILURE`.

## Two-output reporting

The claim verdict and geometry verdict are separate. Regardless of status, report the exact eight-channel anti-pair
closure, full score/label distributions, every rival, singularity-side results and whether prime and composite
geometry are shared. Exact wheel structure cannot rescue a failed Phi prediction.

## Reproducibility order

1. Add ledger registration and freeze this fidelity/protocol pair.
2. Write and hash the primary builder and independent validator.
3. Run the primary builder; hash the label-free candidate file.
4. Only then open primality in the validator.
5. Preserve scripts, manifests, sealed candidates, scored rows, JSON results, notebook, figure and validation receipt.

