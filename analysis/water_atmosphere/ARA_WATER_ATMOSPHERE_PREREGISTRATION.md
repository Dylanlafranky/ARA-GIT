# ARA water-to-atmosphere test: preregistration

**Protocol version:** 0.1  
**Frozen:** 12 July 2026, before selecting or inspecting empirical datasets for this test  
**Status:** protocol only; no result has been claimed

## Question

Can one fixed ARA competition coordinate organize three connected levels?

1. the gas-to-liquid density transition at an interface;
2. the gravity-to-capillary handover in liquid surface waves;
3. the rotation-to-pressure/gravity handover in atmospheric waves.

The first two levels are already described by established mechanics. They test whether ARA is a clean coordinate system for known physics. The third level is the risky scale-transfer test.

## Important correction to the original density idea

“No density to maximum density” is not a well-defined universal axis. There is no single maximum density shared by all matter, and air does not have zero density.

The test therefore uses **local poles** for each measured pair:

- `0` = the gas-side bulk density;
- `2` = the liquid-side bulk density;
- `1` = the halfway composition/density surface inside the interface.

This preserves Dylan's relational meaning without treating water density as a universal constant or pole.

## Test 1 — density and surface tension at the interface

For gas density \(\rho_g\), liquid density \(\rho_l\), and local density \(\rho(z)\), define

\[
\underbrace{x_\rho(z)}_{\substack{\text{normalized phase coordinate}\\\text{ARA density position}}}
=
2\,
\frac{\rho(z)-\rho_g}{\rho_l-\rho_g}.
\]

Thus \(x_\rho=0\) in bulk gas, \(x_\rho=2\) in bulk liquid, and \(x_\rho=1\) at the interface midpoint.

Write the centered order parameter as

\[
\underbrace{\psi}_{\substack{\text{phase-field order parameter}\\\text{ARA position around the ridge}}}
=x_\rho-1.
\]

A standard two-phase free energy is

\[
\underbrace{F[\psi]}_{\substack{\text{total phase-field free energy}\\\text{cost of maintaining the ARA boundary}}}
=
\int
\left[
\underbrace{\frac{\kappa}{2}|\nabla\psi|^2}_{\substack{\text{gradient energy}\\\text{boundary/webbing cost}}}
+
\underbrace{\frac{a}{4}(\psi^2-1)^2}_{\substack{\text{two-phase bulk potential}\\\text{preference for the two poles}}}
\right]dV.
\]

For the ideal flat equilibrium interface, \(\psi\) has a tanh-shaped transition. Both phases are stable away from the interface, while the mixing/gradient energy is concentrated around \(\psi=0\), or ARA \(x_\rho=1\).

Surface tension is not literally one point. It is the integrated energetic cost of the whole thin interface:

\[
\underbrace{\gamma}_{\substack{\text{surface tension}\\\text{total boundary cost per area}}}
=
\int_{-\infty}^{\infty}
\underbrace{\kappa\left(\frac{d\psi}{dz}\right)^2}_{\substack{\text{local interfacial energy density}\\\text{ARA ridge intensity}}}
dz.
\]

### Frozen prediction 1

After each interface is normalized to \(x_\rho\in[0,2]\) and distance is divided by its independently measured interface width:

- the density profiles will collapse approximately onto one monotonic transition;
- interfacial energy will peak at \(x_\rho=1\), allowing measurement uncertainty of \(\pm0.1\);
- a density-only linear ramp will fit worse than the phase-field tanh profile.

This is an **established-mechanics anchoring test**, not evidence by itself that ARA is a new physical law.

## Test 2 — liquid surface waves

For a deep interface between a liquid and gas, the inviscid capillary–gravity dispersion relation is

\[
\omega^2
=
\frac{
\underbrace{\Delta\rho\,gk}_{\substack{\text{gravity restoring term}\\\text{large-scale pole}}}
+
\underbrace{\gamma k^3}_{\substack{\text{capillary restoring term}\\\text{small-scale pole}}}
}{\rho_l+\rho_g},
\qquad \Delta\rho=\rho_l-\rho_g.
\]

