# Q6 CHSH coherence-ladder ARA translation fidelity

**Claim ID / version:** `Q6-CHSH-COHERENCE-FID-v1`  
**Date:** 24 July 2026  
**Status at freeze:** `POST-Q5 CALIBRATION; RAW OUTCOMES ALREADY OPEN`

## Question

Q5 showed four physically prepared Bell parents whose six local child projections were close to the ARA `1.0`
ridge while their three same-axis parent relations were strong.

Q6 asks a stricter established-physics question:

> Can the full nine-cut parent relation distinguish a coherent Bell identity from a classical one-axis correlation
> and from a fully mixed identity, even when all three have ridge-like local children?

## Standard quantum object

For each state, form the real two-qubit correlation tensor

\[
T=
\begin{pmatrix}
\langle XX\rangle&\langle XY\rangle&\langle XZ\rangle\\
\langle YX\rangle&\langle YY\rangle&\langle YZ\rangle\\
\langle ZX\rangle&\langle ZY\rangle&\langle ZZ\rangle
\end{pmatrix}.
\]

Let \(s_1\ge s_2\ge s_3\ge0\) be its singular values. The Horodecki maximum CHSH value is

\[
S_{\max}=2\sqrt{s_1^2+s_2^2}.
\]

The established local-hidden-variable boundary is \(S_{\max}=2\).

## ARA translation

- Each singular direction is an independently retained parent-relation cut through the same two-child identity.
- A coherent Bell parent ideally retains three strong relation axes.
- The equal incoherent mixture of \(\Phi^+\) and \(\Phi^-\), or of \(\Psi^+\) and \(\Psi^-\), retains one
  classical parity axis while the two phase-sensitive axes cancel.
- The equal mixture of all four Bell parents cancels every two-child relation axis.
- Local children remain near the `1.0` ridge in all three cases. The distinguishing information is therefore in
  the relation among the children, not in either child alone.

This gives the frozen qualitative ladder

\[
\text{Bell coherent}\;(3)\quad\longrightarrow\quad
\text{classically correlated}\;(1)\quad\longrightarrow\quad
\text{fully mixed}\;(0),
\]

where the number in parentheses is the predicted count of singular values at least `0.50`.

## Control construction

The Bell rows use the physically prepared public raw-current archives already decoded in Q5.

The following are **equal-state-weight linear reconstructions**, not separately prepared experiments:

\[
\rho_{\Phi,\mathrm{classical}}=\tfrac12(\rho_{\Phi^+}+\rho_{\Phi^-}),
\]

\[
\rho_{\Psi,\mathrm{classical}}=\tfrac12(\rho_{\Psi^+}+\rho_{\Psi^-}),
\]

\[
\rho_{\mathrm{mixed}}=\tfrac14(
\rho_{\Phi^+}+\rho_{\Phi^-}+\rho_{\Psi^+}+\rho_{\Psi^-}).
\]

Because expectation values are linear in the density matrix, the corresponding tensors are formed by the same
equal-weight averages. The controls calibrate the geometry; they are not independent empirical replications.

## Fidelity boundary

Q6 may support only this bounded translation:

> Under the Q5 decoder, the full parent tensor separates physically prepared Bell coherence from reconstructed
> classical and fully mixed controls in the established CHSH/singular-axis geometry.

Q6 cannot claim that ARA discovered Bell nonlocality, derived CHSH, outperformed tomography, supplied a new
entanglement witness, proved Information-cubed, or established universal fractality or quantum gravity.

