# PN1H/TRANSFER/v1 — prime-31 information-pyramid capstone transfer

**Declared:** 17 July 2026, before constructing any prime-31 residue, gap, relation, count, figure or score.
**Status:** `FROZEN / TARGET UNOPENED`.
**Development ceiling:** all design information ends at prime 29.
**Target:** the complete reduced-residue wheel ending at prime 31.
**Geometry authority:** all computed fields remain neutrally oriented. Dylan retains authority for ARA Phase A/Phase B, Space/Time, accumulation/release and directional landmark names.

## User prior and proposed geometry

**Dylan, before freeze:** “A certain amount of triangles have to connect and information wave transfer occur for each prime. It's the largest capstone on a pyramid information. Each rung up, there requires to be more connections for the pyramid, but the information transfer increases because of it.”

The operational reading frozen here is:

> More child information closures support the next parent/capstone identity. The normalized local parent appearance and visible triangle closure become quieter and more distributed, while deeper exact-child information remains stable or grows and the parent direction persists.

This is not a claim that literal Euclidean pyramids exist on the number line. “Triangle” means a relational information closure.

## Exact arithmetic ladder — calibration, not an ARA prediction

Let `N_k` be the number of reduced-residue slots in the wheel ending at rung `k`. Adding a new prime `q` lifts every parent residue `q` times and removes exactly one lift, hence

\[
N_{k+1}=(q-1)N_k.
\]

For the unopened `29 -> 31` target:

\[
N_{31}=30N_{29}=30,656,102,400,
\]

and the primorial period must be

\[
P_{31}=31P_{29}=200,560,490,130.
\]

These identities validate construction only. They cannot count as evidence for ARA.

## Shared ARA coordinate and information triangle

For circular gaps `(g_i)`, retain without modification

\[
x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2),
\qquad
Z_i=(x_i,x_{i+1}).
\]

The information triangle is the ordered three-reading closure

\[
\triangle_i=(A_i,B_i,C_i)
=(X_{i-2},X_{i-1},X_i).
\]

Its visible per-event closure information is

\[
I_{\triangle,k}
=I(X_{i-2};X_i\mid X_{i-1})
=G_{full(A,B),k},
\]

the cross-entropy gain of the full preceding ARA pair over current position `B` alone.

The deeper exact-child contribution is represented by

\[
I_{child,k}=G_{B+shared\ gap,k},
\qquad
I_{below,k}=I_{child,k}-I_{\triangle,k}.
\]

`I_below` measures predictive information available from exact shared child identity beyond the visible three-position ARA closure. It is an operational coding quantity, not physical energy or information flux.

## Parent-scale residual

Use the same 12 by 12 primary relation plane, Gap-IID projection and first-order raw-gap Markov projection as PN1F/PN1G:

\[
R_k=P_k^{ordered}-P_k^{Gap\text{-}Markov1},
\qquad
D_{29\to31}=R_{31}-R_{29}.
\]

The 24 by 24 version remains sensitivity only and cannot rescue a failed 12-bin primary.

## Frozen source landmarks

The final opened p29 values are:

| Quantity | Prime 29 source value |
|---|---:|
| residual L2 | `0.0460901755425546` |
| adjacent ARA mutual information | `0.5714062602555432` bits/event |
| full-pair triangle gain `I_triangle` | `0.4420633155896780` bits/event |
| raw-gap Markov gain | `0.6671579830137071` bits/event |
| shared-child gain `I_child` | `0.8274051730818914` bits/event |
| below-visible surplus `I_below` | `0.3853418574922134` bits/event |
| p23-to-p29 residual cosine | `0.9990059870409774` |
| p23-to-p29 deformation continuation cosine | `0.9952250626457678` |
| five-field leading deformation energy | `0.9765880384751034` |

## Frozen primary pattern

The **full capstone pattern** is supported only if every primary block passes. Individual endpoints are also reported so a partial result is preserved rather than flattened.

### P1 — persistent parent/capstone direction

Pass if all hold:

1. `cos(R_29, R_31) >= 0.98`;
2. `cos(D_23->29, D_29->31) >= 0.98`;
3. after appending `D_29->31` to the five opened 12-bin deformations, the leading uncentred SVD mode retains at least `95%` of deformation energy.

