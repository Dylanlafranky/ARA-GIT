# T350 claim packet v1 — tick-parent versus closure-front

**Frozen:** 11 August 2026, before implementation or scoring  
**Evidence class:** synthetic known-referee causal instrument calibration  
**Originator sign-off:** the user explicitly requested that both interpretations be tested

## Question

When a local ARA state is measured at successive event ticks, is the longer
path/history Di-ARA primarily:

1. a **parent memory** accumulated from the ordered child ticks; or
2. a **pure moving closure front** whose history becomes available only when the
   present relation locks at the handover?

The two readings are not assumed to be globally exclusive. A tick may locate a
closure front even if the history coordinate is a parent compression of prior
ticks. T350 separately tests the strong, discriminating versions.

## Frozen parent-memory prediction

If the history coordinate is the parent of tick-state children, then:

- an invertible sequence of local ARA tick cuts reconstructs the underlying
  path and therefore its history coordinate;
- trajectories with identical endpoints and a long identical final suffix can
  retain distinct history readings because their earlier ordered ticks differ;
- the distinction should become visible before final closure rather than
  appearing only at the last boundary crossing;
- resampling the same continuous path at a different cadence should preserve
  the final history reading within a declared tolerance.

## Frozen pure closure-front prediction

If the history is supplied only by the current closing front, then:

- trajectories with identical present state and identical recent suffix should
  converge to the same history reading;
- the history distinction should remain small before closure and appear mainly
  as a jump at the final handover;
- tick alignment relative to that handover should dominate the apparent
  history result.

## Separate local-front prediction

Regardless of the parent/history verdict, the current state and motion may be a
useful local estimator of distance to the next declared closure. Passing that
check supports the tick as a handover locator, not as the sole source of the
history parent.

## Claim boundary

This test can determine how the frozen ARA instruments relate on controlled
trajectories. It cannot prove which mechanism generates history in an
unmeasured physical system, that every physical identity preserves unlimited
memory, or that a closure front has no top-down influence.

