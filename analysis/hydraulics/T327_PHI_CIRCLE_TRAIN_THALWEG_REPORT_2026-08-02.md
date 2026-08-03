# T327 river thalweg Phi circle-train report

**Run date:** 2 August 2026  
**Frozen protocol:** `T327_PHI_CIRCLE_TRAIN_THALWEG_PROTOCOL_v2_FROZEN.md`  
**Verdict:** **NOT SUPPORTED**

## Answer first

The exact T325 Phi carrier did **not win** the fixed-candidate parent comparison on the deepest-bed path. The parent winner was **persistence**; the local-increment winner was **persistence**. Phi's parent loss was `0.471736` ARA.

The real downstream order had lower-tail shuffle `p=0.550945`. Among the same 41 downstream-ordered elevation-rank paths, the thalweg ranked **16/41** for the Phi parent carrier (1 is best); the 40-control median was `0.480439`.

This is a direct path test, not a test of all river dynamics. The 40 controls are matched sections of the same bed and therefore establish feature specificity, not independent replication.

## Frozen candidate ranking on the thalweg

| candidate | increment ARA | parent loss | sign | local loss | sign |
|---|---:|---:|:---:|---:|:---:|
| persistence | 0.000000000 | 0.266390 | + | 0.166635 | + |
| two_fifths | 0.800000000 | 0.463598 | - | 0.760837 | - |
| ridge | 1.000000000 | 0.466637 | + | 0.833365 | + |
| phi | 0.763932023 | 0.471736 | + | 0.724769 | - |
| fibonacci_8_21 | 0.761904762 | 0.475791 | + | 0.722742 | - |
| three_eighths | 0.750000000 | 0.483610 | - | 0.710837 | - |
| one_over_e | 0.735758882 | 0.528882 | - | 0.697541 | - |
| silver_conjugate | 0.828427125 | 0.551548 | - | 0.789264 | - |
| one_third | 0.666666667 | 0.552311 | + | 0.666467 | - |

## Downstream-order controls

- Observed Phi parent loss: `0.471736`.
- 10,000-shuffle median: `0.464910`; 95% interval `0.354235–0.566365`.
- Lower-tail permutation p-value: `0.550945`.
- Reversed path loss: `0.444687`.
- Circular seam-shift range: `0.414057–0.576810`.

## Resolution

The nearest tested fixed rational to Phi was **fibonacci_8_21**. Their one-step separation is `0.002027261` ARA, while the median raw neighbour spacing at the thalweg is `0.022067024` ARA. The local exact-constant claim is therefore **not resolution-eligible**. The first declared horizon that separates the two beyond that raw grain is **13**.

## Frozen gates

- `phi_parent_winner`: **False**
- `downstream_order_p_lt_0_05`: **False**
- `thalweg_below_control_median`: **True**
- `thalweg_best_ten_percent`: **False**
- `fibonacci_return_no_worse_than_best_fixed`: **False**
- `local_exact_phi_resolution`: **False**
- `multistep_phi_resolution`: **True**

## Boundaries

- Inner bank `0` and outer bank `2` are the predeclared ARA orientation.
- One sign is selected for the complete path; signs are not changed event by event.
- No smoothing, fitted thalweg, interpolation, Fourier transform, or after-result rotation was used.
- A free increment was diagnostic only: `0.018400` with parent loss `0.104302`.
- Fixed lateral-index paths have zero local movement by construction; their median persistence loss was `0.033160`.
