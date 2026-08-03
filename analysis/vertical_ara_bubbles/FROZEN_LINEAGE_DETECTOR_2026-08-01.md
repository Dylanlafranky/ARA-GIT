# Frozen lineage detector — Vertical ARA bubble handover

**Frozen:** 2026-08-01, after inspecting only calibration runs V01–V07 and before computing any Phi distance or registered outcome.

## Purpose

Identify conservative, direct two-child-to-one-parent bubble lineages from adjacent 50 fps contour frames. This detector establishes biological-style ancestry: unrelated bubbles are never paired merely because their sizes form a convenient ratio.

## Primary detector

A transition at frame `f -> f+1` is admitted only when:

1. two different child IDs are present at `f`;
2. both child tracks are present for at least two consecutive frames ending at `f`;
3. both child tracks do not remain separately visible at `f+1`;
4. child equivalent-disc separation at `f` is between `0.65` and `2.25` summed child radii;
5. child separation has not increased by more than 10% from `f-1` to `f`;
6. a single proposed parent exists at `f+1` for at least five consecutive frames;
7. parent area is between `0.65` and `1.35` of summed child area;
8. parent area is at least 90% of the larger child area;
9. the parent centroid is within `1.15` parent-equivalent radii of the area-weighted child centroid;
10. no unassigned third contour lies within `1.15` parent radii of the child-weighted centroid;
11. the family is the mutual best local child-pair/parent explanation;
12. its next-best competing explanation has a score at least 10% worse.

The matching score uses only area closure, centroid continuity and contact geometry. It contains no Phi term and no post-merger outcome.

Calibration yielded 26 primary candidates across V01–V07. V01 contained almost no detected contours and V02 yielded none under the family criteria. These are retained as data facts, not silently replaced.

## Sensitivity detectors

- **Strict:** child age >=3; parent life >=6; area closure `0.70–1.30`; separation <=2.00; parent-centroid distance <=1.00; isolation 1.25; ambiguity 10%. Calibration: 6 candidates.
- **Broad:** child age >=2; parent life >=4; area closure `0.60–1.40`; separation <=2.50; parent-centroid distance <=1.25; isolation 1.00; ambiguity 5%. Calibration: 57 candidates.

The primary result must not depend on the broad detector alone. Detector disagreement is reported rather than optimized away.

## Frozen conceptual distinction

- **Vertical ARA:** the same phase lineage repeated across scale, such as child bubbles closing into a parent bubble.
- **Temporal expression:** the same lineage carried through successive time slices.
- **Phi handover hypothesis:** Phi is a proposed shared relation of this lineage-preserving transition; it is not assumed to belong exclusively to time.

