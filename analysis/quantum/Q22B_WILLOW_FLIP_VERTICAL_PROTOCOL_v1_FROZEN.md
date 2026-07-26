# Q22B frozen protocol v1 — flip-aware Tier-4 to Tier-1 vertical ARA

**Written before q8_7 outcome extraction:** 26 July 2026  
**Source:** Google Quantum AI Willow QEC deposit, DOI `10.5281/zenodo.13273331`

## Correction and prediction

Q22A omitted the singularity inversion incurred while lifting Tier 4 to Tier
1. Three completed boundaries give:

\[
F_3(x_4)=2-x_4.
\]

Q22B freezes that correction before opening the remaining untouched
distance-5 patch `d5_at_q8_7`.

The directional prediction is:

\[
\boxed{
F_3(x_4(t,t+1))
\text{ is closer to future Tier 1 than to matched past Tier 1}
}
\]

at fixed delays \(d=1,2,3\), with no post-result delay selection.

## Data and staging

Use X and Z separately:

| Role | Cycles | Shots |
|---|---:|---:|
| development | 13 | 50,000 |
| untouched holdout | 30 | 50,000 |

Geometry staging contains only metadata, ideal detector coordinates and raw
detector events. The four logical-outcome files may be extracted only after
the protocol, implementation and outcome-blind calibration are checksum
frozen.

## Coordinates

The local Tier-4 coordinate for child \(c\) over \((t,t+1)\) is:

\[
x^{(4)}_{t,c}
=\frac{2S_{t+1,c}}{S_{t,c}+S_{t+1,c}}.
\]

The Tier-1 whole relation is:

\[
J_t=2(P_{t,AB}+P_{t,BA}).
\]

The Tier-1-facing Tier-4 coordinate is:

\[
\tilde x^{(4)}_{t,c}=2-x^{(4)}_{t,c}.
\]

Static and delayed vertical readings replace \(x^{(4)}\) with
\(\tilde x^{(4)}\):

\[
V^{(0)}=\frac{2\tilde x^{(4)}}{\tilde x^{(4)}+\bar J_t},
\qquad
V^{(+d)}=\frac{2\tilde x^{(4)}}{\tilde x^{(4)}+J_{t+1+d}},
\qquad
V^{(-d)}=\frac{2\tilde x^{(4)}}{\tilde x^{(4)}+J_{t-d}}.
\]

Future and past slices are equally distant from the completed Tier-4 window
and never reuse one of its endpoints.

The Information³ lock retains the Tier-1 identity, the **local** Tier-4
identity, and their flip-aware vertical relation. The coordinate is normalized
phase position; the separate half-amplitude-per-downward-tier rule is not
treated as if it were the same quantity.

## Frozen feature sets

| Model | Coordinates |
|---|---:|
| `flip_vertical_state` | 18 |
| `flip_vertical_travel` | 34 |
| `flip_vertical_both` | 42 |
| `flip_past_control` | 34 |
| `flip_broken_control` | 42 |
| `unflipped_control` | 42 |
| `q21_child_topology` | 24 |
| `event_fraction` | 1 |
| `flip_vertical_both_plus_count` | 43 |

The first three have the same summaries as Q22A, except the relation uses
\(2-x_4\). The unflipped control freezes Q22A orientation. The broken control
pairs Tier 4 from shot \(s\) with Tier 1 from shot \(s+1\).

## Model and null

Fit the same standardized nearest-centroid direction on 13-cycle development
records and apply it without refitting to 30-cycle holdout records. Report
AUROC, average precision, accuracy, balanced accuracy, prevalence, all
coefficients and feature counts.

Run `499` development-label permutations per basis with seed `20260726`.
The empirical one-sided p-value denominator is `500`.

## Gates

1. future flip-aware ridge distance is smaller than matched past distance in
   both holdout bases;
2. future flip-aware distance is smaller than broken-shot future distance in
   both holdout bases;
3. `flip_vertical_state` AUROC is at least `0.52` in both bases;
4. `flip_vertical_travel` AUROC is at least `0.52` in both bases;
5. `flip_vertical_both` AUROC is at least `0.55` in both bases;
6. mean primary-minus-unflipped AUROC is at least `0.01`;
7. mean primary-minus-Q21-topology AUROC is at least `0.01`;
8. mean primary-minus-count AUROC is at least `0.01`;
9. mean primary-minus-past AUROC is at least `0.01`;
10. mean primary-minus-broken AUROC is at least `0.01`;
11. permutation p is at most `0.01` in both bases;
12. adding event count changes mean AUROC by less than `0.01`;
13. the primary score direction is concordant in development and holdout in
    both bases.

Every gate is reported. Overall `SUPPORTED` requires all thirteen.
Directional geometry and logical-outcome prediction are also given separate
verdicts.

## Boundary

Q22B tests one flip-aware ARA representation on one processor and one fresh
patch. It does not prove universal fractality, physical causation, a new
quantum state, an absolute inter-tier amplitude law, or decoder superiority.
