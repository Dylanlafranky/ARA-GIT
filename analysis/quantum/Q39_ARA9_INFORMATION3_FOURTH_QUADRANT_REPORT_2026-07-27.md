# Q39 ARA⁹ Information³ Fourth-Quadrant Reconstruction

**Date:** 27 July 2026  
**Ledger:** T294  
**Frozen verdict:** **INCONCLUSIVE — ELIGIBILITY**  
**Numerical result:** **strong ordered reconstruction of fourth-quadrant
magnitude and closure; the complete frozen support claim did not pass**

## Answer first

Q39 tested the geometry one tier below the Bell/preparation lens. The tested
identity was the complete connected ARA⁹ relation lattice

\[
\underbrace{C(t)}_{\substack{\text{connected ARA}^9\\\text{relation lattice}}}
=
\underbrace{T(t)}_{\text{whole pair relation}}
-
\underbrace{\mathbf a(t)\mathbf b(t)^{\mathsf T}}_{\text{separable local relation}}.
\]

Its own closure and direction of travel were used to identify four internal
meta-quadrants. The raw matrix from the fourth quadrant was hidden, and the
three earlier quadrant matrices were required to reconstruct it using the
frozen Information³ rule:

\[
\boxed{
\underbrace{\widehat C_4}_{\substack{\text{predicted fourth}\\\text{quadrant identity}}}
=
\underbrace{C_1}_{\text{first quadrant}}
-
\underbrace{C_2}_{\text{second quadrant}}
+
\underbrace{C_3}_{\text{third quadrant}}
}.
\]

On the previously untouched `pure_strongmax` archive, this fixed rule had
lineage-mean normalized error `0.3074`. Every named baseline was substantially
worse: `0.9361–2.4375`. The correct order also greatly outperformed the same
three matrices placed in the wrong order (`2.4375`). These advantages survived
seed-cluster bootstrap tests at the `20,000`-draw resolution.

That is meaningful evidence that the **ordered first three quadrant
identities retain substantial information about the fourth** in this
simulator family.

It is not a formal pass. Only `71` seeds were represented versus the frozen
minimum of `80`. The ARA rule also failed two numerical gates:

- persistence preserved matrix orientation better on the arithmetic mean;
- ARA was the single lowest-error method on `48.96%` of cycles, below the
  frozen `55%` requirement.

The honest status is therefore:

> **Prospective strong directional evidence for the lower-tier ordered
> Information³ reconstruction, but formally inconclusive and not yet a
> universal fourth-quadrant law.**

## Geometry and tier placement

Q39 preserves the tier correction made after Q38:

| Relative tier | Object |
|---|---|
| Upper calibration lens | complete two-qubit preparation / Bell crosswalk |
| Tested identity | connected \(3\times3\) ARA⁹ lattice \(C(t)\) |
| Internal geometry | four closure–flow quadrants of \(C(t)\) |
| Masked target | fourth quadrant's mean raw \(C(t)\) |

Bell states are therefore not relabelled as the four lower quadrants. They
remain an upper lens through which complete relation structures were
calibrated. Q39 moves **down a tier and across**, into the internal motion of
the connected lattice itself.

The two coordinates were built from the lattice's determinant closure:

\[
\underbrace{h(t)}_{\substack{\text{balanced three-axis}\\\text{closure cut}}}
=
\underbrace{|\det C(t)|^{1/3}}_{\text{geometric-mean singular scale}},
\]

\[
\underbrace{u(t)}_{\text{side of the local ridge}}
=
\frac{h(t)-m}{r},
\qquad
\underbrace{v(t)}_{\text{accumulation/release direction}}
=
\frac{h(t+1)-h(t)}{s}.
\]

The signs of \(u\) and \(v\) give four states:

\[
(\operatorname{sign}u,\operatorname{sign}v)
\in
\{(++),(-+),(--),(+-)\}.
\]

