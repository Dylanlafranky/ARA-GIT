# MX6 Maxwell-Stress / Paired-Phase Test — Protocol v1 (Frozen)

**Frozen:** 2026-07-15, before MX6 outcomes were calculated  
**Status:** public-data Maxwell recovery/crosswalk; not an independent confirmation of ARA  
**Source:** the same hash-locked public PIConGPU/openPMD snapshot used by MX4 and MX5

## Question

The ARA reading under test is:

1. electric and magnetic fields can each be treated as a complete signed phase occurrence;
2. in the radiative sector their parent identity is cross-aligned and survives the joint half-cycle flip
   \((\mathbf E,\mathbf B)\mapsto(-\mathbf E,-\mathbf B)\);
3. the Maxwell stress tensor retains directional structure that a scalar energy total would flatten.

This packet separates exact Maxwell identities from empirical properties of the public field snapshot.

## Fixed data and grain

- File: `simData_200.h5`
- Expected SHA-256: `6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5`
- Public repository: `https://github.com/openPMD/openPMD-example-datasets`
- Producer: PIConGPU 0.5.0
- License: CC0-1.0
- Iteration: `200`
- Shape: `32 x 32 x 32`
- Field grain: all six Yee-grid components, linearly collocated to integer grid points using their recorded offsets
- Snapshot count: one
- No fitted coefficients and no outcome-dependent tuning

Because only one time is present, MX6 cannot observe an actual temporal half-cycle. The sign transformations are algebraic interventions applied to measured field vectors.

## Maxwell quantities

Let

\[
u_E=\frac{\epsilon_0}{2}|\mathbf E|^2,
\qquad
u_B=\frac{1}{2\mu_0}|\mathbf B|^2,
\qquad
\mathbf S=\frac{1}{\mu_0}\mathbf E\times\mathbf B,
\]

and

\[
T_{ij}=\epsilon_0\left(E_iE_j-\frac12\delta_{ij}|\mathbf E|^2\right)
+\frac{1}{\mu_0}\left(B_iB_j-\frac12\delta_{ij}|\mathbf B|^2\right).
\]

The tensor is decomposed as \(\mathbf T=\mathbf T_E+\mathbf T_B\).

## Part A — exact transformation calibration

Evaluate every measured field cell under:

1. **paired flip:** \((-\mathbf E,-\mathbf B)\);
2. **electric-only flip:** \((-\mathbf E,\mathbf B)\);
3. **magnetic-only flip:** \((\mathbf E,-\mathbf B)\).

Frozen expectations:

| Intervention | Maxwell stress | Poynting vector |
|---|---:|---:|
| paired flip | unchanged | unchanged |
| E-only flip | unchanged | reversed |
| B-only flip | unchanged | reversed |

Pass gate for each equality: relative L2 error `<= 1e-12`.

These are deterministic identities. Passing verifies the implementation and demonstrates that stress alone cannot distinguish paired from unpaired flips; the signed cross-product channel is required.

## Part B — radiative/null geometry in the public snapshot

For cells with both fields above a fixed numerical activity floor, define

\[
i_1=\frac{\left||\mathbf E|^2-c^2|\mathbf B|^2\right|}
{|\mathbf E|^2+c^2|\mathbf B|^2},
\qquad
i_2=\frac{2c|\mathbf E\cdot\mathbf B|}
{|\mathbf E|^2+c^2|\mathbf B|^2}.
\]

The activity rule is `|E| > 1e-12 max(|E|)` and `c|B| > 1e-12 max(c|B|)` on this snapshot. The primary **radiative/null-like** rule is `i1 <= 0.10` and `i2 <= 0.10`. Sensitivity is reported at thresholds `0.05`, `0.10`, and `0.20` without selecting among them after inspection.

Fixed diagnostics:

- perpendicularity error: \(|\cos\theta_{EB}|\);
- impedance balance: \(c|\mathbf B|/|\mathbf E|\);
- alignment between \(\mathbf S\) and the eigenvector of the minimum eigenvalue of \(\mathbf T\), using an unsigned angle in `[0, 90] deg`;
- the same summaries for non-null active cells.

This part is descriptive. No minimum null-like fraction is a pass gate because the source was not selected as a pure plane-wave experiment.

## Part C — directional information beyond a scalar total

Define the normalized off-diagonal content

\[
q_{\rm shear}(\mathbf T)=
\frac{\sqrt{2(T_{xy}^2+T_{xz}^2+T_{yz}^2)}}{\|\mathbf T\|_F}.
\]

Report it for total, electric-only, and magnetic-only stress. Also apply a fixed proper rotation to the measured vectors and test

\[
\mathbf T(R\mathbf E,R\mathbf B)=R\mathbf T(\mathbf E,\mathbf B)R^\mathsf T.
\]

Pass gates:

- tensor covariance relative L2 error `<= 1e-12`;
- stress eigenvalue invariance relative L2 error `<= 1e-12`.

Off-diagonal content is coordinate dependent; eigenvalues and the covariance test prevent it being misread as a new invariant.

## Analytic controls

Three fixed controls accompany the public data:

1. plane wave: \(\mathbf E=(E_0,0,0)\), \(\mathbf B=(0,E_0/c,0)\);
2. capacitor-like field: \(\mathbf E=(E_0,0,0)\), \(\mathbf B=0\);
3. parallel fields: \(\mathbf E=(E_0,0,0)\), \(\mathbf B=(E_0/c,0,0)\).

They establish respectively: the special null/radiative sector, electric stress without flux, and a valid non-perpendicular Maxwell configuration.

## Claim boundary

MX6 may support these statements:

- the paired half-cycle reading is exactly compatible with Maxwell's quadratic stress and bilinear energy-flow quantities;
- a public plasma snapshot contains measurable radiative-like and non-radiative field geometries that the ARA vocabulary must keep distinct;
- tensor decomposition preserves direction and child-channel information hidden by a scalar energy total.

MX6 may **not** claim:

- that the public snapshot observed an E/B phase swap through time;
- that E and B are universally perpendicular;
- that Maxwell's equations were predicted from ARA;
- that exact algebraic identities are independent evidence for a new physical law;
- that the ARA ontology of “two complete occurrences forming a parent identity” has thereby been uniquely established.
