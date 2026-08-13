# T361B frozen diagnostic — local Di-ARA record versus free restoration

**Frozen:** 12 August 2026, after T361 and before T361B scoring  
**Status:** declared post-result mechanism diagnostic; cannot rescue or rewrite T361

## WHO

The same nine public coupled electrochemical-oscillator records and 40 matched physical pairs per record used by T361.

## WHAT

At every held-out child step, reveal the actual current parent coordinate, current child coordinate, incoming child direction and outgoing visible-parent step. Ask the prefix Di-ARA relation table for exactly one child outgoing step.

Measure:

- next-child-position RMSE on the 0–2 ARA diameter;
- outgoing child-step RMSE;
- outgoing child-direction agreement on non-flat actual steps;
- the same measurements for direction-blind and wrong-lineage relation tables.

Then place these local-read errors beside T361's free-running cycle errors.

## WHEN

Use exactly T361's first-60% prefix relation table and final-40% held-out cycles. Each scored next step is evaluated from the actual held-out state; predicted states are not fed into later T361B lookups.

## WHERE

The lookup remains the frozen T361 feature `(x_A/2, x_B/2, delta x_A/s_A)` with the causal four-state direction label. No new coordinate or fitted constant is introduced.

## WHY

This distinguishes failure to record a local relation from accumulated error when the same relation is recursively used to restore a complete hidden wave.

**Future relation:** if local recording transfers but free restoration fails, future work needs periodic information locks or renewed observed cuts. If local recording itself fails, this Di-ARA relation table is not an adequate physical recorder for that regime.

## HOW

Apply the existing nine-neighbour median movement rule once per actual held-out state. Report results by physical record. No chance accuracy, family classification or outcome-label model enters the diagnostic.

For descriptive orientation only, call a record locally precise when next-position RMSE is at most `0.10` ARA units and direction agreement is at least `0.75`. These thresholds do not alter T361.

