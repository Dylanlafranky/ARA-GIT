# Q15 — Unresolved-component self-identity and conditional Phase-B handover

**Protocol:** v1.0 — frozen before the Q15 calculation  
**Frozen:** 2026-07-24 18:43 AEST  
**Status:** post-outcome calibration test, not a blind prediction

## 1. Question

Q8 defined an unresolved component

\[
H_{\mathrm{Q8}}=2-K-R.
\]

Q9 showed that this component closely follows independently calculated Bell-state purity loss. Q10 then mapped its opening/closing path, but Q10's TE-ARA sum was a normalized occupancy of four trajectory quadrants. It did **not** answer:

\[
\underbrace{T_H}_{2}
=
\underbrace{H_{\mathrm{self}}}_{\text{repeatable unresolved identity}}
+
\underbrace{O_H}_{\text{state-specific or unmodelled Other}}.
\]

Q15 tests that missing gate. Only if the unresolved component passes its own identity gate will Q15 test whether it participates in the Ramsey/Hahn exchange expected of a candidate ARA Phase B.

## 2. Sources

Primary:

- `Q11_VISIBLE_UNRESOLVED_INFORMATION3_RECORDS.csv`
- unresolved waveform \(U=P=2(1-\operatorname{Tr}\rho^2)\), stored as `target_purity_loss`

Robustness definition:

- `Q8_BELL_RELATION_PLANE_RECORDS.csv`
- algebraic unresolved remainder \(H_{\mathrm{Q8}}=2-K-R\), stored as `hidden_residual`

The purity-defined waveform is primary because it is calculated from the full density matrix rather than defined as the remainder of the same visible-accounting equation.

## 3. Native self-identity decomposition

The four Bell states are four same-protocol realizations of the unresolved waveform. For condition \(c\), state \(s\), and wait \(t\):

\[
U_{cst}=\mu_{ct}+\epsilon_{cst},
\qquad
\mu_{ct}=\frac14\sum_s U_{cst}.
\]

Here:

- \(\mu\) is the repeatable common unresolved trajectory;
- \(\epsilon\) is state-specific Other at this measurement grain.

To prevent a shared positive baseline from being mistaken for an identity, the primary calculation uses change from the first wait:

\[
D_{cst}=U_{cst}-U_{cs0}.
\]

It also tests the native time derivative:

\[
G_{cst}=\frac{dU_{cs}}{dt}.
\]

For either \(X=D\) or \(X=G\), the common-mode energy share is:

\[
\eta_X
=
\frac{4\sum_t\bar X_{ct}^{\,2}}
{4\sum_t\bar X_{ct}^{\,2}
+
\sum_{s,t}(X_{cst}-\bar X_{ct})^2}.
\]

Because the residuals sum to zero at every wait, this is an exact orthogonal common-versus-residual decomposition in the measured data. It is a repeatability/participation measure, not a new physical energy law.

The conservative self-identity fraction is:

\[
\eta_H=\min(\eta_D,\eta_G).
\]

The ARA participation account is then:

\[
\boxed{
H_{\mathrm{self}}=2\eta_H,
\qquad
O_H=2(1-\eta_H),
\qquad
H_{\mathrm{self}}+O_H=2.
}
\]

## 4. Generalization and controls

### 4.1 Leave-one-state-out prediction

For every held-out Bell state, the mean trajectory of the other three states predicts its \(D\) and \(G\) trajectories. Q15 reports pooled leave-one-state-out \(R^2\).

This checks whether the common trajectory transfers to an unseen state instead of merely describing the four-state mean.

### 4.2 Time-alignment permutation null

Within each state, the measured wait-order values are independently permuted 9,999 times. This preserves each state's value distribution while destroying shared temporal alignment.

The one-sided permutation probability is:

\[
p
=
\frac{1+\#(\eta_H^{\mathrm{null}}\geq\eta_H^{\mathrm{observed}})}
{10\,000}.
\]

### 4.3 Cross-definition robustness

The Q8 algebraic remainder and Q11 purity-defined unresolved waveform are compared at identical condition/state/wait records. Pearson correlation must be at least \(0.95\) in both protocols.

This is a robustness check, not complete independence: both quantities come from the same public density matrices.

## 5. Frozen self-identity classifications

All thresholds below were frozen before the Q15 calculation.

### Dominant coherent identity

Required in **both** Ramsey and Hahn:

- \(\eta_D\geq0.80\);
- \(\eta_G\geq0.80\);
- \(\eta_H\geq0.80\);
- leave-one-state-out \(R_D^2\geq0.75\);
- leave-one-state-out \(R_G^2\geq0.50\);
- permutation \(p\leq0.01\);
- Q8/Q11 cross-definition correlation \(\geq0.95\).

Only this classification permits Q15 to promote the component to a calibrated Phase-B crosswalk.

### Coherent but mixed

Required in both protocols:

- \(\eta_D\geq0.60\);
- \(\eta_G\geq0.60\);
- \(\eta_H\geq0.60\);
- both leave-one-state-out \(R^2\) values are positive;
- permutation \(p\leq0.05\);
- cross-definition correlation \(\geq0.90\).

This supports a recurring unresolved mode, but **not** a sufficiently pure identity for a safe Phase-B label.

Anything below these gates remains an unresolved accounting component.

## 6. Conditional Ramsey/Hahn handover test

This stage is interpreted only if the dominant coherent-identity gate passes. It is still calculated and reported diagnostically if the gate fails.

At approximately common Ramsey and Hahn physical waits (relative wait mismatch no more than 2%):

\[
\Delta U=P_R-P_H,
\qquad
\Delta V=V_H-V_R,
\]

where \(V=K+R\) is the visible component.

The proposed handover says that the unresolved amount removed by Hahn should be accompanied by a corresponding visible recovery.

Frozen descriptive gates:

- at least 16 matched state/wait records;
- sign agreement between \(\Delta U\) and \(\Delta V\) at least 75%;
- Pearson correlation at least \(0.80\);
- through-origin slope of \(\Delta V\) on \(\Delta U\) between \(0.5\) and \(1.5\);
- mean absolute error from \(\Delta V=\Delta U\) no more than \(0.20\) on the native 0–2 account;
- within-state Hahn-wait rematching permutation \(p\leq0.05\) for correlation.

The rematching control preserves each Hahn row as a physical unit while breaking its correct wait correspondence to Ramsey.

## 7. Interpretation boundary

Even if every Q15 gate passes:

- this is post-outcome calibration on one public dataset;
- it does not discover a new quantum degree of freedom;
- it does not show that coherence literally leaves the physical quantum system;
- it supports, at most, an ARA crosswalk in which purity loss behaves as a repeatable unresolved identity and exchanges account with the visible component under echo refocusing.

A safe Phase-B statement additionally requires reproduction on a new dataset under a protocol frozen before its outcomes are inspected.
