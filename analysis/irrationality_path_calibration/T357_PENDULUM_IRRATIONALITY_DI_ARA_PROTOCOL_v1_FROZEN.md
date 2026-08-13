# T357 frozen protocol v1 - physical pendulum Irrationality Di-ARA transfer

**Orientation:** `x_P: 0 -> 2` finite/reused to open/resolving; `x_R: 0 -> 2` relation-determined to stochastic residual.  
**Frozen:** 11 August 2026, before T357 implementation or scoring  
**Evidence class:** controlled public physical-system transfer  
**Claim packet:** `T357_PENDULUM_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md`

## WHO

Three experimental single-pendulum records and three experimental double-pendulum records from the public dynamicslab MultiArm-Pendulum archive. The declared records are:

- single: `pend_single.mat`, `SingleDataWithControl_1_Dt_0_0001.mat`, `SingleDataWithControl_2_Dt_0_0001.mat`;
- double: `pend_double.mat`, `DoubleDataWithControl_1_Dt_0_0001.mat`, `DoubleDataWithControl_2_Dt_0_0001.mat`.

The free, driven-1 and driven-2 labels define three replication strata. They are not used inside any coordinate.

## WHAT

Transfer the frozen T348 path/history distinction to a physical oscillator. Convert angle and angular velocity into each arm's observed cycle phase. Use arm 1 as the parent clock. In the single pendulum, measure arm 1 through its own clock. In the double pendulum, measure arm 2 through arm 1's clock.

The primary question is whether the double child is coherently non-closing: it continues to open relative addresses while its ordered path remains more informative than shuffled or deliberately mismatched history.

## WHEN

Detect successive upward rest crossings of arm 1. Each interval between crossings is one parent cycle. Within each complete cycle, use the observed arm-1 phase as the clock and interpolate the physical times at eight equally spaced parent-phase landmarks. Score non-overlapping four-cycle windows, giving 32 ordered samples per window. Summarise windows within each physical record before comparing run types; windows are not treated as independent experiments. Four cycles are frozen because the free single-pendulum record contains four complete phase-clock cycles before settling to encoder-level stillness.

## WHERE

The observable is the physical phase plane of each arm:

`q = wrapped angle relative to the record's circular-mean rest`,

`v = recorded angular velocity when supplied; otherwise the fixed centred finite difference of the recorded angle`,

`z = arg(q/s_q + i v/s_v)/(2*pi) mod 1`,

where `s_q` and `s_v` are the record-level 90th percentiles of absolute nonzero `q` and `v`. Use `z = -arg(...)` so an upward rest crossing advances the declared parent phase; this sign is fixed by the phase-plane orientation, not estimated from the outcome. No Fourier transform, Hilbert transform, regime label or fitted frequency enters the primary mapping.

## WHY

The synthetic T348 calibration separated exact closure, coherent non-closure, deterministic chaos and stochastic wandering. T357 asks whether that instrument transfers to an experimentally recorded physical system without changing its meaning. A pendulum is deliberately chosen because a single arm supplies a clean closure referee while coupling supplies a physically interpretable unknown.

## HOW

### Data preparation

1. Load the six declared `.mat` records and retain angular position and time. The double-pendulum files directly supply `dTheta` and `dt`. The single-pendulum files store MATLAB time-series structures with angle and time but no angular-velocity channel; for those three files only, compute angular velocity as `gradient(unwrap(Theta), Time)` before decimation.
2. Decimate each record to approximately 200 Hz before phase construction.
3. Determine rest and robust phase-plane scales from the complete record without using the single/double label in the formula.
4. Detect arm-1 upward rest crossings with a minimum separation of 0.25 seconds.
5. Within each complete arm-1 cycle, interpolate physical time at eight equally spaced arm-1 phase landmarks, then read the measured child phase at those times. The parent clock is therefore a declared Poincare-style phase grid, not an assumed uniform-time sinusoid.
6. Retain only complete, non-overlapping four-cycle windows.

### Frozen coordinates

