# Phi-ordered recurrence and resonance death — frozen result

**Date:** 30 July 2026  
**Frozen verdict:** **NOT SUPPORTED (`0/5`)**  
**Instrument verdict:** the raw four-child timing is dominated by a
quarter-turn recurrence, not a Phi-ordered walk. The resonance-death
comparison is underpowered and remains unresolved.

> **Interpretation correction after Dylan's review:** this instrument tested
> whether Phi was the local four-child gap or the per-parent-cycle advance of
> that local pattern. Dylan's intended possibility was different: the
> quarter-turn pattern may be the fast internal rotation while its immediate
> orbit remains another locally closed cycle. The complete locally coupled
> identity is simultaneously transported through a still-larger frame—for
> example, the Sun carries the planetary system through the Galaxy. Phi may
> belong to the relation between local closure and that common-mode carrier,
> not to either the quarter-turn or immediate orbit. The frozen `0/5` result
> remains valid for the tested local-step translation. It does **not** test or
> reject that rotation–orbit–carrier hypothesis.

## Plain-language answer

The clarified ARA claim was reasonable to test:

> Four children can keep a parent moving by remaining unequally ordered
> inside the fixed TE-ARA budget. Phi may provide a non-closing handover,
> avoiding terminal resonance death.

That is not what these free-swing double-pendulum runs showed **on the local
timing axis that Codex froze**. The four child states repeatedly occupied
four roughly quarter-cycle locations. From one parent cycle to the next, the
whole child pattern returned almost to the same sampled local phase instead
of advancing by `0.381966` of that cycle. Being more Phi-like on that local
axis did not preserve the next parent excursion; the measured association
was negative.

This rejects the tested placement of Phi in the **raw ordered recurrence of
these four sign-defined children**. It does not reject every possible Phi
handover elsewhere in ARA and, specifically, does not reject a slower parent
carrier underneath or around the quarter-turn sequence. It also does not
establish or refute resonance death, because the matched comparison contained
only one near-repeat and one non-closing event.

## Frozen ARA representation

The two centred raw arm angles supplied two A/B cuts. Their four coupled
children were:

| Child | Raw cut |
|---|---|
| `AA` | both angles on their A side |
| `AB` | first A, second B |
| `BB` | both on their B side |
| `BA` | first B, second A |

Within every eligible top-arm parent cycle:

- the four occupancy shares were normalized so
  `TE-ARA = 2(pAA+pAB+pBB+pBA) = 2`;
- the circular timing centroid of every child was measured;
- the four gaps between those centroids were compared with frozen orbit
  templates;
- the common child-pattern movement into the next parent cycle was measured;
  and
- next-cycle parent-amplitude retention was scored while holding occupancy
  inequality, diagonal share and amplitude rung roughly constant.

No Fourier transform, Hilbert transform, SVD, fitted equation of motion or
pendulum simulation was used.

## Public endpoints

