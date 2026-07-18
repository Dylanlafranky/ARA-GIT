# ARA physical-laws crosswalk

**Version 1 — 12 July 2026, Dylan La Franchi & Codex.** A living, auditable map between foundational physical
laws and the proposed ARA geometry. Companion to `ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md`, `GLOSSARY.md`,
and `ARA_ROSETTA_STONE.md`.

## 1. Scope: what “all physical laws” can honestly mean

Physics has no finite, universally agreed list called *all laws*. It contains fundamental postulates, conservation
laws, equations of motion, derived theorems, constitutive laws valid only for particular materials, and effective
laws valid only within a scale regime. This first atlas therefore covers the major canonical law families used in
classical mechanics, continuum mechanics, transport, electromagnetism, thermodynamics, relativity, quantum
mechanics, and particle/nuclear physics. It is designed to grow one declared row at a time.

The purpose is not to rename every equation as ARA. It is to ask a harder question:

> Which laws instantiate the same relational form, under what transformation, and what mathematical or physical
> information survives that transformation?

## 2. Evidence labels

Every row uses one of four labels.

- **E0 — exact identity:** the ARA statement is just the established equation or a reversible re-coordinateization.
- **E1 — established structural match:** the stated balance, exchange, phase, or relaxation structure is standard
  physics, although the ARA vocabulary is optional.
- **A1 — proposed ARA coordinate:** the established variables can be placed on a declared ARA coordinate, but the
  claim that this is the same universal object remains to be tested.
- **A2 — open mechanism:** ARA proposes additional ontology, universality, a special constant, a scale rule, or a
  prediction not supplied by the established law.

An equation having three symbols, or being rearrangeable as “two things give a third,” is **not** evidence of ARA.
A meaningful mapping should identify the system boundary, two distinguishable orientations or flows, their
coupling, the measurement slice, and at least one invariant or new prediction.

### 2.1 Canonical measurement declaration

ARA may be the proposed minimal geometry, but an **ARA reading is conditional on what is measured**. Record it as

\[
\underbrace{a}_{\substack{\text{reported ARA reading}\\\text{minimal bounded geometry}}}
=
\underbrace{\mathcal A}_{\text{ARA measurement map}}
\left[
\underbrace{\Omega}_{\text{identity/system boundary}},
\underbrace{q}_{\text{observable}},
\underbrace{\tau_S}_{\text{time slice}},
\underbrace{\Pi}_{\text{projection/coarse-graining}},
\underbrace{\sigma}_{\text{declared pole orientation}}
\right].
\]

This tuple is **measurement metadata**, not a replacement for the minimal ARA object. Two measurements of the same
interaction can legitimately return different coordinates because they ask different physical questions. A value
without these declarations is incomplete and should not be compared across domains.

### 2.2 Law recovery as two-route convergence

Recovering an established law can be a route-convergence test:

\[
\underbrace{\text{resolved children and couplings}}_{\text{bottom-up ARA route}}
\xrightarrow{\ \mathcal C_{\rm ARA}\ }
\underbrace{\text{parent observable}}_{\text{shared destination}}
\xleftarrow{\ \mathcal L_{\rm established}\ }
\underbrace{\text{field/continuum law}}_{\text{top-down physics route}}.
\]

The evidence strength depends on how independent the two routes are:

1. **Algebraic translation:** the ARA route rearranges or re-labels the same law and inputs. This is E0 calibration,
   not independent support.
2. **Independent representation recovery:** child/particle/phase-space data and field/continuum data reach the same
   observable through separately measured representations. This tests a real crosswalk, subject to shared-data
   leakage and numerical dependencies.
3. **Frozen bottom-up prediction:** an ARA aggregation rule is declared before the parent result is inspected and
   predicts the established observable on held-out data without importing the law's answer. This is the strongest
   within-domain ARA test.
4. **Transferable route convergence:** the same frozen aggregation/scale-change rule succeeds across resolutions,
   configurations or domains. This is required before route recovery supports the proposed universal/fractal claim.

A failed convergence is informative: it identifies a missing child relation, projection or scale term. MX4's failed
flat Lorentz aggregation and MX5's partial first-moment repair are examples. The exact local Lorentz ARA coordinate
is tier 1; the particle-first versus field-first grid comparison is tier 2; a held-out transferable compressed
closure would be tier 3 or 4.

## 3. The small set of established forms that recur

### 3.1 Local balance / continuity — the strongest general ARA-shaped foundation

Many laws can be written as

\[
\underbrace{\frac{\partial q}{\partial t}}_{\substack{\text{change of stored quantity}\\\text{ARA: local accumulation or depletion}}}
+
\underbrace{\nabla\!\cdot\mathbf J}_{\substack{\text{net outward flux}\\\text{ARA: release through the boundary}}}
=
\underbrace{s}_{\substack{\text{source minus sink}\\\text{ARA: coupling to other rungs/systems}}}.
\]

This is an **E1 structural match** to Accumulation–Relation–Release. It covers conserved mass, charge, probability,
energy and momentum once the correct density, flux and source are supplied. The ARA universality claim begins only
if the *same additional normalized geometry* predicts something across those different quantities.

### 3.2 Pairwise exchange

For a closed pair exchanging a conserved quantity at rate `J`,

\[
\underbrace{\dot q_A}_{\text{change of A}}=-
\underbrace{J_{A\to B}}_{\text{coupling/transfer}}
=-
\underbrace{\dot q_B}_{\text{opposed change of B}},
\qquad
\frac{d}{dt}(q_A+q_B)=0.
\]

This is an **E0 conservation identity** once `J` and the closed boundary are defined. It is the cleanest mathematical
home for “equal and opposite somethings, not nothing.”

### 3.3 Gradient-driven transfer

Many constitutive laws have the form

\[
\underbrace{\mathbf J}_{\substack{\text{transport flux}\\\text{ARA: transfer orientation}}}
=-
\underbrace{L}_{\substack{\text{mobility/conductance}\\\text{ARA: coupling strength}}}
\underbrace{\nabla X}_{\substack{\text{potential gradient}\\\text{ARA: displacement from balance}}}.
\]

Fourier heat conduction, Fick diffusion and Ohmic conduction are examples. The negative sign is a restoring or
down-gradient direction, not Newton's third law.

