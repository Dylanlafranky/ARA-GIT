# PN3A adult sieve-path diagnostic protocol

**Test ID:** `PN3A/ADULT-SIEVE-PATH/DEVELOPMENT-v1`  
**Method lock:** 18 July 2026, before computing the outputs below  
**Evidence class:** opened-data structural diagnostic; not a blind prediction and not a rescue of PN3  
**Protected target:** the prime-31 PN1H wheel remains unopened and prohibited

## 1. User prior and question

Dylan distinguished the diagonal child direction already visible in the PN3 relation plane from the larger adult
wave that contains it:

> “I know it has the child of that axis, but I am more referring to the adult.”

> “Maybe we are only measuring half a wave with primes ... the wave against the primes ... It all seems very very
> connection heavy, without much flow.”

The diagnostic asks whether the terminal prime/composite label has collapsed a larger sieve-survival path, and
whether the child diagonal identified in the opened PN3 plane carries stable information about that adult path.

## 2. Data boundary

Use only the already opened PN3 decimal-rung windows:

| Rung | Interval |
|---|---|
| R6 | `[1,000,000,1,010,000)` |
| R7 | `[10,000,000,10,100,000)` |
| R8 | `[100,000,000,101,000,000)` |
| R9 | `[1,000,000,000,1,010,000,000)` |

The population at every rung is the PN3 population of integers coprime to `29#`, with the same local context rule.
R9 is reconstructed from arithmetic and must exactly match the sealed PN3 packet. No new number interval and no
prime-31 wheel are opened.

## 3. Adult sieve observables

For each candidate `n`, recover its first divisor after the p29 boundary:

\[
d(n)=\min\{p>29:p\text{ prime and }p\mid n\},
\]

using `d(n)=0` when no such divisor exists through `sqrt(n)`, so `n` is prime.

For adjacent candidate edge `i`, define its first death rung as the first non-zero value among the two endpoint death
rungs; use zero only when both endpoints are prime.

At sieve threshold `q`, record exact candidate and edge survival:

\[
S_C(q)=\frac1N\sum_n \mathbf 1[d(n)=0\ \text{or}\ d(n)>q],
\]

with the analogous `S_E(q)` for edges. Record cumulative release `1-S(q)` and the conditional per-prime death hazard.

The established independence references are

\[
M(q)=\prod_{29<p\le q}\left(1-\frac1p\right),
\qquad M(q)^2.
\]

These are controls, not ARA predictions.

## 4. Child diagonal and perpendicular coordinates

Retain the opened PN3 endpoint readings

\[
x=\frac{2g_0}{g_{-1}+g_0},
\qquad
y=\frac{2g_{+1}}{g_0+g_{+1}},
\]

then rotate without adding information:

\[
U=\frac{x+y}{2}\in(0,2),
\qquad
V=\frac{y-x}{2}\in(-1,1).
\]

`U` is Dylan's red diagonal/common-mode child direction. `V` is the perpendicular/differential direction. Use 12
fixed equal bins for each. `U=1,V=0` is the equal-gap ridge.

## 5. Adult-stage transfer diagnostic

Map a composite death factor to one of 12 fixed equal bins in normalized logarithmic sieve progress,

\[
t=\frac{\log(d/31)}{\log(\sqrt{H-1}/31)}\in[0,1],
\]

where `H` is the upper bound of that rung. Reserve a thirteenth class for terminal prime survival; for edges it means
both endpoints survive.

Fit smoothed categorical lookup models on one opened rung and score the next:

1. adult-stage marginal only;
2. `U` child bin;
3. `V` child bin;
4. joint `(U,V)` child bin.

Use Dirichlet shrinkage `lambda=64` toward the training marginal. Primary transfers are R7->R8 and R8->R9; R6->R7
is a small-sample sensitivity. Score multiclass log loss in bits. Positive `baseline loss - child loss` means the child
coordinate transfers information about the adult death path.

For `U` and `V`, compare each primary gain with 100 fixed-seed (`20260718`) within-location-block permutations of the
test coordinate. Permutations are calibration controls, not additional model searches.

## 6. Descriptive adult-child surfaces

At 24 logarithmically spaced sieve thresholds, plot the signed redistribution

\[
R_U(q,u)=\log_2\frac{S_E(q\mid U=u)}{S_E(q)},
\]

and the analogous `R_V(q,v)`. Cells with fewer than 100 starting edges are not interpreted. These opened-data surfaces
show where the child texture enters the adult path; they do not create a new validation endpoint.

## 7. Interpretation rules

1. Exact label/death-rung reconstruction is a required calibration check, not ARA evidence.
2. If `U` gains are positive on both primary transfers and exceed `V` on both, retain the diagonal as a stable
   adult-aligned child coordinate.
3. If the sign or ordering fails to transfer, the opened red diagonal is not the missing adult wave by itself.
4. Agreement with the product, logarithmic density or known sieve behaviour is a recovery/crosswalk, not novelty.
5. Structure remaining after `U`, `V` and the exact sieve-path description remains an open missing-aspect lead.
6. No result may alter PN3's failed frozen endpoints or count as evidence for PN1H.

## 8. Required outputs

- deterministic computation script and executed reproducibility notebook;
- exact adult survival/release curves and terminal reconciliation;
- cross-rung adult-stage transfer scores with permutation controls;
- adult-child redistribution figures;
- machine-readable results and independent validation;
- report, conversation record and follow-up-register entry preserving negative and unresolved results.
