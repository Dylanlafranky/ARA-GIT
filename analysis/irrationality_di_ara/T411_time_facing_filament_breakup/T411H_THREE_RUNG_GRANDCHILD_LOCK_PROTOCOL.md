# T411H — frozen three-rung grandchild-lock protocol

## Status and question

This protocol was frozen before constructing the quarter-window grandchild
coordinate or fitting T411H. It is an already-exposed archive diagnostic, not
a sealed external confirmation.

T411G found that the correctly aligned child–parent relation carried timing
information, but that a fixed two-axis Di-ARA did not transfer better than the
parent state. T411H tests the proposed explanation: the desired event is the
child's Phase A-to-Phase B singularity, while the parent ridge is only its
coarse anchor. A one-rung-lower seam may provide the third relation needed to
lock the correct crossing.

## Who

The same 123 source-qualified S1–S4 silicone-oil filament identities used in
T411F/G, subject to finite causal parent, child, and grandchild coordinates.
Every complete fluid identity is held out once while models are fitted on the
other three.

## What

For each event, use the already-frozen T411D windows:

- parent rate `r_P`: trailing parent-window unresolved thinning rate;
- child rate `r_C`: trailing half-window unresolved thinning rate;
- grandchild rate `r_G`: trailing half-child-window unresolved thinning rate.

The grandchild window is frozen as half the child window, rounded upward to an
odd integer with a minimum of three frames. Thus S1 uses a three-frame
grandchild against a five-frame child; this is a noisier but genuinely distinct
causal scale.

Define adjacent detail magnitudes

\[
D_{PC}=|r_C-r_P|,
\qquad
D_{CG}=|r_G-r_C|,
\]

and the lower seam coordinate

\[
\boxed{x_G=2\frac{D_{PC}}{D_{PC}+D_{CG}}}.
\]

`x_G = 1` is the pure equal-detail ridge. It is a geometric landmark, not a
required empirical threshold; identity asymmetry may displace observations.

The existing coordinates remain:

- `x_P`: causal parent ARA position;
- `x_C`: operational connection-heavy child ARA position.

Centered coordinates and five-frame causal changes are

\[
v=x_P-1,\quad u=x_C-1,\quad w=x_G-1,
\]

with `dv`, `du`, and `dw` measured against the observed value five frames
earlier.

## When

Every fifth raw frame before the offline T411C parent handover, requiring all
three current coordinates and their five-frame lags to be finite. The binary
outcome is whether the parent handover occurs within the next previously frozen
child window. No future quantity enters a predictor.

## Where

This is a vertical three-rung cut through:

1. the parent ridge that coarsely locates the handover;
2. the direct child singularity candidate;
3. the seam between adjacent child and grandchild detail layers.

The quarter-window detail is an operational lower-rung cut of one observed
diameter trajectory. It is not yet an independently measured physical
Phase-B-of-A or Phase-A-of-B current.

## Why

The proposed Information³ lock is that the parent ridge and child crossing do
not uniquely identify the relevant singularity. The lower seam adds a third
relation. If its correct timing improves held-out prediction and the gain is
destroyed by shifting only the grandchild path, the lower relation contains
information not supplied by the parent–child pair alone.

## How

Event-balanced, training-standardised weighted logistic scorers are evaluated
leave-one-fluid-out:

1. constant training prevalence;
2. parent state: `[v, dv]`;
3. parent + child: `[v, dv, u, du]`;
4. parent + grandchild: `[v, dv, w, dw]`;
5. three-rung additive: `[v, dv, u, du, w, dw]`;
6. three-point lock: `[v, dv, u, du, w, dw, v*w, u*w]`.

The two lock interactions are predeclared because the grandchild seam is
proposed to lock both the parent ridge and child singularity. The previously
unsuccessful generic `u*v` interaction is not reintroduced.

## Frozen falsification and decision gates

For 1,000 controls, circularly shift `w` and `dw` together within each held-out
event while preserving the child path, parent path, outcome, grandchild
distribution, and grandchild autocorrelation. Recompute `v*w` and `u*w` after
each shift and apply the already-fitted held-out model unchanged.

The three-point lock is supported only if all five gates pass:

1. Brier error is lower than parent state;
2. Brier error is lower than parent + child;
3. AUC is greater than parent state;
4. Brier error improves on parent state in at least three of four held-out
   fluids;
5. its Brier improvement over parent + child exceeds the 95th percentile of
   grandchild-shift controls (`p <= 0.05`).

## Visual contract

- **Question:** does the grandchild seam add transferable, correctly timed
  information to the parent–child handover?
- **Surface:** reproducible static PNG beside saved CSV/JSON results.
- **Charts:** per-fluid child-versus-grandchild probability heatmaps; model
  Brier/AUC comparison; per-fluid Brier improvement; grandchild-shift null;
  example causal three-rung trajectories.
- **Palette:** one blue/purple root plus neutral references and gold emphasis;
  line style and direct labels supplement color.
- **QA:** all axes show ARA units or seconds; blank heatmap cells are labelled
  as insufficient coverage; the frozen ridge at 1 is a reference, not a fitted
  boundary; the final PNG is inspected at full resolution.

## Interpretation boundary

Passing supports this operational three-rung lock in these filament fluids.
It does not prove a universal physical grandchild identity. Failure rejects the
fixed implementation, not the broader claim that a different lower-rung cut
could lock the singularity.