Define the independently calculated competition ratio and its ARA coordinate:

\[
\underbrace{q_w}_{\substack{\text{capillary/gravity ratio}\\\text{relative source strength}}}
=\frac{\gamma k^2}{\Delta\rho g},
\qquad
\underbrace{x_w}_{\substack{\text{bounded competition coordinate}\\\text{ARA 0--2 position}}}
=\frac{2q_w}{1+q_w}.
\]

The direction is declared in advance:

- \(x_w\to0\): gravity-dominated, long waves;
- \(x_w=1\): equal gravity and capillary restoring contributions;
- \(x_w\to2\): capillary-dominated, short waves.

The crossing wavelength is

\[
k_c=\sqrt{\frac{\Delta\rho g}{\gamma}},
\qquad
\lambda_c=2\pi\sqrt{\frac{\gamma}{\Delta\rho g}}.
\]

For water–air near room temperature, this is approximately \(1.7\) cm. No measured wave outcome is used to tune that location.

Let \(c_p=\omega/k\) be phase speed and \(c_g=d\omega/dk\) be group speed. Established mechanics gives the parameter-free relation

\[
\underbrace{\frac{c_g}{c_p}}_{\substack{\text{envelope/carrier speed ratio}\\\text{handover observable}}}
=
\frac{1+3q_w}{2(1+q_w)}
=
\frac12+\frac{x_w}{2}.
\]

At \(x_w=1\), \(c_g=c_p\). The envelope and carrier have no instantaneous speed difference. This is a precise version of a handover landmark; it is not wave cancellation.

### Frozen prediction 2

Use measured \(\omega(k)\), density, and surface tension from at least four liquid–gas systems. Include every eligible dataset found by the selection rule; do not select only visually clean liquids.

Without shifting, stretching, or fitting the ARA coordinate:

- the observed phase-speed minimum will occur at \(q_w\in[0.67,1.50]\);
- the observed \(c_g/c_p=1\) crossing will occur in the same interval;
- the fixed prediction \(c_g/c_p=0.5+x_w/2\) will have pooled MAE \(\le0.10\);
- it must outperform a pooled raw-wavenumber model and a density-only model under leave-one-liquid-out testing.

Viscosity, finite depth, contamination, and measurement resolution must be recorded. A dataset may be excluded only by a rule written before its outcome is plotted.

## Test 3 — transfer to an atmospheric rung

“Atmospheric tension” is not molecular surface tension. At this rung the restoring competition is pressure/gravity against rotation.

For the simplest rotating shallow-water wave,

\[
\omega^2
=
\underbrace{f^2}_{\substack{\text{rotational restoring term}\\\text{rotation-side pole}}}
+
\underbrace{c^2k^2}_{\substack{\text{pressure/gravity term}\\\text{propagating-side pole}}},
\]

where \(f\) is the Coriolis parameter and \(c=\sqrt{gH}\) is calculated from an independently supplied equivalent depth \(H\).

Use the same bounded operator, with no new width or center parameter:

\[
\underbrace{q_a}_{\substack{\text{gravity-wave/rotation ratio}\\\text{atmospheric source ratio}}}
=\frac{c^2k^2}{f^2},
\qquad
\underbrace{x_a}_{\substack{\text{same bounded operator}\\\text{ARA position one rung up}}}
=\frac{2q_a}{1+q_a}.
\]

The observable projection is not identical to the water projection. For this wave,

\[
\underbrace{\frac{c_g}{c_p}}_{\substack{\text{atmospheric envelope/carrier ratio}\\\text{rung-specific projection}}}
=\frac{q_a}{1+q_a}=\frac{x_a}{2}.
\]

This explicitly records the transformation between appearances:

\[
\text{water projection}=\frac12+\frac{x}{2},
\qquad
\text{atmosphere projection}=\frac{x}{2}.
\]

