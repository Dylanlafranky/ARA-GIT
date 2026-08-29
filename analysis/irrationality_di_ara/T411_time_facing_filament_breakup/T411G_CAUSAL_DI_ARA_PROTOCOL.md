# T411G — frozen causal child–parent Di-ARA protocol

## Status and boundary

This protocol was frozen before fitting the T411G models. It is a diagnostic
cross-identity test using the same already-exposed T411 S1–S4 filament data;
it is not a new sealed external holdout.

T411F showed that absolute child Phase A position alone did not transfer from
S1/S3 to S2/S4. T411G tests the predeclared alternative suggested by that
failure: the event state may require a two-axis Di-ARA relation rather than a
single ARA coordinate.

The statistical models below score the frozen ARA geometry. They do not define
or replace the geometry.

## Who

The same 123 eligible S1–S4 filament identities used by T411F. Each complete
fluid identity is held out in turn while the model is fitted on the other
three. There is no medium change and no pooling of snapshots before the
identity-level split.

## What

At each causal snapshot:

- child coordinate: `x_C = x_child_connection_ara` from T411D;
- parent coordinate: `x_P = x_parent_causal_ara` from T411D;
- centered coordinates: `u = x_C - 1` and `v = x_P - 1`;
- causal five-frame changes: `du` and `dv`;
- child–parent product: `u v`;
- radial flow around the shared ridge center:
  `g_r = u du + v dv`;
- circulation around the shared ridge center:
  `g_theta = u dv - v du`.

Negative `g_r` means motion toward the shared `(1,1)` ridge center; positive
`g_r` means motion away. `g_theta` distinguishes opposite circulation around
that center.

The outcome is whether the independently frozen parent handover occurs within
the next frozen child window.

## When

Every fifth observed frame before the offline T411C parent handover. The
prediction horizon is exactly one previously frozen T411D child window. No
future value is used in a predictor.

## Where

The cut is the coupling plane between the operational connection-heavy child
identity and its direct parent identity. This is a Di-ARA cut, not a claim
that either axis is an independently observed pure Phase A/Phase B current.

## Why

The same child coordinate may represent approach, residence, or retreat.
Adding the parent axis and signed motion tests whether the missing distinction
is relational geometry rather than a universal one-dimensional threshold.

## How

Six fixed weighted logistic scorers are compared under leave-one-fluid-out
evaluation:

1. constant training prevalence;
2. child position only: `[u]`;
3. child state: `[u, du]`;
4. parent state: `[v, dv]`;
5. additive child plus parent: `[u, v, du, dv]`;
6. full Di-ARA: `[u, v, du, dv, uv, g_r, g_theta]`.

Snapshots are event-balanced exactly as in T411F. Continuous features are
standardised using training identities only. The model and scaler are then
applied unchanged to the held-out fluid identity.

## Frozen controls and gates

Primary metrics are pooled out-of-fluid weighted Brier error and weighted AUC.
The full Di-ARA is supported only if all six gates pass:

1. Di-ARA Brier is lower than the constant baseline;
2. Di-ARA AUC is greater than 0.5;
3. Di-ARA Brier is lower than child state `[u, du]`;
4. Di-ARA Brier is lower than the additive `[u, v, du, dv]` model;
5. Di-ARA improves on the constant baseline in at least three of four held-out
   fluid identities;
6. its improvement over child state exceeds the 95th percentile of 1,000
   within-event circular parent-shift controls (`p <= 0.05`).

The circular shift preserves each event's child path, outcome, parent marginal
distribution and parent autocorrelation while breaking the observed temporal
alignment between child and parent. Derived Di-ARA terms are recomputed after
each shift.

## Interpretation boundary

- Passing would support a transferable causal child–parent Di-ARA instrument
  on these four fluid identities.
- Partial passage would identify which part of the geometry transfers but
  remains diagnostic.
- Failure would reject this fixed operational Di-ARA as a transferable
  predictor; it would not reject Di-ARA as a general framework.

