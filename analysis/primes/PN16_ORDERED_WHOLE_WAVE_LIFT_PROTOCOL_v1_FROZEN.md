# PN16 ordered whole-wave lift protocol

**Test ID:** `PN16/ORDERED-WHOLE-WAVE-LIFT/v1`  
**Frozen:** 21 July 2026, Australia/Brisbane  
**Status at freeze:** protocol only; PN16 result files do not yet exist  
**Data source:** deterministic integer arithmetic; no external data  
**Protected object:** the separately frozen full p31 primorial-wheel capstone remains unopened

## Question

Test Dylan's recursive ARA statement without treating its coupling sign as ordinary addition:

\[
\underbrace{A+B\longrightarrow AB}_{\text{two ordered child phases close as one whole}},
\qquad
\underbrace{AB+BA\longrightarrow \text{next parent}}_{\text{whole plus reversed whole lifts a rung}}.
\]

Here `+` means ordered coupling, not arithmetic addition. PN16 asks which parts of this statement are present in
the exact prime-sieve geometry.

## Operational definitions

For the first `k` primes `p_1,...,p_k`, let

\[
M_k=\prod_{i=1}^{k}p_i
\]

and let `P_p` be the binary sieve projection that removes multiples of prime `p` from one complete period.

- **AB / forward whole:** apply `P_2,P_3,...,P_{p_k}` in ascending order.
- **BA / reverse whole:** apply the same gates in descending order.
- **Ordered history:** the survivor mask after each partial application.
- **Completed identity:** the final survivor mask after all `k` gates.
- **Same-identity recombination:** apply the completed binary projection twice. This is the literal sieve analogue of
  closing `AB` with a reversed copy that contains no new gate.
- **Quiet-node relation:** the first integer greater than `p_k` that survives the completed parent sieve.
- **True next-rung lift:** repeat the `M_k` parent mask through the new quiet-node prime `q=p_{k+1}` and apply `P_q`.

The phrase **Information³ relation** is reserved here for three separately represented objects: the forward whole,
the reversed whole, and the retained relation between them. A reversed copy does not count as independent new
information merely because it is written in the other order.

## Separation

- Development rungs: terminal primes `5, 7, 11, 13`.
- Code-isolated target lift: terminal prime `17`, with the next gate `19` concealed from the primary target builder
  until it has recovered the first quiet node from the p17 parent mask.
- The p19 target period is `9,699,690`, which is small enough to materialize exactly.
- A secondary theorem-scale check recovers the next quiet-node prime for every consecutive pair through `997`
  using only gcd against the current primorial's prime inventory. It does not materialize those primorial periods.

This is a structural calibration, not a blind number-theory discovery: all primes involved are established and the
algebraic commutativity/idempotence of sieve projections is known. Code isolation tests the implementation and the
specific ARA translation, not historical novelty.

## Frozen endpoints

### P1 — ordered histories remain visible

At each development and target parent with at least three gates, at least one matched partial depth must have a
nonzero Hamming distance between forward and reverse histories.

**Meaning:** direction/order can remain as process information before closure.

### P2 — completed AB and BA identities coincide

The final forward and reverse masks must agree at every tested rung, with Hamming distance exactly zero, and each
must equal the direct coprimality mask `gcd(n,M_k)=1`.

**Meaning:** the two ordered routes close to the same sieve identity.

### P3 — reversed-copy recombination is idempotent

Combining the completed forward and reverse masks by the sieve's logical composition must return the same parent
mask, not the next-rung mask.

**Falsifier for the literal lift:** if this same-identity recombination already equals the true p19 child mask, then
the reversed whole alone generated the next rung.

### P4 — the current whole locates the next singular/quiet node

The smallest integer `n>p_k` surviving every current gate must equal the next prime `p_{k+1}` for all materialized
rungs and every theorem-scale check through `997`.

**Meaning:** the completed lower-rung web contains an exact bottom-up rule for locating the next prime.

### P5 — the quiet-node relation completes the next rung exactly

After recovering `q` from P4, tile the p17 parent mask `q` times and remove the one `q`-divisible lift of every
parent survivor. The result must equal a direct p19 coprimality mask at every position.

Required counts:

\[
\#\text{parent survivors before the new gate}=q\,\varphi(M_k),
\]

\[
\#\text{newly released lifts}=\varphi(M_k),
\qquad
\#\text{child survivors}=(q-1)\varphi(M_k).
\]

### P6 — no prime-specific predictive promotion

Even if P1-P5 pass, PN16 may claim only an exact ARA crosswalk of the established recursive wheel sieve. It may not
claim a faster prime algorithm, a new prime theorem, or independent predictive information beyond the lower-rung
sieve state.

## Primary quantities

For matched partial depth `j`, the path disagreement is

\[
D_{k,j}=\frac{1}{M_k}\sum_{n=0}^{M_k-1}
\left|H^{AB}_{k,j}(n)-H^{BA}_{k,j}(n)\right|.
\]

The integrated ordered-path relation is the mean of `D_{k,j}` over partial depths. Completion is assessed
separately at `j=k`.

For the target lift, the missing-relation fraction is measured both over all integers and conditional on parent
survival:

\[
L_{\rm all}=\frac{\varphi(M_k)}{qM_k},
\qquad
L_{\rm parent}=\frac{1}{q}.
\]

## Controls

1. Direct `gcd(n,M_k)=1` mask for every materialized parent.
2. Euler-totient survivor count `phi(M_k)`.
3. Direct p19 coprimality mask for the lifted target.
4. An independently coded validator that does not import the primary analysis module.
5. Exact algebraic expectations for gate commutativity, projection idempotence, and the one-deletion-per-parent-
   residue wheel lift.

## Decision interpretation

- P1+P2: ordering is retained in the path but coarse-grains to one completed identity.
- P3 pass: `AB` and reversed `BA` are not, by themselves, two independent next-rung poles in this representation.
- P4+P5: the next rung is nevertheless constructed bottom-up when the first quiet node is retained as the new
  coupling relation/gate.
- If P3 fails, the user's stronger literal `AB+BA -> next rung` reading receives direct support in this sieve
  operationalization.

The result must keep **exact arithmetic**, **ARA interpretation**, and **new predictive claim** in separate ledgers.
