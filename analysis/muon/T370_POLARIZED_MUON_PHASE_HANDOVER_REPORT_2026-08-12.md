# T370 — Polarized-muon parent-phase handover

> **Superseded sampling interpretation:** T370B's complete-archive audit found
> that only the 230 G acquisition was physically resolved by this first cut.
> The apparent high-field passes were slow envelope structure at an inadequate
> sampling resolution and must not be counted as independent parent-phase
> replications. The frozen T370 numbers remain below for provenance; use
> `T370B_MUON_PHASE_LINEAGE_REPORT_2026-08-12.md` for the corrected result.

## Result

**SUPPORTED AS A CROSSWALK** — the frozen
common parent-phase model passed every primary gate in **3 of
4** independent public acquisitions (required: 3 of 4).

The result is a clean recovery of the known polarized-muon decay relation in
ARA language. It is not yet evidence for a new hidden field: the ARA circle and
the established precessing-spin sinusoid are the same mathematical instrument
at this cut.

## Plain-language reading

Before the muon decays, its directional parent relation rotates. After many
decays, different detectors receive slightly different shares of the visible
positrons depending on that parent phase. A single rotating two-coordinate
parent, learned only before 3 microseconds, predicted part of the detector
pattern after 3 microseconds in 3 acquisitions.

For each individual decay, the unobserved two-neutrino packet carries the
remaining energy and the opposite total momentum in the stopped-muon frame.
That makes it the natural hidden complementary daughter branch. Its exact
closure with the visible electron/positron is conservation bookkeeping, not an
independent empirical success.

## Frozen holdout results

| Run | Acquisition | f (/µs) | lambda (/µs) | ARA RMSE | no-phase | persistence | wrong orientation | corr. | vs no-phase | gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EMU00066666 | LCB1-88 T=135.0 F=1600 | 0.200 | 0.95 | 0.03052 | 0.03202 | 0.03478 | 0.03050 | 0.308 | +4.7% | FAIL |
| EMU00066667 | LCB1-88 T=135.0 F=2200 | 0.200 | 0.35 | 0.03149 | 0.03209 | 0.03630 | 0.03153 | 0.194 | +1.9% | PASS |
| EMU00066668 | LCB1-88 T=135.0 F=3000 | 0.200 | 1.00 | 0.02578 | 0.02800 | 0.03017 | 0.02585 | 0.411 | +7.9% | PASS |
| EMU00066669 | LCB1-88 T=135.0 F=230 | 3.120 | 0.00 | 0.03501 | 0.03761 | 0.04215 | 0.04048 | 0.368 | +6.9% | PASS |

## Exact daughter closure crosswalk

- Events below the stopped-muon Michel endpoint: **1,122,159**
- Median visible daughter ARA: **0.659621**
- Median hidden-packet ARA: **1.340379**
- Maximum numerical closure error in `visible + hidden = 2`:
  **0**

## What this establishes

The pre-decay parent carries directional information that is expressed in the
visible daughter distribution, and a two-pole/circular ARA representation can
recover it from raw detector counts on untouched later time bins. The hidden
combined neutrino packet is the exact complementary daughter in the muon rest
frame.

## What it does not establish

- Standard EMU data do not measure the neutrinos.
- The hidden packet is inferred from conservation, not observed separately.
- The parent-phase ARA model is mathematically the standard polarized-muon
  phase model, so this is a physics crosswalk/recovery rather than a novel
  ARA-only prediction.
- The four acquisitions use different applied fields. They are independent
  repetitions of the frozen method, not identical-condition replications.
- A distinct new claim would require ARA to predict untouched structure beyond
  the standard phase model, or independent directional/energy measurements of
  both visible and invisible daughters.

## Reproduction

```powershell
$env:PYTHONPATH='F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\_vendor'
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\t370_polarized_muon_phase_handover.py'
```

Raw files are public under ISIS experiment DOI `10.5286/ISIS.E.RB1620201`. The repository
does not need to store them; expected SHA-256 hashes are recorded in the JSON.
