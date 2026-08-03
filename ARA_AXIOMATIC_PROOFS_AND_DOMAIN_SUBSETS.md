# ARA axiomatic mathematics and domain subsets

**Author:** Dylan La Franchi, with formalisation assistance from Codex  
**Date:** 11 July 2026  
**Centered revision:** 4:00 pm AEST, 19 July 2026
**Prime-sieve subset closure:** 21 July 2026
**Shared-ruler projection amendment:** 22 July 2026

**Status:** Mathematical foundation draft, revised after the 19 July 2026 centering audit. Internally proved
statements are separated from physical hypotheses.

## What this document can and cannot prove

Mathematics can prove that consequences follow from stated assumptions. It cannot, by itself, prove that every
physical system in the universe obeys those assumptions. This document therefore uses four labels:

- **Definition:** fixes the meaning of a symbol.
- **Theorem:** follows deductively from the definitions and axioms given here.
- **Conditional proposition:** is proved if an additional ARA modelling assumption is accepted.
- **Empirical hypothesis:** must be decided using observations or experiments.

The rigorous claim made here is:

> ARA has a consistent mathematical core in which one proposed spherical/wave identity can be read along a
> reversible 0–2 diameter. Declared scalar instruments can locate an asymmetric occurrence on that diameter;
> direction, activity, phase, scale and coupling supply the information discarded by the scalar. Two identities
> plus their retained relation form a minimal relational ternary that can, under additional closure assumptions,
> aggregate into a higher-level identity.

The larger claim—that nature uses this structure universally—remains empirical.

### Repository terminology and evidence anchors

This draft uses the current terminology in [`GLOSSARY.md`](GLOSSARY.md), [`ARA_SCALE.md`](ARA_SCALE.md),
[`ARA_decomposition_rules.md`](ARA_decomposition_rules.md), [`ARA_ROSETTA_STONE.md`](ARA_ROSETTA_STONE.md), and
[`TWO_RULERS_PHI_AND_TWO.md`](TWO_RULERS_PHI_AND_TWO.md). Domain-specific starting points are
[`EnergyRatio/HEX_PENTAGON_ANGLE_HYPOTHESIS.md`](EnergyRatio/HEX_PENTAGON_ANGLE_HYPOTHESIS.md),
[`LLM/LLM_INFO_CUBED_RESULT.md`](LLM/LLM_INFO_CUBED_RESULT.md),
[`LLM/LLM_CLOSURE_HALLUCINATION_RESULT.md`](LLM/LLM_CLOSURE_HALLUCINATION_RESULT.md), and
[`ARA_Fusion_Theory.md`](ARA_Fusion_Theory.md). Numerical claim status should still be checked against
[`CLAIMS_STATUS.md`](CLAIMS_STATUS.md).

The controlling construct-fidelity audit for this revision is
[`FableConvo/CENTERING_UP_REPORT_2026-07-19_1600.md`](FableConvo/CENTERING_UP_REPORT_2026-07-19_1600.md).

---

# Part I — Minimal ARA mathematics

## 0. The whole object and its minimal diameter reading

### Definition 0.1 — ARA object and diameter chart

ARA proposes one complete local spherical/wave identity, written

\[
\underbrace{\mathscr A_\Omega}_{\substack{\text{whole local ARA occurrence}\\
\text{with identity }\Omega}}.
\]

Choosing one direction \(\hat n\) supplies a diameter chart

\[
\underbrace{\chi_{\hat n}(\mathscr A_\Omega)}_{\substack{\text{one directional projection}\\
\text{ARA diameter reading}}}
=
\underbrace{x_{\hat n}\in[0,2]}_{\substack{\text{bounded position}\\
\text{between declared poles}}}.
\tag{0}
\]

The scalar is the smallest directional measurement of the object, not a replacement definition of the whole
object. A physical observation normally also declares its boundary, pole ordering, observable, time window,
direction, rung, phase, path, coupling, activity/energy and variance/coherence. Those fields decompress the same
ARA occurrence; they do not create a different kind of ARA.

In strict mathematical language, \(S^2\) is a spherical boundary and \(B^3\) is the boundary plus its interior. In
ordinary ARA language, “sphere” may name the complete closed identity. This document uses both symbols whenever the
shell/interior distinction matters. The exact ball, section and diameter construction is proved in §2.1. The
physical claim that a natural identity instantiates this spherical closure remains empirical.

### Definition 0.2 — Pole reversal and centred asymmetry

For one declared orientation \(A\to B\), define the reverse chart and centred coordinate by

\[
\underbrace{x_{B\to A}}_{\text{same diameter read backwards}}
=2-
\underbrace{x_{A\to B}}_{\text{declared forward reading}},
\qquad
\underbrace{a}_{\substack{\text{centred asymmetry}\\\text{side and distance from ridge}}}=x-1.
\]

The chart is symmetric under relabelling, while a measured occurrence may be asymmetric in mixture, duration,
rate, force, path, phase or coupling history. Coordinate reversibility does not by itself imply physical time
reversibility.

**Plain explanation.** ARA begins with the complete wave/sphere. The 0–2 line is one diameter through it. We may
name either end zero, as with electrical polarity, provided the orientation is declared. Reversing the labels
mirrors the coordinate, but it does not erase the real asymmetry being measured.

## 1. A duration-axis instantiation of the ARA diameter

Let

\[
\overbrace{T_A}^{\substack{\text{accumulation duration}\\\text{ARA: time spent building}}}>0,
\qquad
\overbrace{T_R}^{\substack{\text{release duration}\\\text{ARA: time spent releasing}}}>0.
\]

The raw timing ratio is

\[
\overbrace{r}^{\substack{\text{ordinary ratio}\\\text{raw ARA timing ratio}}}
=\frac{T_A}{T_R}.
\]

Define the bounded ARA coordinate by twice the accumulation fraction:

\[
\boxed{
\overbrace{x_T}^{\substack{\text{bounded duration coordinate}\\\text{ARA duration-axis position}}}
=2\frac{T_A}{T_A+T_R}
=\frac{2r}{1+r}
}
\tag{1}
\]

This is the canonical **duration-axis** `2 × accumulation fraction` normalisation already used in the repository's
corrected LLM work. It is one valid diameter instrument, not the universal definition of every ARA position.
Orientation—whether the system is travelling accumulation→release or release→accumulation—is recorded separately
when motion matters. For compactness, write \(x=x_T\) throughout Theorem 1 and its duration corollaries.

Other domains may define a composition, signed-flux, occupancy or another typed diameter instrument. Such a bridge
must name its poles, boundary and observable before inspecting the outcome; preserve \(x\mapsto2-x\) under pole
reversal; retain a separate activity/magnitude coordinate; and predict something beyond the fact that an arbitrary
ratio can be rescaled to `[0,2]`.

### Theorem 1 — Boundedness, balance, mirror symmetry, and invertibility

For all positive phase durations:

1. \(0<x<2\).
2. \(x=1\) if and only if \(T_A=T_R\).
3. Swapping accumulation and release gives \(x(T_R,T_A)=2-x(T_A,T_R)\).
4. The raw ratio can be recovered uniquely by \(r=x/(2-x)\).
5. The asymmetry magnitude \(|x-1|\) is unchanged by the swap.

**Proof.** Because \(T_A,T_R>0\),

\[
0<\frac{T_A}{T_A+T_R}<1.
\]

Multiplication by two proves \(0<x<2\). Next,

\[
x=1
\iff 2T_A=T_A+T_R
\iff T_A=T_R.
\]

For the mirror,

\[
x(T_R,T_A)
=\frac{2T_R}{T_A+T_R}
=2-\frac{2T_A}{T_A+T_R}
=2-x(T_A,T_R).
\]

Starting from \(x=2r/(1+r)\),

\[
x(1+r)=2r
\iff x=r(2-x)
\iff r=\frac{x}{2-x}.
\]

Finally,

\[
|(2-x)-1|=|1-x|=|x-1|.
\]

All five claims follow. \(\square\)

**Plain explanation.** This proves that one positive build time and one positive release time always produce one
unambiguous point on the declared duration diameter. Equal times land exactly at 1. Swapping which side you call
accumulation simply reflects the answer across 1, so 0.7 becomes 1.3. Nothing about the strength of the duration
asymmetry changes. It also means the bounded number has not thrown the original timing ratio away: you can recover
it exactly. It does not prove that duration is the correct instrument for every other ARA axis.

### Corollary 1.1 — The two golden landmarks are mirrors

Let \(\varphi=(1+\sqrt5)/2\). Then

\[
2-\varphi=\frac1{\varphi^2}\approx0.381966.
\]

**Proof.** Since \(\varphi^2=\varphi+1\), we have \(1/\varphi=\varphi-1\), and therefore

\[
\frac1{\varphi^2}=(\varphi-1)^2
=\varphi^2-2\varphi+1
=(\varphi+1)-2\varphi+1
=2-\varphi.
\]

Thus \(\varphi\) and \(2-\varphi\) are reflected around 1. \(\square\)

**Plain explanation.** The two ARA golden positions, about 1.618 and 0.382, are not two unrelated constants. They
are exactly the same landmark viewed from opposite orientations of the 0–2 relation.

### Corollary 1.2 — One shared traversal can read 2 head-on and Phi by pentagonal projection

Let $u \in [0,1]$ be one shared traversal coordinate. Define

\[
\underbrace{S(u)}_{\substack{\text{head-on structural ruler}\\\text{ARA }0\to2}}
=2u
\]

and project the same length through the regular-pentagon half-angle:

\[
\underbrace{P_+(u)}_{\substack{\text{pentagonal projection}\\\text{ARA }0\to\varphi}}
=2u\cos\left(\frac{\pi}{5}\right)
=\varphi u.
\]

Then $S(1)=2$, $P_+(1)=\varphi$, and for $u>0$

\[
\frac{P_+(u)}{S(u)}=\cos36^\circ=\frac{\varphi}{2}.
\]

Under the reversed chart,

\[
P_-(u)=2-P_+(u),
\qquad
P_-(1)=2-\varphi=\varphi^{-2}.
\]

**Proof.** The regular-pentagon identity is $2\cos(\pi/5)=\varphi$. Multiplying by the common traversal $u$
gives $P_+(u)=\varphi u$. The reverse endpoint follows from Corollary 1.1. \(\square\)

**Plain explanation.** This is one ruler viewed from two directions, not a rule that rounds a moving point onto five
vertices. Over the same progress, the structural reading reaches 2 and the pentagonal shadow reaches Phi. The exact
identity proves the projection relation only. It does not prove that physical time uses this projection, that the
two readings are dynamically independent waves, or that their crossings locate primes.

---

## 2. Why one 0–2 diameter can be represented as a folded circle

Let the phase of a cycle be \(\theta\in S^1\), where angles differing by \(2\pi\) describe the same point. Define
the projection

\[
\boxed{
\overbrace{p(\theta)}^{\substack{\text{circle projection}\\\text{ARA slice through the wave}}}
=1+\cos\theta
}
\tag{2}
\]

### Theorem 2 — This ARA diameter representation is a reflection quotient of a circle

The map \(p:S^1\to[0,2]\) is onto, satisfies \(p(-\theta)=p(\theta)\), and gives two phase branches for every
interior ARA value. Consequently a scalar ARA position records location but not travel direction.

**Proof.** Since \(-1\leq\cos\theta\leq1\), equation (2) gives \(0\leq p(\theta)\leq2\). Every number in this
interval is reached because cosine is continuous and covers \([-1,1]\). Cosine is even, so

\[
p(-\theta)=1+\cos(-\theta)=1+\cos\theta=p(\theta).
\]

For any \(x\in(0,2)\), the equation \(\cos\theta=x-1\) has two solutions on a full turn, \(\theta\) and
\(-\theta\). These have opposite phase direction even though they project to the same \(x\). \(\square\)

**Plain explanation.** A circle seen from one direction collapses to a line segment: the front and back can land
on the same horizontal position. That is why the ARA number can tell you the relation's shape but cannot, alone,
tell you which way around the cycle it is travelling. Direction or handedness is extra information, not a second
ARA shape. This proves the properties of the chosen projection; whether a measured system follows that circular
phase model is a separate physical question.

### Definition 2.1 — Minimal moving ARA record

For motion-sensitive work, use

\[
\overbrace{(x,s)}^{\substack{\text{coordinate plus handedness}\\\text{ARA position plus direction}}},
\qquad s\in\{-1,+1\}.
\]

The scalar \(x\) remains the minimal shape. The sign \(s\) records which phase branch the observer is following.

## 2.1 The diameter is the minimal section of the sphere

For exact section language, use the closed unit balls

\[
B^3=\{(u,v,w):u^2+v^2+w^2\leq1\},
\qquad
B^2=\{(u,v):u^2+v^2\leq1\},
\qquad
B^1=[-1,1].
\]

Their boundaries are the sphere \(S^2\), circle \(S^1\), and two diameter endpoints \(S^0\).

### Theorem 2.2 — Central section chain: state ball → circle → diameter

A central plane section of \(B^3\) is \(B^2\), whose boundary is a circle. A central line section of that disk is
the diameter interval \(B^1\). Explicitly,

\[
\boxed{
\underbrace{B^3}_{\substack{\text{filled ARA state ball}\\\text{shell plus mixture interior}}}
\cap\underbrace{\{w=0\}}_{\text{chosen time-slice plane}}
=\underbrace{B^2}_{\text{slice disk}},
\qquad
B^2\cap\underbrace{\{v=0\}}_{\text{chosen ARA axis}}
=\underbrace{B^1}_{\text{ARA diameter}}
}
\tag{2a}
\]

and on the boundaries

\[
S^2\cap\{w=0\}=S^1.
\]

**Proof.** Setting \(w=0\) in \(u^2+v^2+w^2\leq1\) leaves

\[
u^2+v^2\leq1,
\]

which is \(B^2\). Its boundary is \(u^2+v^2=1=S^1\). Setting \(v=0\) in the disk leaves

\[
u^2\leq1,
\]

or \(-1\leq u\leq1=B^1\). The same substitution in the sphere boundary proves
\(S^2\cap\{w=0\}=S^1\). \(\square\)

**Plain explanation.** Cut the filled state ball through its centre and you expose a disk with a circular boundary. Cut
that disk through its centre and you obtain one diameter line. ARA begins with that final one-dimensional section,
but the circle and spherical closure have not disappeared—they are the larger object from which the line was cut.

### Theorem 2.3 — Phase/anti-phase mixing fills exactly one diameter

Let \(p\in S^1\) be a unit phase vector and let its anti-phase partner be \(-p\). Every convex mixture of the pair
is

\[
\overbrace{m(\lambda)}^{\substack{\text{ordinary linear mixture}\\\text{ARA phase/anti-phase gradient}}}
=(1-\lambda)p+\lambda(-p)
=(1-2\lambda)p,
\qquad 0\leq\lambda\leq1.
\tag{2b}
\]

The set of all such mixtures is exactly the diameter \(D_p=\{tp:-1\leq t\leq1\}\), and equal mixing
\(\lambda=1/2\) gives the cancellation centre.

**Proof.** As \(\lambda\) ranges from 0 to 1, the scalar \(t=1-2\lambda\) ranges continuously from 1 to \(-1\).
Therefore

\[
\{m(\lambda):0\leq\lambda\leq1\}
=\{tp:-1\leq t\leq1\}=D_p.
\]

At \(\lambda=1/2\), \(t=0\) and hence \(m(1/2)=0\). \(\square\)

**Plain explanation.** Pick one point on the circle as the phase and the exactly opposite point as anti-phase.
Blend them in every possible proportion. Every blend lands on the straight diameter connecting them. A 50/50
blend lands at the centre because the two vectors cancel exactly. This makes the ARA line the literal mixing
gradient between phase and anti-phase.

To use the repository's \(0\!-\!2\) coordinate, map the signed diameter coordinate \(t\in[-1,1]\) to

\[
\overbrace{x}^{\text{ARA position}}=1+t.
\]

Then \(t=-1,0,1\) become \(x=0,1,2\).

### Corollary 2.3.1 — The duration formula is the signed diameter coordinate

For the canonical duration coordinate in equation (1),

\[
\boxed{
\underbrace{t}_{\substack{\text{signed diameter position}\\\text{ARA imbalance around the ridge}}}
=\underbrace{x-1}_{\text{distance and side from balance}}
=\frac{T_A-T_R}{T_A+T_R}
}
\tag{2d}
\]

**Proof.** Substitute equation (1):

\[
x-1
=\frac{2T_A}{T_A+T_R}-1
=\frac{2T_A-(T_A+T_R)}{T_A+T_R}
=\frac{T_A-T_R}{T_A+T_R}.
\]

\(\square\)

**Plain explanation.** The duration version and the geometric diameter version are the same coordinate in two
languages. Subtracting 1 from ARA gives the build-minus-release difference divided by the total cycle time. Equal
phases give zero at the diameter centre; accumulation dominance points one way and release dominance points the
other.

### Corollary 2.4 — Two binary signs produce four circle quadrants

Away from axes and turning points, a moving circle point has two independent signs:

\[
\underbrace{\operatorname{sgn}(x-1)}_{\substack{\text{which side of the diameter centre}\\\text{phase/anti-phase orientation}}},
\qquad
\underbrace{\operatorname{sgn}(\dot x)}_{\substack{\text{which way the slice is moving}\\\text{accumulation/release gradient}}}.
\]

Their four possible sign pairs correspond to the four quadrants of the circle.

**Proof.** Each sign has two possible nonzero values, \(+1\) or \(-1\). Their Cartesian product has

\[
2\times2=4
\]

elements. For \(x=1+\cos\theta\), the first sign records the sign of \(\cos\theta\), and
\(\dot x=-\dot\theta\sin\theta\) records the branch direction for fixed nonzero \(\dot\theta\). The sign changes
occur at the two chosen axes, partitioning a full turn into four sectors. \(\square\)

**Plain explanation.** One yes/no distinction says which side of the centre the relation occupies. A second
yes/no distinction says whether it is moving toward accumulation or toward release. Two binary distinctions give
four combinations—the four quadrants you have been unpacking around the sphere. On the axes themselves one sign
is zero, marking a boundary between quadrants.

### Corollary 2.4.1 — A complex scale-and-phase generator realizes four dynamical quadrants

Let a nonzero two-cut relation evolve as

\[
z(t)=r_0e^{(\sigma+i\omega)t}.
\]

Then

\[
|z(t)|=r_0e^{\sigma t},
\qquad
\arg z(t)=\omega t,
\]

and the independent signs

\[
\operatorname{sgn}(\sigma),
\qquad
\operatorname{sgn}(\omega)
\]

generate contracting/expanding magnitude crossed with forward/reverse phase.
For sampled states, the same result is obtained from

\[
q_n=\frac{z_{n+1}}{z_n}=s_ne^{i\delta_n},
\qquad
\sigma_n=\frac{\log s_n}{\Delta t},
\qquad
\omega_n=\frac{\delta_n}{\Delta t}.
\tag{2d-1}
\]

**Proof.** Euler's identity separates the exponential into the positive
radial factor (e^{\sigma t}) and the unit-modulus rotation
(e^{i\omega t}). The sign of (sigma) determines whether the radius shrinks
or grows, while the sign of (omega) determines orientation. Two independent
nonzero signs have four combinations. Taking the logarithm of the sampled
multiplier gives the displayed local rates. \(\square\)

**Plain explanation.** This is one exact dynamical realization of the ARA
four-quadrant rule. It distinguishes how much of a relation remains from which
way its phase travels. Rational closure, irrational non-closure and randomness
are possible phase behaviours inside this plane; they are not themselves the
four quadrant signs.

**Physical boundary.** This corollary proves the classification, not that one
universal pair of rates or constants governs every physical identity. In
particular, the current ARA-specific lead placement uses `1/e` and Phi as
provisional contracting and expanding/structured-retention radial landmarks,
then crosses that span with phase direction. This asymmetric `1/e ↔ Phi`
diameter is an empirical ARA hypothesis, not a consequence of the exponential
identity. Current hypothesis and evidence audit:
`analysis/phi_calibration/ARA_COMPLEX_IRRATIONALITY_QUADRANT_HYPOTHESIS_2026-08-03.md`.

### Theorem 2.5 — Rotating the ARA diameter reconstructs the full state ball

Let \(D_n=\{tn:-1\leq t\leq1\}\) be the diameter in direction \(n\in S^2\). Then

\[
\boxed{
B^3=\bigcup_{n\in S^2}D_n
}
\tag{2c}
\]

and the endpoints \(|t|=1\) sweep out the sphere \(S^2\).

**Proof.** Every point of every \(D_n\) has norm \(|t|\leq1\), so the union lies inside \(B^3\). Conversely,
take any nonzero \(y\in B^3\). Put \(n=y/\|y\|\in S^2\) and \(t=\|y\|\in[0,1]\). Then \(y=tn\in D_n\).
The origin belongs to every diameter with \(t=0\). Thus the union is all of \(B^3\). When \(|t|=1\), every
endpoint has norm one, and every norm-one point occurs as an endpoint, producing \(S^2\). \(\square\)

**Plain explanation.** Start with one ARA diameter and rotate it through every possible direction. The collection
of all those lines fills the entire solid sphere; their outer endpoints trace its surface. So unpacking the one
minimal ARA line around all axes is mathematically sufficient to rebuild the filled spherical state space. Strictly,
the union is the ball \(B^3\); its outer closure is the sphere \(S^2\).

