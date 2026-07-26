# Q2 public-hardware I/Q ARA protocol v1 — FROZEN

**Protocol ID:** `Q2-PUBLIC-HARDWARE-IQ-v1`  
**Ledger ID:** `T259`  
**Frozen:** 24 July 2026, 06:47 AEST  
**Target-value boundary:** frozen after metadata/manifest/schema inspection and before numerical arrays  
**Fidelity:** `Q2_PUBLIC_HARDWARE_IQ_FIDELITY_v1.md`  
**Dataset audit:** `Q2_PUBLIC_HARDWARE_DATASET_AUDIT_2026-07-24.md`  
**Status:** FROZEN

## Question

On a public real superconducting-qubit readout dataset, does a coupled two-cut ARA representation of I and Q
retain held-out ground/excited separation that one fixed native cut loses, while remaining equivalent to a
standard classifier given the same I/Q information?

This is a real-hardware measurement benchmark. It is not full Bloch tomography and does not derive quantum
mechanics.

## Public source

- DOI: <https://doi.org/10.5281/zenodo.14033026>
- archive: `AllopticalSCQreadout_data.zip`
- required SHA-256:
  `73F3E2CA7B3658452B4C171532C751E96D7392DCB8741B87A18E28C7073D67FD`
- conditions: `0`, `10`, `50`, `250`, `500`, `1000 Hz`

## Eligible primary arrays

Use only non-`_prep` files:

`Fig_4a/IQblobs_{condition}Hz.mat`

and only:

- `I_g`, `Q_g`;
- `I_e`, `Q_e`.

Each must contain exactly `50,000` paired shots per class.

Forbidden primary inputs include `angle`, `threshold`, `Pgg`, `Pee`, `QNDFid`, all author fits and all
publication-level summaries.

## Frozen split

Use six leave-one-condition-out folds.

For each fold:

- the entire named hardware condition is untouched target data;
- the other five complete conditions are training data;
- no target shot contributes to centring, scaling, covariance, axis choice or threshold selection;
- target order is retained;
- no random row split is permitted.

The selected one-cut comparator is chosen inside training only. Perform leave-one-training-condition-out
validation across the five training conditions for I-only and Q-only linear discriminants. Select the cut with
the higher mean balanced accuracy; resolve an exact tie in favour of I.

## ARA coordinate calibration

For each native cut \(u\in\{I,Q\}\), estimate from all training conditions:

\[
\mu_{g,u},\quad \mu_{e,u},\quad
m_u=\frac{\mu_{g,u}+\mu_{e,u}}2,
\]

and pooled within-class standard deviation

\[
s_u=
\sqrt{
\frac{
\sum_g(u-\mu_{g,u})^2+\sum_e(u-\mu_{e,u})^2
}{
n_g+n_e-2
}}.
\]

Orient and transform the cut as

\[
x_u=
1+
\operatorname{sgn}(\mu_{e,u}-\mu_{g,u})
\frac{u-m_u}{s_u}.
\]

If a centroid difference is exactly zero, use positive orientation. If \(s_u\le10^{-15}\), the fold is
`INCONCLUSIVE: DEGENERATE CUT`.

Do not clip the primary coordinates. Report the fraction outside `[0,2]` as a noise/scale diagnostic.

## Registered models

All models use equal class priors.

1. **I-only LDA:** one-dimensional shared-variance linear discriminant on raw I.
2. **Q-only LDA:** one-dimensional shared-variance linear discriminant on raw Q.
3. **Selected one-cut LDA:** I or Q selected from training-only condition validation.
4. **Two-cut ARA LDA:** shared-covariance LDA fitted independently on \((x_I,x_Q)\).
5. **Raw I/Q LDA:** separately implemented shared-covariance LDA on raw \((I,Q)\).
6. **Raw I/Q QDA:** standard quadratic discriminant, secondary only.

Use a Moore–Penrose pseudoinverse with fixed relative cutoff `1e-12`. No target-tuned regularisation is allowed.

The two-cut ARA and raw I/Q LDA receive exactly the same measured information through an invertible affine map.
They are expected to agree; this is a translation audit, not an ARA superiority contest.

