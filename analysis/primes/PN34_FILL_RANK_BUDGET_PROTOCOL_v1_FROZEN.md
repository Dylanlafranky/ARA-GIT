# PN34 remaining-fill rank budget — protocol v1 FROZEN

**Test ID:** `PN34/FILL-RANK-BUDGET/v1`  
**Frozen:** 22 July 2026, before fresh target anchors, candidates or truth were calculated  
**Fidelity:** `PN34_FILL_RANK_BUDGET_FIDELITY_PACKET_v1_DRAFT.md`  
**Development:** `PN34_FILL_RANK_BUDGET_DEVELOPMENT.json` (opened PN26 evidence only)

## Question

Does the PN33-style remaining-fill coordinate of PN26's omitted Phase B parent prospectively calibrate how many
Phase A quiet readings are required, across new scales?

## Frozen construction

For each scale anchor `S`, declare the rung `S -> 2S`, generate all prime children through

\[
p\leq\lfloor\sqrt{2S}\rfloor,
\]

and split their cumulative logarithmic weight at the closest half exactly as in PN26. The lower complete parent is
Phase A and the retained complement is Phase B.

For every target anchor `N`, seal the first three Phase A quiet candidates. No primality routine or target label is
allowed in the primary builder.

For the omitted parent, calculate

\[
R_B=\prod_{p\in B}\frac{p}{p-1},
\qquad
x_B=2\frac{\log R_B}{\log2},
\qquad
\widehat\pi_k=1-\left(1-\frac1{R_B}\right)^k.
\]

`x_B` is constant within a cohort. It is therefore registered as a **population rank-budget prior**, not an
individual candidate classifier.

## Fresh cohorts

These intervals were searched in repository methods/records before freezing and had not been used by an earlier
prime test.

| Cohort | Interval | Seed |
|---|---|---:|
| low | `[89,000,000, 89,500,000)` | 34001 |
| middle | `[89,000,000,000, 89,000,500,000)` | 34002 |
| high | `[8,900,000,000,000, 8,900,000,500,000)` | 34003 |

Sample 2,000 distinct deterministic anchors per cohort. Retain a maximum search offset of 4,096.

## Registered endpoints

For each cohort separately:

1. **Top-1 calibration:** observed first-reading coverage is within `1.5` percentage points of `pi_hat_1`.
2. **Top-2 calibration:** observed first-two coverage is within `0.5` percentage points of `pi_hat_2`.
3. **Top-3 calibration:** observed first-three coverage is within `0.15` percentage points of `pi_hat_3`.
4. **Rank budgets:** observed top-two coverage is at least `99%`, and observed top-three coverage is at least `99.9%`.
5. **Direction across scale:** the ordering of predicted top-one coverage across the three cohorts matches the
   ordering of observed top-one coverage, with ties retained.
6. **Benchmark:** report row-level Brier score and log loss for the fill prior, the frozen pooled PN26 prior
   (`0.9398333333`), and the conditional PNT prior `D_A/log(S)`. This benchmark is descriptive and cannot replace
   endpoints 1–5.
7. **Independent reconstruction:** every sealed candidate and coordinate is independently reproduced, and the full
   prime truth mask passes deterministic spot checks.

## Decision rule

- **Supported population rank-budget crosswalk:** endpoints 1–5 and 7 pass.
- **Partial:** calibration passes at two of three depths or two of three scales, but not all registered endpoints.
- **Null:** adequate data show no useful calibration or the direction is reversed.
- **Implementation failure:** freeze, reconstruction, prime truth or ordering checks fail.

No result may be described as individual miss prediction unless a varying pre-label coordinate separates first-state
hits from misses within cohorts. PN34 does not register such a coordinate.

## Separation and reproducibility

1. Hash this protocol, the primary builder and independent validator.
2. Run the primary builder to seal fresh anchors, ranked candidates and population priors without labels.
3. Hash the prediction file.
4. Only then run the validator, which reconstructs the parent independently and opens prime truth.
5. Preserve all manifests, predictions, validated rows, results, notebook outputs and validation receipts.

