# T359 - raw-event-clock oscillator Irrationality Di-ARA

**Run date:** 12 August 2026  
**Source:** Ocampo-Espindola et al., Zenodo 10.5281/zenodo.15122129  
**Frozen overall verdict:** **INCONCLUSIVE - EVENT CLOCK QA FAILED**

## Plain-language answer

T359 repeated T358 on the same physical archive but anchored every 0→2 cycle to a repeated event in the raw current: the signal first entered its lower state and its next rise into the upper state began a new cycle. The clock failed the preregistered physical-period QA.

The detunings meeting the complete coherent-nonclosure definition were **50, 290, 340 ohm**. The result is the median of 40 matched physical cuts inside each record, not 40 independent experiments.

## Event-clock QA

- Records passing every G0 component: `9/11`.
- Record-median event count range: `23.0–80.5`.
- Record-median period range: `2.357–3.816` seconds.
- Record-median valid-period share range: `1.000–1.000`.
- Maximum constructed backtrack fraction: `0.000000`.

## Record-level ARA readings

| delta R (ohm) | x_P | x_R | one-cycle rho | one-cycle miss | closing pair share | coherently non-closing pair share |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 1.714 | 0.019 | 0.997 | 0.0767 | 0.000 | 0.900 |
| 50 | 1.786 | 0.016 | 0.998 | 0.0536 | 0.000 | 0.900 |
| 100 | 1.474 | 0.019 | 1.000 | 0.0138 | 1.000 | 0.000 |
| 150 | 0.600 | 0.066 | 1.000 | 0.0013 | 1.000 | 0.000 |
| 170 | 0.600 | 0.062 | 1.000 | 0.0011 | 1.000 | 0.000 |
| 190 | 0.600 | 0.064 | 1.000 | 0.0012 | 1.000 | 0.000 |
| 240 | 1.759 | 0.014 | 1.000 | 0.0214 | 1.000 | 0.000 |
| 290 | 1.853 | 0.016 | 1.000 | 0.0356 | 0.000 | 1.000 |
| 340 | 1.820 | 0.020 | 1.000 | 0.0428 | 0.000 | 1.000 |
| uncoupled 150 | 1.714 | 0.019 | 0.999 | 0.1816 | 0.000 | 1.000 |

## Frozen gates

| gate | result | requirement | observed |
|---|---|---|---|
| G0 | FAIL | raw event clock physical-period QA | records=11; event_ok=9; period_ok=11; share_ok=11; direction_ok=11 |
| G1 | PASS | 170-ohm closure referee | True |
| G2 | PASS | coherent non-closure in >=3/7 candidate detunings | 3 |
| G3 | PASS | shuffle chronology penalty in >=4/7; support preserved | hits=7; max_dxP=0.000000 |
| G4 | FAIL | coupled candidate structure exceeds uncoupled detuned drift | hits=0; group=False |
| G5 | FAIL | wrong-record lineage penalty in >=4/7 | 0 |
| G6 | PASS | reversal preserves unsigned geometry and reverses orientation | max_dxP=0.000000; max_drho=0.000000; orientation_hits=9 |

Grouped gates: `{"G0": false, "G1": true, "G2": true, "G3": true, "G4": false, "G5": false, "G6": true, "overall": false}`

## Calibration conclusion

G0 failed only because the two shorter uncoupled-control records contained 23 and 28 detected events rather than the frozen minimum of 30. All eleven records passed the physical-period, valid-period-share and one-way-direction checks. The frozen G0 failure is retained.

G1, G2 and G3 passed: the event clock recovered the 170-ohm closure reference, identified coherent non-closure at 50, 290 and 340 ohm, and strongly distinguished real chronological order from shuffled order. However, G4 and G5 failed decisively. Coupled, uncoupled and wrong-record paths all became almost equally deterministic.

The reason is methodological: mapping every oscillator linearly between its own successive events converts any sufficiently recurrent trace into an almost perfect sawtooth. This preserves within-clock order but normalizes away the coupling identity that T359 needed to distinguish. T359 is therefore not supported as a coupling-specific transfer. This event-phase instrument should not be reused for that claim unless raw within-cycle amplitude or shape is retained alongside phase.

## Evidence boundary

This calibration reads one controlled physical archive. A valid-clock failure is evidence that this specific frozen sector prediction did not transfer here; it is not a universal rejection of ARA or Irrationality Di-ARA. Success would remain a finite empirical transfer rather than proof of exact irrationality or bedrock geometry.

## Reproduction

```powershell
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\t359_event_clock_oscillator_irrationality_di_ara.py'
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\validate_t359_event_clock_oscillator_irrationality_di_ara.py'
```
