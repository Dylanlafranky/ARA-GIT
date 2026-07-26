# Frozen protocol — Q6B physical CHSH coherence ladder

**Protocol ID:** `Q6B-PHYSICAL-CHSH-v1`  
**Ledger ID:** `T265`  
**Frozen:** 24 July 2026, after Q6 exposed a raw-tensor Tsirelson violation and before any physical projection was calculated  
**Test class:** remedial post-hoc known-source calibration  
**Source:** Figshare DOI `10.6084/m9.figshare.14160476.v2`

## Inputs and bootstrap

Inherit Q6's four checksum-locked archives, raw-current decoder, orientation maps, equal-state-weight control
definitions, seed `2026072406`, `5,000` record-bootstrap draws and strong-axis threshold `0.50`.

## Fixed physical projection

For every point estimate and every bootstrap state:

1. reconstruct the Hermitian linear density matrix from all sixteen Pauli coefficients;
2. project its eigenvalues onto the unit probability simplex using the Euclidean simplex algorithm;
3. preserve the eigenvectors and rebuild \(\rho_{\mathrm{phys}}\);
4. derive all physical Pauli expectations, the \(3\times3\) tensor, descending singular values and
   \(S_{\max}=2\sqrt{s_1^2+s_2^2}\).

Construct controls by equal-weight averaging the already projected physical state matrices, then derive their
metrics. Do not project a second time unless numerical tolerance requires Hermitization.

## Frozen gates

All gates must pass for `SUPPORTED`; any gate failure gives `NOT SUPPORTED`.

1. `P1`: all seven physical entities have trace error at most `1e-12`.
2. `P2`: all seven have minimum eigenvalue at least `-1e-12`.
3. `P3`: all seven have Hermiticity residual at most `1e-12`.
4. `P4`: all seven satisfy \(S_{\max}\le2\sqrt2+10^{-12}\).
5. `B1`: all four Bell rows satisfy \(S_{\max}>2.00\).
6. `B2`: all four Bell rows satisfy \(S_{\max}\ge2.20\).
7. `B3`: all four Bell rows have \(s_2\ge0.50\).
8. `B4`: all four Bell rows have exactly three singular axes at least `0.50`.
9. `B5`: each Bell row crosses \(S=2\) in at least `95%` of bootstrap draws.
10. `C1`: both classical controls satisfy \(S_{\max}\le2.00\).
11. `C2`: both classical controls have \(s_1\ge0.70\).
12. `C3`: both classical controls have \(s_2\le0.30\).
13. `C4`: both classical controls have exactly one singular axis at least `0.50`.
14. `C5`: each classical control satisfies \(S_{\max}\le2.10\) in at least `90%` of bootstrap draws.
15. `M1`: the uniform control satisfies \(S_{\max}\le0.60\).
16. `M2`: the uniform control has \(s_1\le0.30\).
17. `M3`: the uniform control has zero singular axes at least `0.50`.
18. `M4`: the uniform control satisfies \(S_{\max}\le0.60\) in at least `95%` of bootstrap draws.
19. `O1`: mean Bell \(S_{\max}\) minus mean classical \(S_{\max}\) is at least `0.40`.
20. `O2`: retained-axis sequence is exactly `3,3,3,3 / 1,1 / 0`.

## Interpretation boundary

This is a remedial calibration on already-open data. A pass would show that the ARA-described closure ladder
survives an explicit physical-state constraint. It would not be a blind prediction, an independent experiment,
a new entanglement witness, or a derivation of CHSH/Bell physics.

