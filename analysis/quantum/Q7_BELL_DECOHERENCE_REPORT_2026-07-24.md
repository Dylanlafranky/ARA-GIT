# Q7 physical Bell-decoherence trajectory

**Date:** 24 July 2026  
**Ledger:** `T266`  
**Primary verdict:** **SUPPORTED - 8/8 frozen gates**  
**Hahn intervention replication:** **SUPPORTED - 4/4 gates**  
**Independent validation:** **PASSED - 28/28 checks**

## Answer first

The public two-qubit experiment shows the exact directional distinction the ARA crosswalk predicted.

All four physically prepared Bell states began with three strong correlation-tensor axes. During free Ramsey
evolution, each became a one-strong-axis remnant at `16.02-20.02 us`. The physical Horodecki CHSH value crossed
from above `2` to at most `2` at `20.02-24.02 us`.

At the final Ramsey sample (`40.02 us`):

- the dominant axis retained a median **93.36%** of its initial strength;
- the second axis retained only **9.01%**;
- the preferential-retention gap was **84.35 percentage points**.

The field did not collapse isotropically from `3 -> 0`. It collapsed directionally from `3 -> 1`.

Hahn echo delayed the same transition. Every state still had three strong axes at `125.89 us` and first became a
one-axis state at `251.19 us`, where the physical CHSH crossing also occurred. The geometric-mean crossing delay
was **11.45x** relative to Ramsey.

## The mathematics and the ARA reading

From the physically reconstructed state, form the standard two-qubit correlation tensor

\[
\underbrace{T_{ij}}_{\substack{\text{physics: Pauli}\\\text{relation cut}}}
=
\underbrace{\langle\sigma_i\otimes\sigma_j\rangle}_{\substack{\text{ARA: one directional}\\\text{cut through the parent}}},
\qquad i,j\in\{X,Y,Z\}.
\]

Its descending singular values are

\[
\underbrace{s_1\ge s_2\ge s_3}_{\substack{\text{physics: independent}\\\text{correlation strengths}}}.
\]

Using the Q6B threshold \(s_i\ge0.50\), the ARA parent initially has three strong relational cuts. Directional
dephasing removes the two phase-sensitive cuts much faster than the persistent cut:

\[
\underbrace{(s_1,s_2,s_3)}_{\text{coherent parent: 3 cuts}}
\longrightarrow
\underbrace{(s_1,0,0)}_{\text{directional remnant: 1 cut}}.
\]

The independent Bell discriminator is the established Horodecki result

\[
\underbrace{S_{\max}}_{\text{maximum CHSH signal}}
=
2\sqrt{
\underbrace{s_1^2}_{\text{first retained relation}}
+
\underbrace{s_2^2}_{\text{second retained relation}}
}.
\]

Plainly: Bell violation requires at least two sufficiently strong relation directions. The experiment loses its
Bell violation after the second direction contracts, even though one strong parent relation remains.

## Per-state results

| State | Ramsey first 1-axis | Ramsey \(S_{\max}\le2\) | Final \(s_1\) retention | Final \(s_2\) retention | Hahn last 3-axis | Hahn first 1-axis / crossing |
|---|---:|---:|---:|---:|---:|---:|
| Phi-plus | `16.02 us` | `20.02 us` | `96.60%` | `8.93%` | `125.89 us` | `251.19 us` |
| Phi-minus | `16.02 us` | `24.02 us` | `97.20%` | `2.77%` | `125.89 us` | `251.19 us` |
| Psi-plus | `20.02 us` | `24.02 us` | `86.59%` | `9.49%` | `125.89 us` | `251.19 us` |
| Psi-minus | `20.02 us` | `20.02 us` | `90.11%` | `9.09%` | `125.89 us` | `251.19 us` |

## Frozen-gate result

All primary gates passed:

- all `88` reconstructed states were trace-one, positive-semidefinite, Hermitian and Tsirelson-bounded;
- all four Ramsey states began with three strong axes;
- all four crossed the CHSH boundary inside the measured interval;
- all four showed a one-axis state after their last three-axis observation;
- the dominant axis was retained while the second contracted;
- no CHSH failure preceded the last three-axis sample.

All four echo gates also passed, including the frozen minimum fourfold crossing delay.

Independent recomputation from the source files passed `28/28` checks.

## What this adds to ARA

Q5/Q6B showed a static ladder:

\[
\text{coherent Bell parent}=3,\qquad
\text{classical relation}=1,\qquad
\text{uniform mixture}=0.
\]

Q7 adds a real temporal path through that geometry:

\[
\boxed{\text{prepared coherent parent }3
\ \xrightarrow{\text{directional dephasing}}\
\text{one-axis remnant }1.}
\]

The Hahn pulse then changes how quickly the path is traversed without changing the state labels or the measurement
definition. This is materially stronger evidence for the usefulness of the ARA relational-axis description than
another static reconstruction, because the proposed geometry survives both time evolution and a physical
intervention.

## Boundaries

This remains established dephasing, Bell/Pauli tomography and Horodecki physics expressed through ARA's
parent/child and directional-cut language. The paper already disclosed the coarse Ramsey and Hahn lifetimes, so
this is not a blind discovery of decoherence or dynamical decoupling.

The result does **not** establish ARA superiority, derive quantum mechanics, prove that all systems are fractal, or
show that every decoherence mechanism must follow `3 -> 1`. Isotropic depolarization may instead drive `3 -> 0`.

## Reproduction

Run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q7_bell_decoherence_test.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q7_bell_decoherence_validate.py'
```

Inputs are checksum-pinned in
`analysis/quantum/Q7_BELL_DECOHERENCE_DATA_QUALITY_AUDIT_2026-07-24.md`.

