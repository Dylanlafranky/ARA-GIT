# Q38 Fixed-Anchor Phase-Cycle Test

**Date:** 27 July 2026  
**Ledger:** T293  
**Frozen verdict:** **INCONCLUSIVE — ELIGIBILITY**  
**Numerical result:** **the registered Phase-A → Phase-B → Phase-A cycle
did not pass; a sharp low-amplitude anti-turn remains descriptively visible**

## Question

Q37 compared seven approach slices with seven exit slices using a different
reference tensor at each distance from the pinch. Dylan noticed that the
offset sequence

`-0.569, -0.284, -0.137, -0.107, -0.111, -0.110, +0.245`

could instead represent entry into a complete Phase-B region, travel around
its rounded boundary and emergence into Phase A.

Q38 removed the moving-reference ambiguity. For every independently selected
pinch event, it fixed one Phase-A tensor on the approach side and compared
every exit slice with that same anchor. A complete operational cycle required:

1. a reliable anti-oriented Phase-B entry within seven slices;
2. a later reliable Phase-A return within fourteen slices;
3. event and lineage majorities;
4. separation from displaced-time, pair and network controls.

- [Translation-fidelity packet](Q38_FIXED_ANCHOR_PHASE_CYCLE_FIDELITY_v1.md)
- [Frozen protocol](Q38_FIXED_ANCHOR_PHASE_CYCLE_PROTOCOL_v1_FROZEN.md)
- [Machine-readable results](Q38_FIXED_ANCHOR_PHASE_CYCLE_RESULTS.json)
- [Independent validation](Q38_FIXED_ANCHOR_PHASE_CYCLE_VALIDATION.json)
- [Figure](Q38_FIXED_ANCHOR_PHASE_CYCLE_GEOMETRY.png)
- [Event table](Q38_FIXED_ANCHOR_PHASE_CYCLE_EVENTS.csv.gz)
- [Post-verdict Q37 replay](Q38_Q37_LANDMAX_DESCRIPTIVE_REPLAY.json)

## ARA and tensor coordinates

For each event at time \(t\), the fixed Phase-A anchor was the
highest-amplitude approach tensor among offsets `-7..-3`:

\[
\underbrace{C_A}_{\substack{\text{fixed approach}\\\text{Phase-A anchor}}}
=
\underset{k\in\{-7,\ldots,-3\}}{\operatorname{argmax}}
\underbrace{\lVert C_{t+k}\rVert_F}_{\text{relation amplitude}}.
\]

Each exit slice \(j=1,\ldots,14\) was then given two coordinates:

\[
\underbrace{r_j}_{\substack{\text{orientation relative}\\\text{to the fixed anchor}}}
=
\frac{\langle C_A,C_{t+j}\rangle_F}
{\lVert C_A\rVert_F\lVert C_{t+j}\rVert_F},
\qquad
\underbrace{a_j}_{\substack{\text{amplitude relative}\\\text{to the fixed anchor}}}
=
\frac{\lVert C_{t+j}\rVert_F}{\lVert C_A\rVert_F}.
\]

`r = +1` means the same tensor orientation, `r = -1` means the opposite
orientation, and `r = 0` means orthogonal or mixed. Direction was declared
reliable only when \(a_j\ge0.10\). The registered Phase-B entry required
\(r_j\le-0.25\); strong entry required \(r_j\le-0.50\). Phase-A return
required \(r_j\ge+0.25\) and \(a_j\ge0.50\).

The continuous cycle score was

\[
\underbrace{Q}_{\substack{\text{weakest completed}\\\text{cycle component}}}
=
\min\!\left(
\underbrace{-r_B}_{\text{anti-oriented entry strength}},
\underbrace{r_A^+}_{\text{return strength}}
\right).
\]

If either entry or return was absent, the frozen score was \(Q=-1\).

These are operational ARA-facing coordinates of reconstructed tensors. They
do not, by themselves, identify a physical hidden state or literal
topological sphere.

## Untouched target and eligibility

- Public archive: Zenodo `10.5281/zenodo.16753415`
- File: `unnati_submit_12_pure_mimic.hdf5.zip`
- Deposited and locally verified MD5:
  `04477abdac1849dd034576c0dbb685cb`
- HDF5 shape: `2 × 100 × 500 × 66`
- Primary branch: `c2`
- Network control: `c4`
- Complete `c2` lineages: `696`
- Represented lineages: `688`
- Registered events: `10,458`
- Represented seeds: `32`

The frozen floors were `2,000` events, `500` lineages and `80` seeds.
Events and lineages passed; seeds did not. The registered verdict is
therefore **INCONCLUSIVE — ELIGIBILITY** regardless of the numerical gates.

