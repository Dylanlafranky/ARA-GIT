# Water / Geodesic / Log-Rung Recovery Audit — 13 July 2026

## Outcome

The archived work does contain the components Dylan recalled. They were distributed across separate walks rather than
stated as one coupling law:

1. **Water supplied the 1:2 closure:** one central node coupled to two equivalent constraint nodes along a bent arc.
2. **The sphere work supplied the curved metric:** angular/great-circle distance rather than a flat perpendicular.
3. **The vertical-translation work supplied the logarithm:** local transfer factors multiply; their logarithms add.
4. **The later chain model supplied the recursion:** ARA-to-ARA handovers propagate through successive rungs.

The current decomposition is therefore a clarification of an early research path, not a wholly new construction:

\[
I_{k+1}
=
\mathcal C_{1:2}
\left(A_k,B_{1,k},B_{2,k};J(\Delta\theta),E_k\right),
\qquad
\Delta K
=
\sum_i\log_b T_i.
\]

Here the first expression is the local curved triadic closure and the second is its accumulated rung translation.

## Recovered lineage

| File | Repository evidence | Relevance to the present rule |
|---|---|---|
| `archive/numbered_tests/111_three_system_curvature_bridge.py` | committed 22 Apr 2026, 02:38 +1000 | Three-system coupling matrix; explicit section on geodesic deviation from a coupling gradient. |
| `archive/numbered_tests/115_water_rosetta_stone.py` | committed 22 Apr 2026, 02:38 +1000; header says April 2026 | Calls water a three-system template; explicitly says the 104.5° angle occurs when “TWO equivalent constraints act on one system”; places the two H nodes on opposite sides of O; uses three-circle overlap. |
| `archive/numbered_tests/116_sp3_template_test.py` | same archived sequence | Tests whether the water angular match generalises; importantly records that the original universal molecular claim fails. |
| `archive/numbered_tests/116b_circle_packing_gap.py` | same archived sequence | Uses spherical cells and great-circle arcs; exploratory attempt to turn the flat gap into a curved/spherical quantity. |
| `archive/numbered_tests/117_triple_tangency_constraint.py` | same archived sequence | Treats three-node closure as a curved triangular junction and tests how junction angles change with radius ratio. |
| `archive/numbered_tests/142_circular_vertical_translation.py` | committed 22 Apr 2026, 21:54 +1000 | States that vertical displacement is rotation around a circle in log space, with phase/topology determining angular position. |
| `archive/numbered_tests/143_ara_chain_coupling.py` | committed 22 Apr 2026, 21:54 +1000 | States that total transfer is the product of local links and therefore a sum of log transfers; separately names the “perpendicular wiggle.” |
| `archive/numbered_tests/163_sphere_triangulation.py` | committed 22 Apr 2026, 21:54 +1000 | Maps ARA to sphere coordinates and explicitly defines side lengths as great-circle distances / ARA gaps. |
| `FableConvo/PROVENANCE_LEDGER.md` | later transcript extraction | Preserves Dylan's earlier wording: “two small waves to one large wave... the larger holding the connection inside it.” |
| `FableConvo/ARA_MAPPING_WATER.md` | added 6 Jul 2026 | Later calibrated mapping: 2-donor + 2-acceptor water network, two competing liquid topologies, Widom-line ridge; retires the old phi-four phase-energy ratio. |

This lineage supports a provenance claim: Dylan was repeatedly walking the same local shape -- two similar child
contributions, one larger/central identity, a curved angular relation and a scale-changing chain -- before the present
hypergraph/geodesic notation existed.

## Additional numbered-test lineage for why the rung is logarithmic

Dylan subsequently identified Tests 8, 9, 19, 51, 87, 111, 112, 114, 156 and 175 as related parts of this walk.
They do not all derive the logarithm, but together they recover a longer conceptual sequence:

