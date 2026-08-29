# T450 pre-freeze source inventory and proposed first cut

## Outcome first

The public source can support a genuine multi-scale pose/behaviour web, but it cannot directly measure the fly's internal molecular, neural, cardiac or metabolic systems. The defensible visible backbone is body geometry at 99.96 frames/s, nested inside the already extracted one-second, ten-minute, hourly, daily and lifecycle histories.

This was a source-capability audit, not an ARA result. No pose feature, scale boundary, ridge, phase or event gate has yet been frozen as T450.

## What is directly recorded

- 14 body points as x/y camera-pixel positions: head, both eyes, thorax, abdomen, six legs, both wings and proboscis;
- nine-state ethogram: unstereotyped, idle, proboscis extension, fore/hind/wing grooming, altered locomotion, locomotion and on-edge;
- seconds elapsed, on-edge state, temperature and relative humidity;
- frame rate, camera, arena centre, quadrant, start time and light schedule.

The coordinates are camera pixels. Cross-fly physical distance therefore requires a within-fly body-length normalization; raw pixel distances cannot be treated as one common physical scale.

## Coverage and continuity

- T448 already extracted all 47 individuals, spanning 5,147 complete pre-collapse hours; the median retained history is 106 hours (range 32–187).
- The HDF5 cohort is 125.06 GiB. The associated videos are 3.61 TiB and are not required for the first pose cut.
- Eight HDF5 files were pose-audited: the first and last filename from each of four experimental dates, spanning 720 recorded hours.
- All eight use 99.96 frames/s, contain the same datasets and vocabularies, and have matching time-axis lengths.
- Across 32 lifecycle-spanning five-second blocks, head + thorax + abdomen were jointly present in 99.9875% of frames.
- In the stratified all-node blocks, at least 10 of 14 points were present in 99.95% of frames; the median was 12 points.
- All 14 points were jointly present in only 2.025%. This is not system failure: the proboscis is an intermittent event node and legs can be occluded.
- X/Y missingness masks agreed exactly in one validation file from each experimental date.

Stable backbone nodes in this sample were head, eyes, thorax, abdomen and wings (100% sampled availability). Limb coverage was useful but asymmetric (72.3%–99.5% by node), so raw left/right visibility must be controlled before any biological asymmetry claim. The proboscis was present in 2.075% and should be treated as an event channel, not a required skeleton component.

The HDF5 files do not expose a per-point confidence score. “Finite” therefore establishes availability, not anatomical accuracy; any micro-scale coordinate used by T450A needs a tracking-noise check, and a small raw-video audit if the result depends on movements near the noise floor.

## What can be derived without changing the measured medium

These are candidate observed relations, not yet ARA phases:

1. **Whole-body traversal:** thorax displacement and body-axis rotation, normalized by the fly's own head–abdomen or head–thorax length.
2. **Core posture:** head–thorax–abdomen length, bend and compactness after rigid movement is removed.
3. **Internal articulation:** leg and wing motion in the fly's body frame after subtracting thorax translation and body rotation.
4. **Left/right balance:** paired appendage relations, conditional on both nodes being visible and with visibility asymmetry retained as a control.
5. **Quiet micro-movement:** residual core and appendage motion during seconds classified as idle.
6. **Event channels:** proboscis appearance/extension and discrete behavioural transitions.

The source cannot tell us that any one of these is “time.” It can test whether several independently measured biological children share a slower relation that is not reducible to locomotor failure, behaviour classification or one organ-like branch.

## Proposed T450A — scale and node discovery (not frozen)

### Who

Use the eight audited adult male flies as a calibration cohort: six files from experiments 1–3 for development and two files from the later/hotter experiment 4 for a small regime-transfer check. This is a pilot for selecting observable nodes and rungs, not the final 31/16 confirmatory test.

### What

Measure whole-body traversal, core posture, body-frame articulation, left/right balance and idle micro-movement independently from the same pose frames. The future target is a layered event web in which a relation shared across several children may be compared with the existing T449 ten-minute children and T448 hourly/daily lifecycle parents.