Source: the
[dynamicslab MultiArm-Pendulum repository](https://github.com/dynamicslab/MultiArm-Pendulum),
double-pendulum free-swing runs 1–4. Run 1 was a historical/development
reference. Runs 2–3 were frozen replication endpoints. Run 4 was retained as
the final confirmation endpoint.

All four source hashes matched the values frozen before inspection.

| Endpoint | Eligible cycles | Scored transitions |
|---|---:|---:|
| Run 1, reference | 35 | 34 |
| Run 2, frozen | 47 | 46 |
| Run 3, frozen | 40 | 39 |
| Run 4, confirmation | 36 | 35 |
| Runs 2–3 pooled | 87 | 85 |

## Primary results

### 1. The child timing gaps preferred quarters

On frozen runs 2–3, median distance from the candidate gap template was:

| Candidate | Median distance; lower is better |
|---|---:|
| Quarter, `0.25` | **0.010101** |
| `3-e` | 0.093111 |
| `3/8` | 0.124088 |
| Phi, `phi^-2` | 0.128993 |
| `2/5` | 0.147273 |
| `sqrt(2)-1` | 0.161486 |
| Third | 0.244768 |
| `pi-3` | 0.319980 |

The close rational control `3/8` beat Phi, while ordinary quarters beat both
by a large margin. Run 4 independently repeated the quarter result:
`0.003179` for quarters versus `0.130377` for Phi.

**ARA reading:** the four children form a clean quadrant-like order within
the measured parent cycle. That is useful recurrence structure, but it is not
a Phi allocation **on this local axis**. The result may instead supply the
fast internal rotation whose slower carrier still needs to be measured.

### 2. The pattern returned almost to itself

The pooled median common movement from one parent cycle to the next was:

`0.001836` of a full circular cycle.

Run 4 was even closer to recurrence:

`0.000229`.

The frozen translation required movement near `0.381966`. The observed
ordered pattern therefore behaved like a parent-locked recurrence on this
sampled axis, not a non-closing Phi step. `pi-3` was merely the nearest
**non-zero** candidate; the actual winner was the separately declared
near-zero recurrence state.

This is compatible with a larger common-mode carrier being absent or aliased
out: sampling only relative motion inside a fixed local parent can repeatedly
observe the same rotational phase while discarding transport of the complete
locally coupled identity through the next-higher frame.

### 3. Phi-likeness did not preserve the next parent cycle

After matching cycles by TE-ARA allocation inequality, diagonal share and
amplitude rung, the frozen runs gave:

`Spearman rho = -0.291521`, one-sided permutation `p = 0.9110`.

The direction is opposite to the proposal. The result is not evidence that
Phi harms every pendulum identity; it says this frozen Phi-order score did
not predict improved retention.

### 4. Resonance death was not adequately sampled

The registered comparison defined:

- near-repeat: circular movement `<0.05`;
- non-closing: movement from `0.10` to `0.45`.

After the frozen matching, only one event remained in each group. Their
retention difference pointed opposite to the proposal (`-0.336868`,
permutation `p=1.0`), but `n=1+1` is not a credible estimate of a general
resonance-death effect.

The correct status is **underpowered / unresolved**, not “resonance death
disproved.”

## Frozen checks

| Check | Result |
|---|---|
| Phi has the best pooled four-gap template | Fail — quarter won |
| Phi has the best pooled intercycle movement | Fail — near-zero recurrence won |
| Phi-specific score positively predicts retention | Fail — direction was negative |
| Non-closing events retain better than near-repeats | Fail / underpowered |
| Run 4 confirms the Phi pattern | Fail — quarter plus near-zero repeated |

**Total: `0/5`; NOT SUPPORTED.**

## What was learned

1. TE-ARA fixes the total budget but not its allocation; exact closure to `2`
   remains definitional in this normalization.
2. The four-child representation exposes a stable quadrant sequence that a
   one-child cut cannot show.
3. This sequence is parent-locked: it almost reappears at the same circular
   location on the next cycle.
4. A maintained asymmetry can coexist with local recurrence. Therefore “not
   equal shares” is not by itself evidence of a Phi non-locking handover.
5. Local rotation, immediate orbit and common-mode carrier drift require
   separate ARA coordinates. This test measured the first and sampled the
   second; the fixed pendulum pivot did not supply the third.
6. Testing resonance death requires a system or perturbation that actually
   supplies many transitions between near-repeat and non-closing regimes.

## Reproduction

Run:

```powershell
& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\pendulum_scripts\phi_ordered_recurrence_test.py'

& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\pendulum_scripts\validate_phi_ordered_recurrence.py'
```

The raw runs 2–4 are intentionally stored outside Git under
`F:\SystemFormulaFolder\external_data\MultiArm-Pendulum\DoublePendulum`.
Their expected hashes and download provenance are frozen in the protocol and
test script.

Files:

- `PHI_ORDERED_RECURRENCE_PROTOCOL_2026-07-30.md`
- `phi_ordered_recurrence_test.py`
- `phi_ordered_recurrence_results.json`
- `phi_ordered_recurrence_cycles.csv`
- `validate_phi_ordered_recurrence.py`
