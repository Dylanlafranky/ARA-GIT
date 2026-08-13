# T360 frozen protocol v1 — magnetic-Plinko Irrationality Di-ARA calibration

**Frozen:** 12 August 2026, 09:27 AEST, after source inspection but before trajectory extraction or scoring  
**Evidence class:** small public-video physical calibration plus a published aggregate parent field  
**Orientation:** downstream is positive `v`; board-right is positive `u`; connection coordinate `x_C: 0 -> 2` runs from locally free/far to nearest-gate/connection-loaded; path coordinate `x_P: 0 -> 2` runs from locally unique/open to repeatedly occupied/parent-channel-loaded.  
**Scope correction:** this is a *magnetic* Plinko board. It tests continuous nearest-connection steering and row-to-row handover, not high-speed collision physics.

## WHO

Five sequential physical puck drops visible in the public Georgia Tech experiment video are the individually ordered child paths. The same experiment's published image of 400 physical trajectories supplies the aggregate parent path field. The board contains 28 attracting magnets arranged in five staggered rows.

The tracked object is a magnetic puck carrying a white spherical marker. The public video is a 480 x 360, 15 fps derivative of an experiment originally recorded at 200 fps. Only the public 15 fps stream is scored; no 200 fps microphysics is reconstructed.

## WHAT

Keep two relations separate.

1. **State/connection relation:** the puck's instantaneous proximity and directional response to the nearest declared magnet gate, mapped to `x_C in [0,2]`.
2. **Path/history relation:** how strongly the puck occupies a repeatedly used channel in the 400-run aggregate parent field, mapped to `x_P in [0,2]`.

The frozen physical claim is:

> Approaching the real connection lattice should produce a direction change toward a real magnet and should be followed by increased occupancy of a repeatedly used parent channel. The real chronological geometry should outperform geometrically wrong and lineage-destroying controls.

This is a calibration of the proposed Irrationality Di-ARA navigator/zip relation. It is not a claim that magnets or the known paths were discovered by ARA, and it is not evidence that every physical system uses the same observable cadence.

## WHEN

- Track the active white marker at every usable public-video frame.
- Split each run into child segments at crossings of the five magnet-row bands.
- Define an approach slice immediately before a row and an exit slice immediately after it, using the nearest available tracked points because the public derivative is only 15 fps.
- Treat release-to-exit as the run-level parent path.
- Retain raw frame number and pixel position. No sub-frame timing is inferred.

## WHERE

Use the board plane only. Affine-normalize the video and published aggregate image to a common lattice coordinate system using the magnet rows and outside columns:

- `u = 0` and `u = 1` at the outside magnet-column centres;
- `v = 0` at the first magnet row and `v = 1` at the fifth magnet row;
- increasing `v` follows the physical downstream direction.

The ARA axes are relational coordinates on this board plane, not additional spatial dimensions.

## WHY

This is a clean physical step beyond the pendulum calibration. Free traversal, increasing connection, directional deflection, and repeated downstream channels all occur in one visible system. The lattice also provides natural wrong-geometry controls without changing the observed puck path.

The test asks whether the two parts remain distinguishable:

- **where the identity is now** relative to a connection gate; and
- **how its history is being rationalized/locked** into a reused parent route.

## HOW

### Source preservation

Archive the public video derivative, published setup figure, and published 400-run trajectory figure. Record source URLs, dimensions, hashes, and limitations in `T360_SOURCE_README.md`.

### Marker extraction

1. Use a fixed board region of interest.
2. Detect compact high-value, low-chroma connected components consistent with the active white spherical marker.
3. Reject the narrow wand and accumulated coloured overlays by compactness, component size, and temporal continuity.
4. Link candidates with a past-only nearest predicted position; a run boundary is a downstream-to-release reset.
5. Smooth only for derivatives with a fixed short Savitzky-Golay or local polynomial window. Preserve unsmoothed coordinates in the output.

No coloured source overlay is used as scoring truth. It may be shown as a source annotation only.

### Magnet lattice and parent field

- Recover magnet centres from the published red-point layer and verify 28 centres in five staggered rows.
- Recover the blue 400-run trajectory ink as a binary/density parent field after masking magnets, labels, and axes.
- Affine-normalize both public surfaces through the magnet lattice.
- The parent field is aggregate-only; it does not supply individual timing or independent 400-run histories.

### State/connection coordinate

For tracked point `p_t`, let `d_t` be distance to the nearest real magnet and let `d_90` be the frozen 90th percentile of all usable nearest-magnet distances. Define

`x_C(t) = 2 * clip(1 - d_t / d_90, 0, 1)`.

This maps locally far/free traversal toward 0 and nearest-gate loading toward 2. It is a gradient, not a three-bin classifier.

### Directional connection response

