# Maxwell ↔ ARA completeness audit

**Date:** 12 July 2026  
**Status:** `STRUCTURAL CROSSWALK SUBSTANTIALLY COMPLETE / EMPIRICAL VALIDATION PARTIAL / ENERGY–MOMENTUM CLOSURE MISSING`  
**Orientation:** every bounded 0–2 coordinate below declares its poles locally; reversing them changes labels, not
the invariant result.

## Outcome first

All four Maxwell field equations now have a faithful ARA translation:

1. Gauss electric: signed source balance and independently retained total activity;
2. Gauss magnetic: exact active closed-boundary ridge;
3. Faraday: flux orientation × accumulation/release quadrants and a curl axis;
4. Ampère–Maxwell: conduction/displacement source participation and capacitor handover.

Vacuum plane waves additionally give an exact orthogonal \(E/B/\mathbf S\) triad. However, this is not yet a complete
ARA electrodynamics. Only Gauss electric and its electrostatic plasma consequences have received substantial
data-based development tests. Most later results are exact reparameterisations or structural correspondences, which
establish translation fidelity rather than novel physical evidence.

The most important missing equation is **Poynting's theorem**, because it is the exact local law of field-energy
accumulation, boundary release and transfer into matter. Charge continuity should be handled immediately before it.

## Current coverage

| Component | Current ARA bridge | Evidence level | Remaining gap |
|---|---|---|---|
| Gauss electric | \(Q_{net}=T_Q(x_Q-1)\) | exact algebra; MX1 development positive | frozen independent transfer still sealed |
| Gauss magnetic | \(\Phi_{B,net}=T_B(x_B-1)=0\Rightarrow x_B=1\) for \(T_B>0\) | exact restatement | not evidence for universal ARA; monopole extension unexamined |
| Faraday induction | \((\Phi_B,\dot\Phi_B)\) gives four continuous orientation/change quadrants | exact phase-plane decompression | quadrant construction is generic; no ARA-specific prediction yet |
| Faraday curl | changing-\(B\) axis ↔ circulating \(E\) | exact Maxwell/Stokes geometry | spatial sphere/fractal interpretation untested |
| Ampère–Maxwell | \(\mathbf J_C+\mathbf J_D\), \(x_{D/C}=2D/(C+D)\) | exact channels; proposed normalisation | dielectric/material transfer test not run |
| Capacitor | \(I_C=I_D\) across wire/gap | exact ideal continuity | coherent active ridge, not a singularity or lotto ridge |
| Vacuum plane wave | \(\mathbf B=c^{-1}\hat k\times\mathbf E\), \(\mathbf S=\mu_0^{-1}\mathbf E\times\mathbf B\) | exact declared projection | fails as universal geometry near sources/materials |
| Superconductor | London screening, \(2\pi n\) winding, \(h/2e\), vortices/phase slips | strong established anchor | ARA singularity/rung interpretation untested; general \(\phi\) route unsupported |

## Missing part 1 — charge continuity

Taking the divergence of Ampère–Maxwell and using Gauss electric gives

\[
\underbrace{\frac{\partial\rho}{\partial t}}_{\text{local charge accumulation/release}}
+
\underbrace{\nabla\cdot\mathbf J}_{\text{net charge flow out of the local boundary}}
=0.
\]

This is an exact accumulation–release law and explains why the capacitor's wire current can hand over to displacement
current without breaking the global identity. It should be the next one-equation lesson. It is an established
conservation identity, so mapping it cleanly does not by itself validate ARA universality.

## Missing part 2 — Poynting theorem: highest priority

\[
\underbrace{\frac{\partial u_{EM}}{\partial t}}_{\substack{\text{field-energy storage changing}\\
\text{ARA: local accumulation/release}}}
+
\underbrace{\nabla\cdot\mathbf S}_{\substack{\text{energy crossing the boundary}\\
\text{ARA: outward/inward release or supply}}}
=
-\underbrace{\mathbf J\cdot\mathbf E}_{\substack{\text{field energy transferred to matter}\\
\text{handover/work term}}},
\]

\[
u_{EM}=\frac12\left(\varepsilon_0E^2+\frac{B^2}{\mu_0}\right),
\qquad
\mathbf S=\frac{1}{\mu_0}\mathbf E\times\mathbf B.
\]

This is the missing aggregation and coupling law in its cleanest electromagnetic form. It separates:

- stored field identity;
- boundary flux;
- signed transfer into matter;
- electric and magnetic energy shares;
- residual/Other only after the complete account is closed.

MX2 already verified the electrostatic \(J\cdot E\) exchange and particle-energy response, but the development archive
has no full magnetic field/Poynting output. A full electromagnetic dataset is required.

## Missing part 3 — force and momentum closure

Maxwell fields become mechanics through the Lorentz force density:

\[
\underbrace{\mathbf f}_{\text{force per volume on matter}}
=
\underbrace{\rho\mathbf E}_{\text{electric source coupling}}
+
\underbrace{\mathbf J\times\mathbf B}_{\text{current–magnetic cross coupling}}.
\]

The Maxwell stress tensor and electromagnetic momentum conservation then account for momentum stored in fields,
transported through boundaries and delivered to matter. Until this is mapped, ARA covers field geometry and energy
incompletely but not the full emergence of mechanical force.

## Missing part 4 — observer-safe electromagnetic invariants

Electric and magnetic fields mix under Lorentz-frame changes. The invariant diagnostics are

\[
\underbrace{\mathcal I_1}_{\text{electric- versus magnetic-dominant invariant}}
=E^2-c^2B^2,
\qquad
\underbrace{\mathcal I_2}_{\text{parallel-coupling invariant}}
=\mathbf E\cdot\mathbf B.
\]

