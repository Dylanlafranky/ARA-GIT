# MX5 Child-ARA / TE-ARA Closure Test — Protocol v1 (Frozen)

**Frozen:** 2026-07-14, before MX5 outcomes were calculated  
**Status:** post-MX4 development follow-up; not an independent confirmation test  
**Source:** the same hash-locked public PIConGPU/openPMD snapshot used by MX4

## Why this test exists

MX4 recovered the Lorentz relation exactly at the particle rung but did not preserve it after separately coarse-graining particles, charge/current and fields.  Its total grid-force comparison was:

- vector correlation: `0.4770623592`;
- NRMSE by target standard deviation: `0.8878462481`;
- median angular error: `61.67518109 deg`.

The proposed missing term is the child-scale relation discarded by the flattened product:

\[
\langle \rho\mathbf E\rangle
=\langle\rho\rangle\langle\mathbf E\rangle
+\langle\rho'\mathbf E'\rangle,
\qquad
\langle\mathbf J\times\mathbf B\rangle
=\langle\mathbf J\rangle\times\langle\mathbf B\rangle
+\text{cross-scale covariance}.
\]

MX5 tests three versions in increasing compression.  Versions A and B are identity checks.  Version C is the only non-trivial compact recovery test.

## Fixed data and grain

- File: `simData_200.h5`
- Expected SHA-256: `6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5`
- Iteration: `200`
- Shape: `32 x 32 x 32`
- Species: electrons and ions
- Field interpolation: the recorded Yee offsets with trilinear interpolation
- Parent grid: integer grid points, cloud-in-cell (CIC) child deposition
- Scoring mask: one-cell interior with non-zero CIC occupancy
- No fitted coefficients and no outcome-dependent tuning

The source records a quadratic particle shape.  CIC is retained here to isolate the closure question against the exact MX4 baseline.  This is a declared operator choice and a limitation.

## Common quantities

For particle `i`:

\[
\mathbf f_{E,i}=q_i\mathbf E_i,
\qquad
\mathbf f_{B,i}=q_i\mathbf v_i\times\mathbf B_i,
\qquad
S_i=|\mathbf f_{E,i}|+|\mathbf f_{B,i}|,
\]

\[
x_i=\frac{2|\mathbf f_{B,i}|}{S_i}.
\]

The particle-first target at parent node `g` is

\[
\mathbf F_g^{\rm child}
=\frac{1}{V_g}\sum_i W_{ig}w_i
(\mathbf f_{E,i}+\mathbf f_{B,i}).
\]

The flattened parent estimate is

\[
\mathbf F_g^{\rm flat}
=\bar\rho_g\bar{\mathbf E}_g
+\bar{\mathbf J}_g\times\bar{\mathbf B}_g.
\]

## Version A — exact child-ARA reassembly

Reassemble each particle from its two ARA channels before deposition:

\[
\mathbf F_g^{\rm ARA-child}
=\frac{1}{V_g}\sum_i W_{ig}w_i\frac{S_i}{2}
\left[(2-x_i)\hat{\mathbf u}_{E,i}
+x_i\hat{\mathbf u}_{B,i}\right].
\]

This must equal `F_child` apart from floating-point error.  Pass gate:

- relative L2 error `<= 1e-12`.

**Interpretation ceiling:** passing validates decompression and reassembly only.  It cannot establish a new physical law because the same information is retained.

## Version B — parent plus exact Other

Define the child-scale term lost by parent flattening:

\[
\mathbf O_{E,g}=\mathbf F_{E,g}^{\rm child}-\bar\rho_g\bar{\mathbf E}_g,
\qquad
\mathbf O_{B,g}=\mathbf F_{B,g}^{\rm child}-\bar{\mathbf J}_g\times\bar{\mathbf B}_g,
\]

\[
\mathbf F_g^{\rm recovered}
=\mathbf F_g^{\rm flat}+\mathbf O_{E,g}+\mathbf O_{B,g}.
\]

Pass gate:

- relative L2 error `<= 1e-12`.

This is also an identity check.  Its purpose is to expose and measure the missing relation, not to predict it.

### TE-ARA-style force-identity diagnostics

These diagnostics are dimensionless force/activity coordinates.  They are **not joules** and are not asserted to be a universal TE-ARA energy measure.

Child activity:

\[
A_g=\frac{1}{V_g}\sum_i W_{ig}w_iS_i.
\]

Coherent child participation:

\[
T^{F}_{g}=\frac{2|\mathbf F_g^{\rm child}|}{A_g}\in[0,2].
\]

`0` means nearly complete vector cancellation at the parent grain; `2` means the child forces are almost fully aligned.

Magnitude-only Parent/Other coordinate:

\[
x_{O,g}=\frac{2|\mathbf O_g|}
{|\mathbf F_g^{\rm flat}|+|\mathbf O_g|}.
\]

`0` means the flattened parent magnitude dominates, `1` means equal magnitudes, and `2` means Other dominates.  Because vectors can oppose, this is not an energy percentage and does not add linearly to the observed resultant.

## Version C — compressed first-moment / field-gradient closure

Retain only the first positional child moments at each parent node:

\[
P_{\rho,a,g}
=\frac{1}{V_g}\sum_i W_{ig}q_iw_i\,\delta r_{ig,a},
\]

\[
\mathbf M_{J,a,g}
=\frac{1}{V_g}\sum_i W_{ig}q_iw_i\mathbf v_i\,\delta r_{ig,a}.
\]

Predict the missing term from local field gradients:

\[
\widehat{\mathbf O}^{(1)}_{E,g}
=\sum_a P_{\rho,a,g}\,\partial_a\bar{\mathbf E}_g,
\qquad
\widehat{\mathbf O}^{(1)}_{B,g}
=\sum_a \mathbf M_{J,a,g}\times\partial_a\bar{\mathbf B}_g,
\]

\[
\widehat{\mathbf F}^{(1)}_g
=\mathbf F_g^{\rm flat}
+\widehat{\mathbf O}^{(1)}_{E,g}
+\widehat{\mathbf O}^{(1)}_{B,g}.
\]

This is a standard Taylor/moment closure expressed in the ARA child/parent/Other bookkeeping.  It contains no fitted coefficients.

### Frozen outcome classes

Version C is a **useful compact recovery** only if all three hold:

- total vector correlation `>= 0.70`;
- total NRMSE `<= 0.70`;
- median angular error `<= 45 deg`;
- and each metric is better than the frozen MX4 flat-parent baseline.

It is **partial compact recovery** if at least two of correlation, NRMSE and median angle improve over MX4 by at least 5% in their favourable direction.  Otherwise it is **not recovered by this first-moment closure**.

## Required reporting

Report:

1. source hash and data-quality checks;
2. Version A and B identity-gate errors;
3. Version C total, electric and magnetic metrics;
4. direct comparison with the frozen MX4 parent baseline;
5. distributions of `T^F` and `x_O`, including the fraction with `x_O > 1`;
6. lower- and upper-z half sensitivity;
7. limitations: one snapshot, one simulation, no observed acceleration, CIC mismatch to the recorded quadratic particle shape.

## Claim boundary

A or B passing says the bookkeeping is internally correct.  C succeeding would show that a compact child-aware moment closure retains materially more of the Lorentz structure than the flat parent operator on this snapshot.  None of these outcomes alone proves universal ARA geometry or new plasma physics.
