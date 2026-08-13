# T350 frozen protocol v1 — tick-parent versus closure-front

**Frozen:** 11 August 2026, before implementation or scoring  
**Evidence class:** synthetic known-referee causal instrument calibration  
**Claim packet:** `T350_TICK_PARENT_CLOSURE_FRONT_CLAIM_PACKET_v1.md`

## WHO

Controlled continuous phase paths are evaluated in matched families. Every
family begins at the same phase, reaches the same integer-turn endpoint, and
shares an exactly identical final half-path after a declared merge. Only the
ordered early path differs:

- gradual reference;
- front-loaded movement;
- back-loaded movement;
- early burst;
- positive detour;
- negative detour;
- oscillatory detour;
- deterministic pseudo-stochastic bridge.

Calibration and untouched holdout sets use different turn counts, detour
amplitudes, durations and seeds.

## WHAT

At every tick retain the ARA phase position and an invertible ARA motion cut:

`x_position(t) = 2 frac(u_t)`

`x_motion(t) = 1 + tanh((u_t-u_{t-1})/v_ref)`.

The candidate history parent uses the existing T348/T349 path measurements:

- address openness `x_P`;
- stochastic residual `x_R`;
- an uncompressed six-lag closure/coherence signature `rho(H)`.

All history quantities are computed causally from prefixes. No future point is
used in a prefix measurement.

## WHEN

History is measured at normalized event fractions:

`1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8, 31/32, 1`.

The paths merge at `1/2`. Thus all ticks after the merge, including the final
closure tick, are exactly shared within a matched family.

Calibration durations are `513` and `1025`; untouched durations are `769` and
`1537`. Calibration turns are `2,4,6`; holdout turns are `3,5,7`.

## WHERE

The continuous unwrapped path `u(s)` is projected to the ARA circumference by
`frac(u)` while its signed local traversal remains available in
`x_motion`. The declared closure is the final integer-turn boundary.

## WHY

T349 established that compressed state and compressed history preserve
different information. T350 asks whether the history difference is already
carried by the ordered state ticks or is created only at the final closing
front.

## HOW

### Matched paths

For normalized time `s <= 1/2`, each family supplies a continuous early path
from the common start to the common merge. For `s > 1/2`, every member uses the
same linear suffix. Endpoint position, final motion and the complete post-merge
tick sequence are therefore identical within a matched configuration.

The pseudo-stochastic bridge is a frozen finite sine expansion with
seed-determined coefficients, so the same underlying continuous path can be
evaluated at multiple cadences without introducing new random draws.

### Existing history instrument

`x_P` and `x_R` retain the T348/T349 formulas. The closure signature is
calculated at lags nearest to the causal-prefix fractions
`1/64,1/32,1/16,1/8,1/4,1/2`. Each component is the magnitude of the mean
relative phase vector at that lag. History-vector distances use
`(x_P/2, x_R/2, rho_1,...,rho_6)` and therefore lie on a common 0–1 scale.

### Frozen comparisons

1. **Tick reconstruction:** invert `x_motion` and cumulatively recover `u_t`
   from the first phase.
2. **Same-present ambiguity:** compare each non-reference history to its
   gradual reference although the final half-path and current tick are exact
   matches.
3. **Emergence timing:** find the first causal prefix reaching half of the
   final matched history distance.
4. **Closure-jump share:** divide the last-prefix-to-closure distance change by
   the largest matched history distance observed over the event.
5. **Cadence stability:** compare final history vectors for the same continuous
   path at the two holdout durations.
6. **Local closure estimate:** in the common linear suffix, estimate ticks to
   the final closure from current remaining unwrapped distance divided by the
   current signed step.

## Frozen gates

### Parent-memory gates

1. **P1 reconstruction:** maximum unwrapped-path reconstruction error below
   `1e-9` on holdout trajectories.
2. **P2 retained history:** at least `70%` of holdout matched pairs retain a
   final history distance of at least `0.02`, and median final/peak distance is
   at least `0.30`, despite an identical final half-path.
3. **P3 pre-closure emergence:** median first-half-final emergence occurs by
   normalized time `0.75`, and median closure-jump share is below `0.25`.
4. **P4 cadence stability:** median matched-cadence final history distance is
   at most `0.08`, with at least `80%` at or below `0.12`.

All four must pass for `SUPPORTED [history behaves as a parent compression of
ordered tick states under this synthetic instrument]`.

### Pure closure-front gates

1. **F1 current sufficiency:** at least `90%` of matched pairs have final
   history distance at or below `0.02` and the median is at or below `0.01`.
2. **F2 boundary emergence:** median half-final emergence occurs at or after
   `0.90`, and median closure-jump share is at least `0.50`.

Both must pass for `SUPPORTED [history appears only at the pure closing front
under this synthetic instrument]`.

### Separate local-front gate

3. **F3 local handover locator:** within the exact common suffix, median
   absolute error of the current-state time-to-closure estimate is below one
   tick and its 95th percentile is below two ticks.

F3 is reported separately. It cannot rescue F1/F2 and does not contradict a
parent-memory result.

## Leakage controls

- Holdout turns, amplitudes, durations and seeds cannot alter formulas or
  thresholds.
- Family labels are referee truth only and do not enter the history
  calculations.
- The parent and front verdicts are computed independently.
- No `e`, Phi, reciprocal constant or fitted universal landmark is used.
- The final report must preserve failed gates and alternative explanations.

## Chart contract

Create one static research figure containing:

1. representative ARA-position trajectories showing gradual, abrupt and
   detour paths before their shared suffix;
2. matched history distance through time, with merge and closure marked;
3. final-state equality versus retained history distance;
4. tick reconstruction and cadence-stability distributions;
5. parent-memory and pure-front gate scorecards;
6. local closure-estimation error through the shared suffix.

Use blue and gold as the two primary roots, neutrals for controls, direct
labels and fixed honest scales. Save CSV, JSON, Markdown and PNG artifacts and
inspect the rendered figure before reporting.

## Evidence boundary

The test is deliberately synthetic and the paths are known. Passing establishes
an instrument relation, not a universal physical mechanism. Exact tick
reconstruction is partly algebraic; the load-bearing tests are retained
history under an identical suffix, causal emergence timing and cadence
stability.

