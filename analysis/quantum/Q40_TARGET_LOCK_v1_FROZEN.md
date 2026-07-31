# Frozen Target Lock — Q40 Conditional Return-Flow Relation Reversal

**Test ID:** `Q40-RETURN-FLOW-RELATION-REVERSAL-v1`  
**Target lock date:** 27 July 2026  
**Locked after:** Q40 fidelity, protocol and pretarget audit hashes  
**Locked before:** archive download, extraction or numerical inspection

## Public deposit

- **Dataset:** Akhouri, Shandera and Henry, *Dataset for 6–14 qubits
  evolving on network with varying connectivity*
- **Zenodo DOI:** `10.5281/zenodo.16753415`
- **Record:** `https://zenodo.org/records/16753415`
- **Deposited filename:**
  `unnati_submit_12_inhomo_v1_greedy.hdf5.zip`
- **Deposited MD5:** `c04eb02b1766d9f83fb0240689d209a5`
- **Deposited size shown by Zenodo:** `290.4 MB`
- **Primary connectivity branch:** `c2`
- **Expected source structure from deposited description:** `500` time
  steps across `100` trials, including all two-qubit density-matrix
  partitions and connectivity at each time step

## Deterministic selection record

The frozen pretarget procedure required:

1. metadata enumeration only after hashing the Q40 core packet;
2. exclusion of archives numerically opened in earlier ARA quantum work;
3. compatible raw 12-qubit, 500-slice, 100-trial density-matrix structure;
4. lexicographic selection of the first remaining deposited filename;
5. branch `c2` as primary.

The already-open `pure_*` targets were excluded. Repository text searches
across `analysis/quantum`, `MASTER_PREDICTION_LEDGER.md`,
`CLAIMS_STATUS.md` and `FableConvo/PROVENANCE_LEDGER.md` returned no prior
mention of an `inhomo` or `therm` target. The first compatible remaining
filename in deposited lexical order was
`unnati_submit_12_inhomo_v1_greedy.hdf5.zip`.

## Lock

No archive value, HDF5 group, derived matrix, quadrant coordinate, event
count or outcome metric from this target was inspected before this lock.

The primary verdict must use branch `c2`. Other branches are secondary and
cannot rescue the primary. If the downloaded MD5 differs from the deposited
MD5, or if the target lacks the expected schema, Q40 stops without choosing a
replacement after value access.
