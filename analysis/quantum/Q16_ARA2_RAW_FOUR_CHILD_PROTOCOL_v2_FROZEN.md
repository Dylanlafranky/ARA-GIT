# Q16 frozen protocol v2 — raw ARA×2 four-child geometry

**Registered:** 25 July 2026  
**Orientation:** parent signs are reversible; score geometry under `x -> 2-x`  
**Fidelity:** `Q16_ARA2_RAW_FOUR_CHILD_FIDELITY_v2.md`, `Q16-ARA2-RAW-v2`  
**Status:** v2 supersedes unrun v1 after byte-schema audit and before calculation  
**Class:** corrected `(E/R)` public-data reconstruction; not a recovered blind prediction

## ARA object

\[
(A_1,B_1)\times(A_2,B_2)
\xrightarrow{\mathcal C,\ J_{12}}
\{C_{00},C_{01},C_{10},C_{11}\}.
\]

Each parent has its own normalized `TE-ARA=2`. The retained relation \(J_{12}\) is measured, not forced to zero or
renamed from a conventional residual.

## Source and child order

Figshare: <https://doi.org/10.6084/m9.figshare.14160476.v2>.

| Child | File ID | Size (bytes) | MD5 |
|---|---:|---:|---|
| `C00` | `26690657` | `307629500` | `1724b4484ffb88e41dbac5f50981e91a` |
| `C01` | `26690660` | `305874138` | `43f782ed4404b01393fb57a2da5d1534` |
| `C10` | `26690663` | `41182988` | `8cd8a5f2b3b9a2ccd090e47312bcc390` |
| `C11` | `26690666` | `151973378` | `3275210b912d51e5f10ba99d93ad6ca5` |

Only file-ID order fixes child labels. Conventional state names remain quarantined until comparison.

## Raw cuts

- sequential settings: `K0…K8`, identified only by within-archive timestamp order;
- member segments: all `G0…G4`;
- ARA dimensions: `K0G0…K8G4` (`45` total);
- selected records per child/setting: earliest `40` for development and latest `40` for holdout;
- measurement and bucket suffixes provide record order only.

Decode each member as little-endian unsigned 16-bit current:

\[
I=3.0519\times10^{-5}\,(\mathrm{raw}-32766).
\]

This is instrument-unit conversion, not a quantum state reconstruction.

For cut \(c=(K,G)\), derive one common ridge \(m_c\) from equally weighted development records across all four
children. For every record:

\[
x_{s,c,r}
=2\frac{n(I_{s,c,r}>m_c)}
{n(I_{s,c,r}>m_c)+n(I_{s,c,r}<m_c)}.
\]

Retain ties, \(n\), median, quartiles, MAD, minimum, maximum and mean absolute displacement from \(m_c\).

## Parent and relation operator

From the four development or holdout child centroids:

\[
\begin{aligned}
M&=(C_{00}+C_{01}+C_{10}+C_{11})/4,\\
U&=(C_{00}+C_{01}-C_{10}-C_{11})/2,\\
V&=(C_{00}-C_{01}+C_{10}-C_{11})/2,\\
J&=(C_{00}-C_{01}-C_{10}+C_{11})/2.
\end{aligned}
\]

No holdout rotation, pole change, cut deletion or threshold repair is permitted.

## Frozen gates

1. `U` and `V` development/holdout absolute cosine are each `>=0.80`.
2. At least `75%` of informative cuts retain direction for each parent.
3. Held-out record decoding against frozen development parent axes gives balanced accuracy `>=0.80` for both bits.
4. The two-bit child decoder gives four-child balanced accuracy `>=0.70` and exceeds the `99th` percentile of
   `9,999` development-label shuffles.
5. Across `1,000` within-one-archive time-block pseudo-child resamples, no more than `5%` pass gates 1–4 together.

### Relation branch

- **stateful relation:** \(J\) holdout cosine `>=0.80`, energy share
  \(E_J/(E_U+E_V+E_J)>=0.05\), and \(E_J\) exceeds its `99th` label-shuffle percentile;
- **planar closure:** both parents pass but the stateful relation branch fails;
- **unresolved:** parent, decoder or data-quality gate fails.

## Required geometry

Save raw-cut distributions, all child centroids, development/holdout \(U,V,J\), pairwise distances, all three
parallelogram residuals, tetrahedral/Cayley–Menger volume, bootstrap intervals, worked record examples and every
negative control. The pooled centre \(M\) is descriptive only because the common ridge construction constrains it.

## Conventional comparison quarantine

Only after the ARA result JSON is saved may a second section attach archive names, projection names, Pauli/Bell
patterns, density matrices, CHSH or standard interpretations. They cannot alter a cut, gate or verdict.

## Verdict ceiling

A full pass is at most `SUPPORTED [corrected reconstruction, same deposit, unreplicated]`. It is not proof of a
hidden fourth degree of freedom, new quantum dynamics or universal fractality. Failure of a parent/decoder/control
gate is `NOT SUPPORTED` for this representation; invalid byte alignment is `INCONCLUSIVE`.

## Determinism

- seed `20260725`;
- `2,000` held-out bootstraps;
- `9,999` label shuffles;
- `1,000` pseudo-child controls;
- source and protocol hashes verified before calculation;
- independent validator required.

