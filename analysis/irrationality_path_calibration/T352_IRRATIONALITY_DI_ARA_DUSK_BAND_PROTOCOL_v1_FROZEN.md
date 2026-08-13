# T352 frozen protocol v1 — Irrationality Di-ARA dusk band

**Frozen:** 11 August 2026, before T352 implementation or scoring  
**Evidence class:** synthetic known-referee transition/instrument calibration  
**Upstream instruments:** T348 path/history Di-ARA; T349 state/history separation; T350 parent-memory result

## Question

Directly coupled identities can possess a finite handover region rather than an
instantaneous boundary. T352 asks the narrower question: does the already
calibrated Irrationality Di-ARA resolve an equivalent finite transition band
when a structured non-closing path becomes a rationally closing path?

The result must distinguish three possibilities:

1. **resolved dusk:** a finite ordered band exists beyond unavoidable window
   mixing and then settles into the new identity;
2. **measurement dusk only:** the apparent band is no wider or more structured
   than an abrupt switch passed through the same window;
3. **no resolved band:** the Di-ARA coordinates jump or fail to recover the two
   endpoint identities.

## WHO

Known-referee circle paths use the T348 rational-rotation and irrational-
rotation families. Each matched identity contains the same irrational and
rational endpoint advances but one of three transition modes:

- abrupt switch;
- smooth ordered handover;
- order-destroyed handover containing the same transition increments in a
  shuffled order.

Both irrational-to-rational and rational-to-irrational directions are tested.
Calibration and holdout use disjoint rational denominators, irrational square-
root advances, transition durations, initial phases and seeds.

## WHAT

At each fixed sliding window retain the T348 path/history measurements:

\[
D_I(t)=\bigl(x_P(t),x_R(t),C_t(H)\bigr),
\]

where:

- `x_P`: finite/reused addresses `0` → open/densely resolving addresses `2`;
- `x_R`: relation-determined `0` → stochastic residual `2`;
- `C_t(H)`: uncompressed local closure history.

The operational **dusk band** is a contiguous, finite excursion away from both
stable endpoint cores while the ordered local rule changes, followed by return
to the new endpoint core. A residual excursion is not, by itself, proof of a
physical stochastic process; it means the frozen past-trained instrument cannot
fully explain the changing local rule.

## WHEN AND WHERE

Paths contain `3072` states. The declared transition is centred at state `1536`.
Use fixed `512`-state windows every `64` states. A window is:

- **pre:** wholly before the transition;
- **post:** wholly after the transition;
- **handover:** overlapping the transition or lying within half a window of
  either transition edge.

The local/sliding result is kept separate from a cumulative-prefix parent
reading. T352's primary dusk verdict concerns the local window because a
cumulative history is expected to retain the old identity after the local
handover has finished.

## HOW

### Referee paths

Let the circle state obey

\[
u_{t+1}=(u_t+a_t)\bmod1.
\]

One endpoint advance is irrational,
`sqrt(d)-floor(sqrt(d))`; the other is a coprime rational advance `p/q`.

- **Abrupt:** `a_t` changes at the declared centre.
- **Ordered:** `a_t` interpolates linearly between the two endpoint advances
  across a declared finite duration.
- **Shuffled:** the exact ordered-transition increment multiset is permuted
  only inside that duration. Its total transition advance and stable endpoints
  are therefore retained while local chronology is destroyed.

Calibration uses `q={5,7,9}`, `d={2,3,5}`, transition durations `{256,512}` and
12 replicates. Holdout uses `q={6,10,14}`, `d={13,17,23}`, transition durations
`{384,640}` and 16 replicates. Parameters are paired by listed index; they are
not cross-multiplied.

### Frozen local measurements

Address openness, stochastic residual and closure history retain the T348
formulas, using resolutions `{16,32,64,128,256}`, eight nearest neighbours and
lags through `min(128,W/4)`.

For each path calculate stable pre/post medians. Let

\[
b_R=\max(\widetilde x_{R,pre},\widetilde x_{R,post}),
\qquad
E_R=\max_{handover}x_R-b_R.
\]

The normalized residual-excess area is

\[
A_R=\operatorname{mean}_{handover}\max(x_R-b_R,0).
\]

The band width counts chronological window centres for which
`x_R >= b_R+0.25`, multiplied by the fixed stride. Coordinate roughness is the
total Euclidean step length in `(x_P,x_R)` over the handover, divided by the
number of steps.

### Frozen controls

1. **Endpoint recovery:** the pure pre/post windows must recover the appropriate
   T348 finite/open and determinate sectors.
2. **Abrupt control:** quantifies the maximum band produced by unavoidable
   window mixing alone.
3. **Order-destroyed control:** preserves transition increments and endpoints
   but destroys their smooth chronology.
4. **Direction reversal:** rational→irrational must reproduce the band without
   requiring the same signed `x_P` direction.
5. **Cumulative-prefix diagnostic:** reported separately to show retained parent
   history; it cannot define the local dusk verdict.

## Frozen gates

All gates are scored on untouched holdout paths. Intervals use 5,000 matched-
identity bootstraps, keeping the abrupt, ordered and shuffled versions of one
identity together.

1. **D1 endpoint recovery.** In both directions, stable irrational windows have
   median `x_P>1.25`, stable rational windows have median `x_P<0.75`, and all
   four stable endpoint groups have median `x_R<0.75`.
2. **D2 finite ordered excursion.** For both directions, ordered handovers have
   median `E_R>=0.25` with a 95% matched-bootstrap lower bound above zero.
3. **D3 reclosure.** In both directions, the median absolute difference between
   the final fully post-transition `x_R` and the stable post median is at most
   `0.10`; at least 90% of paths contain a non-empty stable post region.
4. **D4 beyond window smear.** Ordered-minus-abrupt `A_R` has a strictly
   positive 95% matched-bootstrap interval in both directions. Failure here
   produces the explicit verdict `MEASUREMENT DUSK ONLY`, even if D2 passes.
5. **D5 ordered versus destroyed chronology.** Shuffled coordinate roughness
   minus ordered roughness has a strictly positive 95% matched-bootstrap
   interval in both directions.
6. **D6 directional symmetry.** Both directions pass D2–D5, and their median
   ordered `E_R` values differ by at most `0.25` ARA.

All six gates must pass for `SUPPORTED [synthetic Irrationality Di-ARA dusk
instrument only]`. D1–D3 passing with D4 failing is `MEASUREMENT DUSK ONLY`.
Any other combination is `NOT SUPPORTED` with failed components retained.

## Required outputs

- complete local-window coordinates;
- one row per matched transition identity and mode;
- matched-bootstrap summaries and gate table;
- cumulative-prefix diagnostic;
- static figure showing the two directional Di-ARA trajectories, ordered versus
  abrupt residual profiles, ordered versus shuffled roughness, and the verdict;
- machine-readable JSON and an independently recomputed validation report.

## Evidence boundary

The generator explicitly supplies stable rational/irrational endpoints and a
declared changing rule. Passing T352 shows only that the existing Irrationality
Di-ARA instrument distinguishes a finite ordered transition from abrupt window
mixing and destroyed chronology under these controlled conditions. It does not
show that bubbles, day/night, a quantum system or nature universally implements
this dusk mechanism. A physical transfer test must independently measure enough
pre-transition history on both sides and preserve an independent coupling-
bearing consequence.