## Registered result

| Variant | Complete cycles | Strong Phase-B entries | Mean \(Q\) | Lineages with ≥50% cycles |
|---|---:|---:|---:|---:|
| Exact pinch | **41.72%** | **41.95%** | **-0.1670** | **41.13%** |
| Time control | 41.55% | 41.67% | -0.1728 | 41.28% |
| Pair control | 40.35% | 40.40% | -0.1951 | 40.41% |
| Network control | 20.72% | 54.24% | -0.5753 | 1.89% |

The exact event was almost indistinguishable from the displaced-time and
pair controls. Its cycle fraction exceeded the time control by only `0.17`
percentage points and the pair control by `1.37` points, far below the
frozen `10`-point margin.

The network control entered an anti-oriented state frequently but usually
did not complete the required return. That result is useful because it shows
why both halves of the ordered cycle were necessary: anti-orientation alone
does not identify the proposed complete traversal.

All eight frozen numerical gates failed:

| Frozen gate | Result |
|---|---|
| Event cycle fraction ≥ `55%` | `41.72%` — FAIL |
| Lineage-majority fraction ≥ `55%` | `41.13%` — FAIL |
| Bootstrap probability cycle fraction > `50%` ≥ `.99` | `0.0000` — FAIL |
| Median \(Q\) ≥ `.25` | `-0.9771` — FAIL |
| Cycle margin ≥ `.10` over every control | FAIL |
| Score margin ≥ `.10` over every control | FAIL |
| Cycle bootstrap ≥ `.95` against every control | minimum `.5297` — FAIL |
| Score bootstrap ≥ `.95` against every control | minimum `.6308` — FAIL |

Thus eligibility is not hiding an otherwise successful registered result.
Even if the target had supplied `80` seeds, the frozen cycle claim would not
have passed.

## The local shape that remains

The fixed-anchor median orientation and amplitude paths begin:

| Exit slice | Median orientation \(r_j\) | Median amplitude \(a_j\) |
|---:|---:|---:|
| `+1` | **-0.9693** | **0.0922** |
| `+2` | +0.9563 | 0.2541 |
| `+3` | +0.9861 | 0.4670 |
| `+4` | +0.9938 | 0.6507 |
| `+5` | +0.9977 | 0.7754 |
| `+6` | +0.9996 | 0.8183 |
| `+7` | +0.9999 | 0.9243 |
| `+8` | +1.0000 | 1.0000 |

This exposes an important measurement distinction:

- immediately after the pinch, the median tensor points almost exactly
  opposite the approach anchor;
- at that same slice, its median magnitude is only `9.22%` of the anchor,
  below the frozen `10%` direction-reliability floor;
- the relation then rebuilds in magnitude while its median orientation has
  already returned to the Phase-A side.

Only `47.08%` of exact events had reliable amplitude at `+1`. Within that
reliable subset, `87.39%` were strongly anti-oriented. This is a strong
descriptive **pinch-timed anti-turn**, but it is not a majority complete
Phase-B cycle and was not a registered secondary endpoint.

Among completed events, the first reliable positive return with at least
half-amplitude occurred at median offset `+9`. The time and pair controls
returned at approximately the same offsets (`+10` and `+9`), so this timing
does not distinguish the exact pinch.

The most faithful present interpretation is:

> The measured identity nearly collapses in amplitude, briefly reverses
> orientation, and then reconstructs. Q38 does not show that it remains in a
> stable Phase-B basin for seven slices.

In ARA language, the remaining lead is a possible distinction between a
fast orientation flip and slower identity-amplitude reformation. That is a
post-result thread for a new test, not a passed Q38 claim.

### Post-result quadrant-double-flip alternative

After Q38 was open, Dylan proposed a more specific alternative:

\[
2\rightarrow0\;\big|\;0\rightarrow2,
\qquad
AB\rightarrow BA.
\]

If the parent relation has two labelled child directions
\(C\approx\sigma uv^{\mathsf T}\), one child flipping gives
\(-uv^{\mathsf T}\), while both children flipping gives
\((-u)(-v)^{\mathsf T}=uv^{\mathsf T}\). The observed parent can therefore
follow `+ → - → +` while the underlying children have completed an ordered
double reversal. This is consistent with the immediate weak anti-turn but
cannot be identified from the parent tensor because
\(uv^{\mathsf T}=(-u)(-v)^{\mathsf T}\).

