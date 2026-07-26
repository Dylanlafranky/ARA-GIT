# Q6B physical CHSH coherence-ladder fidelity

**Claim ID / version:** `Q6B-PHYSICAL-CHSH-FID-v1`  
**Date:** 24 July 2026  
**Status at freeze:** `REMEDIAL CALIBRATION AFTER Q6 RAW-TENSOR PHYSICALITY FAILURE`

## Why Q6B is required

Q6's frozen raw-tensor ladder passed its sixteen geometric gates, but the `Phi-minus` point estimate gave
\(S_{\max}=2.88579\), above the quantum Tsirelson limit \(2\sqrt2\approx2.82843\).

The raw Pauli expectations were measured in separate tomography settings. Finite sampling, state-preparation and
measurement error can make their unconstrained linear inversion non-positive. The Horodecki CHSH theorem applies
to a physical two-qubit density matrix, so Q6's raw result cannot be presented as a valid CHSH measurement.

## Frozen remediation

For each state:

1. linearly reconstruct
   \[
   \rho_{\mathrm{lin}}=\frac14\sum_{i,j\in\{I,X,Y,Z\}}
   \langle ij\rangle\,\sigma_i\otimes\sigma_j;
   \]
2. Hermitize it;
3. diagonalize it;
4. project its four eigenvalues onto the probability simplex, preserving the eigenvectors;
5. reconstruct the nearest positive-semidefinite, unit-trace matrix under this declared eigenvalue projection;
6. recompute the full correlation tensor and \(S_{\max}\).

This is a transparent physicality projection, not the authors' maximum-likelihood reconstruction and not a
claim of optimal tomography.

## ARA fidelity

The ARA question remains unchanged:

- coherent Bell parents should retain several strong relational cuts and cross the CHSH boundary;
- equal incoherent Bell-pair mixtures should retain one classical relation axis but not cross it;
- the equal four-state mixture should retain no strong relation axis.

Q6B tests whether that ladder survives the required physical-state constraint. A failure is evidence that the raw
ARA ladder did not survive a physically admissible quantum reconstruction.

