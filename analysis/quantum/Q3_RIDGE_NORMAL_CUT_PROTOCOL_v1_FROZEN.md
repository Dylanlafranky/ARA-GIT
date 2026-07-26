# Q3 ridge-normal quantum-output cut protocol v1 — FROZEN

**Protocol ID:** `Q3-RIDGE-NORMAL-CUT-v1`  
**Date frozen:** 24 July 2026  
**Evidence class:** post-hoc known-source calibration  
**Source:** the already-open Q2 public superconducting-qubit I/Q archive  
**Fidelity:** `Q3_RIDGE_NORMAL_CUT_FIDELITY_v1.md`

## Purpose

Calibrate the corrected ARA cut rule before applying it to a fresh quantum target:

> For an Information-facing readout question, use the training-defined cut perpendicular to the equal-class
> ridge; retain the ridge-tangent cut as the Phase-B/control direction.

## Data and split

Reuse only the non-`_prep`, first-readout arrays from the DOI-pinned Q2 archive:

- `I_g`, `Q_g`, `I_e`, `Q_e`;
- six conditions: `0`, `10`, `50`, `250`, `500`, `1000 Hz`;
- `50,000` paired shots per class and condition.

Run six leave-one-condition-out folds. The complete target condition must not contribute to centring, covariance,
whitening, cut orientation or threshold choice.

## Registered transformation

For each fold:

1. fit the pooled two-class covariance on all five training conditions;
2. form a symmetric inverse-square-root whitener from its eigendecomposition;
3. centre at the training class midpoint;
4. orient \(\hat n_A\) from ground toward excited in the whitened plane;
5. set \(\hat n_B=(-n_{A,y},n_{A,x})\);
6. classify the target using `Phase A >= 0`;
7. classify the target control using `Phase B >= 0`;
8. compare Phase A decisions with an independently computed raw-I/Q LDA;
9. measure the held-out class-centroid displacement along Phase A and Phase B;
10. sweep the cut from `0°` to `179°` in one-degree steps, where `0°` is Phase A and `90°` is Phase B.

Eigenvalues smaller than `max_eigenvalue * 1e-12` make the fold inconclusive. No target-tuned rotation,
regularisation or threshold is allowed.

## Metrics

For every held-out condition report:

- Phase-A balanced accuracy;
- Phase-B/control balanced accuracy;
- raw-I/Q LDA balanced accuracy;
- Phase-A versus raw-LDA prediction disagreements;
- signed held-out separation components \(d_A,d_B\);
- Information-facing separation share \(d_A^2/(d_A^2+d_B^2)\);
- held-out separation angle \(\operatorname{atan2}(d_B,d_A)\);
- best descriptive sweep angle and balanced accuracy.

Also report condition-weighted overall metrics and the worst fold.

## Calibration gates

These gates classify whether the translation instrument is behaving coherently. They are **not** an independent
ARA hypothesis test because the source was already opened.

| Gate | Requirement |
|---|---:|
| C1 Phase-A and raw-I/Q LDA predictions | `0 disagreements` |
| C2 Phase-A condition-weighted balanced accuracy | `>= 0.80` |
| C3 Phase-B/control condition-weighted balanced accuracy | between `0.40` and `0.60` |
| C4 mean held-out Phase-A separation share | `>= 0.90` |
| C5 worst held-out Phase-A separation share | `>= 0.75` |
| C6 training tangent centroid residual | `<= 1e-12` |
| C7 pole-reversed Phase-A decisions | `0 disagreements` |

If all pass, verdict is `CALIBRATED`. A clean gate failure is `NOT CALIBRATED`. Source/schema/implementation
failure is `INCONCLUSIVE`.

## Required interpretation

If calibrated, the result supports this narrow statement:

> On the known Q2 measurement plane, the ARA instruction “cut perpendicular to the readout ridge for the
> Information-facing direction” is a faithful translation of the Fisher/LDA discriminant normal, and that
> training-defined direction generalises across the six held-out hardware conditions.

It does not show that ARA discovered LDA, outperforms LDA, reconstructs a qubit state, or proves universal
fractal spheres.