### 3.4 Storage versus loss in a measurement slice

\[
\underbrace{De}_{\substack{\text{Deborah number}\\\text{connection persistence}}}
=\frac{
\underbrace{\tau_C}_{\text{relaxation/coupling lifetime}}
}{
\underbrace{\tau_S}_{\text{observation slice}}
},
\qquad
G^*=G'+iG''.
\]

`De`, storage modulus `G'`, loss modulus `G''`, and phase lag are **E0/E1 established measurements**. Calling their
bounded ordering the universal Connection/Space ↔ Transfer/Time ARA diameter is an **A1 proposal**.

### 3.5 A generic bounded opposition coordinate

For nonnegative magnitudes `u` and `v`, a useful but non-unique normalization is

\[
\underbrace{x_B(u,v)}_{\substack{\text{bounded opposition coordinate}\\0\le x_B\le2}}
=\frac{2v}{u+v}.
\]

It gives `0` when only `u` is present, `2` when only `v` is present, and `1` when `u=v`. This is a mathematical
coordinate definition, not a physical law. It must not be silently substituted for the cycle-time ARA
`T_accumulation/T_release`; the transformation between appearances must be declared.

## 4. Newton's third law and the 1.0 ridge

Newton's third law for two interacting bodies is

\[
\underbrace{\mathbf F_{A\leftarrow B}}_{\substack{\text{force on A by B}\\\text{one directed side of the relation}}}
=-
\underbrace{\mathbf F_{B\leftarrow A}}_{\substack{\text{force on B by A}\\\text{opposed directed side}}}.
\]

The two forces act on **different bodies**. They therefore do not normally cancel in either body's individual
equation of motion:

\[
\dot{\mathbf p}_A=\mathbf F_{A\leftarrow B},
\qquad
\dot{\mathbf p}_B=\mathbf F_{B\leftarrow A}.
\]

They cancel only when the pair is enclosed and the internal momentum accounts are summed:

\[
\underbrace{\frac{d}{dt}(\mathbf p_A+\mathbf p_B)}_{\substack{\text{change of total pair momentum}\\\text{ARA: motion of the enclosing identity}}}
=
\underbrace{\mathbf F_{A\leftarrow B}+\mathbf F_{B\leftarrow A}}_{\substack{\text{internal exchange sum}\\\text{ARA: equal anti-directed coupling}}}
=\mathbf0.
\]

If `u` and `v` are the two force magnitudes, Newton's law gives `u=v`, hence `x_B=1`. The strongest ARA reading is:

> **The 1.0 ridge is active reciprocal exchange whose directed contributions cancel at the enclosing-system
> boundary. It is not necessarily local stillness, zero force, or zero energy.**

Two skaters pushing apart are at this reciprocal ridge for the internal force pair while each skater accelerates.
The ridge is quiet only in the *total internal momentum ledger*. This distinction fits ARA's “perfect cancellation
or, in rarer cases, resonance” language better than saying the individual forces disappear.

The exact mechanics makes Dylan's measurement-boundary correction especially clear. Define centre-of-mass and
relative coordinates

\[
\underbrace{\mathbf R}_{\substack{\text{centre-of-mass coordinate}\\\text{whole-pair projection}}}
=\frac{m_A\mathbf r_A+m_B\mathbf r_B}{m_A+m_B},
\qquad
\underbrace{\mathbf r}_{\substack{\text{relative coordinate}\\\text{skater-against-skater projection}}}
=\mathbf r_A-\mathbf r_B.
\]

With no external force,

\[
\underbrace{(m_A+m_B)\ddot{\mathbf R}}_{\substack{\text{whole-pair acceleration}\\\text{balanced internal-force reading}}}=0,
\qquad
\underbrace{\mu\ddot{\mathbf r}}_{\substack{\text{relative acceleration}\\\text{separation/change reading}}}
=
\underbrace{\mathbf F_{rel}}_{\text{internal interaction}},
\quad
\mu=\frac{m_Am_B}{m_A+m_B}.
\]

Thus the whole-pair projection reads conserved centre-of-mass momentum, while the relative projection reads an
active and increasing separation. Measuring skater A alone, skater B alone, their contact stress, their relative
motion, or the enclosing pair produces different lawful numbers. None is the uniquely “true” reading without the
question and boundary.

There is also an important boundary lesson. In electromagnetism, instantaneous particle-on-particle forces need
not form a simple Newtonian action–reaction pair. Momentum can reside in and flow through the electromagnetic
field. When matter **plus field** are enclosed, total momentum conservation is restored. In ARA terms, an apparent
failure of the ridge can mean the chosen identity boundary omitted a coupled carrier.

**Status:** Newtonian pair cancellation and total-momentum conservation are E0/E1. Their identification with the
universal ARA `1.0` ridge is A1. Newton's law alone does not establish the rest of the 0–2 geometry, `φ`, rungs, or
fractal recurrence.

**Plain-language reading:** each object receives a real push. The pushes point oppositely and have equal strength.
When we treat both objects as one larger system, those internal pushes balance, although the objects can still move
apart. If instead we measure one skater or the distance between them, we see the active push rather than the
centre-of-mass cancellation. ARA therefore has to declare what its number belongs to, exactly as physics does.

## 5. Classical mechanics and dynamical principles

