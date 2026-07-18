# Maxwell ↔ ARA completeness audit

**Date:** 12 July 2026; checkpoint updated 13 July 2026
**Status:** `FIELD EQUATIONS + CHARGE + POYNTING STRUCTURALLY COMPLETE / LORENTZ FORCE + MAXWELL STRESS NEXT / EMPIRICAL VALIDATION PARTIAL`
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

Charge continuity is complete as a rung-relative child/parent conservation bridge. Poynting's theorem is now also
structurally recovered as the exact local law of field-energy accumulation, boundary release and transfer into matter.
The next unfinished layer is Lorentz force plus Maxwell stress: momentum stored in fields, transported through
boundaries and handed to matter.

## Current coverage

| Component | Current ARA bridge | Evidence level | Remaining gap |
|---|---|---|---|
| Gauss electric | \(Q_{net}=T_Q(x_Q-1)\) | exact algebra; MX1 development positive | frozen independent transfer still sealed |
| Gauss magnetic | \(\Phi_{B,net}=T_B(x_B-1)=0\Rightarrow x_B=1\) for \(T_B>0\) | exact restatement | not evidence for universal ARA; monopole extension unexamined |
| Faraday induction | \((\Phi_B,\dot\Phi_B)\) gives four continuous orientation/change quadrants | exact phase-plane decompression | quadrant construction is generic; no ARA-specific prediction yet |
| Faraday curl | changing-\(B\) axis ↔ circulating \(E\) | exact Maxwell/Stokes geometry | spatial sphere/fractal interpretation untested |
| Ampère–Maxwell | \(\mathbf J_C+\mathbf J_D\), \(x_{D/C}=2D/(C+D)\) | exact channels; proposed normalisation | dielectric/material transfer test not run |
| Capacitor | \(I_C=I_D\) across wire/gap | exact ideal continuity | coherent active ridge, not a singularity or lotto ridge |
| Charge continuity | \(\dot Q_k=-\oint_{\partial V_k}\mathbf J\cdot d\mathbf A\); shared child interfaces cancel only in the parent external account | exact conservation and scale-relative coarse-graining | no ARA-specific prediction beyond conservation yet |
| Poynting energy continuity | \(\dot u_{EM}=-(\nabla\cdot\mathbf S+\mathbf J\cdot\mathbf E)\); four boundary-flow × matter-handover quadrants and \(x_P=2P_{out}/(P_{in}+P_{out})\) | exact conservation/reparameterisation | full electromagnetic dataset test not run; no independent ARA prediction yet |
| Vacuum plane wave | \(\mathbf B=c^{-1}\hat k\times\mathbf E\), \(\mathbf S=\mu_0^{-1}\mathbf E\times\mathbf B\) | exact declared projection | fails as universal geometry near sources/materials |
| Superconductor | London screening, \(2\pi n\) winding, \(h/2e\), vortices/phase slips | strong established anchor | ARA singularity/rung interpretation untested; general \(\phi\) route unsupported |

## Completed bridge — charge continuity

Taking the divergence of Ampère–Maxwell and using Gauss electric gives

\[
\underbrace{\frac{\partial\rho}{\partial t}}_{\text{local charge accumulation/release}}
+
\underbrace{\nabla\cdot\mathbf J}_{\text{net charge flow out of the local boundary}}
=0.
\]

This is an exact accumulation–release law and explains why the capacitor's wire current can hand over to displacement
current without breaking the global identity. It is also an exact scale lesson: one interface flux is release from one
child, accumulation into its neighbour, and an internal term absent from the enclosing parent's external flux sum.
This is an established conservation identity, so mapping it cleanly does not by itself validate ARA universality.

### 13 July state and scale refinements

- Incoming/outgoing roles are defined by boundary, rung and time window. Maxwell supplies electromagnetic measurement
  variables; the scale-relative classification is also expressible inside ARA.
- An exact parent \(x=1\) is a grain-relative closure, not a final scale-independent state. Child asymmetries may
  cancel in the parent while remaining nonzero under decomposition.
- If an equal two-branch identity exhausts the declared participation account, then
  \(\mathrm{TE}_A=1\), \(\mathrm{TE}_B=1\), \(\mathrm{TE}_{A+B}=2\) while the ARA composition is \(x=1\).
