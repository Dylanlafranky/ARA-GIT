# T412 — Frozen child-to-grandchild channel crossing

## Question

Does the post-hoc T411J lead become a causal handover signal when tested as the event it actually proposes: the grandchild-oriented closure channel overtaking the child-oriented closure channel?

## ARA relation under test

For centered parent, child and grandchild ARA coordinates

\[
v=x_P-1,\qquad u=x_C-1,\qquad w=x_G-1,
\]

the coefficient-free three-rung closure is

\[
A=1-\frac{|z_1-z_2|+|z_2-z_3|+|z_3-z_1|}{4},
\]

\[
R=1-\left|\frac{z_1+z_2+z_3}{3}\right|,
\qquad H=A R.
\]

The two already-defined channels are

\[
H_C=H(v,-u,w),\qquad H_G=H(v,u,-w).
\]

The frozen crossing coordinate is

\[
D(t)=H_G(t)-H_C(t).
\]

A forward channel handover is a causal transition from

\[
D(t-1)<0\quad\hbox{to}\quad D(t)\ge 0.
\]

This is not a new fitted score. T411J already calculated both channels; T412 tests their change of dominance.

## Who, what, when, where, why and how

- **Who:** the 123 qualifying S1–S4 filament-breakup events already represented in the frozen T411J snapshot table. The diagnostic partition is the primary evaluation population; development is reported separately.
- **What:** the signed child-to-grandchild closure difference `D = H_G - H_C` and its negative-to-nonnegative crossing.
- **When:** every predictor is calculated strictly before the offline breakup target. A crossing counts as event-window aligned when it occurs within one already-frozen child horizon before breakup.
- **Where:** across the parent/child/grandchild vertical ARA branch. No new physical feature, capillary prediction or fitted classifier is added.
- **Why:** a dominance transfer may carry timing information that either absolute closure channel hides.
- **How:** score the continuous coordinate, detect forward crossings causally, compare their timing with reverse crossings and within-event circular time shifts, and retain the existing event-balanced weights.

## Frozen primary tests

1. Event-balanced AUC of `D(t)` for whether breakup occurs within one child horizon.
2. Forward crossing concentration: fraction of negative-to-nonnegative crossings inside the final child horizon.
3. Event hit rate: fraction of events with at least one forward crossing inside that horizon.
4. Within-event circular time-shift controls preserve each event's values and rough cadence while breaking alignment to breakup.
5. Absolute-channel comparators are the already-frozen `H_C` and `H_G` scores.
6. Reverse positive-to-negative crossings are a direction control.

## Frozen gates

The lead is supported in-source only if all of the following pass on the diagnostic partition:

1. `AUC(D) > 0.5`.
2. `AUC(D)` exceeds both `AUC(H_C)` and `AUC(H_G)`.
3. The time-shift probability of an equal-or-higher AUC is at most 0.05.
4. Forward-crossing event-window concentration exceeds the 95th percentile of the shifted control.
5. `AUC(D) > 0.5` in at least three of the four fluids, using each fluid's prescribed partition (S1/S3 development; S2/S4 diagnostic).

Two-snapshot persistence is a declared sensitivity check, not a primary gate, because the shortest child horizon contains only one evaluated snapshot.

## Claim boundary

T411J used these events when the difference channel was noticed. T412 is therefore a **frozen retrospective causal audit**, not an independent confirmation. A separate physical dataset is required before calling the channel crossing replicated.

## Protocol erratum recorded during QA

The first written version incorrectly required three of four fluids to pass *inside the diagnostic partition*. The frozen source split places only S2 and S4 in diagnostic and S1 and S3 in development, so that condition was impossible by construction. Before interpreting the outcome, the gate was corrected to its stated scientific intent: at least three of all four prescribed fluid evaluations above chance. No score, crossing definition, horizon, null control or numerical threshold changed.