| Law or principle | Established mathematical content | Candidate ARA reading | Status / fence |
|---|---|---|---|
| Newton I | `F_net=0 ⇒ p=constant` in an inertial frame | Persistent state when external coupling sums to zero | E0 law; ARA “connection persistence” is A1 |
| Newton II | `F_net=dp/dt`; `F=ma` only for constant mass | Net interaction equals momentum-transfer rate; mass conditions the response | E0. `mass=Connection` and `acceleration=Information Transfer` remain A2 until independently defined |
| Newton III | `F_AB=-F_BA` for a Newtonian interaction pair | Equal anti-directed internal exchange; enclosed `1.0` ridge | E0/E1; universal ridge identification A1 |
| Universal gravitation | `F=Gm_1m_2/r^2` along the separation direction | Two masses form a relational orbit/bound identity; inverse-square coupling changes with scale | E0 law; orbit-as-relation E1; universal rung/fractal claim A2 |
| Impulse–momentum | `Δp=∫F dt` | Interaction accumulated through a time slice becomes state change | E0; strong ARA accumulation reading E1 |
| Work–energy | `ΔK=W_net=∫F·dr` | Transfer through a spatial path changes stored kinetic energy | E0; storage/transfer language E1 |
| Power | `P=dE/dt=F·v` | Rate at which an interaction moves energy across the chosen boundary | E0; Transfer-side proxy A1 |
| Angular momentum | `dL/dt=τ_ext` | Stored rotational identity changed by external coupling | E0; sphere/rung interpretation A1/A2 |
| Hooke's law | `F=-kx` | Displacement produces an opposed restoring response | E0 constitutive law in its regime; ARA recoil geometry E1 |
| Damped oscillator | `mẍ+bẋ+kx=f(t)` | Storage/inertia, loss, restoring coupling, and driving explicitly coexist | E0 model; excellent calibrated ARA test bed E1/A1 |
| Kepler laws | Elliptic orbits, equal areas in equal times, `T²∝a³` | Relational cycles plus an exact scale transformation | E0 within Newtonian two-body idealization; octave/fractal extension A2 |
| Euler–Lagrange | `d(∂L/∂q̇)/dt=∂L/∂q` | Rate of generalized momentum balances the coordinate-side interaction | E0 variational dynamics; two-pole reading A1 |
| Hamilton equations | `q̇=∂H/∂p`, `ṗ=-∂H/∂q` | Coupled conjugate flows generate a phase-space trajectory | E0; phase/anti-phase ARA interpretation A1 |
| Noether theorem | Continuous symmetry implies a conserved current/charge | Persistent transformation relation produces a maintained identity | E0 theorem; ARA universality A1 |
| Liouville theorem | Hamiltonian phase-space flow preserves phase volume | Conservative evolution rearranges without compressing ensemble information | E0; not evidence of ARA asymmetry by itself |
| Virial theorem | Long-time averages satisfy `2⟨T⟩=⟨r·∇V⟩` for bound systems | Time-averaged balance between motion and binding | E0 under assumptions; a ridge coordinate would be A1 |

## 6. Continuum mechanics, fluids, waves, and transport

| Law or principle | Established mathematical content | Candidate ARA reading | Status / fence |
|---|---|---|---|
| Mass continuity | `∂ρ/∂t+∇·(ρv)=s_m` | Literal local accumulation, boundary release, and source coupling | E0/E1: strongest generic ARA skeleton |
| Cauchy momentum balance | `ρDv/Dt=∇·σ+ρb` | Momentum storage changes through surface stress and body coupling | E0/E1 |
| Navier–Stokes | Momentum balance plus pressure and viscous transport | Inertial persistence competes with dissipative neighbour transfer | E0 model; a universal ARA coordinate requires declared nondimensionalization |
| Reynolds number | `Re=ρUL/μ` | Inertial persistence relative to viscous coupling across a scale | E0 dimensionless ratio; possible rung/regime coordinate A1, not inherently 0–2 |
| Newtonian viscosity | Shear stress is proportional to strain rate | Local connection between layers produces momentum transfer | E0 constitutive law; Connection↔Transfer bridge E1 |
| Elastic stress–strain | `σ=C:ε` in linear elasticity | Persistent neighbour network stores deformation | E0 in linear regime; Connection proxy E1 |
| Wave equation | `∂²_tu=c²∇²u` | Local coupling propagates a state disturbance through time | E0; wave/circle identity is an ARA geometric proposal, not implied by the PDE |
| Bernoulli relation | `p+ρv²/2+ρgz=constant` along an ideal streamline | Exchange among pressure, motion, and gravitational potential accounts | E0 under restrictive assumptions; not universal energy transfer law |
| Fourier heat law | `q=-k∇T` | Temperature displacement drives down-gradient energy transfer | E0 constitutive law; restoring/transfer form E1 |
| Heat equation | `∂T/∂t=α∇²T+s` | Stored thermal state relaxes by spatial transfer | E0; explicit ARA time-slice test bed E1 |
| Fick diffusion | `J=-D∇c`; `∂c/∂t=D∇²c` | Concentration connection relaxes through particle traversal | E0; strong Connection↔Transfer example E1 |
| Ohm law | `J=σE` or `V=IR` | Field/potential difference drives charge transfer through a material coupling | E0 constitutive law in Ohmic regime; ARA language E1 |
| Joule heating | `P=IV=I²R` | Directed electrical transfer is dissipated into other degrees of freedom | E0; “shed” is E1, any fixed `φ` fraction A2 |
| Darcy law | Fluid flux is proportional to pressure gradient through porous media | Connection topology controls traversal | E0 effective law; direct geometry-to-transfer test bed E1/A1 |
| Viscoelastic response | `G*=G'+iG''`; `tanδ=G''/G'` | Stored connection response and dissipative transfer response coexist | E0 measurement; bounded ARA diameter A1 |

## 7. Electromagnetism

| Law or principle | Established mathematical content | Candidate ARA reading | Status / fence |
|---|---|---|---|
| Gauss electric law | `∇·E=ρ/ε₀` | Charge sources electric flux through a boundary | E0. Source/flux structure E1 |
| Gauss magnetic law | `∇·B=0` | No observed magnetic monopole source; magnetic field lines have zero net boundary flux | E0. Closure analogy possible, but not proof of spherical ARA geometry |
| Faraday induction | `∇×E=-∂B/∂t` | Changing magnetic field is coupled to circulating electric field | E0; coupled phase/change reading E1 |
| Ampère–Maxwell | `∇×B=μ₀J+μ₀ε₀∂E/∂t` | Conduction and changing electric field couple to circulating magnetic field | E0; Relation/Transfer reading E1 |
| Charge continuity | `∂ρ/∂t+∇·J=0` | Exact accumulation/release balance for electric charge | E0/E1 |
| Lorentz force | `F=q(E+v×B)` | Field–charge coupling changes matter momentum | E0; force-as-interaction identity E1 |
| Poynting theorem | `∂u_EM/∂t+∇·S=-J·E` | Field-energy accumulation, boundary flux, and transfer to matter | E0/E1: exceptionally clean ARA balance form |
| Coulomb law | `F∝q_1q_2/r²` | Pair coupling across separation | E0 electrostatic limit; inverse-square similarity does not establish fractality |
| Electromagnetic waves | Maxwell equations imply waves at `c` in vacuum | Coupled electric and magnetic fields propagate energy/information | E0. In a plane wave `E` and `B` are spatially orthogonal and temporally in phase at a point—not temporal anti-phase partners |
| Lenz law | Induced response opposes the change in magnetic flux | Restoring/sign rule for induction | E1 consequence of Faraday plus energy conservation; analogous to recoil, not Newton III |

