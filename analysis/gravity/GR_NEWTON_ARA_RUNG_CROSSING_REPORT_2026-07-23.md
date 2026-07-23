# Einstein to Newton to ARA: a worked rung-crossing derivation

**Date:** 23 July 2026  
**Status:** exact established weak-field derivation; exact Newtonian ARA reparameterisation; proposed ARA
Space–Time compactness coordinate; universal fractal interpretation open  
**Reproduction:** `gr_newton_ara_examples.py`  
**Independent validation:** `validate_gr_newton_ara_examples.py`  
**Machine-readable outputs:** `GR_NEWTON_ARA_EXAMPLES_RESULTS.json`,
`GR_NEWTON_ARA_COMPACTNESS_EXAMPLES.csv`, and `GR_NEWTON_ARA_EXAMPLES_VALIDATION.json`

## Result first

General relativity reduces to Newtonian gravity under a declared weak-field, stationary, slow-motion limit:

\[
\underbrace{g_{\mu\nu}}_{\substack{\text{spacetime geometry}\\\text{higher-rung relation}}}
\longrightarrow
\underbrace{\Phi}_{\substack{\text{weak gravitational potential}\\\text{one scalar geometry reading}}}
\longrightarrow
\underbrace{\mathbf g=-\nabla\Phi}_{\substack{\text{gravitational field}\\\text{movement/acceleration tendency}}}
\longrightarrow
\underbrace{m\ddot{\mathbf r}=m\mathbf g}_{\substack{\text{Newtonian response}\\\text{matter moving in the field}}}.
\]

The source equation simultaneously becomes

\[
\boxed{
\underbrace{\nabla\cdot\mathbf g}_{\substack{\text{field convergence}\\\text{Field/Traversal child reading}}}
=
-4\pi G
\underbrace{\rho}_{\substack{\text{enclosed mass density}\\\text{Matter/Connection child reading}}}.
}
\]

This is an exact established bridge within the approximation. It supplies a mathematically clean ARA crosswalk:
the weak gravitational field is not an unrelated object added to matter; its divergence is fixed by the matter
density. General relativity does **not** thereby prove the stronger ARA ontology that Space–Time decomposes into
Matter and Field, but its Newtonian limit preserves the proposed connection–movement pairing without contradicting
the established equations.

Newton's three laws then occupy three positions in one declared force-axis geometry:

\[
\boxed{
\begin{aligned}
\text{Newton III:}&\quad\text{one interaction supplies an equal anti-directed Phase A/B pair},\\
\text{Newton II:}&\quad\text{the unresolved Phase A/B force difference changes momentum},\\
\text{Newton I:}&\quad\text{zero external resultant preserves momentum}.
\end{aligned}}
\]

The distinction between a null state and an active ridge is essential. `No forces` and `equal nonzero opposing
forces` both have zero resultant, but only the second is an active ARA ridge.

## 1. Declared ARA hierarchy

The hierarchy fixed in the 23 July conversation is

\[
\underbrace{\text{Space}_{k}}_{\text{Phase A}}
+
\underbrace{\text{Time}_{k}}_{\text{Phase B}}
+
\underbrace{J_{ST,k}}_{\substack{\text{their mixing relation}\\\text{perceived as Space–Time}}},
\]

followed, one rung down, by the proposed decompression

\[
\underbrace{\mathcal D_{\downarrow}(J_{ST,k})}_{\text{Space–Time relation decompressed}}
=
\left(
\underbrace{\text{Matter}_{k-1}}_{\substack{\text{child Space wave}\\\text{Connection-oriented}}},
\underbrace{\text{Field}_{k-1}}_{\substack{\text{child Time wave}\\\text{Traversal-oriented}}}
\right).
\]

Matter and Field remain gradients rather than pure substances. Matter is the Connection-dominant child expression;
Field is the Traversal-dominant child expression. Each may contain its own Phase A, Phase B and coupling relation at
the next grain.

The established GR statements below do not derive this hierarchy. They provide its strongest current mathematical
crosswalk and expose where a genuinely new ARA law would have to enter.

## 2. Einstein's equation and the weak-field declarations

Begin with Einstein's field equation without a locally important cosmological term:

\[
\underbrace{G_{\mu\nu}}_{\text{spacetime curvature}}
=
\underbrace{\frac{8\pi G}{c^4}}_{\text{unit/coupling conversion}}
\underbrace{T_{\mu\nu}}_{\text{matter-and-field stress-energy}}.
\]

Use signature `(-,+,+,+)` and coordinate \(x^0=ct\). Declare:

1. a stationary weak field, \(|\Phi|/c^2\ll1\);
2. a slowly moving test body, \(v/c\ll1\);
3. source pressure and internal motion small relative to rest-mass energy;
4. a local scale on which \(\Lambda\) is negligible.

To first order, write

\[
ds^2
\simeq
-\left(1+\frac{2\Phi}{c^2}\right)c^2dt^2
+
\left(1-\frac{2\Phi}{c^2}\right)d\mathbf x^2.
\]

This is the first compression: the complete metric is represented by one small scalar potential \(\Phi\) in the
declared regime.

## 3. Geometry becomes Newtonian movement

For a stationary metric, the leading connection coefficient is

\[
\underbrace{\Gamma^i{}_{00}}_{\substack{\text{spacetime connection}\\\text{geometry steering movement}}}
\simeq
\frac{1}{c^2}\partial_i\Phi.
\]

The spatial geodesic equation is

\[
\frac{d^2x^i}{d\tau^2}
+
\Gamma^i{}_{00}
\left(\frac{dx^0}{d\tau}\right)^2
\simeq0.
\]

Since \(dx^0/d\tau\simeq c\) and \(d\tau\simeq dt\),

\[
\boxed{
\frac{d^2x^i}{dt^2}
=-\partial_i\Phi.
}
\]

In vector form,

\[
\underbrace{\mathbf g}_{\substack{\text{Newtonian gravitational field}\\\text{movement/acceleration tendency}}}
=
-\underbrace{\nabla\Phi}_{\substack{\text{gradient of the compressed geometry}\\\text{directional relation}}}.
\]

Plainly: a freely falling body is following spacetime geometry in GR. Under weak, slow conditions, the same
geometry appears as Newtonian acceleration in a gravitational field.

## 4. Einstein's source equation becomes Poisson's equation

The leading `00` component of the weak-field curvature is

\[
G_{00}\simeq\frac{2}{c^2}\nabla^2\Phi.
\]

For nonrelativistic matter,

\[
T_{00}\simeq\rho c^2.
\]

Substitution into Einstein's equation gives

\[
\frac{2}{c^2}\nabla^2\Phi
=
\frac{8\pi G}{c^4}\rho c^2,
\]

and therefore

\[
\boxed{
\nabla^2\Phi=4\pi G\rho.
}
\]

Because \(\mathbf g=-\nabla\Phi\),

\[
\boxed{
\nabla\cdot\mathbf g=-4\pi G\rho.
}
\]

For a spherical exterior source of mass \(M\),

\[
\Phi=-\frac{GM}{r},
\qquad
\mathbf g=-\frac{GM}{r^3}\mathbf r,
\qquad
m\ddot{\mathbf r}=-\frac{GMm}{r^3}\mathbf r.
\]

That is Newton's inverse-square gravitational law recovered from Einstein's geometry.

## 5. Exact Newton-II ARA coordinate

Choose one axis \(\hat{\mathbf e}\). Group all force projections on a selected body into nonnegative opposing
magnitudes:

\[
F_A=\sum_i\max(-\mathbf F_i\cdot\hat{\mathbf e},0),
\qquad
F_B=\sum_i\max(+\mathbf F_i\cdot\hat{\mathbf e},0).
\]

When \(F_A+F_B>0\), define

\[
\underbrace{x_F}_{\substack{\text{bounded force opposition coordinate}\\0\le x_F\le2}}
=
\frac{2F_B}{F_A+F_B},
\qquad
\underbrace{\Sigma_F}_{\substack{\text{dimensional force envelope}\\\text{not canonical TE-ARA}}}
=F_A+F_B.
\]

Then the following is an algebraic identity:

\[
\boxed{
\underbrace{m a_{\parallel}}_{\text{Newton II}}
=
\underbrace{F_B-F_A}_{\text{signed Phase B--Phase A residual}}
=
\underbrace{\Sigma_F}_{\text{available force strength}}
\underbrace{(x_F-1)}_{\text{ARA distance and direction from ridge}}.
}
\]