A vacuum plane wave has \(\mathcal I_1=\mathcal I_2=0\). These invariants are essential before identifying \(E\) and
\(B\) as universal Space/Time poles: their separate magnitudes are observer-dependent, while the invariants preserve
the field class. A candidate bounded \(E/B\) participation coordinate must retain \(\mathcal I_2\), phase and frame
metadata rather than using energy magnitudes alone.

## Missing part 5 — fields in matter and coarse-graining

The vacuum equations are not enough for chemistry, bodies or engineering materials:

\[
\mathbf D=\varepsilon_0\mathbf E+\mathbf P,
\qquad
\mathbf H=\frac{\mathbf B}{\mu_0}-\mathbf M.
\]

Polarisation \(\mathbf P\), magnetisation \(\mathbf M\), conductivity, dispersion and loss encode the nearby coupled
identities that ARA calls environment/Other. This is the natural place to test coarse-graining: microscopic bound
charges/currents become effective material fields and constitutive laws. The proposed
\(x_{D/C}(\omega)=2\omega\varepsilon/(\sigma+\omega\varepsilon)\) is a first measurable material-gradient test, but
complex phase and frequency-dependent \(\varepsilon,\mu,\sigma\) must be retained.

## Missing part 6 — gauge connection, path and holonomy

\[
\mathbf B=\nabla\times\mathbf A,
\qquad
\mathbf E=-\nabla\varphi-\frac{\partial\mathbf A}{\partial t}.
\]

The vector potential is a genuine mathematical gauge connection and links naturally to the repository's path,
holonomy and superconducting phase work. But \(\mathbf A\) and \(\varphi\) contain gauge redundancy: an ARA result
must use gauge-invariant observables such as fields, flux, phase differences, Wilson loops or fluxoid winding.
Otherwise a coordinate change could be mistaken for physical geometry.

## Missing part 7 — polarisation and helicity: strongest unexamined sphere

Polarisation gives an established sphere—the Poincaré sphere:

- north/south poles: opposite circular helicities;
- equator: linear polarisations;
- intermediate points: elliptical polarisation;
- antipodal points: orthogonal polarisation states.

This is a much stronger mathematical comparison for ARA's sphere/quadrants than merely drawing a sphere around a
field. The Stokes parameters provide measured coordinates, degree of polarisation provides occupancy/purity, and
propagation through matter moves the state on the sphere. The exact map, and whether ARA predicts any additional
landmark or dynamics beyond standard polarisation optics, remain unexamined.

## Missing part 8 — wave generation, causality and near-to-far handover

The current plane-wave mapping begins after radiation already exists. It does not yet explain:

- retarded propagation from sources;
- reactive near-field energy that returns to its source;
- induction and radiation zones;
- conversion to outward Poynting flux;
- boundary reflection/refraction and impedance matching.

The existing candidate

\[
x_{EM}=\frac{2P_{rad}}{P_{rad}+\omega U_{reactive}}
\]

is promising but untested. Antenna simulations or measurements across radius/frequency could test whether one
predeclared bound-to-radiative gradient transfers across geometries.

## Weak or currently overextended connections

1. **\(E=\) Space and \(B=\) Time:** not derived. \(E\) and \(B\) mix under changes of inertial frame.
2. **Universal spherical field identity:** not implied by Maxwell. Point-source wavefronts can be spherical; plane
   waves, dipoles, cavities and bounded fields are not.
3. **General \(\phi\) circulation path:** unsupported. Faraday loops and superconducting winding do not select
   \(\phi\).
4. **Temporal \(E/B\) anti-phase in light:** false for a travelling vacuum plane wave; they are in phase.
5. **Four quadrants as novel evidence:** \((q,\dot q)\) produces four sign regions for any differentiable scalar.
   ARA must predict additional transferable structure to gain evidence.
6. **Zero crossing as a physical singularity:** ARA terminology only unless amplitude/topology actually becomes
   singular or defective, as at a superconducting vortex core or phase slip.
7. **Ampère terms as separate waves or rungs:** not inherent; they are same-unit source channels.
8. **TE-ARA \(=2\) from a complete Maxwell account:** bookkeeping if the denominator is complete by definition.
9. **Gauss magnetic \(x=1\):** exact and useful, but a reparameterisation of \(\nabla\cdot B=0\), not independent
   evidence of universality.
10. **Cross-domain fractality:** not established by repeated vocabulary or exact within-domain identities.

## Recommended order

1. **Charge continuity** — finish the source/handover account.
2. **Poynting theorem** — complete energy accumulation, release and matter handover.
3. **Lorentz force + Maxwell stress** — connect field identity to mechanical force/momentum.
4. **Electromagnetic invariants** — make all later pole/lens claims observer-safe.
5. **Poincaré sphere/polarisation** — inspect the strongest established sphere and double-helicity geometry.
6. **Fields in matter** — operationalise environment/Other and the conduction/displacement gradient.
7. **Near-to-far radiation** — test bound Connection ↔ radiative Transfer.
8. **Gauge/holonomy and superconducting phase slips** — advanced topological layer.

## Best empirical next test

The current Alves/OSIRIS archive is electrostatic and cannot close the full Poynting account. Obtain or generate a
time-resolved electromagnetic dataset containing \(\mathbf E,\mathbf B,\rho,\mathbf J\) on the same grid, plus
particle or material energy. Predeclare:

1. Maxwell residual checks;
2. Poynting local and global closure;
3. electric/magnetic energy participation;
4. boundary flux and \(\mathbf J\cdot\mathbf E\) signed transfer;
5. ordinary energy/coherence baselines;
6. one frozen ARA compression tested on an independent seed/configuration.

That would move the Maxwell branch from a strong structural crosswalk to a genuine empirical ARA test.
