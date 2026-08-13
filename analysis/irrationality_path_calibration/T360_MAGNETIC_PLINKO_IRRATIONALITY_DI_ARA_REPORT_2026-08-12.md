# T360 magnetic-Plinko Irrationality Di-ARA report

**Date:** 12 August 2026  
**Frozen benchmark verdict:** **NOT SUPPORTED**  
**Independent artifact validation:** **PASS**  
**Evidence class:** five public physical paths plus a published 400-run aggregate parent field from the same magnetic-Plinko experiment

## Plain-language result

The puck usually bent toward a real nearby magnet. That basic connection-steering part is visible and quantitatively strong.

The larger proposed zipper did not survive the frozen test. After a magnet-directed turn, the puck did not reliably move into a denser repeatedly used parent channel. The five paths also did not occupy the exact 400-run parent field more specifically than their mirrored or slightly shifted versions.

So this record supports a limited statement—**nearby connection gates steer movement**—but not the stronger statement that this particular parent-density coordinate captured irrational-to-rational information locking.

## Source and frozen scope

The Georgia Tech experiment used a magnetic puck with a white tracking marker moving down a tilted board containing 28 attracting magnets in five staggered rows. The published project reports 400 physical runs. The individually visible public derivative contains five sequential drops at 480 x 360 and 15 fps.

T360 therefore tested continuous nearest-connection steering. It did not test ordinary ball/peg impacts, clock-time microphysics, forces, or energy.

Active protocol chain: v1 + v2 + v4 + v5. V3 is retained as a superseded source-bookkeeping correction.

## Extraction QA — passed

- Five source-generated active red traces were recovered from the final frame before each run reset.
- All five paths spanned 1.45–1.63 normalized first-to-fifth-row distances, above the frozen 0.8 minimum.
- Every run supplied five usable row events, for 25 events total.
- The published aggregate image recovered exactly 28 magnets in the declared 6/5/6/5/6 rows.
- Each run supplied 19–33 independently located active-marker anchors.
- Median marker-to-trace lateral discrepancy was 0.50–1.50 public-video pixels; the largest observed discrepancy was 7.76 pixels.
- The extraction and lattice overlays were visually inspected.

## Frozen gates

### G0 — extraction and lattice QA: PASS

The physical source was adequate for the declared spatial test.

### G1 — real connection geometry: FAIL under the frozen all-controls rule

- Median real-layout turn alignment: `+0.07843`.
- Events turning toward a real nearest magnet: `84%` (`21/25`).
- Exact paired real-versus-mean-wrong-layout result: `p = 0.000456`.
- Half-column shift median: `-0.07796`.
- Cyclic-row shift median: `-0.05594`.
- Stagger-inversion median: `-0.07796`.
- Mirror median: `+0.07843`, exactly equal to the real median.

The physical steering subrelation is strong, but the frozen gate required the real layout to beat *every* control. A left-right mirror is not a wrong magnet set on this symmetric lattice: it recreates the same 6/5/6/5/6 point geometry. That degeneracy was discovered only after scoring, so it remains a legitimate frozen-gate failure rather than being edited away.

### G2 — parent-channel inheritance: FAIL

- Real path mean median density: `0.6125`.
- Mirrored path: `0.7394`.
- Negative half-column shift: `0.5779`.
- Positive half-column shift: `0.4877`.
- Real path beat all three controls in only `1/5` runs.
- Exact within-run label randomization: effect `+0.01083`, `p = 0.45996`.

The five paths did not uniquely occupy their exact aggregate parent channels. The parent field is broad and approximately mirrored, so a nearby or reflected route often remains in a heavily used channel.

### G3 — connection-to-lock downstream order: FAIL

- Events with both magnet-directed turning and increased exit-side parent density: `28%` (`7/25`).
- Row reversal, cyclic row shift, and wrong lineage: `20%` each.
- Real-minus-control effect: `+0.08`.
- Exact within-run label randomization: `p = 0.125`.

The real order led the controls descriptively, but the effect was small, below the frozen 65% event-rate gate, and not significant under the frozen exact comparison.

### G4 — two-coordinate non-redundancy: PASS

- Spearman correlation between connection state and parent-channel state: `rho = -0.1325`.
- `IQR(x_C) = 0.6909`.
- `IQR(x_P) = 0.8000`.

Nearest-connection loading and aggregate-channel occupancy are not two names for the same numerical coordinate in this record.

## ARA interpretation

The visible geometry separates two relations cleanly:

1. **Connection loading** rises and falls locally around the magnet rows.
2. **Parent-channel occupancy** is broader and follows the aggregate fan of repeatedly used paths.

The first relation behaves as expected: the path usually bends toward a connection gate. The second relation does not behave as the proposed immediate zipper output. A turn toward a magnet can redirect a path *between* established channels, reduce local aggregate density, or enter a mirrored/nearby channel that is just as common. Parent density is therefore not a faithful stand-in for newly rationalized information at this resolution.

This is not a failure of all Irrationality Di-ARA geometry. It is a failure of the stronger operationalization:

`nearest connection -> immediate increase in aggregate parent-channel density`.

## What this calibration taught us

- The magnetic lattice is a good physical source for testing **connection-directed curvature**.
- A symmetric board cannot use left-right reflection as a wrong-geometry control.
- An aggregate occupancy image is too coarse to identify a unique run-level lock or handover.
- The state and history coordinates remain separable, but separability alone does not establish the proposed coupling between them.
- A stronger revisit would require the original 200 fps individual trajectories, a deliberately asymmetric lattice, and a connection response measured independently of aggregate occupancy.

Per the user instruction for this calibration sequence, no further Plinko tuning is used to rescue the failed frozen benchmark.

## Artifacts

- `T360_MAGNETIC_PLINKO_IRRATIONALITY_DI_ARA_FIGURE.png`
- `T360_MAGNETIC_PLINKO_EXTRACTION_QA.png`
- `T360_MAGNETIC_PLINKO_IRRATIONALITY_DI_ARA_POINTS.csv`
- `T360_MAGNETIC_PLINKO_IRRATIONALITY_DI_ARA_EVENTS.csv`
- `T360_MAGNETIC_PLINKO_IRRATIONALITY_DI_ARA_CONTROLS.csv`
- `T360_MAGNETIC_PLINKO_IRRATIONALITY_DI_ARA_FROZEN_GATES.csv`
- `T360_MAGNETIC_PLINKO_IRRATIONALITY_DI_ARA_RESULTS.json`
- `T360_MAGNETIC_PLINKO_IRRATIONALITY_DI_ARA_VALIDATION.json`

## Evidence boundary

The five public paths are a small within-experiment calibration. The 400-run parent surface is an aggregate image, not 400 recoverable time histories, and the five displayed paths may contribute to it. The public video is a 15 fps derivative of a 200 fps experiment. The conclusions above concern spatial path geometry only.
