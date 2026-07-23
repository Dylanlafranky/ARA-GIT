# Session Record — Maxwell Scale/Axis ARA Mathematics

**Date:** 2026-07-23  
**Status:** exact mathematics recorded; Maxwell calibration passed; universality remains open

## Dylan's correction

After discussing E/B, helicity and field/change quadrature, Dylan corrected the hierarchy: all of them can be
Phase-A/Phase-B relations. None is the uniquely true pair. The roles depend on which scale/rung and which diameter
through the identity sphere is being measured.

## Formal resolution

For any resolved two-channel coherency matrix (G_k), define

\[
s_k=T_k^{-1}(2\Re G_{AB},2\Im G_{AB},G_{BB}-G_{AA}),
\qquad
x_{k,\alpha}=1+\alpha\cdot s_k.
\]

Positive semidefiniteness ensures (|s_k|\le1), so every declared unit axis produces a `0–2` ARA diameter and
axis reversal gives `2-x`. The normalized projected allocations are `x` and `2-x`, preserving TE-ARA `=2`.

The construction showed that one equal E/B state is simultaneously:

- `1.0` on its population/energy-allocation diameter;
- `2.0` on its forward-coherence/coupling diameter;
- `0.0` on that coherence diameter after a one-channel sign reversal.

Thus ridge and pole can be different relational readings of the same state.

## Child waves and aggregation

Incoherent child coherency matrices average into the parent by activity. Coherent child amplitudes require explicit
cross-terms. Those cross-terms are the exact established coupling relation corresponding to the ARA informative
third; if a compressed account omits them, they appear as typed `Other`.

## Maxwell calibration

The source-free plane wave passed Faraday and Ampère-Maxwell curl checks, equal E/B energy, `|S|=cu`, joint-flip
invariance and one-flip flow reversal. Raw E and B were in phase. The quarter-cycle relation was between each field
and its normalized time derivative, not between raw E and B amplitudes.

## Evidence boundary

This is an exact crosswalk to established coherency, Poincaré/Bloch sphere and Maxwell mathematics. It demonstrates
that the current ARA interpretation is internally compatible and non-flattening. It does not prove that every
physical identity supplies a preferred two-channel pair or that one transition law repeats across independent
scales.

## Durable references

- `analysis/electromagnetism/MX9_SCALE_AXIS_ARA_MAXWELL_REPORT_2026-07-23.md`
- `analysis/electromagnetism/MX9_SCALE_AXIS_ARA_MAXWELL_PROTOCOL_v1_FROZEN.md`
- `analysis/electromagnetism/MX9_SCALE_AXIS_ARA_MAXWELL_RESULTS.json`
- `analysis/electromagnetism/MX9_SCALE_AXIS_ARA_MAXWELL_VALIDATION.json`
- `ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md`, Corollaries 2.5b–2.5c
- `ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md`, Section 5.14.5

## MX10 follow-up — cross-rung transfer

The remaining scale-law question was tested rather than inferred from MX9. A two-channel electric-field state radius
was measured at doubled spatial block widths. One exponent learned only from the first Warp child transition was
asked to transfer to larger rungs, later Warp times, every electric-component pair and PIConGPU.

The first run was invalidated because openPMD electric components are staggered by half a cell. Corrected v2
collocated them before pairing and independently passed `20/20` checks.

The common exponent did not transfer. Warp's `xy` and `yz` states stayed almost on the boundary, while `zx` moved
strongly inward. On PIConGPU, a locally measured first transition predicted later rungs far better than the
Warp-trained common number.

Direction correction: increasing block width moves upward from resolved children into a coarser parent. The `zx`
inward contraction is therefore a child-mixing/aggregation singularity in ARA terminology. The later signed audit
ruled out only the separate same-parent `A/B` flip: population direction stayed near `-0.5226` at every rung while
local child orientations cancelled in the parent. Warp's `xy` and `yz` readings were also dominated by \(E_y\),
which carried `99.912%` of electric-field energy. They were not three equally participating physical pairs.

