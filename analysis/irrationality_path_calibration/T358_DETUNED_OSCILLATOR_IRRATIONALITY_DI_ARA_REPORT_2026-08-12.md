# T358 - detuned physical-oscillator Irrationality Di-ARA

**Run date:** 12 August 2026  
**Source:** Ocampo-Espindola et al., Zenodo 10.5281/zenodo.15122129  
**Frozen overall verdict:** **NOT SUPPORTED AS A COMPLETE DETUNED PHYSICAL TRANSFER**

## Plain-language answer

This test asked whether two physically coupled but deliberately mismatched oscillators can keep making an orderly nonzero miss, rather than either closing or wandering like unrelated clocks. Forty matched oscillator pairs were read in every experimental record. Each result below is the median physical record, not forty inflated replications.

The archive integrity and shape checks passed: 11 declared files, 80 current channels per file, 200 Hz, and 17827 chronological pair-windows. The analysis did not use the paper's synchronization labels, fitted frequencies, Fourier or Hilbert transforms.

The detunings meeting the complete frozen coherent-nonclosure definition were: **none ohm**. The overall verdict remains tied to all six frozen gates; partial passes do not rescue failures.

## Data-interface audit

**Primary derivative phase-plane clock valid:** **NO**

The median adjacent-step phase-backtrack fraction ranged from 0.459 to 0.464 across records. A physical one-way cycle clock should be overwhelmingly monotone; this audit uses 0.10 as a conservative validity ceiling. The observed value near 0.46 means that the registered eight landmarks were not a faithful eight-part physical oscillation.

This audit threshold was not one of the frozen G1-G6 outcome gates, so the preregistered FAIL remains unchanged. It limits its meaning: T358 shows that this particular raw derivative phase-plane interface failed the registered test. It does **not** establish that the physical oscillators lack the proposed ARA relation. The intended physical geometry question is therefore **inconclusive pending an event-defined raw-waveform clock**.

## Record-level ARA readings

| delta R (ohm) | x_P | x_R | one-cycle rho | one-cycle miss | closing pair share | coherently non-closing pair share |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 1.186 | 1.512 | 0.408 | 0.0422 | 0.000 | 0.000 |
| 50 | 1.208 | 1.520 | 0.407 | 0.0444 | 0.000 | 0.000 |
| 100 | 1.237 | 1.413 | 0.378 | 0.0430 | 0.000 | 0.000 |
| 150 | 1.127 | 1.371 | 0.353 | 0.0480 | 0.000 | 0.000 |
| 170 | 1.090 | 1.221 | 0.349 | 0.0382 | 0.000 | 0.000 |
| 190 | 1.189 | 1.259 | 0.291 | 0.0691 | 0.000 | 0.000 |
| 240 | 1.212 | 1.175 | 0.321 | 0.0537 | 0.000 | 0.000 |
| 290 | 1.232 | 1.213 | 0.336 | 0.0525 | 0.000 | 0.000 |
| 340 | 1.246 | 1.153 | 0.324 | 0.0566 | 0.000 | 0.000 |
| uncoupled 150 | 1.290 | 1.624 | 0.515 | 0.0276 | 0.000 | 0.000 |

`x_P` reads reused to opening addresses. `x_R` reads history-determined to unexplained/stochastic residual. Coherent non-closure requires both high `rho` and a miss greater than 0.03 turns.

## Frozen gates

| gate | result | requirement | observed |
|---|---|---|---|
| G1 | FAIL | 170-ohm closure referee | False |
| G2 | FAIL | coherent non-closure in >=3/7 candidate detunings | 0 |
| G3 | PASS | shuffle chronology penalty in >=4/7; support preserved | hits=7; max_dxP=0.000000 |
| G4 | PASS | coupled candidate structure exceeds uncoupled detuned drift | hits=6; group=True |
| G5 | FAIL | wrong-record lineage penalty in >=4/7 | 0 |
| G6 | PASS | reversal preserves unsigned geometry and reverses orientation | max_dxP=0.000000; max_drho=0.000000; orientation_hits=9 |

Grouped gates: `{"G1": false, "G2": false, "G3": true, "G4": true, "G5": false, "G6": true, "overall": false}`

## Scientific and ARA reading

The established-physics description is two weakly coupled electrochemical populations whose intrinsic frequencies are shifted by resistance detuning. The ARA description is two same-tier identities, each with 40 child oscillators, sampled through direct parent-child phase cuts. The test asks whether the relation remains ordered while failing to reuse the same one-cycle address.

The uncoupled control matters because two precise clocks with different periods can create a perfectly orderly miss without coupling. A genuine relation-specific result therefore needs chronology and lineage information beyond simple frequency drift.

## Evidence boundary

This is one public physical archive with controlled detuning. The chronology and coupling-specificity controls passed, but the primary phase interface failed its independent physical-clock audit. Those partial results are diagnostic, not a supported transfer. This archive cannot prove an exactly irrational number, universal ARA geometry, or uniqueness of any phase cut.

## Reproduction

```powershell
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\t358_detuned_oscillator_irrationality_di_ara.py'
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\validate_t358_detuned_oscillator_irrationality_di_ara.py'
```