- The joint signature \((x,\mathrm{TE})=(1,2)\) does not distinguish frozen closure, coherent resonance or incoherent
  cancellation. Time variation, flux/activity and phase coherence are required.
- The proposed ARA resonant-death edge case additionally requires identity-holding connection and subthreshold
  adjacent-rung anti-phase response. This is a registered musing, not a Maxwell result.

## Completed bridge — Poynting theorem

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

The completed ARA decompression sets \(b=\nabla\cdot\mathbf S\) and \(m=\mathbf J\cdot\mathbf E\). Their signs give
four exact boundary-flow × matter-handover quadrants. With
\(P_{in}=[-b]_++[-m]_+\) and \(P_{out}=[b]_++[m]_+\), the bounded coordinate
\(x_P=2P_{out}/(P_{in}+P_{out})\) preserves
\(\dot u_{EM}=P_{in}-P_{out}\). This completes the structural recovery; it remains an exact reparameterisation until a
frozen ARA consequence adds held-out information beyond ordinary energy conservation.

## Next part 1 — force and momentum closure

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

## Next part 2 — observer-safe electromagnetic invariants

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

## Next part 3 — fields in matter and coarse-graining

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

## Next part 4 — gauge connection, path and holonomy

\[
\mathbf B=\nabla\times\mathbf A,
\qquad
\mathbf E=-\nabla\varphi-\frac{\partial\mathbf A}{\partial t}.
\]

The vector potential is a genuine mathematical gauge connection and links naturally to the repository's path,
holonomy and superconducting phase work. But \(\mathbf A\) and \(\varphi\) contain gauge redundancy: an ARA result
must use gauge-invariant observables such as fields, flux, phase differences, Wilson loops or fluxoid winding.
Otherwise a coordinate change could be mistaken for physical geometry.

## Next part 5 — polarisation and helicity: strongest unexamined sphere

Polarisation gives an established sphere—the Poincaré sphere:

- north/south poles: opposite circular helicities;
- equator: linear polarisations;
- intermediate points: elliptical polarisation;
- antipodal points: orthogonal polarisation states.

This is a much stronger mathematical comparison for ARA's sphere/quadrants than merely drawing a sphere around a
field. The Stokes parameters provide measured coordinates, degree of polarisation provides occupancy/purity, and
propagation through matter moves the state on the sphere. The exact map, and whether ARA predicts any additional
landmark or dynamics beyond standard polarisation optics, remain unexamined.

## Next part 6 — wave generation, causality and near-to-far handover

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

1. **Charge continuity — COMPLETED:** source/handover and child/parent scale account.
2. **Poynting theorem — STRUCTURAL RECOVERY COMPLETED:** energy accumulation, release and matter handover.
3. **Lorentz force — LOCAL CROSSWALK COMPLETE / CHILD CLOSURE PARTIAL; Maxwell stress — NEXT:** connect field identity to mechanical momentum transport.
4. **Electromagnetic invariants:** make all later pole/lens claims observer-safe.
5. **Poincaré sphere/polarisation:** inspect the strongest established sphere and double-helicity geometry.
6. **Fields in matter:** operationalise environment/Other and the conduction/displacement gradient.
7. **Near-to-far radiation:** test bound Connection ↔ radiative Transfer.
8. **Gauge/holonomy and superconducting phase slips:** advanced topological layer.

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

## 14 July 2026 addendum — MX4 Lorentz-force data crosswalk

The next force step was run on the official openPMD example repository's PIConGPU 0.5.0 electromagnetic snapshot.
The source supplies a (32^3) Yee grid, all components of (mathbf E) and (mathbf B), and 225,449 electron plus
225,280 ion position/momentum records. The protocol was frozen before calculating the force outcomes.

At the particle rung, define

\[
\mathbf f_E=q\mathbf E,
\qquad
\mathbf f_B=q(\mathbf v\times\mathbf B),
\qquad
x_F=\frac{2|\mathbf f_B|}{|\mathbf f_E|+|\mathbf f_B|},
\qquad
c_F=\cos\angle(\mathbf f_E,\mathbf f_B).
\]