| Test | Contribution | Evidential qualification |
|---|---|---|
| 8 | Places systems on a `log10(Action/pi)` axis and tries wrapping that axis around a circle. | Its `log10(pi)` spacing result is explicitly non-significant; useful provenance, not evidence for a special spacing constant. |
| 9 | Treats each octave as a bounded interval on a log-action axis, with compressed edges and a looser middle; uses hydrogen's power-law level compression as a motivating example. | The proposed Chebyshev/ARA within-octave profile is exploratory and is not derived from hydrogen. |
| 19 | Measures occupation density and deserts per decade along the action ladder. | Shows why logarithmic binning is operationally useful across many orders of magnitude; the density profile is highly vulnerable to selection and sampling bias. |
| 51 | Treats light-matter absorption/release as a cross-scale handover. | Relevant to what may traverse rungs, but it does not derive logarithmic rung distance. |
| 87 | Places heterogeneous oscillatory processes on one `logT`/`logE` spine spanning tens of decades. | Demonstrates scale compression; its hand-entered heterogeneous catalogue and earlier fixed boundaries do not establish universality or Information-cubed. |
| 111 | Represents paired frequencies as `[1,sqrt(A),1/sqrt(A)]`, preserving their geometric mean, and measures asymmetry by `abs(log(A))`. | This contains the strongest reciprocal-symmetry clue. The script overstates a coupling/stiffness matrix as a metric tensor and does not recover GR. |
| 112 | Maps an asymmetric coupling landscape on the two sides of Phi. | Supplies a candidate well/asymmetric-basin picture, but scans ARA linearly and does not itself derive the logarithm. |
| 114 | Explicitly states that between-scale coupling is logarithmically stronger and that the scale above constrains the scale below. | This is direct provenance for the claim, but the script assumes rather than derives `logarithmically stronger`; its `8/8` score includes re-labelled established facts and constructed comparisons. |
| 156 | Defines a circle circumference `2*pi*R` in log-decades, with scale gap divided into completed turns plus final phase. | A coherent geometric coordinate construction; the cross-scale result is retrospective and its radii/phase inputs are fitted rather than independently derived. |
| 175 | Tries an inner normalized circle `R=1/ARA` driving an outer data circle `R=ARA`, including a `log(log(x))` alternative. | Useful nested-scale decompression. Follow-up Test 176 says the nested version had rhythm but unstable amplitude, so it is not a validated physical law. |

The key result is that the logarithm can now be derived **conditionally**, without relying on the old numerical fits.
Let a positive scale ratio be (q=E_2/E_1). If successive local rung ratios compose multiplicatively while rung
displacements compose additively, then the rung coordinate (K) must obey

\[
K(q_1q_2)=K(q_1)+K(q_2),
\qquad K(1)=0,
\qquad K(1/q)=-K(q).
\]

For a continuous monotone coordinate, the solutions are

\[
K(q)=c\ln q,
\]

where $c$ only selects the unit/base. Thus the logarithm is not being selected because a log curve happens to fit:
it is the essentially unique continuous coordinate that turns multiplicative scale composition into additive rung
distance. Test 111's reciprocal construction then becomes exact:

\[
d(A,1)=|\ln A|=|\ln(1/A)|.
\]

Phase and anti-phase reciprocal ratios are therefore equally distant from the $1.0$ ridge in log-ratio geometry.
This also supplies an exact bridge to the bounded ARA $0$–$2$ coordinate, provided the two channels are
nonnegative quantities in common units. Let

\[
x=\frac{2A}{A+B},
\qquad
r=\frac{A}{B}.
\]

Then

\[
r=\frac{x}{2-x},
\qquad
u=\ln r=\ln\!\left(\frac{x}{2-x}\right),
\qquad
x=\frac{2}{1+e^{-u}}=1+\tanh(u/2).
\]

This is a scaled logit/log-odds transform. It makes the landmarks exact:

- $x=1\Longleftrightarrow A=B\Longleftrightarrow u=0$;
- exchanging $A\leftrightarrow B$ sends $x\mapsto2-x$ and $u\mapsto-u$;
- $x\to0$ sends $u\to-\infty$;
- $x\to2$ sends $u\to+\infty$.

Thus the finite ARA diameter is a compact view of an unbounded log-ratio line. Near the upper pole,

\[
2-x\approx2e^{-u},
\]

