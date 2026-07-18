# MX4 frozen protocol — Lorentz-force ↔ ARA crosswalk across particle and grid rungs

**Frozen:** 14 July 2026, before any force-channel outcome was calculated  
**Status:** `DEVELOPMENT TEST FROZEN / SOURCE STRUCTURE AUDITED / OUTCOMES UNSEEN`  
**Scope:** established-physics recovery and cross-scale translation, not a novel proof of ARA

## Question

Can the Lorentz force be represented without flattening it as a two-channel ARA relation, and does that representation remain coherent when the measurement is coarse-grained from individual particles to a field grid?

The established particle law is

\[
\underbrace{\mathbf f_i}_{\substack{\text{force on}\text{particle }i}}
=
\underbrace{q_i\mathbf E_i}_{\substack{\text{electric}\text{channel }\mathbf f_{E,i}}}
+
\underbrace{q_i(\mathbf v_i\times\mathbf B_i)}_{\substack{\text{magnetic}\text{channel }\mathbf f_{B,i}}}.
\]

Plainly: the electric field supplies one force contribution. The particle's motion crossing the magnetic field supplies another, perpendicular contribution. The measured force is their vector mixture.

The continuum law at the next coarser rung is

\[
\underbrace{\mathbf f_V}_{\substack{\text{force per}\text{volume}}}
=
\underbrace{\rho\mathbf E}_{\substack{\text{electric}\text{force density}}}
+
\underbrace{\mathbf J\times\mathbf B}_{\substack{\text{magnetic}\text{force density}}}.
\]

Plainly: after many particles are grouped into a cell, their charges become charge density and their directed motion becomes current density. The same two-channel relation should still be visible, although coarse-graining and field variation can introduce a residual.

## Public source and provenance

Source repository: <https://github.com/openPMD/openPMD-example-datasets>  
Source archive: <https://raw.githubusercontent.com/openPMD/openPMD-example-datasets/draft/legacy_datasets.tar.gz>  
License: CC0-1.0 at the source repository  
Producer recorded inside the file: PIConGPU 0.5.0  
Snapshot: iteration 200, three-dimensional Cartesian electromagnetic PIC

| Local source | Bytes | SHA-256 |
|---|---:|---|
| `legacy_datasets.tar.gz` | 8,858,128 | `5785344baf064bd96f576326b82029804191df8100817bd2953c3c82b8c67a27` |
| `simData_200.h5` | 23,023,000 | `6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5` |

The source contains all three components of \(\mathbf E\) and \(\mathbf B\), species charge densities, and 225,449 electron plus 225,280 ion particle records with position, momentum and weighting. It contains one snapshot and does not store \(\mathbf J\).

## Data-quality gate

Before physical interpretation, the implementation must verify:

1. source hashes, file shape and finite values;
2. openPMD SI conversion factors for field, charge, mass, position and macro-weighted momentum;
3. relativistic velocity from per-particle momentum;
4. Yee-grid component offsets and a declared interpolation rule;
5. species counts, fixed charge signs and positive masses/weights;
6. boundary sensitivity by reporting both all-particle and interior-only summaries;
7. the inability of a single snapshot to test observed acceleration.

Failure of any required unit or record check blocks the affected result.

## Frozen ARA coordinates

For each particle define channel magnitudes

\[
F_E=\lVert\mathbf f_E\rVert,\qquad
F_B=\lVert\mathbf f_B\rVert,
\]

the dimensional activity envelope

\[
S_F=F_E+F_B,
\]

and the 0–2 ARA mixing coordinate

\[
\underbrace{x_F}_{\substack{\text{ARA position}\text{on the force-channel axis}}}
=
\frac{2F_B}{F_E+F_B}.
\]

Plainly: \(x_F=0\) is entirely electric, \(x_F=2\) is entirely magnetic and \(x_F=1\) means equal channel magnitudes. It does **not** mean cancellation; cancellation or reinforcement depends on their direction.

Retain the directional relation

\[
\underbrace{c_F}_{\substack{\text{channel alignment}\text{or quadrant coordinate}}}
=
\cos\theta_F
=
\frac{\mathbf f_E\cdot\mathbf f_B}{F_EF_B}.
\]