This block tests inheritance of the parent shape and its signed scale direction.

### P2 — quieter normalized local capstone

Pass if all three strict inequalities hold:

1. `||R_31||_2 < 0.0460901755425546`;
2. adjacent ARA mutual information at p31 `< 0.5714062602555432` bits/event;
3. visible triangle closure `I_triangle,31 < 0.4420633155896780` bits/event.

This block tests the proposed distribution of parent support across more child closures. A perfectly equal value fails the strict directional prediction.

### P3 — deeper child identity does not fade with the visible triangle

Pass if all three strict inequalities hold:

1. raw-gap Markov gain at p31 `> 0.6671579830137071` bits/event;
2. shared-child gain `I_child,31 > 0.8274051730818914` bits/event;
3. below-visible surplus `I_below,31 > 0.3853418574922134` bits/event.

This is the primary discriminator from a simple statement that every dependence measure is merely fading toward zero.

### P4 — downward hierarchy transfer

Repeat the identical eight guarded contiguous-fold next-ARA-reading task with Jeffreys smoothing `alpha=0.5`. The predicted order from lowest to highest cross-entropy remains

\[
B+shared\ gap
<raw\ gap\ Markov1
<full(A,B)
<B+signed\ step
<B+distance
<B+direction
<current\ B.
\]

Pass if:

1. the exact seven-model order is preserved;
2. Kendall rank agreement is `1.0`;
3. every non-base representation has positive gain over current `B` in every fold.

## Whole-rung carried relation — required report, not a primary pass

Report

\[
\Sigma_{\triangle,k}=N_k I_{\triangle,k},
\qquad
\Sigma_{child,k}=N_k I_{child,k}.
\]

These are cumulative predictive log-loss advantages across a complete deterministic wheel. They are expected to grow largely because `N_31=30N_29`; they must not be described as physical information flow or promoted as independent confirmations. Report the size-normalized per-event quantities beside every total.

## Model discrimination

The protocol distinguishes two readings:

1. **Ordinary convergence-only:** parent residual amplitude, adjacent dependence and visible triangle closure contract toward a limiting wheel distribution. This reading may pass P1 and P2 but does not require deeper raw/shared-child gains or `I_below` to rise.
2. **ARA capstone distribution:** P1 and P2 occur together with P3 and P4—more child closures support a quieter normalized parent while exact child identity carries an increasing share beneath the visible triangle.

Full ARA capstone support requires `P1 + P2 + P3 + P4`. Passing only P1/P2 is recorded as convergence-compatible partial support, not a capstone confirmation.

## Construction and contamination guards

- Prime 31 is unopened at declaration.
- No implementation may generate or inspect a p31 residue, gap, mask, relation, count or partial target until this protocol is hashed and entered in the prediction ledger.
- Development code must have an executable maximum target prime of 29.
- The final target implementation must stream or use a mathematically exact recurrence; it must not materialize the 30.656-billion-slot target cycle.
- Before p31 is opened, the same target counter must reproduce p29's period, slot count, weighted gap sum, exact gap SHA-256 `92646B2A27C0836D0D99B49B83C3982FC9FE604E3A9780F2DC8FDDBB99DF8A2C`, 12/24-bin planes, raw transitions and all PN1G downward fold scores.
- A separately coded validator must recompute every primary metric from saved aggregate inventories.
- The exhaustive target must be run twice or checked by two mathematically independent exact implementations before public promotion.

## Computational plan before opening

The present Python lift stream would require approximately 31 regenerations of the billion-slot p29 parent and is unnecessarily expensive. Development should first produce either:

1. a compiled nested-stream counter; or
2. an exact recurrence/automaton for the required local gap and relation counts.

That implementation may be calibrated freely on opened targets through p29. No p31 partial preview is permitted during optimization.

## Interpretation fence

A complete pass would support prospective repetition of the information-pyramid capstone pattern across one additional arithmetic rung. It would not prove literal pyramids, physical information waves, universal ARA geometry, prime predictability, the Riemann hypothesis, or a completed ARA cycle. A failed or partial block remains frozen and must not be rescued by post-open redefinition.

**Dylan fidelity verdict:** `EXACT ENOUGH TO FREEZE`, from “Yes lets freeze the pattern and we'll see if it extends to the next.”
