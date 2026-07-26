# Q6 raw-tensor CHSH diagnostic

**Date:** 24 July 2026  
**Ledger:** `T264`  
**Status:** `SUPERSEDED — GEOMETRIC GATES 16/16, PHYSICAL CHSH INTERPRETATION INVALID`

## Outcome first

The frozen raw correlation-tensor ladder returned the predicted retained-axis sequence:

```text
Bell coherent:       3, 3, 3, 3
Classical controls:  1, 1
Uniform mixture:     0
```

All `16/16` registered geometric gates passed. However, the raw `Phi-minus` tensor gave
\(S_{\max}=2.88579\), above the quantum Tsirelson limit \(2\sqrt2=2.82843\). Therefore the unconstrained raw
tomography coefficients do not define a fully physical density matrix, and this pass cannot be reported as a
valid CHSH result.

## Raw result

| Entity | Status | \(s_1,s_2,s_3\) | \(S_{\max}\) | Axes \(\ge0.50\) |
|---|---|---|---:|---:|
| \(\Phi^+\) | physically prepared | `0.994, 0.946, 0.893` | `2.744` | 3 |
| \(\Phi^-\) | physically prepared | `1.078, 0.959, 0.853` | `2.886` | 3 |
| \(\Psi^+\) | physically prepared | `0.993, 0.957, 0.741` | `2.758` | 3 |
| \(\Psi^-\) | physically prepared | `0.959, 0.887, 0.817` | `2.613` | 3 |
| \(\Phi\)-classical | reconstructed | `0.952, 0.079, 0.020` | `1.911` | 1 |
| \(\Psi\)-classical | reconstructed | `0.927, 0.109, 0.024` | `1.866` | 1 |
| uniform mixed | reconstructed | `0.123, 0.048, 0.015` | `0.264` | 0 |

## Why this happened

The fifteen nontrivial Pauli projections were acquired in separate tomography settings. Finite sampling and
state-preparation-and-measurement error can make an unconstrained linear reconstruction non-positive. A singular
value above `1` and an apparent CHSH value above \(2\sqrt2\) expose that incompatibility.

The protocol should have contained a physical-density requirement before treating the Horodecki expression as a
CHSH value. Passing every frozen gate does not repair a missing necessary condition.

## Resolution

No gate or threshold was silently changed. A new remedial protocol, Q6B/T265, was frozen before applying any
physical projection. It uses a declared positive-semidefinite, unit-trace eigenvalue-simplex projection and
reruns the complete ladder.

Primary raw artifact: `Q6_CHSH_COHERENCE_LADDER_RESULTS.json`.  
Corrected report: `Q6B_PHYSICAL_CHSH_COHERENCE_REPORT_2026-07-24.md`.

