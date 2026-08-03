# T307 — Complex irrationality quadrant in the muon-Fusion overlap model

**Frozen:** 3 August 2026, before the `N=257..1024` outcomes were calculated  
**Status at freeze:** unrun  
**Originator of the ARA hypothesis:** Dylan La Franchi

## Question

Does the newly specified ARA complex quadrant carry ordered, recoverable
information in the existing muon-catalysed-Fusion scheduling model, or do the
same four signs appear without useful lineage structure?

This is a test of the idealised Kou–Chen-derived scheduling instrument used by
T305/T306. It is **not laboratory muon data** and cannot establish that natural
muon dynamics use these constants.

## Fresh range and fixed resources

- Fresh prefixes: every integer `N=257..1024`.
- Source phases: the same `128` equally spaced phases as T305/T306.
- Arrival families: `beam7`, `beam7_cycle23`, and `beam7_decay`.
- Fixed pulse width: `0.15/1024` of the unit cycle.
- Every carrier and every prefix receives the same pulse count, width, peak,
  and energy per pulse.

The narrower width is frozen because carrying T305's `0.15/64` width to 1,024
pulses would saturate much of the observation circle and destroy the
phase-resolved observable. Width is not recomputed by prefix.

## Primary relation and controls

The primary pair is

\[
\alpha_L=\phi^{-1},
\qquad
\alpha_R=e^{-1}.
\]

The carrier centres remain

\[
c_k(\alpha)=\operatorname{frac}(k\alpha).
\]

Fixed pair controls are inherited from T306:

1. anti-Phi versus `1/e`;
2. Phi-Time versus `sqrt(2)-1`;
3. `1/e` versus `sqrt(2)-1`;
4. Phi-Time versus `pi-3`;
5. `1/e` versus `pi-3`;
6. `sqrt(2)-1` versus `pi-3`.

## Two raw cuts and the complex ARA state

For pair `(L,R)`, prefix `N`, arrival family `f`, and source phase `theta_j`,
retain the complete phase-resolved contrast

\[
D_{N,f}(\theta_j)=F_{L,N,f}(\theta_j)-F_{R,N,f}(\theta_j).
\]

Do not reduce this vector to a percentile. Its perpendicular cosine and sine
cuts form the complex first circular moment

\[
z_{N,f}
=
\frac{2}{128}\sum_{j=0}^{127}
D_{N,f}(\theta_j)e^{-i\theta_j}.
\]

The two cuts are therefore defined before exposure:

\[
u_{N,f}=\Re z_{N,f},
\qquad
v_{N,f}=\Im z_{N,f}.
\]

This is a joint handover observable: it measures the directed relation between
the two schedules inside the same muon-arrival field.

## Local quadrant measurement

For adjacent valid states,

\[
q_N=\frac{z_{N+1}}{z_N}=s_Ne^{i\delta_N},
\]

\[
\log s_N=\log|q_N|,
\qquad
\delta_N=\arg q_N\in(-\pi,\pi].
\]

The four states are:

| radial sign | phase sign | ARA label |
|---|---|---|
| `log(s)>0` | `delta>0` | expanding, forward |
| `log(s)>0` | `delta<0` | expanding, reverse |
| `log(s)<0` | `delta>0` | contracting, forward |
| `log(s)<0` | `delta<0` | contracting, reverse |

For each series, a state is amplitude-valid when both endpoints exceed

\[
h=\max\left(10^{-12},10^{-6}\operatorname{median}_N|z_N|\right).
\]

Values are never clamped. Exact sign boundaries within `1e-12` are recorded
separately.

## Frozen train/holdout prediction

- Training prefixes: `257..640`.
- Holdout prefixes: `641..1024`.

The ARA predictor groups training transitions by the quadrant of the previous
`q`. Within each group it stores the component-wise median of the following
complex ratio. On holdout it uses only the already-observed previous quadrant:

\[
\widehat z_{N+1}
=
\widetilde q_{\,Q(q_{N-1})}z_N.
\]

Fixed baselines:

1. persistence, `z_hat(N+1)=z_N`;
2. one local multiplicative continuation, `z_hat(N+1)=q_(N-1) z_N`;
3. one global component-wise median training ratio;
4. a generic complex affine AR(2), fitted only on training data;
5. `1,000` deterministic temporal shuffles of the training
   previous-state/next-ratio association (`seed=3072026`).

Errors are mean absolute complex error divided by the holdout median `|z|`.
No target-by-target normalization is used.

## Broken-lineage controls

For the primary pair only, repeat the construction after cyclically shifting
the right-hand schedule responses by fixed prefix offsets `17`, `31`, and
`47`, separately inside training and holdout. These controls preserve each
schedule's marginal distribution while breaking the declared same-prefix
lineage.

## Frozen gates

### G0 — implementation and source integrity

- all output overlap values lie in `[0,1]`;
- the two stored real cuts reproduce the reported complex `z`;
- an independent direct recomputation matches selected states to `1e-10`;
- every output row has a unique declared grain.

### G1 — usable four-quadrant coordinate

Pass when at least two of the three primary arrival families have at least
`90%` valid adjacent steps and contain all four non-boundary quadrants.

G1 establishes coordinate usability only; it is not evidence of an ARA law.

### G2 — ordered lineage information

For an arrival family, the ARA quadrant predictor passes when its holdout
error is below:

- persistence;
- global-ratio continuation;
- generic affine AR(2); and
- the fifth percentile of the `1,000` shuffled errors.

G2 passes overall when this occurs in at least two of the three primary
families. The local-ratio continuation remains a separately reported strong
baseline and is not required to lose: it uses more continuous state
information than the four-state ARA compression.

### G3 — primary-pair specificity

For each family, rank all seven fixed pairs by the ARA predictor's improvement
over the best of persistence, global ratio and affine AR(2). G3 passes when
the primary Phi-Time/`1/e` pair ranks first in at least two families.

### G4 — intact lineage versus broken lineage

G4 passes when the intact primary pair's ARA prediction error is lower than
all three fixed broken-lineage errors in at least two families.

## Post-gate landmark audit

Only after G0–G4 are scored, inspect multi-lag radial ratios for lags
`1,2,4,8,16,32,64`. Compare, in log distance, the provisional
`1/e <-> Phi` radial landmarks with:

- reciprocal exponential `1/e <-> e`;
- reciprocal golden `1/Phi <-> Phi`;
- unity/persistence.

This audit is descriptive. It cannot rescue a failed ordered-lineage test,
and the ARA normalization is not applied before the raw ratios are reported.

## Verdict language

- **Quadrant structure supported in this model:** G0–G4 pass.
- **Generic complex structure only:** G0–G2 pass but G3 or G4 fails.
- **Coordinate recovered without predictive support:** G0/G1 pass and G2
  fails.
- **Not supported / invalid:** G1 fails, or G0 fails respectively.

No verdict from this protocol is evidence that physical muons contain a
literal universal `1/e <-> Phi` mechanism.
