# T351 independent validation

**Status:** **PASSED — 28/28 checks passed**

The validator independently reloaded saved CSV/JSON artifacts, recomputed headline medians and AUROCs, verified frozen hashes and checked that the failed verdict was preserved.

| Check | Status | Detail |
|---|---|---|
| protocol hash | PASS | 8BF4382F69BB278F22E9848C346A36FBA001F60A7CB36AEFC2DD2CD90234DBBB |
| claim hash | PASS | 2353B43F143969F565CFB10A4666508602A822786B49E7755CD59971DBC3ABC0 |
| event count | PASS | 384 |
| time-series count | PASS | 355200 |
| two splits | PASS | ['calibration', 'holdout'] |
| six regime-mode rows per config | PASS | expected 6 |
| phase-scale bounds | PASS | candidate geometry in [0,1] |
| response bounds | PASS | connection response in [0,1] |
| figure exists | PASS | 148690 |
| report evidence boundary | PASS | boundary stated |
| recompute z1_connection_share_at_80 | PASS | 0.810314170415032 |
| recompute z2_lock_order_spearman | PASS | 0.724410236211756 |
| recompute z3_median_k_minus_g_onset_lag | PASS | -0.0226236979166667 |
| recompute z4_pause_connection_gain | PASS | 0.0379814487988347 |
| recompute z4_pause_front_velocity | PASS | 0 |
| recompute z5_reverse_unlock_spearman | PASS | -0.728239116489942 |
| recompute z6_progressive_post_front_response | PASS | 0.999999999998527 |
| recompute z6_memory_post_front_response | PASS | 0 |
| recompute z7_response_auroc | PASS | 1 |
| recompute geometry_only_auroc | PASS | 0.5 |
| recompute late_snap_share_at_80 | PASS | 0.198258820953134 |
| recompute false_seam_response_gap | PASS | 0.970837276151012 |
| primary verdict arithmetic | PASS | False |
| boundary verdict arithmetic | PASS | True |
| control verdict arithmetic | PASS | False |
| gate families complete | PASS | ['boundary', 'control', 'primary'] |
| gate failure preserved | PASS | NOT SUPPORTED |
| tooth records present | PASS | 15504 |
