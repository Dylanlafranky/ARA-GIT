# Q9 Information³ Bell completion fidelity

**Claim ID / version:** `Q9-INFORMATION3-BELL-COMPLETION-FID-v1`  
**Date:** 24 July 2026  
**Status at freeze:** `POST-OUTCOME COMPLETION TEST ON OPEN Q7/Q8 DATA`

## Dylan's instruction being translated

Fill the unresolved quantum structure using the Information³ lock:

1. two children;
2. their relation;
3. the parent identity produced by that closure.

This must be tested without silently reading the deliberately hidden child value.

## Two nested locks

### Whole-state lock

For any two-qubit density matrix:

\[
\rho
=\frac14\left[
I\otimes I
+\mathbf a\cdot\boldsymbol\sigma\otimes I
+I\otimes\mathbf b\cdot\boldsymbol\sigma
+\sum_{ij}T_{ij}\sigma_i\otimes\sigma_j
\right].
\]

Here \(\mathbf a\) is Child A, \(\mathbf b\) is Child B, and \(T\) is their relation. This is the exact
standard-quantum form of the proposed Information³ lock at this rung.

### Bell relation-plane lock

For the Bell-family phase relation:

\[
C=u+iv,\qquad R=|C|.
\]

Hide \(v\). Supply:

- the visible perpendicular partner \(u\);
- the parent transverse radius \(R_s\);
- neighbouring time direction to choose between the two mirror signs.

Then:

\[
|v|=\sqrt{\max(0,R_s^2-u^2)}.
\]

This is a data-completion test, not a forward forecast. Both temporal neighbours are permitted for an interior
missing value; endpoints are excluded.

## Meaning of unresolved structure

The state-level lock will split measured information into:

\[
I_A=\lVert\mathbf a\rVert^2,\qquad
I_B=\lVert\mathbf b\rVert^2,\qquad
I_{AB}=\lVert T\rVert_F^2.
\]

The exact identity

\[
4\operatorname{Tr}(\rho^2)-1=I_A+I_B+I_{AB}
\]

separates measured child information from measured relation information. Relative to a pure two-qubit state,

\[
I_{\rm unresolved}=3-(I_A+I_B+I_{AB})=4(1-\operatorname{Tr}\rho^2).
\]

This unresolved term can arise from environmental entanglement, classical mixing, preparation/readout
limitations or physical projection. It is not automatically a coherent perpendicular environmental wave.

