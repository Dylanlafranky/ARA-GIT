# Frozen protocol — Q13 Ramsey/Hahn latent child

**Protocol ID:** `Q13-RAMSEY-HAHN-LATENT-CHILD-v1`  
**Ledger ID:** `T272`  
**Frozen:** 24 July 2026, after Q12 outcomes were open but before calculating Q13 candidates, covariance
reductions, rank-one scores or permutation nulls  
**Test class:** post-outcome leave-one-Bell-identity-out latent-coordinate test  
**Source:** Q11's `88` two-axis visible/unresolved records

## Four child trajectories

For each Bell state and wait index, construct:

\[
\begin{aligned}
R_A&=C_{V,\rm Ramsey},&
R_B&=C_{P,\rm Ramsey},\\
H_A&=C_{V,\rm Hahn},&
H_B&=C_{P,\rm Hahn}.
\end{aligned}
\]

Here:

- \(A\) denotes the visible compact relation;
- \(B\) denotes independently defined unresolved-to-pure information;
- each \(C=(x-1)+i(y-1)\) contains amplitude \(x\) and opening/closing \(y\).

Analyze centred amplitude and direction components separately. Equal wait indices are treated as matched ordinal
stages, not equal physical times.

## Held-out latent procedure

Test each of \(R_A,R_B,H_A,H_B\) as candidate hidden child \(h\).

For each leave-one-Bell-state-out fold:

1. pool the other three Bell states (`33` rows);
2. for each of the three visible children \(v_j\), fit
   \[
   v_j=\alpha_j+\beta_j h
   \]
   by ordinary least squares;
3. apply the frozen coefficients to the held-out Bell state (`11` rows);
4. calculate the held-out visible covariance before and after conditioning:
   \[
   S=\operatorname{Cov}(\mathbf v),
   \qquad
   S_r=\operatorname{Cov}(\mathbf v-\widehat{\mathbf v}(h));
   \]
5. calculate off-diagonal covariance energy
   \[
   E_{\rm off}(M)=\sum_{i<j}M_{ij}^2;
   \]
6. calculate reduction
   \[
   \Delta=1-\frac{E_{\rm off}(S_r)}{E_{\rm off}(S)}.
   \]

The removed covariance is:

\[
D=S-S_r.
\]

Report its leading-singular-value energy share and whether its three off-diagonal signs agree with the fitted
rank-one induced relation

\[
I=\boldsymbol\beta\boldsymbol\beta^{\mathsf T}\operatorname{Var}(h).
\]

## Candidate selection

For each candidate, take median \(\Delta\) across four held-out Bell states separately for amplitude and
direction. Define:

\[
\text{score}(h)=\frac{\widetilde\Delta_x(h)+\widetilde\Delta_y(h)}2.
\]

The candidate with maximum score is selected. Ties resolve alphabetically.

The Phase B claim predicts the selected candidate is \(R_B\) or \(H_B\).

## Selection-corrected permutation null

Use `999` deterministic permutations with seed `27013`.

Within each Bell state, independently permute every candidate hidden trajectory across its eleven wait indices,
then repeat the complete four-candidate cross-validation. For each permutation retain:

- the maximum candidate amplitude reduction;
- the maximum candidate direction reduction;
- the maximum composite score.

Use add-one p-values:

\[
p=\frac{1+\#(\text{null}\ge\text{observed})}{1000}.
\]

## Frozen gates

All ten gates must pass for `CALIBRATED`.

1. `L1`: `44` complete matched state/wait cells contain all four finite children.
2. `L2`: every held-out fold uses `33` training and `11` testing rows with no Bell-state overlap.
3. `L3`: the selected candidate is unresolved Phase B: \(R_B\) or \(H_B\).
4. `L4`: selected-candidate median amplitude covariance reduction is at least `0.60`.
5. `L5`: selected-candidate median direction covariance reduction is at least `0.25`.
6. `L6`: selection-corrected amplitude permutation p-value is at most `0.01`.
7. `L7`: selection-corrected direction permutation p-value is at most `0.05`.
8. `L8`: selected-candidate median leading-singular energy share of removed covariance is at least `0.70` on
   both axes.
9. `L9`: selected-candidate median sign agreement across the three induced visible relations is at least `2/3`
   on both axes.
10. `L10`: the same candidate has the highest composite reduction in at least `3/4` held-out Bell states.

## Boundaries

- Q11/Q12 data and outcomes were open before this freeze.
- The test uses derived local coordinates, not raw absolute-unit observables.
- Conditioning uses the deliberately revealed hidden candidate in held-out rows; this tests mediation structure,
  not recovery of an unmeasured hidden trajectory.
- The rank-one fitted induced matrix is rank one by construction. Empirical content lies in held-out covariance
  removal, agreement with the removed matrix and the permutation comparison.
- With only eleven ordinal stages per held-out state, covariance estimates are noisy.
- Success would support one-latent-to-three-relations geometry, not a literal Ramsey-to-Hahn temporal handoff,
  causal environmental identity or universal ARA law.