The frozen reconstruction is

\[
\widehat F
=
\frac{S_F}{2}
\sqrt{(2-x_F)^2+x_F^2+2x_F(2-x_F)c_F}.
\]

Plainly: the 0–2 coordinate says how much of each channel is present, the envelope says how large the interaction is, and the angle says whether the channels reinforce, oppose or turn across one another. Those three quantities reconstruct the resultant force magnitude.

This \(S_F\) is a force-channel total in newtons. It is **not** promoted to a physical TE-ARA energy measurement. A physical TE-ARA participation test requires an independently observed change or residual energy ledger, which this single snapshot does not contain.

## Frozen tests

### MX4-L1 — particle-rung algebra and energy handover

For both species:

- interpolate \(\mathbf E\) and \(\mathbf B\) to particle positions using declared trilinear interpolation with each Yee component's recorded offset;
- compute \(\mathbf f_E\), \(\mathbf f_B\), direct \(\mathbf f\), \(x_F\), \(S_F\) and \(c_F\);
- compare \(\widehat F\) with \(\lVert\mathbf f\rVert\);
- verify that the magnetic channel does no work:

\[
\mathbf v\cdot\mathbf f_B=0,
\]

and therefore

\[
\mathbf v\cdot\mathbf f=\mathbf v\cdot\mathbf f_E=q\,\mathbf v\cdot\mathbf E.
\]

Primary numerical gates:

- relative reconstruction error \(\le 10^{-12}\) at the aggregate level;
- normalised magnetic-work leakage \(\le 10^{-12}\);
- normalised total-power identity error \(\le 10^{-12}\).

Passing MX4-L1 establishes correct translation and implementation only. Because the equations are algebraically equivalent, it is not independent evidence for a new physical law.

### MX4-L2 — particle-to-grid rung bridge

Use the same particle state to construct two independently ordered coarse-grainings:

1. **particle-first:** calculate each particle force, then deposit the forces to cell centres;
2. **field-first:** deposit \(\rho\) and \(\mathbf J\), collocate the fields, then calculate \(\rho\mathbf E+\mathbf J\times\mathbf B\).

The fixed primary implementation uses trilinear cloud-in-cell deposition and excludes one boundary cell. A quadratic-shape sensitivity run may be added, but cannot replace the primary result.

Report:

- component and vector correlation;
- NRMSE relative to the particle-first target's standard deviation;
- magnitude ratio and median angular error;
- results for total, electric and magnetic channels separately;
- residuals against field-gradient strength and cell occupancy.

Development interpretation bands, declared before outcome:

- `strong rung preservation`: vector correlation \(\ge 0.90\), NRMSE \(\le 0.50\), median angle \(\le 15^\circ\);
- `partial rung preservation`: correlation \(\ge 0.70\) but any strong criterion fails;
- `not recovered by this operator`: correlation \(<0.70\).

These are diagnostic development bands, not universal physical constants. A failure may reject the chosen coarse-graining operator without rejecting Lorentz's law or the broader ARA proposal.

### MX4-L3 — acceleration confirmation (not available here)

The genuinely independent dynamical test would compare the frozen force prediction against finite-difference particle momentum:

\[
\frac{\Delta\mathbf p_i}{\Delta t}
\stackrel{?}{=}
q_i\left(\mathbf E_i+\mathbf v_i\times\mathbf B_i\right).
\]

This dataset has only one snapshot, so MX4-L3 is predeclared `NOT RUN — MISSING SECOND TIME STATE`. It must not be inferred from MX4-L1 or MX4-L2.

## Claims permitted after this run

If successful, the strongest allowed statement is:

> On one public PIConGPU electromagnetic snapshot, the declared ARA force-channel coordinates exactly reconstructed the per-particle Lorentz resultant, preserved the electric-versus-magnetic energy distinction, and [did/did not] survive the declared particle-to-grid coarse-graining operator.

The run cannot establish that ARA derives Lorentz force, predicts new electromagnetic behaviour, or outperforms established physics.