Tier correction: \(u,v\) refer to hypothetical internal children of the
ARA⁹ connected lattice \(C=T-\mathbf a\mathbf b^{\mathsf T}\), not
automatically to Q24's upper local qubit vectors \(\mathbf a,\mathbf b\).
Bell preparations were the earlier calibration lens for a complete \(C\);
Q38 is examining the trajectory and singularity of \(C\) itself—down a tier
and across its own chart.

The underlying two-reversal parity rule predates Q38 in the ARA axiomatic and
the Maxwell MX6 two-child sign result. The new element is the proposed
perpendicular, time-resolved application at this quantum pinch. It is
recorded without changing the frozen verdict in:
[Q38 Post-Result Quadrant Double-Flip Hypothesis](Q38_POST_RESULT_QUADRANT_DOUBLE_FLIP_HYPOTHESIS_2026-07-27.md).

## Mandatory post-verdict replay of Q37

The frozen protocol required the same fixed-anchor method to be replayed on
Q37's `pure_landmax` archive only after the untouched Q38 verdict had been
sealed. This replay cannot rescue or change Q38.

The fixed-anchor Q37 medians were:

| Exit slice | `+1` | `+2` | `+3` | `+4` |
|---:|---:|---:|---:|---:|
| Median orientation | **-0.9742** | **-0.8460** | **+0.9833** | +0.9919 |

The apparent `-0.107, -0.111, -0.110` plateau disappeared. With one fixed
anchor, the path is anti-oriented for two median slices and has returned
strongly positive by the third.

The Q37 replay also failed to distinguish the exact pinch:

| Variant | Complete-cycle fraction |
|---|---:|
| Exact pinch | 43.84% |
| Time control | 44.06% |
| Pair control | 43.47% |
| Network control | 40.16% |

Therefore the earlier plateau was produced by the moving paired-reference
measurement: both sides of the pinch were changing as the seven pairs moved
outward. It was valid as Q37's local paired geometry, but it was not evidence
that one fixed Phase-A identity observed a complete seven-slice Phase-B
boundary.

## Plain-language result

Dylan's suspicion found a real feature, but not the full proposed feature.

The relation does appear to turn sharply to its opposite immediately after
the pinch. However, that opposite-pointing state is extremely weak in
magnitude, and most events do not complete the frozen reliable
Phase-A → Phase-B → Phase-A cycle. Similar cycle frequencies also occur at
control locations.

So the seven slices did not take us all the way around a stable Phase-B
sphere. A better description is:

> **At the pinch, the old relation almost disappears. Its faint remainder
> points the opposite way, then the relation rebuilds on the original side.**

That is compatible with a handover or reconstruction picture inside this
simulator, but it is not yet evidence for a universal ARA singularity flip.

## Scientific boundary

The source is a deterministic simulator containing two-qubit reduced density
matrices, not quantum-hardware measurements. The analysis reconstructs raw
connected relation tensors without Ramsey or Hahn filtering, but the tensors
remain outputs of the simulator and the operational coordinate definitions.

Q38 does not prove:

- a physical hidden Phase B;
- traversal through a topological sphere;
- a universal singularity;
- conservation through an unmeasured channel;
- a new law of quantum mechanics.

It does identify a reproducible analysis target: the relation between
amplitude collapse, instantaneous anti-orientation and subsequent
reconstruction.

## Reproduction and validation

Primary run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q38_fixed_anchor_phase_cycle_test.py'
```

Independent validation:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q38_validate_fixed_anchor_phase_cycle.py'
```

Post-verdict Q37 replay:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q38_replay_landmax_descriptive.py'
```

Independent validation passed all audit families:

- archive MD5, frozen-document hashes and exact file sizes;
- cache shapes;
- eligibility counts and the complete `10,458`-event list;
- `4,224` sampled raw-metric checks across all four variants, with maximum
  absolute error \(1.42\times10^{-14}\);
- every summary and seed-cluster bootstrap;
- every frozen gate and the eligibility verdict.

The validator initially contained an approximate archive byte count copied
from the download display. It was corrected to the already verified exact
size (`224,548,658` bytes); no event, coordinate, gate or interpretation was
changed.

## Result classification

| Claim | Classification |
|---|---|
| Q38 registered full fixed-anchor cycle | **Not supported numerically** |
| Formal registered verdict | **Inconclusive — eligibility (`32/80` seeds)** |
| Immediate low-amplitude anti-turn | **Strong descriptive signal** |
| Seven-slice stable Phase-B traversal | **Not supported** |
| Q37 `-0.11` plateau as a fixed-anchor sphere edge | **Not supported** |
| Amplitude-collapse → anti-turn → reconstruction thread | **Open; requires a new frozen test** |
| Perpendicular ordered child double flip | **Post-result hypothesis; parent-only data are non-identifying** |
