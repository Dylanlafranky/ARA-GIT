# Q14 child-phase-swap fidelity contract

**Test ID:** `Q14-CHILD-PHASE-SWAP-v1`  
**Ledger ID:** `T273`  
**Frozen:** 24 July 2026, after Q13 outcomes were open but before calculating Q14 swap metrics  
**Source:** Q13's 44 matched Ramsey/Hahn four-child cells

## Dylan's claim being tested

At a parent-to-child crossing, the two phase paths exchange roles:

\[
A_{\rm parent}\rightarrow B_{\rm child},
\qquad
B_{\rm parent}\rightarrow A_{\rm child}.
\]

For Q13's two parent views, the testable correspondence is therefore:

\[
(R_A,R_B)\longleftrightarrow(H_B,H_A)
\]

rather than the same-label correspondence:

\[
(R_A,R_B)\longleftrightarrow(H_A,H_B).
\]

## Fidelity boundary

Ramsey and Hahn are separate experimental protocols, not successive time events. Q14 tests whether their two
derived child sets have a crossed correspondence at matched ordinal stages. It does not observe literal energy
travelling from Ramsey to Hahn.

The four coordinates are locally normalized transforms of the same reconstructed density matrices. “Energy
path” is therefore represented here by normalized child participation, not by an independently measured energy
observable.

## No reinterpretation after opening

- Do not exchange labels after seeing results.
- Do not add state-specific or wait-specific flips.
- Do not choose different pairings for amplitude and direction.
- The swap and same-label controls use identical records, scales and held-out folds.
- Report both amplitude and direction, including failed gates.