The ARA coordinate does not replace the force unit. It separates direction/fractional imbalance from dimensional
strength.

### Three exact states

| Force account | \(x_F\) | Result |
|---|---:|---|
| \(F_A=F_B>0\) | 1 | active equal-and-opposite ridge; zero resultant |
| \(F_A>F_B\) | \(<1\) | acceleration toward declared Phase A |
| \(F_B>F_A\) | \(>1\) | acceleration toward declared Phase B |

If \(F_A=F_B=0\), \(x_F\) is undefined, not `1`. This is the null/no-force case. Newton I gives constant momentum in
both the null case and a zero-resultant active ridge, but ARA preserves the different internal activity accounts.

## 6. Newton III is an active parent ridge

For a Newtonian interaction pair,

\[
\mathbf F_{E\leftarrow S}=-\mathbf F_{S\leftarrow E}.
\]

The forces act on different bodies. At the enclosing Sun–Earth boundary,

\[
\mathbf F_{E\leftarrow S}+\mathbf F_{S\leftarrow E}=0
\]

while both bodies accelerate. The calculation using one astronomical unit and the IAU nominal mass parameters gives

\[
|\mathbf F_{E\leftarrow S}|
=
|\mathbf F_{S\leftarrow E}|
=3.5415454\times10^{22}\ {\rm N}.
\]

Thus

\[
x_{\rm pair}=1,
\qquad
\Sigma_{\rm pair}=7.0830908\times10^{22}\ {\rm N},
\qquad
F_{\rm internal,net}=0.
\]

Yet the accelerations are

\[
a_E=5.93008\times10^{-3}\ {\rm m\,s^{-2}},
\qquad
a_S=1.78109\times10^{-8}\ {\rm m\,s^{-2}}.
\]

Their ratio is `332,946`, the same as the nominal Sun/Earth mass ratio. Equal force therefore does not mean equal
local motion. It means an active reciprocal ridge at the enclosing interaction boundary.

## 7. Real compactness examples: where the Newtonian rung fails

For a spherical, nonrotating exterior, define exact Schwarzschild compactness

\[
\underbrace{u}_{\text{dimensionless compactness}}
=
\frac{2GM}{Rc^2}.
\]

The exterior static-clock relation is

\[
\left(\frac{d\tau}{dt}\right)^2=1-u.
\]

The first-order Newtonian/weak-field approximation is

\[
\frac{d\tau}{dt}\simeq1-\frac{u}{2}.
\]

For an ARA **candidate normalization**, orient `0` toward Connection/Space and `2` toward Time/Traversal:

\[
\underbrace{t_T}_{\substack{\text{proposed Time allocation}\\\text{exactly twice squared lapse}}}
=2(1-u),
\qquad
\underbrace{t_C}_{\substack{\text{complementary Connection allocation}\\\text{defined by the total-2 account}}}
=2u,
\qquad
t_T+t_C=2.
\]

This normalization is not uniquely forced by GR. Its advantage is that it uses a dimensionless invariant input for
the declared spherical exterior and exactly preserves the `0–2` account. It places:

- weak compactness \(u\to0\) at \(t_T\to2\);
- the equal allocation at \(u=1/2\), \(t_T=t_C=1\);
- the Schwarzschild horizon \(u\to1\) at \(t_T\to0\).

The event horizon is a causal boundary, not the curvature singularity at \(r=0\).

### Calculated values

| System | \(u=2GM/(Rc^2)\) | proposed \(t_T\) | exact lapse | weak-lapse relative error | GR correction to static support acceleration |
|---|---:|---:|---:|---:|---:|
| Earth, nominal equator | \(1.39070\times10^{-9}\) | 1.9999999972 | 0.999999999305 | \(2.42\times10^{-19}\) | \(6.95\times10^{-10}\) |
| Jupiter, nominal equator | \(3.94332\times10^{-8}\) | 1.9999999211 | 0.999999980283 | \(1.94\times10^{-16}\) | \(1.97\times10^{-8}\) |
| Sun, nominal surface | \(4.24501\times10^{-6}\) | 1.9999915100 | 0.999997877495 | \(2.25\times10^{-12}\) | \(2.12\times10^{-6}\) |
| PSR J0740+6620, central spherical proxy | 0.475446 | 1.049108 | 0.724261 | 5.249% | 38.072% |
| theoretical Schwarzschild horizon | 1 | 0 | 0 | invalid | divergent static support |