For each 32-sample window:

- **Address openness `x_P`:** occupied circular bins at resolutions `B={4,8,16,32}`; twice the clipped slope of `log(N_B)` on `log(B)`.
- **Stochastic residual `x_R`:** train a past-only `k=3` nearest-neighbour circular successor predictor on the first 16 ordered samples; score the last 16 against the training circular-mean successor null; set `x_R = 2*min(1,L_local/L_null)`.
- **Closure history `C(H)`:** for lags `1..16`, retain resultant coherence `rho_h` and signed circular miss `d_h`. The declared one-parent-cycle lag is `h=8`.
- **Physical closure:** `rho_h >= 0.80` and `abs(d_h) <= 0.03` turns. This is a finite-resolution physical tolerance, not mathematical equality.
- **Traversal orientation:** the signed circular mean of one-step increments. It is descriptive and is used only for the reversal check.

Record-level readings are medians across that record's windows. Family comparisons use the three record-level readings, not the pooled window count.

### Frozen controls

1. **Time shuffle:** fixed-seed permutation of the same 32 values within each window. Support is unchanged; chronology is destroyed.
2. **Time reverse:** reverse each 32-value window. Support and unsigned closure should remain; orientation should reverse.
3. **Broken lineage:** for every double run, keep its arm-1 parent-cycle sampling schedule but replace arm 2 with the next declared double run's arm-2 phase after mapping both records to fractional record time. This preserves a plausible child path while breaking the physical parent-child relation.

Random seed: `3570811`.

## Frozen gates

All thresholds are evaluated on record-level medians. A comparison replicates when it has the declared direction in at least two of the three run strata.

1. **Single closure referee:** at least two single records have `x_P < 1`, `x_R < 1`, one-cycle coherence `rho_8 >= 0.80`, and one-cycle miss `|d_8| <= 0.03`.
2. **Relative address opening:** `x_P(double) - x_P(single) >= 0.20` in at least two run strata and the median paired difference is positive.
3. **Structured rather than shuffled:** at least two double records have `x_R < 1.25`; shuffling increases `x_R` by at least `0.25` and lowers best closure coherence by at least `0.15` in at least two double records. Because shuffling preserves values, `|Delta x_P| <= 0.02` must hold in every record.
4. **Coherent non-closure:** in at least two double records, one-cycle coherence is at least `0.80`, one-cycle miss exceeds `0.03` turns, and no physical closure occurs at lag 8. At least one coherent near-return (`rho >= 0.80`) must occur somewhere in lags 1-16.
5. **Lineage specificity:** broken lineage must increase `x_R` by at least `0.15` or lower best closure coherence by at least `0.15` in at least two double records.
6. **Reversal geometry:** in every record, reversal changes `x_P` by at most `0.02` and best closure coherence by at most `0.05`; orientation reverses sign in at least five of six records with absolute sum error no greater than `0.02` turns/sample.

The overall verdict is `SUPPORTED [controlled physical transfer]` only if Gates 1-6 all pass. Failed gates remain failed; descriptive geometry cannot rescue them. A partial result may support specific subclaims but must not be promoted to the overall verdict.

## Chart contract

One static research figure with:

1. the `x_P`-`x_R` ARA plane for chronological single, chronological double, shuffled double and broken-lineage double record-level readings, fixed 0-2 axes and ridge lines at 1;
2. one representative single and double relative-phase path through successive parent cycles;
3. lagged closure curves showing coherence and absolute miss for chronological and shuffled examples;
4. paired record-level differences with the frozen thresholds visible;
5. a compact frozen-gate panel.

Palette: blue for single, gold for double, open grey for controls, dark-neutral reference lines. No conclusion may rely on colour alone.

## Evidence boundary

Passing T357 would show that the T348 distinction transfers to these pendulum records under the frozen physical mapping. It would not prove a universal ARA law, prove a number-theoretically irrational frequency ratio, establish that all coupled pendulums are non-closing, or show that the selected estimators are unique.
