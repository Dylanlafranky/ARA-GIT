# T411D — causal connection-heavy child forecast

## Question

Can a connection-heavy child crossing predict the already-defined T411C parent
rate handover before it occurs?

This is a temporal prediction test.  The T411C centred-rate crossing is retained
only as an offline target; it is not allowed into the predictor.

## Who / what / when / where / why / how

- **Who:** the same source-qualified silicone-oil filament runs used by T411C.
  S1 and S3 are development identities.  S2 and S4 remain sealed holdout.
- **What:** a one-rung-down ARA relation between persistent unresolved thinning
  and its faster departure.
- **When:** every 1 ms frame, using that frame and earlier frames only.
- **Where:** the child of the T411C unresolved-rate branch, before the T411C
  parent reaches its equal-rate ridge.
- **Why:** the ARA hypothesis says a connection-heavy child crossing should
  lead the parent handover.  Its projection need not place the parent exactly
  at 1 because the child's connection and movement contributions can be
  asymmetric.
- **How:** causal trailing regressions estimate two unresolved rates.  The slow
  estimate uses the frozen T411C parent window; the fast estimate uses half
  that window, the pure octave child scale.

## Frozen coordinate

Let

\[
r_I^{(P)}(t)=r_{obs}^{(P)}(t)-r_M(t)
\]

be the causal unresolved rate at the parent window and

\[
r_I^{(C)}(t)=r_{obs}^{(C)}(t)-r_M(t)
\]

the causal unresolved rate at the half-window child scale.  Define

\[
C_t=\max\!\left(r_I^{(P)}(t),0\right),\qquad
M_t=\left|r_I^{(C)}(t)-r_I^{(P)}(t)\right|,
\]

and

\[
\boxed{x_C(t)=2\frac{C_t}{C_t+M_t}}.
\]

Here 0 is movement-departure dominance, 1 is equal child participation and 2
is persistent connection dominance.  `C` and `M` have the same units
(mm/s).  They are an operational child decomposition, not two independently
measured physical currents.

The causal parent coordinate is

\[
x_P(t)=2\frac{r_I^{(P)}(t)}{r_{obs}^{(P)}(t)}
\]

where all rates are non-negative.

## Online trigger

The child trigger is armed after an observed child value below 1.0 while
the causal parent remains below 1.  It fires at the first frame for which the
last five observed child values are all at or above 1 and the causal parent is
still below 1.  The issue time is the fifth confirming frame, not the earlier
interpolated crossing.  This makes the trigger deployably causal.

The parent-only comparator uses the same five-observation confirmation rule on
`x_P = 1`.  The established capillary comparator solves `r_M(t) = r_cap` from
source metadata alone.

## Development and sealed evaluation

1. Run the coordinate on S1/S3 only.
   An offline parent target earlier than the first possible trailing parent
   rate is causally unresolvable and is excluded before any prediction score.
   This prevents edge-padded centred estimates from becoming impossible
   temporal targets.
2. Freeze the median observed delay from child issue to the offline T411C
   parent target.  Freeze the analogous parent-only offset.
3. Predict each S2/S4 parent handover as child issue time plus the frozen
   development delay.  Do not refit by fluid.
4. Score in physical seconds.  Direct breakup time may be used only afterward
   to express normalized error.
5. Compare forecast coverage, pre-target issue fraction, absolute error,
   parent-only error, capillary error and circular-shift timing controls.

## Frozen decision gates

All gates apply to qualified holdout runs having a finite offline T411C target.

1. Child forecast coverage at least 75%.
2. At least 70% of issued child triggers precede the parent target.
3. Positive median issue lead.
4. Child median normalized absolute error no greater than 0.10 of direct
   breakup lifetime.
5. Child issue time precedes the parent-only issue time at the matched-event
   median.  Parent-only error is still reported, but a closer alarm issued
   after the target is a detector rather than an advance forecast.
6. Child median error is below the 5th percentile of 1,000 circular-shift
   control medians (one-sided `p <= 0.05`).

The capillary comparator is reported but is not a required win: it is an
established-physics crosswalk with identity metadata unavailable to a purely
geometric child signal.

## Boundaries

- The T411C target is an inferred offline handover, not a directly observed
  microscopic event.
- The causal predictor does not use centred smoothing, future persistence,
  final breakup time, or holdout-derived parameters.
- A successful result supports temporal information in this operational child
  cut.  It does not prove that `C` and `M` are uniquely the physical child
  identities.
- A failure distinguishes poor timing utility from failure of the earlier
  offline reconstruction.
