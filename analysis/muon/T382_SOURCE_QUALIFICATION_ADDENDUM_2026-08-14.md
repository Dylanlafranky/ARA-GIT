# T382 source-qualification addendum

**Status:** FROZEN BEFORE RAW COUNT INSPECTION  
**Recorded:** 14 August 2026  
**Reason:** metadata/manual audit after the T382 architecture freeze and before outcome execution

The T382 protocol described the RAL Silver family as transverse-field runs. The NeXus metadata records instrument orientation `l`, while the experiment contains a broad field ladder and the EMU documentation distinguishes longitudinal-field geometry, low transverse fields and possible spin/detector configurations. The metadata inspected so far do not independently establish that the selected field value is perpendicular to the initial muon spin for every run.

The word `transverse` is therefore withdrawn as an established source fact before outcome inspection. The controlled field remains `External Other`. The spin-precession child is permitted to enter C03 only if the following calibration-only qualification passes:

1. the manually documented forward bank (detectors 1-48) and backward bank (49-96) form a stable efficiency-corrected asymmetry;
2. repeated 20 G and 25 G calibration runs contain a coherent non-zero phase progression;
3. its fitted cadence changes in the same direction as field and is stable across repeated runs;
4. the first and final low-field validation bookends reproduce the relation;
5. the relation is not matched by circular detector-label shifts or a time-constant asymmetry;
6. the result is explicitly labelled a daughter-visible reconstruction of the parent spin relation, not a continuous individual pre-decay observation.

If this qualification fails, execution stops at Gate A and no child-pole or parent-ridge interpretation is made. If it passes, the fixed forward/backward detector axis supplies the physical phase origin used by T382; it is not chosen from the holdout runs.

This addendum does not alter the frozen dataset split, landmarks, holdout fields or decision gates. It narrows the claim boundary before counts are opened.
