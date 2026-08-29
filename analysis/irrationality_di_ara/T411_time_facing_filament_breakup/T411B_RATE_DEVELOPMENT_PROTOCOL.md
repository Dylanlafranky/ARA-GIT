# T411B - Child/movement rate handover development protocol

**Status:** frozen before S2/S4 rate extraction or scoring  
**Reason for new cut:** T411 cumulative development measured whole-history
parent participation and produced no equal-participation handover before the
reliable-width endpoint.

## Relational address

- **Who:** the same S1/S3 development filaments; S2/S4 remain holdout.
- **What:** present mechanical thinning rate versus present non-mechanical
  thinning rate.
- **When:** every one-millisecond sample with a derivative window chosen from
  physical pixel resolution and capillary rate.
- **Where:** the filament mid-plane, one rung down from cumulative history.
- **Why:** determine which branch controls the filament's movement now and
  locate its equal-participation handover before direct breakup.
- **How:** differentiate the observed and plate-modelled diameter trajectories,
  subtract the mechanical rate, and form their exact 0-2 ARA relation.

## Rate waves and coordinate

\[
r_M(t)=-\frac{dD_M}{dt},
\qquad
r_I(t)=-\frac{dD_{obs}}{dt}-r_M(t).
\]

`r_M` is the directly parameterized parent rate. `r_I` is the unresolved
current rate and may include capillarity, gravity, redistribution and smaller
couplings. Where both are non-negative,

\[
x_{rate}(t)=\frac{2r_I(t)}{r_M(t)+r_I(t)}.
\]

The inferred handover is the first persistent upward crossing of `x_rate = 1`
after `u = t/t_break >= 0.05`. The direct breakup at `u=1` remains a separate
observed endpoint.

## Pixel-aware derivative

The published width has finite pixel resolution. For each run, the derivative
window aims to span the time required for the theoretical capillary rate to
change the neck by two pixels:

\[
\Delta t_{target}=\frac{2/(px/mm)}{r_C}.
\]

The odd Savitzky-Golay window is at least 11 samples and at most 31% of the
reliable run. A second-order polynomial and centred derivative are used. This
is a descriptive handover test, not a causal real-time forecaster.

## Frozen controls inherited from T411

- S1/S3 development; S2/S4 holdout.
- `D_px >= 5`; no imputation through the sub-five-pixel tail.
- exact measured plate velocity and source geometry.
- 1 versus 2 mm plate and low/high Bond-number gravity controls.
- local `Bo`, height-sensitive `G_H`, late capillary-rate crosswalk.
- within-run circular shift of `r_I` against `r_M` as temporal-order control.

No holdout rate coordinate may be computed until a development window and
gate are registered and hashed.