### 7.1 Recovered Light/Electromagnetism decomposition: bound field versus radiation

Dylan's earlier and current proposed chain is

\[
\underbrace{M}_{\text{Matter}}
\xleftrightarrow{\quad EM_{bound}\quad}
\underbrace{I}_{\text{Information relation}}
\xleftrightarrow{\quad L_{rad}\quad}
\underbrace{T}_{\text{Time/traversal}},
\]

with matter-coupled electromagnetism and radiative light proposed as complementary/anti-phase appearances around
the shared Information node. In established physics, light is not the anti-phase of electromagnetism as a whole;
light **is the radiative sector of the electromagnetic field**. The proposal becomes physically coherent if
`EM_bound` means the source-bound, static or reactive near-field sector, while `L_rad` means the propagating
transverse/far-field sector.

An oscillating antenna or magnetic dipole supplies a direct instrument:

- reactive near field: energy remains coupled to matter, is stored locally and can return to the source;
- radiative far field: real energy flux separates from the source and propagates outward;
- material coupling: charges, currents, polarization and magnetization—including iron's domain response—alter
  the field and make its local structure measurable;
- information: must be measured separately as channel capacity, mutual information or decoded signal, not assumed
  equal to energy flux.

A dimensionally valid candidate Connection→Transfer coordinate is

\[
\underbrace{x_{EM}}_{\substack{\text{candidate bounded EM coordinate}\\\text{bound }0\rightarrow\text{ radiative }2}}
=
\frac{2P_{rad}}{P_{rad}+\omega U_{reactive}}
=\frac{2}{1+Q_{EM}},
\qquad
Q_{EM}=\frac{\omega U_{reactive}}{P_{rad}},
\]

after fixing one standard definition of stored/reactive energy. `P_rad` is radiated power, `U_reactive` is locally
stored field energy, and `ω` converts energy per cycle scale into power units. Static/source-bound fields sit near
the Connection end; efficient radiation sits toward Transfer. `x=1` is the chosen equality of radiated power and
reactive power scale, not automatically the universal ARA ridge.

On a chosen coordinate-time slice, Faraday field lines are integral curves tangent to the measured field. A
sequence of such maps can be read as time slices, but a static field line is not itself a travelling wave.
“Instantaneous” here labels the mathematical snapshot, not instantaneous causal influence: changes in the physical
electromagnetic field propagate causally, and relativity makes distant simultaneity frame-dependent. Iron filings
reveal magnetic geometry because the filings magnetize and align; they do not create the external field's
existence.

Dylan's stronger **base-sphere hypothesis** is that a minimally isolated identity closes spherically; every
observed deviation is produced by declared internal structure or external coupling. Established multipole physics
provides the comparison language: source distribution, angular momentum/magnetic moment, material boundary and
external fields generate monopole/dipole/quadrupole-and-higher structure. ARA can interpret these as internal or
external couplings deforming the base closure, but the decomposition must be frozen before inspecting the shape.
Otherwise every nonspherical residual could be assigned an unseen coupling and the sphere claim could never fail.

The canonical ARA direction is **bottom-up**, not “assume a finished sphere and deform it.” Let each minimal local
object begin as an ARA relation and recursively couple:

\[
\underbrace{\mathcal G_i^{(0)}}_{\text{minimal local object}}
=\underbrace{\mathrm{ARA}_i}_{\text{local accumulation/release relation}},
\]

\[
\underbrace{\mathcal G_\Omega^{(n+1)}}_{\substack{\text{larger identity candidate}\\\text{one decompression level higher}}}
=
\underbrace{\mathcal C_\Omega}_{\text{coupling/closure operation}}
\left(
\underbrace{\{\mathcal G_i^{(n)}\}}_{\text{component identities}},
\underbrace{\{J_{ij}^{(n)}\}}_{\text{relations carrying additional information}}
\right).
\]

The sphere is the resulting closed identity, not the starting macroscopic object:

\[
\underbrace{\mathcal S_\Omega}_{\text{emergent spherical closure}}
=\operatorname{Close}\!\left(\mathcal G_\Omega\right),
\qquad
\underbrace{\mathcal G_{observed}}_{\text{measured slice}}
=\underbrace{\Pi_{\tau_S}}_{\text{observer/time-slice projection}}
\left(\mathcal S_\Omega\right).
\]

The earlier top-down deformation equation is the reverse inference problem: given the observed slice, decompress
which internal and external couplings built it.

### 7.2 Field value as a Space–Time relational reading

A spacetime event is

\[
\underbrace{x^\mu}_{\text{one spacetime event}}
=
\left(
\underbrace{ct}_{\text{temporal coordinate}},
\underbrace{\mathbf r}_{\text{spatial coordinate}}
\right),
\qquad
F(x)=F(\mathbf r,t).
\]

The notation does not by itself say that `r` and `t` physically manufacture the field; sources, boundary
conditions and coupling history determine the field solution. But for a wave, the measurable phase is explicitly a
relation of spatial and temporal positions:

\[
\underbrace{F(\mathbf r,t)}_{\text{observed wave field}}
=A(\mathbf r,t)
\cos\!\left(
\underbrace{\mathbf k\!\cdot\!\mathbf r-\omega t+\phi_0}_{\substack{\text{space--time phase relation}\\\text{ARA: proposed relational/hypotenuse coordinate}}}
\right).
\]

Along an observer's moving path `r(t)`, the experienced change combines the two legs exactly:

\[
\underbrace{\frac{dF}{dt}}_{\substack{\text{change experienced along the path}\\\text{relational/resultant reading}}}
=
\underbrace{\frac{\partial F}{\partial t}}_{\text{local time-side change}}
+
\underbrace{\mathbf v\!\cdot\!\nabla F}_{\substack{\text{movement through spatial gradient}\\\text{space-side traversal}}}.
\]