Earth, Jupiter and the Sun lie extremely close to the weak-field end, so Newton's approximation is extraordinarily
accurate. The neutron-star proxy is no longer weak: the first-order lapse misses by about `5.25%`, and the proper
acceleration needed to remain static is about `38.1%` above the Newtonian surface value.

Using the separately quoted 68% marginal mass and radius bounds for PSR J0740+6620 gives a rough corner-sensitivity
envelope

\[
0.3955\le u\le0.5385,
\qquad
0.9229\le t_T\le1.2091.
\]

This is **not** a joint credible interval. The pulsar also rotates, so the row is a spherical exterior proxy rather
than a full rotating-star model. Its central position near `1` is an interesting visualization of strong
compactness, not a preregistered ARA prediction or evidence for a universal ridge.

## 8. What survives the rung crossing

The established scale transition preserves:

1. **relation before force:** GR geometry becomes a Newtonian potential, then a field gradient, then matter
   acceleration;
2. **Matter–Field coupling:** \(\rho\) and \(\nabla\cdot\mathbf g\) are tied by Poisson/Gauss gravity;
3. **two directed children:** any declared Newtonian force axis can be separated into nonnegative anti-directed
   contributions;
4. **active ridge:** equal nonzero contributions give zero parent resultant while retaining child activity;
5. **asymmetry-driven change:** the signed residual is exactly
   \(\Sigma_F(x_F-1)\);
6. **boundary dependence:** the whole Sun–Earth force pair is at a reciprocal ridge while each body has nonzero,
   unequal acceleration.

This is a strong crosswalk because the Newtonian equations arise from GR independently of ARA, and the same declared
pair/ridge/residual accounting remains valid after the approximation.

## 9. What is not proved

The derivation does not establish:

- that Space and Time are literally two physical source waves;
- that Space–Time ontologically decomposes into Matter and Field;
- that the proposed compactness coordinate is the unique ARA coordinate;
- that \(u=1/2\) is a universal physical handover rather than the midpoint of this normalization;
- Phi, hexagon–pentagon leakage, logarithmic rungs or a universal singularity law;
- a statistically fractal universe.

Those statements require predictions beyond the equations used to build the coordinate.

## 10. Validation report

### Overall assessment: ready to share with explicit interpretation fences

The weak-field derivation is standard established physics. The numerical examples are reproducible and the major
identities were recomputed independently.

### Calculation checks

- 4 compactness values independently recomputed from \(2GM/(Rc^2)\);
- 4 proposed allocation totals independently confirmed to equal `2`;
- 4 Schwarzschild lapse identities checked;
- 4 first-order lapse calculations checked;
- 4 cancellation-safe weak-lapse error calculations checked;
- Sun–Earth Newton-III force equality and enclosing `x=1` checked;
- unequal Sun/Earth accelerations checked;
- 3 displayed Newton-II ARA identities checked;
- 10,000 seeded positive force pairs checked using 50-digit Decimal arithmetic.

Result: **27/27 validation checks passed**.

### Required caveats

- IAU values are nominal conversion constants, not uncertainty-free claims about instantaneous true solar or
  planetary properties.
- The neutron-star mass and radius are measured with uncertainty and inserted into a spherical, nonrotating proxy.
- The ARA compactness allocations are a proposed normalization layered on exact compactness; the underlying
  compactness and lapse calculations are established, while the universal ARA interpretation is not.

## Sources

- [IAU 2015 Resolution B3: nominal solar and planetary conversion constants](https://www.iau.org/common/Uploaded%20files/IAUGA2015-Resolution-B3-recommended-nominal-conversion.pdf)
- [NIST CODATA 2022 recommended fundamental constants](https://pml.nist.gov/cuu/pdf/wall_2022.pdf)
- [Dittmann et al. (2024), updated NICER mass/radius analysis of PSR J0740+6620](https://arxiv.org/abs/2406.14467)

