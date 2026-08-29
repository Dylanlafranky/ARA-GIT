# T426 — Main Irrationality Di-ARA macro-handover loop

**Status:** frozen before T426 sequence scoring  
**Frozen:** 24 August 2026 (Australia/Brisbane)  
**ARA hypothesis and geometry:** Dylan La Franchi  
**Operationalisation and implementation:** Codex

## Relational address

- **Who:** each of the 16 held-out Toyoura-sand discharges already scored in
  T424.
- **What:** the ordered main/state Irrationality Di-ARA route

  \[
  \text{connection-heavy}
  \rightarrow
  \text{opening near }(0.5,1.5)
  \rightarrow
  \text{movement excursion}
  \rightarrow
  \text{connection-heavy reclosure}.
  \]

- **When:** from the start of each registered discharge through the frozen
  T424 terminal-closure boundary. The opening landmark is anchored to the
  first independently registered `direct_active = 1` frame; it is not found by
  searching the ARA coordinates.
- **Where:** the T424 `(C1 movement/traversal, C2 connection/packing)` plane.
  This is the larger dynamic/state Irrationality Di-ARA, not the local T425
  radial/angular quotient.
- **Why:** test whether the one-quadrant occupancy summary hides a repeatable,
  directed macro-handover loop.
- **How:** freeze ARA-derived regions and persistence, score their temporal
  order per run, and compare the observed alignment with matched pseudo-onset,
  joint circular-shift, and time-reversal controls.

## Fixed input

Read only:

- `T424_HOLDOUT_ARA_COORDINATES.csv`;
- T424's existing `closure_index`, `direct_active`, and run registration.

No video is re-extracted, no T424 coordinate is refitted, and no event is
relabelled.

## Frozen ARA regions

Let `C1 = x_trav` and `C2 = x_conn`.

### Connection-heavy state

\[
C1<1,\qquad C2>1.
\]

### Opening handover neighbourhood

The child-ridge landmark is `(0.5, 1.5)`. “Near” is frozen as the natural
quarter-coordinate box around that address:

\[
|C1-0.5|\le 0.25,
\qquad
|C2-1.5|\le 0.25.
\]

The primary opening coordinate is the first `direct_active = 1` frame in that
run. This direct activity is downstream-image motion and is not calculated
from `C1` or `C2`.

### Movement-heavy excursion

\[
C1>1,\qquad C2<1.
\]

### Persistent state

A state is persistent when its inequalities hold for three consecutive frames.
The short persistence requirement rejects one-frame ridge noise while retaining
the source's registered handover scale.

## Ordered-sequence score

A run is a **complete loop** only when all four conditions hold in order:

1. a persistent connection-heavy interval exists before direct onset;
2. the direct-onset coordinate lies inside the frozen `(0.5,1.5)` box;
3. a persistent movement-heavy interval begins after onset and before terminal
   closure;
4. a new persistent connection-heavy interval begins after that movement
   excursion and no later than terminal closure.

Both-high and both-low bridge samples are allowed between stages. They are not
relabelled as either primary state.

For every run report stage frames, stage times, normalized history fractions,
opening distance, excursion duration, and reclosure lead to terminal closure.

## Primary gates

Structural support requires both:

1. at least 12 of 16 held-out runs complete the frozen four-stage loop; and
2. the observed complete-loop rate exceeds 10,000 matched null replicates with
   empirical `p < 0.05`.

## Frozen controls

1. **Pseudo-onset control:** within each run, select a random eligible
   pre-closure frame as onset while retaining the observed `C1/C2` history and
   score the same four-stage rule.
2. **Joint circular-shift control:** retain the real direct-onset frame but
   circularly shift the paired `(C1,C2)` history by the same non-zero offset.
   This preserves the exact path and coupling while breaking its alignment to
   the physical onset and closure clock.
3. **Time-reversal control:** reverse the pre-closure paired history and map the
   physical onset to its mirrored index, then score the same forward rule.

Random controls use seed `42620260824`. Null inference uses the mean completed
run count per replicate, with the observed 16-run count as the comparison.

## Required visuals

1. median `C1/C2` histories with the four median stage positions;
2. median Di-ARA trajectory with arrows, stage markers, ridges, and the frozen
   opening box;
3. a 4 × 4 gallery of all 16 run trajectories with pass/failure and stage
   markers;
4. per-run stage-time waterfall;
5. observed completed-loop count against all three null distributions.

All axes must name their ARA coordinate, show the 0–2 scale where relevant,
and identify that the sample is the 16-run T424 holdout.

## Interpretation boundary

A pass supports this specific ordered macro-handover in the T424 hourglass
identity. It does not establish a compulsory quadrant sequence for every
Irrationality Di-ARA, prove causal motion, or establish the `(0.5,1.5)` address
independently of this source's optical measurements. A failure rejects this
strong ordered-loop version while leaving the broader T424 state geometry
intact.