Estimate velocity on the approach and exit sides of each magnet-row event. Let `delta_v` be the change in the unit direction vector and `m_hat` the unit vector from the approach point to the nearest real magnet. Score

`A_real = dot(delta_v, m_hat)`.

Positive values mean the directional change contains a component toward the declared connection. Recompute the same score with four frozen wrong layouts:

1. left-right mirrored magnets;
2. one half-column horizontal shift with wrap;
3. cyclic row shift by one row;
4. within-row permutation of magnet columns.

### Parent-channel/path coordinate

Let `D(p_t)` be the smoothed, normalized density of the published 400-run parent field at the matched board location, with the source path itself carrying at most five of 400 trajectories. Define

`x_P(t) = 2 * clip(D(p_t), 0, 1)`.

At each row event, calculate the change from median approach density to median exit density. Positive change is a move further into a repeatedly occupied parent channel.

### Coupled zipper score

For each row event, retain the ordered pair

`Z_e = (A_real, Delta x_P)`.

The event supports the proposed connection-to-information-lock handover only when both entries are positive. Report the complete two-dimensional distribution; do not collapse a failed component into a positive combined average.

### Chronology and lineage controls

- **Row-order reversal:** reverse the five event order within each run.
- **Cyclic row shift:** rotate event identities within each run.
- **Wrong lineage:** pair one run's connection states with a different run's next-row parent-channel changes.
- **Path mirror:** mirror each individual trajectory laterally against the unchanged parent field.
- **Horizontal path shifts:** shift each path by plus/minus one half-column against the unchanged parent field.

## FROZEN GATES

All gates remain separate. A failed gate cannot be rescued by a descriptive plot.

### G0 — extraction and lattice QA

Pass only if:

- at least four of five runs contain at least 12 linked active-marker frames;
- each accepted run spans at least 60% of the first-to-fifth-row downstream distance;
- exactly 28 magnet centres in five rows are recovered from the published source;
- every accepted trajectory overlay is visually inspected against the source contact sheet with no gross identity jump.

### G1 — real connection geometry

The pooled median `A_real` must be positive, at least 70% of row events must have `A_real > 0`, and the real layout must beat every frozen wrong layout in median alignment. An exact event-level randomization test over layout labels must give one-sided `p <= 0.05` for real versus the joint wrong-layout distribution.

### G2 — parent-channel inheritance

Each accepted real path's median parent density must exceed its own lateral mirror and both half-column shifts in at least four of five runs. The pooled real-minus-control difference must be positive with an exact within-run randomization `p <= 0.05`.

### G3 — connection-to-lock chronology

At least 65% of usable row events must have both `A_real > 0` and `Delta x_P > 0`. The real ordered pairing must exceed row reversal, cyclic row shift, and wrong-lineage pairing in the joint-positive rate; the one-sided exact/randomization `p` against the pooled chronology controls must be `<= 0.05`.

### G4 — two-coordinate non-redundancy

Across all usable tracked points, `x_C` and `x_P` must not be numerically interchangeable: absolute Spearman correlation must be below 0.90, while both coordinates retain non-zero interquartile range. This gate tests whether state and parent-channel history are genuinely distinct measurements in this record.

## VERDICTS

- `SUPPORTED [small physical magnetic-Plinko calibration]` only if G0-G4 all pass.
- `PARTIAL` is forbidden as a benchmark verdict. If any gate fails, report `NOT SUPPORTED` and preserve which geometry components survived descriptively.
- The geometry discussion may distinguish supported subrelations, but it must not overwrite the frozen benchmark verdict.

## CHART CONTRACT

1. **Source and extraction:** representative source frames with tracked marker overlays and declared run boundaries.
2. **Board geometry:** normalized magnet lattice, five extracted child paths, and the published aggregate parent density.
3. **ARA movement:** `x_C` and `x_P` over downstream position for every run, fixed 0-2 axes and ridge at 1.
4. **Connection handovers:** row-event arrows showing approach, magnet direction, and exit direction; colour/shape must distinguish supportive from opposing events.
5. **Controls and gates:** real versus mirrored/shifted/shuffled/wrong-lineage comparisons with exact event/run counts and pass/fail values.

Use blue for parent/history, gold for connection/state, green for jointly supportive handovers, muted red for opposing handovers, and grey for controls. No claim may depend on colour alone.

## EVIDENCE BOUNDARY

The five public paths are too few and too coarsely sampled for universal or microphysical claims. The 400-run parent field is an aggregate image and is not an independent time-series archive; because the five video paths come from the same experiment, parent-field inheritance is a within-experiment calibration, not external replication. Passing would show that this declared ARA instrument detects the expected nearest-connection-to-reused-channel handover in this record. Failing would count against this operationalization, not automatically against every possible ARA cut.
