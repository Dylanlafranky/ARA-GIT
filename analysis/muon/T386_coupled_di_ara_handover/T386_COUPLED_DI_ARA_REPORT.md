# T386 — coupled Di-ARA muon-handover result

## Outcome

**CALIBRATION STRUCTURE ONLY**

The coupled coordinates improved probability calibration, but the frozen ranking and/or coupling-specific gates did not all pass.

This remains a Class-D liquid-scintillator detector-proxy result.  It does not
measure a neutrino trajectory or prove deterministic muon decay.

## Exact model comparison

| Split | Raw MG AUC | State MS AUC | Determinacy MD AUC | Additive MC0 AUC | Coupled MC AUC | Raw MG log loss | Coupled MC log loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| Validation | 0.741865 | 0.712320 | 0.734674 | 0.712004 | 0.711774 | 0.643351 | 0.633828 |
| Evaluation | 0.741824 | 0.710783 | 0.735617 | 0.710251 | 0.710197 | 0.640918 | 0.632357 |

## Coupling checks

- Validation-selected component comparator: `MS`.
- Evaluation event-bootstrap log-loss improvement, coupled minus comparator:
  median `-0.000054`, 95% interval
  `[-0.000483, 0.000441]`.
- Same-time observed MC evaluation log loss:
  `0.632357`.
- Within-lead shuffled-alignment log loss median:
  `0.632814`;
  observed alignment beat `100.0%`
  of 100 shuffles.
- Time-reversed fixed-model evaluation AUC:
  `0.712179`.
- Forbidden acquisition leakage AUC:
  `0.999978` (audit only).

## Frozen gates

- PASS — `proper_scores_improve_vs_raw_both_splits`
- FAIL — `auc_gain_at_least_0p02_vs_raw_both_splits`
- FAIL — `coupled_logloss_beats_each_component_both_splits`
- FAIL — `evaluation_bootstrap_above_zero`
- PASS — `observed_alignment_beats_95pct_shuffles`
- PASS — `guard_and_forbidden_fields_excluded`


## Interpretation boundary

The event-centred figure includes the final 128 ns and the observed pulse to
show the detector handover retrospectively.  Those samples are absent from the
causal predictor.  A pattern inside the shaded region may describe the local
release geometry; it is not forewarning.

T386 uses the already-opened T385 source.  A successful result would still
require execution on an unopened dated BUAP archive before being described as
external confirmation.

## Reproduction

Run:

```powershell
python analysis/muon/t386_coupled_di_ara_handover.py
python analysis/muon/validate_t386_coupled_di_ara_handover.py
```
