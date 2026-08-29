# T404 — corrected child-release and Di-ARA audit

Date frozen: 2026-08-18

## Why this audit exists

T403 placed the eight T402 detector bins into source time with a linear interpolation between the T400 child-window boundaries. That conversion was not faithful to T400. The registered T400 local coordinate is cumulative parent ARA,

\[
x_C(t)=2\,\frac{x_P(t)-x_P(L)}{x_P(R)-x_P(L)},
\]

and therefore is nonlinear in time. T404 preserves T403 as an historical artefact, corrects this inverse map, and retests the attractive `0.5 -> 1.0` interpretation without moving any observed curve.

This is a post-discovery audit, not a new blind confirmation. The coordinate defect and the aggregate T402 topology were already visible before this protocol was written.

## Who, what, when, where, why and how

- **Who:** the T398 fitted stopped-muon delayed-release population, the T400 nested child coordinate, the T402 C-minus-AC detector relation, the 326 saved T402 deterministic resampling probes, and the independent coarse T378 COHERENT timing archive.
- **What:** distinguish an exact child-to-parent octave (`release landmark x 2 = ridge`) from a more general three-stage relation (`detector/storage turn -> maximum child release -> detector ridge`). Reconstruct the candidate Di-ARA as remaining-parent storage versus delayed-child release flow.
- **When:** only inside the previously frozen T400 primary child window. No boundary is refit.
- **Where:** the unchanged local T400 ARA coordinate `x_C in [0,2]`. T378 remains on its own published time grid and is used only for broad chronology.
- **Why:** determine whether the earlier apparent `0.532 -> 1.032` relation is physical, approximate, or an inverse-coordinate artefact before attempting an individual spinning-muon claim.
- **How:** invert the saved T400 `time_us <-> local_child_ara` curve monotonically; resample T398 source components at the corrected times; compare registered T402 KDE landmarks; bootstrap the saved T402 split histograms with a fixed binned landmark estimator; use circular shifts as order controls; and retain measured, fitted, derived, and independent evidence classes separately.

## Frozen identities and landmarks

1. **Detector turning point** `x_D`: the positive crest of the T402 C-minus-AC topology.
2. **Child release maximum** `x_R`: the T400 primary delayed-release crest on the true local child coordinate.
3. **Parent/detector handover** `x_H`: the T402 zero crossing nearest the local ridge.

The registered exact-octave residuals are

\[
\epsilon_{D\to H}=x_H-2x_D,
\qquad
\epsilon_{R\to H}=x_H-2x_R.
\]

Exact doubling requires a residual compatible with zero. The detector and source landmarks are never substituted for one another.

## Corrected Di-ARA instrument

The candidate two-axis relation is:

- storage axis: fitted remaining-muon fraction inside the frozen child window;
- flow axis: fitted delayed-release rate inside the same window.

Each axis is separately mapped to `[0,2]` only to display its within-window geometry. This normalization forces neither their path nor their quadrant order, but the two axes are derived from the same fitted delayed template and are therefore not independent evidence. The Di-ARA can describe the candidate handover; it cannot by itself prove a new physical mechanism.

## Registered evaluations

1. Verify that the corrected inverse mapping reproduces T400's saved `local_crest_ara` and quantify the displacement from T403's linear map.
2. Report all four pre-existing T402 KDE bandwidths without selecting a preferred one.
3. Test whether `x_D < x_R < x_H` holds across all four bandwidths.
4. Report both exact-octave residual families and ratios across all four bandwidths.
5. Bootstrap the 326 saved T402 split histograms with a fixed quadratic-crest plus linear-zero-crossing estimator. These overlapping splits are robustness probes, not independent experiments.
6. Compare the registered order and octave error with all seven non-zero circular shifts of each detector difference curve.
7. Use T378 only for independent prompt-before-delayed chronology; do not claim a nested-coordinate replication from its coarse bins.
8. Audit T397/RAL Silver for scope only: it is an aggregate muSR phase measurement, not an event-linked observation of one spinning muon producing its daughters.

## Interpretation gates

- **Coordinate correction:** pass only if the corrected map reproduces the saved T400 crest to numerical precision.
- **Three-stage relation:** supported descriptively only if all four registered bandwidths satisfy `x_D < x_R < x_H` and at least 90% of valid bootstrap means retain that order.
- **Exact detector octave:** supported only if zero lies inside the bootstrap 95% interval of `x_H - 2x_D` and the unshifted octave error is not a common circular-shift result (`p <= 0.05`).
- **Exact source octave:** supported only if zero lies within the four-bandwidth range of `x_H - 2x_R`. This is a bandwidth robustness condition, not a sampling confidence interval.
- **Individual birth:** cannot pass from T397, T398, T400, T402, or T403 because none links a named muon spin trajectory to its charged daughter and both neutrinos event by event.

## Claim boundary

T404 may establish or reject an exact octave relation in the saved population geometry, and it may identify a candidate storage-flow Di-ARA sequence. It cannot establish the creation instant of either neutrino from one individual muon. Any such test requires event-linked spin or polarization, decay time, charged-daughter direction/energy, and neutral-sensitive or missing-momentum information.
