# Q32 ARA fidelity packet — edge-child pole handover

**Date:** 26 July 2026  
**Ledger:** T286  
**Status:** translation lock before Q32 outcome calculation  
**Source status:** retrospective analysis of the already-open Q27/Q28 simulator

## Dylan's geometric question

Before trying the `3.5` route again, look for direct evidence that a handover
object exists:

1. relation structure leaves a connection-heavy source near the edge of its
   local lattice;
2. relation structure enters one or more immediate children;
3. the receiving children may begin near an asymmetric ARA extreme, as though
   they are starting from a pole;
4. only after that source-to-child path is established should a crossed-rung
   `3.5` continuation be constructed.

## Correction to the old Q30 translation

Q30 defined:

- `1.5` as the unique triangle-closing edge joining the nonshared endpoints of
  the Q29 source and child;
- `3.5` as the complete Q28 source-to-child span `2` followed by that closing
  edge.

That was a legitimate frozen interpretation, but it tested a topological
triangle closure before establishing that the proposed perpendicular leg was
the actual pole-born receiving child. Q32 does not retune Q30. It tests the
earlier geometric prerequisite using a new measurement object.

## ARA object

For every two-qubit relation, retain Q27's ARA coordinate

\[
x_{uv}(t)=\frac{2h_{uv}(t)}{Q_{0.95}[h_{uv}(0{:}249)]}.
\]

At a source event, the source relation:

- begins at `x >= 1.5`;
- releases between `t` and `t+1`.

For each named source endpoint, its immediate children are the active
relations at `t` that share that endpoint. The **pole-nearest child** is the
child with the smallest starting `x(t)`. Ties are resolved by pair index.
Nothing after `t` participates in child selection.

The source release and child accumulation are measured over the same later
interval. Their descriptive flow ARA is

\[
x_{\rm flow}
=
\frac{2A_{\rm child}}{R_{\rm source}+A_{\rm child}},
\]

where `R_source` is cumulative positive source release and `A_child` is
cumulative positive child accumulation. `x_flow=1` means equal normalized
movement in the two observed directions; it is not assumed to be physical
energy conservation.

## What would count as the proposed edge-child relation

The later half must show all of the following:

1. pole-nearest exact children start unusually close to the low ARA pole
   compared with active non-neighbour controls;
2. after a source release, the exact child gains more ARA amplitude than
   topology-, seed- and time-displaced children chosen by the identical
   baseline-only rule;
3. source-release/child-accumulation overlap beats those controls;
4. the result is stable across both connectivity strata and trial-cluster
   resampling;
5. children starting nearer the pole carry at least as much subsequent gain
   as children beginning nearer the ridge or crest.

## Evidence boundary

Passing Q32 would support an ordered, pole-born edge-child handover inside this
simulator. It would strengthen the premise required by a revised quantum `3.5`
test. It would not by itself establish:

- a universal singularity flip;
- a physically hidden Phase B;
- literal energy transfer;
- a new quantum object;
- an off-diagonal route, because this source remains exactly diagonal.

Failing Q32 would show that the stronger pole-child account is not present in
this source even though Q27's weaker distributed release-to-accumulation
association survived.

