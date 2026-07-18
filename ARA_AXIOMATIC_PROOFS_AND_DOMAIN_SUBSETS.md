# ARA axiomatic mathematics and domain subsets

**Author:** Dylan La Franchi, with formalisation assistance from Codex  
**Date:** 11 July 2026  
**Centered revision:** 4:00 pm AEST, 19 July 2026

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

### TE-ARA definition — identity-mode participation, not Gauss flux

For a declared node, boundary, time window and predeclared energy-mode decomposition with \(E_{total}>0\), define

\[
\boxed{
\underbrace{\mathrm{TE\!-\!ARA}}_{\substack{\text{main-identity energy participation}\\\text{reported on }0\text{--}2}}
=2\frac{
\underbrace{E_{id}}_{\substack{\text{energy assigned to the main}\\\text{Phase-A/Phase-B identity wave}}}
}{
\underbrace{E_{total}}_{\text{all energy in the same boundary/window}}
}
}.
\tag{4d}
\]

TE-ARA weights how much measured energy participates in the declared identity mode. ARA supplies that mode's
Phase-A/Phase-B position. Gauss supplies signed electric source flux. They are different projections and must not
be compared as untyped numbers.

A candidate dimensionless main-identity contribution is

\[
\underbrace{j_{id}}_{\text{signed identity contribution}}
=
\underbrace{\frac{\mathrm{TE\!-\!ARA}}2}_{\text{identity participation}}
\underbrace{(x-1)}_{\text{centred ARA direction}}.
\tag{4e}
\]

Equation (4e) is an ARA aggregation hypothesis outside the exact Gauss decomposition. Applying it physically
requires a common unit scale, independently declared modes, and separately measured surrounding contributions.

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

# Part IX — What is proved, assumed, and still testable

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
13. A deterministic many-to-one projection has a nonnegative hidden-information cost.
14. Pentagon/phi, octave projection, and five-versus-six angular-defect identities are exact mathematics.
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
11. The candidate aggregation \(j_{id}=(\mathrm{TE\!-\!ARA}/2)(x-1)\), with typed surrounding contributions,
    transfers beyond the exact Gauss construction to independently measured domains.

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
7. **ARA × TE-ARA aggregation:** predeclare the identity modes, energy participation, direction coordinate, unit
   scale and surrounding terms, then predict a signed held-out physical result not used to construct those inputs.

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
fusion sections are exact or conditional decompressions with their assumptions visible. The mathematics proves
internal coherence and calculability inside those declared models; raw-first observation and prospective tests must
decide whether the same relational geometry recurs in nature.
