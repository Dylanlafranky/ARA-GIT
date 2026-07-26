# Q33 — Two-Axis Parent/Child 3.5 Projection Protocol v1 (FROZEN)

**Date frozen:** 26 July 2026  
**Ledger:** T287  
**Source:** Q27/Q28 public simulator cache, already fully opened  
**Design:** fixed development capacities (`t=0..249`) with unchanged
later-time evaluation events

## 1. Claim

Q33 tests the previously declared ARA path

\[
\underbrace{2}_{\text{complete same-rung span}}
+
\underbrace{\left(1+\frac12\right)}_{\text{full current contribution + child at half parent capacity}}
=
\frac72.
\]

The missing empirical statement is not the arithmetic. It is whether the Q32
endpoint child has parent-facing capacity `1/2`.

## 2. Source and fixed arrays

Use:

- `q27_derived_cache.npz`;
- `q28_connected_cache.npy`;
- branches `c2`, `c4`;
- seeds `0..99`;
- times `0..499`;
- all `66` unordered pair relations.

The full connected matrix is \(C_{b,s,t,p}\). Define:

\[
h=|\det C|^{1/3},\qquad
E=\lVert C\rVert_F^2.
\]

For every branch, seed and pair, freeze from `t=0..249`:

\[
s_h=Q_{0.95}(h),\qquad
s_E=Q_{0.95}(E).
\]

The local ARA coordinate is \(x=2h/s_h\). The parent-facing child capacity is
\(\rho=s_{E,c}/s_{E,p}\). No evaluation value enters either scale.

## 3. Splits and backward window

- development events: `t=8..242`;
- evaluation events: `t=258..492`;
- backward origin window: exactly eight earlier slices plus the event slice;
- forward handover interval: exactly one slice, inherited from Q32.

The source crest origin is the latest maximum local `x` in `[t-8,t]`. A child
pole origin is the latest minimum local `x` in the same interval.

## 4. Source events

An event requires:

1. source local `x(t) >= 1.5`;
2. `h(t) > h(t+1)`;
3. full-route source energy loss from the backward crest to `t+1` is positive;
4. the source pair is not itself one of the six active matching edges at `t`;
5. exactly one active edge touches each source endpoint;
6. deterministic sampling:

\[
(97s+53t+31p+11b)\bmod16=0.
\]

The two endpoint edges are the exact child routes. No future child value
participates in event or route selection.

## 5. Parent projection and route coordinates

For each exact or control child \(c\):

\[
\rho_{c\mid p}=\frac{s_{E,c}}{s_{E,p}},
\qquad
V_{c\mid p}=1+\rho_{c\mid p},
\qquad
L_{c\mid p}=3+\rho_{c\mid p}.
\]

Record:

- capacity ratio \(\rho\);
- absolute half-distance \(|\rho-0.5|\);
- vertical leg \(V\);
- complete path \(L\);
- child local `x` at its backward origin.

The two exact children remain separate observations and are also averaged once
per source event so a source with two routes is not double-weighted.

## 6. Transfer and angle diagnostics

For the full backward-origin route:

\[
\Delta E_p^+
=
\max(E_p(t_{\rm crest})-E_p(t+1),0),
\]

\[
\Delta E_c^+
=
\max(E_c(t+1)-E_c(t_{\rm pole}),0).
\]

Record individual \(\Delta E_c^+/\Delta E_p^+\) and the sum across the two
children. These are realised transfer diagnostics, not capacity definitions.

Define signed matrix movements

\[
D_p=C_p(t_{\rm crest})-C_p(t+1),
\qquad
D_c=C_c(t+1)-C_c(t_{\rm pole}).
\]

Record the ordinary angle between \(D_p\) and \(D_c\), plus the axial angle
\(\min(\theta,180^\circ-\theta)\). No exact angle is a success gate.

## 7. Controls

### Topology

From the active matching at the exact event time, take the four edges disjoint
from the source. Choose two distinct edges whose starting local coordinates
minimise total absolute distance from the two exact-child starting
coordinates. Exhaust all ordered two-edge assignments; break ties
lexicographically. This gives equal child count and baseline matching.

### Seed

Use seed `(s+37) mod 100` at the same time. Retain the active edge touching
each named source endpoint. If the source pair itself is active, that control
is unavailable for the event.

### Time

Use the same seed at

\[
t'=t_{\min}+((t-t_{\min}+137)\bmod N),
\]

within the event split, with enough backward and forward support. Retain the
active edge touching each named source endpoint. If the source pair itself is
active, that control is unavailable.

Control capacities, origins, movements and angles are calculated by the same
rules. Comparisons use only source events for which both exact and the named
control are finite.

## 8. Frozen primary gates

Eligibility:

- at least `5,000` evaluation source events;
- at least `100` evaluation branch/seed strata;
- at least `5,000` exact child routes;
- at least `2,000` paired source events for every control.

Cross-rung half-capacity:

1. pooled event-mean exact \(\rho\) median lies in `[0.40,0.60]`;
2. both `c2` and `c4` exact medians lie in `[0.35,0.65]`;
3. exact median \(|\rho-0.5|\) is at least `5%` lower than every control;
4. trial-cluster bootstrap probability that exact mean half-distance is lower
   than each control is at least `0.95`.

Backward pole:

5. the median exact child-origin local coordinate is at most `0.5`;
6. at least `50%` of exact source events have both child origins at or below
   `0.5`.

The `3.5` projection is **supported inside this simulator** only if all
eligibility, half-capacity and backward-pole gates pass.

If exact capacity is instead same-rung-like—pooled median in `[0.80,1.20]`—and
the half-capacity gates fail, label
`ORDERED HANDOVER, BUT Q32 CHILDREN ARE SAME-RUNG IN THIS ENERGY PROJECTION`.

Otherwise label `CROSS-RUNG 3.5 PROJECTION NOT SUPPORTED BY THIS
IMPLEMENTATION`. Insufficient eligibility produces `INCONCLUSIVE`.

## 9. Diagnostics that cannot promote the verdict

- immediate and backward-route realised transfer ratios;
- summed two-child transfer;
- signed and axial angle distributions;
- local starting and origin gradients;
- vertical/path values, which are algebraic transforms of \(\rho\);
- direct-capacity versus squared-amplitude alternative readings.

## 10. Validation and evidence fence

An independent validator must:

- verify source and protocol hashes;
- reopen both caches;
- recompute development scales from the connected matrices;
- deterministically reconstruct a bounded raw event sample;
- recompute headline capacity, origin, transfer and angle metrics from saved
  event rows;
- verify gate logic and artifact row counts.

The later split has been used by Q27–Q32 and is not blind. Bootstrap
probabilities measure stability within this simulator, not replication.
