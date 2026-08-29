# T436 validation

## Overall assessment

**Ready to share as a negative known-answer calibration result.** The frozen
direct transfer did not improve timing and must not be presented as support for
the tested clock.

## Methodology review

- The test answers the requested timing question, not the earlier identity-
  recovery question.
- The ARA identity is stated explicitly: T435 half-phase child axis; independent
  time-facing `U`, `R`, and parent `H` coordinates.
- The prediction stage reads only the T435 waveform-only artifact. Horizon C is
  opened only by the scorer.
- The search basin is defined by the T435 waveform-only relation and power
  maximum. It is not restricted to the already-known one-cycle tolerance.
- The test transfers T419/T421 equations and does not define any coordinate as
  the complement of another.

## Calculation spot-checks

- Prediction SHA-256 recomputed as
  `5783eca884375e15ce89f46b52101bfdcb22da2caae07683f2e65df9bad662ce`;
  it matches `T436_PREDICTION_SHA256.txt`.
- Common horizon: `3685.496267868691 M`.
- T436 clock: `3586.252533887843 M`.
- Signed error: `-99.243733980848 M`; absolute error is the same magnitude.
- T435 frozen error: `37.542193320750 M`.
- T436 therefore worsens the error by `61.701540660098 M`.
- T436 error / T435 parent cycle:
  `99.243733980848 / 11.371038902294 = 8.727763121172`.
- Eligible parent-basin reads: `1,389`.
- Eligible coordinate ranges:
  - `U`: `0.426171` to `0.689554`;
  - `R`: `1.999513` to `2.000000`;
  - `H`: `0.026730` to `0.157254`.
- Minimum eligible `|U-R|`: `1.310076`; consequently there are zero `U=R`
  sign-changing crossings in the basin.

## Controls

- Child-only timing equals the failed joint clock (`99.244 M` error).
- Parent-only timing lands at the waveform-power maximum (`7.152 M` error), so
  it does not demonstrate an independent child/parent lock.
- The unhalved-phase control also lands at that maximum (`7.152 M`).
- The arbitrary quarter-shift control is closer (`3.647 M`) than the primary
  clock, directly failing specificity.
- Reverse chronology has `43.246 M` error.

## Visualization review

The audit figure was rendered and inspected at full resolution. It includes:

- numeric 0–2 coordinate axes and simulation-time units;
- exact T435, T436, common-horizon, and waveform-power landmarks;
- a full-scale Di-ARA plane plus an explicitly labelled closure-pole zoom;
- separate child, parent, and joint distances;
- exact error bars for the primary clock and all controls.

The visual makes the negative geometry clear: the tested phase history remains
pressed against the closure pole rather than traversing a child singularity.

## Required caveats

1. The common-horizon answer was already known historically before T436, so the
   exercise is a locked method-transfer calibration, not blind confirmation.
2. SXS:BBH:0305 is one numerical-relativity simulation.
3. The failure applies to the direct T419/T421 instrument on the T435 half-phase
   carrier. It does not falsify Irrationality Di-ARA generally.
4. The near timing of `H` alone is not an independent success because it occurs
   at the already-observed waveform-power maximum and is reproduced by the
   wrong-rung control.

## Methodological implication

The most likely identity mismatch is now explicit: T419 measured residual phase
after a carrier/frequency reconstruction, whereas T436 applied the instrument
to the deterministic T435 carrier axis itself. A future test should freeze a
parent-carrier removal and apply `U/R/H` to the residual modal or edge phase,
then score it on an untouched SXS simulation. That is a new test, not a post-hoc
rescue of T436.