### When

Read one continuous 60-second pose burst centred at 12.5%, 37.5%, 62.5% and 87.5% of each recording, without using death or collapse to place the bursts. Each burst remains attached to its containing ten-minute window, hour and 24-hour parent so the scale lineage is explicit.

### Where

The relational address is:

\[
\text{individual adult fly}
\rightarrow
\text{lifecycle-position parent}
\rightarrow
\text{60-s pose burst}
\rightarrow
\text{body-frame feature children}
\rightarrow
\text{empirically selected local rungs}
\rightarrow
\text{existing 10-min, 1-h and 24-h parents}.
\]

No wing, leg or proboscis node will be connected directly to death. It must first form or predict an adjacent-scale parent relation.

### Why

The immediate aim is to discover which biological children are actually observable and at which characteristic time scales, rather than imposing arbitrary seconds/minutes rungs. This supplies the pieces needed for the later meta-wave test: ask whether a common relation moves through many subsystem nodes while branch-specific failures remain distinct.

### How

1. Put every burst in a fly-centred frame: thorax at the origin, head–abdomen axis as orientation, and median body length as scale.
2. Keep traversal, rotation, shape and articulation as independent coordinates; do not collapse them into one score before their relations are inspected.
3. On development flies only, scan scale-dependent persistence, variance, time-reversal asymmetry and change-point stability from the native 10-ms floor through 60 s. Select rungs only where a feature exhibits a stable scale break or plateau; the native frame interval is measurement resolution, not automatically an ARA rung.
4. Freeze those feature definitions, scale boundaries, quality rules and 0–2 mappings before viewing the two experiment-4 pose histories.
5. Define a cross-node edge only when a lag/direction survives within-fly circular shifts and retains its direction in the regime-transfer files. Same-time correlation alone is not a lineage edge.
6. After the pilot, expand the frozen extractor to the full 31-development/16-holdout cohort, using only the pose windows needed by the selected rungs.

## Intended sequence after T450A

T450B would use the selected nodes and rungs to infer each fly's lifecycle periods from development-only changes in its observed histories, not from fixed lifespan percentages or the known death time. T450C would then build the dynamic web: within-rung child exchanges, adjacent-rung child-to-parent leads, overlap events, and the resulting common mode would be evaluated blind against experiment 4 and only afterward against collapse/death.

That later sequence addresses the requested “web between all the points.” T450A must come first because otherwise the web's nodes and time scales would be chosen after seeing the lifecycle answer.

## Proposed scale ladder

Only the upper rungs are already anchored by earlier tests:

- **measurement floor:** 1 / 99.96 s ≈ 10.004 ms (not yet a rung);
- **micro and bout rungs:** unresolved until T450A finds stable scale breaks in development pose data;
- **behaviour child:** ten-minute windows from T449;
- **behaviour parent:** one-hour composition from T448;
- **daily parent comparison:** 24-hour within-fly direction from T448B;
- **outer observed parent:** the multi-day adult recording/lifecycle.

This preserves the user's scale rule: a node's meaning depends on its rung and coupling. It also prevents a visually attractive micro-event from being mistaken for the lifecycle handover simply because both can be mapped to 0–2.

## Public-data boundary

This dataset can reveal behavioural and postural children of the observed adult lifecycle. It cannot directly separate internal physiology, ordinary ageing, starvation, temperature stress and terminal failure; those require a second dataset or an explicitly different measurement medium later.

## Files

- `INVENTORY_METHOD.md` — sampling and leakage boundary
- `inventory_public_pose_data.py` — reproducible remote inventory
- `results/T450_SOURCE_INVENTORY.json` — machine-readable summary
- `results/T450_file_inventory.csv` — audited-file schema and duration table
- `results/T450_node_continuity_summary.csv` — node availability
- `results/T450_continuity_by_lifecycle_quartile.csv` — sampled lifecycle coverage
- `results/T450_sampled_pose_continuity.csv` — block-level audit
