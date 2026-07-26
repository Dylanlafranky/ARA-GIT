# Q5 four-Bell-state public dataset audit

**Audit date:** 24 July 2026  
**Raw-value status at freeze:** the three additional state archives were not downloaded or opened  
**Purpose:** replicate the Q4 parent/child result across all four Bell-state identities

## Controlling source

- Figshare item: **Figure 2 — Bell states tomography**
- DOI: <https://doi.org/10.6084/m9.figshare.14160476.v2>
- authors: Mateusz Madzik and Serwan Asaad
- licence: CC BY 4.0
- associated paper: <https://arxiv.org/abs/2008.03968>

The Figshare API declared four immutable archives:

| File ID | Archive | Declared prepared parent | Size (bytes) | MD5 |
|---:|---|---|---:|---|
| `26690657` | `UPDOWN-DOWNUP.zip` | \(\Psi^-\) | `307629500` | `1724b4484ffb88e41dbac5f50981e91a` |
| `26690660` | `UPDOWN+DOWNUP.zip` | \(\Psi^+\) | `305874138` | `43f782ed4404b01393fb57a2da5d1534` |
| `26690663` | `UPUP-DOWNDOWN.zip` | \(\Phi^-\) | `41182988` | `8cd8a5f2b3b9a2ccd090e47312bcc390` |
| `26690666` | `UPUP+DOWNDOWN.zip` | \(\Phi^+\) | `151973378` | `3275210b912d51e5f10ba99d93ad6ca5` |

Q4 has already opened and reconstructed only `UPUP-DOWNDOWN.zip`. The other three archive values remain
untouched at the Q5 freeze.

## Intended grain and comparability

The source paper declares the same fifteen two-qubit Pauli projections for Bell-state tomography. Q5 treats:

- one archive as one prepared-state replication;
- the raw classified acquisition record within each measurement orientation as the bootstrap grain;
- the same six local children, three same-axis parent relations and six mixed-pair controls for every state.

The Q4 raw-current decoder, current threshold, state threshold, Pauli reconstruction and ARA affine map are
frozen unchanged. Per-archive acquisition timestamps may be read after freeze solely to map the raw records to
the declared orientations.

## Leakage boundary

Before freeze, Q5 used only:

- Figshare item metadata;
- archive names, file IDs, sizes and checksums;
- the already published ideal Bell/Pauli sign identities;
- the completed Q4 decoder and thresholds.

Q5 did not inspect any raw value, MATLAB source, figure, fitted probability, density matrix or reconstructed
projection from the three additional archives.

## Data-quality decision

| Dimension | Assessment before freeze |
|---|---|
| provenance | strong: author deposit linked to the experimental paper |
| immutability | strong: versioned DOI and file checksums |
| target coverage | exactly the four declared Bell parents |
| decoder comparability | strong if each archive retains the Q4 acquisition schema |
| leakage risk | controlled by freezing before downloading the three new archives |
| replication grain | four prepared states, but still one device/deposit |
| generalisability | does not establish cross-device or cross-day replication |

**Decision:** suitable for a frozen four-parent discrimination and parent/child replication test.

