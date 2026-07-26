# Q5 public four-Bell-state ARA protocol v1 — FROZEN

**Protocol ID:** `Q5-BELL-FOUR-STATE-v1`  
**Ledger ID:** `T263`  
**Frozen:** 24 July 2026, 11:55 AEST, before downloading or opening the three additional archives  
**Source audit:** `Q5_BELL_FOUR_STATE_DATASET_AUDIT_2026-07-24.md`  
**Fidelity:** `Q5_BELL_FOUR_STATE_FIDELITY_v1.md`  
**Status:** FROZEN

## Primary question

Does the Q4 ARA parent/child pattern replicate across all four prepared Bell identities, and do the three
same-axis parent cuts distinguish them while the local child cuts remain ridge-like?

## Eligible sources

Use only the four checksum-locked Figshare archives listed in the source audit. `UPUP-DOWNDOWN.zip` is the
previously opened Q4 state; the other three are untouched replications.

The author scripts may be inspected after freeze only to recover acquisition-orientation timestamps and confirm
the common binary schema. Source-supplied density matrices, fidelities, plotted projections and Bell verdicts
are forbidden as outcomes or predictors.

## Frozen decoder

Use the Q4 decoder without outcome-dependent adjustment:

- unsigned little-endian 16-bit current values;
- offset `32766`;
- scale `3.0519e-5`;
- current threshold `0.1`;
- `40` readouts per state segment;
- state present only when the tunnelling fraction is strictly greater than `0.5`;
- the same nine measured orientations and standard linear reconstruction of fifteen Pauli expectations;
- ARA coordinate \(x_P=1-\langle P\rangle\).

If an archive cannot be reconstructed with that schema and its own documented orientation timestamps, that
state is `INCONCLUSIVE`; thresholds or signs must not be retuned.

## Frozen expected identities

| Archive | Expected closest parent | Required signs \((XX,YY,ZZ)\) |
|---|---|---|
| `UPUP+DOWNDOWN.zip` | `Phi-plus` | \((+,-,+)\) |
| `UPUP-DOWNDOWN.zip` | `Phi-minus` | \((-,+,+)\) |
| `UPDOWN+DOWNUP.zip` | `Psi-plus` | \((+,+,-)\) |
| `UPDOWN-DOWNUP.zip` | `Psi-minus` | \((-,-,-)\) |

## Per-state frozen gates

Every state must pass all gates for the overall verdict `SUPPORTED`.

| Gate | Requirement |
|---|---:|
| S1 local-child mean absolute expectation | `<= 0.20` |
| S2 same-axis signs | exactly the frozen target pattern |
| S3 weakest same-axis absolute expectation | `>= 0.50` |
| S4 same-axis mean magnitude minus local-child mean magnitude | `>= 0.40` |
| S5 mixed-pair mean absolute expectation | `<= 0.25` |
| S6 same-axis sign product | `<= -0.125` |
| S7 nearest ideal Bell pattern | declared state, MAE margin `>= 0.20` |
| S8 ARA/Pauli affine and pole-reversal residuals | both `<= 1e-12` |

## Cross-state frozen gates

| Gate | Requirement |
|---|---:|
| C1 four-way parent identification | `4/4` correct |
| C2 parent sign-pattern coverage | all four patterns distinct and observed |
| C3 minimum pairwise distance between \((XX,YY,ZZ)\) parent vectors | `>= 1.00` |
| C4 bootstrap parent-label stability | each state correct in `>= 90%` of `2000` record-level draws |
| C5 local-only ideal discrimination | impossible: one common ideal local pattern |

The overall result is `SUPPORTED` only if all `32/32` per-state gates and all `5/5` cross-state gates pass.
Any clean empirical failure is `NOT SUPPORTED`. Missing/corrupt source structure is `INCONCLUSIVE`.

## Controls and outputs

Report:

1. all fifteen Pauli expectations and ARA coordinates for every state;
2. all per-state gates and Bell-pattern errors;
3. the four parent vectors and their six pairwise distances;
4. record-level bootstrap intervals and label-stability rates;
5. local-only compression and parent-label permutation controls;
6. checksum, row-count, orientation-coverage and independent calculation validation.

The same-information standard Pauli account is the compulsory control. ARA may expose the parent/child geometry
more directly, but cannot outperform a lossless affine representation of the same fifteen expectations.

## Required interpretation

A pass may say:

> Across the four public prepared states, ridge-like local children coexist with four distinct structured parent
> relations, and the frozen three-cut ARA/Pauli pattern identifies every declared parent.

It may not say that ARA discovered Bell states, proves universal fractality, outperforms quantum tomography, or
establishes cross-device generalisation.