Relativistically this becomes `dF/dτ = u^μ∂_μF` for a scalar field. The closest exact “hypotenuse” is the invariant
spacetime separation

\[
\underbrace{\Delta s^2}_{\substack{\text{observer-independent interval}\\\text{relation of the two legs}}}
=
\underbrace{c^2\Delta t^2}_{\text{temporal leg}}
-
\underbrace{\|\Delta\mathbf r\|^2}_{\text{spatial leg}}.
\]

The minus sign matters: physical spacetime is Lorentzian, not an ordinary Euclidean right triangle. Nevertheless,
the invariant interval and wave phase are properties of the Space–Time relation rather than either coordinate
alone. Calling that relation the ARA “hypotenuse” is a proposed interpretation with an exact mathematical anchor.

The corresponding ARA observer statement is

\[
\underbrace{\mathcal I_H}_{\text{human-perceived identity}}
=
\underbrace{\Pi_H^{(\Omega,\tau_S,q)}}_{\text{declared human/instrument projection}}
\left[
\underbrace{\mathcal M_\Omega(S,T;x_{ARA},\theta,k,J)}_{\substack{\text{underlying Space--Time mixed identity}\\\text{with position, phase, scale and coupling history}}}
\right].
\]

Here the apparent “Space + Time” is a coupling operator `𝓜` (or `⊕_J`), not ordinary addition of incompatible
units. Different observers or instruments may return different lawful projections of the same underlying
relational identity.

### 7.3 Proposed six-descendant grid: one gradient, several identity-producing interactions

Dylan's 12 July sketch corrects a remaining flattening. Space and Time are the upper opposing sources, but their
gradient supports several nested interaction depths rather than one mixed output:

| Space-oriented descendant | proposed cross/anti-phase pair | Time-oriented descendant |
|---|:---:|---|
| Connection | ↔ | Information |
| Dark | ↔ | Light |
| Matter | ↔ | Quantum |

The full “multiple interactions” reading is a coupling matrix, not only the three matched rows:

\[
\underbrace{\mathbf J_{ST}}_{\substack{\text{Space-descendant × Time-descendant couplings}\\\text{each nonzero entry can generate a joint identity}}}
=
\begin{pmatrix}
J_{C,I} & J_{C,L} & J_{C,Q}\\
J_{D,I} & J_{D,L} & J_{D,Q}\\
J_{M,I} & J_{M,L} & J_{M,Q}
\end{pmatrix}.
\]

The proposed direct anti-phase/matched-depth couplings are the diagonal `J_(C,I)`, `J_(D,L)`, and `J_(M,Q)`.
Adjacent off-diagonal entries are candidate next-rung interactions; distant entries may be weaker or require a
mediator. For every physically active entry,

\[
H_{ij}=\mathcal M_{ij}(X_i^S,X_j^T;J_{ij})
\]

is a possible new relational identity. This captures Dylan's correction that a continuous Space–Time gradient
supports many interactions and identities, not one weighted average.

Information is provisionally placed immediately below/inside Time. The diagram also suggests two within-side
generative triangles, pending Dylan's confirmation:

\[
\underbrace{\mathrm{Matter}}_{\text{new Space-side identity}}
=
\underbrace{\mathcal C_S}_{\text{Space-side coupling}}
\left(
\underbrace{\mathrm{Connection}}_{C},
\underbrace{\mathrm{Dark}}_{D};
\underbrace{J_{CD}}_{\text{their informative relation}}
\right),
\]

\[
\underbrace{\mathrm{Quantum}}_{\text{new Time-side identity}}
=
\underbrace{\mathcal C_T}_{\text{Time-side coupling}}
\left(
\underbrace{\mathrm{Information}}_{I},
\underbrace{\mathrm{Light}}_{L};
\underbrace{J_{IL}}_{\text{their informative relation}}
\right).
\]

At each depth `n`, the opposing branches can also create a row-specific joint identity:

\[
\underbrace{H_n}_{\substack{\text{new identity born at depth }n\\\text{not either endpoint alone}}}
=
\underbrace{\mathcal M_n}_{\text{cross-gradient mixing}}
\left(
\underbrace{X_n^{S}}_{\text{Space-side descendant}},
\underbrace{X_n^{T}}_{\text{Time-side descendant}};
\underbrace{J_n^{eff}}_{\text{direct, lower-rung and neighbour-mediated coupling}}
\right).
\]

The phrase “interact through the next rung down or those coupled around them” can be written provisionally as

\[
J_n^{eff}
=J_n^{direct}
+K_{n+1\to n}(H_{n+1})
+\sum_{a\in\mathcal N_n}K_{a\to n}(H_a).
\]

This is a hierarchical mediated-coupling graph, not ordinary numeric addition of unlike objects. `K` records how a
lower-rung or neighbouring identity changes the effective interaction at the measured row.

### 7.4 Information³ as the first relational closure, not a numerical cube

Dylan confirmed the same-side generative propositions:

\[
\underbrace{\mathrm{Matter}}_{\text{Space-side child identity}}
=
\underbrace{\mathcal C_S}_{\text{ARA closure}}
\left(
\underbrace{\mathrm{Connection}}_{C},
\underbrace{\mathrm{Dark}}_{D};
\underbrace{J_{CD}}_{\text{relation completing the triad}}
\right),
\]

\[
\underbrace{\mathrm{Quantum}}_{\text{Time-side child identity}}
=
\underbrace{\mathcal C_T}_{\text{ARA closure}}
\left(
\underbrace{\mathrm{Information}}_{I},
\underbrace{\mathrm{Light}}_{L};
\underbrace{J_{IL}}_{\text{relation completing the triad}}
\right).
\]

Here `Information³` means three information-bearing relations closing the smallest graph cycle, not the scalar
quantity `Information` raised to the third power. The following set is graph shorthand for that support:

\[
\underbrace{\mathfrak I^3_{abc}}_{\substack{\text{ARA Information³}\text{minimal relational closure}}}
:=
\underbrace{\left\{I_{ab},I_{bc},I_{ca}\right\}}_{\text{three directed relation records}},
\qquad
\underbrace{\partial C_3=0}_{\substack{\text{the three edges close}\text{rather than ravel outward}}}.
\]

