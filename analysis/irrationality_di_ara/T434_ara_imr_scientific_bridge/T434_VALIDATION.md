# T434 validation record

**Validation outcome:** calculations and frozen provenance reproduced; the
primary result is `NOT SUPPORTED`.

## Reproduced checks

- Protocol SHA-256 matches `T434_FREEZE_LOCK.json`.
- Frozen implementation SHA-256 matches `T434_FREEZE_LOCK.json`.
- Four eligible events were scored.
- 10,000 temporal-shift controls were present.
- Median primary absolute percentage difference reproduced as 47.0539%.
- Events within 25% reproduced as 0/4.
- Temporal-shift error p-value reproduced as 0.070193.
- Median orientation-invariant AUC reproduced as 0.660454.
- AUC shift p-value reproduced as 0.295970.

## Evidence-quality boundary

The ARA coordinates and model-free frequency translation share the same public
detector strain, so this is not independent signal discovery. The independently
published component is the event-specific IMR cutoff. Event GPS is used to
locate each retrospective crop.

The post-result median-frequency diagnostic is explicitly exploratory. Its
strong temporal-shift result does not survive the stronger event-identity and
child-order controls, so it must not be reported as a confirmed bridge.

## Visual QA

`T434_ARA_IMR_COMPARISON.png`, `T434_EVENT_GALLERY.png` and
`T434_BRIDGE_AUDIT.png` were rendered and inspected. Axes and units are shown;
the audit visual distinguishes the frozen primary, the published IMR cutoff and
the post-result diagnostic.
