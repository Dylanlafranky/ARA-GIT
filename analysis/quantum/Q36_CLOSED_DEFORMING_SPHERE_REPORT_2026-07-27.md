# Q36 Closed-Deforming Sphere Test

**Date:** 27 July 2026  
**Ledger:** T291  
**Status:** **MIXED / INCONCLUSIVE — the registered closed-deforming signature
did not pass**

## Question

Dylan proposed that the Q35 relation need not fully unravel at the
lattice-facing determinant boundary. It could remain a complete but irregular
identity: a "wibbly-wobbly" sphere, analogous to gas or plasma remaining
inside a spherical container even though its internal lattice has dissolved.

Q36 translated that picture into a deliberately stricter tensor consequence:

1. balanced three-axis determinant closure should fall;
2. most of the total connected-relation magnitude should remain;
3. normalized shape motion should increase;
4. the determinant should subsequently reclose.

The method and gates were frozen before calculating these outcomes.

- [Fidelity packet](Q36_CLOSED_DEFORMING_SPHERE_FIDELITY_v1.md)
- [Frozen protocol](Q36_CLOSED_DEFORMING_SPHERE_PROTOCOL_v1_FROZEN.md)
- [Machine-readable results](Q36_CLOSED_DEFORMING_SPHERE_RESULTS.json)
- [Independent validation](Q36_CLOSED_DEFORMING_SPHERE_VALIDATION.json)
- [Figure](Q36_CLOSED_DEFORMING_SPHERE_GEOMETRY.png)

## ARA and tensor coordinates

For each fixed Q35-complete `c2` relation lineage, the raw \(3\times3\)
connected tensor was \(C_t\).

\[
\underbrace{A_t}_{\substack{\text{total measured}\\\text{relation magnitude}}}
=
\underbrace{\lVert C_t\rVert_F}_{\text{Frobenius norm}}
\]

\[
\underbrace{h_t}_{\substack{\text{balanced}\\\text{three-axis closure}}}
=
\underbrace{|\det C_t|^{1/3}}_{\text{geometric mean singular scale}}
\]

\[
\underbrace{L_t}_{\substack{\text{lattice-facing}\\\text{shape share}}}
=
\frac{3h_t^2}{A_t^2},
\qquad
\underbrace{D_t}_{\substack{\text{deforming/mobile}\\\text{shape share}}}
=1-L_t.
\]

The TE-ARA display used \(x_L=2L\) and \(x_D=2D\), so
\(x_L+x_D=2\) exactly. That equality is bookkeeping, not evidence.

Normalized shape motion was measured independently:

\[
\underbrace{W_t}_{\substack{\text{change in normalized}\\\text{relation shape}}}
=
\left\|
\frac{C_{t+1}C_{t+1}^{\mathsf T}}{\lVert C_{t+1}\rVert_F^2}
-
\frac{C_{t-1}C_{t-1}^{\mathsf T}}{\lVert C_{t-1}\rVert_F^2}
\right\|_F.
\]

## Data and eligibility

- Public archive: Zenodo `10.5281/zenodo.16753415`
- Primary branch: `c2`
- Network control: `c4`
- Q35-complete `c2` lineages: `2,495`
- Represented lineages: `2,486`
- Represented seeds: `87`
- Registered evaluation trough events: `51,037`
- Controls: displaced time, next eligible pair, and matched `c4` network

All frozen eligibility floors passed.

## Result

| Registered quantity | Exact trough | Time control | Pair control | Network control |
|---|---:|---:|---:|---:|
| Median total-amplitude retention | **0.0561** | 0.7005 | 0.2806 | 1.0156 |
| Events retaining at least half amplitude | **0.063%** | 58.53% | 42.55% | 74.35% |
| Median determinant-closure retention | **0.0362** | 0.6252 | 0.2076 | 1.0078 |
| Median selective gap \(r_A-r_h\) | **0.0172** | 0.0135 | 0.0008 | -0.0147 |
| Median deforming share \(D\) | **0.9098** | 0.8280 | 0.8538 | 0.8642 |
| Median effective rank | **2.0004** | 2.0030 | 2.0018 | 2.0015 |
| Median shape-wobble ratio | **0.1573** | 0.7258 | 0.3800 | 1.0113 |
| Median seven-slice reclosure ratio | **1.7151** | 1.7060 | 2.0941 | 2.3503 |
| Reclosed to at least 0.75 | **100%** | 99.76% | 99.78% | 94.39% |