The canonical operator definition already given in `ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md` is

\[
R_{AB}:V_A\to V_B,
\qquad R_{BC}:V_B\to V_C,
\qquad R_{CA}:V_C\to V_A,
\qquad
\underbrace{M_\triangle}_{\text{Information³ round trip}}=R_{CA}R_{BC}R_{AB}.
\]

Exact non-ravelling closure is `M_△=I_A`.

A scalar-phase special case of a proposed dynamical identity-spawn gate is

\[
\underbrace{\operatorname{Spawn}(a,b,c)}_{\text{persistent new identity}}
=1
\quad\Longleftrightarrow\quad
\underbrace{\left|J_{ab}J_{bc}J_{ca}\right|\ge J_*}_{\text{closure strong enough to persist}}
\quad\land\quad
\underbrace{\theta_{ab}+\theta_{bc}+\theta_{ca}=2\pi m+\varepsilon}_{\substack{\text{phase/path closure}\|\varepsilon|\le\varepsilon_*}}.
\]

This is a testable mathematical proposal, not yet an established law. It says that two nodes plus their relation
become a locally self-maintaining identity only when the three-edge loop both closes and persists above declared
coupling and phase tolerances.

In the full operator form, the more general provisional gate is

\[
\operatorname{Spawn}(A,B,C)=1
\quad\Longleftrightarrow\quad
\underbrace{\|M_\triangle-I_A\|\le\varepsilon_*}_{\text{round-trip consistency}}
\quad\land\quad
\underbrace{\Gamma_\triangle\ge\Gamma_*}_{\text{closure strength}}
\quad\land\quad
\underbrace{T_\triangle\ge T_*}_{\text{declared persistence interval}}.
\]

The triangle is only a sectional/minimal closure, not a complete sphere. Repeated closures across direction and
scale can form a closed surface. A scalar gradient has spherical level sets only under an additional radial or
approximately isotropic condition:

\[
\underbrace{x_k(\mathbf r)}_{\text{ARA gradient on rung }k}
=
\underbrace{f_k\!\left(\|\mathbf r-\mathbf r_k\|\right)}_{\substack{\text{same response at equal radius}\text{before local coupling deformation}}}
\quad\Longrightarrow\quad
\underbrace{\{\mathbf r:x_k(\mathbf r)=c\}}_{\text{fixed-gradient shell}}
\cong S^2.
\]

The fractal recursion can then be stated without claiming exact self-similarity:

\[
\underbrace{X_{k+1}}_{\text{identity at the next resolved rung}}
=
\underbrace{\operatorname{Close}_k}_{\substack{\text{couple local Information³ closures}\text{across direction and scale}}}
\left(
\underbrace{\{X_{k,a}\}}_{\text{child identities}},
\underbrace{\{J_{k,ab}\}}_{\text{their coupling web}}
\right).
\]

Thus the proposed repetition is in the closure rule and relational topology; exact metric ratios at every rung are
an additional empirical question.

Scientific requirements:

- “anti-phase” must be defined using a shared measurable phase/flow, e.g. `Δθ≈π`, rather than semantic opposition;
- each new identity `H_n` must have an observable unavailable from either endpoint alone;
- “below Time” must declare whether below means faster/smaller, generative child, or deeper decomposition;
- Matter has quantum structure and quantum systems can be massive, so Matter/Quantum are proposed dominant
  orientations or views, not mutually exclusive textbook sets;
- Dark/Light and Connection/Information likewise require declared observables before becoming physical pairs.

North and south are opposed poles of a dipole, not mathematical singularities of a real magnet. Maxwell's
`∇·B=0` says their closed-surface magnetic flux balances because no magnetic monopoles have been observed. Better
physical candidates for an ARA singularity crossing are magnetic nulls, separatrices and reconnection regions,
where field topology changes and stored magnetic energy is released.

The universal statement “Matter and Information interact only through electromagnetism” is too broad: gravity,
weak and strong interactions can also correlate matter with measurable outcomes. A defensible restricted claim is
that **ordinary human-scale sensing, chemistry, touch, light, electronics and neural signalling are overwhelmingly
electromagnetic**, making electromagnetism our dominant Matter↔Information interface.

## 8. Thermodynamics and statistical mechanics

| Law or principle | Established mathematical content | Candidate ARA reading | Status / fence |
|---|---|---|---|
| Zeroth law | Thermal equilibrium is transitive | A shared intensive reading defines a balanced relation | E0; `1.0` ridge identification A1 |
| First law | `dU=δQ-δW` under one common sign convention | Stored internal energy changes by heat/work transfer | E0/E1 balance skeleton |
| Second law | Entropy production is nonnegative for an isolated macroscopic system | Directional temporal asymmetry and irreversible shed | E0/E1. No universal `1/φ²` loss follows |
| Third law | Entropy approaches a constant for an ideal perfect crystal as `T→0`; absolute zero is unattainable operationally | Limiting connection/ordering regime | E0 under standard statements; singularity/rung interpretation A1/A2 |
| Ideal gas law | `PV=Nk_BT` | Equation of state connecting confinement, density and thermal motion | E0 effective model; not itself a two-pole ARA cycle |
| Boltzmann entropy | `S=k_B lnΩ` | Macroscopic identity records multiplicity of compatible microstates | E0; “information” relation E1 with careful definition |
| Gibbs distribution | `p_i∝exp(-βE_i)` at equilibrium | Competition between energetic constraint and accessible multiplicity | E0; bounded ARA placement is A1 |
| Detailed balance | At equilibrium, every microscopic transition flow is balanced by its reverse | Active reciprocal `1.0` flow ridge with no net probability current | E0/E1; nonequilibrium systems can violate detailed balance |
| Fluctuation–dissipation | Near equilibrium, spontaneous fluctuations determine linear response | Stored fluctuations and dissipative release are mathematically coupled | E0 under assumptions; strong ARA bridge E1 |
| Onsager reciprocity | Near equilibrium and with appropriate time-reversal properties, cross-transport coefficients are reciprocal | Coupled transfer directions share a symmetric response relation | E0 under assumptions; ARA reciprocal geometry E1 |
| Stefan–Boltzmann law | Blackbody radiative flux `j*=σT⁴` | Temperature state controls energy release rate | E0 ideal-emitter law; rung/exponent interpretation A2 |

