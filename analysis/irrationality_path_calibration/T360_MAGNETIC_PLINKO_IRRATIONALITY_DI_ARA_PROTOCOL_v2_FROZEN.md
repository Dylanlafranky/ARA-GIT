# T360 frozen protocol v2 — magnetic-Plinko Irrationality Di-ARA calibration

**Frozen:** 12 August 2026, after v1 source-extraction QA but before path extraction, metric calculation, control scoring, or result inspection  
**Status:** v2 supersedes v1 for scoring; v1 remains preserved as the audit trail  
**Reason for amendment:** in the 15 fps public derivative the active white marker intermittently merges with the growing coloured LabView tracking trace. The five complete source-generated traces are spatially richer than the downsampled marker positions. V2 therefore scores published tracker geometry and uses the visible moving marker only for direction and independent alignment QA.  
**Evidence class and physical scope:** unchanged — small within-experiment magnetic-Plinko calibration, not collision microphysics or external replication.

All WHO, WHAT, WHERE, WHY, source-preservation, ARA-orientation, control, verdict, chart, and evidence-boundary declarations in v1 remain active except where explicitly replaced below.

## REPLACEMENT WHEN

- One complete LabView trace is recovered for each of the five sequential drops.
- Forward direction is declared from the visibly moving white marker: release at the top, exit at the bottom.
- Parameterize each spatial trace by normalized downstream position `v`, not by assumed uniform time.
- Split each run at the five magnet-row crossings.
- No velocity, acceleration, dwell-time, or sub-frame timing claim is made.

## REPLACEMENT MARKER/TRACE EXTRACTION

1. Recover each run from its final source frame and unique trace colour: white, red, cyan, green, and yellow in chronological run order.
2. Use fixed HSV/brightness ranges declared in code before metric calculation.
3. For every image row, take the median trace-column location and linearly interpolate gaps no longer than one magnet-row spacing.
4. Smooth only the recovered spatial curve with a fixed short Savitzky-Golay window before tangent calculation. Preserve raw mask pixels and unsmoothed row medians.
5. Extract compact white-marker centres independently from frames where the marker separates from the trail. These centres are QA anchors only and never replace a failed trace geometry.

## REPLACEMENT DIRECTIONAL CONNECTION RESPONSE

At each magnet-row crossing, estimate the incoming and outgoing **spatial unit tangents** from equal downstream windows around the row. Let `delta_tau` be outgoing minus incoming tangent and `m_hat` the unit spatial direction from the approach-side trace point to the nearest declared magnet. Score

`A_real = dot(delta_tau, m_hat)`.

Positive values mean the path bends toward the declared connection. This is spatial steering geometry, not force, acceleration, or energy.

The same four wrong magnet layouts from v1 remain frozen.

## REPLACEMENT CHRONOLOGY LANGUAGE

In v2, chronology means preserved **downstream spatial order** from release to exit. Row reversal, cyclic row shift, and wrong-lineage controls destroy that order or pairing. They do not test clock-time cadence.

## REPLACEMENT G0 — trace, direction, and lattice QA

Pass only if:

- all five unique source traces span at least 80% of the first-to-fifth-row downstream distance;
- each trace supplies usable incoming and outgoing tangent windows for at least four row events;
- at least six independently detected active-marker centres align to each corresponding source trace with median absolute lateral discrepancy no greater than 8 public-video pixels;
- exactly 28 magnet centres in five rows are recovered from the published aggregate source;
- the recovered traces, magnet registration, and marker anchors are visually inspected with no gross path swap.

## REPLACEMENT G1 — real connection geometry

The pooled median spatial `A_real` must be positive, at least 70% of usable row events must have `A_real > 0`, and the real layout must beat every frozen wrong layout in median alignment. An exact event-level randomization test over layout labels must give one-sided `p <= 0.05` for real versus the joint wrong-layout distribution.

## G2-G4

G2-G4 remain unchanged except that every mention of chronological order refers to downstream spatial order and every direction-change metric uses spatial tangents rather than frame-time velocity.

## V2 EVIDENCE BOUNDARY

The published coloured curves are outputs of the experiment's tracking pipeline, not raw camera coordinates. V2 can test spatial nearest-connection steering and repeated-channel inheritance, but it cannot independently validate the LabView tracker, recover timing, or estimate physical forces. Passing would remain an instrument calibration on this experiment; failing would remain evidence against this operationalization.