The exact trough had the greatest deforming share, with seed-cluster bootstrap
probability `1.000` against every control. That isolated result is real but
insufficient: the whole measured tensor magnitude fell at almost the same
time, and normalized shape motion was lower rather than higher.

The decisive failures were:

- median amplitude retention was `0.0561`, far below the frozen `0.75` gate;
- only `0.063%` of events retained even half their local amplitude, far below
  the frozen `80%` gate;
- the selective difference between amplitude and determinant retention was
  only `0.0172`, not the required `>0.25`;
- shape wobble was `0.1573` of its local level and failed every registered
  control comparison.

Reclosure passed strongly, but it also occurred strongly in the controls.

## Plain-language result

At the exact determinant trough, this measured relation does **not** look like
a still-full ball whose interior merely becomes loose and wobbly. It looks
more like the measured relation pinches almost shut: balanced closure falls to
about `3.6%` of its nearby level and total relation magnitude falls to about
`5.6%`. The small remainder is strongly non-lattice-shaped, but it is small;
it is not most of the previous sphere preserved in a fluid form.

The relation then expands again. Every registered event reached at least
`75%` of its local determinant level within seven slices, with a median peak
of `1.715` times the local baseline. Therefore Q36 also does not support a
simple permanent-disappearance account.

The most faithful ARA description of this result is presently:

> **A narrow compression or handover seam is visible in the measured tensor,
> followed by re-expansion. Q36 does not show that a full deforming sphere
> remains observable at the exact seam, and the sampled tensor cannot tell us
> whether identity continuity persists through an unmeasured channel.**

That is compatible with a singularity-like pinch as a future hypothesis, but
it is not proof of one. The registered "closed but wobbly at the boundary"
signature itself did not pass.

## Frozen gate verdict

| Gate | Result |
|---|---|
| Eligibility | PASS |
| Median amplitude retention \(\ge0.75\) | FAIL |
| At least 80% retain half amplitude | FAIL |
| Selective gap \(>0.25\) with bootstrap support | FAIL |
| Deforming share exceeds all controls | PASS |
| Wobble \(>1\) and exceeds all controls | FAIL |
| Seven-slice reclosure | PASS |

**Frozen claim verdict:** `MIXED/INCONCLUSIVE CLOSED-DEFORMING SIGNATURE`.

The predeclared relation-loss alternative also did not pass because the small
positive selective gap and rapid reclosure do not describe simple permanent
loss.

## Scientific boundary

This test concerns a connected \(3\times3\) tensor inside one deterministic
greedy network simulator. It does not observe a literal material boundary,
topological sphere, plasma, hidden quantum state or energy conservation.
Tensor magnitude is relation magnitude, not joules. Selecting determinant
troughs necessarily selects weak balanced closure, so the independent evidence
had to come from retained total magnitude, increased wobble and controlled
reclosure; the first two did not appear.

The present time sampling may also skip a continuous but extremely narrow
path through the seam. Distinguishing a true zero from an unresolved pinch
would require finer sampling of the underlying state or an independently
measured channel that remains finite through the boundary.

## Reproduction and validation

Primary run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q36_closed_deforming_sphere_test.py'
```

Independent validation:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q36_validate_closed_deforming_sphere.py'
```

Validation passed every check:

- all four frozen source hashes;
- exact reconstruction of `2,495` eligible lineages;
- exact reconstruction of `51,037` saved events;
- exact event lists for `24` deterministic lineage samples;
- raw \(3\times3\) matrix reconstruction for `24` event samples, with maximum
  absolute discrepancies around \(10^{-7}\);
- exact reconstruction of reported variant medians.

