# T329 actual bubble-handover Phi seam report

**Run date:** 2 August 2026  
**Frozen protocol:** `T329_ACTUAL_HANDOVER_PHI_SEAM_PROTOCOL_v1_FROZEN.md`  
**Verdict:** **NOT SUPPORTED — ACTUAL HANDOVER PHI SEAM**

## Answer first

T329 followed only independently detected binary mergers in which one released bubble ID
continued from child to parent. The inherited bubble's direction immediately before the merger
was compared with its direction immediately after it. Left/right mergers were reflected using
the observed side of the joining child, never by selecting the sign closest to Phi.

Eligible seams were `23` calibration,
`52` evaluation and
`16` holdout.

## Frozen candidate ranking

Lower circular distance is better.

| split | rank | candidate | increment | mean loss | median loss |
|---|---:|---|---:|---:|---:|
| evaluation | 1 | persistence | 0.000000000 | 0.286706 | 0.138734 |
| evaluation | 2 | one_third | 1.333333333 | 0.613541 | 0.627264 |
| evaluation | 3 | one_over_e | 1.264241118 | 0.640843 | 0.675520 |
| evaluation | 4 | three_eighths_grid | 1.250000000 | 0.646321 | 0.689761 |
| evaluation | 5 | fibonacci_8_21 | 1.238095238 | 0.650793 | 0.701666 |
| evaluation | 6 | phi | 1.236067977 | 0.651495 | 0.703693 |
| evaluation | 7 | two_fifths | 1.200000000 | 0.663980 | 0.720581 |
| evaluation | 8 | silver_conjugate | 1.171572875 | 0.673820 | 0.749009 |
| evaluation | 9 | ridge | 1.000000000 | 0.713294 | 0.861266 |
| holdout | 1 | persistence | 0.000000000 | 0.419947 | 0.376063 |
| holdout | 2 | one_third | 1.333333333 | 0.533838 | 0.641734 |
| holdout | 3 | one_over_e | 1.264241118 | 0.546753 | 0.579793 |
| holdout | 4 | three_eighths_grid | 1.250000000 | 0.550314 | 0.565552 |
| holdout | 5 | fibonacci_8_21 | 1.238095238 | 0.553290 | 0.562068 |
| holdout | 6 | phi | 1.236067977 | 0.553797 | 0.561905 |
| holdout | 7 | two_fifths | 1.200000000 | 0.560308 | 0.551378 |
| holdout | 8 | silver_conjugate | 1.171572875 | 0.567415 | 0.551378 |
| holdout | 9 | ridge | 1.000000000 | 0.580053 | 0.623937 |

## Phi comparisons

Phi-minus-rival differences are negative when Phi is better.

| split | rival | mean difference | 95% video-cluster interval |
|---|---|---:|---:|
| evaluation | persistence | +0.364789 | [+0.229724, +0.503693] |
| evaluation | ridge | -0.061800 | [-0.129560, -0.001535] |
| evaluation | silver_conjugate | -0.022325 | [-0.040803, -0.006789] |
| evaluation | two_fifths | -0.012485 | [-0.022819, -0.003864] |
| evaluation | fibonacci_8_21 | +0.000702 | [+0.000207, +0.001290] |
| evaluation | three_eighths_grid | +0.005174 | [+0.001798, +0.009019] |
| evaluation | one_over_e | +0.010651 | [+0.003596, +0.018769] |
| evaluation | one_third | +0.037953 | [+0.013895, +0.066744] |
| holdout | persistence | +0.133850 | [+0.018402, +0.332817] |
| holdout | ridge | -0.026256 | [-0.130005, +0.039452] |
| holdout | silver_conjugate | -0.013618 | [-0.042997, +0.014941] |
| holdout | two_fifths | -0.006511 | [-0.024045, +0.010880] |
| holdout | fibonacci_8_21 | +0.000507 | [-0.000290, +0.001352] |
| holdout | three_eighths_grid | +0.003483 | [-0.001990, +0.009288] |
| holdout | one_over_e | +0.007043 | [-0.004025, +0.018782] |
| holdout | one_third | +0.019959 | [-0.013895, +0.053224] |

## Frozen controls

### evaluation

- `real_minus_broken`: `+0.027471` (95% `-0.030247` to `+0.089708`; 50 events, 10 videos).
- `real_minus_contact_scramble`: `+0.022160` (95% `-0.025172` to `+0.069583`; 50 events, 10 videos).
- `real_minus_preordinary`: `-0.005568` (95% `-0.116364` to `+0.130818`; 42 events, 12 videos).

### holdout

- `real_minus_broken`: `-0.009657` (95% `-0.077181` to `+0.052514`; 16 events, 3 videos).
- `real_minus_contact_scramble`: `+0.072178` (95% `+0.000000` to `+0.144729`; 16 events, 3 videos).
- `real_minus_preordinary`: `+0.036033` (95% `-0.074406` to `+0.289824`; 11 events, 3 videos).

## Information³ bookkeeping

The declared contact decomposition satisfied

\[
x_{AA}=(x_{AB}+x_{BA})\bmod2
\]

with maximum numerical discrepancy `4.441e-16`.
This validates the decomposition but is not evidence for Phi.

## Resolution and scope

The nearest fixed candidate was `fibonacci_8_21`. Its one-step
separation from exact Phi was `0.002027261` ARA, while the
median estimated seam-turn grain was `0.037217916` ARA.

The archive contains too few repeated merger lineages for a Fibonacci near-return test.
Therefore T329 is a one-step handover test only.

## Frozen gates

- `evaluation_phi_winner`: **False**
- `holdout_phi_winner_underpowered`: **False**
- `evaluation_phi_beats_all_with_cluster_interval`: **False**
- `lineage_and_contact_side_specificity`: **False**
- `event_specificity_vs_pre_event_turn`: **False**
- `exact_constant_resolution`: **False**
- `strict_holdout_sufficient`: **False**
- `multi_handover_fibonacci_test_available`: **False**

## Reproduction

- production: `work/run_t329_actual_handover_phi_seam.py`
- independent validator: `work/validate_t329_actual_handover_phi_seam.py`
- result JSON: `T329_ACTUAL_HANDOVER_PHI_SEAM_RESULTS.json`
- validation JSON: `T329_ACTUAL_HANDOVER_PHI_SEAM_VALIDATION.json`
- events: `results/T329_ACTUAL_HANDOVER_PHI_SEAM_EVENTS.csv`
- candidate scores: `results/T329_ACTUAL_HANDOVER_PHI_SEAM_CANDIDATE_SCORES.csv`
- controls: `results/T329_ACTUAL_HANDOVER_PHI_SEAM_CONTROLS.csv`
- figure: `T329_ACTUAL_HANDOVER_PHI_SEAM_FIGURE.png`
