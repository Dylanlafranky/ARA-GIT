# T356 physical-rung diagnostic — frozen addendum

**Frozen:** 11 August 2026, after the T356 `5/7` result and before scoring the
double-pendulum endpoint  
**Status:** new explanatory test; cannot rescue or alter T356's frozen verdict

## Observation being followed

T356 showed a central maximum-flow ridge in the deepest triple-pendulum arm
and in the externally entrained run, but broad or split flow maxima in several
upper free-swing arms. The velocity/angle audit exceeded correlation `0.999`,
so the split is not explained by channel misalignment.

## Frozen hypothesis

If lower-rung child coupling splits an upper arm's flow around its geometric
centre, the same depth ordering should recur in public double-pendulum runs:

- deepest arm 2 should lie closer to the plain-ARA midpoint than upper arm 1;
- deepest arm 2 should retain more of its interval peak speed at the midpoint;
- this ordering should repeat across runs rather than depend on one triple run.

## Data and unchanged instrument

Public dynamicslab double-pendulum free-swing runs 1–4. Run 1 is the local
`pend_double.mat`; runs 2–4 are the separately stored public source files.

The T356 instrument is unchanged:

1. angle-only reversal detector (`0.02*pi` rad prominence; `0.4*1.333 s`
   minimum same-polarity spacing);
2. unweighted midpoint of consecutive opposite reversals;
3. recorded `dTheta` maximum as the held-out physical referee;
4. error normalized by the containing half-swing duration.

No threshold, weight, lag or offset is fitted to the double-pendulum results.

## Frozen gates

- **D1 depth ordering:** pooled arm-2 median error is lower than arm-1;
- **D2 per-run replication:** arm-2 median error is lower in at least 3/4 runs;
- **D3 clean lower ridge:** arm-2 median error is `<0.12` in at least 3/4 runs;
- **D4 flow retention:** pooled arm-2 midpoint flow fraction exceeds arm-1;
- **D5 central tendency:** pooled signed target phase for both arms lies within
  `0.05` of `0.5`, distinguishing a split around the ridge from one consistently
  displaced ridge.

All five gates are required for **SUPPORTED DEPTH-SPLIT EXPLANATION**.

## Boundary

A pass would show a repeatable rung-dependent split in this pendulum archive.
It would support the interpretation that plain ARA fixes the geometric centre
while coupling can redistribute the strongest local flow around it. It would
not establish the mechanism of that redistribution, identify a universal
parent observable, or change T356's failed `7/7` requirement.