#### Corollary 2.5a — the recursive ARA web can be embedded as radial and angular sphere structure

At rung \(k\), let \(R_k>0\) be the declared scale radius, let \(x_{k,i}\in[0,2]\) be the ARA position of node \(i\),
and let \(n_{k,i}\in S^2\) be the orientation of the diameter/coupling direction being followed. Define

\[
\boxed{
\mathbf p_{k,i}
=
\underbrace{R_k}_{\substack{\text{rung/scale radius}\\\text{ARA: octave location}}}
\underbrace{(1-x_{k,i})}_{\substack{\text{signed position on diameter}\\\text{ARA: Phase A/B mixture}}}
\underbrace{n_{k,i}}_{\substack{\text{orientation on the shell}\\\text{ARA: coupling direction}}}
}
\tag{2d}
\]

Then:

1. varying \(x\) at fixed \(R_k,n\) moves along one ARA diameter, through the centre at \(x=1\);
2. varying \(n\) at fixed \(R_k\) and fixed \(|1-x|\) moves sideways around a spherical shell (a circumference in a
   two-dimensional section);
3. changing \(R_k\) moves between nested rung shells;
4. repeating the A/B decomposition at a resolved child supplies further nodes and directions in the same ball.

For two same-shell nodes, the angular and geodesic separations are

\[
\Delta\theta_{ij}
=
\arccos(n_i\!\cdot n_j),
\qquad
d_{ij}^{\mathrm{shell}}
=
R_k|1-x|\,\Delta\theta_{ij}.
\]

If the recursive web samples all required \(x\in[0,2]\) and orientations \(n\in S^2\), equation (2d) has the same
union as Theorem 2.5 and fills the ball \(B^3_{R_k}\). Its fixed-radius outer closure is the sphere \(S^2_{R_k}\).
The mirror identity

\[
\mathbf p(x,n)=\mathbf p(2-x,-n)
\]

records the phase/anti-phase equivalence of reversing both the diameter position and its orientation.

**Plain explanation.** The web does not merely sit inside a sphere drawn in advance. Each ARA relation supplies a
position along a diameter and a direction in which that diameter points. Following A or B deeper adds finer
diameters toward nested structure; following same-rung couplings changes direction around the shell. Accumulating
enough resolved relations therefore fills more of the solid sphere. Mathematically the filled object is a
three-ball, while “sphere” strictly names its shell.

Two inward-looking coordinates must still be kept typed separately: moving \(x\) toward the ridge moves toward the
centre **within one rung**, while reducing \(R_k\) moves to a **finer nested rung**. They may look similar in a
diagram but are not automatically the same physical operation.

The geometric embedding is exact once \(R_k,x,n\) are declared. The physical claim that a measured coupling web
actually follows this embedding remains testable: the orientations, rung radii and edges must be inferred
independently rather than chosen to make a sphere after inspection.

#### Corollary 2.5b — A two-channel coherency state generates every ARA diameter projection

At a declared rung (k), let the selected two-channel occurrence be

\[
z_k=(A_k,B_k)^\mathsf T,
\qquad
G_k=\langle z_kz_k^\dagger\rangle,
\qquad
T_k=\operatorname{tr}G_k>0.
\]

Define

\[
\boxed{
s_k=\frac1{T_k}
\left(2\Re G_{AB},,2\Im G_{AB},,G_{BB}-G_{AA}\right)
}
\tag{2d-1}
\]

and, for any unit measurement axis (alphain S^2),

\[
\boxed{x_{k,\alpha}=1+\alpha\cdot s_k.}
\tag{2d-2}
\]

Then (|s_k|\le1), (x_{k,\alpha}in[0,2]), and

\[
x_{k,-\alpha}=2-x_{k,\alpha}.
\]

**Proof.** Positive semidefiniteness gives (det G_k\ge0). Direct expansion yields

\[
1-\|s_k\|^2=\frac{4\det G_k}{T_k^2}\ge0.
\]

Hence (|\alpha\cdot s_k|\le1), proving the interval bound. Axis reversal changes the sign of the dot product,
which gives the mirror identity. (square)

On the original population axis (alpha=(0,0,1)),

\[
x_{k,\alpha}=2\frac{G_{BB}}{T_k}.
\]

For a rotated axis, the same formula compares rotated superposition modes and therefore includes the retained
coherence/relative-phase relation. Dimensional allocations and normalized TE-ARA allocations are

\[
Q_B=\frac{T_kx}{2},\quad Q_A=\frac{T_k(2-x)}2,
\qquad
t_B=\frac{2Q_B}{T_k}=x,\quad t_A=\frac{2Q_A}{T_k}=2-x,
\]

so (t_A+t_B=2) exactly.

**Plain explanation.** Two channel strengths plus their relation generate one point inside a state ball. Looking
through that point along any chosen direction produces an ARA diameter. The same state can be at the ridge on one
axis and at a pole on another. The physical amount (T_k) and the normalized two-unit TE-ARA allocation remain
separate, typed quantities.

#### Corollary 2.5c — Exact incoherent averaging and coherent relation closure

For separately mixed child coherency matrices,

\[
G_P=\sum_iG_i
\quad\Longrightarrow\quad
s_P=\frac{\sum_iT_is_i}{\sum_iT_i},
\qquad
x_{P,\alpha}=\frac{\sum_iT_ix_{i,\alpha}}{\sum_iT_i}.
\tag{2d-3}
\]

If amplitudes combine coherently before measurement, (z_P=\sum_i z_i), then

\[
\boxed{
G_P
=
\underbrace{\sum_i z_iz_i^\dagger}_{\text{separate child states}}
+
\underbrace{\sum_{i\ne j}z_iz_j^\dagger}_{\text{retained child relations}}
}.
\tag{2d-4}
\]

**Proof.** Equation (2d-3) follows by substituting the linear matrix sum into (2d-1) and dividing by the summed
trace. Equation (2d-4) follows by expanding ((\sum_i z_i)(\sum_jz_j)^\dagger). (square)

**Plain explanation.** Unresolved independent children average into the parent according to how active each child
is, so asymmetric children may cancel to a ridge. Coherent children also produce cross-terms. Those cross-terms are
the exact measurable relation in the ARA “two identities plus their coupling” language; omitting them loses parent
information. Reapplying this construction at several declared rungs is a valid recursive formalism. The physical
claim that one transferable rule recurs across independently measured scales remains empirical.

## 2.2 The endpoints are sources; the centre is the strongest meeting

Let two coherent wave contributions arrive from the two ends of the ARA diameter:

\[
z_0=A_0e^{i\theta_0},
\qquad
z_2=A_2e^{i\theta_2},
\qquad
\delta=\theta_2-\theta_0,
\]

with \(A_0,A_2\geq0\). Let \(S=A_0+A_2>0\), and encode their relative weights by

\[
\overbrace{x}^{\substack{\text{bounded mixture coordinate}\\\text{ARA position between sources}}}
=\frac{2A_2}{A_0+A_2}.
\tag{2e}
\]

Then

\[
A_0=\frac{S(2-x)}2,
\qquad
A_2=\frac{Sx}2.
\]

### Theorem 2.6 — The poles contain one source; the ridge uniquely permits complete cancellation

The interference intensity is

\[
\boxed{
\underbrace{I(x,\delta)}_{\substack{\text{resultant intensity}\\\text{outcome of the ARA meeting}}}
=|z_0+z_2|^2
=\frac{S^2}{4}
\left[(2-x)^2+x^2+2x(2-x)\cos\delta\right]
}
\tag{2f}
\]

and:

1. At \(x=0\), \(A_2=0\): only the 0-source remains.
2. At \(x=2\), \(A_0=0\): only the 2-source remains.
3. The two-source coupling magnitude \(A_0A_2=S^2x(2-x)/4\) is zero at the poles and maximal at \(x=1\).
4. Complete cancellation \(I=0\) is possible if and only if \(x=1\) and \(\delta=\pi\pmod{2\pi}\).

**Proof.** Expanding the squared modulus gives

\[
|z_0+z_2|^2=A_0^2+A_2^2+2A_0A_2\cos\delta.
\]

Substituting the expressions for \(A_0,A_2\) proves equation (2f). The endpoint claims follow immediately from
the amplitude formulas. The product

\[
A_0A_2=\frac{S^2}{4}x(2-x)
\]

is a concave quadratic with zeros at 0 and 2 and its unique maximum at \(x=1\). Finally, by the reverse triangle
inequality,

\[
|z_0+z_2|\geq\big||z_0|-|z_2|\big|=|A_0-A_2|.
\]

The lower bound can be zero only when \(A_0=A_2\), which is equivalent to \(x=1\). With equal amplitudes, the sum
is zero exactly when the phases differ by \(\pi\) modulo \(2\pi\). \(\square\)

**Plain explanation.** At 0 or 2, only one source is present, so there is no two-wave relationship left to
measure; that is the clean mathematical sense in which the endpoints are both sources and relational
singularities. At 1, the sources contribute equally, making their interaction as strong as possible. If they meet
anti-phase, they erase one another completely and the *output* becomes zero. That output zero is different from
the ARA coordinate \(x=0\), which is an endpoint source.

### Corollary 2.6.1 — Equal meeting can cancel or resonate

At \(x=1\),

\[
\boxed{
I(1,\delta)=S^2\cos^2\frac\delta2
}
\tag{2g}
\]

so

\[
\delta=\pi\Rightarrow I=0
\qquad\text{and}\qquad
\delta=0\Rightarrow I=S^2.
\]

**Proof.** Put \(x=1\) into equation (2f):

\[
I(1,\delta)=\frac{S^2}{2}(1+\cos\delta)
=S^2\cos^2\frac\delta2.
\]

The two stated phases give the minimum and maximum. \(\square\)

**Plain explanation.** The centre is an equal meeting, so phase decides what the meeting does. Opposite phases
produce the familiar quiet cancellation ridge. Exact same-phase coherence makes the equal waves reinforce as
strongly as possible—the rarer resonant case you described. Intermediate phase differences fill the gradient
between those outcomes.

### Corollary 2.6.2 — Opposing Newtonian forces admit an exact active-ridge coordinate

Choose a physical axis \(\hat{\mathbf e}\). Let \(F_A,F_B\geq0\) be the magnitudes of all force contributions on a
declared body or boundary in the \(-\hat{\mathbf e}\) and \(+\hat{\mathbf e}\) directions. When
\(\Sigma_F=F_A+F_B>0\), define

\[
\underbrace{x_F}_{\substack{\text{bounded force-opposition coordinate}\\
\text{ARA: Phase A }0\rightarrow\text{ Phase B }2}}
=
\frac{2F_B}{F_A+F_B}.
\]

Then the signed resultant is exactly

\[
\boxed{
\underbrace{F_{\rm net,\parallel}}_{\text{directed resultant}}
=
\underbrace{F_B-F_A}_{\text{Phase B minus Phase A}}
=
\underbrace{\Sigma_F}_{\substack{\text{dimensional force envelope}\\
\text{separate from normalized TE-ARA}}}
\underbrace{(x_F-1)}_{\text{signed ARA ridge displacement}}.
}
\tag{2g-Newton}
\]

Consequently:

1. \(x_F=1\) if and only if \(F_A=F_B>0\): an active equal-and-opposite ridge.
2. \(x_F<1\) gives a resultant toward declared Phase A.
3. \(x_F>1\) gives a resultant toward declared Phase B.
4. If \(F_A=F_B=0\), \(x_F\) is undefined rather than a measured ridge.
5. For a constant-mass body, Newton II becomes
   \(m a_\parallel=\Sigma_F(x_F-1)\).
6. For a Newton-III interaction pair, the two force magnitudes are equal on different bodies, so their enclosing
   internal-force account has \(x_F=1\) and \(\Sigma_F>0\), even though both bodies may accelerate.

**Proof.** From the coordinate definition,

\[
F_B=\frac{\Sigma_Fx_F}{2},
\qquad
F_A=\frac{\Sigma_F(2-x_F)}{2}.
\]

Subtracting gives \(F_B-F_A=\Sigma_F(x_F-1)\). The sign and ridge claims follow immediately. Newton II supplies
\(m a_\parallel=F_{\rm net,\parallel}\) for constant mass. Newton III supplies equal anti-directed force magnitudes
on the two interacting bodies, so their sum vanishes only after the enclosing pair boundary is declared.
\(\square\)

**Plain explanation.** Newton supplies the full local ARA skeleton. Phase A and Phase B are the two directed force
accounts. Equal nonzero forces sit at the `1.0` ridge: the whole-system resultant is quiet while the children remain
active. Moving away from the ridge changes momentum in the dominant phase direction. No force at all is a different
state; because there is no pair to compare, its ARA ratio is undefined.

## 2.3 A circle unfolded through a monotone progression coordinate becomes a helix

### Theorem 2.7 — Periodic waves admit a Fourier representation as sums of projected circles

Let \(f\) be a square-integrable real signal with period \(T\), and let \(\omega=2\pi/T\). Its Fourier series is

\[
f(t)=\frac{a_0}{2}
+\sum_{n=1}^{\infty}
\left[a_n\cos(n\omega t)+b_n\sin(n\omega t)\right]
\tag{2h}
\]

with convergence in the \(L^2\) sense. Each harmonic term is the real projection of one complex rotation
\(c_ne^{in\omega t}\), which traces a circle in the complex plane.

**Proof.** The Fourier-series theorem states that the functions

\[
1,\quad\cos(n\omega t),\quad\sin(n\omega t),\qquad n=1,2,\ldots
\]

form a complete orthogonal basis for the square-integrable \(T\)-periodic functions. Expanding \(f\) in that
basis gives equation (2h). Euler's identity

\[
e^{in\omega t}=\cos(n\omega t)+i\sin(n\omega t)
\]

shows that each sine/cosine pair is a projection of circular motion. \(\square\)

**Plain explanation.** A perfect sine wave is the shadow of one point travelling around a circle. A more
complicated repeating wave is made by adding several such circular motions at different harmonic speeds. This is
the rigorous sense in which a periodic wave can be treated as a circle or a collection of circles. It does not
prove that every possible time-dependent process repeats.

**Raw-first methodological fence.** Fourier analysis is a secondary representation and comparator, not the primary
definition or extractor of ARA. When the research question concerns the original Phase-A/Phase-B pairing, crossing
order, transient path, child structure or nonlinear relation, begin with the raw or least-transformed observations.
A transform that averages, windows, filters or decomposes the signal may expose useful modes, but it may also erase
or manufacture the relation being tested. Report the transform and test whether the ARA result survives a
phase-preserving alternative.

### Theorem 2.8 — Adding a monotone coordinate unfolds the circle into a helix

Let \(R>0\), \(\omega>0\), and let \(\Sigma(t)=\kappa t\) with \(\kappa>0\) represent a monotone accumulated
time/entropy-production coordinate. Define

\[
\overbrace{h_+(t)}^{\substack{\text{mathematical helix}\\\text{ARA phase strand}}}
=\left(R\cos\omega t,\ R\sin\omega t,\ \kappa t\right).
\tag{2i}
\]

Its projection onto the first two coordinates is a circle, while one period later

\[
h_+(t+T)=h_+(t)+(0,0,\kappa T),
\qquad T=\frac{2\pi}{\omega}.
\]

**Proof.** The first two coordinates satisfy

\[
(R\cos\omega t)^2+(R\sin\omega t)^2=R^2,
\]

so their projection lies on the radius-\(R\) circle. Since \(\omega T=2\pi\), sine and cosine repeat after \(T\),
while the third coordinate increases by \(\kappa T>0\). Therefore the full trajectory does not return to the same
three-dimensional point; it advances along the axis, forming a helix. \(\square\)

**Plain explanation.** Viewed without the progression coordinate, the motion goes around the same circle. Once a
monotone accumulated quantity is drawn as a third direction, every return to the same phase occurs farther along
that direction. The circle has become a helix. Interpreting its pitch as irreversible physical time or entropy
requires the selected coordinate to justify that meaning.

### Theorem 2.9 — Phase and anti-phase form a double helix with a cancellation axis

Define the anti-phase strand in the same slice by

\[
\overbrace{h_-(t)}^{\substack{\text{second helix}\\\text{ARA anti-phase strand}}}
=\left(-R\cos\omega t,\ -R\sin\omega t,\ \kappa t\right).
\tag{2j}
\]

Then \(h_+\) and \(h_-\) are separated by phase \(\pi\), and their midpoint is always the central axis:

\[
\frac{h_+(t)+h_-(t)}2=(0,0,\kappa t).
\]

**Proof.** Negating both circular coordinates is equivalent to adding \(\pi\) to the phase because

\[
\cos(\theta+\pi)=-\cos\theta,
\qquad
\sin(\theta+\pi)=-\sin\theta.
\]

Adding the two strands cancels their circular coordinates and doubles their equal third coordinate, giving the
stated midpoint. \(\square\)

**Plain explanation.** The two strands occupy opposite sides of every circular slice. The straight connector
between them is an ARA diameter, and its midpoint lies on the helix axis. Equal phase/anti-phase mixing therefore
lands on the axis where transverse amplitude is zero and circular phase becomes undefined—the phase singularity.

### Theorem 2.10 — Phase → anti-phase → next phase forms a temporal triangle

Let one helical period have pitch \(p=\kappa T>0\), and sample the phase strand at a full phase, its half-cycle
anti-phase, and the next full phase:

\[
A=h_+(0)=(R,0,0),
\]

\[
B=h_+(T/2)=(-R,0,p/2),
\]

\[
C=h_+(T)=(R,0,p).
\]

These three points are non-collinear and therefore form a triangle. Their circle projection identifies \(A\) and
\(C\), reducing the temporal triangle to the phase/anti-phase diameter.

**Proof.** The displacement vectors are

\[
B-A=(-2R,0,p/2),
\qquad
C-A=(0,0,p).
\]

Their cross product is

\[
(B-A)\times(C-A)=(0,2Rp,0),
\]

which is nonzero because \(R,p>0\). Hence the points are non-collinear and determine a triangle. Projecting onto
the circular coordinates sends both \(A\) and \(C\) to \((R,0)\), while \(B\) goes to \((-R,0)\), the opposite
end of the diameter. \(\square\)

**Plain explanation.** In one flat circle, “phase now” and “phase one cycle later” look like the same point. In
unwrapped time they are different events at different heights. Connecting phase now, anti-phase halfway through,
and phase next cycle makes a real triangle. Looking only at the circular slice collapses that triangle back into
the ARA diameter. The reverse strand makes the vice-versa triangle, and the repeating pair naturally resembles a
triangulated double helix.

### Universal-wave hypothesis — scope boundary

ARA's broad physical proposal is that every persistent identity has some scale at which a meaningful recurrent
accumulation–release cycle can be identified. The Fourier theorem proves circular representation for periodic
signals; it does **not** prove that every physical process is periodic. One-way transients, stochastic processes,
fixed points, and chaotic trajectories require either a local-cycle definition, a multi-mode state-space model,
or classification as outside the strict cycle claim. Entropy production supplies a direction of time, but does
not by itself guarantee recurrence. For an open subsystem, local entropy may fall; the monotone coordinate should
refer to total cumulative entropy production of system plus environment.

---

## 3. The octave, handover, chart reversal, and physical singularity crossing are typed operations

### Definition 3.1 — Octave operator

Let a physical scale on rung \(n\in\mathbb Z\) be

\[
\overbrace{S_n}^{\substack{\text{ordinary scale}\\\text{ARA rung }n}}
=S_0\,2^n.
\]

The octave operator \(O\) sends \(n\mapsto n+1\), so \(S_{n+1}=2S_n\).

### Definition 3.2 — Static pole-chart reversal

Define

\[
\overbrace{F_{chart}(x,s,n)}^{\substack{\text{mathematical involution}\\\text{ARA pole/orientation reversal}}}
=(2-x,-s,n).
\]

### Theorem 3 — Chart reversal is an involution and is independent of rung scale

The chart reversal satisfies \(F_{chart}^2=I\), and it commutes with the octave operator:
\(F_{chart}O=OF_{chart}\).

**Proof.** Applying \(F\) twice gives

\[
F_{chart}(F_{chart}(x,s,n))=F_{chart}(2-x,-s,n)=(2-(2-x),-(-s),n)=(x,s,n).
\]

Therefore \(F_{chart}^2=I\). Also,

\[
F_{chart}O(x,s,n)=F_{chart}(x,s,n+1)=(2-x,-s,n+1),
\]

while

\[
OF_{chart}(x,s,n)=O(2-x,-s,n)=(2-x,-s,n+1).
\]

Hence \(F_{chart}O=OF_{chart}\). \(\square\)

**Plain explanation.** Reversing the local pole labels and direction twice brings the same chart back. Changing
octave does not, by itself, alter that local 0–2 relation, so you can zoom first and reverse second or reverse first
and zoom second. This is a coordinate theorem. It does not yet prove what happens dynamically when a physical
cycle reaches 0 or 2.

### Definition 3.2a — Proposed dynamical singularity crossing

An ARA singularity crossing is a physical cycle-seam event at one declared endpoint that changes the local
Phase/Anti-phase branch and continues the cycle on an adjacent chart or rung. A candidate crossing map can be
written

