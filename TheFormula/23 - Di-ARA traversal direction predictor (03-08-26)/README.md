# Thread 23 — Di-ARA traversal direction predictor

> **Architecture correction (3 August 2026):** this thread inherited T336's
> unestablished `T+iR` geometry and is invalid as a framework-level ARA test.
> Its scores remain only an implementation diagnostic. See
> `../T336_T337_ENSO_ARCHITECTURE_INVALIDATION_2026-08-03.md`.

This post-T336 test asks whether continuous signed traversal predicts the
direction of future ENSO movement even though full Di-ARA failed to improve
exact point value.

The frozen six-month verdict is **NOT SUPPORTED IN THIS FORM**. Traversal
balanced accuracy was `0.7353`, versus `0.7438` for ordinary raw movement.
The bootstrap interval did not support improvement. A three-month `+0.0192`
lead is exploratory and below the frozen material threshold.

The result separates a coordinate from a propagation law. The next coherent
test is geometry-to-future-geometry before decoding an observable.

Start with:

- `T337_DI_ARA_ENSO_DIRECTION_REPORT_2026-08-03.md`
- `T337_DI_ARA_ENSO_DIRECTION_PROTOCOL_v1_FROZEN.md`
- `T337_DI_ARA_ENSO_DIRECTION_VALIDATION.json`
