# T309 — Galactic-Orbit 7.5/15 ARA Geometry

**Registered:** 31 July 2026  
**Status:** registered exact-3D confirmation after the scalar clue, not blind discovery  
**Source state:** the JPL Earth–Sun vectors were already opened in T308  
**Primary question:** does the full three-dimensional Earth-orbit-plus-parent-
travel geometry reproduce the previously documented `7.5 : 15` ARA cadence?

## Prior information and evidential boundary

Before this protocol was written, the public approximate speeds

\[
v_{\oplus|\odot}\approx29.8\ {\rm km\,s^{-1}},
\qquad
V_{\rm gal}\approx230\ {\rm km\,s^{-1}}
\]

had already produced the perpendicular idealisation

\[
\tan^{-1}(29.8/230)\approx7.4^\circ,
\qquad
2(7.4^\circ)\approx14.8^\circ.
\]

T309 therefore cannot count as an outcome-blind discovery of `7.5 : 15`.
It asks the harder question left open by that clue: does the relationship
survive the real three-dimensional Earth velocity, the orientation of the
ecliptic relative to Galactic travel, orbital eccentricity, year-to-year
variation and reasonable parent-frame controls?

## ARA interpretation

The Earth orbit is the child cycle. The local Galactic trajectory of the
Solar System is the parent traversal. In a declared frame \(F\),

\[
\mathbf v_\oplus^{(F)}(t)
=
\mathbf V_{\rm parent}^{(F)}
+
\mathbf v_{\oplus|\odot}(t).
\]

The child does not climb a structural rung during one year. Its
\(0\rightarrow2\rightarrow0\) cycle is extruded along the moving parent
axis.

For one branch, define the measured child-to-parent inclination

\[
\alpha(t)
=
\cos^{-1}
\frac{
\bigl(\mathbf V+\mathbf v(t)\bigr)\cdot\widehat{\mathbf V}
}{
\left|\mathbf V+\mathbf v(t)\right|
}.
\]

Let \(t^\star=t+P/2\), where \(P\) is the Earth period estimated from the
calibration half. The opposite Phase A/Phase B branch aperture is measured
directly:

\[
\beta(t)
=
\cos^{-1}
\frac{
\bigl(\mathbf V+\mathbf v(t)\bigr)\cdot
\bigl(\mathbf V+\mathbf v(t^\star)\bigr)
}{
\left|\mathbf V+\mathbf v(t)\right|
\left|\mathbf V+\mathbf v(t^\star)\right|
}.
\]

In the ideal perpendicular circular case, \(\beta=2\alpha\). T309 does not
impose that equality. It measures both quantities separately.

The paired ARA coordinate is retained as a descriptive crosswalk:

\[
x_A(t)=
\frac{2\alpha(t)}
{\alpha(t)+\alpha(t^\star)},
\qquad
x_B(t)=2-x_A(t).
\]

The identity \(x_A+x_B=2\) is forced by this normalization and is not an
empirical result. Whether the observed pair sits near the ridge and how far
its children depart from it remain reportable geometry.

## Public source and fixed frame

### Child velocity

NASA/JPL Horizons geometric Cartesian Earth (`399`) relative to Sun
(`500@10`) vectors, one-day cadence, ecliptic ICRF/J2000 axes, kilometres and
seconds, `2000-01-01` through `2026-01-01`. T309 reuses the raw response and
parsed vectors retained by T308.

### Primary parent frame

The primary parent is the local circular Galactic direction
\((l,b)=(90^\circ,0^\circ)\), transformed from the IAU Galactic frame to
ICRS and then to the J2000 ecliptic frame. Its fixed speed is NASA's published
`829,000 km/h = 230.277777... km/s`.

This is a declared local circular-orbit model. It is not a claim that the
Sun has zero peculiar velocity or that the Galactic trajectory is perfectly
straight over long times.

### Fixed controls

1. Same Galactic direction at parent speeds
   `200, 220, 230.2777778, 240, 250, 300, 369 km/s`.
2. CMB direction \((l,b)=(264^\circ,48^\circ)\) at `369 km/s`.
3. The scalar perpendicular approximation
   \(\alpha_{\rm scalar}=\tan^{-1}({\rm median}|v|/V)\).

The CMB control tests reference-frame specificity; it is not treated as a
superior definition of the parent.

## Calibration and evaluation split

- Calibration: `2000-01-01` through `2012-12-31`, used only to estimate the
  orbital period from the least-squares long-run slope of unwrapped ecliptic
  longitude. An instantaneous-speed median is forbidden because eccentricity
  makes Earth spend unequal time in different orbital sectors.
- Evaluation: `2013-01-01` onward.
- Opposite-branch velocities are obtained by deterministic linear
  interpolation at \(t+P/2\).
- Complete-year stability summaries require at least 350 paired daily
  observations, so the incomplete final year is excluded from that summary.

## Fixed outputs

For the primary frame:

1. median, mean, 2.5%, 25%, 75%, 97.5%, minimum and maximum of \(\alpha\);
2. the same summaries for \(\beta\);
3. yearly median and maximum values for both;
4. \(\beta-[\alpha(t)+\alpha(t^\star)]\), which checks whether the parent
   direction lies between the two observed branches;
5. the descriptive paired ARA coordinate \(x_A\);
6. fraction of observations within `±0.25°` of `7.5°` for \(\alpha\);
7. fraction within `±0.5°` of `15°` for \(\beta\);
8. all fixed speed and CMB-frame controls.

## Registered interpretation

### Central cadence supported

- evaluation median \(\alpha\) is within `0.25°` of `7.5°`; and
- evaluation median \(\beta\) is within `0.5°` of `15°`.

### Stable crest/envelope recurrence

The central gate fails, but in at least `9/12` complete evaluation years:

- yearly maximum \(\alpha\) is within `0.25°` of `7.5°`; and
- yearly maximum \(\beta\) is within `0.5°` of `15°`.

The report must call this an envelope recurrence, not the orbit's typical
angle.

### Not supported

Neither the central nor stable-envelope gate passes.

### Frame qualification

Any supported result must be labelled Galactocentric if the CMB control does
not reproduce it. Sensitivity of the result to plausible parent speed is part
of the conclusion, not a removable nuisance.

## Reproduction contract

```powershell
python t308_phi_temporal_ruler_orbital_probe.py --fetch
python t309_galactic_orbit_7_5_15.py
python validate_t309_galactic_orbit_7_5_15.py
```

No Fourier decomposition, fitted rotation, outcome-selected parent direction
or post-result change to the target angles is permitted.

## Post-result audit notice

The fixed speed controls revealed that the registered result was sensitive to
the rounded `230.2778 km/s` parent value. A separate post-result robustness
audit was therefore required using:

- Reid & Brunthaler's measured Sgr A* reflex proper motion;
- the GRAVITY Collaboration's `R0 = 8.178 kpc` geometric distance;
- Schönrich, Binney & Dehnen's local Solar radial component.

This audit is not part of the registered primary outcome and cannot overwrite
it. It controls the scientific conclusion about whether the recurrence
survives the best available Galactocentric velocity estimate.
