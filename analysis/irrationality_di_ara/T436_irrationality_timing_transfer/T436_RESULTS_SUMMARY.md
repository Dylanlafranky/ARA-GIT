# T436 results — Irrationality Di-ARA timing transfer

**Frozen verdict: NOT SUPPORTED.**

## Answer first

The transferred Irrationality Di-ARA clock predicted the common handover at
`3586.252534 M`, compared with the first common horizon at
`3685.496268 M`. Its absolute error is `99.243734 M`
(`8.728` T435 parent-waveform cycles),
versus T435's `37.542193 M` error.

The timing error worsened by `61.701541 M` (`164.4%` larger than T435). The primary estimate is before
the common horizon by `99.243734 M`.

## Frozen gates

- **FAIL** — improves on T435.
- **FAIL** — within one parent waveform cycle.
- **FAIL** — joint lock specificity.

## What the clock measured

The primary estimate minimized the predeclared joint distance

```text
sqrt((U-R)^2 + (H-1)^2)
```

inside the waveform-only late parent basin (`T435 relation <= 1`, before the
total modal-power maximum). At the selected read:

- `U = 0.689554`;
- `R = 1.999630`;
- `H = 0.047979`;
- child distance `|U-R| = 1.310076`;
- parent-ridge distance `|H-1| = 0.952021`.

This is the T421 hierarchy transferred to the T435 half-phase child axis:
child singularity and parent ridge are measured together rather than treating a
single waveform extremum as the clock.

## Timing comparison

| Clock | Predicted time (M) | Signed error (M) | Absolute error (M) | Error (parent cycles) |
|---|---:|---:|---:|---:|
| T436 joint Irr-Di-ARA | 3586.253 | -99.244 | 99.244 | 8.728 |
| T435 frozen median | 3723.038 | 37.542 | 37.542 | 3.302 |
| Child-only |U-R| | 3586.253 | -99.244 | 99.244 | 8.728 |
| Parent-only |H-1| | 3692.648 | 7.152 | 7.152 | 0.629 |
| Wrong rung / full phase | 3692.648 | 7.152 | 7.152 | 0.629 |
| Quarter-shift control | 3681.849 | -3.647 | 3.647 | 0.321 |
| Reverse-time control | 3642.251 | -43.246 | 43.246 | 3.803 |
| Waveform power maximum | 3692.648 | 7.152 | 7.152 | 0.629 |

## Evidence boundary

This same simulation's common-horizon time was already revealed in T435 before
T436 was designed. The prediction script did not read the answer key and its
artifact was hashed before scoring, but the result remains **known-answer
calibration**, not independent blind evidence. A fixed rerun on an untouched SXS
simulation is required before treating the timing rule as predictive.

## Files

- `T436_FROZEN_PROTOCOL.md`
- `T436_waveform_irrationality_clock.py`
- `T436_score_known_handover.py`
- `results/T436_WAVEFORM_ONLY_IRRATIONALITY_CLOCK.npz`
- `results/T436_WAVEFORM_ONLY_IRRATIONALITY_CLOCK.json`
- `results/T436_SCORED_RESULT.json`
- `results/T436_IRRATIONALITY_HISTORY.csv`
- `results/T436_TIMING_COMPARISON.csv`
- `results/T436_IRRATIONALITY_TIMING_COMPARISON.png`