## Registered controls

### Pole reversal

Replace both ARA cuts by \(x'_u=2-x_u\), refit on reversed training coordinates and score the reversed target.
Predictions must be invariant.

### Label shuffle

Within each training condition, combine the two classes and permute their labels using seed
`2026072402 + fold_index`. Fit the two-cut ARA LDA and score the true held-out labels.

### Pair destruction

Within each held-out class and condition, circularly shift Q by `10,007` shots while retaining I order. Apply the
fixed ARA classifier. This destroys shot-level I/Q pairing while retaining both one-dimensional class
distributions. It is descriptive because diagonal class separation may not require covariance.

### Exact complement audit

For every target coordinate, verify \(x_u+(2-x_u)=2\). This is algebraic consistency only.

## Metrics and uncertainty

Primary metric: balanced accuracy, equal to ordinary accuracy here because class counts are equal.

Report:

- per-condition confusion counts and balanced accuracy;
- condition-weighted overall balanced accuracy;
- gain over the training-selected one-cut comparator;
- raw I/Q versus ARA prediction disagreement;
- pole-reversal disagreement;
- label-shuffle and pair-destruction performance;
- out-of-range ARA-coordinate fraction;
- Cohen’s kappa and Matthews correlation coefficient;
- target score margins.

For uncertainty, partition each target class into `50` contiguous blocks of `1,000` shots. Use `2,000` paired
bootstrap replicates with seed `2026072403`, resampling the six conditions and then the contiguous class blocks
within each selected condition. The gain interval is computed from paired ARA-minus-selected-one-cut block
results.

## Primary gates

All seven gates must pass for `SUPPORTED`.

| Gate | Threshold |
|---|---:|
| G1 two-cut ARA balanced accuracy | `>= 0.80` |
| G2 gain over training-selected one cut | `>= +0.005` |
| G3 paired 95% bootstrap lower bound for gain | `> 0` |
| G4 worst held-out-condition balanced accuracy | `>= 0.70` |
| G5 raw-I/Q versus ARA accuracy difference and prediction disagreements | `<= 1e-12` and `0` |
| G6 pole-reversal prediction disagreements and complement residual | `0` and `<= 1e-12` |
| G7 label-shuffle balanced accuracy | `<= 0.55` |

Any clean gate failure is `NOT SUPPORTED`. Missing arrays, schema mismatch, degenerate cuts, implementation
failure or source-integrity failure is `INCONCLUSIVE`.

## Registered replications and secondary outputs

The following cannot rescue a failed primary gate:

1. repeat the full six-fold analysis on `I_g2`, `Q_g2`, `I_e2`, `Q_e2`;
2. repeat it on the six `_prep` files for both first and second readouts;
3. report QDA as a standard non-linear same-input comparator;
4. map the raw repeated T1 and Ramsey/T2 curves into training-calibrated ARA paths and compare them with the
   source-appropriate exponential and damped-oscillation descriptions.

The T1/T2 arm is a separate dynamics crosswalk. It must not be merged numerically with the I/Q state-discrimination
verdict and cannot be called multi-axis tomography.

## Reporting boundary

The final report must give four separate conclusions:

1. **data quality:** whether the public source and split were valid;
2. **benchmark:** whether G1–G7 passed;
3. **coordinate geometry:** whether two cuts retained information absent from one and whether raw/ARA accounts
   tied under equal information;
4. **physics boundary:** what this does *not* establish about qubit state, universal fractality or ARA ontology.

## Planned artifacts

- `q2_public_hardware_iq_test.py`
- `q2_public_hardware_iq_validate.py`
- `Q2_PUBLIC_HARDWARE_IQ_FOLDS.csv`
- `Q2_PUBLIC_HARDWARE_IQ_BLOCKS.csv`
- `Q2_PUBLIC_HARDWARE_IQ_SUMMARY.csv`
- `Q2_PUBLIC_HARDWARE_IQ_RESULTS.json`
- `Q2_PUBLIC_HARDWARE_IQ_VALIDATION.json`
- `Q2_PUBLIC_HARDWARE_IQ_REPORT_2026-07-24.md`