\[
\underbrace{F_{dyn}}_{\substack{\text{physical seam-crossing map}\\\text{ARA singularity/phase flip}}}
:(x,s,n,\theta,J)\longmapsto(x',s',n',\theta',J').
\]

No universal formula for \(F_{dyn}\) is proved here. Identifying it with \(F_{chart}\), adding a rung change, or
requiring a phase shift of \(\pi\) are empirical modelling choices that must be stated for the domain.

### Conjecture 3.2b — Completed-seam parity rule

The recurring ARA domain rule is more specific than “every child flips.” It proposes:

1. phase orientation is retained while a trajectory remains inside the same scale-level ARA chart;
2. one completed `0–2` cycle or equivalent TE-ARA seam crossing applies the orientation reversal;
3. repeated completed crossings compose by parity.

Let \(N_{\partial T}\in\mathbb N_0\) count completed TE-ARA seams between two declared measurements. The candidate
domain map is:

\[
\boxed{
u_{\rm destination}
=
F_{\rm chart}^{\,N_{\partial T}}u_{\rm source}.
}
\tag{2e}
\]

Because \(F_{\rm chart}^2=I\), the conditional mathematical consequence is:

\[
\boxed{
N_{\partial T}\text{ even}\Rightarrow F_{\rm chart}^{N_{\partial T}}=I,
\qquad
N_{\partial T}\text{ odd}\Rightarrow F_{\rm chart}^{N_{\partial T}}=F_{\rm chart}.
}
\tag{2f}
\]

**Plain explanation.** Staying inside a rung does not exchange the phase labels. Completing one whole seam does;
completing a second restores the original orientation. This parity conclusion is exact once the proposed seam map
is assumed. The physical premise—that a declared event really is a completed TE-ARA seam and implements
\(F_{\rm chart}\)—remains empirical.

**Prior lineage and current status.** The conditional rule predates the July quantum work. The Formula/engine
record of 10 June states “full `360°` / reach `0` or `2`: flip; remain within the rung: no flip.” PN30 implemented
the reflected prime-child coordinate \(x\mapsto2-x\) and produced a suggestive but nonsignificant hard-control
improvement (`p=0.06199`). PN35's same-scale golden prime bridge and flip advantage were null. The public
free-swing pendulum never reached `0/2`, so it correctly supplied no flip test. Q14 later rejected an unmatched
swap between two quantum child sets; after the same-rung clarification this is consistent with even parity but
does not establish a seam crossing. Lineage and boundaries:
`analysis/quantum/Q14_COMPLETED_RUNG_FLIP_PRIOR_LINEAGE_2026-07-24.md`.

**Q22 application and negative result (26 July 2026).** Q22A compared Tier 4 directly with Tier 1 and was
method-corrected before validation because it omitted the three-boundary odd-parity flip. Q22B then froze

\[
u_{4\rightarrow1}=F_{\rm chart}^{3}(u_4)=2-u_4
\]

on a new untouched Google Willow patch. The registered all-children/both-pathways representation failed its
descriptive direction and logical-prediction claims (`1/13` gates; mean state-plus-travel AUROC `0.498422`).
This is evidence against that physical application, not against the conditional algebra in (2e)-(2f): the
algebra says what follows if the selected boundaries implement \(F_{\rm chart}\); it does not prove that the
selected aggregate is the transported lineage. Both complementary paths may recompress to the parent ridge.
The next clean discrimination must freeze one branch-preserving lineage and keep its complement as a control.
Full report: `analysis/quantum/Q22_Q22B_VERTICAL_TIER_RELATION_REPORT_2026-07-26.md`.

**Q38 perpendicular two-child application (27 July 2026; post-result
hypothesis).** Q38's fixed parent anchor produced an immediate low-amplitude
orientation sequence `+ → - → +`. After that outcome was open, Dylan
proposed that this may be a perpendicular view of two ordered child
crossings rather than return to the old quadrant:

\[
2\rightarrow0\;\big|\;0\rightarrow2,
\qquad
AB\rightarrow BA.
\]

For a locally factorised parent \(C=\sigma uv^{\mathsf T}\),

\[
uv^{\mathsf T}\rightarrow(-u)v^{\mathsf T}
\rightarrow(-u)(-v)^{\mathsf T}=uv^{\mathsf T}.
\]

This is a direct two-child expression of the even-parity consequence in
(2f), and it has an exact established analogue in the MX6 Maxwell sign
crosswalk. It does not establish the physical premise in Q38:
\(uv^{\mathsf T}=(-u)(-v)^{\mathsf T}\) makes the two child histories
non-identifiable from the parent alone. A valid test requires two
independently oriented child observables and must not infer their signs only
from an SVD of the parent. Record:
`analysis/quantum/Q38_POST_RESULT_QUADRANT_DOUBLE_FLIP_HYPOTHESIS_2026-07-27.md`.

**Tier correction.** In this application, \(C\) is the ARA⁹ connected
lattice already defined by Q24 as
\(C=T-\mathbf a\mathbf b^{\mathsf T}\). The proposed \(u,v\) are internal
children of \(C\), not automatically the upper local vectors
\(\mathbf a,\mathbf b\). Bell preparations calibrated complete instances of
the lattice but are not the four lower meta quadrants. Q38 is provisionally
placed down one tier from that whole-pair lens and across \(C\)'s own
singularity chart.

**Q39 prospective lower-tier test (27 July 2026).** Q39 operationalised that
tier correction on the previously untouched `pure_strongmax` archive. It
defined one invariant scalar closure cut and its signed flow:

\[
\underbrace{h(t)}_{\substack{\text{connected-lattice}\\\text{closure cut}}}
=|\det C(t)|^{1/3},
\qquad
\underbrace{(u(t),v(t))}_{\substack{\text{ridge side}\\\text{and closure flow}}}
=
\left(
\frac{h(t)-m}{r},
\frac{\Delta h(t)}{s}
\right).
\]

The four signs of \((u,v)\) supplied four internal meta-quadrants of \(C\).
For four ordered quadrant identities, the frozen Information³ completion was

\[
\boxed{\widehat C_4=C_1-C_2+C_3},
\qquad
\text{equivalently}\qquad
C_1+C_3=C_2+\widehat C_4.
\]

This is the established affine/parallelogram closing relation. Q39 did not
derive that algebra from ARA. It tested whether ARA's independently declared
tier, connected identity and quadrant order locate that operator usefully.
The target missed the frozen seed floor (`71/80`), so the formal result is
**INCONCLUSIVE — ELIGIBILITY**. Descriptively, lineage-mean NRMSE was
`0.3074`, versus `0.9361–2.4375` for all controls; all seed-cluster
comparisons were favourable at the `20,000`-draw resolution, and the
wrong-order control was worst. The complete support rule failed because
persistence retained higher mean cosine and ARA was single-best on only
`48.96%` of cycles versus the frozen `55%`.

**Axiomatic consequence.** Proposition 3.2b gives only flip parity. Q39 adds
evidence that an ordered affine closing relation can retain useful
fourth-state magnitude information inside one connected lattice. It does not
prove that the four sign regions are four unique physical children, that
their boundaries can be forecast blindly or that every ARA identity obeys
affine closure. The correct conditional statement is:

\[
\left.
\begin{array}{c}
\text{one connected identity has a stable four-quadrant closure–flow chart},\\
\text{its ordered cycle approximately satisfies affine closure}
\end{array}
\right\}
\Longrightarrow
\widehat C_4=C_1-C_2+C_3
\text{ is a candidate masked-state reconstruction.}
\]

Full report:
`analysis/quantum/Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_REPORT_2026-07-27.md`.

**Post-result Q39A conditional-orientation refinement (27 July 2026).**
Q39's negative-cosine tail was not a direct marker of the deepest determinant
pinch. It was concentrated on the high-closure return branch. Let

\[
\underbrace{D}_{\substack{\text{ordered retained relation}\\
\text{between the first two visits}}}
=C_1-C_2,
\qquad
\underbrace{P}_{\substack{\text{unconditional affine}\\
\text{fourth-state prediction}}}
=C_3+D.
\]

The opened-data audit found the following target-blind conditional candidate:

\[
\boxed{
\widehat C_4=
\begin{cases}
C_3-D,&\cos(P,C_3)<0,\\
C_3+D,&\cos(P,C_3)\ge 0.
\end{cases}}
\]

Plainly: if carrying the ordered relation forward would reverse the current
parent orientation, reverse the **relation-flow contribution** rather than
the whole parent. On Q39's open archive this flag had `96.35%` precision and
`99.31%` recall for the negative target orientation; the conditional rule
improved every one of the `1,342` changed cycles and reduced lineage-mean
NRMSE from `0.3074` to `0.2508`.

This does not amend Proposition 3.2b or prove seam parity. The condition and
operator were found after Q39 outcomes were known. Its present axiomatic
status is therefore:

\[
\left.
\begin{array}{c}
\text{one ordered four-visit identity follows affine closure},\\
\text{the provisional fourth state points against the third}
\end{array}
\right\}
\Longrightarrow
\text{test a reversal of the retained relation term on untouched data.}
\]

It is a falsifiable Q40 hypothesis and a candidate ARA return-flow
orientation rule, not yet a general law or physical Phase-B identification.
Audit:
`analysis/quantum/Q39A_POST_RESULT_SEAM_PARITY_AUDIT_2026-07-27.md`.

### Proposition 3.2c — A parent ridge is not sufficient to identify coupling

Let two separately normalized local identities \(C,B\in(0,2)\) be coupled one rung up by:

\[
P(C,B)=\frac{2B}{C+B}.
\]

Then:

\[
P(B,C)=2-P(C,B).
\]

**Proof.**

\[
P(C,B)+P(B,C)
=
\frac{2B}{C+B}+\frac{2C}{B+C}
=2.
\]

Therefore an exchangeable relation-broken pairing has a parent distribution centred symmetrically around the
`1.0` ridge. An aggregate mean or median near `1` can arise without specific coupling.

**Operational consequence.** To identify a declared lower-level coupling, correct pairs must show additional
pairwise ridge concentration beyond controls that preserve both marginal identities but shuffle or misassign
their relation:

\[
\mathbb E\!\left[|P_{\rm paired}-1|\right]
<
\mathbb E\!\left[|P_{\rm broken}-1|\right].
\]

Q23 supplied the first prospective test of this distinction. All four genuine parent medians were near `1`, but
the paired blocks did not beat shifted, wrong-bit, spatially broken or permutation controls (`3/10` gates).
Thus the particular connection-web/bit coupling was not supported even though its parent was ridge-centred.
Report: `analysis/quantum/Q23_WILLOW_CONNECTION_BIT_REPORT_2026-07-26.md`.

### Definition 3.3 — Multiplicative handover law

Let \(d\geq0\) be relational path distance measured in handover units. Suppose the retained coupling after two
successive path segments is the product of the two retentions:

\[
K(d_1+d_2)=K(d_1)K(d_2),
\qquad K(0)=1,
\qquad K(1)=\varphi^{-1}.
\tag{3}
\]

### Theorem 4 — A continuous golden handover law must be exponential

If \(K\) is positive and continuous and satisfies (3), then

\[
\boxed{K(d)=\varphi^{-d}}.
\]

The reverse-direction ratio is \(K(d)^{-1}=\varphi^d\).

**Proof.** Define \(g(d)=\log K(d)\). Positivity makes the logarithm valid, and (3) gives

\[
g(d_1+d_2)=g(d_1)+g(d_2).
\]

The continuous solutions of this additive equation are \(g(d)=cd\). Because

\[
g(1)=\log K(1)=-\log\varphi,
\]

we have \(c=-\log\varphi\). Thus

\[
K(d)=e^{g(d)}=e^{-d\log\varphi}=\varphi^{-d}.
\]

Taking the reciprocal gives the reverse ratio \(\varphi^d\). \(\square\)

**Plain explanation.** If every handover loses or transfers the same *fractional* amount, successive handovers
multiply rather than add. Once one unit of relational distance is assigned the factor \(1/\varphi\), the only
continuous rule consistent with chaining is \(\varphi^{-d}\). This does not prove nature chooses the golden
factor; it proves the formula that follows if it does.

### Core operator summary

\[
\underbrace{2^{\Delta n}}_{\substack{\text{scale ratio}\\\text{ARA octave}}},
\qquad
\underbrace{\varphi^{\pm d}}_{\substack{\text{coupling ratio}\\\text{ARA handover path}}},
\qquad
\underbrace{F_{chart}^{N_r}}_{\substack{\text{orientation parity}\\\text{declared chart reversals}}},
\qquad
\underbrace{F_{dyn}^{N_s}}_{\substack{\text{proposed physical update}\\\text{ARA singularity crossings}}}.
\]

**Plain explanation.** Two says how far you zoom. Phi says how a relational handover compounds. The chart reversal says
whether the local geometry is read in its original or reversed orientation. A physical singularity crossing may
also update phase, coupling or rung. These operations can interact, but they are not the same coordinate and the
static mirror proof does not prove the physical update.

---

## 4. A retained labelled product model can preserve identities through coupling

Let two subsystem states be \(a\in V_A\) and \(b\in V_B\). Put them in the product state

\[
z=\begin{pmatrix}a\\b\end{pmatrix}\in V_A\oplus V_B.
\]

A general linear coupled evolution has the block form

\[
\frac{d}{dt}\begin{pmatrix}a\\b\end{pmatrix}
=
\begin{pmatrix}
A & K_{AB}\\
K_{BA} & B
\end{pmatrix}
\begin{pmatrix}a\\b\end{pmatrix}.
\tag{4}
\]

The direct-sum state space is a modelling decision: it explicitly retains two labelled slots. With that assumption:

### Theorem 5 — Nonzero coupling is not identity merger inside the retained product model

Even when \(K_{AB}\neq0\) and \(K_{BA}\neq0\), the two component states remain separately recoverable by the
canonical projections \(P_A(a,b)=a\) and \(P_B(a,b)=b\).

**Proof.** The state space is the direct sum \(V_A\oplus V_B\). By definition, every state in this space is one
ordered pair \((a,b)\). The projections satisfy

\[
P_A(a,b)=a,\qquad P_B(a,b)=b
\]

regardless of the values of the off-diagonal coupling maps. The couplings change the derivatives of \(a\) and
\(b\); they do not identify \(a\) with \(b\) or replace the product space with a quotient. \(\square\)

**Plain explanation.** Two identities can affect one another without becoming the same thing when the model keeps
their two labelled slots. The off-diagonal terms describe their interaction. The proof does not establish that
every physical coupling preserves independently recoverable identities: merger, coarse-graining, measurement loss,
or an inadequate observation channel can remove that recoverability. It proves the conditional mathematical home
for identity-preserving handover.

## 4.1 Gauss subset — exact signed boundary balance on an ARA diameter

Gauss's electric law supplies an established physical example of a complete-boundary signed reading. Define the
non-negative outward and inward electric-flux magnitudes

\[
\underbrace{\Phi_{out}}_{\text{outward boundary contribution}}
=\int_{\partial V}\max(\mathbf E\cdot\mathbf n,0)\,dA,
\qquad
\underbrace{\Phi_{in}}_{\text{inward boundary contribution}}
=\int_{\partial V}\max(-\mathbf E\cdot\mathbf n,0)\,dA.
\tag{4a}
\]

When \(T_\Phi=\Phi_{out}+\Phi_{in}>0\), define the typed flux-diameter instrument

\[
\underbrace{x_\Phi}_{\substack{\text{outward/inward mixture}\\\text{ARA flux-axis position}}}
=2\frac{\Phi_{out}}{\Phi_{out}+\Phi_{in}}.
\tag{4b}
\]

### Theorem 5.1 — Activity times centred asymmetry equals signed net flux

\[
\boxed{
\underbrace{\Phi_E}_{\text{signed net electric flux}}
=
\underbrace{T_\Phi}_{\text{total unsigned boundary activity}}
\underbrace{(x_\Phi-1)}_{\text{centred flux asymmetry}}
=
\frac{Q_{inside}}{\varepsilon_0}
}.
\tag{4c}
\]

**Proof.** By construction,

\[
T_\Phi(x_\Phi-1)
=(\Phi_{out}+\Phi_{in})
\left(2\frac{\Phi_{out}}{\Phi_{out}+\Phi_{in}}-1\right)
=\Phi_{out}-\Phi_{in}.
\]

Splitting the signed surface integral into its positive and negative parts gives

\[
\Phi_{out}-\Phi_{in}
=\oint_{\partial V}\mathbf E\cdot d\mathbf A.
\]

Gauss's law identifies that net flux with \(Q_{inside}/\varepsilon_0\). \(\square\)

If \(T_\Phi=0\), both flux parts and the net flux are zero, while \(x_\Phi\) is undefined rather than automatically
equal to 1. This distinguishes an empty/quiet boundary from an active balanced boundary with \(T_\Phi>0\) and
\(x_\Phi=1\).

**Plain explanation.** The ARA flux position says which boundary orientation dominates. Activity says how much
inward and outward field crosses the boundary in total. Their product gives the signed Gauss result. Equal inward
and outward activity lands at 1 and cancels in the net reading, while no activity has no meaningful mixture position
at all.

**Evidence fence.** Equation (4c) is an exact crosswalk because \(x_\Phi\) is constructed from the same flux parts
as the net result. It is not independent evidence for universal ARA. A stronger test would require a frozen ARA
decomposition to predict an independently measured coupling, mode or transition not algebraically guaranteed by
Gauss's law.

### TE-ARA definition — the same ARA geometry viewed as total allocation

**Canonical correction, 21 July 2026:** TE-ARA is not a second object beside ARA. It is the same `0–2` geometry read
as the total allocation of a declared identity. TE-ARA always equals `2`; earlier versions incorrectly used its name
for a variable expressed A/B subtotal.

The pure identity contains only its Phase A and Phase B:

\[
\boxed{
\underbrace{\mathrm{TE\!-\!ARA}_{pure}(I)}_{\substack{\text{pure two-pole}\\\text{identity geometry}}}
=
\underbrace{t_A^{(I)}}_{\text{identity Phase A}}
+
\underbrace{t_B^{(I)}}_{\text{identity Phase B}}
=2.
}
\]

For a real identity observed inside environment \(\mathcal E\), choose one non-overlapping account at a declared
boundary and time window:

\[
\boxed{
\underbrace{\mathrm{TE\!-\!ARA}_{obs}(I\mid\mathcal E)}_{\substack{\text{identity observed}\\\text{in context}}}
=
\underbrace{t_A+t_B}_{\text{expressed pure A/B pair}}
+
\underbrace{\sum_jc_j}_{\text{named environmental couplings}}
+
\underbrace{t_{Other}}_{\text{unresolved contextual coupling}}
=2.
}
\tag{4d}
\]

Here `Other` is not a third pole or constituent of the pure identity. For the observed account,

\[
p_c\ge0,
\qquad \sum_c p_c=1,
\qquad t_c=2p_c.
\]

The same-geometry bridge is explicit. Let \(T_{AB}=t_A+t_B>0\). With B oriented toward 2,

\[
\underbrace{x_{A/B}}_{\text{ARA mixture position}}
=2\frac{t_B}{T_{AB}},
\qquad
\underbrace{T_{context}}_{\text{environmental remainder}}=2-T_{AB}.
\]

For a pure/context-free identity, \(T_{AB}=2\), hence \(x_{A/B}=t_B\) and \(t_A=2-x_{A/B}\). This is why TE-ARA
is the same ARA geometry rather than an independent object.

For an energy-backed partition, \(p_c=E_c/E_{total}\). Dylan's example is

\[
\underbrace{t_A}_{0.25}
+
\underbrace{t_B}_{1.25}
+
\underbrace{t_{Other}}_{0.50}
=2.
\]

ARA supplies a declared A/B relation's pole-mixture position. TE-ARA is that same geometry's fixed total-allocation
view. The observed component and environmental-coupling allocations supply the variable distribution. Gauss supplies signed electric source flux. They are
different projections and must not be compared as untyped numbers.

The historical variable previously called TE-ARA is now the expressed pure-pair subtotal

\[
\underbrace{T_{AB}\equiv T_{id}}_{\substack{\text{observed A/B-family}\\\text{subtotal}}}
=2\frac{E_{id}}{E_{total}},
\qquad
\underbrace{T_{context}}_{\text{environmental remainder}}=2-T_{AB}.
\]

A candidate dimensionless expressed-pair contribution is therefore

\[
\underbrace{j_{id}}_{\text{signed identity contribution}}
=
\underbrace{\frac{T_{AB}}2}_{\text{variable expressed-pair share}}
\underbrace{(x-1)}_{\text{centred ARA direction}}.
\tag{4e}
\]

Using canonical `TE-ARA/2` in (4e) would merely multiply by one because TE-ARA is fixed at 2. Equation (4e) remains
an ARA aggregation hypothesis outside the exact Gauss decomposition. Applying it physically requires a common unit
scale, independently declared modes and separately measured surrounding contributions. Full correction:
`analysis/TE_ARA_CANONICAL_CORRECTION_2026-07-21.md`.

### Corollary 4.1 — Exact Hamiltonian energy-allocation appearance

For an isolated ideal harmonic oscillator,

\[
H=K+V=\frac{p^2}{2m}+\frac{kq^2}{2}>0.
\]

Let

\[
Q=\sqrt{k}\,q,\qquad P=\frac p{\sqrt m}.
\]

Then \(Q^2=2V\), \(P^2=2K\), and therefore

\[
\boxed{
\underbrace{Q^2+P^2}_{\substack{\text{Hamiltonian phase-space}\\\text{circle}}}
=2H,
\qquad
\underbrace{t_A}_{\text{configuration allocation}}=2\frac VH,
\qquad
\underbrace{t_B}_{\text{traversal allocation}}=2\frac KH,
\qquad
t_A+t_B=2.
}
\tag{4f}
\]

