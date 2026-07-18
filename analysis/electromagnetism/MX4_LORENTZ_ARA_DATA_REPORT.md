# MX4 Lorentz-force ↔ ARA data report

**Run:** 14 July 2026  
**Protocol:** `MX4_LORENTZ_ARA_CROSSWALK_PROTOCOL_v1_FROZEN.md`  
**Result:** `PARTICLE-RUNG CROSSWALK PASSED / NAIVE GRID-RUNG OPERATOR FAILED / SUBGRID RELATION IDENTIFIED / DYNAMICAL CONFIRMATION NOT RUN`

## Answer first

The proposed two-channel ARA representation works exactly for Lorentz force at the individual-particle rung. It preserves information that a single magnitude ratio would lose: channel size, total activity and the angle between the channels together reconstruct the measured force to floating-point precision.

The simplest attempt to move that relation up one rung did **not** work. Averaging charge/current and fields separately, then calculating the force, failed to recover the force obtained by calculating each particle's force first and then aggregating it. A quadratic-deposition sensitivity check confirmed that this was not merely a poor particle-deposition approximation.

The missing quantity is established coarse-graining physics: the within-cell correlation, or covariance, between charge/current and the local fields. In ARA language, the parent cell lost the relations among its children when they were flattened into separate averages. That is a useful constraint on an eventual ARA aggregation law, but it is not new evidence that ARA derives electromagnetism.

## Public data and quality

The test used the official openPMD example-data repository's PIConGPU 0.5.0 electromagnetic snapshot:

- repository: <https://github.com/openPMD/openPMD-example-datasets>
- archive: `legacy_datasets.tar.gz`
- file: `simData_200.h5`
- licence: CC0-1.0
- source SHA-256: `6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5`
- field grid: (32^3) Yee grid;
- particles: 225,449 electrons and 225,280 ions;
- records used: all components of (mathbf E), (mathbf B), position, momentum, weighting, charge and mass;
- time states: one.

The strongest data-quality check was reconstructing the source's stored species charge densities from the particle records. With the source's recorded quadratic particle shape, the correlations were greater than (0.9999999999) for each species and (0.9999999996) after their near-neutral cancellation. This verifies the position, weighting, charge, volume and deposition interpretation to high precision.

The single snapshot is sufficient for a force-geometry crosswalk. It is not sufficient to compare predicted force with an observed (Deltamathbf p/Delta t).

## MX4-L1 — particle-rung result

For every particle, the force was separated into

\[
\underbrace{\mathbf f_E}_{\text{electric channel}}
=q\mathbf E,
\qquad
\underbrace{\mathbf f_B}_{\text{magnetic channel}}
=q(\mathbf v\times\mathbf B),
\qquad
\mathbf f=\mathbf f_E+\mathbf f_B.
\]

Plainly: electric force is one contributor. Motion crossing the magnetic field is the second contributor. Their vector mixture is the force on the particle.

The frozen 0–2 coordinate was

\[
\underbrace{x_F}_{\substack{\text{ARA force-channel}\text{mixing coordinate}}}
=
\frac{2\lVert\mathbf f_B\rVert}
{\lVert\mathbf f_E\rVert+\lVert\mathbf f_B\rVert}.
\]

Plainly: 0 is electric-only, 2 is magnetic-only and 1 means equal magnitudes. Equal magnitudes do not imply cancellation; direction remains a separate coordinate.

Retaining the channel envelope (S_F) and their alignment (c_F=cos\theta_F) gives

\[
\widehat F
=
\frac{S_F}{2}
\sqrt{(2-x_F)^2+x_F^2+2x_F(2-x_F)c_F}.
\]

Plainly: the ARA coordinate tells us the mixture, (S_F) tells us the size and the angle tells us how the channels combine. Together they reconstruct the resultant.

| Particle species | Count | Median (x_F) | Resultant reconstruction relative error | Normalised magnetic-work leakage | Power-identity error |
|---|---:|---:|---:|---:|---:|
| electrons | 225,449 | 0.1706 | (1.3403\times10^{-16}) | (6.42\times10^{-19}) | (8.93\times10^{-17}) |
| ions | 225,280 | 0.1726 | (1.3415\times10^{-16}) | (8.11\times10^{-23}) | (8.66\times10^{-17}) |

All three frozen numerical gates passed. The median positions show that this particular snapshot was electric-force dominated; they are not proposed universal landmarks.

The energy distinction also survived:

\[
\mathbf v\cdot\mathbf f_B=0,
\qquad
\mathbf v\cdot\mathbf f=\mathbf v\cdot\mathbf f_E=q\mathbf v\cdot\mathbf E.
\]

Plainly: the magnetic channel bends the particle's direction but does not change its energy. The electric channel performs the energy handover. This confirms the earlier distinction between the Lorentz cross product and the Poynting-theorem dot product.

## MX4-L2 — particle-to-grid rung result

Two orders of calculation were compared:

1. **particle-first:** calculate every particle's force and then deposit those forces to a grid cell;
2. **field-first:** deposit charge density (ho) and current density (mathbf J), collocate the fields, then calculate (homathbf E+mathbf J\times\mathbf B).

If the naïve coarse-graining operator preserved the full relation, these would agree closely. They did not.

