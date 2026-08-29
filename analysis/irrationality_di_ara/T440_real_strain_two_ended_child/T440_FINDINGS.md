# T440 findings — real-strain two-ended Space/Time child reconstruction

## Answer first

**ARA geometry verdict:** the real-strain parent coordinates form a persistent,
record-specific inverse Space/Time band. All `20/20` locked detector streams
had a negative parent relation (median Spearman `-0.589`, range `-0.830` to
`-0.049`) without being forced to sum to two. When the twenty streams are
aligned to the published event time, the median Space/Connection parent rises
away from the Time/Movement parent, reaches a difference of `+0.884` at
`-49.4 ms`, then the ordering reverses between `+17.3` and `+21.2 ms`; by
`+60.4 ms` the difference is `-0.470`. This is a visible parent-scale
separation-and-return/reversal shape and is the most important descriptive
result in T440.

**Frozen benchmark verdict:** the particular magnitude-derived child localizer
was **not supported**. None of ten locked events satisfied all four registered
localization gates in both H1 and L1; the protocol required seven. That verdict
rejects this operational child instrument. It does **not** erase the parent
geometry above or turn the run into an empty result.

The independently paired Space-end/Time-end histories also had a common-grid
median Bhattacharyya overlap of `0.9146`, above all 5,000 wrong-event
permutation controls (`p=0.00020`). The relation therefore retains a specific
same-record identity. What is unresolved is whether the event-aligned reversal
is a merger-localized handover, a broader detector/background response, or a
mixture: the present off-source controls preserve summary statistics but not
an equivalently aligned parent-history shape.

> **Future-reader rule:** do not summarize T440 only as “failed the gates.” The
> frozen gates decide the registered child-localization claim. The geometry
> verdict separately retains the inverse parent band, event-aligned
> separation/reversal, same-record identity and broad child-plane texture.

## What was measured

Each detector supplied two independent 0–2 parent histories:

- Space/Connection parent: spectral amount plus spectral concentration;
- Time/Movement parent: spectral-centroid position plus adjacent-spectrum
  redistribution.

Their sum was not constrained. Across evaluation streams, the median standard
deviation of `P_S+P_T` was `0.368`, and the median parent Spearman relation was
`-0.589`; the histories are opposed on average but are not a forced mirror.

The candidate child was approached independently as local change magnitude:

- `E_S=|dP_S/dt|` from the Space/Connection end;
- `E_T=|dP_T/dt|` from the Time/Movement end.

Both were mapped independently to their own off-source 0–2 child tier. Only
after their independent histories and landmarks were written was
`sqrt(E_S E_T)` used as a descriptive joint history.

## What shape actually appeared

### Parent scale

- The pooled parent Di-ARA occupies `62.25%` of a descriptive `20×20` plane.
  It forms a broad inverse band rather than a line constrained by
  `P_S+P_T=2`.
- Every locked detector stream is inverse, but the standard deviation of the
  parent sum remains substantial: median `0.368`, range `0.261–0.497` ARA
  units. The two parents push and pull; they are not bookkeeping complements.
- In the event-aligned population median, Space/Connection becomes dominant
  before the published event, peaks relative to Time/Movement near `-49 ms`,
  and then hands the lead to Time/Movement just after the event. This is a
  post-hoc descriptive landmark, not yet a frozen event predictor.

### Direction of the parent cut

A post-hoc rotation separated the visible parent plane into an exchange
direction, `(Space-Time)/sqrt(2)`, and a perpendicular/common direction,
`(Space+Time-2)/sqrt(2)`. The pooled principal axis lay only `15.45 degrees`
from the exact inverse direction and carried `4.53x` the perpendicular
variance. All `20/20` locked detector streams varied more strongly along the
inverse band; their median along-band/perpendicular variance ratio was `3.85`.

Thus T440 does **not** observe a full two-dimensional ARA orbit. It primarily
observes an exchange axis or chord. That is compatible with an edge-on or
perpendicular *view of a larger traversal*, but the missing orthogonal phase
coordinate is not contained in this construction and cannot be inferred from
the inverse band alone.

The published event GPS is an external alignment anchor, not an ARA landmark.
At the nearest common-grid slice the population medians were Space `1.436` and
Time `0.787`, not a ridge crossing. The median individual exchange coordinate
crossed zero only around `+21.2` to `+25.1 ms` (the difference of separately
aggregated parent medians crosses slightly earlier, around `+17.3` to
`+21.2 ms`). Therefore the GPS line must not be described as the geometric
handover in this cut.

