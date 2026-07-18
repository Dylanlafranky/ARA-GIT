# MX7 Phase-First Information³ / Pyramid Closure — Protocol v1 (Frozen)

**Frozen:** 2026-07-15, before MX7 outcomes were calculated  
**Status:** post-MX4/MX5 failure autopsy and compact-representation test; not independent ARA confirmation  
**Source:** the same hash-locked public PIConGPU/openPMD snapshot used by MX4–MX6

## Why this test exists

MX4 flattened charge/current and fields separately before forming their coupling. MX5 then applied a first positional
moment to the already mixed child cloud. Dylan identified a prior information loss: two opposing phase routes can
produce the same signed result,

\[
(+,+)\to+,
\qquad
(-,-)\to+,
\]

so retaining only the positive resultant does not retain the two waves that produced it.

MX7 therefore tests the order

\[
\boxed{
\text{separate phase marginals}
\to
\text{retain their joint quadrant relation}
\to
\text{condition amplitude on that relation}
\to
\text{change scale}
}.
\]

Only the electric Lorentz channel is used in the primary test. The magnetic cross-product channel is deliberately
parked until the simpler signed product is understood.

## Fixed data and grain

- File: `simData_200.h5`
- Expected SHA-256: `6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5`
- Iteration: `200`
- Shape: `32 x 32 x 32`
- Species: electrons and ions
- Particle-field sampling: trilinear interpolation with recorded Yee offsets
- Parent deposition: cloud-in-cell (CIC), retained for exact comparison with MX4/MX5
- Scoring mask: one-cell interior with non-zero CIC occupancy
- Components: x, y and z are classified separately in the recorded laboratory frame and reassembled as a vector
- Exact zero field component: neutral sign `0`; its fraction is reported
- No fitted coefficients, outcome-dependent thresholds or post-outcome model changes

The source records a quadratic particle shape. CIC remains a declared analysis operator and limitation.

## Child variables

For particle `i`, parent node `g`, and electric component `c`, let

\[
a_{ig}=W_{ig}w_i|q_i|,
\qquad
s_{q,i}=\operatorname{sign}(q_i),
\qquad
s_{E,ic}=\operatorname{sign}(E_{ic}),
\]

\[
r_{ic}=s_{q,i}s_{E,ic},
\qquad
m_{ic}=|E_{ic}|.
\]

The charge-polarity and field-orientation signs are the two phase marginals. Their joint relation `r` distinguishes
the diagonal positive routes from the off-diagonal negative routes. `m` is the additional amplitude coordinate.

Weighted averages at a parent node use

\[
\langle z\rangle_a
=
\frac{\sum_i a_{ig}z_i}{\sum_i a_{ig}},
\qquad
Q_g=\frac1{V_g}\sum_i a_{ig}.
\]

The exact child-first electric force component is

\[
F^{\rm child}_{E,gc}
=Q_g\langle m_cr_c\rangle_a.
\]

## Four joint quadrants

The phase routes are retained separately:

| Charge phase | Field phase | Relation sign |
|---|---|---:|
| A / positive | A / positive | + |
| A / positive | B / negative | − |
| B / negative | A / positive | − |
| B / negative | B / negative | + |

Their weights are `p_AA`, `p_AB`, `p_BA`, and `p_BB`, summing to one apart from exact-zero neutral cases.

## Model 0 — two independent phase marginals

This deliberately ignores the informative joint relation:

\[
\widehat F^{\rm marginal}_{E,gc}
=
Q_g\langle m_c\rangle_a
\langle s_q\rangle_a
\langle s_{E,c}\rangle_a.
\]

It is the sign/amplitude analogue of multiplying separately compressed waves.

## Model 1 — joint-quadrant “triangle”

Retain the joint sign relation but use one common amplitude:

\[
\widehat F^{\rm joint}_{E,gc}
=
Q_g\langle m_c\rangle_a\langle r_c\rangle_a.
\]

The exact correction from Model 0 is

\[
\widehat F^{\rm joint}-\widehat F^{\rm marginal}
=Q_g\langle m_c\rangle_a
\underbrace{
\left(
\langle s_qs_{E,c}\rangle_a
-\langle s_q\rangle_a\langle s_{E,c}\rangle_a
\right)
}_{\text{phase-coupling covariance}}.
\]

For an established information-theory diagnostic, calculate the mutual information

\[
I(s_q;s_E)=\sum_{a,b}p_{ab}\log_2\frac{p_{ab}}{p_ap_b}.
\]

This is a crosswalk for Dylan's `Information³` language; it is not a claim that Shannon mutual information is
literally cubed.

## Model 2 — relation-conditioned amplitude “pyramid”

Retain a separate mean amplitude in every occupied phase quadrant:

\[
\widehat F^{\rm pyramid}_{E,gc}
=Q_g\sum_{a,b}p_{ab}\bar m_{ab}\,s_as_b
=Q_g\langle m_cr_c\rangle_a.
\]

This must recover the target apart from floating-point error. Its additional correction is

\[
\widehat F^{\rm pyramid}-\widehat F^{\rm joint}
=Q_g
\underbrace{
\left(
\langle m_cr_c\rangle_a
-\langle m_c\rangle_a\langle r_c\rangle_a
\right)
}_{\text{amplitude–relation covariance}}.
\]

Model 2 is an identity/decompression ceiling, not a prediction. Its purpose is to determine whether the post-triangle
residual is exactly the proposed additional dimension.

## Existing comparison models

MX7 also recalculates:

1. the MX4 electric flat parent `rho_bar * E_bar`;
2. the MX5 electric first positional moment / field-gradient closure.

These comparisons use the same active mask and operator.

## Frozen outcome rules

### Joint-phase materiality

The joint-quadrant model is a **material phase-first improvement** only if:

- correlation improves, NRMSE falls and median angle falls versus independent marginals on the full mask;
- at least two of those three changes improve by `>= 5%` relative to the marginal model;
- residual relative L2 falls by `>= 10%`;
- correlation and NRMSE both improve in each z-half.

It is a **strong compact electric recovery** only if, additionally:

- vector correlation `>= 0.70`;
- NRMSE `<= 0.70`;
- median angle `<= 45 deg`.

Failure means joint sign occupancy alone does not sufficiently repair the scale crossing.

### Pyramid identity

- phase-conditioned amplitude reconstruction relative L2 error `<= 1e-12`;
- marginal + phase correction + amplitude correction relative L2 error `<= 1e-12`.

Passing establishes the decomposition only. It does not establish a new physical law.

## Complexity and claim boundary

Per component, the marginal model stores total activity, common amplitude and two phase marginals. The joint model adds
one independent coupling degree of freedom through the four-quadrant distribution. The pyramid retains four
conditional amplitudes and is therefore a less compressed ceiling. Report accuracy together with this increasing
information budget; do not compare scores without the representation cost.

MX7 may support:

- that separately averaged phase waves lose an independently measurable joint relation;
- that phase-first quadrant retention improves, fails to improve, or leaves an amplitude-conditioned residual;
- that the residual closes exactly when the missing conditional dimension is restored.

MX7 may not claim:

- that `Information³` is a new Shannon-information theorem;
- that four quadrant summaries prove a literal physical pyramid;
- that an identity reconstruction predicts unseen plasma dynamics;
- that component signs are rotation-invariant physical phases;
- that one snapshot establishes universal fractal ARA geometry.