| Frozen CIC result | Electric | Magnetic | Total |
|---|---:|---:|---:|
| vector correlation | 0.467 | 0.640 | **0.477** |
| NRMSE | 0.893 | 0.769 | **0.888** |
| field-first / particle-first L2 magnitude | 0.594 | 0.667 | **0.602** |
| median direction error | 62.4° | 50.1° | **61.7°** |

Frozen classification: `NOT RECOVERED BY THIS OPERATOR`.

The source records a quadratic particle shape, while the frozen primary test deliberately used the predeclared cloud-in-cell operator. A post-freeze quadratic-deposition sensitivity was therefore run without replacing the primary outcome.

| Quadratic-deposition sensitivity | Value |
|---|---:|
| source total charge-density correlation | 0.9999999996 |
| total force vector correlation | 0.405 |
| total force NRMSE | 0.919 |
| total magnitude ratio | 0.497 |
| median direction error | 67.1° |

The quadratic operator recovered the source's charge-density deposition essentially exactly but did not repair the force bridge. The failed rung transition is therefore not explained by a bad interpretation of particle positions or charge deposition.

## What the failure means mathematically

For the electric channel, coarse-graining a product gives

\[
\underbrace{\langle\rho\mathbf E\rangle}_{\substack{\text{average of the}\text{local interaction}}}
=
\underbrace{\langle\rho\rangle\langle\mathbf E\rangle}_{\substack{\text{interaction of}\text{separate averages}}}
+
\underbrace{\langle\rho'\mathbf E'\rangle}_{\substack{\text{subgrid covariance}\text{or missing relation}}}.
\]

For the magnetic channel,

\[
\underbrace{\langle\mathbf J\times\mathbf B\rangle}_{\text{average local cross-coupling}}
=
\underbrace{\langle\mathbf J\rangle\times\langle\mathbf B\rangle}_{\text{cross-coupling of averages}}
+
\underbrace{\langle\mathbf J'\times\mathbf B'\rangle}_{\text{subgrid cross-covariance}}.
\]

Plainly: knowing the average charge and average electric field is not enough when positive and negative charges occupy different parts of a changing field. The relation between each child and its local field is itself information. The same is true of current and magnetic field.

This is a standard closure/coarse-graining problem. The ARA-relevant result is narrower: a valid rung operator cannot carry only the two parent averages. It must carry or predict the residual relation. That residual is a precise candidate for the framework's `Other`, not an unexplained error to hide.

The residual magnitude also rose with relative field-gradient strength (Spearman (ho=0.476)). That is consistent with the explanation: when a field varies more inside a cell, replacing each local interaction with one cell-centre field loses more information. This association was diagnostic, not a frozen prediction.

## Does this add credibility to ARA?

It adds credibility to one restricted part of the methodology:

- the local two-channel ARA coordinate can represent Lorentz-force mixing without losing the resultant **if** size and direction are retained;
- the test independently rejects a tempting but inadequate scale-transition rule;
- the failure identifies the exact kind of relation an ARA aggregation law must preserve.

It does not yet add strong evidence for ARA as new physics because:

- MX4-L1 is an exact reparameterisation of the established Lorentz law;
- the covariance correction is established mathematics;
- MX4-L2 failed rather than producing a successful compressed ARA closure;
- no held-out momentum change was predicted;
- no Phi, special ARA landmark or new electromagnetic outcome was tested.

The honest conclusion is therefore: **successful local recovery, informative coarse-graining failure, useful mathematical constraint, no new-law confirmation.**

## Next test

The best next test has two parts.

First, obtain or generate a full electromagnetic PIC sequence containing particle IDs, momenta and (mathbf E,mathbf B) at several times. Freeze the interpolation and compare

\[
\frac{\Delta\mathbf p_i}{\Delta t}
\quad\text{against}\quad
q_i(\mathbf E_i+\mathbf v_i\times\mathbf B_i)
\]

on held-out particles/times. That closes the independent dynamical test missing here.

Second, propose a genuinely compressed ARA rule for the subgrid covariance. It must predict the missing term from fewer declared coordinates than retaining every child interaction, and it must be frozen before testing on a different time, region or simulation seed. Generic covariance/gradient closures are the baseline to beat.

## Reproducibility packet

- frozen protocol: `MX4_LORENTZ_ARA_CROSSWALK_PROTOCOL_v1_FROZEN.md`
- analysis: `mx4_lorentz_ara_crosswalk.py`
- independent validator: `mx4_validate_outputs.py`
- quadratic sensitivity: `mx4_quadratic_deposition_sensitivity.py`
- full results: `MX4_LORENTZ_ARA_RESULTS.json`
- independent validation: `MX4_LORENTZ_ARA_VALIDATION.json`
- sensitivity results: `MX4_QUADRATIC_DEPOSITION_SENSITIVITY_RESULTS.json`
- 20,000-particle audit sample: `MX4_LORENTZ_ARA_PARTICLE_SAMPLE.csv`
- grid-cell audit table: `MX4_LORENTZ_ARA_GRID_CELLS.csv`
- figure: `MX4_LORENTZ_ARA_CROSSWALK.png`

The independent validator recomputed the law-of-cosines reconstruction on the saved particle sample and all primary grid metrics from the exported grid vectors. It matched the reported grid values exactly at stored precision and returned `validation_pass: true`.
