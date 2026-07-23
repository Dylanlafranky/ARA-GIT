# Frozen protocol — ARA child-to-parent composition across three continuity laws

**Frozen:** 23 July 2026, before running the comparison  
**Status:** prospective reconstruction test  
**Primary question:** can one unchanged ARA boundary operator compose two child flow accounts into the directly
measured parent account across classical, electromagnetic and quantum continuity equations?

## 1. Frozen operator

For child \(i\), declare non-negative accumulation and release activities

\[
A_i\ge 0,\qquad R_i\ge 0,\qquad
T_i=A_i+R_i,
\qquad
x_i=\frac{2R_i}{T_i}.
\]

The inverse map is

\[
R_i=\frac{T_i x_i}{2},
\qquad
A_i=\frac{T_i(2-x_i)}{2}.
\]

If an interface transfer of magnitude \(I\) is counted as release by one child and accumulation by the other, it
is internal to the enclosing parent. The frozen parent operator is therefore

\[
\boxed{
x_P^{\rm pred}
=
\frac{2\left(\sum_iR_i-I\right)}
{\sum_i(A_i+R_i)-2I}
}
\]

when the parent external activity

\[
T_P=\sum_i(A_i+R_i)-2I
\]

is non-zero. The parent direct reading is independently calculated from its two external boundaries:

\[
x_P^{\rm direct}
=
\frac{2R_P}{A_P+R_P}.
\]

No coefficient is learned or fitted.

## 2. Raw analytic systems

### System A — classical mechanical wave

A one-dimensional ideal string with unit density and tension is used as a Newton/Hamilton continuum. The raw
displacement is a superposition of right- and left-travelling analytic waves. Its energy density and energy flux
satisfy

\[
\partial_t u_{\rm string}+\partial_x S_{\rm string}=0.
\]

One interval is divided into two adjacent child intervals.

### System B — electromagnetic transmission line

A lossless unit-inductance, unit-capacitance transmission line is used. Raw voltage and current are constructed
from analytic forward and backward waves. Its field energy density and Poynting-like line power satisfy

\[
\partial_t u_{\rm EM}+\partial_x P_{\rm EM}=0.
\]

The same two-child boundary operator is used unchanged.

### System C — quantum holdout

A freely evolving Gaussian wave packet in units \(\hbar=m=1\) is used. Probability density and probability current
satisfy

\[
\partial_t|\psi|^2+\partial_x j=0.
\]

The quantum case is the holdout. The operator cannot be changed after Systems A and B.

## 3. Boundary conversion

For a one-dimensional signed flux \(F\), positive means movement to the right. For interval \([a,b]\):

\[
A=\max(F(a),0)+\max(-F(b),0),
\]

\[
R=\max(-F(a),0)+\max(F(b),0).
\]

For adjacent children \([a,c]\) and \([c,b]\), the internal handover is

\[
I=|F(c)|.
\]

This declaration is fixed for all three theories.

## 4. Controls

Three parent estimates are compared:

1. **Frozen ARA boundary operator:** remove the internal handover from both accumulation and release.
2. **Naive child mean:** \((x_1+x_2)/2\).
3. **Activity-weighted but unclosed:** \((T_1x_1+T_2x_2)/(T_1+T_2)\), which leaves the internal transfer counted
   inside the parent.

The controls are intentionally plausible flattenings of the child accounts.

## 5. Frozen sampling and exclusions

- Use 4,097 deterministic time samples per system.
- Use the fixed spatial boundaries stored in the reproduction script.
- Exclude only samples where the directly measured parent external activity is at or below \(10^{-12}\), because
  an ARA position is undefined when both parent channels have zero activity.
- No smoothing, Fourier decomposition, machine learning, prime sieve or post-result parameter tuning is allowed.
- Save a bounded deterministic sample for inspection; regenerate the complete arrays from the script.

## 6. Pass criteria

The primary test passes only if:

1. all three models retain at least 99% of their planned samples;
2. the maximum absolute frozen-operator error is at most \(5\times10^{-12}\) in every model;
3. orientation reversal satisfies \(x'_P=2-x_P\) to the same tolerance;
4. both incorrect controls have larger mean absolute error than the frozen operator in every model;
5. analytic/local continuity residuals are zero to numerical precision for the classical and EM models, and the
   independently finite-differenced quantum residual is below \(10^{-6}\).

## 7. Interpretation fence

A pass would establish that ARA's proposed child/parent boundary accounting is an exact common reparameterisation
of these three conservation-law systems. It would show why an internal child coupling must disappear from the
parent boundary account.

It would **not** discover a new force, derive quantum mechanics from classical mechanics, prove universal
fractality, establish Phi, or show that every physical law has this continuity form. Because the operator is
constructed from conservation accounting, a pass is primarily a formalization and cross-domain consistency result.

The next discriminating test after a pass is to hide a real source, sink or storage relation and ask whether an
ARA residual predicts that missing `Other` term prospectively.
