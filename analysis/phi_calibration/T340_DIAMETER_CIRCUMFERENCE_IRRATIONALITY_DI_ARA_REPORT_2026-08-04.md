# T340 — diameter/circumference Irrationality Di-ARA result

**Run:** 4 August 2026  
**Protocol:** `T340_DIAMETER_CIRCUMFERENCE_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md`  
**Protocol SHA-256:** `12CEE15FB825BAC1047AE96194528A0AC1653955E979E2B62977C50DBA2D8451`  
**Cross-domain verdict:** **NOT SUPPORTED**

## Frozen question

Does one complex ARA step separate into an exponential radial/diameter axis (`1/e <-> e`) and a golden circumferential axis (principal step magnitude `phi^-2` turns, orientation-equivalent to `1/phi` the other way)?

## Results

| Domain | Split | N | implied radial alpha | radial winner | implied angular tau | angular winner | joint |
|---|---:|---:|---:|---|---:|---|---|
| recorded_qutrit/three_planes_circle | calibration | 1,575,525 | 1.809114 | octave | 0.266936 | quarter | no |
| recorded_qutrit/three_planes_circle | holdout | 1,571,673 | 1.807079 | octave | 0.267010 | quarter | no |
| recorded_bubbles/octave_relative_roots | calibration | 500 | 1.205287 | plastic | 0.033436 | quarter | no |
| recorded_bubbles/octave_relative_roots | evaluation | 688 | 1.171998 | plastic | 0.022396 | quarter | no |
| recorded_bubbles/octave_relative_roots | holdout | 160 | 1.248485 | plastic | 0.021847 | quarter | no |
| recorded_river/thalweg_rank1 | calibration | 10 | 1.033794 | plastic | 0.051692 | quarter | no |
| recorded_river/thalweg_rank1 | evaluation | 10 | 1.115670 | plastic | 0.084540 | quarter | no |
| recorded_river/thalweg_rank1 | holdout | 11 | 1.092695 | plastic | 0.157511 | quarter | no |
| muon_fusion_model/parent_phi_time_vs_e | development | 2,301 | 1.598937 | phi | 0.210555 | quarter | no |

## Interpretation

The fixed universal placement was not supported: among the three primary real-data holdouts, 0 selected e on the radial axis, 0 selected the golden step on the circumference axis, and 0 selected both. The result can still support the two-axis Di-ARA decomposition while requiring identity-specific radial and angular landmarks.

The two axes remain a valid and useful decomposition regardless of the fixed-constant verdict. A radial failure does not become an angular success, and a nearby `3/8` result is not renamed Phi.

## Evidence boundary

The qutrit, bubble and river archives were opened before T340. They test a frozen new interpretation on inherited measurements, not a pristine discovery. The muon-Fusion population is a construction-positive check only because its idealised schedule already contains exponential and Phi components.

## Reproduction

```powershell
$python = 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python analysis/phi_calibration/T340_diameter_circumference_irrationality_di_ara.py
& $python analysis/phi_calibration/validate_t340_diameter_circumference_irrationality_di_ara.py
```

Outputs:

- `T340_DIAMETER_CIRCUMFERENCE_IRRATIONALITY_DI_ARA_RESULTS.json`
- `T340_DIAMETER_CIRCUMFERENCE_IRRATIONALITY_DI_ARA_SUMMARY.csv`
- `T340_DIAMETER_CIRCUMFERENCE_IRRATIONALITY_DI_ARA_CELLS.csv`
- `T340_DIAMETER_CIRCUMFERENCE_IRRATIONALITY_DI_ARA_FIGURE.png`
