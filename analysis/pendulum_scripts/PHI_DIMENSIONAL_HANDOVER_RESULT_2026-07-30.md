# Phi dimensional handover — frozen pendulum result

**Date:** 30 July 2026  
**Protocol:** `PHI_DIMENSIONAL_HANDOVER_PROTOCOL_2026-07-30.md`  
**Data:** public dynamicslab *MultiArm-Pendulum*, Zenodo `10.5281/zenodo.6633719`  
**Frozen evaluation:** free-swing run 3  
**Verdict:** **NOT SUPPORTED — 1 of 4 registered check families passed**

## Question

Does one Phi operation appear simultaneously as:

1. a child turn near the parent's local ARA diameter landmarks
   \(0.381966/1.618034\);
2. a parent-cycle location near \(0.381966/0.618034\);
3. improved preservation of the parent's following excursion?

Runs 1–2 were development reports, run 3 supplied the frozen verdict, and the driven triple run was transfer
only. The test used raw angles and extrema; no Fourier, Hilbert, SVD/POD, normal-mode model or pendulum
equation entered the endpoints.

## Frozen run-3 result

There were `212` eligible nested child→parent events:

- arm 3 → arm 2: `124`;
- arm 2 → arm 1: `88`.

### 1. Landmark specificity — failed

Diameter median nearest-landmark distance:

| landmark | distance |
|---|---:|
| Phi \(0.382/1.618\) | **0.3192** |
| quarters \(0.5/1.5\) | 0.3951 |
| thirds \(0.667/1.333\) | 0.5444 |
| ridge \(1.0\) | 0.8777 |

Phi was the best of the **registered non-pole diameter alternatives**.

Circular median nearest-landmark distance:

| landmark | distance in turns |
|---|---:|
| turn/opposition \(0/0.5\) | **0.0725** |
| Phi \(0.382/0.618\) | 0.1153 |
| thirds \(0.333/0.667\) | 0.1564 |
| quarters \(0.25/0.75\) | 0.1775 |

The circular half therefore preferred ordinary parent turn/opposition locations, not Phi. The registered
two-cut specificity gate failed.

### 2. Dimensional locking — passed, narrowly interpreted

Diameter-Phi proximity and circular-Phi proximity co-moved:

| pair | Spearman \(r\) | p |
|---|---:|---:|
| arm 3 → arm 2 | +0.191 | 0.033 |
| arm 2 → arm 1 | +0.494 | \(1.0\times10^{-6}\) |
| weighted pooled | **+0.325** | — |

This is the only registered family that passed. Because both coordinates are constructed from the same
monotonic parent half-cycle, positive association alone is not evidence of a physical Phi operator. The event-time
control below is decisive.

### 3. Parent identity retention — failed in the opposite direction

Median next-excursion retention:

- bottom quartile of joint Phi proximity: `0.97881`;
- top quartile: `0.96765`;
- top minus bottom: **−0.01116**.

Phi-near events preserved the next parent excursion slightly **less**, not more.

### 4. Event-time controls — failed

`2,000` circular event-time shifts per pair preserved the parent trajectories and event counts.

| endpoint | observed | shifted median | one-sided p |
|---|---:|---:|---:|
| joint Phi proximity | 0.56215 | 0.57637 | 0.8806 |
| retention advantage | −0.01116 | +0.00068 | 0.9760 |

Actual child turns were no closer to the proposed joint Phi handover than shifted event times. Both primary
effects pointed away from the prediction.

## Development and transfer pattern

The negative result was not an isolated run-3 accident:

| run | joint proximity p | retention difference | retention p |
|---|---:|---:|---:|
| free run 1 | 0.8386 | −0.0042 | 0.6922 |
| free run 2 | 0.7346 | −0.0197 | 0.9825 |
| **free run 3** | **0.8806** | **−0.0112** | **0.9760** |
| driven transfer | 0.9375 | −0.0853 | 0.9950 |

All four records rejected a positive Phi-proximity advantage under this instrument.

## Post-verdict pole-control audit

The protocol should also have registered the local diameter poles `{0,2}`. This omission cannot change the
already negative frozen verdict, but it matters for interpreting Phi's apparent diameter win.

Independent row-level validation found median distance to the diameter poles:

| run | poles \(0/2\) | Phi \(0.382/1.618\) |
|---|---:|---:|
| free run 1 | **0.1092** | 0.2944 |
| free run 2 | 0.3402 | **0.2954** |
| free run 3 | **0.1223** | 0.3192 |
| driven transfer | **0.0025** | 0.3795 |

On the frozen evaluation and driven transfer, the child turns sit much closer to the parent's local poles.
Phi looked best only because the registered diameter controls did not include the most relevant ARA alternative.

## Plain ARA reading

This test located the **turn/pole handover**, not a Phi handover. When a child reaches an extremum, the adjacent
parent is commonly near its own turn or opposition geometry. That is ordinary nested phase/anti-phase locking.

The result does **not** show that Phi is absent from the pendulum or from ARA. It rejects the specific statement:

> “The raw child extrema are jointly located at the parent's Phi diameter and Phi circular positions, and this
> location improves next-excursion identity retention.”

If Phi is the diagonal path that prevents repeated occupation, it may live in the **travel between successive
turn/pole handovers**, rather than at the extremum itself. That would be a new endpoint and must be frozen as a
separate test; it cannot repair this result.

## Validation

`validate_phi_dimensional_handover.py` independently re-read all `814` saved event rows and reproduced `20/20`
headline counts and medians with zero failures. It also supplied the post-verdict pole control.

## Reproduction

From `analysis/pendulum_scripts`:

```powershell
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe phi_dimensional_handover_test.py
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe validate_phi_dimensional_handover.py
```

Outputs:

- `phi_dimensional_handover_results.json`;
- `phi_dimensional_handover_events.csv`.
