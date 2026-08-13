# T347 cross-rung return and Phase-B ablation report

**Date:** 9 August 2026  
**Frozen protocol SHA-256:** `fecd7973e838dd0b71bdc3d099d56e46154a8212735a4c70c213420cde0c0e16`  
**Evidence boundary:** numerical BAW representation already used in T344–T346; not independent confirmation.

## Answer first

Frozen Gates A/B/C: **FAIL / FAIL / FAIL**.
The frozen Phase-B reconstruction classification is **unresolved**.

In plain language, the chosen `W=30` view did **not** reveal one smooth adult
direction spanning the `W=15` handover. The exact entry/exit pairing was no
more directionally persistent than zero and was worse than matched unrelated
exits. The parent view was less smooth, not more smooth, than the centre's
step-level motion. Finally, the two `7|8` / `8|7` child decompositions did not
show the registered `B then A` ordering in either ordered-transition
information or directness.

The attenuation curve has a clear descriptive shape: `lambda=0` produced the
lowest directional loss, while adding intact, reversed, or wrong-child turns
made reconstruction progressively worse. This does not earn the frozen
"Phase A maintains direction" label because Gate A—evidence that there is a
stable parent direction to maintain—failed.

## Frozen components

| component | estimate | 95% whole-track CI | positive conditions |
|---|---:|---:|---:|
| parent_persistence | -0.012941 | [-0.036032, +0.009260] | 2/3 |
| smoothing_score | -0.060194 | [-0.094948, -0.024999] | 1/3 |
| delta_i_ba | -0.005878 | [-0.020244, +0.007780] | 1/3 |
| delta_d_ba | -0.010332 | [-0.020188, +0.000000] | 0/3 |
| max_perpendicular_departure | +0.323694 | [+0.316643, +0.330395] | 3/3 |
| centre_chord_alignment | +0.176419 | [+0.159044, +0.194219] | 3/3 |

The parent-persistence matched wrong-lineage test gave `p=1.000000` (null median `+0.063966`).

The condition split is not stable: parent persistence was positive in low and
medium flow (`+0.012251`, `+0.052286`) but negative in high flow
(`-0.099542`). Scale-up smoothing was positive only in medium flow. This is
evidence against one common frozen mechanism across the three conditions.

## Graded reconstruction

| model | best lambda | improvement vs lambda=0 | 95% CI | matched-null p |
|---|---:|---:|---:|---:|
| intact | 0.25 | -0.013076 | [-0.018859, -0.007693] | 1.000000 |
| reversed | 0.25 | -0.014598 | [-0.020222, -0.008869] | 1.000000 |
| wrong_child | 0.25 | -0.011421 | [-0.017427, -0.005434] | — |

## Interpretation boundary

The attenuation arm changes a reconstructed angular contribution while holding the observed event fixed. It does not physically remove Phase B. The result tests this operational decomposition only; it cannot establish a universal carrier, energy flow or universal ARA geometry.

The numerical representation is strongly streamwise: using
`abs(sin(theta)) < 0.01`, `60.38%` of retained entry directions and `58.81%`
of exits were near-horizontal. The example panel visibly exposes that
anisotropy. T347 therefore rejects this operational decomposition in this
numerical representation; it is not a clean falsification of a freely
resolved two-dimensional open-spiral geometry.

## Reproduction artifacts

- `T347_CROSS_RUNG_RETURN_AND_PHASE_B_ABLATION_FIGURE.png`
- `T347_CROSS_RUNG_RETURN_AND_PHASE_B_ABLATION_EVENTS.csv`
- `T347_CROSS_RUNG_RETURN_AND_PHASE_B_ABLATION_ABLATION_CURVES.csv`
- `T347_CROSS_RUNG_RETURN_AND_PHASE_B_ABLATION_MATCHED_NULLS.csv`
- `T347_CROSS_RUNG_RETURN_AND_PHASE_B_ABLATION_BOOTSTRAPS.csv`
- `T347_CROSS_RUNG_RETURN_AND_PHASE_B_ABLATION_RESULTS.json`
- `T347_CROSS_RUNG_RETURN_AND_PHASE_B_ABLATION_VALIDATION_2026-08-09.md`
- `t347_cross_rung_return_phase_b_ablation.py`
- `validate_t347_cross_rung_return_phase_b_ablation.py`
