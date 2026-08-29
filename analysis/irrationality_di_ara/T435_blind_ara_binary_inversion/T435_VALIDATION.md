# T435 validation record

**Validation outcome:** the frozen provenance, calculations, controls, and visual outputs reproduce. The correct primary status is `PARTIAL`.

## Provenance and leakage checks

- `T435_FROZEN_PROTOCOL.md` and `T435_FREEZE_LOCK.json` were written before either answer key was opened.
- The waveform-only prediction was written with `answer_keys_opened: false`.
- Prediction SHA-256 `e54f0c397bcb273fe77eab9887c97f453a66412d80d69843ffe7b7c94a8fd5b9` was sealed before reveal.
- The scoring script verifies that hash before loading metadata or horizons.
- Inference used only `Lev6:Strain_N4.h5` plus its format companion JSON.
- Hidden scoring used `Lev6:Horizons.h5` and `Lev6:metadata.json` only after the seal.

## Reproduced calculations

- Orientation coherence: `0.9942114513`.
- Unhalved-phase control: `0.0061876817`.
- Median axis error: `0.7919008650 degrees`.
- Relation Spearman: `0.9995591542`.
- Circular-shift relation control: `-0.3335856422`.
- Science `omega^(-2/3)` crosswalk: `0.9992897455`.
- Child-radius Spearman pair: `0.9993285367`, `0.9994232300`.
- Child-share mean absolute error: `0.0857843377`.
- Common-horizon time: `3685.4962678687 M`.
- Blind handover time: `3723.0384611894 M`.
- Timing error: `37.5421933208 M`; allowed parent cycle: `11.3710389023 M`.

## Methodological judgment

The half-phase orientation result is an exact crosswalk to the familiar quadrupolar relation between waveform and orbital phase. It is meaningful confirmation that the ARA octave/child rule selected the right operation, but it is not a new discovery of binary dynamics.

The relation score is a valid waveform-to-horizon bridge, but it is rank-based and both quantities are strongly monotone during inspiral. It demonstrates recovery of the ordering and closing trajectory, not absolute distance.

The radius gate is the weakest frozen gate. Both predicted child radii share the same dominant closing coordinate, so correlations near one are expected even if the child split is imperfect. The independent share error was therefore retained as a non-gated diagnostic and prevents overclaiming full identity recovery.

The handover failure is not altered. Although the total-power maximum alone was close to the common-horizon time, the frozen three-landmark median was late.

## Data-quality boundary

- One simulation is insufficient for generalization.
- Horizon coordinate centers have gauge dependence; SXS documentation itself cautions that center-of-mass motion can contain gauge artifacts.
- The result is robust to the frozen unhalved and circular-shift controls, but not yet tested across simulation identities.
- The source is simulated within GR; it is not independent detector evidence.

## Visual QA

`results/T435_BLIND_BINARY_INVERSION_AUDIT.png` was rendered and inspected. Titles, axes, units, the common-horizon marker, the blind handover marker, controls, and frozen gates are visible. The timing bar is explicitly red and shown as allowed-cycle/error rather than omitted at a negative value.

The bounded interactive report payload in `results/T435_ARTIFACT_PAYLOAD.json` passed the Data Analytics artifact validator with five reviewed datasets and seven provenance sources, then rendered successfully as a report. Every native card, chart, and table points to a materialized CSV snapshot through executable DuckDB source SQL.

## Confidence

- High confidence in the orientation and relation calculations.
- Moderate confidence that the result demonstrates a useful blind ARA inversion crosswalk.
- Low confidence that T435 alone separates complete individual black-hole identities; that claim requires cross-simulation child-share holdouts.
