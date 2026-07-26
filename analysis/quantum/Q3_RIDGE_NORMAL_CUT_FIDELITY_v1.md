# Q3 ridge-normal quantum-output cut fidelity

**Claim ID / version:** `Q3-RNC-FID-v1`  
**Date:** 24 July 2026  
**Status:** `POST-HOC GEOMETRIC CALIBRATION ON AN ALREADY-OPEN SOURCE`

## ARA question

The corrected spherical-cut rule distinguishes two directions in a measured two-cut plane:

- for an Information-facing question, cut perpendicular to the equal-readout ridge and orient toward the
  changing class;
- retain the ridge-tangent direction as the orthogonal Phase-B/control cut.

Q3 asks whether that rule can be translated without flattening into a standard, reproducible measurement
geometry on the already-open Q2 public superconducting-qubit I/Q data.

## Mathematical translation

Within the five training hardware conditions, let the class centroids be \(\mu_g,\mu_e\) and the pooled
within-class covariance be \(\Sigma\). Whiten the two-cut plane:

\[
\mathbf z=(\mathbf x-\mathbf m)\Sigma^{-1/2},
\qquad
\mathbf m=\frac{\mu_g+\mu_e}{2}.
\]

In that whitened plane, define the Information-facing Phase-A cut as

\[
\hat{\mathbf n}_A
=
\frac{(\mu_e-\mu_g)\Sigma^{-1/2}}
{\|(\mu_e-\mu_g)\Sigma^{-1/2}\|},
\]

and define the Phase-B/control cut as its ninety-degree rotation

\[
\hat{\mathbf n}_B=(-n_{A,y},n_{A,x}).
\]

The equal-class linear decision ridge is perpendicular to \(\hat{\mathbf n}_A\), so

\[
s_A=\mathbf z\cdot\hat{\mathbf n}_A
\]

is exactly the shared-covariance linear-discriminant score up to a positive scale. The tangent score
\(s_B=\mathbf z\cdot\hat{\mathbf n}_B\) contains no training centroid difference by construction.

## ARA back-translation

- \(\hat{\mathbf n}_A\): the cut that crosses the observed ground/excited ridge most directly; the
  Information-facing direction for this question.
- \(\hat{\mathbf n}_B\): the same plane viewed along the ridge; the orthogonal control/Phase-B direction.
- the two cuts together: a decompressed account of the same I/Q point, not additional measurements.
- rotating the cut: walking around the same measured two-dimensional section of the sphere.

This test does **not** establish that I/Q are literal universal Information and Connection axes. It checks whether
the proposed cut-selection instruction maps coherently onto standard Fisher/LDA geometry.

## Evidence boundary

The Q2 numerical values and outcomes were opened before Q3 was specified. Q3 is therefore a known-source,
post-hoc calibration. It may validate the translation and prepare an untouched test, but it cannot serve as
independent confirmation of ARA or quantum ontology.

