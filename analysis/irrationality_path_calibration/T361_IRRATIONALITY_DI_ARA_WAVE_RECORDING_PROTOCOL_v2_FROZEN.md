# T361 frozen protocol amendment v2 — numerical recording details

**Frozen:** 12 August 2026, before T361 outcome scoring  
**Active protocol chain:** v1 plus this amendment

This amendment removes numerical ambiguity without changing the v1 question.

1. Cycle samples use `linspace(event_i,event_(i+1),64)`, including both observed boundaries.
2. A per-step change with magnitude below `0.01` ARA units is direction-flat and inherits the preceding non-flat direction. The first unresolved direction is inherited from the first later non-flat step.
3. The relation lookup distance uses `(x_A/2,x_B/2,delta x_A/s_A)`, where `s_A` is the prefix 90th percentile of nonzero `|delta x_A|`, bounded below by `1e-6`. Nine nearest prefix transitions are retrieved by ordinary Euclidean distance.
4. Child `delta x_B` is the median of the retrieved transitions. The same rule is used for the direction-blind and wrong-lineage recorders.
5. Pearson waveform correlation is zero if either compared waveform has standard deviation below `1e-9`.
6. Turning points are indices where the inherited non-flat direction changes. `turn_error` is the median nearest-index separation divided by 63. If both paths contain no turns it is zero; if only one contains turns it is one.
7. Circular angular error is `abs(angle(exp(2*pi*i*(z_pred-z_actual))))/(2*pi)` averaged over the scored readings.
8. Record summaries are medians across all pair-cycle rows in that physical record. Gate counts use the nine physical records, not pair-cycles as independent experiments.
9. The population child parent is the median actual or recovered child coordinate at each of the 64 within-cycle time fractions across all available held-out pair-cycles in that record. This is a cycle-aligned coarse-grained parent, not a claim that all child cycles share identical laboratory timestamps.
10. Irrationality readings use the concatenated actual held-out angular path for each pair. `x_P` uses circular bin counts at 8, 16, 32 and 64 bins. `x_R` uses the prefix angular successors as the chronological relation table and the held-out angular successors as the scored continuation with `k=3`, matching the existing circular-loss definition. `C(H)` retains lags 1–128; lag 63 is the one-cycle boundary-to-boundary return because both cycle endpoints are included.