Plainly: one coordinate says whether the lattice is on the high-closure or
low-closure side of its local middle; the other says whether closure is
currently accumulating or releasing. Their mixing makes the four
meta-quadrants.

## Prospective design

The fidelity packet and protocol were frozen before the target values were
downloaded or inspected:

- [translation-fidelity packet](Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_FIDELITY_v1.md);
- [frozen protocol](Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_PROTOCOL_v1_FROZEN.md);
- protocol SHA-256:
  `db74e4f69c4a263d317b5b1ae53dfb042d94585e2f2eb8404048e5fcad3f7ccb`;
- fidelity SHA-256:
  `6ac71c0904a6295391261fca67cde7e7cc71d02a9d91f50c27d45f0b27a8d779`.

The untouched target was the public Zenodo archive
`unnati_submit_12_pure_strongmax.hdf5.zip`, deposited MD5
`11b5f14ba185a9901f6a85bd31497d71`. Development used slices `0..249`;
evaluation used slices `250..498`.

A qualifying cycle contained four consecutive, non-overlapping quadrant
visits in the circulation direction learned from development. Each visit
lasted at least two samples. The median visit lengths were `4, 3, 4, 3`
slices, respectively. All retained evaluation cycles followed the frozen
negative circulation direction.

The target matrix \(C_4\) was used only after prediction, for scoring.
Quadrant timing was observed from the scalar closure–flow cut, so this was a
masked-state reconstruction rather than a blind forecast of when the fourth
quadrant would begin.

## Population and eligibility

| Quantity | Result | Frozen floor |
|---|---:|---:|
| Complete cycles | `17,967` | `500` |
| Represented seed–pair lineages | `1,121` | `300` |
| Represented seeds | **`71`** | **`80`** |
| Eligible development lineages | `1,609` | — |
| Median cycles per represented lineage | `16` | — |
| Median development circulation coherence | `0.9106` | `0.80` per lineage |
| Median minimum-quadrant occupancy | `0.1606` | `0.05` per lineage |

The cycle and lineage floors passed comfortably, but the seed floor did not.
The formal verdict is therefore **INCONCLUSIVE — ELIGIBILITY**, irrespective
of the numerical pattern.

## Reconstruction result

### Error, direction and closure

| Predictor | Lineage-mean NRMSE ↓ | Lineage-median NRMSE ↓ | Lineage-mean cosine ↑ | Lineage-mean closure error ↓ |
|---|---:|---:|---:|---:|
| **ARA \(C_1-C_2+C_3\)** | **0.3074** | **0.2199** | 0.8763 | **0.2836** |
| Persistence \(C_3\) | 1.2444 | 0.7904 | **0.9958** | 1.6824 |
| No flip \(C_1\) | 0.9361 | 0.3989 | 0.6846 | 0.8889 |
| Linear \(2C_3-C_2\) | 1.7240 | 1.6190 | 0.7573 | 2.1319 |
| Three-state mean | 1.2416 | 1.0897 | 0.8464 | 1.5678 |
| Wrong order \(C_2-C_1+C_3\) | 2.4375 | 1.5811 | 0.6656 | 3.0323 |

ARA had lower NRMSE than the comparison method on:

| Comparison | Individual cycles won by ARA |
|---|---:|
| Persistence | `72.22%` |
| No flip | `77.27%` |
| Linear continuation | `87.14%` |
| Three-state mean | `94.92%` |
| Wrong order | `80.13%` |

Across all six methods simultaneously, ARA was best on `48.96%` of cycles.
That is by far the largest single-method share, but below the frozen `55%`
gate.

ARA error was at most:

- `0.10` on `34.20%` of cycles;
- `0.25` on `59.55%`;
- `0.50` on `84.59%`;
- `1.00` on `92.56%`.

### Seed-cluster inference

The lineage-mean NRMSE advantage of ARA was:

| Baseline | Baseline minus ARA | 95% seed-cluster bootstrap interval | \(p\), no ARA advantage |
|---|---:|---:|---:|
| Persistence | `+0.8641` | `[0.7388, 0.9854]` | `<0.00005` |
| No flip | `+0.6992` | `[0.5648, 0.8461]` | `<0.00005` |
| Linear | `+1.4337` | `[1.3297, 1.5334]` | `<0.00005` |
| Mean | `+0.9514` | `[0.8830, 1.0221]` | `<0.00005` |
| Wrong order | `+1.9542` | `[1.7017, 2.2074]` | `<0.00005` |

The reported probability is bounded by the `20,000`-draw bootstrap
resolution; it should not be read as literally zero.

### Why magnitude passed but mean direction did not

ARA's median cosine was `0.99967`, so a typical reconstruction pointed almost
exactly with the target. However, `1,302` cycles (`7.25%`) had negative ARA
cosine. This sign-failure tail pulled the arithmetic mean down to `0.8744`.
Persistence changed magnitude poorly but usually kept the immediately
preceding orientation, giving mean cosine `0.9958`.

The NRMSE distribution also contained one extreme value, `260.43`, caused by
normalization against a nearly zero target norm. Its `99.9`th percentile was
only `1.218`. The preregistered arithmetic means are retained, but the
medians and full distribution are essential for understanding this tail.

Plainly: the ordered ARA rule usually reconstructed both the target's size
and direction very closely. In a minority of cycles it chose the wrong
orientation badly. Persistence rarely made that sign mistake, but it usually
missed how much the lattice had changed.

### Post-result Q39A orientation audit

The frozen Q39 result above is unchanged. A subsequent opened-data audit
tested whether the `1,302` negative-cosine cycles marked the deepest Q36
determinant pinch. They did not. Reversed cycles had a shallower median
minimum (`u=-0.9199`) than same-orientation cycles (`u=-0.9987`), and
`1,293/1,302` occurred in the high-closure, accumulating \(Q_{++}\) target
quadrant.

A target-blind post-result flag,

\[
\cos(C_1-C_2+C_3,C_3)<0,
\]

identified `1,293` of the `1,302` reversed cycles with `49` false positives.
Conditionally reversing only the relation term,

\[
\widehat C_4=
\begin{cases}
C_3-C_1+C_2,&\cos(C_1-C_2+C_3,C_3)<0,\\
C_1-C_2+C_3,&\text{otherwise},
\end{cases}
\]

reduced lineage-mean NRMSE from `0.3074` to `0.2508`, raised cosine from
`0.8763` to `0.9905`, and improved all `1,342` changed cycles. Because the
condition was discovered after Q39 was open, this is a Q40-ready
**return-flow / relation-orientation hypothesis**, not a Q39 rescue or proof
of physical seam parity. Full audit:
[Q39A post-result orientation and seam audit](Q39A_POST_RESULT_SEAM_PARITY_AUDIT_2026-07-27.md).

## Frozen gates

| Gate | Result |
|---|---|
| Eligibility | **FAIL — 71/80 seeds** |
| Lower lineage-mean NRMSE than every baseline | PASS |
| Seed-cluster \(p<0.05\) against every baseline | PASS |
| Higher lineage-mean cosine than every baseline | **FAIL** |
| Lowest NRMSE on at least `55%` of cycles | **FAIL — 48.96%** |
| Wrong-order control worse | PASS |

Because eligibility failed, the registered outcome cannot be promoted even
if all numerical gates had passed. Independently, two numerical gates also
failed.

## Independent quantum crosschecks

ARA reconstruction fidelity was defined as negative NRMSE and compared with
two quantities calculated directly from the target density matrices:

| Crosscheck | Spearman \(\rho\) | Direction |
|---|---:|---|
| Two-qubit purity \(\operatorname{Tr}(\rho^2)\) | `-0.1926` | registered normalized-fidelity association; denominator-confounded |
| Computational-basis \(l_1\) coherence | `+0.1725` | higher basis coherence associated with better reconstruction |

