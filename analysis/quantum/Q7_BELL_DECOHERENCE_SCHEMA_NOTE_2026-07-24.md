# Q7 schema correction note

**Date:** 24 July 2026  
**Applies to:** `Q7-BELL-DECOHERENCE-v1`

The frozen protocol described each sixteen-number source cell as a Pauli-expectation vector. The first execution
showed that every initial singular value was approximately `0.25`, inconsistent with both the published Bell
states and the source's aggregate norm.

Direct schema inspection gave

\[
\min c_{II}=0.24999999999999994,
\qquad
\max c_{II}=0.25000000000000006.
\]

Therefore the file stores the coefficients in

\[
\rho=\sum_{ij}c_{ij}\,\sigma_i\otimes\sigma_j,
\]

while the reconstruction code expects

\[
\rho=\frac14\sum_{ij}\langle ij\rangle\,\sigma_i\otimes\sigma_j.
\]

The exact bridge is

\[
\boxed{\langle ij\rangle=4c_{ij}}.
\]

This is a source-unit correction, not an outcome-dependent parameter. No registered threshold, expected
transition, target split or gate changed. The frozen protocol file and its SHA-256 remain untouched.