The rotated diagnostic is
`results/T440_ROTATED_PARENT_DIAGNOSTIC.png`, with numerical values in
`results/T440_ROTATED_PARENT_DIAGNOSTIC.json`.

### Child-side cut

- The independently derived child plane occupies `93.0%` of the same
  descriptive `20×20` grid and is strongly edge-rich. It looks far less like a
  single closed child identity than the parent plane.
- That near-full occupancy explains the unstable peak landmarks: absolute
  differentiation plus separate off-source ECDF mapping magnified local
  spectral texture and nearly saturated the child coordinate plane.
- Consequently, failure to lock one child time is evidence against this
  **magnitude-only child extraction**, not evidence that the parent relation or
  every possible child handover is absent.

### Relation retained across the whole record

- Same-record Space/Time pairing is much more coherent than wrong-event
  pairing (`0.9146`, permutation `p=0.00020`).
- Opposing signed motion occurs in every event window and `98.125%` of
  off-source windows. Thus opposition is a persistent property of the measured
  record-level relation; sign alone cannot identify the astrophysical event.

The geometry-first figure is `results/T440_GEOMETRY_FIRST.png`; its numerical
companion is `results/T440_GEOMETRY_SUMMARY.json`.

## Frozen benchmark results

| Gate | Locked events passing |
|---|---:|
| both H1/L1 overlap percentiles at least 90% | 0/10 |
| both H1/L1 best-lag association percentiles at least 90% | 0/10 |
| both detectors' independent side peaks within 32 ms | 1/10 |
| H1/L1 joint-child times within 16 ms | 0/10 |
| all four gates | 0/10 |

The median Space-end versus Time-end peak separation was `80.1 ms`. The median
H1 versus L1 joint-child separation was `138.7 ms`, far outside the registered
16 ms replication allowance. Median within-file percentiles were `0.317` for
history overlap and `0.354` for best-lag association.

## What the wrong-event result does and does not establish

Pairing the two feature families from the correct detector record preserves its
specific signal-plus-noise morphology; pairing different events destroys that
identity. The very low wrong-event p-value therefore establishes a
record-specific bridge. Matched off-source controls show that strong two-ended
overlap is also common elsewhere in the same records, so overlap alone does not
localize the bridge to the astrophysical event. It remains real as a persistent
record-level relation but cannot yet be promoted to a merger-specific child
handover.

## Directional result

All 20 evaluation detector streams placed the joint maximum in an opposing
derivative quadrant: `S+/T-` in 11 and `S-/T+` in 9. This is strong descriptive
evidence that the chosen parents behave as a push/pull Di-ARA. Matched
off-source controls were also opposing in `98.125%` of windows, locating that
push/pull relation at the persistent record/background level rather than
making it unique to the merger. The control narrows the identity of the shape;
it does not make the shape disappear.

## ARA reading

The test successfully maintained the requested relational separation: two
independent parents, two independent child-side cuts, no complement and no
forced ridge. The parent geometry is clearer than the derived child geometry.
In ARA terms, the instrument sees a broad inverse Space/Time parent relation
and an event-aligned exchange of dominance, while the magnitude-only child cut
unfurls into an almost fully occupied transition plane and cannot lock one
shared child identity at a common time across the two ends and two detectors.

This suggests one of three boundaries:

1. absolute local change is too generic and measures detector/background
   texture rather than the child;
2. the child is expressed by signed direction or phase at another cadence,
   not transition magnitude alone;
3. the 64 ms time-frequency lens is too coarse for a localized handover and
   creates jagged, nearly saturated child coordinates.

## Scientific boundary

The input is real calibrated GWOSC strain, but it is detector response plus
noise—not a direct recording of separate black holes, horizons, spacetime
density or internal children. A common gravitational-wave transient can create
shared feature timing without validating ARA's generative physical hypothesis.

## Best next test

Retain the two independent parents, but replace absolute derivative magnitude
with a **signed, multi-resolution phase-transfer test**:

1. freeze a 16/32/64 ms scale ladder;
2. search for a Space rise paired with Time fall, and the reverse, without
   pooling the two directions;
3. require the same signed transition to persist across adjacent scales and
   reproduce after detector propagation-delay alignment;
4. compare against identically phase-preserving off-source controls.

That directly tests whether the broad inverse relation contains a localized
phase handover hidden by the magnitude-only cut. It must be registered as a new
test; it cannot rescue T440.

## Validation

Independent validation passed all source hashes, public data-quality flags,
coordinate bounds, overlap reconstruction, gate reconstruction, wrong-event
p-value, and the absence of a forced sum-to-two constraint. See
`results/T440_VALIDATION.json`.
