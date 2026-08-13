# T344 BAW weir Irrationality Di-ARA — computational addendum v1 (frozen)

**Frozen:** 6 August 2026, after schema-only inspection and before calculating any
ARA coordinate, sector, prediction or closure-class outcome.

This addendum implements, but does not change,
`T344_BAW_WEIR_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md`.

## Workbook mapping

Each laboratory workbook contains:

- sheet `x`: horizontal image coordinate in pixels, zero at the left image border;
- sheet `y`: vertical image coordinate in pixels, zero at the upper image border;
- row `3`: particle number in columns `B...`;
- column `A`, rows `5...`: time in seconds;
- a native nominal cadence of `0.01 s`; and
- time zero fixed by the source to crossing of the weir crest.

The physical ARA chart is declared as

\[
p_t=(x_t,z_t)=(x_{\rm image,t},-y_{\rm image,t}),
\]

so downstream/right is positive `x` and physical up is positive `z`. This sign choice
only fixes the forward/reverse label orientation; reciprocal and predictive tests are
unchanged under a declared mirror.

For each workbook:

1. parse particle IDs from row `3` independently on `x` and `y`;
2. require unique, finite IDs;
3. use only the exact intersection of IDs present on both sheets;
4. join observations by the exact time value in column `A`;
5. retain only rows for which both coordinates are finite; and
6. never interpolate an `x`-only, `y`-only or missing-time value.

The source's differing sheet extents are recorded as data quality, not silently padded.

## Consecutive-event rule

Positions are consecutive when

\[
|t_{j+1}-t_j-0.01|\le10^{-8}\ \mathrm{s}.
\]

A Di-ARA quotient requires three positions at consecutive native times. A next-sector
target requires one further consecutive position. Rolling-window calculations require
the entire window to remain consecutive.

## Prediction estimators

All evaluation rows remain grouped by whole trajectory.

### Categorical baselines

Global, radial-child and turn-child probabilities are Laplace-smoothed frequency tables
with pseudocount `1` per next-sector class. Persistence assigns probability `0.97` to the
current sector and divides `0.03` equally among the other sectors; this avoids infinite
log loss while remaining a fixed no-fit baseline.

### Additive, intact and broken models

Use scikit-learn multinomial logistic regression with:

- standardisation learned on training rows only;
- L2 penalty;
- `C=1`;
- `solver="lbfgs"`;
- `max_iter=1000`;
- no class reweighting; and
- fixed seed `344` wherever the implementation accepts one.

The additive model receives `(X-1,Y-1)`. The intact parent adds
`(X-1)(Y-1)` and `D=|X-1|-|Y-1|`. The broken model receives the same feature form after
replacing `Y` with its deterministic donor value.

### Deterministic causal donor

Within condition and elapsed-track decile, sort trajectories by
`SHA256(condition + ":" + particle_id)`. The donor is the next eligible trajectory in
that circular **ID list**, but donor time never wraps: use only its observation in the
same decile whose elapsed fraction is closest to the recipient's current elapsed
fraction. A donor row may supply current `Y`; it may not supply the recipient target or
any future value. If no donor row exists, exclude that broken-control row and report it.

## Predictive-information estimator

For closure-class comparisons, retained next-state information is measured out of
sample as the intact parent's log-score gain over the training-fold global base rate:

\[
I_t=\log p_{\rm parent}(S_{t+W+1}\mid S_t)
-\log p_{\rm base}(S_{t+W+1}).
\]

This is reported in nats. Positive `I_t` means the present relation reduces surprise
about the future state relative to knowing only the source fold. This estimator is the
operational held-out mutual-information quantity named in the protocol; no probabilities
are learned from the held-out condition.

## Bootstrap and weighting

Compute each metric within trajectory first, then average trajectories with equal
weight. Use `2,000` whole-trajectory bootstrap replicates with seed `344`; percentile
`2.5%` and `97.5%` bounds form the reported `95%` interval. A result whose interval
touches zero does not pass.

For Gate D matching, stratify by condition, elapsed-track decile and current-speed
quintile learned from the training conditions. Retain only strata containing the two
classes being compared. Weight retained strata equally, then trajectories equally
inside strata.

## Classification and ridge tolerance

Use the protocol's exact ridge tolerance `1e-12` in ARA coordinate space. Boundary
events are reported and excluded from four-sector classification. No empirical median
is used to move a ridge.

## Output requirements

The program must write:

- source/data-quality manifest;
- event-level ARA sample sufficient for reproduction without redistributing the source;
- per-condition sector and transition summaries;
- fold-level predictions and model scores;
- causal broken-pair audit;
- closure-class and `W=8/15/30` sensitivity summaries;
- whole-trajectory bootstrap differences;
- exact-landmark secondary table;
- JSON result and validation summaries;
- a static multi-panel figure; and
- an interactive HTML explorer if practical.

Raw source workbooks remain ignored by Git; reproduction instructions point to the DOI
and verify the official SHA-256 values.

