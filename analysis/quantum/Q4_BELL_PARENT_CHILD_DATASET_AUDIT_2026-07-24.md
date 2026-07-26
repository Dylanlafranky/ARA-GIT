# Q4 public Bell-tomography dataset audit

**Audit date:** 24 July 2026  
**Target-value status:** unopened  
**Purpose:** select the first public real-tomography parent/child test after Q3 calibration

## Selected source

- Figshare item: **Figure 2 — Bell states tomography**
- DOI: <https://doi.org/10.6084/m9.figshare.14160476.v2>
- authors: Mateusz Madzik and Serwan Asaad
- selected archive: `UPUP-DOWNDOWN.zip`
- Figshare file ID: `26690663`
- size: `41,182,988` bytes
- required MD5: `8cd8a5f2b3b9a2ccd090e47312bcc390`
- license: CC BY 4.0

The repository description states that it contains raw current traces acquired during prepared Bell-state
tomography and MATLAB scripts that reproduce the analysis.

## Scientific source context

The associated open paper, **“Bell-state tomography in a silicon many-electron artificial molecule”**, reports
two-qubit state tomography using parity readout. Its published methods specify fifteen linearly independent Pauli
projections:

`ZZ, YZ, XZ, ZY, ZX, YY, YX, XY, XX, YI, XI, IY, IX, ZI, IZ`.

The selected archive name declares the target superposition

\[
\left(|\uparrow\uparrow\rangle-|\downarrow\downarrow\rangle\right)/\sqrt2,
\]

conventionally the \(\Phi^-\) Bell state up to bit-label convention.

## Pre-freeze inspection boundary

Before the Q4 protocol was frozen, only these items were inspected:

- Figshare metadata, file names, sizes, checksum and licence;
- the associated paper and its published fifteen-projection method;
- the ZIP member-name manifest.

No binary current value, MATLAB source text, figure content, fitted probability, reconstructed density matrix or
projection outcome was opened. The archive checksum was verified after download.

The member manifest shows:

- top-level `Bell.m`, `MLE.m` and `nearestSPD.m` scripts;
- raw `.bin` files in timestamped groups;
- paired `_1` and `_2` readout files;
- source `.fig` files.

The manifest is sufficient to freeze the expected parent/child pattern but not yet to guarantee that every raw
file can be decoded independently. Format or completeness failure after freeze will be `INCONCLUSIVE`, not a
failed geometric result.

## Data-quality decision

| Dimension | Pre-freeze assessment |
|---|---|
| provenance | strong: public author tomography deposit linked to an open paper |
| immutability | strong: versioned Figshare DOI and fixed file checksum |
| physical grain | raw current traces grouped by acquisition time and measurement index |
| projection coverage | published method declares all 15 two-qubit Pauli projections |
| leakage risk | author density matrices and figure results must be excluded from prediction inputs |
| interpretation risk | high unless local marginals are separated from pair correlations |
| generalisability | one device, one prepared Bell state, one archived experiment |

**Decision:** suitable for a frozen real-data Bell parent/child geometry test.