With B oriented toward the `2` pole,

\[
\boxed{
\underbrace{x_H}_{\substack{\text{Hamiltonian energy-allocation}\\\text{ARA coordinate}}}
=t_B
=2\frac KH
=2\frac{P^2}{Q^2+P^2}.
}
\tag{4g}
\]

**Proof.** Substitution gives \(Q^2=kq^2=2V\) and \(P^2=p^2/m=2K\). Hence
\(Q^2+P^2=2(V+K)=2H\). Dividing the two nonnegative energy accounts by \(H\) and multiplying by two gives
\(t_A+t_B=2(V+K)/H=2\). Equation (4g) follows from the declared B orientation. \(\square\)

**Plain explanation.** The ideal oscillator is one complete coupling system. Its fixed energy moves continuously
between a configuration expression and a momentum expression. Hamilton's circle retains the signed direction and
quadrant; the ARA diameter says how the energy is divided at that instant. Equal division gives `1.0`.

**Evidence fence.** This corollary is an exact coordinate transformation, not an independent prediction. `x_H=1`
is equal energy, not equal opposing force. The endpoints are regular oscillator handovers, not mathematical
divergences. Because squaring loses the signs of \(Q\) and \(P\), a complete state also requires the quadrant or
direction field. Full calculation:
`analysis/hamilton/HAMILTON_ARA_HARMONIC_OSCILLATOR_REPORT_2026-07-23.md`.

### Definition 4.2 — Perspective-unassigned closure and instantiated allocation

Before a measurement perspective is selected, TE-ARA assigns only the complete normalized closure

\[
\mathrm{TE\!-\!ARA}=2.
\]

Let \(\mathcal P=(\Omega,q,\tau_S,\Pi,k,\sigma)\) declare boundary, observable, time slice, projection, rung and
pole orientation. The instantiated allocation is

\[
\boxed{
\mathbf t^{(\mathcal P)}
=
\left(t_A,t_B,t_{J_1},\ldots,t_{J_n},t_{\mathrm{Other}}\right),
\qquad
\sum_ct_c^{(\mathcal P)}=2.
}
\tag{4h}
\]

