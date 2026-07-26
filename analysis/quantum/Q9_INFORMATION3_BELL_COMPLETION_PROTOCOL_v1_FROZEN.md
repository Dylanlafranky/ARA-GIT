# Frozen protocol — Q9 Information³ Bell completion

**Protocol ID:** `Q9-INFORMATION3-BELL-COMPLETION-v1`  
**Ledger ID:** `T268`  
**Frozen:** 24 July 2026, after Q8 outcomes were open but before calculating the Q9 purity allocation or signed
masked-child completion scores  
**Test class:** post-outcome exact-closure and masked-data completion test  
**Source:** the `88` checksum-pinned public physical Bell trajectories used by Q7/Q8

## Inputs

Inherit Q7's source hashes, exact coefficient conversion, wait ordering, physical density-matrix reconstruction,
Bell-state labels and Q8 family-coordinate definitions.

## Part A — exact Information³ state lock

For each record calculate:

\[
a_i=\langle\sigma_i\otimes I\rangle,\qquad
b_j=\langle I\otimes\sigma_j\rangle,\qquad
T_{ij}=\langle\sigma_i\otimes\sigma_j\rangle.
\]

Reconstruct:

\[
\rho_{I^3}
=\frac14\left[
I\otimes I
+\sum_i a_i\sigma_i\otimes I
+\sum_j b_j I\otimes\sigma_j
+\sum_{ij}T_{ij}\sigma_i\otimes\sigma_j
\right].
\]

Calculate:

\[
I_A=\lVert\mathbf a\rVert^2,\quad
I_B=\lVert\mathbf b\rVert^2,\quad
I_{AB}=\lVert T\rVert_F^2,\quad
I_{\rm unresolved}=3-I_A-I_B-I_{AB}.
\]

Verify independently:

\[
I_A+I_B+I_{AB}=4\operatorname{Tr}(\rho^2)-1.
\]

Split \(I_{AB}\) into Q8's orthogonal compact Bell block
\[
I_{\rm core}=K^2+2R^2
\]
and measured relation Other
\[
I_{\rm off}=I_{AB}-I_{\rm core}.
\]

## Part B — masked perpendicular-child completion

For each condition/state trajectory, exclude both endpoints. Hide the current measured \(v_t\).

Inputs permitted at the hidden time:

1. visible \(u_t\);
2. parent transverse radius \(R_{s,t}=(s_{2,t}+s_{3,t})/2\);
3. the immediately preceding and following measured \(v\) values, used only to choose the mirror sign.

Magnitude:

\[
m_t=\sqrt{\max(0,R_{s,t}^2-u_t^2)}.
\]

Direction lock:

\[
\ell_t=\frac{v_{t-1}+v_{t+1}}2.
\]

Choose \(+m_t\) or \(-m_t\), whichever is closest to \(\ell_t\). If exactly tied, use the sign of
\(v_{t-1}\); if that is zero, choose positive.

Fixed controls:

- zero fill: \(\widehat v=0\);
- time-only linear fill: \(\widehat v=\ell_t\);
- magnitude-only positive branch: \(\widehat v=m_t\).

This is interpolation/completion, not causal prediction. The parent radius contains current whole-state
information; therefore the result tests child-from-parent decompression, not measurement reduction.

## Frozen gates

All gates must pass for `CALIBRATED`.

1. `I1`: all `88` Information³ density reconstructions have Frobenius error at most `1e-12`.
2. `I2`: all `88` purity-closure residuals are at most `1e-12`.
3. `I3`: all `88` allocations satisfy \(I_A,I_B,I_{AB},I_{\rm off},I_{\rm unresolved}\ge-1e-10\).
4. `I4`: median measured off-core relation share \(I_{\rm off}/I_{AB}\) is at most `0.05` in both Ramsey and Hahn.
5. `I5`: masked ARA/Information³ signed-\(v\) completion MAE is at most `0.08`.
6. `I6`: masked ARA/Information³ completion improves zero-fill MAE by at least `50%`.
7. `I7`: masked ARA/Information³ completion improves positive-branch-only MAE by at least `50%`.
8. `I8`: at least `80%` of masked signs are correct.
9. `I9`: all completion outputs obey \(|\widehat v|\le R_s+1e-12\).

Time-only linear interpolation is reported as a strong same-neighbour control but is not a pass gate. Beating it
is not expected automatically because it uses the same two temporal neighbours and directly interpolates the
target coordinate.

## Interpretation boundary

A pass shows:

- the two children plus their relation exactly close the measured two-qubit state;
- Q8's compact Bell block dominates measured relation information;
- a missing perpendicular relation child can be filled from the parent radius plus temporal branch information.

It does not show that the parent radius can be obtained without measurement, that \(I_{\rm unresolved}\) is a
coherent environmental wave, or that the method predicts future data.

