# PN1 — Primorial sieve-rung inheritance

**Frozen:** 17 July 2026, before generating or inspecting any PN1 wheel results.  
**Orientation:** up = larger primorial period / later sieve rung; down = smaller primorial period / earlier rung.  
**Classification ceiling:** exact identities are `RECONSTRUCTION / INSTRUMENT CALIBRATION`; the held-out distribution test may rate the finite arithmetic relation but is not RH or physical-universality evidence.

## Fidelity packet — `PN1/v1`

**USER PRIOR — verbatim:** “scalable and reversable ternary”; “The thing is, it depends on the direction it is approached from in my head… it is all the same fractally occuring ARA shape, just with different identities”; after the sieve-rung proposal, “the overall test you propose sounds reasonable” and “Thanks, lets commence the test.”  
**Identity/system:** one complete circular wheel of admissible residue slots modulo a primorial.  
**Ordered poles/direction:** retained candidate slots ↔ released/composite slots; moving up adds the next prime mask and enlarges the complete wheel period. This is a static scale transition, not physical time.  
**Scale/rung origin:** (P_k=\prod_{j\le k}p_j); one rung is the transition (P_k\to P_{k+1}=p_{k+1}P_k).  
**Invariant relational claim:** after the parent wheel is repeated and coupled to the next-prime mask, its ordered local relation survives strongly enough that the parent relation distribution predicts the child better than an order-destroyed parent with the identical gap multiset.  
**Permitted decompression:** survivor set, shed set, exact modular phase, circular gap order, adjacent-pair coordinate, three-gap relation, absolute local scale as an audit field.  
**Forbidden substitutions/proxies:** old global (U/D) gap ARA; treating index as physical time; a phi/Fibonacci scan; an RH claim; calling exact sieve identities new ARA evidence; dropping phase/shed and then calling the scalar the full state.  
**Observable:** exact primorial residue wheels, their circular gaps, next-prime closure mask, and held-out Jensen–Shannon distances.  
**Known ambiguity:** the sieve wheel may be only a clean mathematical calibration occurrence rather than the most revealing prime-number ARA lens; residue races and prime–zero duality remain separate later objects.  
**Wrong object:** testing only the final prime-gap list, a fitted exponent, or a shuffled/noncircular sequence and treating it as the registered nested wheel transition.

**Dylan fidelity verdict:** `EXACT ENOUGH TO TEST`, recorded from his explicit acceptance of the proposed overall test and instruction to commence; the protocol’s low-energy rule permits an ordinary-language answer to be converted to the fixed label.

## Three-view translation

**Plain restatement:** At each rung the previous candidate circle is copied into a larger circle. The next prime supplies a new coupling mask: some slots remain and some are released into the composite account. Keeping the survivors, shed, order and mask lets us test whether the same nearby-gap relation is inherited by the child rather than merely seeing the same collection of gap sizes.

**Mathematical representation:** Let (C_k\subset\mathbb Z/P_k\mathbb Z) be the reduced residue system and (M_q=\{n:n\not\equiv0\pmod q\}), where (q=p_{k+1}). Then

\[
C_{k+1}=\widetilde C_k\cap M_q,
\qquad
E_{k+1}=\widetilde C_k\setminus C_{k+1},
\qquad
\widetilde C_k=C_{k+1}\sqcup E_{k+1},
\]

where (widetilde C_k) is the (q)-fold lift of (C_k) into period (qP_k). For circular gaps (g_i>0), the registered local coordinate is

\[
x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2).
\]

The registered three-gap relation is the ordered pair ((x_i,x_{i+1})); absolute scale (g_i+g_{i+1}+g_{i+2}) is retained separately for audit but is not used in the primary distribution distance.

**Back-translation:** Two neighbouring gaps are reduced to their relative share on the (0\!-!2) line, and two overlapping readings lock three neighbouring gaps without pretending their overall size is the same. If that ordered relation is genuinely carried up the sieve ladder, the parent distribution should resemble the next wheel more than a parent whose identical gaps have been randomly rearranged.

**AI additions:** sieve wheel chosen as the ARA identity; (x_i) chosen as the bounded local coordinate; overlapping pair chosen as the three-gap extension; Jensen–Shannon divergence chosen as the distribution score; permutation chosen as the order-null.  
**Information discarded by the primary score:** absolute residue location, absolute three-gap size, zeta-zero information, and the exact modular phase. These remain audit fields; the phase is used only in the exact calibration check.  
**Alternative objects:** residue-class prime races, normalized final prime gaps, zeta-zero spacings, and explicit-formula prime residuals.  
**First collapse risk:** (x_i) alone discards scale and modular phase. It is therefore only the registered local relation coordinate, never the full ARA state.

## Frozen test contract

### Data and split

- Exact wheels for cumulative primes `[2, 3, 5, 7, 11, 13, 17, 19]`; no downloaded or estimated data.
- Development/calibration rungs end at `13`; no parameter selection may use wheels `17` or `19`.
- Held-out transitions: `13 -> 17` and `17 -> 19`. They are sequential and therefore not independent replications.
- Fixed seed `20260717`; `200` independent circular gap-order permutations per held-out parent.

### Primary prediction — relational inheritance

For both held-out transitions and both registered observables:

1. pair distribution: (x_i), `64` equal-width bins on `[0,2]`;
2. three-gap distribution: ((x_i,x_{i+1})), `24 x 24` equal-width bins on `[0,2]^2`;

the Jensen–Shannon divergence from ordered parent to actual child must be smaller than the median divergence from shuffled parent to actual child. The fixed one-sided permutation value is

\[
p=\frac{1+\#\{D_{shuffle}\le D_{ordered}\}}{201}.
\]

**Signed prediction:** all four comparisons win with (p\le0.05).  
**Primary falsifier:** any one of the four has (D_{ordered}\ge\operatorname{median}(D_{shuffle})) or (p>0.05). No partial-success rewrite is allowed; partial patterns may be reported only as secondary description.

### Mandatory exact calibration checks

For each transition:

1. measured release fraction equals (1/q) by exact integer counts;
2. survivor and shed sets are disjoint and reconstruct the lifted parent exactly;
3. the modular phase rule (n\bmod q=0) identifies every released slot and no survivor;
4. geometry-only context has zero information about closure over the complete (q)-fold lift: each repeated parent context contains exactly one release among (q) phase positions.

Failure of any exact check invalidates the implementation; it is not an ARA null.

### Rivals and robustness

- Primary negative control: random circular permutation preserving the complete parent gap multiset, total period, mean, variance and every one-gap statistic.
- Coordinate rival: conventional log-ratio (log(g_{i+1}/g_i)); it is a monotone reparameterisation and may not be portrayed as independent corroboration.
- Bin sensitivity after the frozen primary: pair bins `[32, 128]`; three-gap bins `[12, 36]`.
- Split-half check: repeat the primary distances on the two declared semicircular residue ranges without retuning.
- Exact sieve update is the full-information ceiling. ARA cannot claim to outperform an algorithm supplied the complete mask.

### Rating fence

- `SUPPORTED [pre-registered, arithmetic, unreplicated]` only if all four primary comparisons pass and all calibration/robustness checks remain coherent.
- `SUGGESTIVE` is forbidden as a rescue for the registered all-four claim; a three-of-four pattern is `NOT SUPPORTED` for the primary and may seed a new test.
- Exact calibration success is reported as `RECONSTRUCTION`, regardless of the primary result.
- Nothing in PN1 may be cited as progress on RH, proof of universal physical ARA geometry, or a unique advantage over the equivalent log-ratio coordinate.

