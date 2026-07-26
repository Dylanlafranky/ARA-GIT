# Q31 source selection addendum — v3 frozen before candidate-6 outcomes

**Frozen:** 2026-07-26 20:00 AEST  
**Parent files:** `Q31_LATTICE_TO_TRAVERSAL_PROTOCOL_v1_FROZEN.md`, Q31 source-selection v1–v2

## Candidate 5 data-gate result

The Dalmasso et al. archive contains five H1 hardware files with 1,280–1,480 shots each, so it easily clears the independent-shot requirement. However, the filenames and repository schema identify only 10, 14, 14, 16 and 18 ordered hardware steps. The longer 600–1,000-step files are classical numerical simulations, not hardware measurements.

Candidate 5 therefore fails the frozen requirement of at least 25 ordered samples around each handover. Q31 does not substitute the emulator or numerical paths and does not calculate a confirmatory flip verdict from this source.

Classification:

**Ineligible for Q31 v1 by ordered-path gate; retained as a later short-path lattice-flow crosswalk.**

## Candidate 6

**Source:** Farid et al., source data for *Inductively shunted transmon: A superconducting qubit with flux noise insensitive plasmon states and a protected fluxon decay exceeding 3 hours*  
**Public record:** Zenodo record `8004359`  
**Archive:** `Source Data _ full_version.zip`  
**Published size:** 297,216,848 bytes  
**Published MD5:** `ced1ed4af893ad064045900903e19a17`

Public metadata state that the repository contains:

- raw superconducting-qubit measurements;
- single-shot I and Q records;
- 500 time traces of consecutive QND pulses per file;
- long fluxon-decay monitoring traces;
- a state check every 30 seconds until tunnelling is detected;
- repeated excitation, monitoring and transition logging;
- raw monitoring records as well as separately logged transition times.

## Provisional eligibility decision

Candidate 6 is selected provisionally because a persistent fluxon state followed by an experimentally detected tunnelling event is a direct measured persistence-to-release transition. Raw I/Q provides at least two fixed-basis coordinates, and repeated traces provide independent units.

Before any ARA outcome calculation, its schema must confirm:

1. at least 30 raw experimental traces with a detected transition;
2. at least 25 ordered raw samples in a common window around each transition;
3. retained I and Q or another two-coordinate raw relation object throughout that window;
4. at least 500 eligible evaluation transitions after the deterministic split;
5. a transition anchor supplied by the experiment’s state detector, not selected by Q31 metrics.

If item 4 cannot be met but items 1–3 and 5 pass, candidate 6 may be reported only as an exploratory geometry run; the frozen confirmatory Q31 verdict remains **inconclusive**.

## Frozen local ARA orientation

For this candidate only:

- `2` = persistent fluxon-state connection;
- `1` = detector-defined tunnelling handover;
- `0` = released/post-tunnelling traversal.

The raw I/Q path is the relation object. The detector-defined tunnelling time is the handover. Q31 cannot move that time or discard unfavourable detected transitions.

## Evidence boundary

A passing result would support the registered ARA transition geometry in a superconducting-qubit fluxon transition. It would not identify the counter-side as a universal hidden Phase B, and it would not establish a general quantum-gravity or metaphysical singularity.
