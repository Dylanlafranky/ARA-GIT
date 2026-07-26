# Q16 — ARA-First Raw Four-Child Quantum Restart

**Date:** 25 July 2026  
**Ledger:** T275  
**Protocol:** `Q16-ARA2-RAW-v2`  
**Frozen protocol SHA-256:** `63a099cf2ab200459d09240862a5e0239dfb241f45126c6474921adbb19fe51e`  
**Verdict:** **SUPPORTED — 8/8 frozen gates**

## Outcome

The corrected ARA-first test recovered two stable parent directions and a stable retained relation from the raw
current records of four prepared quantum identities.

In ARA language, the tested architecture was:

\[
\underbrace{(A_1,B_1)}_{\text{parent ARA 1}}
\times
\underbrace{(A_2,B_2)}_{\text{parent ARA 2}}
\longrightarrow
\underbrace{\{C_{00},C_{01},C_{10},C_{11}\}}_{\text{four ordered children}}.
\]

The ARA stage did not use Bell-state names, Pauli axes, density matrices, Ramsey filters or Hahn filters to
construct its geometry. The four source archives were renamed in immutable file-ID order. All nine unnamed
measurement settings and all five raw current segments were retained.

The result supports the following limited claim:

> Four already-prepared raw quantum records can be organized as the children of two recurring binary parent
> directions plus a stable relation direction. That geometry generalizes from early to later acquisition-index
> records and is absent from same-archive pseudo-child controls.

It does **not** establish that ARA generated the four quantum identities, add a hidden fifth physical state, prove
universal fractality, or outperform quantum tomography.

## Why this was a restart

The earlier quantum trail increasingly used standard quantum summaries to decide what the ARA sphere ought to
contain. That reversed the intended methodology. Q16 instead used:

1. ARA geometry to declare the expected two-parent/four-child architecture;
2. the rawest available current records to construct 0–2 cuts;
3. a frozen acquisition-index development/holdout split;
4. ARA-native negative controls;
5. conventional quantum interpretation only after the ARA result was saved.

The unrun v1 protocol is preserved. A byte-level pre-run audit showed that `_1..._10` identified acquisition
buckets rather than two parent channels. The corrected v2 protocol was then frozen before any Q16 result was
calculated.

## Native ARA construction

Each raw record was divided into nine unnamed settings `K0...K8` and five retained current segments `G0...G4`,
giving 45 diameter cuts. For cut \(c\), a development-only ridge \(m_c\) was frozen. Each raw record received:

\[
x_c =
2\,
\frac{n(I>m_c)}
     {n(I>m_c)+n(I<m_c)}.
\]

Thus \(x_c=0\) and \(x_c=2\) are the two occupancy poles and \(x_c=1\) is equal occupancy around the frozen raw
ridge. Ties were excluded rather than assigned to either pole.

The four children were combined with the frozen contrasts:

\[
M=\frac{C_{00}+C_{01}+C_{10}+C_{11}}4,
\]

\[
U=\frac{C_{00}+C_{01}-C_{10}-C_{11}}2,
\qquad
V=\frac{C_{00}-C_{01}+C_{10}-C_{11}}2,
\]

\[
J=\frac{C_{00}-C_{01}-C_{10}+C_{11}}2.
\]

`U` and `V` are the two proposed parent directions. `J` is the relation contrast: whether the effect of changing
one parent orientation depends on the other parent orientation.

## Frozen results

| Test | Frozen threshold | Result |
|---|---:|---:|
| Parent `U` holdout cosine | at least `0.80` | `0.877841` |
| Parent `V` holdout cosine | at least `0.80` | `0.829311` |
| `U` cut-sign retention | at least `0.75` | `0.977778` |
| `V` cut-sign retention | at least `0.75` | `0.822222` |
| `U` bit balanced accuracy | at least `0.80` | `0.981250` |
| `V` bit balanced accuracy | at least `0.80` | `0.906250` |
| Four-child balanced accuracy | at least `0.70` and over shuffle 99th | `0.887500` |
| Same-archive pseudo-child false-positive rate | at most `0.05` | `0/1000 = 0` |

The four-child label-shuffle 99th percentile was `0.487625`; the observed result was `0.887500`,
\(p=0.0001\). Nearest-centroid classification reached `0.956250`.

The independent bootstrap interval for four-child accuracy was `[0.8375, 0.93125]`. Independent validation
redecoded raw binaries, reproduced every central metric exactly, reran label/relation shuffles, and repeated
1,000 pseudo-child controls with zero failures.

## The relation is material

The retained relation had:

- development-to-holdout cosine: `0.818388`;
- energy: `0.042857`;
- share of `U+V+J` contrast energy: `0.239840`;
- shuffle 99th percentile: `0.012523`;
- shuffle \(p=0.0001\).

It therefore passed the frozen definition of a **stateful retained relation**.

In plain language: two labels were not enough to describe the measured shape as two unrelated switches. How the
two parent directions combined carried a reproducible part of the raw identity.

## The four children form a tetrahedral relation, not a flat square

The four development centroids had centered rank `3` and normalized tetrahedral volume `0.110957`. The holdout
centroids retained centered rank `3` and normalized volume `0.108646`. All three possible parallelogram residuals
were large.

That matters for ARA fidelity. The architecture is not merely four corners on a flat plane. The two parent
directions require a third relation direction to locate the four children in the measured raw space:

\[
\boxed{A + B + J_{AB}\ \longrightarrow\ \text{locked four-child identity}.}
\]

This is a concrete Information³-style crosswalk: two identities plus their coupling relation.

## The previously discarded segment was not empty

Segment `G0`, which earlier decoders discarded, carried:

- `9.42%` of parent-`U` energy;
- `6.92%` of parent-`V` energy;
- `1.87%` of relation-`J` energy;
- `6.79%` of total `U+V+J` contrast energy.

It is not the main relation channel, but it is not absence. Retaining it preserves part of the raw sphere that
the processed reconstruction had flattened.

## Construction–evidence fence

Some parts of the analysis follow algebraically once four labeled points exist:

- the `M/U/V/J` Walsh decomposition always exists;
- four binary labels can always be written with two bits;
- four centered points can have rank no greater than three.

Those facts are not themselves evidence for ARA.

The empirical content is instead:

- the raw prepared identities are strongly separable;
- the same `U`, `V` and `J` directions recur in later acquisition-index records;
- parent signs persist over 45 independent raw cuts;
- the four-child rule beats 9,999 label shuffles;
- within-archive pseudo-children do not manufacture the same result;
- the non-planar centroid geometry and relative volumes remain stable across the split.

## Post-result conventional quantum crosswalk

Only after the ARA result was saved were conventional names restored:

| ARA child | Public preparation |
|---|---|
| `C00` | \(\Psi^-\) |
| `C01` | \(\Psi^+\) |
| `C10` | \(\Phi^-\) |
| `C11` | \(\Phi^+\) |

The strongest setting concentration was:

| ARA direction | Dominant unnamed setting | Share of that direction's energy |
|---|---:|---:|
| `U` | `K0` | `46.12%` |
| `V` | `K4` | `55.68%` |
| `J` | `K8` | `72.91%` |

The older conventional decoder identifies `K0`, `K4` and `K8` with the three mutually related Bell-correlation
directions conventionally called `ZZ`, `XX` and `YY`. In Bell-state stabilizer algebra, two binary correlation
signs determine the third relation sign. This established quantum structure is an unusually clean comparator for
the ARA result:

\[
\text{parent direction 1}
+
\text{parent direction 2}
+
\text{their retained relation}
\longrightarrow
\text{four Bell identities}.
\]

This comparison does not retroactively make Q16 blind or prove ARA caused the standard structure. It shows that
the ARA-first raw decomposition lands on a physically meaningful established relation after translation.

## Correction to the earlier “unresolved H” idea

Q16 contains all four Bell children. Its third geometric direction is a relation contrast between those four
children, not evidence for a missing fourth Bell child.

The safest revised reading is:

> Q15's unresolved \(H\) is a purity/accounting remainder constructed from processed dynamical summaries. Q16
> shows that the raw static four-state geometry already has two parent directions plus a third relation direction.
> The two quantities may be related, but Q16 does not identify unresolved \(H\) as a hidden Bell state or a
> physical Phase B.

Q15 remains useful as a proxy/coherence audit, but its `self + Other = 2` normalization was not a complete
TE-ARA identity decomposition because mandatory Phase A and Phase B were not independently identified.

## Strongest limitations

1. **Not genuinely blind.** The archive outcomes and earlier Q4–Q15 results were already known. The Q16 operator
   and gates were frozen before Q16 calculations, but this is corrected post-outcome reconstruction.
2. **Possible archive/batch confounding.** The four preparations live in separate archives/acquisition runs.
   Same-archive pseudo-child controls rule out easy within-archive splitting artefacts, but cannot eliminate a
   preparation-correlated device/day/batch effect.
3. **Acquisition-index holdout.** Numeric record order was used as a directional development/holdout split.
   Individual records do not carry enough wall-clock metadata to call this a verified chronological holdout.
4. **One public deposit and one apparatus.** The result needs unchanged replication on another raw source,
   preferably with interleaved preparation labels and per-shot timestamps.
5. **Coordinate, not superior physics.** This test establishes an informative ARA organization of raw records.
   It does not yet predict an unknown quantum outcome more accurately than established quantum methods.

## Next decisive test

Freeze the Q16 operator unchanged, then apply it to an independent raw four-preparation dataset with:

- interleaved or randomized preparations;
- per-shot timestamps;
- common hardware settings;
- all raw readout segments retained;
- a genuinely untouched device/run holdout;
- conventional state names hidden until after scoring.

The decisive replication question is whether the same two-parent-plus-relation architecture recurs without
archive identity being confounded with preparation identity.

## Reproduction

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q16_ara2_raw_four_child_test.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q16_ara2_raw_four_child_validate.py'
```

Primary artifacts:

- `Q16_ARA2_RAW_FOUR_CHILD_RESULTS.json`
- `Q16_ARA2_RAW_FOUR_CHILD_DATA_QUALITY.json`
- `Q16_ARA2_RAW_FOUR_CHILD_VALIDATION.json`
- `Q16_ARA2_RAW_FOUR_CHILD_RECORDS.csv`
- `Q16_ARA2_RAW_FOUR_CHILD_CUTS.csv`
- `Q16_ARA2_RAW_FOUR_CHILD_CONTRASTS.csv`
- `Q16_ARA2_RAW_FOUR_CHILD_CONTROLS.csv`