Together with (S_F=|\mathbf f_E|+|\mathbf f_B|), the tuple ((x_F,S_F,c_F)) reconstructed the Lorentz resultant
with relative errors (1.34\times10^{-16}) for both species. Magnetic-work leakage and the identity
(mathbf v\cdot\mathbf f=\mathbf v\cdot\mathbf f_E) were also at floating-point zero. This completes the local
Lorentz translation, but it remains an exact reparameterisation of established physics rather than independent ARA
evidence.

The frozen particle-to-grid bridge failed. Calculating particle forces and then depositing them did not agree with
depositing (ho,mathbf J) separately and then calculating (ho\mathbf E+mathbf J\times\mathbf B): total vector
correlation (0.477), NRMSE (0.888), median direction error (61.7^\circ). A post-freeze quadratic-deposition
sensitivity recovered the stored total charge density at (r=0.9999999996) but left the force bridge worse
((r=0.405)). The failure is therefore not explained by incorrect charge deposition.

The missing established terms are the subgrid relations

\[
\langle\rho\mathbf E\rangle
=\langle\rho\rangle\langle\mathbf E\rangle+\langle\rho'\mathbf E'\rangle,
\qquad
\langle\mathbf J\times\mathbf B\rangle
=\langle\mathbf J\rangle\times\langle\mathbf B\rangle+\langle\mathbf J'\times\mathbf B'\rangle.
\]

This rejects the naïve ARA aggregation operator that carries only separate parent averages. In ARA terms, the
within-cell child relation is a measurable candidate for `Other`; a successful ARA rung law must predict or retain
it. Merely adding the full covariance back is standard closure bookkeeping. A new ARA result would require a frozen
compressed rule that predicts it on held-out data.

Lorentz-force status is now:

- `LOCAL PARTICLE-RUNG CROSSWALK COMPLETE`;
- `NAIVE GRID-RUNG OPERATOR FAILED`;
- `SUBGRID/COVARIANCE REQUIREMENT IDENTIFIED`;
- `MOMENTUM-CONTINUITY/MAXWELL-STRESS TEST STILL OPEN`;
- `FINITE-DIFFERENCE PARTICLE ACCELERATION CONFIRMATION NOT RUN — ONE SNAPSHOT`.

Full packet: `analysis/electromagnetism/MX4_LORENTZ_ARA_DATA_REPORT.md`.

## 14 July 2026 addendum — MX5 child identities and partial moment closure

MX5 froze three versions after the MX4 parent-averaging failure. Exact child-ARA vector reassembly passed at
(3.99\times10^{-15}) relative grid error, while flat parent plus exact `Other` passed at
(9.44\times10^{-17}). These are identity checks, not independent ARA evidence.

The useful Maxwell/plasma resolution came from a dimensionless force/activity TE-ARA analogue. A post-freeze
descriptive species drill, not an outcome gate, found electron and ion internal coherence medians of (1.2175/2)
and (1.1449/2), while their species-level forces had an almost exact
ridge magnitude coordinate (1.00023), a median angle (177.55^\circ), and pair coherence only (0.07184/2).
Thus a quiet whole can contain two active, nearly cancelling force identities. This is established plasma balance
made visible by explicit grain-aware bookkeeping.

Exact `Other` exceeded the flat-parent magnitude in (78.99\%) of active cells. An unfitted first
position-moment/field-gradient approximation improved the total comparison from correlation (0.4771), NRMSE
(0.8878), angle (61.68^\circ) to (0.6045), (0.8019), (48.47^\circ). Both spatial halves agreed. This is
`PARTIAL COMPACT RECOVERY`; it misses the stronger frozen gates, and its correction correlates only (0.4310) with
exact `Other`.

Maxwell status is therefore refined to:

- local Lorentz ARA crosswalk: complete as exact reparameterisation;
- child/parent identity decomposition: demonstrated on one snapshot;
- first compact subgrid moment: useful but incomplete;
- Maxwell stress/momentum continuity: still open;
- time-resolved acceleration and independent transfer: still open.

Full packet: `analysis/electromagnetism/MX5_CHILD_ARA_TEARA_CLOSURE_REPORT.md`.