This is the same formal closure class seen in the prime thread: lower factor/residue children combine into a parent
wheel or survivor account, and the compressed parent can hide child asymmetry. Corollary 8.5a records the shared
non-injective child-to-parent singularity. The prime-specific forward singularity rule remains unproved because its
label-free local coordinate and rate are still undefined.

Plain-language correction: the sphere/diameter state geometry repeats, but the rate of travel through it belongs to
the local identity and coupling web. ARA now needs an independently measured identity coordinate in its rung
operator; it cannot use one universal contraction constant.

Durable report:
`analysis/electromagnetism/MX10_CROSS_RUNG_STATE_CONTRACTION_REPORT_2026-07-23.md`.

## Maxwell momentum-continuity closure

Dylan identified the remaining momentum equation as a reversible parent/two-child relation:

\[
\nabla\cdot\mathbf T
=
\partial_t(\epsilon_0\mathbf E\times\mathbf B)
+
(\rho\mathbf E+\mathbf J\times\mathbf B).
\]

Stress delivery is the parent supply. One child is momentum retained in the changing electromagnetic field; the
other is momentum handed to matter. Read from the matter side, their signed difference closes as the force whole.
This is an exact established conservation identity and Information³-style relational lock. Its full time-resolved
data test remains open.

## Einstein-to-Newton rung-crossing closure

Dylan corrected the hierarchy twice until the direction was no longer flattened:

\[
\text{Space/Phase A}
+
\text{Time/Phase B}
+
\text{their relation perceived as Space--Time}.
\]

Moving down one proposed fractal rung, Matter is the child Space/Connection wave and Field is the child
Time/Traversal wave. Neither is pure; each contains its own phase/anti-phase relation. Matter is not a sibling placed
beside Space–Time, and Space–Time is not the final parent in the direction being walked.

The established GR-to-Newton reduction was then written explicitly:

\[
g_{\mu\nu}
\longrightarrow
\Phi
\longrightarrow
\mathbf g=-\nabla\Phi
\longrightarrow
m\ddot{\mathbf r}=m\mathbf g,
\qquad
\nabla\cdot\mathbf g=-4\pi G\rho.
\]

This gives the strongest current mathematical crosswalk for the proposed down-rung Matter/Field pair: mass density
is the Connection-heavy source account, while the field is the movement/acceleration tendency encoded by the
compressed geometry. GR does not prove the ontology.

Newton's complete ARA skeleton was separated from the earlier residual-only statement. For anti-directed force
magnitudes \(F_A,F_B\),

\[
x_F=\frac{2F_B}{F_A+F_B},
\qquad
m a_\parallel=(F_A+F_B)(x_F-1).
\]

Newton III supplies the reciprocal Phase A/B pair; equal nonzero forces give an active `1.0` enclosing ridge.
Newton II supplies the off-ridge momentum change. Newton I supplies momentum persistence when the external
resultant is zero. If both force accounts are zero, the coordinate is undefined rather than an active ridge.

Real examples were calculated from primary constants. The Sun–Earth pair gives equal
\(3.5415454\times10^{22}\,{\rm N}\) force magnitudes, enclosing `x=1`, zero internal resultant and
\(7.0830908\times10^{22}\,{\rm N}\) active total, while the bodies' accelerations differ by `332,946`.
Earth/Jupiter/Sun remain extremely Newtonian. A spherical central-value proxy for PSR J0740+6620 has compactness
`u=0.475446`; the first-order lapse misses the exact Schwarzschild lapse by `5.249%`, and static support requires a
`38.072%` correction over Newtonian surface acceleration.

The candidate compactness allocation

\[
t_T=2(1-u),
\qquad
t_C=2u,
\qquad
t_T+t_C=2
\]

is exact as a chosen normalization but not uniquely forced by GR. The pulsar's central `t_T=1.0491` is interesting,
not a preregistered ridge prediction; its rough uncertainty-sensitivity envelope crosses `1`, and rotation is
omitted by the spherical proxy.