The proposed repeated object is the competition coordinate and its equal-contribution crossing, not an assertion that every measured response curve must be numerically identical.

### Frozen prediction 3

Select atmospheric wave observations with independent values of \(f\), \(k\), and equivalent depth or wave speed. Do not estimate these parameters by fitting the response being tested.

- the observed rotation/propagation transition will occur at \(q_a\in[0.5,2.0]\), corresponding to \(x_a\in[0.67,1.33]\);
- the fixed shallow-water projection \(c_g/c_p=x_a/2\) must beat a constant-speed null and a raw-wavenumber pooled model;
- the ARA center may not be moved away from \(q_a=1\);
- results must be reported separately by latitude and wave class before pooling.

Real atmospheric waves include stratification, shear, moisture, and spherical geometry. Systematic failure is evidence against this proposed rung transfer, not permission to add corrections after seeing the result.

## Dataset selection rules

### Liquid datasets

An eligible dataset must provide:

1. at least 20 measured \((k,\omega)\) pairs;
2. points on both sides of the independently calculated \(q_w=1\) crossing;
3. liquid and gas density, surface tension, temperature, and fluid depth;
4. dynamic viscosity, with weak-damping ratio \(2\nu k^2/\omega\le0.10\) at every included point;
5. deep-water condition \(kh\ge3\) at every included point;
6. sufficient wavenumber resolution to estimate \(d\omega/dk\);
7. no surfactant unless surface contamination is explicitly the studied condition.

Minimum target: four distinct liquids and two independent laboratories or publications.

### Atmospheric datasets

An eligible dataset must provide enough information to estimate \(k\), \(\omega\), \(f\), and an independent \(c\) or equivalent depth. Minimum target: 30 wave packets from at least three regions or independent observing campaigns.

## Controls

The following comparisons are mandatory:

1. **Raw scale:** pooled response as a function of dimensional \(k\).
2. **Density only:** response as a function of \(\rho_l\) or \(\Delta\rho\), without surface tension.
3. **One-pole physics:** gravity-only and capillary-only water models; rotation-only and pressure-only atmospheric models.
4. **Flexible ceiling:** a spline fitted inside each system. This is not a fair simple baseline, but shows how much structure remains unexplained.
5. **Permutation:** shuffle fluid properties or atmospheric parameters between records and recompute the collapse.

## Scoring and interpretation

Report MAE, RMSE, median absolute error, crossing location in \(q\), and bootstrap 95% intervals. Report every eligible dataset, including failures.

The evidence levels are deliberately separate:

- **Level A — mathematical embedding:** known interface mechanics can be written on ARA 0–2. Useful, but not novel empirical evidence.
- **Level B — empirical liquid collapse:** measured liquids follow the fixed coordinate without per-liquid tuning. Evidence that the coordinate is practically useful.
- **Level C — rung transfer:** the predeclared operator and center work on held-out atmospheric observations. This is the actual fractal/scale-transfer test.

The scale-transfer claim fails if any of these occur:

- the atmospheric center needs to be moved after inspection;
- density alone performs as well as the full competition ratio;
- success exists only on theoretical or synthetic curves;
- different liquids or atmospheric classes require unrelated coordinate definitions;
- exclusions are chosen after viewing outcomes.

## Plain-language summary

At the smallest level, air and liquid are the two sides. The thin interface between them is the ARA midpoint, and surface tension measures the energetic cost of maintaining that boundary.

At the wave level, long waves are mainly restored by gravity and very short waves mainly by surface tension. Their contributions are equal near a 1.7 cm wavelength for water. Exactly there, the wave pattern and its energy envelope travel at the same speed. That is a real, measurable handover.

At the atmospheric level, molecular surface tension is replaced by a larger-scale competition between rotation and pressure/gravity. The risky ARA claim is that the same 0–2 competition operator still places the transition correctly, even though the measured projection changes. If that only works after moving the center or changing the coordinate, the proposed rung relation has failed.
