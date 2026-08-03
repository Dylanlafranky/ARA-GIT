# T320 cross-domain Phi-pillar transfer protocol v1 — FROZEN

**Frozen:** 31 July 2026, Australia/Brisbane, before the new route statistics
were calculated.

## Corrected ARA claim

The value `2` is the complete octave route around one ARA cycle, not a raw
size ratio between neighbouring objects:

\[
\underbrace{A_k\rightarrow B\rightarrow A_{k+1}}_{
\text{mixed Phase A--Phase B--Phase A route}}
=1+1=2.
\]

The empirical proposal is that the direct route between the same same-phase
endpoints is the shorter Phi pillar:

\[
\underbrace{A_k\rightarrow A_{k+1}}_{
\text{direct same-phase route}}=\phi.
\]

Phase B must give the mirrored construction. The statement is therefore
about two routes between the same endpoints. It is not the statement that
every physical child/parent size ratio equals Phi.

## Shared route coordinate

For independently specified states \(A_0,B,A_1\) in a common metric space,
let

\[
d_0=d(A_0,B),\qquad d_1=d(B,A_1),\qquad c=d(A_0,A_1).
\]

Normalize the observed two-leg route to the ARA octave value `2` without
normalizing either leg separately:

\[
q=\frac{2c}{d_0+d_1}.
\]

The frozen Phi-pillar prediction is

\[
q=\phi.
\]

This is not forced by the normalization. The triangle inequality only forces
\(0\le q\le2\). For the exact regular-pentagon construction, the two legs are
equal and the angle at \(B\) is \(108^\circ\), which gives \(q=\phi\).

## Evidence classes and eligibility

The transfer audit keeps three classes separate:

1. **Exact geometry benchmark.** Recompute the regular-pentagon result and
   polygon controls. This is deductive, not empirical.
2. **Ordered-scale calibration.** Reuse the already validated sunflower
   lineage result only as evidence that Phi can be a same-phase scale carrier.
   It does not observe both physical routes and cannot pass the new route
   test.
3. **Raw physical transfer.** Use the public triple-pendulum record because it
   supplies three simultaneously measured nested arms in one mechanical
   state space. No other existing ARA archive is promoted into this class
   unless it contains three independently identified, commensurate states.

Existing quantum Q46/Q47, Solar-System T317 and Phi-carrier T302/T305 results
will be classified for eligibility before their numerical outcomes are used.
A dataset is ineligible for the route test if its required third state is
assigned by complement, if its tiers have incompatible units, or if the
tested Phi coordinate answers a different question.

## Triple-pendulum transfer test

### Source and split

Public dynamicslab *MultiArm-Pendulum*, Zenodo
`10.5281/zenodo.6633719`.

- development only for metric scales: free-swing runs 1 and 2;
- frozen evaluation: free-swing run 3;
- transfer only: driven triple-pendulum run 1.

### Predeclared hierarchy

The same adjacent-rung ordering used by the earlier pendulum work is retained:

\[
\underbrace{\text{arm 3}}_{A_0\text{ / child scale}}
\rightarrow
\underbrace{\text{arm 2}}_{B\text{ / intermediate scale}}
\rightarrow
\underbrace{\text{arm 1}}_{A_1\text{ / larger scale}}.
\]

This is an ARA operational assignment, not a standard claim that pendulum arm
number is an ontological scale.

### Common state space

At each time sample, arm \(j\) is represented by its rest-centred angular
state

\[
z_j(t)=\left(\frac{\theta_j(t)}{s_\theta},
              \frac{\dot\theta_j(t)}{s_\omega}\right),
\]

where \(s_\theta\) and \(s_\omega\) are pooled robust scales calculated once
from all three arms in development runs 1 and 2. The same two scales are used
for every arm and frozen evaluation sample. Euclidean distance in this state
space supplies \(d\).

### Phase eligibility

A sample is eligible when the endpoint state vectors have the same
orientation and the middle state has the opposite orientation:

\[
z_3\cdot z_1>0,\qquad z_3\cdot z_2<0,\qquad z_1\cdot z_2<0.
\]

Samples whose state norm or either route leg is numerically zero are excluded.
To reduce oversampling, results are summarized in non-overlapping `0.10 s`
windows before run-level medians are formed.

The two mirror branches are fixed by the sign of the arm-1 rest-centred angle.
They must give compatible \(q\) distributions.

### Frozen controls

- route candidates: \(1\), \(\sqrt2\), \(1.5\), \(\phi\), \(\sqrt3\), `2`;
- angle candidates: \(90^\circ,108^\circ,120^\circ,135^\circ,144^\circ,180^\circ\);
- time-shift the middle arm by `17%`, `31%` and `47%` of the record while
  leaving both endpoints fixed;
- swap the endpoint labels, which must leave \(q\) invariant;
- report the equal-leg ratio \(\min(d_0,d_1)/\max(d_0,d_1)\) rather than
  assuming an isosceles triangle.

### Frozen physical-transfer gates

The triple-pendulum route is **supported** only if all hold on run 3:

1. Phi uniquely minimizes median absolute error in \(q\) among the fixed
   candidates;
2. `108°` uniquely minimizes median absolute included-angle error;
3. the median equal-leg ratio is at least `0.90`;
4. both mirror branches independently select Phi;
5. the real alignment has lower median Phi error than every shifted-middle
   control.

Otherwise it is mixed or not supported. The driven record is transfer-only
and cannot change the verdict.

## Cross-domain verdict rule

The phrase **physically cross-domain confirmed** is prohibited unless at
least two independent raw physical domains pass the same route statistic.
Exact geometry and Fibonacci-selected scale families do not count as two
physical replications.

If fewer than two existing domains are eligible, the correct outcome is
**insufficient eligible domains**, not a forced confirmation or rejection.

## Boundaries

- Normalizing the indirect route to `2` is ARA bookkeeping; only \(q\), leg
  balance, angle and controls are non-forced observations.
- A failure of the pendulum mapping rejects this three-arm operationalization,
  not the exact pentagon identity.
- A pass would show the same route geometry in one physical state-space cut;
  it would not prove that every sphere, field or scale transition uses Phi.
