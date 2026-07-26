# Q17 - Which Children Form the Strongest Phase A/B Pair?

**Date:** 25 July 2026  
**Claim:** `Q17-CHILD-PAIR-v1`  
**Frozen protocol SHA-256:** `58f7520b9521e80620d2a232974b96fec3d4ac43bb7b5063d5f1f1dbc8228bb3`  
**Verdict:** **NOT SUPPORTED - no direct child-to-child Phase A/B architecture passed**

## Terminology correction - 26 July 2026

At the grouped parent rung, the correct ARA terms are **Phase A** and **Phase B**. **Anti-phase** is reserved for
the pure reversal exposed after decompression to the child-below rung. The frozen Q17 calculation is unchanged;
this note corrects only the explanatory language.

## Answer first

The same child pairing ranked first in development and holdout:

\[
\boxed{(C00,C11)+(C01,C10)}.
\]

It was therefore the **strongest available pairing**, but it did not behave like two clean Phase A/B diameters of
shared parent spheres. The children were highly distinguishable and radially balanced, yet neither selected pair
was sufficiently antipodal around the common ridge. The complete architecture also remained too close to the
runner-up and failed the frozen quality threshold.

The safest ARA reading is:

> The four Q16 children are not well described as two fixed direct child-to-child Phase A/B pairs. They remain
> better represented as four mixed child identities located by multiple parent/relation cuts.

This is compatible with Q16's non-planar four-child result. It does not overturn the Q16 two-parent/four-child
architecture.

## The important ARA distinction exposed by the failure

P3 is the same diagonal used by the Q16 Coupling ARA:

\[
\underbrace{(C00+C11)}_{\text{one Coupling-ARA pole group}}
\quad\longleftrightarrow\quad
\underbrace{(C01+C10)}_{\text{opposite Coupling-ARA pole group}}.
\]

Q17 asked a different, stricter question: whether `C00` and `C11` were themselves opposite Phase A/B children,
and likewise whether `C01` and `C10` were opposite children. They were not.

The result therefore distinguishes **children sharing a pole group** from **children occupying opposite poles**.
The strongest structure is group-to-group. The individual children remain corners/mixed identities within that
larger multi-axis geometry.

## Side-by-side interpretation

| Native ARA | Established mathematical/data view |
|---|---|
| A true Phase A/B pair should sit on opposite poles of one parent sphere. | Two child centroids should be antipodal around a shared centre. |
| The pair midpoint should return close to the parent `1.0` ridge. | The midpoint should be close to the four-child centroid. |
| Both poles should carry comparable radial shares of the parent TE-ARA. | The two radial norms should be similar. |
| The same diameter should survive later records. | The development contrast should align with the holdout contrast. |
| The strongest available pairing is P3. | P3 had the highest frozen quality score in both splits. |
| P3 is not a complete Phase A/B closure. | Its opposition, total quality and winning margin failed their gates. |

## Frozen construction

For split \(S\), the four child centroids were \(\mu_i^S\), their common centre was
\(M^S=\frac14\sum_i\mu_i^S\), and each child radial vector was \(r_i^S=\mu_i^S-M^S\).

For every candidate pair:

\[
\text{opposition}_{ij}=-\cos(r_i,r_j),
\]

\[
\text{balance}_{ij}=
\frac{2\min(\lVert r_i\rVert,\lVert r_j\rVert)}
{\lVert r_i\rVert+\lVert r_j\rVert},
\]

\[
\text{closure error}_{ij}=
\frac{\left\lVert(\mu_i+\mu_j)/2-M\right\rVert}{R}.
\]

The complete-pair quality score rewarded small closure error, strong opposition and strong radial balance. The
weaker pair controlled the architecture score. Selection used development records only.

## Architecture results

| Split | Rank | Architecture | Pairing | Quality \(Q\) | Minimum opposition | Minimum balance | Maximum closure error |
|---|---:|---|---|---:|---:|---:|---:|
| Development | 1 | P3 | `(C00,C11) + (C01,C10)` | `0.469955` | `0.413000` | `0.990954` | `0.489735` |
| Development | 2 | P2 | `(C00,C10) + (C01,C11)` | `0.385051` | `0.344403` | `0.900918` | `0.572775` |
| Development | 3 | P1 | `(C00,C01) + (C10,C11)` | `0.307403` | `0.124945` | `0.905767` | `0.657334` |
| Holdout | 1 | P3 | `(C00,C11) + (C01,C10)` | `0.403838` | `0.296184` | `0.944513` | `0.515785` |
| Holdout | 2 | P2 | `(C00,C10) + (C01,C11)` | `0.380759` | `0.391012` | `0.847161` | `0.547451` |
| Holdout | 3 | P1 | `(C00,C01) + (C10,C11)` | `0.280395` | `0.100282` | `0.845551` | `0.658987` |