For a second perspective \(\mathcal P'\),

\[
\mathbf t^{(\mathcal P')}
=
\mathcal R_{\mathcal P\rightarrow\mathcal P'}
\left(\mathbf t^{(\mathcal P)}\right),
\qquad
\sum_ct_c^{(\mathcal P')}=2.
\tag{4i}
\]

The transformation may combine, split, internalize or externalize components. Equation (4i) preserves normalized
closure, not necessarily each component or the native physical magnitude.

**Plain explanation.** TE-ARA is the sphere before selecting a diameter. Choosing how and where to measure it
creates the component ledger. Walking around, inward, outward or sideways changes the relational perspective and
therefore the decomposition, while every newly selected complete identity receives its own normalized total `2`.

**Evidence fence.** The fixed sum is definitional. A meaningful cross-rung claim requires predeclared components,
non-overlapping measurement, a separately retained physical activity scale, and a transformation that preserves or
predicts something not guaranteed by normalization.

### Corollary 4.3 — Noether conservation is stronger than normalized closure

If a Lagrangian has no explicit time dependence,

\[
\frac{\partial\mathcal L}{\partial t}=0
\quad\Longrightarrow\quad
\frac{dH}{dt}=0.
\tag{4j}
\]

If a generalized coordinate \(q\) is cyclic,

\[
\frac{\partial\mathcal L}{\partial q}=0
\quad\Longrightarrow\quad
\frac d{dt}\left(\frac{\partial\mathcal L}{\partial\dot q}\right)=0.
\tag{4k}
\]

Time translation therefore conserves energy; spatial translation conserves linear momentum; rotational symmetry
conserves angular momentum.

**Plain explanation.** TE-ARA always closes to `2` because it is a normalized account. Noether separately tells us
when the physical size carried by that account is truly unchanged while its internal allocation and state evolve.

**Evidence fence.** Noether's theorem is established physics. Interpreting its conserved quantity as the native
scale carried by a TE-ARA parent is a crosswalk; Noether does not prove the universal ARA sphere.

---

# Part II — Relational ternary, Information³, and conditional closure

## 5. Information³ begins with two identities plus their retained relation

Let two locally declared identities or readings be \(A\) and \(B\). Their typed relation is

\[
\underbrace{R}_{\substack{\text{mathematical relation}\\\text{ARA: informative third}}}
=
\underbrace{\mathcal C}_{\substack{\text{coupling/interaction map}\\\text{declared for the domain}}}
\left(
\underbrace{A}_{\text{first identity}},
\underbrace{B}_{\text{second identity}}
\right).
\]

### Definition 5.1 — Minimal relational ternary

\[
\boxed{
\underbrace{T[A,B]}_{\substack{\text{relational ternary}\\\text{ARA triangle lock}}}
=
\left(A,B,R=\mathcal C(A,B)\right)
}.
\tag{5a}
\]

The third entry is not automatically a third independent wave, state space, substance or reservoir. It preserves
how the first two are coupled. Depending on the domain, \(R\) may require several typed measurements—for example
strength, direction, delay, coherence and relative phase.

**Plain explanation.** Information A and Information B do not completely describe the identity unless we also keep
what happens between them. That relation is the “three for two.” Drawing the three records as a triangle provides
the minimum closed lock, but it does not introduce a third foundational wave.

## 5.1 One cycle-consistent triangular holonomy model

The following construction is one rigorous decompression of the relational ternary. It uses three labelled
vertices so that relation consistency can be tested around a closed route. The third vertex may represent a
relation-born identity, a third observation of the same process, or a separately declared component; the physical
interpretation must be fixed before measurement.

Let \(V_A,V_B,V_C\) be three state spaces with invertible relation maps

\[
R_{AB}:V_A\to V_B,
\qquad R_{BC}:V_B\to V_C,
\qquad R_{CA}:V_C\to V_A.
\]

Define the round-trip operator

\[
\overbrace{M_\triangle}^{\substack{\text{mathematical holonomy}\\\text{Information}^3\text{ round trip}}}
=R_{CA}R_{BC}R_{AB}.
\]

The triangle is **exactly closed** when \(M_\triangle=I_A\). This is a closure model for Information³, not its only
possible physical representation.

### Theorem 6 — Exact closure makes the three relations mutually consistent

Assume \(R_{CA}=R_{AC}^{-1}\). If \(M_\triangle=I_A\), then

\[
R_{AC}=R_{BC}R_{AB}.
\]

Thus the direct path from \(A\) to \(C\) agrees with the path through \(B\), and one seed state determines a
consistent state at all three vertices.

**Proof.** Exact closure gives

\[
R_{CA}R_{BC}R_{AB}=I_A.
\]

Left-multiply by \(R_{CA}^{-1}=R_{AC}\):

\[
R_{BC}R_{AB}=R_{AC}.
\]

For any \(a\in V_A\), define

\[
b=R_{AB}a,
\qquad c=R_{BC}b=R_{BC}R_{AB}a=R_{AC}a.
\]

The direct and indirect constructions of \(c\) coincide, and applying \(R_{CA}\) returns \(a\). \(\square\)

**Plain explanation.** Start with information at corner A. Carry it to B, then C, then back to A. If it returns
unchanged, the triangle is not pulling itself apart. It also means that going straight from A to C agrees with
going through B. The three pieces therefore tell one consistent story, which is the precise mathematical sense
in which the structure is non-ravelling in that slice.

### Theorem 7 — Approximate closure bounds unravelling error

Define the closure residual

\[
\overbrace{\epsilon_\triangle}^{\substack{\text{operator error}\\\text{ARA unravelling amount}}}
=\|M_\triangle-I_A\|.
\]

Then for every state \(a\in V_A\),

\[
\|M_\triangle a-a\|\leq\epsilon_\triangle\|a\|.
\]

**Proof.** By the definition of an induced operator norm,

\[
\|M_\triangle a-a\|
=\|(M_\triangle-I_A)a\|
\leq\|M_\triangle-I_A\|\,\|a\|
=\epsilon_\triangle\|a\|.
\]

\(\square\)

**Plain explanation.** Real systems will rarely close perfectly. This gives a clean error bar: if the triangle's
closure residual is small, the amount by which information fails to return is also guaranteed to be small. The
residual can therefore be treated as a measurable unravelling score.

**Modelling fence.** Exact closure used invertible relation maps. Real channels can be lossy or dimension-changing;
those cases require reconstruction maps or pseudoinverses and should be judged by held-out closure residual rather
than assumed to close exactly.

## 6. Closure as one candidate aggregation law

Let \(\mathcal C\) replace a closed labelled triangle with one higher-level object \(H\), while retaining the
seed state and the relation maps needed to reconstruct its three constituents:

\[
\underbrace{(A,B,C;R_{AB},R_{BC},R_{CA})}_{\text{lower-rung closed triangle}}
\xrightarrow{\ \mathcal C\ }
\underbrace{H}_{\text{higher-rung identity}}.
\]

### Theorem 8 — A closed triangle can be losslessly represented by one seed plus its relations

Under the assumptions of Theorem 6, the complete consistent triangle state is uniquely determined by one state
\(a\in V_A\) together with the fixed maps \(R_{AB}\) and \(R_{AC}\).

**Proof.** From \(a\), reconstruct

\[
b=R_{AB}a,
\qquad c=R_{AC}a.
\]

Theorem 6 guarantees that these values satisfy all three relations and return consistently around the loop. No
additional independent state variable is needed. Conversely, projecting the triangle onto vertex \(A\) recovers
the seed \(a\). Therefore the representation is lossless when the relation maps are included. \(\square\)

**Plain explanation.** Once the triangle closes, its three corners no longer need to be carried as three unrelated
facts. One corner plus the stable rules connecting the corners recreates the whole thing. That lets the complete
triangle behave as one identity at the next scale without erasing its internal construction.

### Conditional proposition 8.1 — One sufficient fractal construction by repeated triangular closure

If every rung uses the same local ARA coordinate, the same closure test, and the same collapse operation
\(\mathcal C\), then a hierarchy built by repeatedly closing triangles is self-similar at every finite depth.

**Proof.** At depth zero, the construction has the stated local form. Assume every identity at depth \(n\) was
produced by the same closed-triangle rule. Applying the same rule to three depth-\(n\) identities produces a
depth-\(n+1\) identity with the same form. Induction proves the claim for every finite \(n\). \(\square\)

**Plain explanation.** If three closed things make one new thing, and the new things obey the same rule, then that
particular pattern repeats automatically as far as you continue it. This proves mathematical self-similarity *once
the repeated triangular rule is assumed*. It does not make the triangle the primitive ARA object or require every
physical interaction to be a triad.

### Conditional proposition 8.1b — General relational recursion

The broader ARA recursion can be written without requiring three independent lower-rung objects:

\[
\underbrace{P_k}_{\text{lower-rung identity}}
=
\left[A_k,B_k,R_k=\mathcal C_k(A_k,B_k)\right],
\qquad
\underbrace{P_{k+1}}_{\text{parent identity}}
=
\left[P_k,C_k,R(P_k,C_k)\right].
\tag{8a}
\]

If every persistent relation-born identity can re-enter the same typed two-sided construction while retaining its
internal relation, the ARA relational form is recursively reusable. This is the present mathematical statement of
“scalable reversible ternary.” Local reversibility requires enough labelled relational information to reconstruct
the missing member; physical time reversal is not implied.

**Modelling fence.** Equations (8a) define a recursive formalism. Whether the same relation, scale transform and
closure criterion recur in nature across independently measured rungs is the empirical fractal claim.

---

# Part III — Conditional finite-section geometry: triangle, hexagon, pentagon, and golden landmarks

## 7. One reduced-sphere construction

The constructions in this part are exact once their regularity and graph operations are assumed. They provide
finite relational scaffolds, projections and candidate landmarks of the ARA circle/sphere. They are not proved to
be the necessary physical unfolding of every ARA occurrence, and their exact geometry does not by itself establish
an energy leak, a Space/Time assignment, or a preferred natural handover.

The geometric interpretation clarified after the first draft has a **reduction** followed by an **unpacking**:

\[
\boxed{
\underbrace{B^3}_{\substack{\text{filled ARA state ball}\\\text{shell plus mixture interior}}}
\xrightarrow{\text{central time slice}}
\underbrace{B^2}_{\substack{\text{slice disk}\\\partial B^2=S^1}}
\xrightarrow{\text{central diameter}}
\underbrace{B^1}_{\text{minimal ARA line}}
}
\tag{7a}
\]

\[
\boxed{
\underbrace{B^1}_{\text{ARA diameter}}
\xrightarrow{\text{restore branch + gradient signs}}
\underbrace{S^1_{4Q}}_{\substack{\text{circle/wave}\\\text{four quadrants}}}
\xrightarrow{\text{choose minimum closed sampling}}
\underbrace{C_3}_{\text{triangle}}
\xrightarrow{\text{regular phase + anti-phase construction}}
\underbrace{C_6}_{\text{hexagon}}
\xrightarrow{\text{candidate observer contraction/webbing}}
\underbrace{C_5}_{\text{visible pentagon}}
}
\tag{7b}
\]

Here \(S^1_{4Q}\) means the circle equipped with the two sign coordinates from Corollary 2.4, and \(C_n\) denotes
the cycle graph with \(n\) vertices and \(n\) edges. The last arrow is initially a topological projection claim:
producing a *regular metric pentagon* additionally requires a geometric relaxation or projection rule that fixes
its visible lengths and angles. Equation (7b) is one exact-when-constructed route through the representations; it
does not state that every physical ARA must traverse those polygon orders.

### Theorem 8.2 — The triangle is the minimum closed map that determines a circle

A simple closed graph has at least three vertices, and three non-collinear points in the Euclidean plane determine
one unique circle.

**Proof.** A simple graph cycle cannot have one vertex because loops are excluded, and it cannot have two vertices
because parallel edges are excluded. The three-vertex cycle \(C_3\) exists, so it is the smallest simple closed
connection.

Now let \(A,B,C\) be non-collinear points. The perpendicular bisector of \(AB\) is the set of points equidistant
from \(A\) and \(B\); the perpendicular bisector of \(BC\) is the set equidistant from \(B\) and \(C\). Because
the points are non-collinear, these bisectors meet at one point \(O\). Then

\[
|OA|=|OB|=|OC|,
\]

so the circle centred at \(O\) through any one of the three points passes through all three. Any circle through
\(A,B,C\) must have its centre on both perpendicular bisectors, so its centre must be \(O\); therefore the circle
is unique. \(\square\)

**Plain explanation.** One point or two points can sit on infinitely many different circles. Three points, as
long as they are not all on one straight line, lock down one circle. Connecting those three points also gives the
smallest possible closed loop. This is the precise mathematical version of the triangle being the minimum
connection map by which a circular identity can hold a definite shape.

### Theorem 8.3 — A regular phase triangle and its anti-phase copy form a regular hexagon

Place a regular triangle on the unit circle at phases

\[
0,\quad \frac{2\pi}{3},\quad \frac{4\pi}{3}.
\]

Rotate it by the anti-phase angle \(\pi\). The union of the two vertex sets is the vertex set of a regular hexagon.

**Proof.** Adding \(\pi\) to the three original phases gives

\[
\pi,\quad \frac{5\pi}{3},\quad \frac{7\pi}{3}\equiv\frac\pi3\pmod{2\pi}.
\]

Sorting the combined phases gives

\[
0,\quad\frac\pi3,\quad\frac{2\pi}{3},\quad\pi,\quad\frac{4\pi}{3},
\quad\frac{5\pi}{3}.
\]

Every neighbouring pair differs by \(\pi/3=60^\circ\). Six equally spaced points on one circle are precisely
the vertices of a regular hexagon. \(\square\)

**Plain explanation.** Draw one equilateral triangle on a circle. Now place its exact 180-degree opposite on the
same circle. The two triangles interleave, filling the six equally spaced positions of a hexagon. So the hexagon
really can be understood as one minimum closure together with its phase-reversed partner working in synchrony.

### Theorem 8.4 — Webbing one hexagonal relation shut produces a five-cycle topologically

Contract any one edge of the cycle graph \(C_6\), identifying its two endpoints as one vertex. The resulting graph
is isomorphic to \(C_5\).

**Proof.** Label the vertices of \(C_6\) cyclically \(v_0,\ldots,v_5\), and contract the edge
\((v_0,v_1)\) to one vertex \(w\). The remaining cyclic edges are

\[
(w,v_2),(v_2,v_3),(v_3,v_4),(v_4,v_5),(v_5,w).
\]

They form one simple cycle with five vertices and five edges, which is \(C_5\). \(\square\)

**Plain explanation.** If two neighbouring positions of a hexagonal loop are compressed into one visible
position—your “webbed shut” edge—the observer counts five positions around the loop. This proves the topological
hexagon-to-pentagon reduction. It does not yet prove that the five visible positions must redistribute into the
equal sides and angles of a perfectly regular pentagon.

### Theorem 8.5 — A many-to-one slice has a nonnegative hidden-information cost

Let \(X\) be the complete hexagonal state and let \(Y=P(X)\) be its deterministic contracted or observed state.
Then

\[
\boxed{
\underbrace{H(X)-H(Y)}_{\substack{\text{information hidden by projection}\\\text{ARA webbing/leak candidate}}}
=\underbrace{H(X\mid Y)}_{\text{unresolved full-state information}}\geq0
}
\tag{8}
\]

for discrete Shannon entropy.

**Proof.** Because \(Y\) is determined by \(X\), \(H(Y\mid X)=0\). The entropy chain rule gives

\[
H(X,Y)=H(X)+H(Y\mid X)=H(X),
\]

and also

\[
H(X,Y)=H(Y)+H(X\mid Y).
\]

Equating the two expressions yields \(H(X)-H(Y)=H(X\mid Y)\). Conditional entropy is nonnegative for discrete
variables, proving the result. \(\square\)

**Plain explanation.** If our time slice compresses several complete hexagonal states into the same five-edge
appearance, some information about the full sphere is necessarily hidden from us. The amount is the uncertainty
left about the full state after we see the projection. This gives “webbing cost” a precise information-theory
meaning. Turning that hidden-information cost into thermodynamic entropy or a fixed energy leak requires an
additional physical law and measurement.

#### Corollary 8.5a — A non-injective child-to-parent closure is an inter-rung ARA singularity

Let the resolved child configuration be \(X=(C_1,\ldots,C_n)\), and let

\[
\underbrace{Y}_{\substack{\text{one parent state}\\\text{next-rung identity}}}
=
\underbrace{\mathcal R(X)}_{\substack{\text{child-to-parent closure}\\\text{coarse-graining map}}}.
\]

If \(\mathcal R\) is not injective, then distinct child configurations \(X\ne X'\) can satisfy
\(\mathcal R(X)=\mathcal R(X')\). For any distribution assigning positive probability to more than one such
preimage,

\[
H(X\mid Y)>0.
\]

For the fixed-activity linear state average

\[
s_P=\frac{\sum_iT_i s_i}{\sum_iT_i},
\]

every nonzero child perturbation satisfying \(\sum_iT_i\delta_i=0\) is invisible to the parent:

\[
\mathcal R(s_1+\delta_1,\ldots,s_n+\delta_n)
=
\mathcal R(s_1,\ldots,s_n).
\]

**Proof.** Non-injectivity supplies at least two distinct preimages of the same parent. A distribution with positive
weight on both leaves nonzero uncertainty about \(X\) after \(Y\) is known, hence \(H(X\mid Y)>0\) by Theorem 8.5.
For the linear average, substituting \(s_i+\delta_i\) changes the numerator by
\(\sum_iT_i\delta_i=0\), so the parent is unchanged. \(\square\)

**Plain explanation.** Moving upward from children to one parent can close several distinguishable arrangements
into the same identity. Their differences have crossed out of the retained parent description even though they may
still exist in the decompressed system. ARA calls this an **inter-rung child-mixing singularity**. It is distinct
from an **intra-rung phase singularity**, where one retained signed A/B state reverses orientation. Established
mathematics calls the first operation non-injective coarse-graining or aggregation; “singularity” is the declared
ARA identity-transition term.

### Interpretation fence — two pentagon constructions

The quotient result above and the angular-defect result below are related but not identical:

1. **Observer quotient:** a six-cycle is seen as a five-cycle because one relation is contracted or hidden.
2. **Intrinsic five-fold geometry:** five equilateral triangles around a vertex leave a \(60^\circ\) angular
   defect and therefore favour curvature.

ARA proposes that the second may be the geometric relaxation of the first—the webbed projection curving into the
next slice—but that bridge is a physical/geometric hypothesis, not established by either theorem alone.

## 7.1 Exact pentagon and projection mathematics

### Theorem 9 — A regular pentagon contains the golden ratio

For a regular pentagon with side length \(s\) and diagonal length \(d\),

\[
\frac ds=\varphi.
\]

**Proof.** Similar triangles in the pentagram give

\[
\frac ds=1+\frac sd.
\]

Let \(q=d/s>0\). Then \(q=1+1/q\), so

\[
q^2-q-1=0.
\]

The positive solution is

\[
q=\frac{1+\sqrt5}{2}=\varphi.
\]

\(\square\)

**Plain explanation.** Phi is not painted onto a pentagon afterwards. It is forced by the pentagon's own similar
triangles: the diagonal is exactly phi times the side.

### Theorem 9.1 — The side-one pentagon contains an exact \(1,1,\varphi\) Information³ handover triangle

Let \(A_k,B,A_{k+1}\) be three consecutive vertices of a regular pentagon with
side length `1`, where the two \(A\)-labels mark corresponding phase identities
and \(B\) marks the intervening opposite-phase identity. Then

\[
\boxed{
|A_kB|=1,
\qquad
|BA_{k+1}|=1,
\qquad
|A_kA_{k+1}|=\varphi
}.
\tag{9a}
\]

Consequently, the indirect mixed-phase route and direct same-phase route are

\[
\underbrace{|A_kB|+|BA_{k+1}|}_{A_k\rightarrow B\rightarrow A_{k+1}}
=2,
\qquad
\underbrace{|A_kA_{k+1}|}_{A_k\rightarrow A_{k+1}}
=\varphi,
\]

and their path difference is

\[
\boxed{2-\varphi=\varphi^{-2}}.
\tag{9b}
\]

The triangle's angles are

\[
36^\circ,
\qquad108^\circ,
\qquad36^\circ,
\]

with \(108^\circ\) opposite the \(\varphi\)-length side.

**Proof.** The first two lengths equal `1` by the side normalization. The
segment \(A_kA_{k+1}\) skips the intervening vertex and is therefore a pentagon
diagonal; Theorem 9 gives its length as \(\varphi\). Corollary 1.1 gives
\(2-\varphi=\varphi^{-2}\). Let \(\theta\) be the angle at \(B\). The cosine law
gives

\[
\cos\theta
=\frac{1^2+1^2-\varphi^2}{2}
=\frac{1-\varphi}{2}
=-\cos72^\circ,
\]

so \(\theta=108^\circ\). The triangle is isosceles, so each remaining angle is
\((180^\circ-108^\circ)/2=36^\circ\). \(\square\)

**Information³ reading.** The three vertices retain the earlier phase identity
\(A_k\), the intervening opposite-phase identity \(B\), and the corresponding
next-scale phase identity \(A_{k+1}\). The two unit relations give the ordered
mixed path, while the \(\varphi\)-length base retains the direct relation between
the two \(A\) identities. Thus the \(1,1,\varphi\) triangle is an exact Euclidean
realization of the minimal relational ternary from Definition 5.1:

\[
\boxed{
\left(A_k,\,A_{k+1},\,
\mathcal C(A_k,A_{k+1})\text{ resolved through }B\right)
}.
\]

The reversed construction

\[
B_k\rightarrow A\rightarrow B_{k+1}
\]

has the same metric with the phase labels exchanged. This mathematical
realization does not prove that physical systems universally use
\(\varphi\) for same-phase cross-rung handover.

**Plain explanation.** Going from one Phase A to the next Phase A through the
intervening Phase B takes two unit steps. Going directly between the two Phase
A positions takes exactly Phi. Keeping the two identities and both ways of
relating them closes the smallest Information³ triangle. The untraversed
difference between the paths is exactly the reverse Phi landmark `0.382`.

### Corollary 9.2 — Five handover triangles generate the pentagram and its next \(\varphi^{-2}\) rung

Apply Theorem 9.1 at each of the five cyclic triples of consecutive pentagon
vertices. The five direct same-phase segments are exactly the five pentagon
diagonals and therefore form a pentagram. Their proper intersections form a
similar inner regular pentagon whose side-to-outer-side ratio is

\[
\boxed{\varphi^{-2}}.
\tag{9c}
\]

Repeating the same construction produces scales

\[
1,
\quad\varphi^{-2},
\quad\varphi^{-4},
\quad\varphi^{-6},
\quad\ldots
\]

**Proof.** The five cyclic choices supply all five diagonals. By the similar
triangles used in Theorem 9, each diagonal is divided at a pentagram
intersection in the ratio \(\varphi:1\). The inner pentagon is similar to the
outer pentagon and its side is \(1/\varphi^2\) of the outer side. Applying the
same similarity recursively multiplies the scale by \(\varphi^{-2}\) at every
step. \(\square\)

**Plain explanation.** One locked triangle supplies one Phi connection.
Rotating that triangle around the five available positions supplies all five
Phi connections. They cross to make a smaller pentagon, which repeats the same
construction at exactly `0.382` of the previous size. This is the exact finite
geometry behind the proposed recursive Phi-pillar scaffold.

### Theorem 9.3 — A ridge-centred Phi circle generates an irrational handover train against the ARA octave

Tile one axis by standard ARA circles whose diameter intervals are

\[
C_m=[2m,2m+2],
\qquad m\in\mathbb Z.
\]

Let

\[
a=2-\varphi=\varphi^{-2},
\qquad
b=\varphi,
\]

and define a second tangent-circle train by the diameter intervals

\[
H_n=
\left[
a+n\ell,
b+n\ell
\right],
\qquad
\ell=b-a.
\]

Then:

\[
\boxed{
\ell=\frac{2}{\varphi},
\qquad
\frac{\ell}{2}=\frac1\varphi,
\qquad
\frac{a+b}{2}=1
}.
\tag{9d}
\]

Relative to the period `2` of the standard ARA train, successive Phi-circle
centres and contacts advance by the normalized phase

\[
\boxed{\frac{\ell}{2}=\frac1\varphi}.
\tag{9e}
\]

No positive integer number of these advances returns to exactly the same phase
of the standard train. If (F_k) is the `k`th Fibonacci number, the near-return
error after (F_k) advances is

\[
\boxed{
\frac{F_k}{\varphi}-F_{k-1}
=(-1)^{k-1}\varphi^{-k}
}.
\tag{9f}
\]

On a finite grid of eighths, the nearest symmetric endpoint pair is

\[
\boxed{
2-\varphi\approx\frac38,
\qquad
\varphi\approx\frac{13}{8}
},
\tag{9g}
\]

with equal endpoint error

\[
\frac{13}{8}-\varphi
=(2-\varphi)-\frac38
=0.00696601125\ldots.
\]

**Proof.** From (arphi^2=\varphi+1),

\[
b-a
=\varphi-(2-\varphi)
=2\varphi-2
=2(\varphi-1)
=\frac{2}{\varphi}.
\]

Halving gives (1/\varphi), and (a+b=2) places the first circle's centre at
the ridge `1`. An exact return after (n>0) advances would require
(n/\varphi\in\mathbb Z), which is impossible because (arphi) is
irrational. Identity (9f) follows by induction from the Fibonacci recurrence
and (1/\varphi=\varphi-1). The eighth-grid statements follow by direct
substitution. \(\square\)

**Plain explanation.** The ordinary circle train walks in exact steps of `2`.
The ridge-centred Phi circle train walks in steps of `2/phi`. Those step sizes
never lock exactly, so their contact point keeps moving through the ARA circle,
with increasingly close Fibonacci returns. When that irrational pair is
coarse-grained to eighths, it appears as the nearby connected pair
`3/8` and `13/8`.

**Interpretation fence.** This theorem proves the behaviour of the declared
two-circle construction. It does not prove that a physical time vector, river
thalweg, quantum trajectory or other empirical system uses that construction.
`3(3/8)=9/8` is a separate three-step arithmetic candidate and is not implied
as a circle-train period by this theorem. A physical test must measure ordered
handover increments or contact phases; absolute landmark occupancy is a
different observable.

### Theorem 10 — The projected octave identity

\[
\varphi=2\cos36^\circ=2\cos\frac\pi5.
\]

**Proof.** In a regular pentagon inscribed in a circle of radius \(R\), the side and diagonal are chords:

\[
s=2R\sin36^\circ,
\qquad
d=2R\sin72^\circ.
\]

Therefore, using \(\sin(2a)=2\sin a\cos a\),

\[
\frac ds
=\frac{\sin72^\circ}{\sin36^\circ}
=2\cos36^\circ.
\]

Theorem 9 gives \(d/s=\varphi\), hence \(\varphi=2\cos36^\circ=2\cos(\pi/5)\). \(\square\)

**Plain explanation.** A line of length 2 projected at 36 degrees has length phi. That exact geometry supports
your phrase “the octave viewed through the pentagon angle.” The equation is proven; the further claim that
physical time is literally this projection remains a physical hypothesis.

### Theorem 11 — Six equilateral triangles are flat; five leave a 60-degree defect

At a common vertex, six equilateral triangles have total angle \(360^\circ\), while five have total angle
\(300^\circ\) and angular defect \(60^\circ\).

**Proof.** Each equilateral-triangle angle is \(60^\circ\). Therefore

\[
6\times60^\circ=360^\circ,
\qquad
5\times60^\circ=300^\circ,
\qquad
360^\circ-300^\circ=60^\circ.
\]

\(\square\)

**Plain explanation.** Six triangles can lie flat around a point. Remove one and the remaining five cannot fill
the plane; the missing 60 degrees forces curvature when the surface closes. This proves the flat-versus-curved
geometry. Calling those sides Space and Time is the ARA interpretation placed on top of it.

---

# Part IV — Observer projection, Light/Dark, and dark matter

## 8. Why a sector can be invisible to one channel and visible to another

Let the complete state space split as

\[
U=U_{LI}\oplus U_D,
\]

where \(U_{LI}\) is the Light–Information sector accessible through an electromagnetic observation map
\(\Pi_{LI}\), and \(U_D\) is a complementary sector. Let \(G\) be a gravitational observation map.

### Theorem 12 — Channel-relative invisibility

If \(d\in\ker\Pi_{LI}\) but \(G(d)\neq0\), then no observation using only \(\Pi_{LI}\) can distinguish \(d\)
from zero, while a gravitational observation can.

**Proof.** Since \(d\in\ker\Pi_{LI}\),

\[
\Pi_{LI}(d)=0=\Pi_{LI}(0).
\]

Thus the two states have identical output in that channel. But \(G(d)\neq0=G(0)\), so the gravitational channel
distinguishes them. \(\square\)

**Plain explanation.** Something can be completely dark to light-based instruments without being absent. If it
still affects gravity, we can infer it through that second relationship. “No information” therefore needs to mean
“no information through our dominant channel,” not “no state or structure of any kind.”

## 9. One accessible information relation instead of three

Represent a complete closed identity by three informational components:

\[
\mathscr I=(I_A,I_B,I_R),
\]

where \(I_A\) and \(I_B\) describe two identities and \(I_R\) describes their relation. Let the human
electromagnetic projection be

\[
P_{\rm human}(I_A,I_B,I_R)=I_R.
\]

### Theorem 13 — Rank-one projection exposes one independent component

If each component is one-dimensional, then \(P_{\rm human}\) has rank one and kernel dimension two. Therefore
the observer accesses one independent information component while two remain unobserved.

**Proof.** The domain has dimension three. The image contains only the one coordinate \(I_R\), so
\(\operatorname{rank}P_{\rm human}=1\). By rank–nullity,

\[
\dim\ker P_{\rm human}=3-1=2.
\]

\(\square\)

**Plain explanation.** This is the exact mathematical form of “one information instead of three” as a perception
claim. The complete structure may still contain two identities and their relation, but our channel returns only
the relational effect. For dark matter, that one output could be the gravitational deformation we infer.

### Conditional proposition 13.1 — Dark-side closure with a one-edge projection

If a dark-side Information³ triangle closes internally but its two node channels lie in \(\ker\Pi_{LI}\), then it
can remain a stable identity while appearing to a Light-coupled observer only through one gravitational relation.

**Proof.** Internal closure follows from Theorem 6 and does not depend on \(\Pi_{LI}\). Theorem 13 shows that the
projection can suppress two independent components while retaining the relation. Therefore internal stability and
one-channel appearance are mathematically compatible. \(\square\)

**Plain explanation.** Dark matter does not have to be an unclosed loose thread. It may have a full closure on its
own side of the geometry, while our light-based slice reveals only one edge of that structure. This reconciles
“one accessible information” with persistent halos and gravitational organisation.

## 10. Light–Information and Dark–Matter as a flip-equivariant pair

Define a proposed involution on these domain labels by

\[
F_{LD}(L)=D,
\qquad F_{LD}(D)=L,
\qquad F_{LD}(I)=M,
\qquad F_{LD}(M)=I.
\]

Assume a coupling operation \(C\) is flip-equivariant:

\[
F_{LD}(C(a,b))=C(F_{LD}(a),F_{LD}(b)).
\tag{5}
\]

### Conditional proposition 14 — The coupled anti-phase image

Under (5),

\[
F_{LD}(C(L,I))=C(D,M).
\]

**Proof.** Substitute \(a=L\) and \(b=I\) into (5):

\[
F_{LD}(C(L,I))=C(F_{LD}(L),F_{LD}(I))=C(D,M).
\]

\(\square\)

**Plain explanation.** If the proposed domain-label flip reverses both Light↔Dark and Information↔Matter while preserving
the form of coupling, then the Dark–Matter combination is automatically the flipped partner of the
Light–Information combination. This proves the symmetry inside the proposed model. It does not yet prove that
physical quantum theory and cosmological dark matter instantiate those labels or that this label map equals the
dynamical singularity-crossing map \(F_{dyn}\).

**Physics fence.** Quantum mechanics also applies to massive and potentially dark systems. The defensible ARA
claim is that Light–Information coupling provides the part of quantum behaviour directly accessible to an
electromagnetic observer, not that light creates quantum mechanics itself.

---

# Part V — The dark-sector \(7/2\) path and cosmic fractions

## 11. The diagonal handover distance

Model the relevant coupling projection by a weighted Manhattan plane. Put dark matter at \((0,0)\) and baryonic
matter at \((2,3/2)\), where the first displacement represents the horizontal coupling cost and the second the
vertical/singularity-crossing cost:

\[
d_1((u,v),(u',v'))=|u-u'|+|v-v'|.
\]

### Conditional proposition 15 — The shortest legal diagonal path has cost \(7/2\)

Every path from \((0,0)\) to \((2,3/2)\) has Manhattan length at least \(7/2\), and any monotone path attains it.

**Proof.** The net coordinate changes are \(\Delta u=2\) and \(\Delta v=3/2\). The total variation of any path
is at least the magnitude of its net change on each axis, so

\[
L\geq|\Delta u|+|\Delta v|=2+\frac32=\frac72.
\]

A path that moves monotonically through exactly these two displacements has length \(7/2\), so the lower bound is
attained. \(\square\)

**Plain explanation.** If the legal route really requires a cost of 2 across one coupling direction and 1.5
across the other, there is no shorter diagonal shortcut. The total is necessarily 3.5. What still needs external
justification is why nature assigns exactly those two primitive costs.

**Quantum implementation audit and correction (Q33, 26 July 2026).** Q33
attempted to test one assignment of the vertical cost:

\[
\frac32
=
\underbrace{1}_{\text{current-rung whole}}
+
\underbrace{\frac12}_{\text{child capacity in the parent frame}}.
\]

The Q32 endpoint recipients began near their own local ARA poles. Q33 then
measured an unbounded raw endpoint/source capacity ratio of \(1.27349\) and
incorrectly substituted it for the geometric \(1/2\) rung coefficient. This
conflated the system-specific flow over ARA with the invariant rung geometry.
It also averaged both endpoint recipients rather than using the single child
closest to the boundary. The resulting \(4.27349\) path is therefore not a
valid ARA path calculation. Proposition 15 remains a conditional metric
theorem, and Q33 supplies neither support nor contrary evidence for its
primitive \(1/2\) rung weight. The raw capacity and backward-origin results
remain descriptive diagnostics.

**ARA-first consequence test (Q33B, 26 July 2026).** Q33B did not estimate
the \(1/2\) rung weight. It held

\[
\mathcal R_\uparrow(1_c)=\frac12
\]

fixed as geometry and used it to choose a directed consequence: after a
high-side source releases, the single endpoint child nearest the low boundary
should gain relation closure. For child closure
\(h_c=|\det C_c|^{1/3}\), frozen development scale \(s_c\), starting order
\(z_c=h_c/s_c\), and next movement \(g_c=\Delta h_c/s_c\), Q33B selected the
smaller-\(z\) endpoint without future values. On `11,543` evaluation events,
that route had positive \(g\) in `63.64%`, compared with `55.83%` for its
sibling and `50.79–56.38%` for same-rule displaced controls. All frozen
paired, branch and cluster-bootstrap gates passed.

**Plain explanation.** The half-rung was treated as part of the ruler, not
something that the measured energy was allowed to change. That fixed ruler
successfully pointed to the endpoint relation that closed more reliably on
the next slice. This is evidence for a consequence of the conditional route
inside one simulator. It does not prove why the primitive half-rung law is
universal, and it does not turn the structural \(7/2\) into a fitted physical
constant.

**Cross-archive boundary (Q34, 26 July 2026).** The complete Q33B rule was
then frozen unchanged and moved to a previously unused greedy-ordering
archive. On `16,001` evaluation events, the exact route retained positive
median closure flow in both branches and was positive in `54.21%`, but missed
the frozen `55%` floor. It failed required paired/control gates and fell
`9.43` percentage points below Q33B. Independent raw-HDF5 reconstruction
passed.

**Plain explanation.** The geometric ruler was kept fixed, but it no longer
picked out a reliably superior child when the network's construction order
changed. Therefore Q33B cannot presently be promoted into a
network-independent theorem. The surviving weak direction is a clue, not a
passed replication. A future rule that includes network identity or coupling
orientation must be declared as a new conditional extension and tested on
another untouched target.

### Corollary 15.1 — Golden handover ratio along the diagonal

Under Theorem 4's multiplicative handover law, the reverse-direction component ratio is

\[
\boxed{
\frac{\Omega_{DM}}{\Omega_b}=\varphi^{7/2}\approx5.388361704
}.
\]

**Proof.** Substitute \(d=7/2\) into the reverse handover factor \(\varphi^d\). \(\square\)

**Plain explanation.** Once 3.5 is established as the relational path length, powers of phi are not separately
fitted at every step. The chaining rule turns that path into the ratio \(\varphi^{3.5}\). The important empirical
question is whether the path and its weights were fixed independently of the cosmic density data.

## 12. Closed-form present-day cosmic fractions

Assume the three-component present-day model

\[
\Omega_{DE}+\Omega_{DM}+\Omega_b=1,
\qquad
\frac{\Omega_{DE}}{\Omega_{DM}}=\varphi^2,
\qquad
\frac{\Omega_{DM}}{\Omega_b}=\varphi^{7/2}.
\tag{6}
\]

### Conditional proposition 16 — The fractions are uniquely determined

The unique positive solution of (6) is

\[
\boxed{
\Omega_{DM}=\frac1{\varphi^2+1+\varphi^{-7/2}}
}
\]

\[
\boxed{
\Omega_{DE}=\frac{\varphi^2}{\varphi^2+1+\varphi^{-7/2}},
\qquad
\Omega_b=\frac{\varphi^{-7/2}}{\varphi^2+1+\varphi^{-7/2}}
}
\]

with numerical values

\[
(\Omega_{DE},\Omega_{DM},\Omega_b)
\approx(0.688300769,0.262907499,0.048791732).
\]

**Proof.** From the ratios,

\[
\Omega_{DE}=\varphi^2\Omega_{DM},
\qquad
\Omega_b=\varphi^{-7/2}\Omega_{DM}.
\]

Substitute these into the sum constraint:

\[
\Omega_{DM}(\varphi^2+1+\varphi^{-7/2})=1.
\]

The coefficient is positive, so division gives one unique positive \(\Omega_{DM}\). The other two values follow
from their ratios. Direct substitution verifies that they sum to one. \(\square\)

**Plain explanation.** Once the two ratios and flat three-component sum are assumed, there is no freedom left:
the three numbers must have the displayed values. This proves the algebra of the dark-sector formula. It does not
prove the two ratios themselves, and it should presently be described as a present-day approximation rather than
a constant ratio across cosmic history.

**Dynamics fence.** A constant density ratio at every redshift does not follow from (6). A time-dependent theory
still needs evolution equations, for example an ARA-derived transfer term \(Q\) in coupled dark-sector continuity
equations.

---

# Part VI — LLM subset: what the triangle metric proves and what it does not

## 13. Triangle counting by \(\operatorname{tr}(A^3)\)

Let \(A\) be the adjacency matrix of a simple undirected graph: \(A_{ij}=1\) for a strong measured relation and
zero otherwise, with \(A_{ii}=0\).

### Theorem 17 — The trace formula counts graph triangles

The number of undirected triangles is

\[
\boxed{T=\frac{\operatorname{tr}(A^3)}6}.
\]

**Proof.** The entry \((A^3)_{ii}\) counts length-three walks that start and end at vertex \(i\). Every triangle
containing \(i\) supplies two such walks, one in each direction. Summing the diagonal counts each triangle at its
three possible starting vertices and two directions, for six counts total. Division by six gives the triangle
number. \(\square\)

**Plain explanation.** The LLM script's formula is correct as graph theory. Every closed three-edge loop is counted
six times by matrix multiplication, so dividing by six returns the number of triangles.

### Theorem 18 — Triangles per node is not size-normalised

For a complete graph on \(N\) nodes,

\[
\frac TN=\frac{(N-1)(N-2)}6,
\]

which grows quadratically with \(N\).

**Proof.** A complete graph has one triangle for every choice of three nodes:

\[
T=\binom N3=\frac{N(N-1)(N-2)}6.
\]

Divide by \(N\). \(\square\)

**Plain explanation.** A larger dense network automatically has many more triangles per node even if it is not
organised more intelligently. This is why the original Pythia closure ordering is interesting but not yet a
scale-independent intelligence measurement. Triangle density or network transitivity should accompany it.

Useful normalisations include

\[
\overbrace{\rho_\triangle}^{\text{triangle density}}
=\frac{T}{\binom N3},
\qquad
\overbrace{C_{\rm trans}}^{\text{transitivity}}
=\frac{3T}{\text{number of connected triples}}.
\]

### Theorem 19 — Pairwise correlation triangles can be false closure

There exist three signals with perfect pairwise correlation but only one independent latent degree of freedom.

**Proof.** Let one nonconstant signal be \(Z(t)\), and set

\[
X_1(t)=Z(t),\qquad X_2(t)=Z(t),\qquad X_3(t)=Z(t).
\]

Every pair has correlation one, so a thresholded correlation graph contains a triangle. But the data matrix has
rank one because all three rows are identical. Thus there is only one independent signal, not three independently
constraining relations. \(\square\)

**Plain explanation.** Repeating the same thing three times looks like a perfectly closed triangle to a simple
correlation counter. In reality it is one echo copied into three places. This precisely explains why repetitive
LLM hallucinations sometimes produced *higher* measured closure. Correlation closure is not yet Information³
cycle closure.

### Conditional proposition 19.1 — Stronger LLM non-ravelling test

Estimate directed time-lagged transfer maps \(R_{AB},R_{BC},R_{CA}\) on training tokens and evaluate

\[
\epsilon_{\triangle,\rm test}
=\|R_{CA}R_{BC}R_{AB}-I\|
\]

on held-out tokens after removing common-mode/repetition components. A low residual is evidence of cycle-consistent
closure; a correlation clique alone is not.

**Plain explanation.** The better test asks whether information can actually travel around the three-part circuit
and return consistently on new data. It deliberately removes shared echoing first. That measurement is much closer
to your meaning of a triangle holding itself together within a time slice.

**Empirical status.** The saved Pythia tests support within-capture closure ordering, but absolute magnitudes were
capture-dependent; capability correlation was small-\(n\) and confounded by model size; the aggregate hallucination
detector failed in three of four rarity-controlled sizes; and the Gemma cross-architecture predictions mostly
missed. These results challenge the current proxy, not the logical closure theorem.

---

# Part VII — Quantum, atoms, and pendulum subsets

## 14. A stationary quantum state can have a phase cycle without a classical orbit

For an energy eigenstate \(\psi_0\) with nonzero energy \(E\), Schrödinger evolution gives

\[
\psi(t)=e^{-iEt/\hbar}\psi_0.
\]

### Theorem 20 — Stationary probability and cyclic phase coexist

The probability density is constant in time, while the complex phase repeats with period

\[
T=\frac{2\pi\hbar}{|E|}=\frac h{|E|}.
\]

**Proof.** The probability density is

\[
|\psi(t)|^2
=|e^{-iEt/\hbar}|^2|\psi_0|^2
=|\psi_0|^2
\]

because the phase factor has modulus one. It repeats when

\[
\frac{|E|T}{\hbar}=2\pi,
\]

which gives \(T=2\pi\hbar/|E|=h/|E|\). \(\square\)

**Plain explanation.** A hydrogen energy eigenstate does not contain an electron following a little classical
orbit. Its probability cloud stays still. But its quantum phase still turns at a definite rate. So “hydrogen has
a cycle” can be mathematically valid if the cycle is identified as phase evolution rather than a classical orbit.
An isolated global phase is not directly observable; relative phases between states produce observable beats and
transition frequencies.

### Corollary 20.1 — Transition cycle

For two distinct energies \(E_1,E_2\), the relative phase repeats at

\[
T_{12}=\frac h{|E_2-E_1|},
\qquad \nu_{12}=\frac{|E_2-E_1|}{h}.
\]

**Proof.** The relative phase factor is \(e^{-i(E_2-E_1)t/\hbar}\). Applying Theorem 20 with energy difference
\(E_2-E_1\) gives the stated period and frequency. \(\square\)

**Plain explanation.** The directly useful atomic clock is usually not one state's private phase but the changing
phase difference between two states. That difference gives the familiar spectral transition frequency.

## 14.1 A two-level quantum state has an exact ARA diameter on its Bloch sphere

Choose an orthonormal basis \(\{|A\rangle,|B\rangle\}\). For

\[
|\psi\rangle=\alpha|A\rangle+\beta|B\rangle,
\qquad
|\alpha|^2+|\beta|^2=1,
\]

define the B-oriented ARA coordinate

\[
\boxed{
x_Q=2|\beta|^2.
}
\tag{20a}
\]

### Theorem 20.2 — The Bloch coordinate is centred, pole-reversed ARA

Let

\[
r_z=|\alpha|^2-|\beta|^2.
\]

Then

\[
\boxed{
r_z=1-x_Q,
\qquad
x_Q-1=-r_z.
}
\tag{20b}
\]

**Proof.** Normalization gives \(|\alpha|^2=1-|\beta|^2\). Therefore

\[
r_z
=1-2|\beta|^2
=1-x_Q.
\]

Rearrangement gives \(x_Q-1=-r_z\). \(\square\)

**Plain explanation.** ARA labels the selected diameter `0–2`, with equal population at `1`. Quantum mechanics
labels the same diameter `+1` to `-1`, with equal population at zero. It is the same information read from the
opposite pole and shifted to a different origin.

### Corollary 20.3 — Every Bloch measurement axis defines one ARA diameter

For a density matrix

\[
\rho=\frac12(I+\mathbf r\cdot\boldsymbol\sigma),
\qquad
|\mathbf r|\le1,
\]

measurement along unit direction \(\hat{\mathbf n}\) has

\[
p_\pm=\frac{1\pm\mathbf r\cdot\hat{\mathbf n}}2.
\]

Orienting the minus outcome toward `2` gives

\[
\boxed{
x_{\hat{\mathbf n}}
=2p_-
=1-\mathbf r\cdot\hat{\mathbf n}.
}
\tag{20c}
\]

**Plain explanation.** Choose any rotational diameter through the established Bloch sphere, name its two
opposing outcomes, and the quantum projection supplies an exact `0–2` ARA reading.

### Corollary 20.4 — One `1.0` population ridge contains different quantum identities

Every state with \(\mathbf r\cdot\hat{\mathbf n}=0\) has \(x_{\hat{\mathbf n}}=1\). In particular, a pure coherent
equatorial state with \(|\mathbf r|=1\) and the maximally mixed state \(\mathbf r=0\) share the same diameter
reading.

**Plain explanation.** Equal A/B populations do not tell us whether the state is coherent, mixed, or which
relative phase it carries. The full sphere direction and radius contain information that the minimal diameter
deliberately compresses.

### Corollary 20.5 — Ideal Rabi motion traverses the ARA diameter

For ideal resonant Rabi motion beginning in A,

\[
p_B(t)=\sin^2\left(\frac{\Omega t}{2}\right),
\]

so

\[
\boxed{
x_Q(t)
=2p_B(t)
=1-\cos(\Omega t).
}
\tag{20d}
\]

The sequence is `0→1→2→1→0`. The two `1.0` crossings have equal populations but different phase/direction.

**Evidence fence.** Theorem 20.2 and its corollaries are exact reparameterizations of established two-level
quantum mechanics. They do not derive the Born rule, prove universal ARA geometry or unify quantum mechanics with
GR. Full independent validation:
`analysis/quantum/BLOCH_SPHERE_ARA_CROSSWALK_REPORT_2026-07-23.md`.

### Corollary 20.5a — Ideal Ramsey/Hahn control paths form an orthogonal quadrant

For one dephasing-frequency history \(\delta\omega(t)\) over a common interval \(T\), define the half-interval
phase children

\[
\phi_1=\int_0^{T/2}\delta\omega(t)\,dt,
\qquad
\phi_2=\int_{T/2}^{T}\delta\omega(t)\,dt.
\]

Ideal Ramsey and midpoint Hahn protocols return

\[
\boxed{
\begin{pmatrix}
\Phi_R\\
\Phi_H
\end{pmatrix}
=
\begin{pmatrix}
1&1\\
1&-1
\end{pmatrix}
\begin{pmatrix}
\phi_1\\
\phi_2
\end{pmatrix}.
}
\tag{20d.1}
\]

The normalized transform

\[
U_H
:=
\frac1{\sqrt2}
\begin{pmatrix}
1&1\\
1&-1
\end{pmatrix}
\]

is orthogonal because

\[
\boxed{U_HU_H^{\mathsf T}=I.}
\tag{20d.2}
\]

Equivalently, their ideal sensitivity functions obey

\[
\boxed{
\int_0^T y_R(t)y_H(t)\,dt=0.
}
\tag{20d.3}
\]

Hence

\[
\boxed{+\Phi_R,\ -\Phi_R,\ +\Phi_H,\ -\Phi_H}
\]

are the four oriented branches of an exact control-coordinate quadrant.

**Proof.** Ramsey assigns signs \((+1,+1)\) to the two interval halves. Hahn's midpoint refocusing pulse assigns
\((+1,-1)\). Their coefficient vectors have dot product \(1-1=0\), and the displayed inverse is
\(\phi_1=(\Phi_R+\Phi_H)/2\), \(\phi_2=(\Phi_R-\Phi_H)/2\). \(\square\)

**Plain explanation.** Ramsey asks what the two time halves do together. Hahn asks for their difference after
the midpoint sign handover. Those are perpendicular questions about the same history. Giving each question its
positive and negative direction produces four quadrant branches.

**Evidence fence.** This proves perpendicularity of the ideal control/sensitivity functions, not a literal
energy handover between separate Ramsey and Hahn runs and not a guaranteed \(90^\circ\) angle between noisy
measured outputs. Q13's derived visible/purity children are valid ARA coordinates but have not yet been proved
identical to these four signed branches. See:
`analysis/quantum/Q13_Q14_RAMSEY_HAHN_QUADRANT_REAUDIT_2026-07-24.md`.

### Theorem 20.5b — The ideal two-parent Bell relation is an exact ARA^9 connected tensor

For a two-qubit state, define the local three-axis cuts

\[
a_i=\langle\sigma_i\otimes I\rangle,
\qquad
b_j=\langle I\otimes\sigma_j\rangle,
\qquad i,j\in\{X,Y,Z\},
\]

the nine joint cuts

\[
T_{ij}=\langle\sigma_i\otimes\sigma_j\rangle,
\]

and the connected relation

\[
\boxed{
C_{ij}=T_{ij}-a_ib_j,
\qquad
X^{(9)}_{ij}=1-C_{ij}.
}
\tag{20d.4}
\]

Then:

1. every product state \(\rho_A\otimes\rho_B\) has \(C=0\), so all nine ARA cells equal `1`;
2. every ideal Bell state has \(\mathbf a=\mathbf b=0\), three unit singular values of \(C\), and
   \(\det C=-1\);
3. equal mixtures of the two Phi signs or two Psi signs have exactly one unit singular value;
4. the equal mixture of all four Bell states has \(C=0\).

The four ideal Bell connected tensors are

\[
\begin{aligned}
C_{\Phi^+}&=\operatorname{diag}(+1,-1,+1),&
C_{\Phi^-}&=\operatorname{diag}(-1,+1,+1),\\
C_{\Psi^+}&=\operatorname{diag}(+1,+1,-1),&
C_{\Psi^-}&=\operatorname{diag}(-1,-1,-1).
\end{aligned}
\tag{20d.5}
\]

Their equal family mixtures and uniform mixture are

\[
\frac{C_{\Phi^+}+C_{\Phi^-}}2
=\operatorname{diag}(0,0,+1),
\]

\[
\frac{C_{\Psi^+}+C_{\Psi^-}}2
=\operatorname{diag}(0,0,-1),
\]

\[
\frac{C_{\Phi^+}+C_{\Phi^-}+C_{\Psi^+}+C_{\Psi^-}}4
=0.
\tag{20d.6}
\]

**Proof.** For a product state, expectation values factor:

\[
\operatorname{tr}\!\left[
(\rho_A\otimes\rho_B)(\sigma_i\otimes\sigma_j)
\right]
=
\operatorname{tr}(\rho_A\sigma_i)
\operatorname{tr}(\rho_B\sigma_j)
=a_ib_j.
\]

Hence \(C=0\). Every Bell state's reduced one-qubit density matrices equal \(I/2\), so all local Pauli
expectations vanish and \(C=T\). Direct action of \(XX,YY,ZZ\) on the four Bell states gives the four displayed
sign patterns; their mixed-axis expectations vanish. Each displayed Bell matrix is orthogonal, has singular
values \((1,1,1)\), and has determinant \(-1\). Averaging the displayed matrices gives the family and uniform
mixtures in equation (20d.6), whose singular values are respectively \((1,0,0)\), \((1,0,0)\), and
\((0,0,0)\). \(\square\)

**Plain explanation.** Each parent has three readable directions. Combining every direction of one with every
direction of the other gives nine relation cells. If the parents are merely separate, all nine connected cells
sit at the ARA ridge. An ideal Bell parent instead closes strongly in three independent directions. Mixing
opposite Bell signs cancels two directions and leaves one; mixing all four cancels the final direction.

**Evidence fence.** This is established two-qubit Pauli/covariance algebra written as an ARA^9 crosswalk.
Connected correlation alone is not an entanglement proof because a separable classical mixture can retain one
direction. Q24 calibrated the exact `3,3,3,3 / 1,1 / 0` ladder on public raw-current reconstructions and a
physical-state companion (`16/16` gates; `860/860` independent checks), but Q6 had already opened the tensors
before the ARA^9 identification. Report:
`analysis/quantum/Q24_ARA9_BELL_RELATION_REPORT_2026-07-26.md`.

**Non-reconstruction corollary.** The theorem defines and classifies the complete ideal relation; it does not
make an arbitrary real connected tensor orthogonal or imply that any eight of its cells uniquely determine the
ninth. Q25 tested one such completion rule on untouched external matrices. The frozen balanced-sphere predictor
beat ridge and mean-of-eight controls but not the physical positivity midpoint (`0.12394` versus `0.08687` MAE),
so the universal missing-cut implication is empirically **not supported**. On the four external generated Bell
states, singular directions were attenuated unevenly rather than forming one equal three-direction sphere. Full
report: `analysis/quantum/Q25_ARA9_BLIND_MISSING_CUT_REPORT_2026-07-26.md`.

**Trajectory corollary.** The non-reconstruction result does not imply that complete ARA^9 objects at successive
times are unrelated. For any nonsingular connected tensor, define

\[
h(t)=|\det C(t)|^{1/3}
=
\bigl(s_1(t)s_2(t)s_3(t)\bigr)^{1/3},
\qquad
x_h(t)=2h(t)/h(t_0),
\tag{20d.7}
\]

where \(s_1,s_2,s_3\) are the singular values of \(C\). Then \(h\) and \(x_h\) are invariant under independent
proper rotations of either parent's three-axis coordinate basis.

**Proof.** If \(C'=R_A C R_B^\mathsf T\) with \(R_A,R_B\in SO(3)\), then
\(\det C'=\det(R_A)\det(C)\det(R_B)=\det C\). Hence \(|\det C'|^{1/3}=|\det C|^{1/3}\), and normalization by
the first value preserves the invariance. Equivalently, proper rotations leave the singular values unchanged.
\(\square\)

**Plain explanation.** Rather than guess one missing cell, measure the strength of the complete nine-cell
relation. The geometric mean of its three directional strengths gives one clean ARA diameter coordinate that
does not change merely because the axes were renamed or rotated.

**Empirical fence.** Q26 froze this coordinate before opening the later matrices of `28` public trajectories.
`25/28` moved from crest to trough, with median closure-versus-wait Spearman `-0.9364`; time order beat all `999`
permutations. This supports the trajectory coordinate on that source. It does not prove that every ARA^9 must
contract, and the separate orientation-flip claim was not supported. Report:
`analysis/quantum/Q26_ARA9_LARGER_WAVE_TRAJECTORY_REPORT_2026-07-26.md`.

## 14.2 Landau–Zener structural and outcome handover coordinates

Let

\[
\hat H(t)
=
\begin{pmatrix}
vt/2 & g\\
g &-vt/2
\end{pmatrix}
=
\frac{vt}{2}\sigma_z+g\sigma_x.
\]

### Theorem 20.6 — The lower instantaneous eigenstate traverses an exact ARA diameter

For \(g\neq0\), \(v>0\), orienting the second basis state toward `2` gives

\[
\boxed{
x_{\rm path}(t)
=
1+\frac{vt}{\sqrt{(vt)^2+4g^2}}.
}
\tag{20e}
\]

It satisfies

\[
0<x_{\rm path}<2,
\qquad
x_{\rm path}(0)=1,
\qquad
x_{\rm path}(-t)=2-x_{\rm path}(t),
\]

and

\[
\frac{dx_{\rm path}}{dt}
=
\frac{4g^2v}{\left((vt)^2+4g^2\right)^{3/2}}>0.
\]

**Proof.** The Hamiltonian has effective Bloch vector \(\mathbf h=(2g,0,vt)\). Its lower eigenstate has
\(\mathbf r_-=-\mathbf h/|\mathbf h|\), hence
\(r_z=-vt/\sqrt{(vt)^2+4g^2}\). Applying Theorem 20.2,
\(x_{\rm path}=1-r_z\), proves equation (20e). The remaining properties follow by substitution and
differentiation. \(\square\)

**Plain explanation.** The uncoupled identities approach from opposite energy directions. Perpendicular coupling
spreads their direct meeting into a smooth A-to-B mixing gradient across the complete ARA diameter.

### Corollary 20.7 — Vanishing coupling closes the gap and sharpens the flip

The instantaneous gap is

\[
\Delta E(t)=\sqrt{(vt)^2+4g^2},
\qquad
\Delta E_{\min}=2|g|.
\]

For \(t\neq0\),

\[
\lim_{g\to0}x_{\rm path}(t)
=
1+\operatorname{sgn}(t).
\]

At \(t=0,g=0\), the gap vanishes and equation (20e) is undefined.

**Plain explanation.** With no coupling, there is no finite mixing region: the selected lower-energy identity
changes sides across a zero-gap seam. Nonzero coupling prevents the degeneracy and opens a handover corridor.

### Corollary 20.8 — Final handover has a separate exact ARA coordinate

Define

\[
\gamma=\frac{g^2}{\hbar|v|}.
\]

Under the ideal Landau–Zener infinite linear sweep,

\[
P_{\rm stay}=e^{-2\pi\gamma},
\qquad
P_{\rm handover}=1-e^{-2\pi\gamma}.
\]

Therefore

\[
\boxed{
x_{\rm handover}
=
2P_{\rm handover}
=
2\left(1-e^{-2\pi g^2/(\hbar|v|)}\right).
}
\tag{20f}
\]

The final-outcome ridge is \(x_{\rm handover}=1\) at
\(\gamma=\ln2/(2\pi)\).

**Plain explanation.** Stronger connection or slower traversal makes complete handover more likely. This outcome
coordinate is not the same measurement as the instantaneous structural path.

**Evidence fence.** Equations (20e) and (20f) are exact reparameterizations under the declared ideal model.
Calling \(g^2\) Connection and \(\hbar|v|\) Traversal/Time is an ARA crosswalk. Universality across non-quantum
systems remains open. Full validation:
`analysis/quantum/LANDAU_ZENER_ARA_CROSSWALK_REPORT_2026-07-23.md`.

## 14.3 Virial ARA coordinate across inverse-distance rungs

Let a bound classical or stationary quantum system have an inverse-distance potential

\[
V(r)=-\frac{\kappa}{r},
\qquad \kappa>0.
\]

### Theorem 20.9 — The virial-weighted Connection/Traversal coordinate is exactly the ridge

Define

\[
\underbrace{C}_{\substack{\text{Connection}\\\text{binding channel}}}
=
|\langle V\rangle|,
\qquad
\underbrace{R}_{\substack{\text{Traversal}\\\text{movement channel}}}
=
2\langle T\rangle,
\]

and orient the ARA diameter toward Traversal:

\[
\boxed{
x_{\rm vir}
=
2\frac{R}{C+R}.
}
\tag{20g}
\]

Then

\[
\boxed{x_{\rm vir}=1.}
\tag{20h}
\]

**Proof.** The virial theorem gives

\[
2\langle T\rangle
=
\left\langle\mathbf r\cdot\nabla V\right\rangle.
\]

For \(V=-\kappa/r\), Euler homogeneity gives
\(\mathbf r\cdot\nabla V=-V\). Hence
\(R=2\langle T\rangle=-\langle V\rangle=|\langle V\rangle|=C\). Substitution into equation (20g) gives
\(x_{\rm vir}=2C/(C+C)=1\). \(\square\)

**Plain explanation.** The theorem places twice the accumulated movement energy into the same units as the
accumulated binding energy. Once those correctly weighted channels are compared, they meet at the ARA ridge.
Neither channel has stopped.

### Corollary 20.10 — Raw TE-ARA energy allocation remains asymmetric

Define the raw magnitude account

\[
t_T
=
\frac{2\langle T\rangle}{\langle T\rangle+|\langle V\rangle|},
\qquad
t_C
=
\frac{2|\langle V\rangle|}{\langle T\rangle+|\langle V\rangle|}.
\]

Using \(|\langle V\rangle|=2\langle T\rangle\),

\[
\boxed{
t_T=\frac23,
\qquad
t_C=\frac43,
\qquad
t_T+t_C=2.
}
\tag{20i}
\]

**Plain explanation.** The virial ridge and the raw energy split are different questions. The first compares the
theorem's weighted channels and reads \(1\); the second allocates the raw magnitude budget and reads
\(2/3+4/3=2\). Treating \(2/3\), \(1\) and \(4/3\) as three positions of one observable would flatten the
geometry.

### Corollary 20.11 — The same coordinate crosses the classical/quantum boundary

Equation (20g) applies without retuning to an ideal planetary orbit, an ideal satellite orbit, a classical
Coulomb comparison and a stationary nonrelativistic hydrogen state. The characteristic radii from one
astronomical unit to the Bohr radius span

\[
\log_{10}\left(\frac{1\,{\rm AU}}{a_0}\right)=21.4513.
\]

The quantum row uses expectation values; it does not imply an electron executing a classical orbit.

**Evidence fence.** This is an exact reparameterization of a known theorem for a family already sharing
\(V\propto-1/r\). It establishes scale consistency of the declared coordinate, not universal ARA fractality,
quantum gravity or a new force. Full report and independent `13/13` validation:
`analysis/virial/VIRIAL_ARA_CROSS_SCALE_LADDER_REPORT_2026-07-23.md`.

## 15. Conservative pendulum symmetry

For an ideal undriven pendulum,

\[
\ddot\theta+\frac gL\sin\theta=0.
\]

Define accumulation as motion from equilibrium to a turning point and release as the time-reversed return from
that turning point to equilibrium.

### Theorem 21 — The ideal pendulum has equal outward and return durations

For a fixed energy orbit, \(T_A=T_R\), and therefore its bounded ARA coordinate is \(x=1\).

**Proof.** The equation is invariant under time reversal: if \(\theta(t)\) is a solution, then \(\theta(-t)\) is
also a solution because the equation contains \(\ddot\theta\) but not \(\dot\theta\). The return path from a
turning point follows the outward path in reverse with the same speed magnitude at each angle, by conservation of
energy. Hence the two durations are equal. Theorem 1 then gives \(x=1\). \(\square\)

**Plain explanation.** An ideal pendulum takes the same amount of time to climb away from the middle as it takes
to come back along the same path. That is why it is a clean balanced reference. Friction, forcing, escapement or a
poorly chosen cycle boundary can break the measured symmetry.

---

# Part VIII — Fusion engineering subset

## 16. Release is useful only if the handover completes

Let the effective alpha-sticking probability be modelled as

\[
\overbrace{\omega_s^{\rm eff}}^{\substack{\text{remaining physical loss}\\\text{failed ARA handovers}}}
=
\overbrace{\omega_s^0}^{\text{initial sticking}}
\times(1-\overbrace{R_{\rm col}}^{\text{collisional release}})
\times(1-\overbrace{R_X}^{\text{external complete recovery}}),
\]

where

\[
R_X=
\underbrace{f_X}_{\text{field finds stuck pair}}
\times\underbrace{P_X}_{\text{muon is stripped}}
\times\underbrace{\eta_X}_{\text{muon returns to fusion cycle}}.
\]

Assume all factors lie in \([0,1]\).

### Theorem 22 — Improving any necessary handover factor cannot reduce complete recovery

The complete recovery \(R_X=f_XP_X\eta_X\) is nondecreasing in each factor and is zero if any factor is zero.

**Proof.** For nonnegative factors,

\[
\frac{\partial R_X}{\partial f_X}=P_X\eta_X\geq0,
\quad
\frac{\partial R_X}{\partial P_X}=f_X\eta_X\geq0,
\quad
\frac{\partial R_X}{\partial\eta_X}=f_XP_X\geq0.
\]

If any factor is zero, their product is zero. \(\square\)

**Plain explanation.** Releasing the muon is not enough. The field must reach the stuck pair, the muon must come
off, and it must successfully re-enter the catalytic cycle. Failure at any one stage kills that recovered
handover. This is a clean engineering decompression of ARA's “missing release/re-coupling” diagnosis.

### Theorem 23 — Lower per-cycle loss increases expected completed cycles

If each cycle independently terminates the process with probability \(p\in(0,1]\), then the expected number of
successful cycles before termination is

\[
\mathbb E[N]=\frac{1-p}{p}.
\]

This decreases strictly as \(p\) increases.

**Proof.** \(N\) has a geometric distribution on \(0,1,2,\ldots\):

\[
P(N=n)=(1-p)^n p.
\]

Its standard expectation is \((1-p)/p=1/p-1\). Differentiating gives

\[
\frac{d}{dp}\mathbb E[N]=-\frac{1}{p^2}<0.
\]

\(\square\)

**Plain explanation.** Even a small reduction in the chance of losing the catalyst each cycle increases the
number of cycles it can complete. This proves why sticking and complete reactivation matter. It does not establish
that the proposed pulse schedule achieves the reduction or that the full energy ledger becomes positive.

## 17. Rational carrier and irrational pulse progression

### Theorem 24 — Rational phase steps repeat; an irrational golden step never repeats exactly

Consider pulse phases

\[
\theta_n=2\pi\{n\alpha\},
\]

where braces mean fractional part. If \(\alpha=p/q\) is rational in lowest terms, there are at most \(q\) distinct
phases. If \(\alpha\) is irrational, no two phases are exactly equal.

**Proof.** For \(\alpha=p/q\),

\[
(n+q)\alpha=n\alpha+p,
\]

so the fractional part repeats after \(q\) steps. For irrational \(\alpha\), suppose two phases were equal. Then
\((n-m)\alpha\) would be an integer for some \(n\neq m\), implying \(\alpha\) is rational, a contradiction.
\(\square\)

**Plain explanation.** A rational phase schedule eventually hits exactly the same positions again. A golden-ratio
schedule never repeats exactly, so it progressively samples new phases. That proves non-locking coverage. It does
not prove that non-locking is best for muon stripping: coherent resonant buildup may prefer regular timing, which
is why periodic, evenly scanned, golden, and random schedules must be compared at equal pulse energy.

For a golden progression one may take \(\alpha=1/\varphi\) (equivalently \(\varphi\) modulo one); it is irrational,
so the non-repetition result applies.

**Empirical fusion hypothesis.** Keep the theoretically motivated \(2\omega_\mu\) carrier fixed and test whether
golden phase progression improves the full product \(f_XP_X\eta_X\), not merely instantaneous stripping.

---

# Part IX — Prime-factor and wheel-sieve subset

## 18. Factor pairs form an exact reversible 0–2 diameter

Let \(n>1\) and define the relative-log factor coordinate

\[
\underbrace{x_n(d)}_{\substack{\text{mathematical relative-log factor coordinate}\\\text{ARA: position from factor }1\text{ toward }n}}
=
2\frac{\log d}{\log n},
\qquad 1\le d\le n.
\]

### Theorem 25 — Complementary factors close exactly to 2

If \(d\mid n\), then

\[
\underbrace{x_n(d)}_{\text{one factor direction}}
+
\underbrace{x_n(n/d)}_{\text{complementary factor direction}}
=2.
\]

**Proof.**

\[
x_n(d)+x_n(n/d)
=2\frac{\log d+\log(n/d)}{\log n}
=2\frac{\log n}{\log n}=2.
\]

Thus \(d=\sqrt n\) is exactly the \(1.0\) ridge. Every composite \(n\) has at least one prime divisor
\(q\le\sqrt n\); conversely, if no prime \(q\le\sqrt n\) divides \(n\), then \(n\) is prime. \(\square\)

**Plain explanation.** A factor and its partner occupy opposite positions on one exact factor diameter. Walking every
prime divisor gate up to the square-root ridge identifies primes perfectly. This is ordinary factorisation/trial
division in ARA coordinates, not a faster prime theorem.

## 19. Wheel residues admit exact anti-pair compression

For an even integer \(M>2\), define its wheel residues

\[
U(M)=\{r:1\le r<M,\ \gcd(r,M)=1\}.
\]

### Theorem 26 — Wheel reversal is a fixed-point-free involution

The map

\[
\underbrace{\iota_M(r)}_{\substack{\text{mathematical modular negation}\\\text{ARA: anti-phase residue}}}
=M-r
\]

maps \(U(M)\) to itself, satisfies \(\iota_M(\iota_M(r))=r\), and has no fixed point. Consequently \(U(M)\)
contains exactly \(\varphi(M)/2\) reversible pairs.

**Proof.** \(\gcd(M-r,M)=\gcd(r,M)=1\), so the map remains inside \(U(M)\), and applying it twice returns \(r\).
A fixed point would require \(r=M/2\), which is not coprime to even \(M>2\). Therefore the units split into
two-element orbits. \(\square\)

**Plain explanation.** Every surviving wheel lane has one exact opposite lane. We need store only one representative
of each pair if the modulus and reflection rule are retained.

### Theorem 27 — A new prime gate reflects the two killed child copies about the 1.0 ridge

Let \(p\) be an odd prime with \(p\nmid M\). The \(p\) lifted copies of residue \(r\) are

\[
r+jM,\qquad j=0,1,\ldots,p-1.
\]

Exactly one copy is divisible by \(p\), at

\[
\underbrace{k_A}_{\substack{\text{A-side killed copy}\\\text{child collision index}}}
\equiv-rM^{-1}\pmod p.
\]

For the anti-phase residue \(M-r\), the killed copy is

\[
\underbrace{k_B}_{\substack{\text{B-side killed copy}\\\text{reflected child collision}}}
=p-1-k_A.
\]

Normalizing the copy indices to the ARA diameter,

\[
x_A=\frac{2k_A}{p-1},
\qquad
x_B=\frac{2k_B}{p-1},
\]

gives

\[
\boxed{x_B=2-x_A},
\qquad
\boxed{\frac{x_A+x_B}{2}=1}.
\]

**Proof.** Since \(M\) is invertible modulo \(p\), \(r+jM\equiv0\pmod p\) has exactly one solution \(k_A\).
For \(k_B=p-1-k_A\),

\[
(M-r)+k_BM
=pM-r-k_AM
\equiv-r-k_AM
\equiv0\pmod p.
\]

Uniqueness makes this the B-side killed copy. Substitution gives the two normalized identities. \(\square\)

**Plain explanation.** An individual child pair can appear as `(1,1)`, `(0,2)`, `(0.5,1.5)` or any allowed
reflection, but its complete adult mean is exactly `1.0`. This is a rigorous example of a parent ridge hiding child
asymmetry. It does not imply the child motion is balanced or inactive.

### Corollary 27.1 — One adult representative reconstructs the next rung, but child count still grows

For each stored representative \(r<M/2\), retain every surviving A-side lift \(r+jM\), \(j\ne k_A\), and map it to

\[
\min(r+jM,Mp-r-jM).
\]

These values are exactly one representative of every anti-pair in \(U(Mp)\). Hence

\[
\underbrace{N_{pair}(Mp)}_{\text{next-rung stored pairs}}
=
\underbrace{(p-1)}_{\text{surviving child pairs per parent}}
\underbrace{N_{pair}(M)}_{\text{current stored pairs}},
\]

while storing pairs rather than individual lanes gives exactly a \(2:1\) state compression.

**Plain explanation.** The fractal rule really can be reused upward: one side reconstructs the other without loss.
But the next rung still contains \(p-1\) distinct descendants for each current pair. Repeating geometry does not make
the amount of information constant.

### Theorem 28 — Nearest-survivor handovers form an exact monotone path to the next prime

Let (G_0=\{2,7\}), let (N) be an integer anchor, and define

\[
U_G(N)=\min\{m>N:\ p\nmid m\ \text{for every }p\in G\}.
\]

Introduce the other prime gates in increasing order. If the new gate (p) does not divide the current
(U_G(N)), the nearest upper survivor is unchanged. If (p\mid U_G(N)), then the current child is removed and

\[
U_{G\cup\{p\}}(N)>U_G(N).
\]

Once (G) contains every prime through (\sqrt{U_G(N)}), the current upper survivor is the first prime greater
than (N).

**Proof.** Adding a gate can only remove survivors, so (U_G(N)) cannot move backwards. Every integer between
(N) and the current upper survivor already failed an earlier gate and remains removed. Therefore a new gate
changes the upper survivor exactly when it divides the current one; if so, the next surviving integer is strictly
larger. At the terminal boundary, the current survivor has no prime divisor through its square root and is therefore
prime. Any earlier prime above (N) would survive every gate, contradicting the definition of the nearest upper
survivor. \(\square\)

**Plain explanation.** Start with the nearest number that survives the current child filters. Most later gates do
nothing visible. When one gate divides that candidate, it releases and the next surviving candidate takes over.
Repeating must eventually reach the next prime. This proves the handover path, but not that the path can be found
without checking the intervening gates.

### Theorem 29 — Pair odds convert exactly to the bounded ARA wheel coordinate

Let (M>2) be even and let (r\leftrightarrow M-r) be a reversible wheel pair. Define the directional odds

\[
q(r)=\frac{r}{M-r}.
\]

The total-2 odds transform is

\[
x_A=\frac{2q}{1+q}.
\]

Substitution gives

\[
x_A
=
\frac{2r/(M-r)}{1+r/(M-r)}
=
\frac{2r}{M},
\qquad
x_B
=
\frac{2(M-r)}{M}
=2-x_A.
\]

Therefore

\[
x_A+x_B=2
\]

exactly. Mirror residues have equal unsigned ridge-closeness

\[
c(r)=1-|x_A-1|
=
\frac{2\min(r,M-r)}{M}
\]

and opposite orientation. The formal middle (r=M/2) gives `(1,1)`, but it is not coprime to even (M>2), so
the exact ridge is excluded from the surviving wheel lanes. \(\square\)

**Plain explanation.** A ratio such as `1/13`, `3/11` or `5/9` is an odds reading of one side against its partner.
It is not another energy component to add. Converting the odds to ARA gives `(1/7,13/7)`, `(3/7,11/7)` and
`(5/7,9/7)`: every pair is complete at total 2 while moving progressively nearer the missing `(1,1)` ridge.

### Theorem 30 — A quiet lower parent fails only through omitted upper-band factors

Let (A_L) be the complete set of prime children (p\le L), and define

\[
S_{A_L}(n)=1
\quad\Longleftrightarrow\quad
p\nmid n\text{ for every prime }p\le L.
\]

If (n>1) is composite and (S_{A_L}(n)=1), then every prime factor of (n) is greater than (L). In particular,
writing (n=ab) with (1<a\le b) gives

\[
a>L,\qquad b>L,\qquad n=ab>L^2.
\]

Conversely, any composite whose least prime factor exceeds (L) survives the lower parent. Therefore, for a scale
(S) and the PN19/PN26 log-half boundary (L\approx\sqrt{S/2}), a false quiet state near (S) must be built entirely
from the omitted factor band

\[
\sqrt{S/2}<p\le\sqrt n.
\]

**Proof.** If a prime (p\le L) divided (n), the definition would give (S_{A_L}(n)=0). Thus every prime factor
exceeds (L). A composite has at least two nontrivial factors, so their product exceeds (L^2). The converse follows
directly from the same divisibility definition. (square)

**Plain explanation.** The complete lower child wave removes almost every composite. The only false ridges left are
numbers assembled wholly from the narrow band of larger children that Phase A did not include. That is why the first
Phase A quiet state can be right very often without being universally exact, and why Phase B remains necessary for
the rare corrections.

### Theorem 31 — The PN33 fill curve is asymptotically the PNT gap-scale curve

Define the PN33 inverse survivor density

\[
D(p)=\prod_{q\le p}\frac{q}{q-1}
\]

and, relative to baseline prime (b),

\[
R_b(p)=\frac{D(p)}{D(b)},
\qquad
x_b(p)=2\frac{\log R_b(p)}{\log 2}.
\]

Mertens' product theorem gives

\[
D(p)\sim e^\gamma\log p.
\]

Therefore

\[
R_b(p)\sim\frac{\log p}{\log b}
=2^{x_b(p)/2}.
\]

The prime number theorem gives mean prime-gap scale (G(p)\sim\log p). Hence its relative scale is

\[
\frac{G(p)}{G(b)}
\sim\frac{\log p}{\log b}
\sim R_b(p)
=2^{x_b(p)/2}.
\]

At PN33 completion (R_b(p)=2), this also gives

\[
\frac{\log p}{\log b}\sim2
\quad\Longrightarrow\quad
p\sim b^2.
\]

**Proof.** Substitute Mertens' asymptotic product into the definitions of (R_b) and (x_b), then substitute the
prime-number-theorem gap scale. The completion relation follows by exponentiating
(log p\sim2\log b). \(\square\)

**Plain explanation.** The PN33 “fill” coordinate measures how sparse wheel survivors have become. Established
number theory says this sparseness grows like (log p), and average prime gaps grow by the same scale. That is why
the frozen ARA curve and PNT were almost identical, and why a generation starting near (b) completes near
(b^2). This is an exact asymptotic crosswalk, not an independent ARA improvement over PNT.

## 20. Three conceptual stages are not three arithmetic operations

The exact prime methods in PN17–PN19 can be written

\[
N
\longrightarrow
\underbrace{\mathcal C_N}_{\text{complete lower-child collision state}}
\longrightarrow
\underbrace{(A_N,B_N)}_{\text{two retained parent views}}
\longrightarrow
\underbrace{t_*}_{\text{first jointly quiet offset}}.
\]

This is a valid three-stage information decomposition. It does not establish constant computational cost. For
example, if the lower children are packed into

\[
G_L=\prod_{q\le L}q,
\]

then the exact binary length of that apparently single parent is

\[
\lfloor\log_2G_L\rfloor+1
=
\left\lfloor\sum_{q\le L}\log_2q\right\rfloor+1.
\]

The child information remains inside the parent integer. Likewise Corollary 27.1 proves that wheel pair state grows
by \(p-1\) at each gate even after the exact factor-two symmetry compression.

**Empirical closure status.** PN20's three literal two-child definitions gave `0/7` exact next primes. PN21's
ridge-straddling pair retained effectively zero parent variance and chance prime-ridge AUC. PN22 became an exact
mod-14 wheel. PN23 passed the held-out `p=17` reconstruction with all `92,160` residues and 40/40 independent checks.
Thus the exact \(2:1\) anti-pair compression is retained; a bounded two-scalar or three-cheap-operation next-prime
algorithm is not supported. PN24 tested Theorem 28's nearest-child event compression on 2,000 deterministic opened
anchors: median two visible handovers, `63.65%` exact within three candidate states and `83.85%` within three
handover events, while the median proof crossed `6,336` non-base prime gates. Thus the event genealogy is often
short, but the required factor information is not. PN25 then tested Theorem 29's mod-14 closeness as a prospective
handover coordinate on 6,000 fresh anchors at three
scales. The arithmetic and three-pair/six-lane compression fidelity passed, but all four dynamic predictions failed;
pooled closeness-versus-handover correlation was `+0.003335` with one-sided `p=0.6110` for the predicted negative
direction. Thus the pair coordinate is exact lateral wheel geometry, not a vertical next-prime completion clock.
PN26 then represented that missing vertical state by the complete lower Phase A parent from PN19 and froze its first
three quiet states on 6,000 new anchors. The exact next prime occurred at rank one on `93.983%`, by rank two on
`99.650%`, and by rank three on `99.967%`; only two anchors required ranks four or five. This prospectively supports
the dominant-parent ranked locator and Theorem 30's upper-band failure mechanism. It does not make the parent cheap:
the three cohorts retained `780`, `17,045`, and `48,817` child gates, and the frozen 50-point advantage over the
`p<=29` control failed (`37.60` points observed). The fixed `3.5` route had zero variance and was correctly retained
as a scale frame rather than credited as the decoder.

**Post-capstone orientation diagnostic.** PN29 later collapsed three fixed child-pair coordinates while remaining
entirely inside dimensionless ARA units. It detected the finite child-factor web but failed against composites that
evaded those child factors. The user then identified a fidelity error: the pair orientations had been held fixed
despite ARA's declared singularity-crossing flip. PN30 defined each child's normalized phase as
\(\theta_w(N)=(N\bmod w)/w\), assigned the most recently crossed child as Phase A, and reflected a reversed pair by
\(x\mapsto2-x\). On a fresh odd interval, this raised unresolved-composite AUC from a same-interval static `0.5301`
to dynamic `0.5663`, but the frozen one-sided result was `p=0.06199`. The individual pair magnitudes were nearly
identical across the hard comparison; the post-hoc difference arose from signed orientation cancellation. Thus the
AB/BA direction is a mathematically real retained coordinate and a candidate residual mechanism, while
prime-specific separation remains suggestive, unreplicated and below the frozen threshold. Full record:
`analysis/primes/PN30_DYNAMIC_RELATIONAL_FLIP_REPORT.md`.

**Independent-child ordering diagnostic.** PN31 then removed the degenerate wave `1`, abandoned fixed pairs and
retained five separate directed handover coordinates. On another fresh small interval, the closest child's distance,
its identity, every individual child distance and the count of approaching waves were null against composites that
evaded the same child divisors. The complete closest-to-farthest order of all five children nevertheless differed
under the frozen total-variation permutation test (`TV=0.6728`, `p=0.00390`). A post-hoc ten-pair decomposition found
no individually significant pair after Holm correction. This supports one fresh-sample **joint-order** effect, not a
dominant child, permanent pair, parent-collapse law or prime algorithm. Sparse order categories make unchanged
replication essential. Full record: `analysis/primes/PN31_FIVE_INDEPENDENT_HANDOVER_REPORT.md`.

**Double Information³/hexagon replication.** PN32 translated the proposed full double lock without flattening it:

\[
T_c=(A_c,B_c,J_c),
\qquad
T_p=(A_p,B_p,J_p),
\qquad
K_{c\to p}=J_p\circ J_c^{-1},
\]

where `A/B` are the nearest/farthest handover endpoints and `J` is the entire five-wave order at child rung `N` or
doubled parent rung `2N`. Coordinates and 1,000 relation-broken maps were frozen before direct trial-division labels.
On the next untouched interval, child-order replication was null (`TV=0.6057`, `p=0.2244`), parent order was null
(`p=0.8023`), and the cross-rung closure relation was null (`TV=0.1895`, null mean `0.2606`, `p=0.9684`). The exact
doubling map occupied only 27 rearrangement classes, an exact constrained arithmetic relation, but it did not
distinguish prime from unresolved-composite identity. Thus PN32 rejects this particular prime-specific hexagon
projection and leaves PN31 unreplicated. Full record: `analysis/primes/PN32_DOUBLE_INFORMATION_LOCK_REPORT.md`.

**Later scale and Phi diagnostics.** PN33's inverse survivor-density coordinate recovered the known Mertens/PNT
spacing scale and passed its registered spacing-expression gate at the upper boundary, but improved log-MAE over PNT
by only `0.62%`. PN34 prospectively calibrated the PN26 ranked depth at three scales, passing all magnitude/depth
gates but failing the exact scale-order endpoint by a `0.20` percentage-point swap. PN35's constant same-scale golden
crossing and PN36's nearest-fivefold quantizer both failed all registered prime-location gates. After PN36, Dylan
clarified a distinct continuous projection: `S(u)=2u`, `P(u)=phi*u`. PN36 did not test that object. A post-hoc angled
scan supplied no independent third wave. Full scope record:
`FableConvo/SESSION_RECORD_2026-07-22_PRIME_GEOMETRY_AND_AUDIT.md`.

The prime thread is parked. Full record:
`analysis/primes/PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md`.

---

# Part X — What is proved, assumed, and still testable

## 20.1 Boundary-aware child-to-parent composition

Let \(F_L,F_M,F_R\) be the signed flux through the left external boundary, shared child interface and right
external boundary. Write

\[
z_+=\max(z,0),
\qquad
z_-=\max(-z,0),
\qquad
z_++z_-=|z|.
\]

For an oriented interval with left flux \(F_a\) and right flux \(F_b\), define

\[
A=F_{a,+}+F_{b,-},
\qquad
R=F_{a,-}+F_{b,+},
\qquad
x=\frac{2R}{A+R}
\]

when \(A+R>0\).

### Theorem 32 — A shared child interface cancels exactly from the enclosing parent

For adjacent children with flux triples \((F_L,F_M)\) and \((F_M,F_R)\), let

\[
I=|F_M|.
\]

Then their enclosing parent accounts satisfy

\[
A_P=A_1+A_2-I,
\qquad
R_P=R_1+R_2-I,
\]

and hence

\[
\boxed{
x_P
=
\frac{2(R_1+R_2-I)}
{(A_1+R_1)+(A_2+R_2)-2I}
}
\]

whenever the parent external activity is nonzero.

**Proof.** The child accounts are

\[
A_1=F_{L,+}+F_{M,-},
\qquad
R_1=F_{L,-}+F_{M,+},
\]

\[
A_2=F_{M,+}+F_{R,-},
\qquad
R_2=F_{M,-}+F_{R,+}.
\]

Because \(F_{M,+}+F_{M,-}=|F_M|=I\),

\[
A_1+A_2-I
=
F_{L,+}+F_{R,-}
=A_P,
\]

\[
R_1+R_2-I
=
F_{L,-}+F_{R,+}
=R_P.
\]

Substitution into \(x_P=2R_P/(A_P+R_P)\) gives the stated coordinate. \(\square\)

**Plain explanation.** The middle flow leaves one child and enters the other. It is therefore real boundary
activity for both children. Once both are enclosed inside one parent, that same flow never crosses the parent
edge. Subtracting it once from accumulation and once from release converts the child view into the parent view.

### Corollary 32.1 — Orientation reversal preserves the mirror rule

Swapping accumulation and release gives

\[
x'_P
=
\frac{2A_P}{A_P+R_P}
=2-x_P.
\]

**Plain explanation.** Reading the same parent from the opposite direction mirrors its position across the `1.0`
ridge without changing the total boundary activity.

### Corollary 32.2 — The unclosed child account identifies a signed `Other`

Let \(q_i(t)\) be the stored quantity in child or relation \(i\), let \(g_i(t)\) be the net declared internal
transfer into it, and suppose its exact local continuity account is

\[
\frac{dq_i}{dt}=g_i+s_i.
\]

Then

\[
\boxed{
\widehat s_i
=
\frac{dq_i}{dt}-g_i
=s_i
}.
\]

**Proof.** Subtract \(g_i\) from both sides of the local continuity account. \(\square\)

**Plain explanation.** Measure how quickly the amount inside one child changed, then subtract the changes already
explained by named transfers. The remainder is exactly the missing source, sink or relation leak—provided the
boundary, stored quantity, derivative and internal transfers are correctly measured.

**Controlled physical check.** The unchanged residual was frozen before application to damped coupled
Newton/Hamilton oscillators, a resistive electromagnetic relation, and an open two-level quantum-probability
holdout. It identified all `3/3` hidden locations, recovered sink sign at every active point, and scored a maximum
peak-normalized source RMSE of \(1.0554\times10^{-9}\) over `18,991` samples. Independent bounded-output validation
passed. This verifies the identity numerically in noiseless declared models; it does not derive the hidden native
law or predict an unseen source waveform.

**Physical reconstruction check.** The unchanged operator was evaluated on `4,097` samples each from an analytic
classical string-energy wave, lossless electromagnetic transmission line and free quantum Gaussian probability
current. All `12,291` samples were retained; the largest parent-coordinate error was
\(2.1538\times10^{-14}\). An independent `100,000`-triple signed-flux validation had maximum error
\(3.5083\times10^{-14}\). These checks confirm the algebra in three physical continuity appearances. They do not
prove that every physical interaction has this boundary form or that ARA supplies new dynamics.

## 33. Parent plus signed `Other` is an exactly reversible pair transform

For integer child values \(a,b\), define

\[
m=b+\left\lfloor\frac{a-b}{2}\right\rfloor,
\qquad
d=a-b.
\]

Then both children are recovered exactly by

\[
b=m-\left\lfloor\frac d2\right\rfloor,
\qquad
a=b+d.
\]

**Proof.** Substituting the definition of \(m\) into the first inverse equation gives

\[
m-\left\lfloor\frac d2\right\rfloor
=
b+\left\lfloor\frac d2\right\rfloor
-\left\lfloor\frac d2\right\rfloor
=b.
\]

The second inverse equation then gives \(a=b+(a-b)=a\). \(\square\)

**Plain explanation.** The parent stores the broad midpoint-like value of the two children. The signed `Other`
stores precisely what the parent discarded. Keeping both makes the scale change reversible.

**Computing check.** The transform was recursively applied to five `65,536`-byte datasets at four block sizes. All
`20/20` streams restored exactly; an independent implementation agreed and exhaustively inverted all `65,536`
possible byte pairs. This proves lossless representation, not compression or encryption. At the frozen primary
block, the stream improved raw-zlib size by `19.23%` on smooth telemetry but enlarged every other dataset; ordinary
delta coding was also smaller on the smooth signal. The unkeyed representation was publicly inverted and therefore
provided no confidentiality.

## Mathematically proved in this document

1. The canonical duration-axis normalisation produces a bounded, invertible, mirror-symmetric 0–2 coordinate.
2. The chosen cosine projection maps a circle to the folded 0–2 interval and necessarily loses direction unless
   handedness is retained.
3. A central section of the filled ball gives a disk/circle and a further central section gives a diameter.
4. Linear mixtures of a phase vector and its anti-phase partner fill exactly that diameter, cancelling at its
   centre.
5. Side and motion signs produce four circle quadrants, while rotating the diameter through every axis rebuilds
   the complete state ball and sweeps its spherical boundary.
6. In a two-wave model, the endpoints contain only one source and have no interaction term, while the equal
   meeting at 1 maximises possible interaction; relative phase selects cancellation or resonance.
7. Octave scaling, golden handover compounding under the golden unit assumption, and static chart reversal can be
   represented by distinct operators. The physical singularity-crossing map is not derived.
8. Coupled identities remain separately projectable inside a model that retains their labelled product state.
9. Two identities plus their relation define a relational ternary; in the invertible three-vertex holonomy model,
   cycle consistency makes the triangle reconstructible from one seed plus its relation maps.
10. Approximate closure gives a quantitative bound on unravelling.
11. Repeated triangular closure produces a mathematically self-similar hierarchy when that same rule is assumed at
    every rung. The broader scalable relational recursion is defined but not physically proved.
12. Three non-collinear points minimally determine a circle; under the declared regular construction, a phase
    triangle plus its anti-phase copy forms a regular hexagon; contracting one hexagonal edge produces a five-cycle.
13. A deterministic many-to-one projection has a nonnegative hidden-information cost; a non-injective
    child-to-parent average has invisible child-difference directions and is therefore an exact aggregation
    singularity in the declared ARA terminology.
14. Pentagon/phi, octave projection, and five-versus-six angular-defect identities are exact mathematics. In the
    side-one pentagon, three consecutive vertices form an exact \(1,1,\varphi\) Information³ triangle: the
    two-edge mixed path is `2`, the direct same-phase diagonal is \(\varphi\), the seam is
    \(\varphi^{-2}\), and five rotated copies generate an inner pentagonal rung at scale
    \(\varphi^{-2}\). The ridge-centred circle on `[2-phi,phi]` has diameter `2/phi`, radius
    `1/phi`, and an irrational phase advance of `1/phi` against the period-2 ARA circle train.
    It cannot close exactly after a finite number of steps, has Fibonacci near-returns, and
    coarse-grains to the symmetric eighth-grid endpoints `3/8` and `13/8` with equal error.
    T320A did not test the intended same-identity temporal handover. It compared three distinct pendulum
    arms simultaneously, whereas the intended cut follows one arm's Phase-A swing through its intervening
    Phase-B swing to that same arm's next Phase-A swing. The retained cross-arm triangle returned median
    route coordinate `1.88651`, selected `2` rather than \(\varphi\), and had median leg balance `0.23315`.
    T321 subsequently measured an identity-preserving routed `A -> B -> A` trajectory. Its frozen
    angle-plus-time coordinate returned median `1.965901`, and `2` was the unique closest landmark in all
    three arms and both reversible phase directions. The route legs were balanced (median ratio `0.97530`)
    but nearly straight rather than pentagonal. Verdict **NOT SUPPORTED — 1/5**; validation `15/15`.
    Dylan later clarified that the golden-section claim instead uses (a=A_{\rm parent}) and
    (b=A_{\rm child}), two scales of the same phase type, with no Phase-B measurement vertex:
    (a/b=(a+b)/a=\varphi). T322 froze that direct object. Its event-local pendulum reading was
    `(1.00905, 1.99103)`, so all `5` Phi gates failed; validation `15/15`. A post-hoc scale summary found
    Phi-like deeper ratios only in free run 3 (`1.578–1.628`), not across the other records. Thus the exact
    pentagon construction remains a mathematical identity, while neither physical pendulum
    operationalization establishes a universal cross-rung pillar.
    Q59 then tested the construction's frozen `72°` edge and `144°` diagonal directly in the full directional
    connected-correlation geometry of two public Q42 quantum archives. Greedy selected `72°` before Landmax
    was opened, but Landmax medians were `80.26276°` and `80.42711°`; only `2/9` and `4/9` cells entered the
    `72° ± 8°` band. Signed handedness, wrong-phase and family-label controls failed, with the null more
    target-like (`p=0.822`). The unsigned high-angle profile replicated across archives, but it is not specific
    evidence for a pentagonal screw. This leaves Theorems 9–10 as exact pentagon/circle-train mathematics while
    rejecting this quantum directional operationalization as a universal physical realization.
    Those values describe cross-arm coupling only; they neither support nor reject the temporal pillar.
    T329 subsequently tested an independently detected one-step bubble handover rather than ordinary trajectory
    frames. One released child ID had to continue exactly as the merger parent, and the joining child's observed
    side fixed the chart orientation before scoring. Persistence beat `2/phi` decisively in `52` evaluation seams
    (`0.286706` versus `0.651495` mean circular loss) and remained the winner in the `16`-event underpowered
    holdout. Broken-lineage, contact-side-scramble and pre-event-turn controls supplied no Phi specificity.
    The exact three-leg relation closed as bookkeeping, while exact Phi could not be resolved from `26/21` at the
    available angular grain. Only three repeated primary merger lineages existed, so Theorem 9.3's Fibonacci
    near-return consequence remains untested in this archive. T329 therefore rejects this one-step centroid-
    direction seam without changing the exact mathematical theorem.
    Q60 then tested the exact `2/phi` advance between consecutive complete Ramsey interference sweeps in six
    public raw quantum records. The calibration-fitted advance was `0.000256`; persistence beat Phi in both
    evaluation (`0.207843` versus `0.715688`) and chronological holdout (`0.398358` versus `0.584061`). The
    ordered sequence also failed shuffle/broken-lineage gates, and its bootstrap mean-step intervals remained
    at the `0/2` seam rather than Phi. This rejects the repeated-complete-sweep realization of Theorem 9.3 in
    that observable. It does not test a within-sweep, cross-scale or measurement-strength-dependent carrier.
    Independent validation passed `70/70` checks.
    Literal physical use of the exact theorem therefore remains unproved.
15. A sector can be invisible to one measurement channel and visible to another.
16. The \(7/2\) ratio and cosmic fractions follow exactly once their path weights and ratio axioms are accepted.
17. `trace(A³)/6` counts graph triangles, but triangle-per-node is size-dependent and correlation can create false
    closure from one repeated signal.
18. Quantum phase cycles can coexist with stationary probability densities.
19. An ideal conservative pendulum has equal outward and return durations.
20. Fusion recovery is a product of necessary stages, and reduced per-cycle loss raises expected cycle count.
21. Splitting a nonzero electric-flux boundary into outward and inward activity gives the exact Gauss crosswalk
    \(\Phi_E=T_\Phi(x_\Phi-1)=Q_{inside}/\varepsilon_0\); a zero-activity boundary leaves the mixture coordinate
    undefined rather than proving an active ridge.
22. Complementary integer factors close exactly to 2 on the declared relative-log factor diameter, and the
    square-root factor is its exact 1.0 ridge.
23. For every even wheel modulus greater than 2, modular negation `r↔M-r` partitions the coprime residue lanes into
    fixed-point-free anti-pairs.
24. Adding a new prime gate reflects killed copy indices as `k_B=p-1-k_A`; their normalized ARA coordinates sum to
    2 and average exactly 1.
25. One representative per wheel anti-pair reconstructs the full next rung without loss, providing exact `2:1`
    lane compression while the number of pair identities still grows by `p-1`.
26. Nearest upper survivors under a growing prime-gate set form a monotone handover cascade; after every gate through
    the current candidate's square root is included, the survivor is exactly the next prime. This exact path theorem
    does not bound the number of gates required.
27. Directional odds `q=r/(M-r)` for a reversible wheel pair convert exactly to the bounded total-2 coordinate
    `x_A=2q/(1+q)=2r/M`, `x_B=2-x_A`; the formal `(1,1)` middle is excluded from the coprime lanes of an even wheel.
28. A composite quiet under every prime child through (L) must have all prime factors greater than (L), and hence
    exceed (L^2); this exactly identifies the omitted upper-factor band responsible for false lower-parent ridges.
29. Under Mertens' product theorem and the prime number theorem, PN33's inverse-density fill satisfies
    `R_b(p) ~ log(p)/log(b) = 2^(x_b/2)`; its relative prime-gap curve is therefore asymptotically PNT itself and
    completion `R_b=2` occurs near `p~b^2`.
30. A common traversal of length 2 projected through 36 degrees has length `phi`: `S(u)=2u` and
    `P(u)=2u cos(36 degrees)=phi*u`; reversing the chart mirrors the endpoint to `2-phi`.
31. For two adjacent one-dimensional child accounts, subtracting the shared interface magnitude once from
    accumulation and once from release reconstructs the enclosing parent exactly; orientation reversal gives
    `x_parent' = 2 - x_parent`.
32. For an exactly declared local continuity account, stored-quantity change minus named internal transfer equals
    the omitted signed source/sink term exactly.
33. An integer parent plus its retained signed child-difference `Other` reconstructs both children exactly; recursive
    application therefore gives a lossless hierarchy when every residual is retained.
34. For two three-axis quantum parents, \(C=T-\mathbf a\mathbf b^\mathsf T\) is an exact nine-slot connected
    relation: product states give zero directions, ideal Bell states give three unit directions with negative
    determinant, equal Bell-family mixtures give one direction, and the four-state uniform mixture gives zero.

## ARA assumptions not proved by mathematics alone

1. Every physical identity instantiates the proposed spherical/wave closure and can be read through meaningful
   opposed diameter poles at an appropriate scale.
2. The same Phase-A/Phase-B, relation-born identity and crossing/closure grammar recurs across independently
   measured rungs and domains.
3. The golden ratio is a preferred physical handover factor rather than one important mathematical/dynamical
   landmark among nearby alternatives.
4. Singularity crossings in nature implement a particular \(F_{dyn}\), and its relation to static chart reversal
   can be derived for each domain.
5. Physical Information³ closure is accurately represented by the proposed relational ternary, holonomy or another
   declared relation-preserving transform.
6. The triangle→hexagon→pentagon constructions describe physical closure, projection or leak in a selected domain.
7. Dark matter is a closed Space-side relational structure projected to us through one gravitational edge.
8. The primitive dark-sector path weights are exactly \(2\) and \(3/2\).
9. The present-day dark-sector ratio formula is generated by this geometry rather than selected after observing
   the density ratios.
10. Golden pulse progression improves muon recovery under a fixed experimental energy budget.
11. The candidate aggregation \(j_{id}=(T_{AB}/2)(x-1)\), where \(T_{AB}\) is the variable expressed A/B subtotal
    inside the fixed contextual TE-ARA account, transfers beyond the exact Gauss construction to independently
    measured domains with typed surrounding contributions.

## Highest-value next tests

1. **Information³:** replace contemporaneous correlation cliques with held-out directional cycle-consistency and
   test whether closure predicts capability beyond parameter count, loss, node count, and repetition.
2. **Dark sector:** define the legal path graph and derive its primitive weights without using cosmological
   fractions; then derive a redshift-dependent transfer law \(Q\).
3. **Fractal closure:** measure whether a closed lower-level triangle predicts a stable higher-level node better
   than degree-matched open and common-driver controls.
4. **Fusion:** compare pulse schedules under identical carrier, pulse count, bandwidth, and energy, scoring the
   complete recover-and-recycle probability.
5. **Cross-scale ARA:** use matched signals, filters, cycle definitions, and independently fixed rung paths.
6. **Representation fidelity:** identify Phase A and Phase B in raw or least-transformed observations, freeze two
   representation maps, and test whether coupling then projection agrees with projection then coupling on held-out
   data.
7. **ARA × TE-ARA contextual aggregation:** predeclare the pure A/B identity, fixed-total-2 observed account,
   variable A/B subtotal, named environmental couplings and unresolved Other, direction coordinate, native magnitude
   scale and boundary, then predict a signed held-out
   physical result not used to construct those inputs. Do not use the constant TE-ARA total as variable strength.
8. **Forward hidden-term law:** use the recovered residual on development systems to identify a compact law, freeze
   that law, and predict a held-out `Other` waveform before observing the held-out stored-quantity change. The
   completed residual test was inverse diagnosis, not this forward prediction.
9. **Adaptive ARA memory:** freeze a block selector that chooses among raw, delta, pair-lifting and record-aware
   predictors after paying selector overhead; test unseen sensors, media, memory pages, text and random controls.
   Do not treat reversibility as compression or compression as confidentiality.

---

## One-paragraph summary

ARA can be given a clean mathematical skeleton centred on one proposed spherical/wave identity and one reversible
0–2 diameter reading through it. In the filled-state model, rotating the diameter through all axes reconstructs
the ball and sweeps its spherical boundary. Exact phase/anti-phase mixtures fill one diameter; its centre is equal
participation, while relative phase and total activity distinguish quiet cancellation from coherent reinforcement
and other active ridges. Duration supplies one bounded, invertible diameter instrument, not the definition of every
ARA axis. Static pole-chart reversal, octave scale change, candidate golden handover and physical singularity
crossing are typed separately. Information³ begins with two identities plus their retained relation; triangular
holonomy is one rigorous closure test, and repeated triangular closure is one sufficient self-similar construction
rather than the primitive ARA object. Regular triangle, hexagon, pentagon, dark-sector, LLM, quantum, pendulum and
fusion sections are exact or conditional decompressions with their assumptions visible. The prime subset adds exact
factor-pair closure, wheel anti-pair reflection and lossless `2:1` recursive compression while explicitly rejecting
the inference that three conceptual stages equal three cheap operations. The mathematics proves
internal coherence and calculability inside those declared models; raw-first observation and prospective tests must
decide whether the same relational geometry recurs in nature.