so equal steps in log-ratio shrink the remaining distance to the pole exponentially; the corresponding statement
holds near zero. This provides a precise mathematical meaning for a **gradual singularity well at both poles**.
Reaching either pure endpoint requires an unbounded channel ratio in the ideal model. Calling that ratio an energy
cost is justified only when $A$ and $B$ have been declared as energy/capacity channels in the same units.

If one rung uses a fixed factor $b>1$, then

\[
k=\log_b(E/E_0)
\quad\Longleftrightarrow\quad
E_k=E_0b^k.
\]

Equal rung steps consequently require multiplicatively -- hence exponentially -- increasing absolute scale or
capacity. This is the precise relationship between Dylan's early statements that the stack is logarithmic and that
crossing upward has an exponential cost. Base two is a special case, not yet a universal result.

Test 156 supplies the circle wrapping of that straight log coordinate. With $u=\ln(E/E_0)$,

\[
\theta=(u/R)\bmod 2\pi,
\qquad
N=\left\lfloor\frac{u}{2\pi R}\right\rfloor.
\]

$N$ counts completed log-circles and $\theta$ locates the remainder on the current circle. A circular geodesic separation is

\[
d_{S^1}(u_1,u_2)=\min_{m\in\mathbb Z}|u_1-u_2+2\pi Rm|.
\]

This cleanly joins the log ladder to the geodesic language. It does not establish that every physical scale transition
has the same $R$, base or closure threshold.

Finally, a **well** does not follow from the logarithm alone. A symmetric candidate around the ridge would be

\[
W(A)=\tfrac12\kappa[\ln A]^2,
\]

while an ARA-asymmetric well requires predeclared different coefficients or an additional odd term on the two sides.
Test 112 motivates looking for that asymmetry, but it does not determine a universal well law.

## `TWO_RULERS_PHI_AND_TWO.md`: the typed-ruler synthesis

The May synthesis document adds the missing operational distinction. Its latest correction says that $2$ sets
octave rung spacing, while Phi is a candidate relational handover timing rather than the height of the scale step.
This is compatible with the recovered log geometry once three uses are typed explicitly:

| Quantity | Coordinate/law | Job |
|---|---|---|
| Scale/rung position | $k=\log_2(S/S_0)$ | A doubling of physical scale is one octave step. |
| Local ARA state | $x=2A/(A+B)=1+\tanh[\frac12\ln(A/B)]$ | Places the two-channel mixture on the bounded $0$–$2$ diameter. |
| Handover duty/phase | $h_A+h_B=1$, candidate $(h_A,h_B)=(\phi^{-2},\phi^{-1})$ | Says how long each channel dominates during a cycle. |

These are not three unrelated ARA objects. They are three declared measurements of the same proposed coupled cycle:
scale displacement, instantaneous/aggregated mixture and within-cycle handover. They nevertheless cannot be inserted
into one another without the displayed transformations.

The document's mirror result becomes especially clean. On the bounded state coordinate,

\[
M(x)=2-x.
\]

On the underlying ratio coordinate this is exactly inversion:

\[
r=\frac{x}{2-x}
\quad\Longrightarrow\quad
r(M(x))=\frac1r.
\]

At the Phi landmark,

\[
M(\phi)=2-\phi=\phi^{-2},
\qquad
r(\phi)=\frac{\phi}{2-\phi}=\phi^3,
\qquad
u(\phi)=3\ln\phi.
\]

Thus the document's φ/0.382 mirror pair is exact and now has an exact log-ratio interpretation. It also reveals a
necessary distinction: the golden duty shares $0.382/0.618=(\phi^{-2},\phi^{-1})$ would occupy bounded share
coordinates $2\phi^{-2}\approx0.764$ and $2\phi^{-1}\approx1.236$, not $x=\phi$. "Phi as an ARA-state
landmark" and "Phi-coded duty" may be related projections, but they are not numerically the same coordinate.

The identity

\[
\phi=2\cos(\pi/5)
\]

is exact. Geometrically it says that a length-two vector has component Phi along an axis separated by 36 degrees.
That is an **orthogonal projection**, not technically a shear. The further claim that physical time is the spatial
octave viewed through a fixed pentagonal angle remains a testable ARA conjecture. A Lorentz boost is a hyperbolic
rotation with a variable rapidity, so special relativity does not supply the fixed 36-degree law.

