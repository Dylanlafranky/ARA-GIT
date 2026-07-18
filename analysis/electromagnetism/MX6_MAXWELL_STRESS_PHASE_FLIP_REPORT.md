# MX6 Maxwell Stress / Paired Phase — Public-Data Report

**Run:** 15 July 2026  
**Outcome:** exact Maxwell crosswalk recovered; public-field geometry measured; independent validation passed  
**Evidence tier:** established Maxwell identities plus descriptive public data, not independent confirmation of ARA

## Answer first

The proposed paired reading has a precise Maxwellian home.

On all 32,768 cells of a hash-locked public PIConGPU electromagnetic snapshot,

\[
(\mathbf E,\mathbf B)\mapsto(-\mathbf E,-\mathbf B)
\]

left both the Poynting vector and Maxwell stress tensor unchanged at reported relative L2 error `0.0`. Flipping only
one field also left stress unchanged, but reversed the Poynting vector at error `0.0`.

In ARA language: both signed child orientations must swap together for the directed parent relation to persist. The
parent direction is the bilinear cross-relation \(\mathbf E\times\mathbf B\), not either child alone. Maxwell stress
cannot distinguish a paired from a one-channel flip because it is separately quadratic in E and B; signed flow can.

The strongest exact geometric result is

\[
\boxed{
\mathbf T(\mathbf E\times\mathbf B)
=-u(\mathbf E\times\mathbf B)
},
\qquad
u=\frac{\epsilon_0E^2}{2}+\frac{B^2}{2\mu_0}.
\]

Thus, whenever \(\mathbf E\times\mathbf B\ne0\), the field-pair's flow direction is exactly the minimum-stress
eigen-direction. Across the public grid, the largest numerical angular discrepancy was only
`2.4148e-6 degrees`.

This does **not** establish temporal swapping: the source contains one time snapshot. It numerically recovers the
Maxwell geometry that the ARA interpretation must match.

## Public source and protocol

The source is the openPMD example repository's `legacy_datasets.tar.gz`, produced with PIConGPU. The repository is
public and CC0-licensed.

- local file: `simData_200.h5`;
- SHA-256: `6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5`;
- iteration: `200`;
- time: `3.58e-14 s`;
- field shape: `32 x 32 x 32`;
- components: all three E and all three B components;
- field layout: Yee grid, linearly collocated using the recorded component offsets;
- fitting: none.

The thresholds, transformations, controls and claim ceiling were frozen before MX6 outcomes were calculated in
`MX6_MAXWELL_STRESS_PHASE_FLIP_PROTOCOL_v1_FROZEN.md`.

## 1. Paired versus one-channel phase flips

The quantities tested were

\[
\mathbf S=\frac{1}{\mu_0}\mathbf E\times\mathbf B,
\]

\[
T_{ij}=\epsilon_0\left(E_iE_j-\frac12\delta_{ij}E^2\right)
+\frac1{\mu_0}\left(B_iB_j-\frac12\delta_{ij}B^2\right).
\]

| Intervention | Stress target | Relative L2 error | Poynting target | Relative L2 error |
|---|---:|---:|---:|---:|
| `E -> -E`, `B -> -B` | same | `0.0` | same | `0.0` |
| `E -> -E` only | same | `0.0` | reversed | `0.0` |
| `B -> -B` only | same | `0.0` | reversed | `0.0` |

### Plain explanation

Stress depends on E multiplied by E and B multiplied by B, so changing a sign twice removes the sign. Flow depends
on E crossed with B. Changing both signs again removes the two negatives, but changing only one reverses the result.
This is the numerical version of “each controls one signed direction, and both must swap for the larger identity to
keep its direction.” It is exact Maxwell algebra, not a fitted ARA pattern.

## 2. Why the cross-relation is an exact stress axis

Let \(\mathbf n=\mathbf E\times\mathbf B\). Because \(\mathbf n\) is perpendicular to both fields,

\[
\mathbf E\cdot\mathbf n=0,
\qquad
\mathbf B\cdot\mathbf n=0.
\]

Applying the tensor gives

\[
\mathbf T\mathbf n
=\epsilon_0\left[\mathbf E(\mathbf E\cdot\mathbf n)-\frac12E^2\mathbf n\right]
+\frac1{\mu_0}\left[\mathbf B(\mathbf B\cdot\mathbf n)-\frac12B^2\mathbf n\right]
=-u\mathbf n.
\]

This is why the public-data alignment was essentially exact in both null-like and non-null cells. It is not a
special empirical feature of the selected 686 null-like cells; it is a general Maxwell identity whenever the cross
product is defined and nonzero.

### Plain explanation

E and B jointly define a third direction: the direction perpendicular to both. The stress tensor gives that third
direction a definite pressure/tension value, `-u`. This is unusually close to the proposed ARA “informative third”:
two signed identities and their relation produce a measurable parent direction. The safe scientific wording is that
ARA recognises and cleanly re-expresses a known tensor identity here.

## 3. The radiative/perpendicular sector is special, not universal

The frozen null diagnostics were

\[
i_1=\frac{|E^2-c^2B^2|}{E^2+c^2B^2},
\qquad
i_2=\frac{2c|\mathbf E\cdot\mathbf B|}{E^2+c^2B^2}.
\]