P3 repeated, but its holdout advantage over P2 was only about `6.1%`, below the frozen `10%` margin gate.

## Selected-pair details

| Selected pair | Holdout opposition | Holdout balance | Diameter persistence | Frozen-diameter balanced accuracy | Held-out \(d'\) |
|---|---:|---:|---:|---:|---:|
| `C00-C11` | `0.572973` | `0.998351` | `0.891044` | `1.000000` | `10.538023` |
| `C01-C10` | `0.296184` | `0.944513` | `0.798919` | `0.962500` | `3.821973` |

The pair identities are easy to distinguish, and their radial sizes are well balanced. Distinguishability is not
the same as anti-phase coupling. Their directions do not approach the frozen antipodal requirement of `0.80`.

The second persistence value missed `0.80` by only `0.001081`, but that near miss does not control the verdict:
quality, opposition and winning-margin gates also failed materially.

## Frozen gates

| Gate | Result |
|---|---:|
| Same architecture wins development and holdout | **PASS** |
| Holdout quality \(Q\ge0.70\) | **FAIL** (`0.403838`) |
| Both holdout oppositions \(\ge0.80\) | **FAIL** (minimum `0.296184`) |
| Both radial balances \(\ge0.80\) | **PASS** |
| Both diameter persistences \(\ge0.80\) | **FAIL** (minimum `0.798919`) |
| Both holdout balanced accuracies \(\ge0.80\) | **PASS** |
| Holdout winner exceeds runner-up by at least 10% | **FAIL** |
| Randomized control rates within bounds | **PASS** (`0/9,999`; `0/1,000`) |

## The cut-removal result is especially informative

The full-sphere P3 winner survived removal of seven of the nine settings, including removal of `K8`. However:

- removing `K0` changed the winner to P1;
- removing `K4` changed the winner to P2;
- removing `K8` retained P3 and increased its holdout quality to `0.644226`, but it still failed the complete
  Phase-pair gates.

In ARA language, different cuts expose different parent groupings. No single division of the four children owns
the complete sphere strongly enough to become two fixed direct Phase A/B pairs. The full identity requires the
multi-direction relation.

In established mathematical language, the child centroids occupy a non-planar multi-axis configuration. Removing
one dominant contrast direction changes which two-pair projection looks strongest.

## What this does and does not establish

### Supported observations

- P3 is the most repeatable available two-pair projection.
- All four child identities are strongly distinguishable.
- The selected children have comparable radial magnitudes.
- Pair selection depends meaningfully on which sphere cut is retained.
- Randomized and within-archive pseudo-children did not pass the complete gates.

### Not supported

- two clean, fixed child-to-child Phase A/B pairs;
- a causal handover between child archives;
- time-ordered energy exchange;
- promotion of P3 into the unique physical parent architecture.

## Established comparison after the ARA verdict

Only after saving the ARA result were the public preparation names restored:

| ARA child | Public preparation |
|---|---|
| `C00` | \(\Psi^-\) |
| `C01` | \(\Psi^+\) |
| `C10` | \(\Phi^-\) |
| `C11` | \(\Phi^+\) |

The Q16 centroids already formed a stable rank-three tetrahedral relation. In that established comparison, the
four prepared identities are not expected to reduce to one privileged antipodal pairing in the complete
three-direction measurement space. Q17's failure of the direct-pair hypothesis is therefore scientifically
coherent rather than a broken test.

## Recommended next tests

1. **Group-pole test:** treat each parent pole as a two-child group rather than an individual child and test the
   three two-versus-two divisions directly.
2. **Perpendicular residual test:** remove one frozen parent diameter and test whether the remaining child
   geometry closes as a second ARA diameter plus Coupling ARA.
3. **Recursive child test:** promote one child to a parent only after raw internal substructure capable of
   defining two poles is identified.
4. **Synchronized movement test:** use interleaved preparations or simultaneous timestamps before testing
   directional handover or causal coupling.
5. **Independent replication:** repeat the unchanged Q17 protocol on a second raw four-child deposit.

The immediate next test should be the **group-pole test**. Q16 already recovered two parent directions as
two-versus-two child groupings, while Q17 now shows that forcing individual children into fixed antipodal pairs
is the wrong compression.

## Validation and reproduction

An independent implementation imported none of the primary test code and passed all `80/80` central checks.

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q17_child_phase_pair_test.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q17_child_phase_pair_validate.py'
```

Primary artifacts:

- `Q17_CHILD_PHASE_PAIR_RESULTS.json`
- `Q17_CHILD_PHASE_PAIR_METRICS.csv`
- `Q17_CHILD_PHASE_PAIR_ARCHITECTURES.csv`
- `Q17_CHILD_PHASE_PAIR_LEAVE_SETTING_OUT.csv`
- `Q17_CHILD_PHASE_PAIR_CONTROLS.csv`
- `Q17_CHILD_PHASE_PAIR_VALIDATION.json`
