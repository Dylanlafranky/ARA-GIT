# TE-ARA perspective, Noether invariants, and coherence closure

**Date:** 23 July 2026  
**Status:** canonical ARA clarification plus exact established-mathematics crosswalks  
**Purpose:** preserve the discussion connecting the Hamiltonian parent cycle, perspective-relative TE-ARA
allocation, Noether conservation, Information³, triangular closure, even-cycle coherence, and the double-pendulum
boundary example.

## 1. Settled canonical distinction

TE-ARA is not a second object beside ARA. It is the same geometry read as complete identity allocation. Before a
measurement perspective is selected, only the closure is assigned:

\[
\underbrace{\mathrm{TE\!-\!ARA}}_{\substack{\text{complete identity closure}\\\text{before selecting a diameter}}}
=2.
\]

This is the sphere before choosing a diameter. It has no A/B component values until a perspective is declared.

Let

\[
\mathcal P=(\Omega,q,\tau_S,\Pi,k,\sigma)
\]

declare the identity boundary, observable, time slice, projection, rung and pole orientation. The instantiated
allocation is

\[
\boxed{
\underbrace{\mathbf t^{(\mathcal P)}}_{\substack{\text{TE-ARA allocation}\\\text{from perspective }\mathcal P}}
=
\left(t_A,t_B,t_{J_1},\ldots,t_{J_n},t_{\mathrm{Other}}\right),
\qquad
\sum_c t_c^{(\mathcal P)}=2.
}
\tag{1}
\]

Changing perspective changes the components:

\[
\mathbf t^{(\mathcal P')}
=
\mathcal R_{\mathcal P\rightarrow\mathcal P'}
\left(\mathbf t^{(\mathcal P)}\right),
\qquad
\sum_c t_c^{(\mathcal P')}=2.
\tag{2}
\]

Equation (2) does not say that every component survives unchanged. A child coupling can become an internal parent
term, an unresolved `Other` can become a named edge, or several children can coarse-grain into one parent
component. What remains fixed is the canonical normalized closure.

## 2. Four quantities that must not be flattened

| Quantity | Meaning | Can it vary? |
|---|---|---|
| TE-ARA closure | The uninstantiated complete account | Fixed at `2` |
| TE-ARA allocation | Component vector after choosing perspective | Yes |
| ARA coordinate | One selected two-pole diameter through that allocation | Yes, on `0–2` |
| Physical magnitude | Energy, activity, flux, mass or another native amount | Yes, in native units |

The total `2` is a normalization. It does not mean that every identity contains the same number of joules or the
same physical activity. A system can be normalized to `2` while its physical energy grows or decays.

For a declared energy ledger,

\[
t_c=2\frac{E_c}{E_{\mathrm{account}}},
\qquad
\sum_cE_c=E_{\mathrm{account}},
\qquad
\sum_ct_c=2.
\]

The nontrivial scientific work lies in predeclaring the component boundaries, preventing overlap and double
counting, measuring the native amounts, and testing whether the transformation between perspectives preserves or
predicts anything beyond the guaranteed normalization.

## 3. Hamiltonian parent across the quadrant cycle

For the ideal harmonic oscillator,

\[
H=K+V=\frac{p^2}{2m}+\frac{kq^2}{2},
\qquad
Q=\sqrt{k}\,q,
\qquad
P=\frac p{\sqrt m},
\]

so

\[
Q^2+P^2=2H.
\]

The energy-allocation appearance is

\[
t_A=2\frac VH,
\qquad
t_B=2\frac KH,
\qquad
t_A+t_B=2.
\]

The full oscillator is the parent. Its four signed quadrants,

\[
(+Q,+P)\rightarrow(-Q,+P)\rightarrow(-Q,-P)\rightarrow(+Q,-P),
\]

are directional states of that parent, not automatically four independent identities. Hamilton's equations

\[
\dot Q=\omega P,
\qquad
\dot P=-\omega Q
\]

cross-generate the continuous circulation.

The compressed ARA diameter

\[
x_H=t_B=2\frac KH
\]

records mixture but loses the signs of \(Q\) and \(P\). The parent state therefore requires the quadrant or
\(\dot x_H\) as well. If a quadrant is selected as a new boundary and decompressed, it can then receive its own
child A/B allocation and total-2 ledger. This is the proposed fractal walk:

- around: change phase/quadrant within one parent;
- inward/downward: decompress into children;
- outward/upward: coarse-grain into a larger parent;
- sideways: form a neighbouring coupling and possible new relational parent.

The direction names are relational and must always be tied to a declared axis.

## 4. Noether distinguishes closure normalization from physical conservation

TE-ARA totals `2` by canonical normalization. Noether's theorem supplies the separate, stronger physical question:
does a native physical amount actually remain conserved under a continuous symmetry?

### 4.1 Time translation

\[
\underbrace{\frac{\partial\mathcal L}{\partial t}=0}_{\substack{\text{laws unchanged by}\\\text{shifting the clock origin}}}
\quad\Longrightarrow\quad
\underbrace{\frac{dH}{dt}=0}_{\text{energy conserved}}.
\]

The state can move vigorously while the parent energy remains fixed. For a two-account closed oscillator,

\[
\dot H_A+\dot H_B=0.
\]

This is not the tautology “if the state does not change, it stays the same.” The state changes; the equations do
not depend on absolute time, and the associated Noether charge is conserved.

### 4.2 Spatial translation

\[
\underbrace{\frac{\partial\mathcal L}{\partial q}=0}_{\substack{\text{laws unchanged along}\\\text{the declared spatial direction}}}
\quad\Longrightarrow\quad
\underbrace{\frac{d}{dt}
\left(\frac{\partial\mathcal L}{\partial\dot q}\right)=0}_{\dot p_q=0}.
\]

If no position along the declared axis is physically preferred, momentum along that axis is conserved.

### 4.3 Rotation

\[
\underbrace{\frac{\partial\mathcal L}{\partial\theta}=0}_{\substack{\text{laws unchanged}\\\text{under rotation}}}
\quad\Longrightarrow\quad
\underbrace{\frac{d}{dt}
\left(\frac{\partial\mathcal L}{\partial\dot\theta}\right)=0}_{\text{angular momentum conserved}}.
\]

Rotating the measurement diameter can change the coordinate description without changing the conserved
angular-momentum whole.

The ARA–Noether crosswalk is therefore:

| Transformation | Established conserved quantity | ARA reading |
|---|---|---|
| Shift through time | Energy | Physical scale of the parent can remain fixed while allocation circulates |
| Shift through space | Linear momentum | Movement of the identity preserves a directional physical charge |
| Rotate the system | Angular momentum | Diameter/perspective can rotate while a parent physical invariant survives |

Noether does not prove TE-ARA or universal ARA geometry. It tells us which physical magnitude survives a declared
symmetry transformation; TE-ARA separately records the normalized composition.

## 5. Double pendulum: the same whole from several rungs

At the boundary of one arm or bob \(i\), a schematic physical-energy balance is

\[
\underbrace{\frac{dE_i}{dt}}_{\text{child energy change}}
=
\underbrace{P_{g,i}}_{\text{gravity exchange}}
+
\underbrace{P_{\mathrm{joint},i}}_{\text{other arm/hinge coupling}}
+
\underbrace{P_{\mathrm{drive},i}}_{\text{external supply}}
-
\underbrace{P_{\mathrm{air},i}}_{\text{frictional release}}.
\tag{3}
\]

The corresponding normalized perspective can be written

\[
\mathrm{TE\!-\!ARA}_i
=t_{A_i}+t_{B_i}
+\sum_jt_{J_{ij}}
+t_{\mathrm{Other},i}
=2.
\tag{4}
\]

The component values change during the cycle; the total does not. The native child energy \(E_i(t)\) must be
retained separately.

Moving the boundary changes the ledger:

1. **One arm:** the other arm, hinge and gravity appear as surrounding couplings.
2. **Whole pendulum:** arm-to-arm exchange becomes internal and cancels from the parent net balance.
3. **Pendulum plus Earth:** gravitational exchange becomes internal.
4. **Pendulum plus Earth plus air:** apparent frictional loss reappears as heat and air motion.
5. **Sufficiently closed parent:** the full physical energy account satisfies its conservation law.

A higher rung does not magically replace lost energy. It supplies or absorbs energy through measurable coupling.
What looked missing at the child boundary reappears as a component of the expanded parent.

**Non-double-counting rule:** a shared interaction must be recorded once in the parent ledger or split between
children by a predeclared allocation rule. Assigning the same joint energy fully to both children makes the
TE-ARA decomposition invalid.

## 6. Information³, the coherence triangle, and the square

The minimal relational ternary is

\[
\mathcal I^3(A,B)=\left(A,B,J_{AB}\right).
\]

It contains two identities plus their retained relation. The third term is not automatically a third independent
wave or state.

A dipole supplies one difference:

\[
d_{AB}=B-A.
\]

It can carry polarity, separation or phase information, but it cannot self-contextualize every change. A third
relational lock can close the consistency route:

\[
d_{AB}+d_{BC}+d_{CA}=0.
\]

This permits detection and constraint of a broken relation; it does not guarantee reconstruction of an arbitrary
destroyed node.

The Information³ ternary and a dynamical coherence triangle are related but not yet proven to be the same
dimensional transformation. They become equivalent under a specific model if \(J_{AB}\) acquires its own state,
memory and dynamics and can be promoted to a third vertex:

\[
(A,B,J_{AB})
\longrightarrow
A\leftrightarrow J_{AB}\leftrightarrow B\leftrightarrow A.
\]

Under strict two-state anti-phase alternation,

\[
s_{i+1}=-s_i
\quad\Longrightarrow\quad
s_1=(-1)^n s_1.
\]

Perfect closure therefore requires even \(n\). A triangle is the smallest simple closed network, but its odd cycle
forces one frustrated anti-phase edge. A square permits

\[
A\rightarrow B\rightarrow A\rightarrow B\rightarrow A
\]

without that mismatch. The resulting careful claim is:

- the triangle is a candidate minimum self-closing coherence structure and may generate an informative mismatch;
- the square is the smallest closed loop permitting perfect two-phase alternation and therefore a candidate for
  steadier repeated coherent transfer;
- this does not mean every triangle is dynamically worse than every square;
- the Information³ ternary and coherence triangle remain related-but-unconfirmed manifestations.

## 7. What is now settled and what remains open

### Settled inside the framework

- TE-ARA closure `2` is perspective-unassigned.
- An observed TE-ARA allocation is perspective-bound.
- One ARA coordinate is a selected two-pole diameter through that allocation.
- Native physical magnitude is separate.
- Parent, child and quadrant are relational roles rather than permanent object types.
- Shared coupling accounts cannot be double-counted.

### Exact established crosswalks

- The harmonic oscillator becomes \(Q^2+P^2=2H\) after an invertible unit-aligned rescaling.
- Noether time, spatial and rotational symmetries imply conservation of energy, momentum and angular momentum.
- Odd anti-phase cycles are frustrated; even cycles admit perfect alternation.

### Open ARA claims

- that the perspective-unassigned closure is a literal universal physical sphere rather than a normalization;
- that every domain admits one predictive transformation \(\mathcal R\) between ARA appearances;
- that Information³ and the dynamical triangle are one dimension-shifted geometry;
- that square closure generally increases measured coherence across physical scales;
- and that this structure supplies a GR–quantum unification.

The next strong test for the triangle/square distinction is a frozen comparison of otherwise matched three-node
and four-node coupled oscillators, measuring phase frustration, coherence duration and circulating transfer. The
next physics crosswalk after Hamilton and Noether is the quantum two-level/Rabi–Bloch sphere, where state-sphere
geometry and coherent exchange are independently established.

