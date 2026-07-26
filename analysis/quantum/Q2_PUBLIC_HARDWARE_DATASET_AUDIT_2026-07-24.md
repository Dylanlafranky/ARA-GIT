# Q2 public quantum-hardware dataset audit

**Audit date:** 24 July 2026  
**Purpose:** choose an open real-hardware source for the first post-Q1 test  
**Target-value status during audit:** unopened

## Selection

The selected source is:

- Georg Arnold and Thomas Werner, **“All-optical superconducting qubit readout”**;
- Zenodo record and immutable DOI version: <https://doi.org/10.5281/zenodo.14033026>;
- file: `AllopticalSCQreadout_data.zip`;
- recorded size: `32,029,038` bytes;
- Zenodo MD5: `d2c73dc589981208cd4444be6adffd26`;
- locally verified SHA-256:
  `73F3E2CA7B3658452B4C171532C751E96D7392DCB8741B87A18E28C7073D67FD`.

The record is public, DOI-pinned, small enough for independent reproduction, tied to a peer-reviewed real
superconducting-qubit experiment, and includes the authors’ analysis notebooks beside raw MATLAB arrays.

## Why this source fits Q2

The archive manifest exposes three useful real-hardware levels:

1. six I/Q readout conditions at `0`, `10`, `50`, `250`, `500` and `1000 Hz`;
2. ground- and excited-state arrays with `50,000` I/Q pairs per state and condition, plus a second readout;
3. raw repeated T1 and Ramsey/T2 measurements with both I and Q channels.

The I/Q material directly tests whether two measured cuts retain state-separation information absent from either
fixed cut alone. The T1/T2 material supplies a secondary longitudinal-versus-transverse dynamics crosswalk.

This is not full Bloch tomography. I and Q are readout quadratures, not the qubit’s `X`, `Y` and `Z` axes.

## Pre-freeze inspection boundary

Before the Q2 protocol was frozen, only the following were inspected:

- Zenodo metadata and publication description;
- archive file names;
- file checksums;
- MATLAB variable names, shapes and data types through `scipy.io.whosmat`;
- NPY array shapes and data types through memory-mapped headers.

No numerical shot values, fitted values, plots, class-separation results or target metrics were opened.

The relevant schema was:

| Material | Variables | Shape |
|---|---|---:|
| each non-prepared I/Q file | `I_g`, `Q_g`, `I_e`, `Q_e` | `1 × 50,000` each |
| repeated second readout | `I_g2`, `Q_g2`, `I_e2`, `Q_e2` | `1 × 50,000` each |
| raw T1 repeat file | `I`, `Q` | `1 × 2,000 × 91` |
| raw T2 repeat file | `I`, `Q` | `1 × 2,000 × 126` |
| time coordinate | `t_ns` | one value per curve sample |

Scalar fields already supplied by the source, including `angle`, `threshold`, `Pgg`, `Pee` and `QNDFid`, are
forbidden as predictors in the primary Q2 test because they contain author-derived outcome information.

## Alternatives considered

Two other public records were considered:

- Zenodo `13710919`, associated with near-millisecond superconducting-transmon relaxation and dephasing;
- Zenodo `18296415`, containing hundreds of repeated T1 curves across eleven qubits.

They remain useful follow-ups. The selected record is the closer Q1 continuation because it contains paired raw
I/Q shots as well as T1 and T2/Ramsey dynamics in one compact public archive.

## Data-quality verdict before analysis

| Dimension | Verdict |
|---|---|
| Source provenance | strong: DOI-pinned author deposit |
| Accessibility | strong: open 32 MB archive |
| Grain | explicit at shot, condition and repeated-curve levels |
| Primary labels | explicit `g/e` variable identity |
| Completeness | six conditions with equal shot counts |
| Leakage risk | manageable if author thresholds/fidelities are excluded |
| Split risk | high under random-row splitting; addressed by whole-condition holdout |
| Generalisability | limited to this device/readout experiment |
| Full-state interpretation | prohibited; I/Q is not X/Y/Z tomography |

**Decision:** suitable for a frozen real-hardware measurement-geometry benchmark.
