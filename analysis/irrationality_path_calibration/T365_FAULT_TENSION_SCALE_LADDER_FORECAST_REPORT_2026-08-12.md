# T365 — fault-tension scale-ladder forecast

**Date:** 12 August 2026  
**Verdict:** NOT SUPPORTED UNDER THE FROZEN GATES  
**Evidence class:** causal retrospective forecasting audit on an already-open archive

## Plain-language result

The dense laboratory record showed the exact direction proposed before the
five-rung pass: the smallest tension identity began the handover first, then
the child, then the current identity, and finally its larger parents. The frozen
alarm began **14.0 ms before** independently
measured displacement slip, with **0**
earlier holdout alarm bouts.

This is a short warning in a rapidly sampled laboratory fault, not a field-time
earthquake forecast. Its important content is the ordering: motion appears in
the tension children before it becomes the parent-scale release.

## Dense scale order

| identity | half-ridge lead | full-ridge lead |
|---|---:|---:|
| grandchild (r-2) | 16.0 ms | 2.0 ms |
| child (r-1) | 14.0 ms | 0.0 ms |
| current (r+0) | 8.0 ms | -2.0 ms |
| parent (r+1) | 4.0 ms | -10.0 ms |
| grandparent (r+2) | 2.0 ms | -24.0 ms |

## Replication

- Grandchild half-ridge no later than current full ridge: **5/15**.
- Frozen alarm horizon contained the stress drop: **3/15**.
- Full grandchild → child → current ordering: **2/15**.
- Median event-local warning: **50.0 source rows**.

| medium | event | grandchild_half_relative_row | child_half_relative_row | current_full_relative_row | forecast_start_relative_row | forecast_contains_drop |
| --- | --- | --- | --- | --- | --- | --- |
| dry | 1 |  |  |  |  | False |
| dry | 2 |  |  | 0.0 |  | False |
| dry | 3 |  |  | 1.0 |  | False |
| dry | 4 |  |  | 1.0 |  | False |
| dry | 5 |  |  | 1.0 |  | False |
| dry | 6 |  |  | 1.0 |  | False |
| dry | 7 |  |  | 1.0 |  | False |
| dry | 8 |  |  | 1.0 |  | False |
| dry | 9 |  |  | 0.0 |  | False |
| dry | 10 |  |  | 0.0 |  | False |
| fluid | 1 | -59.0 | -50.0 | -32.0 | -50.0 | True |
| fluid | 2 | -33.0 | -56.0 | -22.0 | -69.0 | True |
| fluid | 3 | -31.0 | -28.0 | -1.0 | -36.0 | True |
| fluid | 4 | -29.0 | -34.0 | 1.0 |  | False |
| fluid | 5 | -23.0 | -26.0 | 3.0 |  | False |

## Which Irrationality it used

At the warning sample, the local grandchild and child both occupied the active
`Ab` tension branch required by the alarm. The broader path/history address was
measured independently at each rung:

| role | rung | x_P | x_R | history_coherence_mean | irrationality_quadrant | local_parent_quadrant | local_child_h |
| --- | --- | --- | --- | --- | --- | --- | --- |
| grandchild | -2 | 1.6739 | 1.3506 | 0.9266 | Ab | Ab | 0.6579 |
| child | -1 | 1.6099 | 1.2339 | 0.9684 | Ab | Ab | 0.5386 |
| current | 0 | 1.7976 | 0.6110 | 0.9627 | aB | aB |  |
| parent | 1 | 1.7741 | 0.1749 | 0.9723 | aB | aB |  |
| grandparent | 2 | 1.6154 | 0.0910 | 0.9905 | aB | aB |  |

These quadrant labels identify the part of the Irrationality Di-ARA occupied by
each scale; they are addresses, not a requirement that one event fill all four
quadrants.

In ARA language, the warning is a **cross-rung seam**. The grandchild and child
have entered `Ab`: their path is still open and now carries substantial
unresolved/release participation. The current, parent and grandparent remain in
`aB`: their paths are open, but their histories are still strongly determined.
The release is therefore visible first as residual child motion while the
larger tension identities still look connection-held.

## Why the replication split

The fluid subset preserved the smaller-rung ordering in **5/5** events and the
exact alarm fired in **3/5**. The dry subset produced **0/10** alarms. Post-hoc
inspection shows why: in the dry records, the release coordinate usually stays
outside `Ab` until the stress-drop row itself and then enters the quadrant near
or beyond its child ridge. The fluid records contain a longer pre-drop `Ab`
approach, so the half-ridge is observable before the marker.

That can represent a material-path difference, an observation-resolution
difference, or both. It cannot be used to rescue the frozen claim: the medium
split was not a predeclared exception. It instead narrows the next question to
whether a smoothly resolved tension approach carries this child-first warning
across a second physical archive.

## Frozen gates

| gate | passed | observed |
| --- | --- | --- |
| G1 causality QA | True | alarm=22107; calibration_end=17819; slip=22114 |
| G2 primary dense forecast | True | lead=14.000000000123691 ms; bouts=1 |
| G3 dense false-alarm boundary | True | earlier false bouts=0 |
| G4 dense child ordering | True | grandchild=16.0 ms; child=14.0 ms; current-full=-2.0 ms |
| G5 marker specificity | True | real=0.0 bins; pseudo median=2060.5; shifted=[3335.0, 2221.0, 1107.0] |
| G6 repeated scale ordering | False | grandchild<=current 5/15; alarm horizon contains drop 3/15 |
| G7 Irrationality address | True | finite rung addresses=5/5 |

## Scientific boundary

The protocol was frozen before the extra rungs were scored, but after this
archive and its base tension geometry had already been opened in T363/T364.
Therefore the result supports a **causal forecast signature on this archive**.
It does not yet establish an independent earthquake predictor. The next scale
step is to carry the exact five-rung alarm to a second synchronized
stress-and-motion archive without re-tuning the widths or landmarks.