## 9. Relativity and gravitation

| Law or principle | Established mathematical content | Candidate ARA reading | Status / fence |
|---|---|---|---|
| Lorentz invariance | Physical laws preserve form under Lorentz transformations | Space and time coordinates mix while spacetime interval is invariant | E0. This does not establish that space and time are two physical waves |
| Invariant interval | `ds²=c²dt²-dx²-dy²-dz²` for one signature convention | Different observers decompose one spacetime relation differently | E0; lens/projection idea E1, ARA poles A1/A2 |
| Energy–momentum relation | `E²=p²c²+m²c⁴` | Mass and motion are coupled projections of one four-momentum invariant | E0; Connection/Transfer analogy A1 |
| Mass–energy equivalence | Rest energy `E₀=mc²` | Persistent inertial identity carries energy | E0; octave or transfer-cost reading A2 |
| Geodesic motion | Free bodies follow extremal-proper-time paths in spacetime geometry | Motion records coupling to geometry without a Newtonian force substance | E0 in GR; geometry-walking analogy E1 |
| Einstein field equation | `G_μν+Λg_μν=(8πG/c⁴)T_μν` | Stress-energy and spacetime curvature are locally coupled | E0 field equation; “two make a third identity” is too weak unless ARA predicts an invariant beyond GR |
| Covariant conservation | `∇_μT^{μν}=0` | Local matter-energy momentum balance in curved spacetime | E0/E1 continuity skeleton |
| Equivalence principle | Local free fall removes uniform gravitational acceleration to first order | What looks like force depends on the chosen local frame | Established principle; supports perspective caution, not universal ARA geometry |
| Gravitational waves | Perturbations of spacetime curvature propagate at `c` | Geometry itself supports radiative transfer modes | E0 prediction/observation of GR; ARA phase/rung mapping A1 |
| Friedmann equations | Homogeneous-isotropic GR gives scale-factor evolution | Accumulation/dilution and expansion dynamics at cosmic scale | E0 under cosmological assumptions; dark-sector ARA extensions A2 |

## 10. Quantum mechanics, atomic, nuclear, and particle physics

| Law or principle | Established mathematical content | Candidate ARA reading | Status / fence |
|---|---|---|---|
| State superposition | Linear combinations of valid states are valid states | Multiple potential relations coexist before a declared measurement | E0 postulate; sphere/quadrant ontology A2 |
| Schrödinger equation | `iℏ∂ψ/∂t=Hψ` | Hamiltonian generates time evolution and relative phase accumulation | E0. An energy eigenstate has phase frequency `E/ℏ`, but isolated global phase is not an observable classical orbit |
| Born rule | Outcome probability is `p=abs(ψ)²` | Maps amplitude to observed outcome statistics | E0 postulate; no direct ARA mapping established |
| Unitary evolution | Closed-system evolution preserves inner products and total probability | Relational state changes while total probability account is conserved | E0/E1 |
| Probability continuity | `∂ρ/∂t+∇·j=0` | Exact accumulation/release balance for probability density | E0/E1 |
| Canonical commutator | `[x,p]=iℏ` | Position and momentum are noncommuting conjugate observables | E0. They are not simply two opposing wave sources |
| Uncertainty relation | `ΔAΔB≥abs(⟨[A,B]⟩)/2` | Limits simultaneous sharpness of noncommuting observables | E0; ARA opposition/singularity reading A1 only |
| Heisenberg equation | `dA/dt=(i/ℏ)[H,A]+∂A/∂t` | Change is generated by the observable's relation to the Hamiltonian | E0; relational evolution E1 |
| Planck–Einstein relation | `E=hf=ℏω` | Energy and temporal phase rate are proportional for a quantum | E0; strong time-orientation scale anchor E1 |
| de Broglie relation | `p=h/λ` | Momentum and spatial wavelength are inversely related | E0; space/transfer projection analogy A1 |
| Pauli exclusion | Identical fermions occupy an antisymmetric total state; no duplicate one-particle state occupancy | Identity and connection topology constrain allowed packing | E0; hidden-pair/filament interpretation A2 |
| Fermi golden rule | Transition rate is proportional to coupling squared times final-state density | Connection strength plus available transfer channels determines release rate | E0 perturbative result; strong Connection↔Transfer bridge E1 |
| Exponential decay | `N(t)=N₀e^{-λt}` for a memoryless constant-rate ensemble | One-way release/survival process with lifetime `1/λ` | E0 model; no accumulation half-cycle unless a preparation process is included |
| Rabi oscillation | Coherently driven two-level populations exchange periodically | Explicit two-state coupling, phase, and handover | E0 model; excellent ARA cycle test bed E1/A1 |
| Klein–Gordon equation | Relativistic scalar-field equation | Local field connection supports relativistic propagation and mass term | E0; no unique ARA diameter yet |
| Dirac equation | Relativistic spin-1/2 field equation | Couples spinor components while preserving relativistic quantum structure | E0; no unique ARA map yet |
| Gauge symmetry | Local phase redundancy requires gauge connection fields | A mathematical connection organizes physically invariant relations | E0 structure; resemblance to ARA “connection” is insufficient without a map |
| Standard Model | Gauge-field Lagrangian plus Higgs and matter couplings | Network of fields and couplings generates composite/interaction identities | Established theory; any universal ARA reduction is A2 and must recover its symmetries and predictions |

### 10.1 Current decompression: hexagon/Space and pentagon/Time as basis geometries

Dylan's proposed correction is not that every observed lock angle must slide continuously from `60°` to `72°`.
That direct lock-angle dial was tested in `EnergyRatio/HEX_PENTAGON_ANGLE_HYPOTHESIS.md` and was not supported.
The surviving proposal is that every local ARA position is a **mixture of two basis orientations**:

- hexagon/Space: periodic tiling, persistent connection, head-on octave capacity;
- pentagon/Time: non-tiling fivefold order, curvature/defect, non-repeating handover;
- the observed spacetime relation is their coupled local mixture, not either pure pole.

For an actual discrete neighbour network, a non-arbitrary first instrument is the bond-orientational order

