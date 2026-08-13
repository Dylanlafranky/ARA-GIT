# T348 independent artifact validation

**All checks passed:** YES

- Overall holdout sector accuracy: 95.6522%
- Macro family holdout sector accuracy: 90.0000%
- Irrational best-miss improvement share: 100.0000%

## Checks

- [x] metrics row count = 2016 paths x 8 rows
- [x] closure row count = 2016 paths x 2 controls
- [x] curve row count = 2 splits x 5 families x 2 controls x 512 lags
- [x] metrics natural key unique
- [x] closure natural key unique
- [x] all coordinates in [0,2]
- [x] all losses non-negative
- [x] all closure coherence in [0,1] within tolerance
- [x] protocol hash matches sidecar
- [x] claim hash matches sidecar
- [x] protocol hash matches result
- [x] claim hash matches result
- [x] independently recomputed gates match emitted gates
- [x] reported holdout accuracy independently matches
- [x] T348_IRRATIONALITY_PATH_FIGURE.png has nontrivial dimensions
- [x] T348_IRRATIONALITY_CIRCLE_EXAMPLES.png has nontrivial dimensions

## Family holdout sector accuracy

- periodic rational: 100.0000%
- irrational rotation: 100.0000%
- deterministic chaos: 50.0000%
- finite stochastic: 100.0000%
- continuous stochastic: 100.0000%

## Interpretation boundary

This validates the frozen synthetic instrument calibration artifacts. It does not establish a universal physical law.
