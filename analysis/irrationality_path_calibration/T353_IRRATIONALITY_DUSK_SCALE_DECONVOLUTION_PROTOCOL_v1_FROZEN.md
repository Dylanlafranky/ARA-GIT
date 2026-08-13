# T353 frozen protocol v1 — Irrationality dusk scale deconvolution

**Frozen:** 11 August 2026, after T352 and before T353 implementation/scoring  
**Evidence class:** synthetic known-referee multiscale follow-up  
**Reason for follow-up:** T352 resolved a finite coordinate excursion but could
not separate its excess-area magnitude from abrupt sliding-window smear.

## Question

Is the apparent Irrationality Di-ARA dusk only the width of the measuring
window, or does it contain a recoverable transition duration of its own?

## WHO

New circle paths use rational denominators `q={11,18,22}`, irrational advances
from `d={31,37,41}`, transition durations `{320,448,576,704}`, 12 new initial
states and both irrational→rational and rational→irrational directions. These
parameters and seeds were not used by T352.

Each matched identity has:

- an ordered linear handover between endpoint advances;
- an abrupt switch at the same centre with the same stable endpoints.

## WHAT

Retain the frozen T348/T352 stochastic-residual coordinate `x_R` in windows of
`W={128,256,384,512}` states, all advanced by a common 32-state stride.

For each `identity × mode × W`, define the stable baseline

\[
b_R=\max(\widetilde x_{R,pre},\widetilde x_{R,post}).
\]

Inside the transition neighbourhood, the observed band width `B(W)` is the
length of the longest chronological run satisfying

\[
x_R\ge b_R+0.25.
\]

For each identity, the abrupt control estimates window smear. The candidate
deconvolved duration is

\[
\widehat T=operatorname{median}_W
\left[B_{ordered}(W)-B_{abrupt}(W)\right].
\]

No fitted multiplier converts this value into the declared duration.

## WHEN, WHERE AND WHY

Paths contain 4096 states and switch at state 2048. Stable pre/post regions are
windows lying wholly outside the declared transition interval. The test is on
the local Irrationality Di-ARA rung; cumulative parent history is outside scope.

Varying `W` changes the observer while holding the underlying event fixed. If
the band is only measurement smear, its width should scale with `W` and the
matched subtraction should approach zero. If a finite ordered handover is
resolved, the subtraction should retain positive duration information across
windows and directions.

## Frozen gates

All intervals use 5,000 matched-identity bootstraps with seed `35320260811`.

1. **M1 stable endpoints:** median stable `x_R<0.75` in every
   `direction × mode × W` group.
2. **M2 abrupt-smear calibration:** within each direction, the median absolute
   intercept from `B_abrupt(W)=a+bW` is at most 64 states and median `R²>=0.75`.
3. **M3 positive deconvolved duration:** in both directions, median `T_hat` has
   a strictly positive 95% matched-bootstrap interval.
4. **M4 duration ordering:** within each direction, Spearman correlation between
   `T_hat` and declared duration is at least 0.75 with a bootstrap lower bound
   above 0.50.
5. **M5 numerical recovery:** within each direction, median absolute
   `|T_hat-T|` is at most 128 states.
6. **M6 directional symmetry:** median `T_hat` differs by at most 64 states
   between the two directions, and ordered width exceeds abrupt width at three
   or more of the four tested windows in each direction.

All six gates must pass for `SUPPORTED [synthetic multiscale dusk-duration
instrument only]`. M1–M2 passing with M3 failing is `WINDOW SMEAR ONLY`.
Positive M3 with failed M4 or M5 is `FINITE BAND, DURATION UNRESOLVED`.

## Evidence boundary

The ordered generator explicitly contains a finite transition. T353 tests
whether its duration can be recovered from the frozen Di-ARA residual after an
abrupt observation-smear control. It does not prove that a physical system has
such a band, that this is the unique deconvolution, or that every direct-
coupling dusk has an Irrationality Di-ARA counterpart.
