# T453 frozen protocol — prospective lifespan and four-coordinate geometry

Frozen before inspecting any T453 result.

## Question

Does the ARA construction recover information about a yeast cell's unseen future from its observed prefix, or does it only redraw a lifespan after both endpoints are known? Does a predeclared four-coordinate construction add information beyond an equally flexible ordinary model of the same measurements?

## Who / what / where / when / why / how

- **Who:** 225 individually tracked budding-yeast cells from the published S1 workbook used in T452.
- **What:** generation timestamps, cell size, and—where available—Rpl13A concentration. The physical observables retain their scientific names and raw units. ARA labels are applied only to derived coordinates.
- **Where:** development uses Experiments 7–8; Experiment 9 is an untouched same-platform holdout; Experiments 1–6 are a harder external-platform transfer without Rpl13A.
- **When:** each prediction is made after at least five observed G1 measurements and before the terminal G1 measurement. Only that prefix is visible to the predictor.
- **Why:** T452 used each cell's completed lifespan to create its 0–2 axes. That is valid for descriptive geometry but cannot establish prospective information.
- **How:** freeze prefix-only coordinates, fit models on Experiments 7–8, and evaluate without adjustment on Experiment 9 and then Experiments 1–6.

## No-lookahead boundary

No predictor may use the cell's total generation count, final elapsed time, future intervals, future size/Rpl13A measurements, an individually completed 0–2 normalization, or any outcome-derived threshold. The unseen future is used only to calculate the answer after features are frozen.

## Outcomes

1. **Remaining observed divisions:** final observed G1 count minus the prefix G1 count.
2. **Remaining observed hours:** final observed G1 time minus current elapsed time.
3. **Near-term sustained slowdown:** whether the first pair of consecutive future division intervals exceeding 1.25 times the median of the first three intervals begins within the next two divisions. The 1.25 threshold, two-interval persistence, and two-division forecast horizon are fixed here. This is an operational slowdown proxy, not the paper's SEP annotation and not death itself.

## Training-only scales

The median completed interval count and median completed observed hours of Experiments 7–8 define population scales. Applying a development-population scale to a new cell is allowed; using that new cell's own future endpoint is forbidden.

## Frozen model families

- **Age baseline:** observed division count and elapsed hours only.
- **Raw linear control:** the observed primitive states without ARA geometry.
- **Raw polynomial control:** the same primitive states plus all squares and pairwise products. This is the matched opponent for nonlinear geometry.
- **Two-coordinate ARA:** development-population generation and clock coordinates, their ridge-centred relation, and prefix-only local interval state.
- **Four-coordinate candidate:** generation, clock, size and Rpl13A concentration are independently mapped to 0–2 coordinates. The centred coordinates are combined as three declared disk cuts—generation/clock, clock/size, and size/Rpl13A—plus their four-coordinate radius and signed closure residual.

The four-coordinate construction is an operational projection test. It is **not** a claim that the observations prove an S3 topology or a physical fourth dimension.

Experiments 1–6 cannot validate the four-coordinate candidate because Rpl13A was not recorded there. They test only the two-coordinate core and a three-observable control.

## Estimation

- Weighted ridge regression, fixed alpha = 1.0, after development-only standardisation.
- Weighted logistic regression, fixed L2 = 1.0, for the slowdown outcome.
- Each cell receives equal total weight regardless of how many prefixes it contributes.
- Remaining-life predictions are clipped at zero.
- Primary regression score: mean of per-cell MAE; RMSE and bias are secondary.
- Primary event score: AUROC; Brier score is secondary.
- Cluster bootstrap resamples whole cells 2,000 times for improvement intervals.

## Frozen gates (secondary to the displayed geometry)

1. Two-coordinate ARA improves Experiment 9 remaining-division MAE by at least 10% versus age alone.
2. Four-coordinate candidate improves Experiment 9 remaining-division MAE by at least 10% versus the matched raw polynomial control.
3. Four-coordinate candidate improves Experiment 9 remaining-division MAE by at least 5% versus two-coordinate ARA.
4. Two-coordinate ARA achieves Experiment 9 slowdown AUROC at least 0.65 and exceeds age alone by at least 0.05.
5. Four-coordinate candidate slowdown AUROC exceeds the raw polynomial control by at least 0.05.
6. Two-coordinate ARA improves external Experiments 1–6 remaining-division MAE by at least 5% versus age alone.

If a holdout outcome lacks both classes, its event gate is unavailable rather than silently redefined.

## Interpretation ladder

- If ARA does not beat age: T452 is best described as completed-lifespan geometry.
- If ARA beats age but the four-coordinate candidate does not beat the matched raw polynomial: prospective relational signal exists, but no special four-coordinate advantage is supported.
- If the four-coordinate candidate beats the matched raw polynomial on untouched Experiment 9: the predeclared relational geometry adds prospective structure in this dataset. It still does not establish “Time itself” or a physical four-dimensional sphere.
