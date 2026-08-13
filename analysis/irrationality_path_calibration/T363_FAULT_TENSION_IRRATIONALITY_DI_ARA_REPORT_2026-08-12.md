# T363 — fault-tension Irrationality Di-ARA

**Run date:** 12 August 2026  
**Frozen verdict:** **NOT SUPPORTED ON THIS PHYSICAL ARCHIVE**  
**Frozen gate vector:** `PASS, FAIL, FAIL, PASS, FAIL, FAIL`  
**Independent validation:** **PASS — 13/13 checks**

## Plain-language result

Changing the measured identity from movement to tension made a substantial difference.

The dense laboratory event showed a physically coherent tension cycle:

1. stored shear tension remained near the high pole;
2. slip was followed by a large stress release;
3. the release coordinate reached `1.979` on the 0–2 scale;
4. stored tension fell by `1.176` ARA units;
5. the tension-only higher parent made its strongest transition `0.282 s` from slip and beat every frozen chronology, missing-coordinate and wrong-marker control.

Across the independent 15 stress-drop events, **all 15** repeated three core components:

- stored tension fell by `0.343–0.735` ARA units;
- release reached `x_F=1.982–2.000`;
- accumulation again dominated after approximately `129–131` source rows.

But the full frozen Irrationality Di-ARA claim still failed:

- the dense record ended before its release ratio returned below the ridge;
- every replication event occupied two qualifying child quadrants rather than the preregistered three;
- the higher Irrationality-parent handover repeated in only `6/15` events;
- the parent step at the independently calculated maximum tension-release time was only at the `69.64th` percentile, not the required top 1%.

The correct conclusion is therefore:

> The data strongly recover an ordinary two-state tension ARA—accumulation and release—with repeatable return to accumulation. They do not support the stronger claim that the selected higher Irrationality parent supplies a universal, repeatable fault-tension handover at this scale.

## What changed from T362

T362 used:

`stored shear stress × displacement movement`.

That asked whether the two-axis relation navigated the next movement. It failed.

T363 instead used:

`stored shear tension × signed stress transfer`.

The second coordinate was

\[
x_F=\frac{2R}{A+R},
\]

where `A` is accumulated positive stress change and `R` is released negative stress change in a causal local window. Thus:

- `x_F=0`: accumulation-dominant;
- `x_F=1`: equal local accumulation and release;
- `x_F=2`: release-dominant.

Displacement marked the physical slip independently; it was not allowed to define the tension coordinates.

## Dense-event findings

### Source and identity QA — passed

- All five source MD5 values matched the public Zenodo metadata.
- Both frozen SHA-256 records matched.
- Outside `±0.1 s` of slip, `corr(x_S,x_F)=0.1498`; the axes were not forced complements.
- Maximum calculated tension release occurred `0.078 s` after the independently marked displacement slip.

### Child tension path

All four physical gradient quadrants were present across the full dense event:

| Quadrant | Bins | Share |
|---|---:|---:|
| `Ab` | 2,234 | 10.03% |
| `aB` | 12,059 | 54.14% |
| `bA` | 7,116 | 31.94% |
| `Ba` | 866 | 3.89% |

Near slip:

- median stored tension before slip: `2.000`;
- median stored tension after slip: `0.824`;
- storage fall: `1.176`;
- maximum release coordinate: `1.979`.

The dense child gate failed only because `x_F` did not return below `1` during the available `0.30 s` post-slip tail. The record ended while the 0.1-second release accumulator still remained release-dominant.

This is an observational boundary, not proof that reconnection never occurred.

### Higher Irrationality parent

The parent used three quadrants:

- `aB`: `1,280` windows;
- `Ab`: `86`;
- `bA`: `11`.

Its globally strongest transition was `0.282 s` from slip, within the frozen `0.512 s` timing requirement. However, the parent step nearest maximum calculated tension release was only at the `69.64th` percentile. The parent therefore reacted strongly in the wider slip interval but did not put its exceptional step exactly at the tension-release maximum.

## Chronology and marker specificity — passed

The real parent handover error was `0.282 s`.

| Comparison | Timing error |
|---|---:|
| real chronology | **0.282 s** |
| 100-shuffle median | 20.150 s |
| reversed chronology | 13.766 s |
| storage-only | 28.550 s |
| signless transfer | 28.550 s |
| wrong marker 0.25 | 33.698 s |
| wrong marker 0.50 | 22.560 s |
| wrong marker 0.75 | 11.422 s |

This is the clearest positive Irrationality result: correct ordered tension geometry contained event-specific handover timing that disappeared when order, transfer orientation, or the physical event marker was broken.

It is still only one dense event and cannot overcome the failed replication gate.

## Fifteen-event replication

### Frozen child gate: 0/15

Every event failed the requirement of at least three qualifying child quadrants because every event used exactly two at the fixed cut.

Crucially, every event passed all other child components:

| Component | Result |
|---|---:|
| stored tension fell by at least 0.25 | 15/15 |
| release reached at least 1.5 | 15/15 |
| accumulation again dominated within 512 rows | 15/15 |
| three qualifying child quadrants | 0/15 |

The reconnection rows were tightly concentrated at `129–131` rows after the drop. That consistency is stronger than the frozen pass/fail headline alone suggests, but it supports a two-quadrant tension cycle rather than the preregistered three-quadrant geometry.

### Frozen parent gate: 6/15

- Dry: `5/10`.
- Fluid: `1/5`.
- Combined: `6/15`.

All 15 event parents visited four qualifying quadrants, but only six put their globally strongest step within 128 source rows of the stress drop. Several strongest parent changes occurred at the window boundary near `+383` rows instead. The present parent estimator is therefore not a stable universal handover locator for these event windows.

## ARA interpretation

The result separates three layers:

1. **Tension state:** stored stress moves from high to lower values.
2. **Tension transfer:** the same event moves from accumulation-dominant to release-dominant and later returns to accumulation dominance.
3. **Irrationality history parent:** the ordered circumference sometimes produces an event-local parent handover, but not with sufficient repeatability across the 15 events.

At this cut, the first two layers are strongly supported. The third is not.

The two-quadrant replication is compatible with a relatively direct tension coupling:

`high storage + accumulation → high release + falling storage → renewed accumulation`.

It does not require a third child quadrant to appear at appreciable occupancy. Requiring three was a reasonable frozen attempt to distinguish a richer Di-ARA path, and the data rejected that stronger form cleanly.

## Evidence boundary

T363 does not establish field-earthquake prediction, a universal fault Irrationality Di-ARA, or a universal fractal-sphere law. It supports a narrower physical realization:

- stress storage and signed release form a useful ARA tension identity;
- the release boundary aligns closely with independently observed slip;
- correct chronology matters in the dense record;
- the ordinary accumulation/release cycle replicates extremely consistently;
- the present higher Irrationality-parent compression is not yet repeatable enough.

No failed gate is revised after seeing the result.

## Reproduction

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'analysis\irrationality_path_calibration\t363_extract_acosta_stress_events.py'
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\t363_fault_tension_irrationality_di_ara.py'
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\validate_t363_fault_tension_irrationality_di_ara.py'
```

## Main artifacts

- `T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_FIGURE.png`
- `T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_RESULTS.json`
- `T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_FROZEN_GATES.csv`
- `T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_TIMESERIES.csv`
- `T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_PARENT_WINDOWS.csv`
- `T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_CONTROLS.csv`
- `T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_REPLICATION_EVENTS.csv`
- `T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_REPLICATION_PARENT_WINDOWS.csv`
- `T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_VALIDATION.md`

