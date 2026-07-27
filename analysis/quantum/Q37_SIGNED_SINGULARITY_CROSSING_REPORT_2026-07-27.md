# Q37 Signed Singularity-Crossing and Traversal Test

**Date:** 27 July 2026  
**Ledger:** T292  
**Frozen verdict:** **INCONCLUSIVE — ELIGIBILITY**  
**Descriptive result:** **the traversal asymmetry repeated on the untouched
archive; stable whole-window anti-orientation did not**

## Question

After Q36 found a narrow determinant pinch followed by re-expansion, Dylan
identified the pinch as the ARA singularity crossing. Two consequences were
frozen before the new target archive was downloaded or opened:

1. the relation should emerge on the far side in an anti-oriented state;
2. the crossing itself should be accumulation-heavy, placing equal
   approach/exit windows near `0.94–0.95`, slightly below the `1.0` ridge.

The test used the untouched `pure_landmax` archive rather than the archive
used to discover the Q36 pattern.

- [Fidelity packet](Q37_SIGNED_SINGULARITY_CROSSING_FIDELITY_v1.md)
- [Frozen protocol](Q37_SIGNED_SINGULARITY_CROSSING_PROTOCOL_v1_FROZEN.md)
- [Machine-readable results](Q37_SIGNED_SINGULARITY_CROSSING_RESULTS.json)
- [Independent validation](Q37_SIGNED_SINGULARITY_CROSSING_VALIDATION.json)
- [Figure](Q37_SIGNED_SINGULARITY_CROSSING_GEOMETRY.png)
- [Event table](Q37_SIGNED_SINGULARITY_CROSSING_EVENTS.csv.gz)

## ARA and tensor coordinates

For each fixed pair lineage, the raw connected \(3\times3\) relation tensor
was \(C_t\). Its total relation magnitude and balanced three-axis closure were

\[
\underbrace{A_t}_{\substack{\text{total measured}\\\text{relation magnitude}}}
=
\underbrace{\lVert C_t\rVert_F}_{\text{Frobenius norm}},
\qquad
\underbrace{h_t}_{\substack{\text{balanced}\\\text{three-axis closure}}}
=
\underbrace{|\det C_t|^{1/3}}_{\text{geometric-mean singular scale}}.
\]

At each independently selected determinant trough \(t\), seven approach
slices were paired with the corresponding seven exit slices:

\[
\underbrace{S_t}_{\substack{\text{signed relation across}\\\text{the proposed seam}}}
=
\frac{
\sum_{k=1}^{7}
\langle C_{t-k},C_{t+k}\rangle_F
}{
\sum_{k=1}^{7}
\lVert C_{t-k}\rVert_F\lVert C_{t+k}\rVert_F
}.
\]

Here `-1` means opposite tensor orientation, `0` means orthogonal or mixed,
and `+1` means the same orientation. This is an operational ARA-facing
orientation test; it is not automatically a measurement of universal
Phase B.

The traversal coordinates were

\[
\underbrace{X_A}_{\substack{\text{total-relation}\\\text{traversal ARA}}}
=
\frac{2\sum_{k=1}^{7}A_{t+k}}
{\sum_{k=1}^{7}A_{t-k}+\sum_{k=1}^{7}A_{t+k}},
\]

\[
\underbrace{X_h}_{\substack{\text{balanced-closure}\\\text{traversal ARA}}}
=
\frac{2\sum_{k=1}^{7}h_{t+k}}
{\sum_{k=1}^{7}h_{t-k}+\sum_{k=1}^{7}h_{t+k}}.
\]

`1.0` is the equal approach/exit ridge. Values below `1.0` mean the
approach/accumulation window is heavier; values above `1.0` mean the
exit/release window is heavier.

## Source and eligibility

- Public archive: Zenodo `10.5281/zenodo.16753415`
- File: `unnati_submit_12_pure_landmax.hdf5.zip`
- Deposited and locally verified MD5:
  `ace64ede12cfbc9e5413326f23c306ad`
- Primary branch: `c2`
- Network control: `c4`
- Complete-loop `c2` lineages: `1,920`
- Represented lineages: `1,915`
- Registered determinant-trough events: `39,567`
- Represented seeds: `71`

The frozen floors required at least `2,000` events, `500` lineages and `80`
seeds. The event and lineage floors passed, but the seed floor did not.
Therefore the registered result must remain **inconclusive**, regardless of
the numerical gate pattern below.

## Result

### Signed orientation

| Variant | Mean \(S\) | Median \(S\) | Negative events |
|---|---:|---:|---:|
| Exact crossing | **-0.1035** | **-0.8749** | **56.18%** |
| Time control | -0.0265 | -0.2699 | 51.68% |
| Pair control | +0.3938 | +0.9881 | 30.26% |
| Network control | +0.2644 | +0.4494 | 35.03% |

The exact crossing was more anti-oriented than every control under
seed-cluster bootstrap resampling (`1.000` for all three comparisons), and
the probability that its seed-weighted signed mean was below zero was
`0.993`.

It nevertheless failed two frozen requirements:

- only `56.18%` of events were negative, below the required `60%`;
- the exact mean was only `0.0770` more negative than the time control, below
  the required `0.10` margin.

The very negative median alongside the modest mean identifies a polarized
distribution: a slight majority of events are strongly anti-oriented, while
a substantial minority return with strong same-orientation relation.

