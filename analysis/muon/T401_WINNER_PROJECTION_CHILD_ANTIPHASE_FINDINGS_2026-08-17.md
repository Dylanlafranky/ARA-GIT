# T401 — winner projection and candidate child anti-phase

**Frozen protocol:** `T401_WINNER_PROJECTION_CHILD_ANTIPHASE_PROTOCOL_2026-08-17.md`  
**Protocol SHA-256:** `0246a7bbc9c55f41e26cdd899f58e97918ae38769e279b8c081428c62e56410b`  
**Verdict:** **NO STABLE MISSING-WINNER BAND**

## Plain-language result

The apparent hole in T400 was a hole in the **winner-only picture**, not a hole in the child distribution.

T400 showed only one value per split: whichever ARA bin contained the most delayed-event weight. With only twenty splits, no winning value happened to land between `1.25` and `1.50`. T401 retained the complete distribution and expanded the check to 200 deterministic partitions. Of those, 164 formed a valid ordered child window.

The candidate band centred at `1.375` was neither empty nor unusually weak:

- mean C occupancy: `0.118614`, or `11.86%` of each split's delayed weight;
- occupancy relative to its two neighbours: `0.99106`, effectively equal;
- binned winner: `13/164 = 7.93%` of valid splits;
- continuous KDE winner: `17/164 = 10.37%` of valid splits;
- volatility relative to the median bin: `1.02934`, an intermediate rather than quiet or turbulent value.

The proposed survivor-bias warning was therefore useful: the first graph really did discard most of the information. But the stronger interpretation—an indirectly exposed child Phase B in that specific band—is not supported by this cut.

## What the null says

A sampling-only winner model based on the pooled full distribution predicted that the `1.375` bin would win `7.50%` of valid splits. The observed rate was `7.93%`; the two-sided binomial comparison was `p = 0.76727`.

So the enlarged result is exactly ordinary for the measured distribution. The chance of receiving **zero** such winners across 164 valid splits would have been only `2.79e-6`; T400's zero was a small-20-split projection accident that disappeared when the resampling field was widened.

## The reflected anti-phase test

The exact ARA reflection (x\mapsto2-x) was compared with all 24 possible lower-to-upper bin pairings after a centred-log-ratio transform removed the trivial constant-sum relation.

For beam-coincident C records:

- reflected exchange score: `0.04670` against the frozen `0.20` gate;
- negative reflected relations: `2/4`, rather than at least `3/4`;
- exact reflection rank: `13/24`, rather than top `3`.

For the AC control, the score was `-0.05055` and the exact mapping ranked `2/24`; its high rank does not indicate reflected exchange because the score has the wrong sign. The C-minus-AC score difference was `0.09726`, just below the frozen `0.10` gate, and the C reflection ranked worse. The missing-band anti-phase interpretation therefore failed independently of the occupancy result.

## Frozen gates

| Gate | Result | Reason |
|---|---:|---|
| G1 occupied but non-dominant | FAIL | Occupied, but it won `7.93%`, above the `1%` missing-winner ceiling. |
| G2 continuous gap persists | FAIL | KDE modes entered the band in `10.37%`, above the `5%` ceiling. |
| G3 beyond sampling/argmax null | FAIL | The observed winner count was ordinary under the null (`p=0.76727`). |
| G4 reflected exchange | FAIL | Score `0.04670`, only `2/4` negative pairs, rank `13/24`. |
| G5 C exceeds AC | FAIL | Score advantage `0.09726` and poorer reflection rank. |

All frozen scientific gates failed. Independent saved-output validation passed every integrity and arithmetic check.

## Execution boundary

Thirty-six of 200 calibration partitions did not form an ordered (L<\text{crest}<R) child interval. That is retained as a result. The occupancy, mode and null calculations use the 164 valid transfers. These heavily overlapping partitions measure resampling stability, not 164 independent physical experiments.

## ARA interpretation

The result does **not** say the delayed identity has no anti-phase. It says this particular visual absence cannot be used to locate it.

The full child distribution is broadly occupied across `0–2`; the apparent null arose only after compressing each distribution to its single largest bin. In ARA terms, T401 prevents a projection artifact from being promoted into a new child identity. A genuine hidden or perpendicular child should survive the full-distribution view, continuous-mode view, reflection test and a source-level control. This candidate did not.

The clean next step is not more winner-bin analysis on the same coarse timing archive. It is an event-linked or finer-time source containing an independently observed parent phase and daughter relation, where an anti-phase can be reconstructed before the target handover is revealed.

## Records

- `T401_winner_projection_child_antiphase/T401_RESULTS.json`
- `T401_winner_projection_child_antiphase/T401_VALIDATION.json`
- `T401_winner_projection_child_antiphase/T401_SPLIT_BIN_DISTRIBUTIONS.csv`
- `T401_winner_projection_child_antiphase/T401_SPLIT_MODES.csv`
- `T401_winner_projection_child_antiphase/T401_BIN_SUMMARY.csv`
- `T401_winner_projection_child_antiphase/T401_MIRROR_RELATIONS.csv`
- `T401_winner_projection_child_antiphase/T401_ALL_PAIRING_SCORES.csv`
- `T401_winner_projection_child_antiphase/T401_SAMPLING_NULL.csv`
- `T401_winner_projection_child_antiphase/T401_WINNER_PROJECTION_CHILD_ANTIPHASE.png`
