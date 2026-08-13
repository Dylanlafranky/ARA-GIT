# T368 - Muon decay handover information test

**Date:** 12 August 2026  
**Frozen verdict:** **NO OBSERVABLE PREFORMATION IN THE RELEASED VARIABLES**

## Result first

The event-level Super-Kamiokande record was used to ask whether the duration of
the open muon-parent interval predicts the momentum class of the electron
observed at closure. The primary untouched holdout contained
**325,185** eligible decays.

The ARA parent/daughter table changed holdout cross-entropy by
**+0.022837%** relative to the unconditional daughter model
(95% bootstrap interval **[+0.017127%,
+0.027862%]**). The daughter entropy changed by
**+0.012480%** from the first to the final parent quartile
(95% interval **[+0.003638%, +0.022523%]**).

The coarse quadrant association was **Cramer's V =
0.000038** and the raw time/momentum Spearman
correlation was **0.006513**. The permutation
control had **0 / 1000** effects at
least as large as the observed effect.

## Plain-language translation

The test treats the time between stopping and decay as the open parent path,
and the tagged electron momentum as one visible part of the daughter state. A
positive result would mean that where the parent sits along its waiting path
contains advance information about the daughter. A null result places the
observable organisation at the decay handover or in the daughter products,
not progressively inside the recorded waiting interval.

This record cannot see a hidden internal muon trajectory. It can only test the
information exposed in waiting duration and electron momentum.

## Data QA

- Source: Super-Kamiokande data release `10.5281/zenodo.15081911`
- Rows: **1,986,465** (published: 1,986,465)
- MD5: `59056d97657ed04b3d19c7766a976519`
- SHA256: `b6bb10270e6c604935b47687293470caeafd01172288170d83349043566cd05a`
- Development decays: **488,982**
- Holdout decays: **325,185**
- Rows with tagged neutrons: **81,560**

## Frozen gates

| gate | result |
|---|---:|
| G1 source and implementation QA | **PASS** |
| G2 coverage | **PASS** |
| G3 predictive imprint | **FAIL** |
| G4 not shuffled | **PASS** |
| G5 progressive determination | **FAIL** |
| G6 nontrivial quadrant effect | **FAIL** |
| G7 robustness | **FAIL** |
| G8 added relational value | **PASS** |

## Controls

- Mismatched-daughter improvement: **-0.030496%**
- Permutation-null 95% interval: **[-0.033302%, -0.022061%]**
- Inner-window improvement: **-0.005021%**
- Inner-window narrowing: **+0.004369%**
- Smooth raw-time logistic cross-entropy: **2.07944654**
- ARA-table cross-entropy: **2.07896661**

## Scientific boundary

The released variables do not include the neutrinos, the electron direction,
the per-event muon charge or a continuous measurement of the muon during the
waiting interval. The archive also mixes positive-muon decay, negative-muon
decay and negative-muon nuclear capture. Consequently, this is not a complete
TE-ARA of muon decay and cannot rule out unmeasured internal geometry.

Neutrons are a separate delayed nuclear-capture branch. Their presence is
reported for post-handover context but is not combined with the primary
electron daughter as if it were one decay identity.

## Reproduction

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\t368_muon_decay_handover.py'
```

The source CSV can be restored from:

`https://zenodo.org/records/15081911/files/decayes_and_neutrons.csv?download=1`
