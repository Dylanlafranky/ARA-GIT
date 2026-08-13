# T357 - physical pendulum Irrationality Di-ARA transfer

**Run date:** 11 August 2026  
**Source:** dynamicslab MultiArm-Pendulum experimental records, Zenodo 10.5281/zenodo.6633719  
**Frozen overall verdict:** **NOT SUPPORTED AS A COMPLETE PHYSICAL TRANSFER**

## Plain-language answer

This test asked whether a second pendulum, viewed through the first pendulum's cycle, behaves like a structured path that keeps missing closure rather than like either an ordinary repeating loop or shuffled motion. The single pendulum was the known closure reference. The double pendulum was not assigned an outcome in advance.

The overall verdict follows the frozen gates exactly. Individual supported components remain useful even when the complete transfer verdict fails. Finite experimental data can establish coherent non-closure over the observed horizon; it cannot prove that an underlying frequency ratio is mathematically irrational.

5 of the six grouped gates passed. The failure was specific: **G4, coherent non-closure**. The free and driven-1 double records returned to almost the same child phase after one arm-1 cycle (`rho=0.993, miss=0.0024` and `rho=0.997, miss=0.0051` turns). They are phase-locked at this cut, not irrationality examples. Driven-2 did not show clean closure, but its one-cycle coherence fell to `0.547`; that is too incoherent to qualify as the ordered, repeatedly missing path frozen in the claim.

The strong partial result is that coupling opened more relational addresses in all three strata while retaining substantial history dependence. Shuffling preserved `x_P` exactly but raised `x_R` by `1.31` to `1.84` and lowered closure coherence in every double record. Broken lineage was penalised in both driven records. The instrument therefore transferred physically, but these particular coupled runs did not instantiate its coherent-nonclosing quadrant.

## Record-level readings

| family | run | windows | x_P | x_R | one-cycle rho | one-cycle miss | best rho |
|---|---|---:|---:|---:|---:|---:|---:|
| single | free | 1 | 0.600 | 0.065 | 1.000 | 0.0000 | 1.000 |
| single | driven1 | 7 | 0.600 | 0.065 | 1.000 | 0.0000 | 1.000 |
| single | driven2 | 6 | 0.600 | 0.065 | 1.000 | 0.0000 | 1.000 |
| double | free | 40 | 1.168 | 0.103 | 0.993 | 0.0024 | 0.999 |
| double | driven1 | 18 | 1.268 | 0.123 | 0.997 | 0.0051 | 0.999 |
| double | driven2 | 12 | 1.576 | 0.636 | 0.547 | 0.0260 | 0.746 |

`x_P` reads finite/reused to open/resolving. `x_R` reads relation-determined to stochastic residual. The one-cycle columns test whether the child returns to the same phase after one arm-1 parent cycle.

## Frozen gates

| gate | result | requirement | observed |
|---|---|---|---|
| G1 | PASS | single closure referee in >=2/3 records | 3 |
| G2 | PASS | double-minus-single x_P >=0.20 in >=2/3 and positive median | hits=3; median=0.667838 |
| G3a | PASS | double x_R <1.25 in >=2/3 | 3 |
| G3b | PASS | shuffle raises x_R >=0.25 in >=2/3 | hits=3; values={'free': 1.8373055971963126, 'driven1': 1.6518628993328144, 'driven2': 1.307579201847783} |
| G3c | PASS | shuffle lowers best rho >=0.15 in >=2/3 | hits=3; values={'free': 0.6164652363886567, 'driven1': 0.6064243032405577, 'driven2': 0.3465541568974785} |
| G3d | PASS | shuffle preserves x_P within 0.02 in all six | 0.0 |
| G4 | FAIL | coherent nonzero one-cycle miss in >=2/3 doubles | 0 |
| G5 | PASS | broken lineage penalty >=0.15 in >=2/3 doubles | hits=2; values={'free': 0.0025722025248998692, 'driven1': 0.5659053253204483, 'driven2': 0.4701937663705277} |
| G6a | PASS | reversal preserves x_P and best rho in all six | max_dxP=0.000000; max_drho=0.000000 |
| G6b | PASS | reversal flips orientation within 0.02 in >=5/6 | hits=6; max_error=0.000000 |

Grouped gates: `{"G1": true, "G2": true, "G3": true, "G4": false, "G5": true, "G6": true, "overall": false}`

## What the controls mean

- **Shuffle** keeps every observed phase value but destroys their order. A rise in `x_R` with unchanged `x_P` means the instrument correctly assigns the damage to history rather than support.
- **Reverse** asks whether the same path is recognised when traversed backwards. Support and unsigned closure should remain while orientation changes sign.
- **Broken lineage** gives the parent clock a physically unrelated arm-2 history. A penalty indicates that the true parent-child pairing contains information not supplied by a plausible child path alone.

## Data sufficiency and QA

All three declared single records and all three declared double records were processed. Complete six-cycle windows per record ranged from 1 to 40. The analysis summarised within physical record before comparison; it did not treat the many windows as independent experiments.

## Evidence boundary

This is a controlled transfer of the T348 instrument to one public pendulum archive. It does not prove universal ARA geometry, a mathematically irrational frequency, or that all coupled pendulums occupy the same sector. Driven and free files are separate experimental runs rather than perfectly matched interventions.

## Reproduction

```powershell
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\t357_pendulum_irrationality_di_ara.py'
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\validate_t357_pendulum_irrationality_di_ara.py'
```

## Artifact index

- frozen claim and protocol: `T357_PENDULUM_IRRATIONALITY_DI_ARA_*_v1.md` plus SHA-256 records;
- complete sampled windows: `T357_PENDULUM_IRRATIONALITY_DI_ARA_WINDOW_SERIES.csv`;
- window metrics and lag curves: `T357_PENDULUM_IRRATIONALITY_DI_ARA_WINDOW_METRICS.csv`, `T357_PENDULUM_IRRATIONALITY_DI_ARA_CLOSURE_CURVES.csv`;
- record summaries and gates: `T357_PENDULUM_IRRATIONALITY_DI_ARA_RECORD_SUMMARY.csv`, `T357_PENDULUM_IRRATIONALITY_DI_ARA_FROZEN_GATES.csv`;
- data QA: `T357_PENDULUM_IRRATIONALITY_DI_ARA_DATA_QA.csv`;
- machine verdict: `T357_PENDULUM_IRRATIONALITY_DI_ARA_RESULTS.json`;
- visual: `T357_PENDULUM_IRRATIONALITY_DI_ARA_FIGURE.png`.
