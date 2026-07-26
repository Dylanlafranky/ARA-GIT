# Frozen protocol — Q11 visible/unresolved Information³ relation

**Protocol ID:** `Q11-VISIBLE-UNRESOLVED-INFORMATION3-v1`  
**Ledger ID:** `T270`  
**Frozen:** 24 July 2026, after Q10 outcomes were open but before calculating Q11 condition metrics, branch
agreement, angular opposition, controls or residual fields  
**Test class:** post-outcome parameter-free relation calibration  
**Source:** Q9's `88` public Bell trajectory allocations

## Data and grain

Analyze eight trajectories separately: Ramsey/Hahn crossed with Phi-plus, Phi-minus, Psi-plus and Psi-minus.
Each trajectory must contain eleven unique, strictly increasing wait coordinates.

Visible compact relation:

\[
V(t)=K(t)+R(t).
\]

Independently defined unresolved-to-pure coordinate from the same reconstructed density matrix:

\[
P(t)=H_P(t)=\frac{I_{\rm unresolved}(t)}2
=2\left(1-\operatorname{Tr}\rho(t)^2\right).
\]

The algebraic \(H=2-K-R\) is not the Q11 target because using it would make complementarity exact by
definition.

## Two-axis coordinates

For \(Z\in\{V,P\}\), calculate within each trajectory:

\[
x_Z(t)=2\frac{Z(t)-Z_{\min}}{Z_{\max}-Z_{\min}},
\]

\[
y_Z(t)=1-\operatorname{clip}\left(
\frac{\dot Z(t)}{\max_t|\dot Z(t)|},-1,1
\right),
\]

where \(\dot Z\) uses `numpy.gradient(Z,t,edge_order=2)`.

The centred relation-plane coordinate is:

\[
C_Z(t)=(x_Z(t)-1)+i(y_Z(t)-1).
\]

## Frozen parameter-free relation

The ARA anti-phase prediction is:

\[
\widehat C_P(t)=-C_V(t),
\]

or:

\[
\widehat x_P(t)=2-x_V(t),
\qquad
\widehat y_P(t)=2-y_V(t).
\]

The measured relation residual is:

\[
E(t)=C_P(t)+C_V(t),
\]

so:

\[
C_P(t)=-C_V(t)+E(t).
\]

This exact final reconstruction is an accounting identity. The empirical question is whether \(E\) is small
and whether the unfitted anti-phase map beats simpler controls.

## Controls

Compare pointwise two-axis Euclidean error against:

1. **ridge-only:** \((\widehat x,\widehat y)=(1,1)\);
2. **same-phase:** \((\widehat x,\widehat y)=(x_V,y_V)\);
3. **amplitude-only anti-phase:** \((\widehat x,\widehat y)=(2-x_V,1)\);
4. **direction-only anti-phase:** \((\widehat x,\widehat y)=(1,2-y_V)\).

## Metrics

Report by condition and overall:

- correlation between predicted and observed amplitude;
- correlation between predicted and observed opening/closing coordinate;
- amplitude MAE, direction MAE and two-axis Euclidean MAE;
- control errors and percentage improvements;
- opening/closing branch agreement, excluding points where either coordinate is within `1e-12` of the ridge;
- angular opposition score
  \[
  s_\theta=-\cos(\theta_P-\theta_V),
  \]
  using only points where both relation radii are at least `0.10`;
- residual \(E\) radius, angle and quadrant for every point.

## Frozen gates

All ten gates must pass for `CALIBRATED`.

1. `R1`: `88` unique rows form eight valid eleven-point, nonzero-range \(V,P\) trajectories.
2. `R2`: all four coordinates are finite and inside `[0,2]` within `1e-12`.
3. `R3`: predicted-versus-observed amplitude correlation is at least `0.95` in Ramsey and Hahn.
4. `R4`: predicted-versus-observed direction correlation is at least `0.40` in Ramsey and Hahn.
5. `R5`: overall median anti-phase two-axis error is at most `0.25`.
6. `R6`: anti-phase mean two-axis error is at least `25%` lower than ridge-only in each condition.
7. `R7`: anti-phase mean two-axis error is at least `50%` lower than same-phase in each condition.
8. `R8`: opening/closing branch agreement is at least `75%` in each condition.
9. `R9`: median angular opposition score is at least `0.75` in each condition.
10. `R10`: \(C_P=-C_V+E\) reconstructs both target coordinates with maximum error at most `1e-12`.

## Boundaries

- Q10 exposed an equivalent aggregate distance before this freeze; Q11 is a formal relation decomposition, not
  a blind discovery.
- \(V\) and \(P\) are different functions of the same reconstructed density matrix, not independent experiments.
- Local normalization tests path shape and direction, not absolute physical magnitude.
- The residual \(E\) is a candidate child field. Q11 does not yet declare its lobes to be physical children.
- Correlation does not identify environmental mechanisms or causation.
- Eleven time samples per trajectory limit turning-point and fine-child resolution.

