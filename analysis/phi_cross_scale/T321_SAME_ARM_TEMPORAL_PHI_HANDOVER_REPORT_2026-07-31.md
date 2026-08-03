# T321 — same-arm routed A–B–A diagnostic

**Date:** 31 July 2026  
**Frozen primary verdict:** **NOT SUPPORTED — 1/5 gates**  
**Independent validation:** **PASS — 15/15 checks**  
**Evidence tier:** retrospective raw-data identity-boundary correction, not a
blind discovery test

**Later scope correction:** Dylan subsequently clarified that the proposed
golden-section object is `A(parent)/A(child)`, where lowercase `b` is a
smaller occurrence of the same Phase-A type. It contains no Phase-B
measurement vertex. T321's frozen result remains valid for the routed
`A -> B -> A` object below, but it is **not a verdict on that later-clarified
cross-scale golden-section claim**. See T322.

## Answer first

The corrected pendulum test held the physical identity fixed. It followed one
arm's complete Phase-A half-swing, the intervening Phase-B half-swing, and
that same arm's next complete Phase-A half-swing:

\[
A_{j,k}\rightarrow B_{j,k}\rightarrow A_{j,k+1}.
\]

On the frozen angle-plus-time trajectory coordinate, the direct-route ARA
reading was

\[
\boxed{q_{\rm median}=1.965901}.
\]

The closest predeclared landmark was `2`, not Phi. This held independently
for all three arms, for both reversible phase directions, and in the driven
transfer record. The routed same-arm `A -> B -> A` operationalization is
therefore **not supported as Phi-shaped**. It does not test the subsequently
clarified direct `A(parent)/A(child)` scale relation.

The negative result is informative rather than empty. The two route legs
were strongly balanced (median equal-leg ratio `0.97530`), but the complete
trajectory triangle was nearly straight (descriptive median included angle
`158.73°`). A balanced regular-pentagon cut would instead require a much more
bent `108°` route. In this pendulum cut, Phase B lies close to the direct
temporal passage between the two Phase-A swings.

![T321 corrected same-arm temporal handover](F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/phi_cross_scale/T321_SAME_ARM_TEMPORAL_PHI_HANDOVER.png)

## Frozen results

| Reading | Events | Median q | Closest frozen landmark |
|---|---:|---:|---|
| Free run 3, primary angle + time | 275 | **1.965901** | **2** |
| Increasing half-swings | 138 | 1.965853 | 2 |
| Decreasing half-swings | 137 | 1.965901 | 2 |
| Arm 1 | 82 | 1.971364 | 2 |
| Arm 2 | 87 | 1.982767 | 2 |
| Arm 3 | 106 | 1.946774 | 2 |
| Driven transfer, primary | 260 | 1.982114 | 2 |

Primary landmark errors:

| Landmark | Median absolute error |
|---|---:|
| `1` | 0.965901 |
| `sqrt(2)` | 0.551688 |
| `1.5` | 0.465901 |
| Phi | 0.347867 |
| `sqrt(3)` | 0.233851 |
| **`2`** | **0.034099** |

The primary median direct distance was `2.01055` ARA trajectory units. The
two median route legs were `1.01884` and `1.01881`; the median full route was
`2.02860`. Consequently the direct path and the route through B were nearly
the same length.

## Frozen gates

| Gate | Result |
|---|:---:|
| Phi is the unique pooled primary winner | fail |
| Both reversible phase directions choose Phi | fail |
| At least two arms choose Phi | fail |
| Median q lies within 0.08 of Phi | fail |
| Real B pairing beats all shifted-B controls on Phi error | **pass** |

Verdict: **NOT SUPPORTED — 1/5**.

## The useful surviving relation

Keeping the true intervening B swing produced a Phi error of `0.34787`. The
three time-recentred but identity-mispaired B controls produced `0.36290`,
`0.35580`, and `0.35896`. The difference is small, but it is consistently in
the declared direction: the real B swing carries information about the
same-arm A-to-A traversal.

That supports the presence of a physical A–B–A coupling relation. It does
**not** make the relation Phi-shaped.

## Coordinate sensitivity

The frozen primary includes the time extrusion because the proposed object
is a circle/wave carried through time and because a complete cycle was
declared to occupy `2` ARA units. Two sensitivity coordinates show why the
physical claim must remain tied to a declared coordinate:

| Coordinate | Evaluation median q | Winner |
|---|---:|---|
| angle + time (frozen primary) | 1.965901 | 2 |
| angle only | 0.077437 | 1 |
| angle + velocity + time | 1.199601 | 1 |

None selected Phi. The exact value is coordinate-dependent, but the negative
Phi verdict is not rescued by either sensitivity reading.

The primary's proximity to `2` is also partly understandable from its frozen
construction: the temporal distance from A to the next A is approximately
the sum of the two consecutive half-cycle temporal distances. The angle
component was free to bend the route away from `2`; empirically it did so
only slightly. This makes the result a faithful rejection of this particular
time-extruded pentagon interpretation, not a universal proof that every
possible same-phase metric must equal `2`.

## Method

- Runs 1–2 supplied only per-arm complete-cycle durations and robust velocity
  scales.
- Public free run 3 was the primary evaluation record.
- Data were read at `500 Hz`; no Fourier, Hilbert, SVD/POD, pendulum equation,
  or fitted normal mode was used.
- Genuine turns used the previously audited prominence and separation rules.
- Every half-swing was resampled to `129` traversal positions.
- The primary path used rest-centred angle on the ARA diameter plus time
  normalized so a complete A–B–A cycle occupies `2` units.
- The route coordinate was

\[
q=\frac{2d(A_k,A_{k+1})}
{d(A_k,B_k)+d(B_k,A_{k+1})}.
\]

## Scientific boundary and next step

T321 corrects T320/T320A's cross-arm identity error while retaining a
Phase-B route vertex. It does not erase
the exact T319 regular-pentagon mathematics or the Fibonacci scale-lineage
calibration; those are different claims. It means this public pendulum does
not provide a Phi result for this routed `A -> B -> A` measurement. It does
not reject the later-clarified same-phase parent/child equation.

T322 performs the next correction by directly comparing parent and child
same-phase recurrence gaps. Its frozen local-matching result is also negative,
while its post-hoc scale audit exposes a state-dependent Phi-like subfamily.
See `T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_REPORT_2026-07-31.md`.

## Reproduction

From `analysis/phi_cross_scale`:

```powershell
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe t321_same_arm_temporal_phi_handover.py
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe validate_t321_same_arm_temporal_phi_handover.py
```

Primary artifacts:

- `T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_PROTOCOL_v1_FROZEN.md`
- `t321_same_arm_temporal_phi_handover.py`
- `T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_RESULTS.json`
- `T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_EVENTS.csv`
- `T321_SAME_ARM_TEMPORAL_PHI_HANDOVER.png`
- `T321_SAME_ARM_TEMPORAL_PHI_HANDOVER.svg`
- `validate_t321_same_arm_temporal_phi_handover.py`
- `T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_VALIDATION.json`