Both must be small for a field pair to be plane-wave/null-like. The sensitivity results were:

| Joint threshold | Null-like cells | Fraction of active cells |
|---:|---:|---:|
| `0.05` | 191 | 0.5829% |
| `0.10` (primary) | 686 | 2.0935% |
| `0.20` | 2,145 | 6.5460% |

At the primary threshold:

| Diagnostic | Null-like median | Other active-cell median |
|---|---:|---:|
| `|cos(E,B)|` | 0.04378 | 0.32232 |
| `c|B|/|E|` | 0.98698 | 0.44599 |

The null-like values are necessarily near perpendicular and balanced because those properties define the frozen
null rule. The non-circular data result is their prevalence in this source: only about 2.09% of its cells satisfy the
primary joint rule.

### Plain explanation

The public plasma does contain the neat perpendicular, equally scaled E/B geometry, but it is a small sector of this
snapshot. The broader statement “E and B form one parent relation” works generally through the tensor and cross
product. The narrower picture “E and B are perpendicular and balanced” belongs to traveling radiation, not every
electromagnetic situation.

## 4. Direction survives the scalar-energy compression

For each tensor, MX6 measured normalized off-diagonal content in the fixed laboratory axes:

\[
q_{\rm shear}=\frac{\sqrt{2(T_{xy}^2+T_{xz}^2+T_{yz}^2)}}{\|\mathbf T\|_F}.
\]

Median values were:

- total stress: `0.68661`;
- electric child stress: `0.73642`;
- magnetic child stress: `0.49774`.

These numbers show that reducing the field to one scalar energy density discards substantial orientation
information in this chosen coordinate system. Off-diagonal content is not itself rotation invariant, so MX6 also
rotated every vector by a fixed proper 3D rotation:

\[
\mathbf T(R\mathbf E,R\mathbf B)=R\mathbf T(\mathbf E,\mathbf B)R^\mathsf T.
\]

- tensor-covariance relative error: `2.9508e-16`;
- eigenvalue-invariance relative error: `4.0388e-16`.

### Plain explanation

The total amount of field energy is only one number. The tensor also says which directions are being pulled, pushed
or sheared. Rotating the measuring axes changes the displayed components but not the physical tensor relation. This
supports keeping ARA direction, projection and measurement frame explicit; it does not by itself prove fractal
recursion.

## 5. Controls

The analytic controls prevent one field picture from being generalized beyond its domain.

- **Plane wave:** E and B are perpendicular and balanced; flux is nonzero and follows the minimum-stress axis.
- **Capacitor-like field:** B and Poynting flow are zero, but electric stress is nonzero.
- **Parallel E and B:** the fields are maximally non-perpendicular and Poynting flow is zero, while Maxwell stress is
  still well defined.

All frozen control checks passed.

## ARA interpretation and evidence boundary

The registered crosswalk is

\[
\underbrace{(\mathbf E,\mathbf B)}_{\substack{\text{two signed child}\text{field occurrences}}}
\longrightarrow
\underbrace{\mathbf E\times\mathbf B}_{\substack{\text{directed coupling relation}\text{informative third}}}
\longrightarrow
\underbrace{(\mathbf S,\mathbf T)}_{\substack{\text{parent flow and}\text{stress identity}}}.
\]

The same E/B children may be decomposed further only where a dataset resolves additional temporal, spectral or
spatial structure. MX6 shows compatibility with nested ARA bookkeeping; it does not demonstrate scale invariance or
the same transition law at multiple rungs.

The result adds credibility in the limited but useful **recovery** sense: ARA maintained its declared two-child plus
relation geometry through a nontrivial vector/tensor law and correctly required measurement scale and direction to
remain explicit. It is not independent evidence for a new law because Maxwell already guarantees the exact results.

The next clean test requires time-resolved public E and B fields. Before reading the outcomes, freeze a radiative
region and test whether observed half-cycle sign reversals occur jointly while Poynting direction and stress persist,
with standing-wave and non-radiative regions as controls. A specifically novel ARA test would additionally need a
predeclared cross-rung or coupling prediction not already implied by Maxwell's equations.

## Reproducibility packet

- protocol: `MX6_MAXWELL_STRESS_PHASE_FLIP_PROTOCOL_v1_FROZEN.md`;
- primary code: `mx6_maxwell_stress_phase_flip.py`;
- independent validator: `mx6_validate_outputs.py`;
- executed notebook: `MX6_MAXWELL_STRESS_PHASE_FLIP_NOTEBOOK.ipynb`;
- cell export: `MX6_MAXWELL_STRESS_PHASE_FLIP_CELLS.csv`;
- results: `MX6_MAXWELL_STRESS_PHASE_FLIP_RESULTS.json`;
- validation: `MX6_MAXWELL_STRESS_PHASE_FLIP_VALIDATION.json`;
- notebook validation: `MX6_NOTEBOOK_EXECUTION_VALIDATION.json`;
- figure: `MX6_MAXWELL_STRESS_PHASE_FLIP.png`.

Both the independent arithmetic validation and top-to-bottom notebook execution passed.

