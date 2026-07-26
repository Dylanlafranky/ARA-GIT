# Q32 frozen protocol — edge-child pole handover before the 3.5 route

**Frozen:** 26 July 2026, before Q32 outcome calculation  
**Test ID:** `Q32-EDGE-CHILD-POLE-HANDOVER-v1`  
**Ledger:** T286  
**Test class:** retrospective source, development-selected lag, unchanged later-half evaluation

## Question

When a connection-rich source relation begins releasing, is its immediate
active child already near an asymmetric ARA pole and does that child
subsequently accumulate more relation amplitude than equally selected false
children?

This test precedes rather than assumes the `1.5/3.5` route.

## Source and fixed split

Reuse the public Q27/Q28 source and derived cache:

- Zenodo DOI `10.5281/zenodo.16753415`;
- extracted HDF5 SHA-256
  `0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb`;
- two connectivity strata, 100 seeds each, 500 ordered slices, 66 pair
  relations;
- development source times `0–242`;
- evaluation source times `250–492`;
- candidate lags `1–6`.

The source is already open. The later half is therefore an unchanged internal
replication partition, not a fresh blind dataset.

## ARA coordinate

Use Q27 unchanged:

\[
h_{uv}(t)=|\det C_{uv}(t)|^{1/3},
\qquad
s_{uv}=Q_{0.95}\{h_{uv}(t):0\le t<250\},
\]

\[
x_{uv}(t)=\frac{2h_{uv}(t)}{s_{uv}}.
\]

Exclude a relation only when `s < 1e-10`.

## Source event fixed without child outcomes

For source pair \(S=(u,v)\), endpoint \(e\in\{u,v\}\), and source time \(t\):

1. require `x_S(t) >= 1.5`;
2. require one-step source release
   \(r_1=x_S(t)-x_S(t+1)>0\);
3. apply Q28's deterministic sampler

\[
(97\,seed+53\,t+31\,pair+17\,endpoint+11\,branch)\bmod16=0.
\]

No child future value is used to admit the source event.

## Children and controls

At time `t`, identify the six source-deposited active relations.

### Exact pole child

Among active relations other than the source that share endpoint `e`, choose
the relation with the smallest finite `x(t)`. Break ties by pair index.

### Topology control

Among active relations sharing neither source endpoint, choose the relation
with the smallest finite `x(t)`. Break ties identically.

### Seed control

In seed `(seed+37) mod 100`, at the same time and named endpoint, apply the
same active-adjacent, minimum-starting-`x` rule.

### Time control

Within the same 250-slice half, shift source time by `+137` modulo the support
that allows the current lag. At that shifted time, apply the same
active-adjacent, minimum-starting-`x` rule.

All four routes therefore receive the same regression-to-the-mean opportunity.
An event enters a control comparison only when that control exists.

## Frozen outcomes at lag L

For each selected child \(C\):

\[
g_C(L)=x_C(t+L)-x_C(t).
\]

Also calculate cumulative positive movements:

\[
R_S(L)=\sum_{k=0}^{L-1}\max[0,x_S(t+k)-x_S(t+k+1)],
\]

\[
A_C(L)=\sum_{k=0}^{L-1}\max[0,x_C(t+k+1)-x_C(t+k)].
\]

The overlap is:

\[
O_C(L)=R_S(L)A_C(L).
\]

The descriptive flow coordinate is:

\[
x_{\rm flow}(L)=\frac{2A_C(L)}{R_S(L)+A_C(L)}
\]

when the denominator is positive.

Record:

- child starting `x`;
- signed later gain `g`;
- cumulative source release `R`;
- cumulative child accumulation `A`;
- overlap `O`;
- flow coordinate;
- fraction with `x_child(t) <= 0.25`;
- fraction with `x_child(t) <= 0.5`;
- fraction with `g > 0`;
- joint direction fraction `R>0 and g>0`.

## Development-only lag selection

For each lag `1–6`, calculate the trial-weighted mean exact-minus-control
advantage for signed child gain:

\[
S_L
=
\frac13\sum_{c\in\{topology,seed,time\}}
\left(\bar g_{\rm exact}-\bar g_c\right).
\]

Select the lag with maximum `S_L`; ties choose the smaller lag. Freeze that
lag for the evaluation half. No evaluation value may alter it.

## Child-gradient diagnostic

Retain all exact active adjacent children, not only the pole-nearest one. Bin
their starting coordinates:

- pole: `x <= 0.5`;
- lower gradient: `0.5 < x < 1`;
- upper gradient: `1 <= x < 1.5`;
- crest: `x >= 1.5`.

At the selected lag, report signed gain and positive accumulation by bin. This
diagnostic is secondary and does not choose the lag.

## Trial-cluster bootstrap

Aggregate each metric within each `(branch, seed)` stratum. Resample the 200
trial strata with replacement for 2,000 deterministic draws using seed
`32032`. Report probabilities that exact exceeds each control. Do not treat
individual source events as independent bootstrap units.

## Frozen gates

### Eligibility

- `E1`: at least 10,000 evaluation source events with an exact child;
- `E2`: at least 100 evaluation trial strata;
- `E3`: at least 2,000 paired events for every primary control.

### Pole origin

- `P1`: at least 50% of exact pole-nearest children begin at `x <= 0.5`;
- `P2`: exact starting `x` is at least `0.05` lower than the topology control;
- `P3`: cluster-bootstrap probability for P2 is at least 95%.

### Incoming child movement

- `I1`: evaluation exact signed gain is positive;
- `I2`: exact signed gain exceeds topology, seed and time controls by at least
  `0.02` ARA units;
- `I3`: cluster-bootstrap probability that exact gain exceeds each control is
  at least 95%.

### Coupled release/accumulation

- `C1`: exact overlap exceeds each control by at least 5% relative to that
  control;
- `C2`: cluster-bootstrap probability that exact overlap exceeds each control
  is at least 95%;
- `C3`: the direction of exact-minus-control gain is the same in both `c2` and
  `c4`.

### Gradient consistency

- `G1`: pole-bin exact children have signed gain at least as large as crest-bin
  exact children on the evaluation half.

## Interpretation

- all `P`, `I`, `C` and `G` gates pass: **supported inside this simulator**;
- incoming and coupled-movement gates pass but pole gates fail:
  **ordered child transfer without pole-origin support**;
- pole gates pass but incoming/control gates fail:
  **asymmetric child position without transfer support**;
- otherwise: **not supported by this implementation**.

No outcome promotes the object to a universal singularity flip or Phase B.
A revised `3.5` route may be frozen only after Q32 is reported without
changing this protocol.

