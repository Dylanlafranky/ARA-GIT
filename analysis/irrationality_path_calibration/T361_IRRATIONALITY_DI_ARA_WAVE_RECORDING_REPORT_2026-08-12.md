# T361 — Irrationality Di-ARA wave recording and recovery

**Run date:** 12 August 2026  
**Source:** Ocampo-Espindola et al., Zenodo 10.5281/zenodo.15122129  
**Frozen verdict:** **NOT SUPPORTED AS A COMPLETE PHYSICAL WAVE RECORDER**  
**Independent validation:** **PASS**

## Question actually tested

This was an instrument-recovery test, not a chance or regime-classification test. The first 60% of complete raw physical cycles recorded the two-wave Di-ARA relation. On the final 40%, the visible parent waveform and only two child entry readings were supplied; the recorder had to rebuild the remaining child waveform.

The retained record was the raw 0–2 parent/child path, its four causal direction states, local movement vectors, circumference angle, radial amplitude, address opening, ordered-relation residual and closure history.

## Frozen complete-wave results

| ΔR (ohm) | RMSE on 0–2 | waveform correlation | direction agreement | quadrant agreement | endpoint error |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.9912 | -0.1435 | 0.5000 | 0.5000 | 0.4431 |
| 50 | 0.8555 | -0.0312 | 0.4921 | 0.4839 | 0.5741 |
| 100 | 0.7967 | -0.0747 | 0.4921 | 0.5000 | 0.4833 |
| 150 | 0.1388 | 0.9701 | 0.9365 | 0.9355 | 0.0269 |
| 170 | 0.0689 | 0.9929 | 0.9683 | 0.9677 | 0.0212 |
| 190 | 0.1369 | 0.9711 | 0.9524 | 0.9516 | 0.0182 |
| 240 | 1.0368 | -0.0644 | 0.4762 | 0.4677 | 0.6375 |
| 290 | 0.9776 | -0.0891 | 0.4762 | 0.4839 | 0.9317 |
| 340 | 0.9846 | -0.0958 | 0.4762 | 0.4839 | 1.2048 |

All six frozen mechanism gates failed because only three of nine records passed the absolute waveform, movement and closure requirements; the four-state comparison passed in zero records, correct-lineage comparison passed in three, and child-to-parent reconstruction passed in one.

## Post-result mechanism diagnostic — T361B

T361B froze a separate diagnostic after the complete-wave result. It asked the prefix Di-ARA for only the **next** child movement from each actual held-out state, rather than feeding each predicted child state recursively into the next lookup.

That distinction changed the diagnosis. Across all nine physical records:

- median next-position error was `0.0183–0.0416` ARA units on the 0–2 diameter;
- median next-direction agreement was `0.927–0.975`;
- all nine records met the declared local-record criterion;
- in the outer regimes, removing the four direction states raised next-position error to `0.114–0.137`, versus `0.032–0.042` for the four-state recorder.

Therefore the complete T361 claim remains failed, but the failure is localized:

- the Di-ARA relation table accurately recorded the **local next movement** throughout the sweep;
- only the `150, 170, 190` ohm band retained enough coherence for 62 recursive hidden steps to remain on the correct complete-wave branch;
- outside that band, small local errors accumulated because the predicted child state became the next lookup address without a renewed information lock;
- the frozen four-state complete-cycle gate failed because direction-blind recovery was already excellent in the coherent band, while the four-state distinction mattered most in regimes where free-running drift later dominated.

This supports a recording interpretation more limited than autonomous whole-wave generation: the current Irrationality Di-ARA is a high-fidelity local relational navigator, but it needs periodic observed cuts or a higher-level correction to restore long hidden paths in more open regimes.

T361B is explicitly post-result and does not rescue or rewrite the T361 verdict.

## Evidence boundary

This concerns one public physical oscillator archive. It supports local relational recording for this declared interface. It does not establish universal ARA geometry, exact mathematical irrationality or unrestricted recovery of missing physical variables.

## Reproduction

```powershell
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\t361_irrationality_di_ara_wave_recording.py'
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\validate_t361_irrationality_di_ara_wave_recording.py'
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\t361b_local_record_vs_free_restoration.py'
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' 'analysis\irrationality_path_calibration\validate_t361b_local_record_vs_free_restoration.py'
```

