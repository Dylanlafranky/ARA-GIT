# PN37 — Full Child ARA and Child-Level Phi Report

**Date:** 2026-07-23 (Australia/Brisbane)  
**Status:** validated post-hoc structural test on the already opened PN10B interval  
**Protocol:** `PN37_FULL_CHILD_ARA_PHI_PROTOCOL_v1_FROZEN.md`

## Answer first

Dylan's parent/child correction is borne out very clearly in this representation.

The complete population of `45,166` prime parents has pooled child ARA

\[
\bar A=1.0000472387,
\]

which is almost exactly the `1.0` ridge. But this does **not** mean the children are individually quiet or balanced. Opening every parent against every lower prime gate through its square root produced `286,253,917` child relations. Their mean absolute distance from the ridge is `0.4997970`, and their A readings span `0.00003164` to `1.99996835`.

Only `45,166` child readings equal `1.0` exactly: one per parent, all supplied by the parity gate `q=2`. Every one of the other `286,208,751` odd-gate child readings is asymmetric.

Plainly: the whole looks balanced because a huge population of below-ridge and above-ridge children nearly cancels. This is the same measurement-grain issue encountered in the LLM work and anticipated by PN10B, now shown using the complete lower factor-child field rather than nine selected children.

The child-level Phi proposal is **not supported by this test**. Phi is microscopically favorable against its within-gate nonzero-residue baseline, but the effect is essentially null and is not distinctive from matched rational landmarks.

## What was measured

For every prime parent `p` in

\[
[4{,}000{,}000{,}000,\;4{,}001{,}000{,}000),
\]

and every lower prime child gate `q <= sqrt(p)`, PN37 calculated

\[
\underbrace{A_q(p)}_{\substack{\text{distance since the previous}\\\text{child collision}}}
=2\frac{p\bmod q}{q},
\qquad
\underbrace{B_q(p)}_{\substack{\text{distance to the next}\\\text{child collision}}}
=2-A_q(p).
\]

Thus each decompressed child has exact TE-ARA closure:

\[
A_q(p)+B_q(p)=2.
\]

The full raw pair table would contain more than 286 million rows. Instead, the deterministic script streams it into a per-parent table and a per-gate table. Their child counts reconcile exactly, and any raw `(p,q)` relation can be regenerated from the formula.

## Complete child geometry

| Quantity | Result |
|---|---:|
| Prime parents | 45,166 |
| Lower prime gate identities | 6,338 |
| Complete `(parent, child gate)` relations | 286,253,917 |
| Pooled Phase A | 1.0000472387 |
| Pooled Phase B | 0.9999527613 |
| Mean child distance from ridge | 0.4997970299 |
| Minimum child A | 0.0000316401 |
| Maximum child A | 1.9999683529 |
| Below 1.0 | 143,096,936 (49.9895%) |
| Exactly 1.0 | 45,166 (0.01578%) |
| Above 1.0 | 143,111,815 (49.9947%) |

The below/above difference is only `14,879` readings across 286 million relations. That near mirror balance is why the pooled whole lands so close to `1.0`.

### ARA landmark regions

| Child ARA region | Count | Share |
|---|---:|---:|
| `0–0.25` left singularity well | 35,738,609 | 12.4849% |
| `0.25–(2-phi)` | 18,891,199 | 6.5995% |
| `(2-phi)–1.0` | 88,467,128 | 30.9051% |
| `1.0–phi` | 88,516,298 | 30.9223% |
| `phi–1.75` | 18,895,879 | 6.6011% |
| `1.75–2.0` right singularity well | 35,744,804 | 12.4871% |

The mirrored regions are extremely close in occupancy. This is broad population coverage of the 0–2 child coordinate, not a concentration at one special landmark.

## Parent cancellation after full decompression

Each parent contains either `6,337` or `6,338` complete child gates. The distribution of parent child-centroids is:

| Statistic | Parent child-centroid |
|---|---:|
| Minimum | 0.97199284 |
| 5th percentile | 0.98740402 |
| Median | 1.00027217 |
| Mean | 1.00004724 |
| 95th percentile | 1.01204970 |
| Maximum | 1.02568655 |

- `4,901` parents (`10.851%`) are within `0.001` of the ridge.
- `22,373` (`49.535%`) are within `0.005`.
- `36,973` (`81.860%`) are within `0.01`.

