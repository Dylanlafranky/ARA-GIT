# Frozen protocol — Q12 residual children

**Protocol ID:** `Q12-RESIDUAL-CHILDREN-v1`  
**Ledger ID:** `T271`  
**Frozen:** 24 July 2026, after Q11 outcomes and residual diagnostics were open but before calculating Q12 mode
energy, held-out predictions or gates  
**Test class:** post-outcome orthogonal child decomposition with held-out-identity test  
**Source:** Q11's `88` visible/unresolved residual records

## Data cell

At every condition/wait cell, order the four complex residuals as:

\[
\mathbf e=
\begin{bmatrix}
E_{\Phi+}&E_{\Phi-}&E_{\Psi+}&E_{\Psi-}
\end{bmatrix}^{\mathsf T}.
\]

There must be `22` complete cells: eleven Ramsey and eleven Hahn.

## Four orthogonal children

\[
\begin{aligned}
m_0&=(E_{\Phi+}+E_{\Phi-}+E_{\Psi+}+E_{\Psi-})/2,\\
m_F&=(E_{\Phi+}+E_{\Phi-}-E_{\Psi+}-E_{\Psi-})/2,\\
m_S&=(E_{\Phi+}-E_{\Phi-}+E_{\Psi+}-E_{\Psi-})/2,\\
m_{FS}&=(E_{\Phi+}-E_{\Phi-}-E_{\Psi+}+E_{\Psi-})/2.
\end{aligned}
\]

Interpret only as coordinate children:

- \(m_0\): common child;
- \(m_F\): Phi/Psi family child;
- \(m_S\): plus/minus orientation child;
- \(m_{FS}\): family-by-orientation interaction/Other.

The inverse is:

\[
E_{f,s}=\frac12(m_0+f\,m_F+s\,m_S+fs\,m_{FS}),
\]

where \(f=+1/-1\) for Phi/Psi and \(s=+1/-1\) for plus/minus.

Parseval closure:

\[
\sum_{\rm states}|E|^2=|m_0|^2+|m_F|^2+|m_S|^2+|m_{FS}|^2.
\]

Report energy shares separately for:

- real/amplitude residual;
- imaginary/direction residual;
- complete complex residual.

## Held-out fourth identity

For each target state \((f,s)\), use only the other three residuals in the same condition/wait cell. Under the
lower-order no-interaction model \(m_{FS}=0\):

\[
\boxed{
\widehat E_{f,s}
=E_{f,-s}+E_{-f,s}-E_{-f,-s}.
}
\]

This is a genuine held-out-state value: the target residual is not used to form its prediction.

## Controls

Compare complex Euclidean error against:

1. zero residual;
2. mean of the other three states;
3. same-family sibling \(E_{f,-s}\).

Report real/amplitude and imaginary/direction MAE, complex mean/median error and sign accuracy separately.

## Frozen gates

All ten gates must pass for `CALIBRATED`; otherwise report the passed structure and failed child claims.

1. `C1`: `88` unique records form `22` complete four-state cells.
2. `C2`: Hadamard inverse reconstructs every complex residual with maximum error at most `1e-12`.
3. `C3`: Parseval energy closure has maximum error at most `1e-12`.
4. `C4`: common-child share of real/amplitude residual energy is at least `50%` in Ramsey and Hahn.
5. `C5`: combined non-common share of imaginary/direction energy is at least `50%` in Ramsey and Hahn.
6. `C6`: held-out no-interaction mean complex error is at least `10%` below zero-residual error in both
   conditions.
7. `C7`: held-out no-interaction mean complex error is at least `5%` below leave-one-out-mean error in both
   conditions.
8. `C8`: held-out real/amplitude sign accuracy is at least `75%` in both conditions, excluding values within
   `1e-12` of zero.
9. `C9`: held-out imaginary/direction sign accuracy is at least `60%` in both conditions, excluding values
   within `1e-12` of zero.
10. `C10`: family-by-orientation interaction energy share is at most `25%` of complete complex residual energy
    in both conditions.

## Boundaries

- The Bell labels and Q11 residual pattern were inspected before this freeze.
- Exact four-mode closure is guaranteed by the orthogonal transform.
- The held-out test is across identities at the same measured wait, not future-time forecasting.
- The four modes are coordinate children. They are not automatically distinct particles, environmental channels
  or causal mechanisms.
- Eleven waits per condition remain sparse.
- Failure of the no-interaction predictor means \(m_{FS}\) is load-bearing rather than evidence against Q11.

