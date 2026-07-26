# H1 Frozen Protocol — Public Hydraulic Two-Cut ARA

**Frozen:** 24 July 2026, 09:10 AEST  
**Target unopened at freeze:** yes  
**Dataset:** UCI 447, DOI `10.24432/C5CW21`  
**Primary target:** hydraulic accumulator condition (`130`, `115`, `100`, `90 bar`)

## Primary question

Do two independently measured spatial pressure cuts from a connection-rich hydraulic cycle retain held-out
accumulator-condition information absent from the best single pressure cut?

## Source and allowed inputs

Allowed primary inputs:

- `PS1.txt` through `PS6.txt`;
- accumulator target column in `profile.txt`;
- cycle row order for grouping;
- the other four profile columns only for diagnostics and confound stratification.

Prohibited primary inputs:

- source-processed features or fitted models;
- pressure/flow/temperature channels other than `PS1`–`PS6`;
- target values from an outer test fold during sensor or hyperparameter selection;
- Fourier, wavelet, PCA, NMF, learned embeddings or post-target feature discovery.

## Cycle representation

Each `60 s`, `100 Hz` pressure trace contains `6,000` samples. Split it into twelve consecutive `500`-sample
windows. For every window calculate the mean and population standard deviation. Concatenate the twelve means and
twelve standard deviations in time order, giving 24 fixed features per sensor.

Rows containing non-finite values fail data-quality validation. The UCI source reports no missing values; no
imputation is permitted.

## Grouped outer test

Assign cycles to consecutive 15-cycle groups:

\[
g_i=\left\lfloor\frac{i}{15}\right\rfloor.
\]

Use deterministic five-fold `StratifiedGroupKFold` with `shuffle=True`, seed `260`. Each 15-cycle group remains
entirely in one fold. Every outer training and test split must contain all four accumulator classes. If fewer than
four valid outer folds remain, classify the benchmark as `BLOCKED`.

No chronological neighbour from a held-out 15-cycle group may appear in training.

## Nested sensor and pair selection

Inside each outer-training set, repeat the same grouped construction with deterministic four-fold
`StratifiedGroupKFold`, seed `1260 + outer_fold`.

Candidates:

- six single sensors;
- all fifteen unordered distinct sensor pairs.

For each candidate, fit shrinkage LDA (`solver="lsqr"`, `shrinkage="auto"`) on the fixed features and score
macro balanced accuracy. Select the candidate with the highest mean inner score. Break exact ties
lexicographically by sensor name.

The chosen single and pair are then refitted on the full outer-training set and scored once on the untouched outer
test set.

## ARA calibration

For every selected raw feature, using outer-training data only:

1. centre by the median;
2. scale by `IQR / 1.349`;
3. if that scale is `<1e-12`, use training standard deviation;
4. if both scales are `<1e-12`, drop the constant feature;
5. orient from `130 bar` toward `90 bar` using the sign of their training means;
6. map to `x = 1 + orientation * (f - median) / scale`;
7. do not clip.

Fit a new shrinkage LDA in ARA coordinates. Independently fit the same classifier on the corresponding centred and
scaled raw features without pole orientation. These same-information accounts must agree exactly up to floating
point tolerance.

## Primary estimand

Concatenate the five outer-fold predictions and calculate:

- two-cut macro balanced accuracy;
- selected one-cut macro balanced accuracy;
- paired gain `two-cut - one-cut`;
- per-fold paired gain;
- per-class recall;
- worst-class recall.

Construct a paired 95% bootstrap interval for gain using `2,000` resamples of the 15-cycle groups, stratified by
outer fold and sampled with replacement. Seed `2600`.

## Frozen gates

All eight gates must pass for the strong two-cut claim to be `SUPPORTED`:

1. **H1-G1:** two-cut macro balanced accuracy `>=0.75`;
2. **H1-G2:** paired gain over selected one cut `>=+0.03`;
3. **H1-G3:** paired 95% bootstrap lower bound for gain `>0`;
4. **H1-G4:** worst accumulator-class recall `>=0.60`;
5. **H1-G5:** two-cut accuracy exceeds one-cut accuracy in at least `4/5` outer folds;
6. **H1-G6:** raw-pair and ARA-pair accuracy difference `<=1e-12` with zero prediction disagreements;
7. **H1-G7:** global pole reversal `x→2-x`, refitted training-only, gives zero prediction disagreements;
8. **H1-G8:** across 100 deterministic training-label permutations per outer fold, mean test balanced accuracy
   `<=0.30` and the 95th percentile `<=0.35`.

Any clean gate failure prevents support. A blocked structural fold or data-quality failure produces `BLOCKED`,
not a failure or success.

## Diagnostics that cannot rescue the frozen result

- pair accuracy using each of the fifteen fixed pairs;
- best single and pair selection frequency;
- confusion matrices;
- class and nuisance-condition counts by fold;
- pair-destruction by independently circularly shifting the second sensor trace within each test cycle;
- pressure-only random forest on the selected pair;
- target results for valve, pump and cooler using the already frozen representation;
- accuracy as the number of five-second windows is reduced.

These are descriptive boundary probes. They may inform a later frozen test but cannot replace failed gates.

## Verdict language

- `SUPPORTED`: all eight gates pass.
- `NOT SUPPORTED`: at least one clean gate fails.
- `BLOCKED`: source structure prevents at least four valid untouched outer folds or required data are invalid.

A supported result would show complementary spatial pressure information in this public connection-rich system.
It would not prove universal ARA, establish new hydraulic physics or show superiority over all conventional
methods. The exact raw/ARA tie is a coordinate-fidelity result, not an information-gain result.