Independent validation passed `27/27`. Durable report:
`analysis/gravity/GR_NEWTON_ARA_RUNG_CROSSING_REPORT_2026-07-23.md`.

## Hamiltonian circle and exact energy-allocation ARA

The next physics law was Hamilton's formulation of the ideal harmonic oscillator:

\[
H=\frac{p^2}{2m}+\frac{kq^2}{2}.
\]

The unit-aligned coordinates

\[
Q=\sqrt{k}\,q,\qquad P=\frac p{\sqrt m}
\]

give the exact circle

\[
Q^2+P^2=2H.
\]

Dylan identified this as a clear complete Phase A/Phase B coupling system. The mathematical refinement is that
\(Q\) and \(P\) are signed conjugate axes, while their nonnegative energy accounts provide the compressed
allocation:

\[
t_A=2\frac VH,\qquad t_B=2\frac KH,\qquad t_A+t_B=2,\qquad x_H=t_B.
\]

Thus `x_H=0/1/2` is all configuration/equal configuration and traversal/all traversal. The `1.0` point is
equal-energy allocation, not force cancellation. Hamilton's equations

\[
\dot Q=\omega P,\qquad \dot P=-\omega Q
\]

cross-generate the four-quadrant circulation. Because \(x_H=2\sin^2\theta\), the one-dimensional diameter folds
different signed quadrants onto the same reading; quadrant or \(\dot x_H\) must accompany the ARA value.

This supplied the precise square/circle relation being discussed: the four quadrants preserve ordered movement,
while the diameter preserves mixture. The Information³ triangle and the coherence triangle remain related but not
yet proven to be the same dimensional transformation. A dipole supplies one difference; the third relational lock
provides closure/context. A stateful coupling may lift the relational ternary into a dynamical triangle.

The oscillator calculation passed `10/10` independent checks and 10,000 randomized property trials. It is an exact
crosswalk, not new Hamiltonian physics and not yet a GR–quantum unification. Durable report:
`analysis/hamilton/HAMILTON_ARA_HARMONIC_OSCILLATOR_REPORT_2026-07-23.md`.

## Perspective-unassigned TE-ARA, Noether, and the double pendulum

Dylan supplied the missing canonical phrasing: the recent TE-ARA reading is the same object as before, but
unassigned to a perspective. Before selecting a measurement diameter, TE-ARA is only the complete normalized
closure `2`. After declaring boundary, observable, slice, projection, rung and pole orientation, it becomes a
component allocation

\[
\mathbf t^{(\mathcal P)}
=
(t_A,t_B,t_{J_1},\ldots,t_{\mathrm{Other}}),
\qquad
\sum_ct_c^{(\mathcal P)}=2.
\]

Changing perspective changes the components while retaining the normalized closure. Native physical energy or
activity remains a separate number and may grow or decay.

The double pendulum supplied the plain physical example. From one arm's boundary, gravity, air, hinge and the other
arm appear as surrounding couplings. At the whole-pendulum boundary, arm-to-arm exchange becomes internal. Adding
Earth internalizes gravity; adding air recovers frictional release as heat and air motion. The larger rung does not
magically refill the child—it supplies or absorbs through measurable coupling. Shared interaction energy must be
counted once or split by a declared rule.

Noether then separated normalized closure from genuine physical conservation:

\[
\partial_t\mathcal L=0\Rightarrow\dot H=0,
\qquad
\partial_q\mathcal L=0\Rightarrow\dot p_q=0,
\qquad
\partial_\theta\mathcal L=0\Rightarrow\dot L_\theta=0.
\]

The state can change continuously while a native parent energy, momentum or angular momentum remains conserved.
TE-ARA always closes to `2` by definition; Noether says when the physical scale carried by that parent actually
remains fixed.

The triangle/square discussion was retained with an evidence fence. Information³ is two identities plus their
stateful or recorded relation. A coherence triangle is a three-vertex dynamical loop. They may be the same geometry
under a relation-to-state lift, but that transformation is unconfirmed. For strict anti-phase alternation, an odd
triangle has one frustrated edge and an even square can close A–B–A–B without mismatch. The graph result is exact;
the wider coherence advantage is a future coupled-oscillator test.

