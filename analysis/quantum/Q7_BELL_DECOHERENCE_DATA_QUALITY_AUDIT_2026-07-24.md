# Q7 public Bell-decoherence data-quality audit

**Date:** 24 July 2026  
**Test:** `Q7-BELL-DECOHERENCE-v1` / ledger `T266`

## Source and access

- Article: Steinacker et al., *Bell inequality violation in gate-defined quantum dots*, Nature Communications 16,
  3606 (2025), DOI `10.1038/s41467-025-57987-0`.
- Public data: Zenodo DOI `10.5281/zenodo.14880901`, licensed CC BY 4.0.
- Physical preparation: four maximally entangled Bell states in a silicon double quantum dot.
- Intervention: free Ramsey waiting versus a Hahn-echo refocusing pulse.
- Measurement: quantum state tomography at eleven wait times per condition and state.

## File integrity

All four source hashes matched the Zenodo record:

| File | MD5 | Shape |
|---|---|---:|
| `MainFigure5b.csv` | `3991a446f66fc244651dc3c303ea0990` | `4 x 11` |
| `MainFigure5c.csv` | `fc7cc2a7376d5ca1ca81c91611b38500` | `4 x 11` |
| `SuppFigure5a.csv` | `c198c156a7aa2235b2c3c35b6a1aaa35` | `9 x 11` |
| `SuppFigure5b.csv` | `55ff84cddfc6b009fcc626345195af5b` | `9 x 11` |

The source contains no headers. Row and basis labels were recovered from the main and supplementary figure
legends rather than guessed from numerical outcomes.

## Exact source-unit correction

The supplementary Pauli cells are not normalized expectations. They are coefficients \(c_{ij}\) in the density
expansion. Across all `88` cells, \(c_{II}=0.25\) to floating-point precision. The unique normalization is

\[
\langle ij\rangle = 4c_{ij},
\qquad
\langle II\rangle=1.
\]

The initial run treated the coefficients as expectations and returned axes four times too small. This was
preserved as a schema diagnostic. The exact factor-of-four correction was applied without changing any frozen
outcome gate.

## Blindness and leakage

This is **partially blinded**, not fully blind:

- before target calculation, the paper had already disclosed that its reported Bell signal remains above `2` for
  about `15 us` under Ramsey and beyond `100 us` under Hahn echo;
- the published figure was viewed to decode row labels and wait coordinates;
- the numerical Pauli trajectories, physical reconstructions, singular-axis transitions, exact sampled
  Horodecki crossings and retention ratios were not programmatically opened before the protocol was hash-locked.

The primary target was the final six Ramsey waits. Hahn echo is an intervention replication whose coarse
direction was already known.

## Fitness for use

**Fit for the declared calibration.** The source has real physical state preparation, a controlled temporal
intervention, full two-qubit Pauli information, fixed public checksums, and sufficient time coverage to observe
both coherent and decohered regimes.

**Limitations:**

- one device and one experimental deposit;
- eleven sampled waits rather than a dense continuous trajectory;
- no raw shot-level data or uncertainty propagation was supplied in these four CSVs;
- the physical projection used here is transparent eigenvalue-simplex projection, not the authors'
  maximum-likelihood tomography;
- the paper's coarse Bell-lifetime direction was known before registration.

