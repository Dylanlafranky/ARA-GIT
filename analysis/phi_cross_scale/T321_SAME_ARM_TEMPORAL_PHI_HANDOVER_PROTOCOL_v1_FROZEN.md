# T321 — same-arm temporal Phi-handover protocol v1 (frozen)

**Frozen:** 31 July 2026, before the corrected result was calculated  
**Status:** retrospective identity-boundary correction to T320/T320A  
**Public source:** dynamicslab *MultiArm-Pendulum*, Zenodo
[`10.5281/zenodo.6633719`](https://doi.org/10.5281/zenodo.6633719)

## Question

Does one pendulum arm, followed through time, exhibit the proposed ARA
same-phase handover geometry?

\[
\underbrace{A_{j,k}\rightarrow B_{j,k}\rightarrow A_{j,k+1}}_{
\text{complete same-identity route}}=2,
\qquad
\underbrace{A_{j,k}\rightarrow A_{j,k+1}}_{
\text{direct same-phase route}}\stackrel{?}{=}\phi.
\]

The arm label \(j\) is fixed. Only time advances. No other arm may substitute
for either endpoint or for the intervening half-swing.

## Frozen physical object

1. Load the three public free-swing triple-pendulum records at `500 Hz`
   (`decimate=20`). Runs 1–2 establish fixed scales; run 3 is the primary
   evaluation record. The public driven triple-pendulum record is a transfer
   check.
2. Rest-centre every arm using its circular mean.
3. Detect genuine alternating turning points with the already-audited rule:
   prominence `0.02*pi` radians and minimum separation
   `0.4 * 1.333 s`.
4. A **swing** is the complete raw half-cycle between consecutive genuine
   turning points. Increasing-angle swings and decreasing-angle swings are
   the two reversible phase labels. The labels may be swapped without
   changing the pooled result.
5. Resample every complete half-swing to `129` equally spaced traversal
   positions. This preserves the complete measured swing path rather than
   replacing it with an instantaneous turning point.
6. An eligible event contains three consecutive half-swings from the same
   arm whose directions alternate: `A_k`, `B_k`, `A_(k+1)`.

## Frozen ARA trajectory coordinates

For arm \(j\), estimate its median complete-cycle duration \(T_j\) from runs
1–2 only, using the time between every second genuine turning point. Define

\[
x_{\theta}=1+\frac{\theta_{\rm rest-centred}}{\pi},
\qquad
x_t=\frac{2t}{T_j}.
\]

Thus a typical complete `A -> B -> A` temporal traversal occupies `2` ARA
units. The primary path is the full resampled trajectory

\[
X(s)=(x_{\theta}(s),x_t(s)),\qquad 0\le s\le1.
\]

For two complete half-swing paths, use root-mean-square pointwise Euclidean
distance after matching equal traversal positions:

\[
d(X,Y)=\sqrt{\frac1{129}\sum_{m=1}^{129}
\lVert X(s_m)-Y(s_m)\rVert_2^2}.
\]

For every eligible same-arm event, calculate

\[
q=\frac{2d(A_k,A_{k+1})}
{d(A_k,B_k)+d(B_k,A_{k+1})}.
\]

By the triangle inequality, `q` lies on the ARA interval `[0,2]`. It is not
forced to equal `2` or Phi. The frozen target is

\[
q=\phi=1.6180339887\ldots
\]

## Sensitivity coordinates

These are reported but cannot overturn the primary verdict:

- configuration-only: `x_theta`;
- phase-space-time: `(x_theta, omega/s_omega, x_t)`, where the robust angular
  velocity scale `s_omega` is estimated from runs 1–2 only.

## Frozen comparison landmarks

For the primary `q`, compare median absolute error against

\[
1,\quad\sqrt2,\quad1.5,\quad\phi,\quad\sqrt3,\quad2.
\]

The winner must be unique at displayed precision (`1e-9`).

## Frozen controls

For each arm, retain the real `A_k` and `A_(k+1)` paths but circularly shift
the intervening B-path identities by `17%`, `31%`, and `47%` of the eligible
event sequence. Re-centre each shifted B path on the original B path's time
centre before calculating distance, so the control destroys the observed
trajectory pairing without winning or losing merely because it was moved to
a remote absolute timestamp.

## Frozen gates

- **G1:** Phi is the unique pooled primary-landmark winner.
- **G2:** both reversible phase directions independently choose Phi.
- **G3:** at least two of the three arms independently choose Phi.
- **G4:** pooled median primary `q` lies within `0.08` of Phi.
- **G5:** the real intervening B pairing has lower median `|q-Phi|` than all
  three shifted-B controls.

Verdict:

- `5/5`: **SUPPORTED**;
- `3–4/5`: **MIXED**;
- `0–2/5`: **NOT SUPPORTED**.

## Evidence boundary

This is not a blind discovery test. The public source and previous wrong-cut
result were already open. It is a frozen, auditable correction of the
physical identity boundary. A positive result would support this specific
same-arm temporal operationalization; it would not by itself establish Phi
as a universal physical handover law. A negative result would reject this
operationalization without invalidating unrelated mathematical Phi
identities or scale-lineage calibrations.