Median NRMSE was `0.0702` in the lowest purity quartile and `0.2337` in the
highest. It was `0.2324` in the lowest \(l_1\)-coherence quartile and `0.0698`
in the highest.

These are weak-to-modest secondary associations over a large sample, not
causal results. Computational-basis \(l_1\) coherence is basis-dependent.

The post-result Q39A audit found that the purity interpretation cannot be
retained as originally worded. Target relation norm fell strongly as purity
rose (Spearman \(\rho=-0.8330\)). Absolute matrix error also fell
(\(\rho=-0.5135\)), even while normalized error rose
(\(\rho=+0.1926\)). After controlling the ranks for target norm, the
NRMSE–purity association shrank to `+0.0853`. Thus “higher purity means worse
reconstruction” was mostly a small-denominator effect; in absolute matrix
distance, the higher-purity targets were reconstructed more closely. See the
[Q39A audit](Q39A_POST_RESULT_SEAM_PARITY_AUDIT_2026-07-27.md).

## What is established mathematics and what Q39 adds

The operator

\[
C_4=C_1-C_2+C_3
\]

is ordinary affine/parallelogram completion. Q39 does not discover that
algebraic identity.

The empirical question was whether ARA's independently declared tier,
quadrant order and connected-lattice representation place that known
operator somewhere useful. On an untouched simulator archive, the placement
did recover the masked fourth lattice state substantially better in
normalized magnitude than persistence, no-flip, linear, averaging and
wrong-order controls.

The wrong-order failure matters. The result is not explained merely by
having access to the same three matrices: their ordered relation carries
information.

## Validation

Independent validation passed:

- archive and frozen-file checksums;
- `4,000` raw density-matrix reconstructions;
- maximum connected-matrix cache error \(2.87\times10^{-8}\);
- maximum closure-cache error \(2.34\times10^{-8}\);
- `17,967/17,967` cycle-count agreement;
- zero quadrant-order or interval failures;
- `254` deterministic metric spot checks with zero numerical discrepancy.

The sampled maximum trace error was \(2.41\times10^{-5}\), Hermiticity error
was zero and the minimum sampled eigenvalue was
\(-5.98\times10^{-7}\), consistent with source/numerical tolerance.

- [machine-readable results](Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_RESULTS.json)
- [independent validation](Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_VALIDATION.json)
- [compressed cycle table](Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_CYCLES.csv.gz)
- [diagnostic figure](Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_GEOMETRY.png)
- [reproduction script](q39_ara9_information3_fourth_quadrant_test.py)
- [validation script](q39_validate_information3_fourth_quadrant.py)

## Interpretation and next discriminating tests

The strongest ARA interpretation presently justified is:

> Inside the connected ARA⁹ lattice, three ordered closure–flow quadrant
> identities carry a strong but imperfect reconstruction of the fourth. The
> relation is primarily powerful for the target's amount and determinant
> closure. A minority orientation-failure mode remains unresolved.

This does not yet establish:

- four unique hidden physical children;
- a literal singularity traversal;
- a new quantum state;
- blind prediction of quadrant timing;
- a universal Information³ law across quantum systems.

The clean next sequence is:

1. freeze the same operator on another untouched archive with an eligibility
   rule the archive can actually satisfy;
2. add a development-fitted affine or autoregressive baseline, fixed before
   evaluation, to distinguish ARA's exact coefficient pattern from generic
   smooth trajectory structure;
3. predict quadrant entry timing rather than receiving boundaries from the
   observed closure–flow cut;
4. freeze the Q39A target-blind return-flow rule
   \(\cos(C_1-C_2+C_3,C_3)<0\) and its conditional relation reversal on an
   untouched archive rather than repairing Q39 post hoc;
5. use pairwise dominance against each named baseline as Q40's primary
   comparison while retaining the stricter six-way single-best share as a
   diagnostic. Q39's frozen `55%` gate remains failed and unchanged.

Q39 is therefore a substantial bridge result, but it remains a bridge to the
next test rather than the final fourth-quadrant claim.
