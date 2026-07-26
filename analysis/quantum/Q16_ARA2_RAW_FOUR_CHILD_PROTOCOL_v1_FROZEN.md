# Q16 frozen protocol — raw ARA×2 four-child geometry

**Registered:** 25 July 2026  
**Orientation:** `C0/C1` pole signs are conventional and reversible; geometry must survive `x -> 2-x`  
**Fidelity packet:** `Q16_ARA2_RAW_FOUR_CHILD_FIDELITY_v1.md`, `Q16-ARA2-RAW-v1`  
**Class:** corrected `(E/R)` public-data reconstruction; not a recovered blind prediction

## Question

When four public prepared-current identities are read through raw `0–2` ARA cuts, do they preserve two independently
recoverable parent directions and their retained relation on later records, without Pauli, Bell, density-matrix,
Ramsey or Hahn geometry generating the result?

## Source and frozen child order

Public Figshare deposit: <https://doi.org/10.6084/m9.figshare.14160476.v2>.

Only immutable file IDs determine the ARA-stage order:

| ARA child | File ID | Archive checksum (MD5) |
|---|---:|---|
| `C00` | `26690657` | `1724b4484ffb88e41dbac5f50981e91a` |
| `C01` | `26690660` | `43f782ed4404b01393fb57a2da5d1534` |
| `C10` | `26690663` | `8cd8a5f2b3b9a2ccd090e47312bcc390` |
| `C11` | `26690666` | `3275210b912d51e5f10ba99d93ad6ca5` |

Conventional state names are quarantined until the post-result comparison.

## Raw observation and ARA coordinate

1. Verify archive size and checksum.
2. Enumerate acquisition groups using filenames/timestamps only.
3. Align common acquisition-cut indices across the four archives without reading target values.
4. Preserve paired `_1` and `_2` readouts as separate cuts.
5. Within every common cut/readout, use the chronologically first half of records as development and the final half
   as holdout.
6. From pooled development currents only, set the ridge \(m_c\) to the median.
7. For state \(s\), cut \(c\), split \(h\):

\[
x_{s,c,h}
=2\frac{n(I>m_c)}{n(I>m_c)+n(I<m_c)}.
\]

Ties are excluded and counted. Retain raw \(n\), median, quartiles, MAD, minimum, maximum and unsigned activity.
The primary ARA geometry is the complete vector \(X_s=(x_{s,1},\ldots,x_{s,C})\), not its mean.

## Frozen ARA×2 operator

For both development and holdout:

\[
\begin{aligned}
M&=(C_{00}+C_{01}+C_{10}+C_{11})/4,\\
U&=(C_{00}+C_{01}-C_{10}-C_{11})/2,\\
V&=(C_{00}-C_{01}+C_{10}-C_{11})/2,\\
J&=(C_{00}-C_{01}-C_{10}+C_{11})/2.
\end{aligned}
\]

- \(U\): first recovered parent direction;
- \(V\): second recovered parent direction;
- \(J\): retained relation/Information³ candidate;
- \(M\): common parent location, reported but not counted as evidence because pooled ridge construction constrains it.

No direction may be retuned on holdout. Global sign reversal is equivalent and scored by absolute cosine plus the
corresponding child-label reversal.

## Registered predictions

1. **Two-parent survival:** both \(U\) and \(V\) development directions recur in holdout with absolute cosine
   similarity at least `0.80`.
2. **Cut-level direction:** at least `75%` of informative cuts retain the development sign for each parent.
3. **Two binary children:** nearest frozen parent-sign decoding scores balanced accuracy at least `0.80` for both
   parent bits on held-out block bootstraps.
4. **Four-child closure:** the ordered pair of recovered bits identifies the four held-out children with balanced
   accuracy at least `0.70` (chance `0.25`) and exceeds the `99th` percentile of `9,999` child-label shuffles.
5. **Negative control:** four time-block pseudo-children created within each archive must not pass all four gates
   above more than `5%` of `1,000` deterministic control resamples.

## Relation branch — signed before calculation

\(J\) is classified, not forced:

- **stateful retained relation:** holdout cosine at least `0.80`, energy share
  \(E_J/(E_U+E_V+E_J)\ge0.05\), and energy above the `99th` percentile of the label-shuffle null;
- **planar/two-parent closure:** both parent gates pass while \(J\) fails one or more stateful-relation gates;
- **unresolved geometry:** a parent gate fails or acquisition alignment/decoder uncertainty dominates.

This branch prevents a result from being repaired after viewing. It does not treat either planar or stateful closure
as automatic proof of universal ARA.

## Geometry disclosures

The report must include:

- every raw `0–2` cut by child and split;
- full distributions and worked raw-record examples;
- native current activity/dispersion beside normalized ARA position;
- \(U,V,J\) development and holdout vectors;
- parent-axis cosine, sign retention and energy;
- four-child pairwise distances;
- parallelogram-closure residual for all three possible pairings;
- tetrahedral/Cayley–Menger volume and its bootstrap interval;
- child, parent and relation views without averaging them into one ridge;
- all negative controls and failed cuts.

## Conventional comparison quarantine

Only after the frozen ARA results are saved may a separate comparison section attach:

- archive/Bell names;
- Pauli projection labels;
- author threshold or MLE reconstruction;
- density matrix, CHSH or standard two-qubit interpretation.

The comparison may explain or rename a result. It may not alter an ARA coordinate, gate, child order or verdict.

## Falsifier and verdict

The ARA×2 raw-four-child prediction is `NOT SUPPORTED` for this representation if either parent direction fails
the holdout cosine gate, either bit fails its accuracy gate, or the four-child decoder does not beat its frozen
shuffle control. Decoder/alignment failure is `INCONCLUSIVE`.

A pass is at most `SUPPORTED [corrected public-data reconstruction, unreplicated]`. It is not a new Bell-state
discovery, a derivation of quantum mechanics, proof of a hidden fourth degree of freedom or proof of universal
fractal geometry.

## Reproducibility

- deterministic seed: `20260725`;
- bootstrap draws: `2,000`;
- label-shuffle draws: `9,999`;
- control resamples: `1,000`;
- script must run from repository root, verify source checksums and save all derived artifacts beside this protocol;
- validator must independently recompute archive manifest, raw coordinates, contrasts, gates and hashes.