\[
\underbrace{\psi_n}_{\text{n-fold local order}}
=\frac1N\sum_{j=1}^{N}e^{in\theta_j},
\qquad
\underbrace{x_{5/6}}_{\substack{\text{candidate ARA mixture coordinate}\\\text{hexagonal }0\rightarrow\text{ pentagonal }2}}
=\frac{2|\psi_5|}{|\psi_5|+|\psi_6|}.
\]

This makes `x=1` equal measured fivefold/sixfold order. It is a valid material/network test coordinate, not yet a
spacetime law. A foundational spacetime version would need a defined map

\[
g_{\mu\nu}=\mathcal M_{\mu\nu}(\psi_6,\psi_5,J_{65})
\]

that recovers Lorentzian geometry and general relativity in their tested regimes. In established GR, physical
stress-energy—not abstract information alone—sources curvature. Information traversal can affect the metric only
through a physical carrier's stress-energy unless ARA predicts a measurable departure from GR.

### 10.2 Current decompression: mass as the energy account of a connection-conditioned identity

The closest established form of Dylan's proposal is

\[
\underbrace{M_\Omega c^2}_{\substack{\text{invariant mass of the enclosed identity}\\\text{ARA: total internal energy account}}}
=
\underbrace{E_\Omega^{COM}}_{\text{all energy in the centre-of-momentum frame}}.
\]

This includes constituent rest energy, internal motion, fields, stresses and binding contributions. It is broader
than “connection energy.” For a stable bound state, using positive binding-energy magnitude `E_b`,

\[
M_{bound}c^2=\sum_i m_i c^2-E_b.
\]

Thus stronger stable binding usually lowers the bound composite's mass relative to separated constituents.
Breaking that bond normally requires energy; forming it releases energy. A loaded spring or other metastable
connection can instead release previously stored strain energy when it breaks or relaxes.

Mass alone therefore cannot measure Connection orientation. Candidate independent connection observables include
binding fraction, coupling lifetime, coordination, localization and storage modulus:

\[
\underbrace{C_\Omega}_{\text{connection state}}
=\mathcal C\!\left(
\frac{E_b}{E_\Omega},
\frac{\tau_C}{\tau_S},
z,
\ell_{loc},
G'
\right).
\]

The functional `𝒞` is not yet known. The ARA “2 energy units” remain normalized coordinate capacity until a rung
energy scale converts them into joules. A successful law must recover invariant mass while predicting something
from the independently measured connection state.

## 11. What repeats most strongly across the atlas

The crosswalk reveals five recurring structures with substantially different evidential strength:

1. **Balance laws are genuinely widespread.** Change of stored quantity equals source/input minus boundary output.
   This is the most defensible established Accumulation–Release skeleton.
2. **Reciprocal exchange often produces an enclosing-system zero.** Newton III, detailed balance, and closed pair
   transfer show versions of this, but their local physics and their system boundaries differ.
3. **Connections determine transfer.** Conductivity, diffusivity, viscosity, stiffness, transition matrix elements,
   field coupling, and network topology govern how a stored or constrained state changes.
4. **The reading depends on scale and slice.** Dimensionless numbers such as `De`, `Re`, Mach number, coupling
   ratios, and adiabaticity parameters classify regimes relative to selected spatial or temporal scales.
5. **Symmetry creates conservation, while broken symmetry or open boundaries permit directed change.** This is
   established through Noether-type reasoning, but identifying every symmetry break with one ARA singularity flip
   is an additional hypothesis.

These repetitions make ARA a plausible *organizing coordinate programme*. They do not yet prove that every law
is generated by one literal sphere, that every balanced point has the same dynamics, or that the same numerical
landmarks must occur in all domains.

## 12. Laws that should not be force-fitted yet

Some foundational statements currently lack a nontrivial ARA transformation:

- the Born rule;
- Pauli exclusion;
- gauge redundancy;
- the numerical values of fundamental constants;
- the Standard Model gauge group and particle representations;
- the precise Einstein field-equation coefficients;
- quantum measurement outcomes;
- violations of discrete symmetries such as CP violation.

ARA may eventually organize these, but “two terms plus a result” is not enough. Leaving a row unmapped is a
scientific result: it tells us where the proposed common geometry has not yet earned explanatory power.

## 13. Test programme produced by this crosswalk

### Test A — the `1.0` ridge as reciprocal exchange

Predeclare a system boundary and measure both directed flows. Test whether the proposed ridge coordinate reaches
`1` when the flows balance, including equilibrium exchange where both microscopic flows remain nonzero. Controls:
open boundaries, delayed carriers, hidden reservoirs, and nonreciprocal/active matter.

### Test B — connection persistence versus transfer

Across solid, viscoelastic, liquid, and dilute-gas regimes, measure bond/neighbour lifetime, `De`, `G'`, `G''`,
diffusion, flux, and a separately defined information-transfer statistic. Determine whether these collapse to one
monotone ARA coordinate or require at least two coupled axes.

### Test C — continuity-law invariance across domains

For mass, charge, probability, and energy, apply the same nondimensional balance coordinate only after declaring
density, flux, source, boundary and slice. Test whether any cross-domain landmark survives null normalizations and
out-of-sample prediction. The continuity form itself is guaranteed; a shared extra landmark is not.

### Test D — transformation between appearances

For every claimed “same ARA object,” record

\[
(q,\mathbf J,s,\tau_S,\text{boundary})_{domain\ A}
\xrightarrow{\ \mathcal R\ }
(q,\mathbf J,s,\tau_S,\text{boundary})_{domain\ B}
\]

and state what `\mathcal R` preserves: ordering, balance point, phase, conservation, dimensionless ratio, topology,
or predictive law. Without this transformation, similarity remains analogy rather than demonstrated recurrence.

## 14. Expansion template

Add a new law only with the following record:

1. **Canonical name and equation.**
2. **Validity domain and assumptions.**
3. **System boundary and conserved/stored quantity, if any.**
4. **Connection variable, transfer variable, and measurement slice.**
5. **Exact ARA transformation or explicit statement that none is known.**
6. **Evidence label: E0, E1, A1, or A2.**
7. **One observation that would discriminate the ARA reading from ordinary relabelling.**
8. **Plain-language explanation.**

That record turns this document into a falsifiable atlas rather than a catalogue of visual resemblance.