### Evidence calibration for the two-ruler document

- The Phi-base ablations do not support Phi as a uniquely privileged predictor base; the document's later operational
  correction is therefore the scientifically safer reading.
- The edge-free ECG scripts recover two peak-ratio families and then split them at ratio 3; their approximate fourfold
  separation is suggestive of octave structure, but the split, peak-selection rule and absence of a null/bootstrap
  prevent a universal octave law from being called confirmed.
- The summary's "0.39/0.61 across all 54 hearts" statement is not reproducible from the named duty script currently
  in the repository: `twoband_ecg_camshaft_duty_test.py` reads at most 20 records and measures envelope correlation
  and phase modulation, not the fraction of time each band dominates. This is a provenance gap, not evidence that the
  reported result is false; the original calculation/output needs locating or reconstructing.
- The solar rise/fall result is recoverable: 24 smoothed cycles give mean rise fraction 0.394 with standard deviation
  0.085. The within-cycle pairing was selected after the between-band duty failed, as the solar report itself notes.
  It is compatible with the golden-duty hypothesis but is not yet Phi-specific evidence against alternative asymmetric
  duty fractions.
- The dual-role solar improvement uses a richer per-rung model and a swept decay parameter alpha=4. It is useful model
  development, not an independent parameter-free validation of the two-ruler ontology.

The strongest new contribution of the two-ruler document is therefore structural and exact: octave scale position,
bounded ARA state and handover duty can be kept on the same geometry without being flattened into one number. Its
Phi-specific physical assignments remain hypotheses with mixed or incomplete empirical support.

## What Test 115 genuinely recovered

The following are real established features used by the script:

- water has one oxygen and two hydrogens with a bent H-O-H angle of about 104.5°;
- two similar O-H bond-dipole contributions sum to a nonzero molecular dipole;
- a simplified electron-domain description has two bonding regions and two lone-pair regions;
- a nonlinear triatomic molecule has three normal vibrational modes;
- water's hydrogen-bond network repeatedly forms and breaks;
- the two H nodes are related mainly through the central O/electronic structure rather than a direct H-H bond.

These strongly motivate the current structural notation

\[
I=\mathcal C_{1:2}(A,B_1,B_2;J_{AB_1},J_{AB_2},J_{B_1B_2},\Delta\theta).
\]

There are two classes but three nodes. The angle/relation is part of the resulting identity. This is a precise
mathematical version of “three hiding in two” and of the current Information-cubed discussion.

## Evidence audit: what the historical scores do not establish

### Test 115: `7/8` is not seven independent confirmations

Several passes are identities, textbook facts or assignments made true by the script:

- `test6_pass = True` labels the dielectric/coupler interpretation as a pass;
- the Hess-law phase-transition check tests an established accounting identity;
- `test8_pass = True` declares that the chosen three-circle picture reproduces the framework map;
- mapping three normal modes onto three ARA names is an interpretation, not a prediction;
- the triple-overlap area is explicitly approximated in the code.

The 4.54% water-angle compression versus 4.51% pi-leak proximity is numerically real, but Test 115 does not derive a
chemical mechanism connecting the two.

### Test 116: the universal molecular-angle claim failed

The original prediction does not generalise: NH3, NF3, H2S and other molecules do not share water's compression. The
script later defines an “SP3 regime” using the observed condition `bond angle > 100°` and then tests the same angles
inside that selected group. That is useful hypothesis generation, but it is outcome-conditioned rather than blind.
An independent electronic-structure classification must be fixed before angles are inspected.

### Test 116b: constructed spherical model, not independent molecular measurement

The reported narrow 5.07–5.19% range is produced by the script's spherical-cap/Voronoi construction and several
approximations. It is not presently an independently measured universal molecular packing gap. The model may be worth
formal mathematical review, but `2/2` should not be read as physical confirmation.

### Test 117: constant-gap claim is false for unequal circles

