# Q41 cadence-defined strand reversal report

Date: 2026-07-27 (Australia/Brisbane)

Verdict: **INCONCLUSIVE — PREDECLARED ADEQUACY FAILURE**

## Plain-language result

Q41 did not get far enough to test whether the 7.5/15 clock selects the
relation-reversal strand.

The untouched `random` ordering archive was physically valid, but its visible
closure paths did not rotate coherently enough to enter the frozen ARA
four-quadrant test. All 6,600 lineages failed the predeclared direction
coherence threshold. There were therefore no eligible development cycles, no
eligible evaluation cycles and no two-turn Ba cycles.

Crucially, the pipeline stopped before prediction or target reveal. No fourth
connected identity was read, no result was fitted and the Q41 operator remains
available for a proper structured transfer test.

## What was frozen before target access

- ARA fidelity packet:
  `Q41_CADENCE_STRAND_REVERSAL_FIDELITY_v1.md`
- Prospective protocol:
  `Q41_CADENCE_STRAND_REVERSAL_PROTOCOL_v1_PRETARGET_FROZEN.md`
- Target lock:
  `Q41_TARGET_LOCK_v1_FROZEN.md`
- Target archive:
  `unnati_submit_12_inhomo_v1_random.hdf5.zip`
- Deposited and verified MD5:
  `f342ff3dda39915da3332db65cc7c2c8`

The added rule was unchanged from the Q40C diagnosis: preserve the Q40 visible
flag and additionally reverse in the two-turn 7.5-sample family when the
target quadrant is Ba.

## Pre-reveal inventory

| Quantity | Result |
|---|---:|
| Closure lineages with calculable coordinates | 6,600 |
| Direction coherence at least 0.80 | 0 |
| Minimum direction coherence | 0.0081 |
| Median direction coherence | 0.3548 |
| Maximum direction coherence | 0.6356 |
| Eligible development cycles | 0 |
| Eligible evaluation cycles | 0 |
| Prediction artifact written | No |
| Fourth connected identity revealed | No |

The data-quality checks themselves passed:

- closure shape: `100 × 500 × 66`;
- connected-correlation shape: `100 × 500 × 66 × 3 × 3`;
- maximum sampled trace error: `4.05e-5`;
- maximum Hermiticity error: `0`;
- minimum sampled density-matrix eigenvalue: `0.00235`; and
- all derived values finite.

## ARA interpretation

The random-order condition does not preserve the coherent parent orbit needed
to assign the already defined four-quadrant sequence. In ARA language, the
local path is too directionally mixed at this grain to identify a completed
7.5/15 seam. This does **not** show that the strand rule is wrong; it shows
that the selected archive cannot instantiate the registered coordinate.

The result is still informative: the near-perfect lag-15 recurrence observed
in Q40 is not a generic consequence of every archive in the source family. It
depends strongly on structured ordering.

## Next registered step

Q41B transfers the identical operator and gates to the still-untouched
inhomogeneous-v1 `landmax` archive. The Q41B protocol and target lock were
written before that archive was downloaded:

- `Q41B_CADENCE_STRAND_REVERSAL_PROTOCOL_v1_PRETARGET_FROZEN.md`
- `Q41B_TARGET_LOCK_v1_FROZEN.md`

Q41 remains frozen as an inconclusive adequacy failure regardless of the Q41B
outcome.

