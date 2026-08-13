# T369 - Muon-capture daughter closure

**Date:** 12 August 2026  
**Frozen verdict:** **COMMON-PARENT RECOVERED; PARTIAL ADDED RELATION; FULL CLOSURE NOT SUPPORTED**

## Result first

The known same-parent relation was tested on **354,273** untouched
capture-enriched stopped-muon rows. Prompt gamma-like presence improved
neutron-presence cross-entropy by
**+1.7577%**
(bootstrap 95% interval **[+1.6214%, +1.8853%]**).
Prompt-present rows had a tagged-neutron rate of **20.439%**,
versus **7.096%** when the prompt child was absent: an
enrichment of **2.881x**.

The frozen joint prompt-time x prompt-energy Di-ARA address added
**+1.1447%** predictive value beyond prompt presence alone.
It improved three-class neutron-multiplicity prediction by
**+2.7462%** over
the unconditional model, and first-neutron timing prediction by
**-0.9992%**.

However, prompt energy alone performed **+2.8962%**,
slightly better than the joint address's **+2.8823%**.
The observed added signal is therefore energy-led; this test did not recover a
two-coordinate timing-energy mixing advantage.

## Plain-language ARA reading

The public record clearly retains the common-parent handover: seeing the prompt
capture child changes the probability of seeing the delayed neutron child from
that stopped muon. This is expected physics and validates the cut.

The stronger question is whether the precise prompt child's position carries
additional relation beyond its mere presence. The frozen gates below decide
that separately; recovering the known relation cannot rescue a failed deeper
claim.

## Population QA

- Source rows: **1,986,465**
- Capture-enriched holdout: **354,273**
- Prompt-present holdout: **20,040**
- Prompt-plus-neutron holdout: **4,096**
- Source MD5: `59056d97657ed04b3d19c7766a976519`
- Source SHA256: `b6bb10270e6c604935b47687293470caeafd01172288170d83349043566cd05a`

## Frozen gates

| gate | result |
|---|---:|
| G1 source QA | **PASS** |
| G2 coverage | **PASS** |
| G3 common parent recovery | **PASS** |
| G4 same row specificity | **PASS** |
| G5 replication | **PASS** |
| G6 continuous added value | **PASS** |
| G7 multiplicity information | **PASS** |
| G8 timing relation | **FAIL** |

## Controls

- Common-parent permutation exceedances: **0 / 1000**
- Mismatched-packet common-parent effect: **-1.4020%**
- Timing-shuffle exceedances: **104 / 1000**
- Strict `5-15 MeV` timing effect: **-1.1467%**
- Time-only neutron-presence effect: **+1.7589%**
- Energy-only neutron-presence effect: **+2.8962%**

## Scientific boundary

The source does not label true nuclear capture per row. Prompt absence and
neutron absence include detector inefficiency, and first-neutron time is a
thermalisation/detection coordinate long after the prompt handover. The source
paper itself uses high-energy gamma candidates as a predominantly
single-neutron reference, so recovering the binary association is a crosswalk,
not a new discovery.

## Reproduction

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\t369_muon_capture_daughter_closure.py'
```