Distance from the seam also matters. Mean paired similarity was `-0.5695` at
the first slice, remained mildly negative through slice six, and became
`+0.2450` by slice seven. The observed geometry is therefore a strong local
anti-turn immediately around the pinch, followed by reorientation—not a
stable seven-slice whole-window inversion.

Determinant-sign parity did not flip. A negative Frobenius relation can occur
without all three tensor axes becoming \(-C\); Q37 therefore does not justify
calling the result a complete three-axis Phase-B inversion.

### Traversal asymmetry

| Variant | Mean \(X_A\) | Mean \(X_h\) | Events below \(1\), \(A/h\) |
|---|---:|---:|---:|
| Exact crossing | **0.9560** | **0.9487** | **57.61% / 57.58%** |
| Time control | 1.0637 | 1.0715 | 27.37% / 26.46% |
| Pair control | 0.9828 | 0.9805 | 51.82% / 51.75% |
| Network control | 0.9998 | 1.0004 | 49.86% / 49.69% |

Across lineages, `60.37%` were below the amplitude ridge and `59.74%` were
below the closure ridge. Seed-cluster bootstrap probability was `1.000` for
being below `1.0` and `1.000` against every control for both measures.

All twelve frozen traversal gates passed numerically:

- both means were inside `[0.92,0.98]`;
- both event majorities exceeded `55%`;
- both lineage majorities exceeded `55%`;
- both seed bootstraps exceeded `0.99`;
- both means beat every control by at least `0.02`;
- all six controlled bootstrap comparisons exceeded `0.95`.

The closure coordinate `0.9487` lands directly inside the prior
`0.94–0.95` interval. The amplitude coordinate `0.9560` is slightly above
that narrow descriptive estimate but inside the preregistered acceptance
band. This independently repeats the Q36 post-result values (`0.952` for
amplitude and `0.938` for closure) in the predicted direction on an untouched
archive from the same public source family.

## Plain-language result

The cleanest picture is:

> The measured relation narrows almost to a pinch. Immediately across that
> pinch, many events point strongly the other way, but not enough events stay
> that way for the registered full Phase-B test to pass. What does repeat very
> cleanly is the unequal crossing: the exit side carries about `95%` of the
> equal-window share expected at a perfectly balanced `1.0` crossing.

In ARA language, this is good evidence for a locally asymmetric handover
geometry in this simulator. It is also evidence for a short-range
anti-orientation at the seam. It is not yet evidence that a complete,
persistent Phase-B sphere has been measured on the far side.

The archive supplied many events and lineages, but those events came from
only `71` qualifying seeds. Because the test demanded `80`, the honest
registered verdict is not “replicated”; it is:

> **Inconclusive by eligibility, with a complete descriptive replication of
> the traversal-asymmetry signature and a mixed anti-orientation result.**

## Frozen gate verdict

| Gate family | Numerical result | Registered status |
|---|---|---|
| Eligibility | `71/80` seeds; other floors pass | **FAIL** |
| Signed median \(\le-0.25\) | `-0.8749` | PASS |
| Signed negative fraction \(\ge60\%\) | `56.18%` | FAIL |
| Signed seed bootstrap below zero | `0.993` | PASS |
| Signed mean beats every control by `0.10` | time margin `0.0770` | FAIL |
| Signed controlled bootstraps | all `1.000` | PASS |
| Traversal amplitude gates | `6/6` | PASS numerically |
| Traversal closure gates | `6/6` | PASS numerically |

**Frozen claim verdict:** `INCONCLUSIVE — ELIGIBILITY`.

Had the frozen seed floor been met, the registered numerical rules would
have returned `TRAVERSAL ASYMMETRY ONLY`.

## Scientific boundary

The source is a deterministic two-qubit-reduction simulator, not quantum
hardware. The archive was untouched within the project, but it belongs to
the same public source family as earlier ARA quantum work. Selecting
determinant troughs deliberately locates low-closure points; the independent
evidence is the signed relation across those points, the unequal-window
coordinates and their separation from time, pair and network controls.

The test does not observe a literal spacetime singularity, hidden state,
energy flow in joules or topologically closed sphere. It recovers a
controlled tensor pinch, local anti-orientation and asymmetric
re-expansion. Mapping those operational features to universal ARA Phase B
requires further eligible archives or hardware data.

## Implementation correction

The first generated summary correctly calculated all event coordinates but
the seed bootstrap for \(X_A<1\) and \(X_h<1\) accidentally compared the
coordinates with `0` rather than the frozen `1.0` ridge. This was detected
before interpretation. The bootstrap null was corrected to `1.0`; the
archive, events, coordinates, controls and frozen protocol were unchanged.
The independent validator reproduced the corrected bootstraps.

## Reproduction and validation

Primary run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q37_signed_singularity_crossing_test.py'
```

Independent validation:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q37_validate_signed_singularity_crossing.py'
```

Independent validation passed all nine audit families:

- archive MD5, frozen-document hashes and exact source sizes;
- cache shapes;
- all `1,920` complete-loop eligibility decisions;
- the complete ordered list of `39,567` events;
- `1,056` sampled raw tensor calculations across all four variants, with
  maximum absolute error \(2.22\times10^{-16}\);
- every exported summary;
- every seed-cluster bootstrap;
- every frozen gate;
- the final eligibility verdict.

