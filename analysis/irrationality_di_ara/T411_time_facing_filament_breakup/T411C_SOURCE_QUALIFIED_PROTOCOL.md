# T411C — source-qualified, time-facing filament handover

## Question

Does a moving filament show a repeatable ARA handover between the current
plate-imposed thinning rate and the additional current thinning rate, when the
measurement is followed longitudinally through time rather than cut across the
finished droplet?

This is a test of the proposed Irrationality Di-ARA *instrument*. It is not a
test that “time causes breakup”, and it does not identify the residual with
time. Gravity, capillarity and unmodelled apparatus effects remain physical
rivals.

## Who / what / when / where / why / how

- **Who:** one silicone-oil filament per experimental run. S1 and S3 are
  development fluids; S2 and S4 remain sealed holdout fluids.
- **What:** the relation between the instantaneous mechanically predicted
  thinning rate and the additional observed thinning rate.
- **When:** each 1 ms source frame, from 5% of the direct video-registered
  lifetime until the last numerically reliable neck-width frame.
- **Where:** the minimum neck at the stationary mid-plane between two plates;
  this is a longitudinal/time-facing cut through one evolving identity.
- **Why:** the prior cumulative cut preserved whole-history ordering but never
  reached the ridge. A current-rate cut is the child/movement-scale version of
  the same decomposition.
- **How:** smooth the measured diameter with a pixel-aware local quadratic
  window, differentiate it, subtract the published mechanical model, and map
  the two non-negative rate contributions to a 0–2 ARA coordinate.

## Frozen coordinate

The published mechanical-only diameter is

\[
D_M(t)=D_0\left(1+\frac{vt}{H_0}\right)^{-3/4}.
\]

Define

\[
r_M=-\frac{dD_M}{dt},\qquad
r_I=-\frac{dD_{obs}}{dt}-r_M,
\]

and, only when \(r_M\ge0\), \(r_I\ge0\) and \(r_M+r_I>0\),

\[
x_{rate}=2\frac{r_I}{r_M+r_I}.
\]

Thus 0 is the pure mechanical-rate pole, 2 is the pure additional-rate pole,
and 1 is their equal-current-rate ridge. The first upward crossing that remains
at or above 1 for five source frames is the inferred rate handover.

No complement is invented: \(r_M+r_I\) is algebraically the observed current
thinning rate.

## Source qualification discovered during development

The published numeric width extraction becomes unreliable below five pixels,
although direct breakup time remains available from the high-speed video.
T411B showed that slow S3 traces can therefore end before the phase under test.
Before opening the holdout, T411C freezes an identity-independent source rule:

\[
\frac{t_{last\ reliable}}{t_{breakup}}\ge0.90
\]

with at least 40 reliable frames. This rule is applied equally to development
and holdout and uses no ARA result.

## Smoothing

The centred local-quadratic window spans the theoretical time required for two
pixels of capillary thinning, with a minimum of 11 frames and a maximum of 31%
of the reliable trace. It is determined from source metadata before observing
the handover coordinate.

## Gravity rival

The apparatus is vertical and gravity is not assumed absent. The frozen rival
checks are:

1. initial local Bond number
   \(Bo_0=\rho g(D_0/2)^2/\sigma\);
2. local \(Bo\) at handover;
3. height-sensitive proxy \(G_H=\rho gHD/(2\sigma)\);
4. 1 mm versus 2 mm plate groups (a fourfold diameter-squared change in
   \(Bo_0\));
5. correlation of handover position with \(Bo_0\).

The residual is not labelled “time”. A repeatable handover that survives these
checks supports a time-facing ARA description; it does not prove that gravity
or capillarity is uninvolved.

## Direct / inferred / proxy / absent

- **Direct:** time, neck diameter, plate motion, fluid identity, direct video
  breakup time.
- **Model-derived:** mechanical-only diameter and rate.
- **Inferred:** additional current rate, ARA coordinate and ridge crossing.
- **Proxy:** Bond-number and height-sensitive gravity measures.
- **Absent:** a direct force or energy partition, and an independent gravity-
  free realization of the same experiment.

