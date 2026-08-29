# T453 findings — prospective lifespan and four-coordinate geometry

## Result in one sentence

Prefix-only ARA coordinates carry modest prospective information about the unseen remainder of individually tracked yeast lifespans, but the proposed four-coordinate construction does not yet reveal an independent sphere or time boundary.

## What changed from T452

T452 described complete lifespans after both endpoints were known. T453 hides every cell's future at each prediction cut. Individual total generation count, final elapsed time, future intervals, and completed 0–2 normalization are forbidden predictors.

## Main numbers

- Usable cells: 217 (86 development, 12 untouched same-platform holdout, 119 external transfer).
- Prefix predictions: 2,131.
- Experiment 9 remaining-division MAE:
  - age only: 2.428
  - raw polynomial: 2.519
  - two-coordinate ARA: 2.301
  - four-coordinate candidate: 2.292
- Two-coordinate ARA improves on age by 5.24% in Experiment 9 and 11.42% in the 119-cell external transfer.
- Four-coordinate candidate improves on raw polynomial by 9.03% in Experiment 9, with a positive cell-cluster bootstrap MAE-gain interval, but improves on two-coordinate ARA by only 0.38%.
- Slowdown AUROC in Experiment 9:
  - age: 0.434
  - raw polynomial: 0.718
  - two-coordinate ARA: 0.682
  - four-coordinate candidate: 0.682
- Frozen gates: 2 of 6 passed.

## Four-coordinate geometry

The candidate used generation, clock, size, and Rpl13A concentration. Six of twelve holdout cells crossed the reference radius² = 1 during an eligible prefix. The median crossing was G1 11 with 4.5 observed divisions still remaining. At the crossing, a median 85.6% of radius² came from generation plus clock; size contributed about 12% and Rpl13A about 2% on average.

This means the radius is currently dominated by the visible lifespan axes. It is not a universal death ridge. Size/Rpl13A bend the path enough to help one prediction comparison, but they do not define a new common boundary.

## ARA interpretation

The result is stronger than a completed-lifespan inversion because all predictions are issued before their endpoints are known, and the two-coordinate relation transfers externally. It is weaker than discovery of a hidden time dimension because the fourth-coordinate candidate does not beat the already-working two-coordinate ARA, and it does not improve the local slowdown handover.

The most useful next cut is another independent, genuinely time-facing child measured longitudinally in the same individual cells. It must improve over both two-coordinate ARA and a matched nonlinear raw control.
