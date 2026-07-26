# Frozen protocol - Q8 Bell relation-plane deconstruction

**Protocol ID:** `Q8-BELL-RELATION-PLANE-v1`  
**Ledger ID:** `T267`  
**Frozen:** 24 July 2026, after Q7 outcomes were open but before calculating the Bell-family complex relation
coordinates  
**Test class:** post-outcome ARA deconstruction / exact quantum crosswalk  
**Source:** Q7's four checksum-pinned public files from Zenodo DOI `10.5281/zenodo.14880901`

## Inputs and physical reconstruction

Inherit Q7's file hashes, row/basis map, wait coordinates, exact source conversion
\(\langle ij\rangle=4c_{ij}\), eigenvalue-simplex physical projection, state order and `0.50` strong-axis
threshold.

## Fixed Bell-family relation coordinates

For Phi states:

\[
u_\Phi=\frac{XX-YY}{2},
\qquad
v_\Phi=\frac{XY+YX}{2}.
\]

For Psi states:

\[
u_\Psi=\frac{XX+YY}{2},
\qquad
v_\Psi=\frac{YX-XY}{2}.
\]

For both:

\[
R=\sqrt{u^2+v^2},
\qquad
\theta=\operatorname{atan2}(v,u),
\qquad
K=|ZZ|.
\]

The compact tensor reconstruction is fixed as:

- Phi: `XX=u`, `YY=-u`, `XY=YX=v`, `ZZ=measured ZZ`;
- Psi: `XX=YY=u`, `XY=-v`, `YX=v`, `ZZ=measured ZZ`;
- all other correlation-tensor entries are zero.

Define:

\[
\mathrm{core\ share}
=1-\frac{\lVert T-T_{\rm core}\rVert_F^2}{\lVert T\rVert_F^2},
\]

\[
\mathrm{TE}_{\rm observed}=K+R,
\qquad
H=2-K-R,
\qquad
H_K=1-K,
\qquad
H_R=1-R.
\]

The alternate-family radius is calculated from the unused orthogonal Bell-family combinations and reported as
cross-family Other.

## Frozen gates

All gates must pass for `CALIBRATED`.

1. `D1`: all `88` physical reconstructions remain trace-one, positive-semidefinite, Hermitian and
   Tsirelson-bounded.
2. `D2`: median compact-core tensor share is at least `0.90` in both Ramsey and Hahn.
3. `D3`: at the first wait, every state has \(K\ge0.80\), \(R\ge0.80\) and
   \(\mathrm{TE}_{\rm observed}\ge1.60\).
4. `D4`: at the final Ramsey wait, every state retains at least `0.75` of its initial \(K\).
5. `D5`: at the final Ramsey wait, every state retains at most `0.20` of its initial \(R\).
6. `D6`: the median final Ramsey \(K\)-retention minus \(R\)-retention is at least `0.60`.
7. `D7`: the median absolute mismatch between \((K,R,R)\) and the descending tensor singular values is at most
   `0.08` across all records.
8. `D8`: for every Ramsey state, the first \(R<0.50\) sample is within one sample of the first one-strong-axis
   observation.
9. `D9`: the geometric-mean Hahn/Ramsey delay in first \(R<0.50\) is at least `4.0`.
10. `D10`: at the first wait, each state's declared Bell-family radius exceeds its alternate-family radius by at
    least `0.60`.
11. `D11`: median absolute error of reconstructing the hidden quadrature magnitude from the parent transverse
    radius,
    \[
    |v|=\sqrt{\max(0,R_s^2-u^2)},\qquad R_s=(s_2+s_3)/2,
    \]
    is at most `0.08`.

## Interpretation boundary

A pass shows that the Q7 tensor can be compressed into and decompressed from a Bell-family relation circle plus a
persistent parity cut with bounded residual. It does not show that \(H\) is uniquely environmental, that
\(K+R\) is a conserved physical energy, or that ARA replaces density-matrix tomography.

