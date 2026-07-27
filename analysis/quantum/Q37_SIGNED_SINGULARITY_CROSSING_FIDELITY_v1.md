# Q37 Translation Fidelity — Signed Singularity Crossing

**Date:** 27 July 2026  
**Ledger:** T292  
**Status:** Frozen before downloading or opening the target values

## User prior retained

> "The pinch is the singularity crossing."

The user further identified the Q36 path as an unusually clear anti-phase
Phase-B candidate. Claude then noted that equal pre/post windows around the
Q36 trough were not mirror-balanced: the approach side was heavier, giving
median-path coordinates `0.952` for total relation amplitude and `0.938` for
determinant closure. Independent event-level checking confirmed a modest but
consistent accumulation-heavy direction.

## Plain ARA translation

The visible relation contracts into the singularity crossing. It should then
emerge on the other side in an anti-oriented Phase-B form rather than merely
returning with the same orientation.

The crossing itself should also be asymmetric. Over equal windows, the
approach/accumulation side should carry slightly more relation than the
exit/release side. The anticipated traversal coordinate is approximately
`0.94–0.95`, just below the ARA ridge at `1`.

## Exact scientific objects

For every fixed pair relation, use the raw connected tensor

\[
C_t=T_t-\mathbf a_t\mathbf b_t^{\mathsf T}.
\]

The unsigned closure and magnitude coordinates are

\[
h_t=|\det C_t|^{1/3},
\qquad
A_t=\lVert C_t\rVert_F.
\]

At every registered determinant trough \(t\), define the signed cross-seam
orientation

\[
S_t=
\frac{
\sum_{k=1}^{7}\langle C_{t-k},C_{t+k}\rangle_F
}{
\sum_{k=1}^{7}
\lVert C_{t-k}\rVert_F\lVert C_{t+k}\rVert_F
}.
\]

This is bounded by `-1` and `+1`.

- \(S_t<0\): exit is anti-oriented relative to approach;
- \(S_t>0\): same orientation dominates;
- \(S_t\approx0\): perpendicular/mixed or unresolved orientation.

The equal-window traversal coordinates are

\[
X_A=
\frac{2\sum_{k=1}^{7}A_{t+k}}
{\sum_{k=1}^{7}A_{t-k}+\sum_{k=1}^{7}A_{t+k}},
\]

\[
X_h=
\frac{2\sum_{k=1}^{7}h_{t+k}}
{\sum_{k=1}^{7}h_{t-k}+\sum_{k=1}^{7}h_{t+k}}.
\]

`1` is equal traversal. Values below `1` are approach/accumulation-heavy in
the frozen direction.

## Fidelity judgment

This translation tests the user's declared geometry directly:

- the pinch is located using the same ARA closure trough as Q36;
- the discarded sign is restored from the raw tensor;
- Phase B is operationalized as cross-seam anti-orientation;
- traversal asymmetry is measured on equal windows without Fourier or fitted
  wave proxies.

**Verdict: exact enough to test.**

## Boundaries

- A negative tensor inner product is an operational anti-orientation, not by
  itself a universal physical Phase B.
- The target is a deterministic public quantum-network simulator, not
  hardware.
- Determinant-sign parity is diagnostic only; an ARA orientation change need
  not equal one particular matrix parity operation.
- The `0.94–0.95` expectation arose from Q36 and is therefore a prediction
  only for the untouched archive, not a prospective discovery in Q36.
- A source-family replication cannot establish universal ARA geometry.

