# PN41 — Prime Thalweg and Phi Handover (v1, frozen)

**Frozen:** 2026-07-23, before either target interval was generated or inspected.

## Question

When the nearest open number-channel is closed by a newly reached prime gate, does its local handover divide the newly opened interval near the mirrored golden position?

This is the first operational test of Dylan's river/thalweg proposal. It is deliberately different from earlier tests of fixed Phi occupancy, a golden angle, or a fixed Phi carrier.

## Fresh deterministic intervals

- Target A: `[4,010,000,000, 4,011,000,000)`
- Target B: `[4,020,000,000, 4,021,000,000)`
- In each interval use 1,000 anchors: `low + 250 + 1,000*i`, for `i=0..999`.
- Anchors are fixed without looking at their next-prime labels or handover paths.

## Natural gate order and thalweg path

For each anchor `N`:

1. Begin with gate `2` and select the first surviving integer above `N`.
2. If the current candidate is composite, its least prime factor `p` is the next natural sieve gate that closes it.
3. After adding every prime gate through `p`, find the adjacent surviving numbers `L < U < R` around the killed candidate `U`.
4. Move the channel from `U` to `R` and repeat until the first fully surviving prime is reached.

This is an exact incremental-sieve lineage. It compresses visible handovers but does not remove silent gate work.

## Frozen handover coordinate

At each visible release define

\[
f=\frac{U-L}{R-L},
\qquad
m=\min(f,1-f),
\]

where `m` is the orientation-free local split on `[0,0.5]`.

The predeclared Phi target is

\[
m_\phi=2-\phi=0.3819660112501051.
\]

Fixed comparison landmarks are:

- quarter: `0.25`
- third: `1/3`
- two-fifths: `0.40`
- half: `0.50`

## Weighting and metrics

- Each anchor with at least one handover receives equal weight.
- Within an anchor, average over its handovers before averaging anchors.
- Primary distance: mean absolute distance from each landmark.
- Secondary occupancy: share within `±0.025` of each landmark, using the same equal-anchor weighting.
- Grid diagnostic: best landmark on `[0.05,0.50]` in steps of `0.001` by mean absolute distance.
- Uncertainty: paired anchor bootstrap, 5,000 resamples per target, deterministic seeds `4100000000` and `4020000000`.

## Frozen success rule

Phi is supported as this particular thalweg-handover landmark only if **all** of the following hold independently in Target A and Target B:

1. Phi has lower mean absolute distance than every fixed comparison landmark.
2. The 95% paired-bootstrap interval for `Phi distance - best-control distance` is wholly below zero.
3. Phi has greater `±0.025` occupancy than every fixed comparison landmark.
4. The unrestricted grid optimum lies within `0.02` of `2-phi`.

Otherwise the result is mixed or not supported. No alternative Phi coordinate may replace this one after reveal.

## Terrain visualization

After scoring, generate a bounded descriptive terrain around the start of Target A:

- every integer, not only primes;
- raw child ARA phase density on `[0,2]`;
- exact collision count and prime/quiet labels;
- survivor field across increasing natural prime-gate rungs;
- the nearest-survivor staircase overlaid as the operational thalweg.

The visualization is explanatory. It is not an additional statistical endpoint.

## Interpretation boundary

- A positive result would support a golden local split in this exact handover coordinate, not a universal Phi law.
- A negative result would reject this coordinate while leaving other independently specified Phi mechanisms open.
- The exact prime recovery is established sieve arithmetic expressed through an ARA valley/river lens; it is not a faster prime algorithm.

