# T411E — Parent–child coarse-ridge drop evaluation

## Status

**Recurring pre-handover state feature; not supported as a specific temporal handover ridge.**

This was a frozen post-hoc mechanism test. S2 and S4 had already been inspected,
so the result is diagnostic and requires a new external identity or archive for
sealed confirmation.

## Exact ARA proposition tested

No medium or identity was changed. The test reused the S1–S4 time-facing
filament-breakup identities from T411D.

The child and parent were compressed into their coarse pair:

\[
R_{PC}(t)=\frac{x_C(t)+x_P(t)}{2}.
\]

The proposed handover landmark was the first causal, five-frame-confirmed
downward crossing after the already-frozen child issue:

\[
R_{PC}>1\quad\longrightarrow\quad R_{PC}\le 1.
\]

The prediction used only the causal issue time; the interpolated crossing was
recorded for description and was not allowed to move the issue backward.

## Result

- Eligible observed handovers: **113**.
- Pair-drop predictions: **87/113 (76.99% coverage)**.
- Pair drop occurred before the observed target: **74/87 (85.06%)**.
- Median lead: **0.082 s**.
- Median absolute timing error: **0.2198 breakup lifetimes**.
- Previous T411D child-only median error on the same covered events: **0.1908**.
- Parent-only median error on the same covered events: **0.0461**.
- Upward pair crossing median error: **0.2462**.

The pair drop was therefore commonly early, but it was less precise than both
the parent-only landmark and the previously frozen child-only forecast.

## Falsification control

With 1,000 circular shifts of the coarse-pair history:

- all S1–S4 observed median error: **0.2198**;
- all S1–S4 shift-null median: **0.2155**;
- one-sided shift result: **p = 0.5834**;
- diagnostic S2+S4 observed median: **0.2304**;
- diagnostic S2+S4 shift-null median: **0.2446**;
- diagnostic one-sided shift result: **p = 0.3017**.

The frozen pair drop did not separate from time-shifted versions. It is not a
validated specific clock for the observed handover.

## ARA interpretation

The proposed parent–child ridge exists as a legitimate compressed coordinate.
The failure is more specific: this coordinate crosses the 1.0 ridge repeatedly.
Consequently, an unqualified rule such as “take the first drop after the child
issue” selects a recurring relaxation feature rather than the unique release
handover.

The result supports this narrower statement:

> The parent–child coarse ridge is often already descending before the observed
> handover, but its first descent is not sufficient to locate the handover.

The parent-only ridge remains the strongest timing landmark in this archive.
Any next pair-ridge test must add an independently frozen state condition—such
as the connection-heavy child's phase or the parent's direction—on development
identities and then be evaluated on a new untouched identity. Selecting the
drop nearest the target would use future knowledge and is not an admissible
forecast.

## Reproduction

- Protocol: `T411E_PARENT_CHILD_RIDGE_DROP_PROTOCOL.md`
- Analysis: `t411e_parent_child_ridge_drop.py`
- Visual: `results/T411E_parent_child_ridge_drop/T411E_RIDGE_DROP_VISUAL.png`
- Event output: `results/T411E_parent_child_ridge_drop/T411E_EVENTS.csv`
- Time-series output: `results/T411E_parent_child_ridge_drop/T411E_TIMESERIES.csv`
- Machine-readable result: `results/T411E_parent_child_ridge_drop/T411E_RESULTS.json`
