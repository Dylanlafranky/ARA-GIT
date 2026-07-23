# PN41 — Prime Thalweg and Phi Handover Report

**Date:** 2026-07-23  
**Protocol:** `PN41_PRIME_THALWEG_PHI_PROTOCOL_v1_FROZEN.md`  
**Verdict:** **PHI NOT SUPPORTED IN THE FROZEN LOCAL-HANDOVER COORDINATE**  
**Unexpected descriptive result:** a replicated local split near **one third**.

## Answer first

Dylan's river/valley idea produced a valid new coordinate: follow the nearest number-channel that remains open as
successive prime-factor gates close composite candidates. The resulting path is an exact discrete thalweg through
the factor-collision terrain and ends at the first prime above each anchor.

The preregistered question was whether a killed channel hands over near the mirrored golden position

\[
2-\phi=0.38196601125\ldots
\]

inside the newly opened survivor interval. It did not. Across two untouched million-integer regions, the best
fixed landmark by mean absolute distance was `1/3`, the unrestricted optimum was `0.334`, and the median folded
handover split was exactly `1/3`. Phi was significantly farther away than the one-third control in both regions.

This rejects **this specific local split as the Phi location**. It does not test every possible Phi role in ARA.
In particular, path curvature, cross-rung drift, or another independently defined handover operator would be a new
hypothesis and must be frozen separately.

## What was tested

For each deterministic anchor `N`:

1. Start at the first odd number above `N`.
2. If that candidate is composite, its least prime factor is the next natural gate that closes the channel.
3. At that gate, locate the surviving neighbours `L < U < R` around the killed candidate `U`.
4. Move to `R` and repeat until the first prime above `N` is reached.

The handover coordinate was frozen as

\[
f=\frac{U-L}{R-L},
\qquad
m=\min(f,1-f).
\]

`m` folds left- and right-oriented handovers onto the same `[0,0.5]` scale. Phi's frozen target was
`m = 2-phi`. Fixed controls were `0.25`, `1/3`, `0.40`, and `0.50`.

Two untouched target intervals were used:

- Target A: `[4,010,000,000, 4,011,000,000)`
- Target B: `[4,020,000,000, 4,021,000,000)`

Each contained 1,000 predeclared anchors. Every anchor was weighted equally, so anchors with long paths could not
dominate the result merely by producing more handovers.

## Results

| Measure | Target A | Target B |
|---|---:|---:|
| Anchors | 1,000 | 1,000 |
| Anchors with at least one handover | 878 | 891 |
| Visible handovers | 2,076 | 2,077 |
| Mean handovers per anchor | 2.076 | 2.077 |
| Mean folded split | 0.330044 | 0.330008 |
| Median folded split | 0.333333 | 0.333333 |
| Best unrestricted landmark | 0.334 | 0.334 |
| Mean absolute distance to Phi mirror | 0.115358 | 0.113490 |
| Mean absolute distance to `1/3` | **0.110964** | **0.109643** |
| Phi minus `1/3` distance | +0.004394 | +0.003847 |
| Paired-bootstrap 95% interval | `[+0.001999, +0.006797]` | `[+0.001409, +0.006353]` |

Positive `Phi minus 1/3` values mean Phi was worse. Both confidence intervals are wholly above zero. All four
frozen Phi-support gates failed in both targets.

The handovers were a rational, discrete family rather than a smooth cloud. The largest exact peaks were:

| Folded split | Target A events | Target B events |
|---|---:|---:|
| `1/2` | 393 | 379 |
| `1/3` | 202 | 198 |
| `2/5` | 194 | 211 |
| `1/4` | 177 | 164 |

Half had the largest narrow-window occupancy because exact central closures are common. One third nevertheless had
the lowest average distance across the whole distribution. Those statements measure different properties and are
not contradictory.

## Plain-language interpretation

Imagine every small prime as closing roads through the integers. Begin just above a chosen number and stand in the
nearest road that is still open. When a later gate reveals that road to be composite, it closes and the path jumps
to the next open road. Repeating this eventually lands on the next prime.

The question was: where does the old road sit inside the gap between the two roads that remain open? If Phi governed
this handover, it should repeatedly sit about 38.2% of the way across after orientation is folded. Instead, the
typical split sat at one third, and this repeated in both fresh regions.

So the intuition that there was a valley-like moving path was productive. The first exact measurement of that path
did reveal a stable geometry, but its local landmark was triangular rather than golden. In ARA language, this looks
more like a possible `Information^3` or three-part closure signature than a Phi handover. Scientifically, that is
only a candidate interpretation: ordinary integer gap ratios and sieve geometry may fully explain the thirds.

## Terrain visualization

The bounded view uses every integer, rather than plotting only primes. It contains:

1. the complete child-phase terrain across the ARA diameter;
2. the survivor field as factor gates accumulate, with the nearest-open-channel staircase overlaid; and
3. exact collision heights, where primes are the zero-collision points.

For the displayed anchor `4,010,000,000`, the path begins at `4,010,000,001`, undergoes five visible handovers,
and terminates at the first prime, `4,010,000,047`. Its successive folded splits are `1/2`, `1/3`, `1/3`,
`5/11`, and `3/28`. This example shows why one handover cannot represent the whole route.

The visualization is explanatory only; no additional statistical endpoint was chosen from it.

## What is established, and what is not

**Established by PN41:**

- the proposed thalweg can be defined exactly without Fourier or fitted curves;
- it is an incremental-sieve lineage through composite-collision terrain;
- it reaches the first prime above every tested anchor;
- its local handovers have a strongly discrete rational structure;
- the mean/median structure replicated near one third across both regions.

**Not established by PN41:**

- a Phi local-handover law;
- a new or faster prime-search algorithm;
- an ARA-specific cause of the one-third result;
- a universal triangle law from this one number-theoretic representation.

The exact prime endpoint is inherited from complete factor-gate arithmetic. ARA contributes a relational geometry
and a useful decomposition of the route; it has not reduced the required arithmetic in this test.

## Independent validation

A separate validator reconstructed all 2,000 cascades and all 4,153 handovers by direct trial division, without
reusing PN41's segmented least-factor window or cascade implementation. It also verified:

- every saved endpoint was the first prime after its anchor;
- every gate, killed candidate, adjacent survivor, split, and folded split;
- all headline summaries and the `0.334` grid optima;
- every cell and prime marker in the bounded terrain data.

All checks passed with zero cascade mismatches.

## Files

- `pn41_prime_thalweg_phi.py` — executable test
- `PN41_PRIME_THALWEG_PHI_PROTOCOL_v1_FROZEN.md` — frozen protocol
- `PN41_PRIME_THALWEG_PHI_RESULTS.json` — complete anchor and handover records
- `PN41_PRIME_THALWEG_TERRAIN.json` — compact visualization data
- `validate_pn41_prime_thalweg_phi.py` — independent validator
- `PN41_PRIME_THALWEG_PHI_VALIDATION.json` — validation record

## Status

PN41 is complete. Its honest result is:

> **The prime thalweg exists as an exact nearest-survivor path. Its frozen local split is not Phi; it is centred
> much closer to one third in both tested regions.**

