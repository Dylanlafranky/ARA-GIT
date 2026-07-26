# Frozen protocol — Q10 unresolved-\(H\) two-axis ARA

**Protocol ID:** `Q10-UNRESOLVED-TWO-AXIS-v1`  
**Ledger ID:** `T269`  
**Frozen:** 24 July 2026, after Q9 outcomes were open but before calculating Q10 two-axis coordinates, quadrant
allocations or loop diagnostics  
**Test class:** post-outcome geometry-first instrument calibration  
**Source:** Q9's `88` public Bell trajectory allocations

## Input identity

Primary unknown waveform:

\[
H(t)=2-K(t)-R(t).
\]

Robustness counterpart:

\[
H_P(t)=I_{\rm unresolved}(t)/2.
\]

Each condition/state trajectory contains eleven strictly increasing wait coordinates. Ramsey and Hahn are
analyzed separately because their physical time grids differ.

## Axis 1 — amplitude

For each trajectory:

\[
x_H(t)=2\frac{H(t)-H_{\min}}{H_{\max}-H_{\min}}.
\]

Here `0` and `2` are the observed local minimum and maximum on this trajectory, not universal physical
singularities.

## Axis 2 — opening/closing rate

Calculate \(\dot H(t)\) with the second-order nonuniform three-point derivative used by
`numpy.gradient(H,t,edge_order=2)`.

Let:

\[
v_{\max}=\max_t|\dot H(t)|.
\]

Then:

\[
y_H(t)=1-\operatorname{clip}\left(\frac{\dot H(t)}{v_{\max}},-1,1\right).
\]

- \(y_H<1\): opening/accumulation;
- \(y_H=1\): locally still/turning;
- \(y_H>1\): closing/release.

## Information³ relation plane

\[
C_H(t)=(x_H(t)-1)+i(y_H(t)-1),
\]

\[
R_H(t)=|C_H(t)|,
\qquad
\theta_H(t)=\operatorname{atan2}(y_H(t)-1,x_H(t)-1).
\]

The four joint quadrants are assigned from low/high amplitude and opening/closing. Each sample receives a
trapezoidal time weight:

\[
w_0=(t_1-t_0)/2,\quad
w_n=(t_n-t_{n-1})/2,\quad
w_i=(t_{i+1}-t_{i-1})/2.
\]

Quadrant TE shares are:

\[
T_q=2\frac{\sum_{i\in q}w_i}{\sum_iw_i},
\qquad
\sum_qT_q=2.
\]

## Geometry diagnostics

For each trajectory report:

- amplitude/rate correlation;
- ordered relation-plane path length;
- start-to-end closure gap;
- chord-closed signed area;
- opening and closing time shares;
- number of derivative-sign changes;
- quadrant TE composition.

A closed-loop candidate requires:

- at least `15%` time in opening and `15%` in closing;
- start-to-end relation-plane gap at most `0.35`.

This classification is descriptive, not a pass gate.

## Frozen gates

All gates must pass for `CALIBRATED`.

1. `U1`: `88` unique records form eight eleven-point, strictly increasing, nonzero-range trajectories.
2. `U2`: every \(x_H,y_H\) is finite and lies inside `[0,2]` within `1e-12`.
3. `U3`: inverse amplitude reconstruction returns every \(H\) with maximum error at most `1e-12`.
4. `U4`: \(C_H,R_H,\theta_H\) reconstruct both centred axes with maximum error at most `1e-12`.
5. `U5`: every four-quadrant TE composition sums to `2` within `1e-12`.
6. `U6`: amplitude and rate axes each have nonzero variance in every trajectory.
7. `U7`: median pairwise amplitude-axis correlation across Bell states is at least `0.80` separately in Ramsey
   and Hahn.
8. `U8`: median pairwise rate-axis correlation across Bell states is at least `0.40` separately in Ramsey and
   Hahn.
9. `U9`: repeating the entire construction with \(H_P=I_{\rm unresolved}/2\) gives median pointwise two-axis
   distance at most `0.25`.

## Boundaries

- This is a descriptive reconstruction of an already-observed unknown waveform, not forecasting.
- Only eleven samples exist per trajectory. A missing closed loop can mean the cycle is longer than the observed
  window or temporally under-sampled.
- The derivative axis is more noise-sensitive than the amplitude axis.
- Relation-plane lobes identify dynamical components, not their physical causes.
- The amplitude maximum is local to the measured record.