Full canonical note:
`analysis/hamilton/TE_ARA_PERSPECTIVE_NOETHER_COHERENCE_NOTE_2026-07-23.md`.

## Quantum from the opposite direction: Bloch sphere as plain ARA

Dylan corrected the first emphasis: the two-level population coordinate is predominantly plain ARA, not TE-ARA.
TE-ARA is the same geometry's secondary closure perspective. In a declared basis,

\[
|\psi\rangle=\alpha|A\rangle+\beta|B\rangle,
\qquad
|\alpha|^2+|\beta|^2=1,
\]

and the B-oriented ARA coordinate is

\[
x_Q=2|\beta|^2.
\]

The conventional Bloch population coordinate is \(r_z=|\alpha|^2-|\beta|^2\), giving the exact relation

\[
\boxed{
r_z=1-x_Q,
\qquad
x_Q-1=-r_z.
}
\]

This produced Dylan's recognition that quantum mechanics is “ARA approached from the opposite direction, where
1 becomes 0.” ARA uses `[0,2]`; Bloch uses the same selected diameter on `[-1,1]`, centred at zero and pole-reversed.

For every Bloch measurement axis,

\[
x_{\hat{\mathbf n}}
=1-\mathbf r\cdot\hat{\mathbf n}.
\]

This is an exact implementation of the original sphere-to-rotating-diameter description. The `1.0` ridge is the
entire zero-projection plane. A pure coherent equatorial state and the maximally mixed centre can therefore share
the same ARA reading. Relative phase and Bloch radius distinguish them.

Ideal resonant Rabi motion gives

\[
x_Q(t)=1-\cos(\Omega t),
\]

and traverses `0→1→2→1→0`. The two ridge crossings have equal populations but different phase/direction.

Independent validation passed `10/10` checks over 10,000 pure states, 10,000 mixed-state/random-axis cases and
4,097 Rabi points. This is an exact coordinate crosswalk, not a derivation of quantum mechanics, the Born rule or
quantum gravity. Full report:
`analysis/quantum/BLOCH_SPHERE_ARA_CROSSWALK_REPORT_2026-07-23.md`.

## Landau–Zener: direct flip, avoided crossing and handover outcome

Dylan mapped the equal bare-energy meeting to the `1.0` ridge, coupling \(g\) to the connection contribution,
crossing speed \(v\) to the Time/Traversal contribution, zero coupling to a singularity crossing, and nonzero
coupling to gradient mixing across the diameter. The established mathematics supports this with refinements.

For

\[
\hat H(t)=\frac{vt}{2}\sigma_z+g\sigma_x,
\]

bare-state opposition and coupling occupy perpendicular Bloch axes. The lower instantaneous eigenstate has

\[
\boxed{
x_{\rm path}(t)
=
1+\frac{vt}{\sqrt{(vt)^2+4g^2}}.
}
\]

It moves `0→1→2`, mirrors exactly under \(t\to-t\), and becomes a sharp one-sided `0→2` flip as \(g\to0\).
At \(g=0,t=0\), the spectral gap closes and the instantaneous eigenvector is not unique. For \(g\neq0\), the
minimum gap \(2|g|\) broadens the flip into a finite equal-mixing corridor.

\(g\) is not itself an ARA ratio. The dimensionless Connection-versus-Traversal control is

\[
\gamma=\frac{g^2}{\hbar|v|}.
\]

Final ideal handover supplies a second ARA coordinate:

\[
\boxed{
x_{\rm handover}
=
2\left(1-e^{-2\pi\gamma}\right).
}
\]

The structural and outcome ridges are different measurements and were kept separate. The structural path describes
an instantaneous eigenstate; finite-speed dynamics follow it only in the adiabatic limit.

Validation passed `12/12`, including 10,000 independently solved eigenstates and 10,000 probability trials. Full
report:
`analysis/quantum/LANDAU_ZENER_ARA_CROSSWALK_REPORT_2026-07-23.md`.