That tight parent distribution coexists with a child mean ridge-distance of almost `0.5`. The parent is near `1` because thousands of strong local asymmetries are coarse-grained together—not because the lower field is itself ridge-quiet.

This is a useful ARA measurement lesson, but the mechanism is also expected from established number theory: prime residues are approximately balanced across the allowed nonzero residue classes modulo each lower prime gate.

## Child-level Phi test

Every child ARA value is rational, so it cannot equal irrational Phi exactly. For each gate, PN37 selected the available nonzero residues nearest the mirror landmarks

\[
2-\phi\approx0.381966,
\qquad
\phi\approx1.618034,
\]

then compared their prime-child occupancy and continuous distance with the exact uniform distribution over that gate's nonzero residues. Gate `q=2` was excluded from this comparison because it forces `A=1` for every odd prime.

| Landmark pair | Occupancy lift vs gate baseline | Observed-minus-expected mean distance |
|---|---:|---:|
| **Phi** `(0.381966, 1.618034)` | **1.0000550** | **-0.00001190** |
| Quarter `(0.25, 1.75)` | 1.0000777 | -0.00003098 |
| Third `(1/3, 5/3)` | 1.0013901 | -0.00002010 |
| Half `(0.5, 1.5)` | 0.9994783 | +0.00000669 |
| Two-thirds `(2/3, 4/3)` | 0.9987472 | +0.00003381 |

Phi produced `220,224` nearest-residue hits versus `220,211.89` expected—roughly twelve extra hits among `286,208,751` primary child relations. Only `48.56%` of gates favored Phi on occupancy and `50.69%` favored it on continuous distance. The quarter landmark was more favorable on distance, and the third landmark was more favorable on occupancy.

Therefore the correct verdict is:

> Phi may still be a child-level landmark in some other identity or operator, but the complete factor-gate children of primes do not show a distinctive Phi preference. The tiny favorable deviation here is consistent with ordinary finite residue variation.

## Relation to earlier prime results

- **PN7B** measures the lateral parent environment: incoming versus outgoing adjacent-prime gaps. Its population mean is almost `1`, while only `2.1178%` of local nodes are exactly balanced.
- **PN10B** opened nine already-paid lower gates. It found a population mean near `1` but wide individual child asymmetry.
- **PN37** opens every lower gate through `sqrt(p)`. It confirms the cancellation diagnosis at much finer grain: the parent centroid becomes tightly ridge-like while essentially every odd-gate child remains asymmetric.
- **PN17** remains the relevant prediction caution. The complete child vector reconstructs the standard local factor-collision mask; compressing it without losing prime location remains unresolved.

These are related ARA views, but they are different axes: adjacent-gap geometry outside the prime, factor-child phase geometry inside the prime, and full survival/non-closure used to establish primality.

## Validation

The primary run passed `11/11` internal reconciliations. A separate validator then:

- regenerated all `45,166` source primes and `6,338` gate identities;
- reconciled both CSVs to `286,253,917` child relations;
- reconstructed eight parent summaries directly from their raw child vectors;
- reconstructed seven gate summaries directly from parent residues; and
- recomputed the primary Phi aggregate from the gate CSV.

All `6/6` independent checks passed. Maximum sampled parent reconstruction error was `2.66e-15`; maximum sampled gate error was `1.11e-16`.

## Reproduction files

- `pn37_full_child_ara_phi.py` — complete streamed calculation
- `validate_pn37_full_child_ara_phi.py` — independent source/sample validation
- `PN37_FULL_CHILD_ARA_PHI_RESULTS.json` — machine-readable findings
- `PN37_FULL_CHILD_ARA_PARENT_SUMMARIES.csv` — one row per prime parent
- `PN37_FULL_CHILD_ARA_GATE_SUMMARIES.csv` — one row per lower prime gate
- `PN37_FULL_CHILD_ARA_PHI_VALIDATION.json` — internal reconciliation
- `PN37_FULL_CHILD_ARA_PHI_INDEPENDENT_VALIDATION.json` — independent reconstruction

## Scientific status

**Ready to share with caveats as a post-hoc structural result.** The parent-cancellation statement is numerically strong and fully reproducible. It is not yet independent evidence for a universal fractal law because residue equidistribution already explains the balance. The child-level Phi claim fails this specific controlled comparison and should not be promoted from these data.
