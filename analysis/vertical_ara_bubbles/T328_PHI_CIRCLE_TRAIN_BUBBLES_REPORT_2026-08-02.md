# T328 bubble Phi circle-train report

**Run date:** 2 August 2026  
**Frozen protocol:** `T328_PHI_CIRCLE_TRAIN_BUBBLE_PROTOCOL_v1_FROZEN.md`  
**Verdict:** **PARTIAL / MIXED**

## Answer first

The exact positive operator `x[n+1] = (x[n] + 2/phi) mod 2` was applied to
the raw movement headings of uninterrupted bubble identities. It was not
applied to bubble area, speed, radius, merger ratios, or a processed Phi
coordinate.

There were **170 evaluation**
roots and **40 holdout** roots.
The evaluation parent winner was
**persistence** and the holdout
winner was **persistence**. The
evaluation return-fingerprint winner was
**phi**; holdout was
**phi**.

The observed-order shuffle p-values were
`0.490451` (evaluation) and
`0.682432` (holdout). A small value would mean the
recorded ordering carries the proposed Phi carrier more strongly than the
same turns rearranged.

## Frozen candidate ranking

| split | rank | candidate | increment | parent loss | return MAE |
|---|---:|---|---:|---:|---:|
| evaluation | 1 | persistence | 0.000000000 | 0.252979 | 0.160702 |
| evaluation | 2 | two_fifths | 1.200000000 | 0.501035 | 0.293215 |
| evaluation | 3 | silver_conjugate | 1.171572875 | 0.502635 | 0.348570 |
| evaluation | 4 | phi | 1.236067977 | 0.504595 | 0.150745 |
| evaluation | 5 | fibonacci_8_21 | 1.238095238 | 0.504637 | 0.156232 |
| evaluation | 6 | three_eighths | 1.250000000 | 0.509274 | 0.163951 |
| evaluation | 7 | one_over_e | 1.264241118 | 0.517034 | 0.228227 |
| evaluation | 8 | one_third | 1.333333333 | 0.518405 | 0.396351 |
| evaluation | 9 | ridge | 1.000000000 | 0.560841 | 0.604091 |
| holdout | 1 | persistence | 0.000000000 | 0.265177 | 0.209849 |
| holdout | 2 | silver_conjugate | 1.171572875 | 0.506851 | 0.323266 |
| holdout | 3 | phi | 1.236067977 | 0.507745 | 0.163647 |
| holdout | 4 | one_third | 1.333333333 | 0.509126 | 0.372232 |
| holdout | 5 | fibonacci_8_21 | 1.238095238 | 0.509987 | 0.169407 |
| holdout | 6 | two_fifths | 1.200000000 | 0.510458 | 0.283762 |
| holdout | 7 | three_eighths | 1.250000000 | 0.515867 | 0.169351 |
| holdout | 8 | one_over_e | 1.264241118 | 0.518269 | 0.216705 |
| holdout | 9 | ridge | 1.000000000 | 0.546008 | 0.597824 |

## Controls

- Evaluation real-minus-broken mean:
  `-0.002055`
  (95% `-0.008217` to
  `0.003825`).
- Holdout real-minus-broken mean:
  `-0.006278`.
- Negative values favour the real lineage.
- Reversed time is reported separately and never used to choose the primary
  direction.

## Resolution

The nearest fixed candidate was **fibonacci_8_21**.
Its one-step separation from Phi was
`0.002027261` ARA, versus median estimated
heading grain `0.043380102` ARA. The first
registered horizon exceeding that grain was
**None**.

## Post-result return sensitivity (not a frozen gate)

The frozen return gate asked only which fixed candidate had the lowest mean
six-lag error. A later validation audit added paired whole-video uncertainty
without changing that gate or the verdict.

- Phi-minus-`8/21` return error was `-0.005487` in evaluation (95% interval
  `-0.005906` to `-0.005141`) and `-0.005760` in holdout (95% interval
  `-0.006338` to `-0.004868`). Thus exact Phi was the better numerical return
  template in both splits.
- Phi-minus-persistence was `-0.009957` in evaluation (95% interval
  `-0.024073` to `0.009224`) and `-0.046202` in holdout (95% interval
  `-0.178983` to `0.001313`). Those intervals cross zero.

Therefore the return win is reproducible as a ranking and is distinct from
the nearest rational template under this scoring, but it is not securely
better than persistence at the source-video inference grain. The positional
resolution audit also remains insufficient to promote the result as exact
constant recovery. Moreover, the observed mean return did not shrink toward
zero across the larger Fibonacci lags: evaluation rose from `0.126486` at lag
2 to `0.189238` at lag 21, while the ideal Phi template falls from `0.472136`
to `0.042572`. The return win is therefore a fixed-template scoring result,
not an observed Fibonacci near-closure sequence. Full audit:
`T328_PHI_CIRCLE_TRAIN_BUBBLES_POST_RESULT_RETURN_AUDIT_2026-08-02.md` and
`T328_PHI_CIRCLE_TRAIN_BUBBLES_VALIDATION.json`.

## Frozen gates

- `holdout_sufficient`: **True**
- `phi_parent_winner_evaluation_and_holdout`: **False**
- `phi_beats_every_rival_with_registered_uncertainty`: **False**
- `observed_order_beats_shuffle_evaluation_and_holdout`: **False**
- `real_lineage_beats_broken_lineage`: **False**
- `phi_fibonacci_return_winner_evaluation_and_holdout`: **True**
- `multistep_exact_constant_resolution`: **False**

## Boundaries

- This archive was used in earlier bubble tests; T328 is a newly frozen
  operator, not an unopened-data claim.
- The result concerns centroid movement direction at 50 fps.
- No smoothing, interpolation, Fourier processing, eventwise sign selection,
  or carrier reanchoring was used.
- Failure here rejects this particular observable placement, not Phi in every
  bubble property and not the full ARA framework.
