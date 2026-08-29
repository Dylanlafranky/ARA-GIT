# T448 — individual fruit-fly lifecycle tomography

## Technical summary

The frozen universal-terminal-point hypothesis failed, but a separately frozen time-facing direction transferred strongly. Across 5,147 complete fly-hours from 47 individual males, a three-coordinate behavioural shadow was built without using lifespan or proximity to death as inputs. Experiments 1–3 supplied 31 development flies; the later, hotter experiment 4 supplied 16 untouched holdout flies.

T448 asked whether unseen flies approached the same three-coordinate terminal region. It failed every frozen point gate: the all-cut AUROC was 0.397, paired win rate was 0.394, and the actual ordering was worse than ordinary shifted endpoints. Traversal↔maintenance alone retained modest signal (AUROC 0.645), but action↔intake and participation↔idle crossed beyond the development terminal centre. The combined state therefore moved away from a fixed point even while following a terminal direction.

T448B then froze the development terminal **direction** as each fly's change relative to itself exactly 24 hours earlier. That direction transferred: terminal mean progress was 0.377 versus a shifted 95% limit of 0.209 (p≈0.0005), 84.0% of terminal observations aligned positively, and median direction cosine was 0.464. The three-cut projection AUROC was 0.703, but participation↔idle alone was 0.712, so multi-cut superiority did not pass.

## ARA reading

The defensible result is not “ARA found the point of death.” The visible handover is better described as a directed passage through a distorted lifecycle shadow. The most stable shared component is a shift from participation toward quiescence/idle over one parent daily cycle; traversal and intake/maintenance relations describe meaningful branch variation but do not yet add predictive information beyond that dominant cut.

The terminal cloud is strongly non-spherical at this scale: its largest-to-smallest standard-deviation ratio is 4.58:1. That supports the user's tomography rule—multiple disks reveal distortion—but does not establish an underlying sphere. The three pairwise plots are ordinary projections of three independent balances, not automatically three Di-ARAs.

## Exact coordinates

Four resolved behavioural parts were retained: traversal (locomotion + altered locomotion), grooming/maintenance, proboscis/intake, and idle/quiescence. Unstereotyped and wall/edge classifications were excluded and retained as QA controls. Because four shares sum to one, they contain three independent balances:

1. traversal ↔ grooming/maintenance;
2. combined external action ↔ proboscis/intake;
3. combined participation ↔ idle/quiescence.

The log-ratio coordinates were robustly centred on development data and mapped onto one common 0–2 display scale. No fly-specific rescaling or lifespan normalization was used.

## Data quality

- 47/47 published HDF5 files were read; 5,147 complete pre-collapse hours were retained.
- Core lifecycle coordinates contain zero missing cells and close numerically to machine precision.
- Environmental logs matched 99.864% of hours; seven rows lacked a temperature/humidity match.
- Median excluded unstereotyped share was 14.48% (95th percentile 29.14%).
- Median excluded edge share was 1.42% (95th percentile 21.21%); high-edge hours remain visible in QA rather than being mistaken for a lifecycle pole.
- The official paper reports accelerated aging/dying under sucrose-agarose, high temperature and low humidity. These recordings are not normal-lifespan fruit flies.

## What passed and failed

### T448 universal terminal point

- Gate A, ≥65% paired wins: **FAIL**, 39.36%.
- Gate B, three cuts outperform every lower-dimensional cut by ≥0.02 AUROC: **FAIL**.
- Gate C, exceed 95% circular-shift null: **FAIL**, p≈0.968.
- Supporting final-24-hour approach slope: **FAIL**, median Spearman −0.168.

### T448B one-cycle terminal direction

- Gate D, real progress exceeds shifted 95% limit: **PASS**, 0.377 vs 0.209; p≈0.0005.
- Gate E, alignment prevalence and cosine: **PASS**, 84.0% positive and median 0.464.
- Gate F, three-coordinate direction beats the best signed single cut by ≥0.02 AUROC: **FAIL**, 0.703 versus 0.712 for participation↔idle.

## Limits

The source's `Collapse (hours into video)` field is an author-provided index landmark and is sometimes earlier than recorded death; the paper does not give a detailed operational definition for that column. The behavioural classifier and collapse annotation both ultimately derive from observation of the animal, so the result is a behavioural precursor/reconstruction test, not an independent molecular prediction of death.

The 24-hour comparison deliberately cancels much of the circadian parent, but it also means flies with fewer than 24 observed hours could not be tested; all published flies here retained at least 32 pre-collapse hours. Environment, starvation, stress and aging are entangled. A normal-food, normal-temperature cohort is needed before generalizing the direction to ordinary lifespan.

## Recommended next cut

Use the 14 tracked body points to split the dominant participation↔idle direction into children: whole-body translation, limb/postural motion after removing translation, gait failure/altered locomotion, and micro-movement during nominal idle. Freeze the 24-hour direction again and ask whether a posture child turns before the coarse behavioural parent. That is the clean route from “shared terminal direction” toward genuinely earlier individual prediction.

## Visuals

- [Data scope and raw behaviours](./results/T448_01_data_scope_and_behaviors.png)
- [Three tomographic disks](./results/T448_02_three_tomographic_disks.png)
- [Combined lifecycle shadow](./results/T448_03_combined_lifecycle_shadow.png)
- [Aligned handover histories](./results/T448_04_aligned_handover_histories.png)
- [All holdout individuals](./results/T448_05_all_holdout_individuals.png)
- [Frozen gates and controls](./results/T448_06_prediction_and_controls.png)
- [Distortion controls](./results/T448_07_distortion_controls.png)
- [Projection distortion](./results/T448_08_projection_distortion.png)
- [Selected complete lifecycles](./results/T448_09_selected_individual_lifecycles.png)
- [Directional histories](./results/T448B_10_directional_histories.png)
- [Direction plane and shift null](./results/T448B_11_direction_plane_and_null.png)
- [Individual terminal arrows](./results/T448B_12_individual_terminal_arrows.png)

## Sources

- McKenzie-Smith et al., 2025, *PLOS Computational Biology*: https://doi.org/10.1371/journal.pcbi.1012753
- Princeton Data Commons lifetime dataset: https://doi.org/10.34770/1sab-8845
- Official analysis code and experiment index: https://github.com/shaevitz-lab/long-timescale-analysis
