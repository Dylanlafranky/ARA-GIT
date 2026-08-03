# Post-protocol audit — temporal Phi ruler

**Declared:** 1 August 2026, after the frozen temporal output was first seen
and before this audit was calculated  
**Reason:** the two-coordinate Golden Handover equation has a unique algebraic
fixed point at Phi. Comparing other diagonal landmarks under that joint metric
therefore gives Phi a structural advantage and is not, by itself, an empirical
target-selection test.

## Audit questions

### 1. Fair direct-ratio comparison

For consecutive movement lengths let

\[
r=\frac{\max(s_0,s_1)}{\min(s_0,s_1)}.
\]

Compare fixed targets using the common one-coordinate loss

\[
E_\tau=\left|\log(r/\tau)\right|,
\qquad
\tau\in\{1,\sqrt2,1.5,\varphi,2\}.
\]

Fit one free target on calibration only by minimizing mean \(E_\tau\), then
apply it unchanged to evaluation and holdout.

### 2. Does real temporal adjacency approach golden self-similarity?

The golden equality residual is

\[
S=\left|\log\left(\frac{q_{\rm whole}}{q_{\rm lineage}}\right)\right|.
\]

It is zero only at Phi, but Phi is not evidence merely because zero occurs
there. The empirical question is whether \(S\) is smaller for real consecutive
slices than for the frozen within-track circular-shift control. Estimate the
paired difference with 5,000 whole-video bootstrap resamples.

## Interpretation

- Phi being best only under the joint metric is algebraic recovery, not a
  target-specific empirical finding.
- Phi being best under direct-ratio loss on evaluation and holdout would be a
  fairer placement result.
- Smaller real-adjacency \(S\) than shifted \(S\) would show local movement
  approaches the golden fixed-point relation more than nonlocal movement from
  the same tracks. It would still not establish that Phi causes lower future
  temporal tension.