The script's law-of-cosines and sector-area formula was recomputed independently. The gap divided by the centre-triangle
area is constant only for a fixed radius configuration, not for all mutually tangent triples:

| Radii | Gap fraction |
|---|---:|
| 1 : 1 : 1 | 0.09310 |
| 1 : 1 : 0.1 | 0.03742 |
| 1 : 1 : 10 | 0.03389 |
| 1 : 0.2 : 0.05 | 0.02794 |

Thus 9.31% is the equal-circle value. The script's own constant-gap criterion is its one failed test, consistent with
the historical `4/5` score. The useful surviving result is angular: as one radius dominates, one centre-triangle angle
approaches zero. Interpreting a chosen angle threshold as dynamical “coupling viability” still requires physical data.

## The recovered log-rung rule

Test 143 contains the correct generic mathematics:

\[
T_{total}=\prod_i T_i
\quad\Longrightarrow\quad
\log T_{total}=\sum_i\log T_i.
\]

This explains why a rung coordinate is logarithmic whenever scale transfer is a chain of multiplicative local
handoffs. It does **not** fix the base or step size. A base-two octave follows only when the declared extensive
quantity doubles:

\[
E_{k+1}=2E_k
\quad\Longrightarrow\quad
\Delta k=\log_2(E_{k+1}/E_k)=1.
\]

Test 143's fitted link efficiencies, Fibonacci/perpendicular interpretation and pi-leak multiples are exploratory and
partly fitted. The multiplication-to-logarithm statement is exact; the specific ARA link constants remain empirical.

## Present interpretation

The most economical recovered geometry is:

1. local identities live on a circular/spherical phase manifold;
2. coupling depends on angular/geodesic separation, not an untyped straight perpendicular;
3. closure may be many-to-one, with water supplying a concrete 1A:2B example;
4. each completed local closure becomes a node at the next grain;
5. chained transfer factors multiply, so rung displacement is additive in log space;
6. Phi is a candidate non-repeating handover rotation, not implied by curvature, water or non-overlap alone.

## Clean next test

For the water/molecular branch:

1. classify A/B roles **before** inspecting target bond angles, using electron density, partial charge,
   electronegativity or a fixed orbital descriptor;
2. define a geodesic/hyperedge model that outputs a numerical bond angle or dipole;
3. freeze it on a training family and predict held-out molecules;
4. compare against mean, VSEPR/valence and a restrained quantum-chemistry baseline;
5. report failures without redefining the regime from the observed angle.

For the log-rung branch, select a controlled system with measured per-link transfer efficiencies and test whether the
product law predicts an unseen multi-link transfer without fitting each link to that target.

## Execution note

The archived Python scripts were inspected completely enough to audit their formulae and scoring logic. A direct rerun
was attempted, but the available Python 3.14 environment has no NumPy and no bundled scientific runtime is configured.
No packages were installed. The Test 117 gap values above were independently recomputed from the script's explicit
law-of-cosines/sector-area equations.

**Status:** `EARLY PROVENANCE RECOVERED / WATER 1:2 CURVED CLOSURE CONFIRMED AS PRIOR IDEA / GEODESIC + LOG-RUNG STRANDS LOCATED / MULTIPLICATIVE-TO-ADDITIVE AXIOMS CONDITIONALLY DERIVE LOG COORDINATE / RECIPROCAL RIDGE SYMMETRY RECOVERED / BOUNDED 0-2 LINE IDENTIFIED AS SCALED LOGIT OF CHANNEL RATIO / EXPONENTIAL ENDPOINT APPROACH EXACT / TWO-RULER DOCUMENT INTEGRATED WITH OCTAVE-STATE-HANDOVER COORDINATES TYPED / PHI MIRROR EXACT AS RATIO INVERSION / ECG DUTY PROVENANCE GAP OPEN / CIRCLE-WRAPPED LOG COORDINATE FORMALISED / UNIVERSAL BASE-RADIUS-PHYSICAL WELL REMAIN OPEN / HISTORICAL SCORES RECALIBRATED / TEST 117 CONSTANT-GAP CLAIM CORRECTED / NEW HELD-OUT TEST REQUIRED`.
