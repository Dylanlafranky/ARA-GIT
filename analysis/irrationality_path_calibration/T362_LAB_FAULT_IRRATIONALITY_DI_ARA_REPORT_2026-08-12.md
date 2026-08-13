# T362 — laboratory-fault Irrationality Di-ARA

**Run date:** 12 August 2026  
**Frozen verdict:** **NOT SUPPORTED ON THIS PHYSICAL ARCHIVE**  
**Gate vector:** `PASS, FAIL, FAIL, FAIL, FAIL, FAIL`  
**Independent validation:** **PASS — 11/11 checks**

## Plain-language result

The physical fault itself genuinely traversed all four ARA child quadrants. Local shear-stress loading and local slip movement were independent measurements rather than an algebraically forced mirror, and every quadrant held substantially more than the frozen 1% minimum.

When those children were compressed into the proposed Irrationality parent, however, every one of the 341 causal windows remained in **one parent quadrant: `Ab`**. The parent therefore did not execute the expected multi-quadrant handover.

Its strongest change occurred only **0.058 seconds after the main slip**, which is visually and descriptively sharp. But the wrong-paired stress/movement control produced the same timing. The correctly coupled pair therefore did not uniquely locate that event. On untouched holdout slices, the two-axis relation also failed to predict the next movement better than the simpler controls.

The correct conclusion is consequently:

> This archive contains a real four-quadrant child traversal and a sharp parent response at rupture, but the frozen Irrationality-parent and predictive claims are not supported. At this scale the proposed parent coordinate acts like an open/residual regime descriptor, not a complete navigator of the slip handover.

## What was measured

### Dense primary event

- Local shear stress: S20 at `x = 73.15 mm`.
- Local fault displacement: L3 at `x = 70 mm`.
- Original sampling: `2 µs`.
- Frozen analysis bins: non-overlapping `2 ms`.
- Common synchronized record: `22,275` bins across approximately `44.55 s`.
- Calibration: first 80% only.
- Untouched holdout: final 20%, containing the main rupture.

The main-slip time was defined independently as the largest positive local-displacement increment. The ARA handover was defined label-blind as the largest chronological step in the sliding `(x_P,x_R)` parent path.

### Replication layer

Ten dry and five water-pressurized pre-mainshock fault-coupling histories were tested separately. This layer tested only the connection-side handover; it was not used to invent a missing movement coordinate.

## Frozen gate results

### G1 — independent physical traversal: PASS

- All source MD5 values matched the published Zenodo records.
- Both frozen SHA-256 files matched.
- Outside `±0.1 s` of rupture, raw coordinate correlation was `r = -0.07549`; the axes were not forced complements.
- Physical quadrant occupancy:
  - `Ab`: `6,074` bins (`27.27%`);
  - `aB`: `8,219` bins (`36.89%`);
  - `bA`: `4,100` bins (`18.41%`);
  - `Ba`: `3,882` bins (`17.43%`).

This is a strong instrument-level result: the two independent physical cuts retain four-state geometry rather than merely duplicating one variable.

### G2 — Irrationality parent traversal: FAIL

- Parent windows: `341`.
- Parent occupancy: `Ab = 341`; every other quadrant `0`.
- Qualifying parent quadrants: `1/4`, below the frozen requirement of at least two.
- Strongest parent step: `0.058 s` after main slip, inside the 1.024 s timing allowance.

The timing half passed, but the required parent traversal did not. The result is a one-quadrant compression, not a multi-quadrant parent handover.

### G3 — broken-geometry discrimination: FAIL

- Real chronological timing error: `0.058 s`.
- Median of 100 same-value time shuffles: `22.534 s`.
- Connection-only timing error: `29.126 s`.
- Movement-only timing error: `18.502 s`.
- Wrong-paired stress/movement timing error: `0.058 s`.

Real chronology strongly beat destroyed time and either axis alone. It did **not** beat the deliberately wrong stress/movement pairing. The sharp parent step is therefore tied to the event boundary but is not specific to the correct two-axis coupling.

### G4 — two-axis movement record: FAIL

All methods predicted the *next* signed movement from the preceding slice; the response was not included in its own feature vector.

| Method | Holdout RMSE | MAE | Direction agreement |
|---|---:|---:|---:|
| two-axis directional | 0.7577 | 0.6065 | 0.5277 |
| direction-blind | 0.7572 | 0.6160 | 0.4970 |
| connection-only | **0.7377** | 0.6032 | 0.4914 |
| movement-only | 0.7562 | 0.6051 | 0.5262 |
| wrong pair | 0.7438 | **0.5947** | **0.5358** |
| persistence | 1.0104 | 0.8212 | 0.4584 |

The full relation did not beat every control by 10%; it did not beat any of the four non-persistence controls on RMSE. Direction agreement also remained below the frozen 0.65 floor.

### G5 — held-out rupture localization: FAIL

The primary predicted movement magnitude at the actual main-slip slice was at the `72.37th` percentile of holdout risk, below the frozen top-1% requirement.

The method did not anticipate the rupture as an exceptional next movement.

### G6 — repeated connection handover: FAIL

- All histories in final 20%: `9/15`, below `12/15`.
- Dry: `4/10`, below `8/10`.
- Fluid: `5/5`, above `4/5`.

The fluid histories form a clean positive subgroup, but the frozen replication claim was joint and therefore fails. The medium difference is a follow-up question, not a post-hoc rescue.

## ARA interpretation

The visual impression of “mainly one quadrant” is correct **at the parent level** and wrong **at the child/physical level**:

- The physical connection–movement path visits all four child quadrants.
- Coarse-graining its angular history yields one open/residual parent state (`Ab`) across the complete record.
- Rupture produces a sharp movement *inside that parent regime* rather than a demonstrated parent-quadrant crossing.

This makes the present operational distinction useful:

1. **Child traversal** records the instantaneous mixture of physical connection and movement.
2. **Parent compression** summarizes whether recent angular addresses are reused/open and whether successor movement is determined/residual.
3. A violent physical event does not automatically imply that the chosen parent compression must cross a ridge. It may instead be an extreme event within one broad parent regime.

The one-quadrant result may mean that this laboratory event is open/residual at the one-second parent scale, or that the current `x_P/x_R` compression is too coarse for stick-slip. T362 alone cannot choose between those explanations.

## Evidence boundary

T362 does not support earthquake prediction, universal ARA geometry, or a completed Irrationality Di-ARA fault mechanism. It does support a narrower physical observation: independent stress and slip cuts produce nontrivial four-state ARA geometry, while the tested parent compression and one-step navigator fail to add unique rupture information on this archive.

No core ARA axiom is changed from this failed domain realization. The result belongs in the empirical calibration record.

## Reproduction

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'analysis\irrationality_path_calibration\t362_extract_acosta_coupling.py'
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\t362_lab_fault_irrationality_di_ara.py'
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\validate_t362_lab_fault_irrationality_di_ara.py'
```

## Main artifacts

- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_FIGURE.png`
- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_RESULTS.json`
- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_FROZEN_GATES.csv`
- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_TIMESERIES.csv`
- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_PARENT_WINDOWS.csv`
- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_PREDICTION_PATH.csv`
- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_PREDICTORS.csv`
- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_CONTROLS.csv`
- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_REPLICATION.csv`
- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_SOURCE_QA.csv`
- `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_VALIDATION.md`

