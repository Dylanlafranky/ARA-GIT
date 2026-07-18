# PN1C/v1 — parameter-matched sieve-rung compression competition

**Test ID:** `T228 / PN1C/v1`  
**Frozen:** 17 July 2026, before generation or inspection of the prime-23 wheel  
**Orientation:** up = larger primorial period / later sieve rung; this is a static scale hierarchy, not physical time  
**Status at freeze:** `REGISTERED [pre-registered]`

## F0 — fidelity packet

**USER PRIOR — verbatim:** “Okay. Lets run the next step.” The immediately preceding registered next step was: “a parameter-matched compression contest asking whether ARA describes this inherited order more efficiently than Markov, moment and constellation alternatives.”

**Identity/system:** one complete cyclic primorial gap wheel.  
**Parent rung:** wheel through prime 19, already opened by PN1.  
**Held-out child rung:** wheel through prime 23, unopened when this packet was written.  
**Ordered poles/direction:** for adjacent positive gaps, (x=2g_{next}/(g+g_{next})); (x<1) means the next gap is smaller, (x>1) means it is larger, and reversal maps (x\mapsto2-x).  
**Invariant relational claim:** a low-budget linear 0–2 ARA partition of the parent's overlapping relation should preserve the child's relation more efficiently than matched ordinary compressed summaries.  
**Permitted decompression:** fixed decoding from stored parent summary into the same (24\times24) child-comparison grid.  
**Forbidden substitutions:** no prime-23 tuning, no exact modular phase/mask, no full child reconstruction, no phi/RH interpretation, and no relabelling a rival win as ARA after the result.  
**Observable:** Jensen–Shannon divergence in bits between each decoded parent summary and the exact child distribution of ((x_i,x_{i+1})).  
**Wrong object:** testing raw prime gaps rather than the primorial wheel, changing the 0–2 orientation, allowing an eligible model more than 36 declared scalar slots, or supplying exact prime-23 phase information.

**Plain restatement:** keep only a very small description of how neighbouring parent-wheel gaps lean and turn. Ask whether the fixed linear ARA description carries that local order into the next unopened sieve rung better than equally small log, moment, learned-category, independence and constellation descriptions.

**Mathematical object:** if (P_{19}) is the parent (24\times24) empirical distribution and (Q_{23}) the held-out child distribution, each frozen compressor (m) stores (S_m(P_{19})) using at most 36 scalar slots and emits (\widehat Q_m=D_mS_m(P_{19})). Score

\[
d_m=\operatorname{JSD}_2(Q_{23},\widehat Q_m).
\]

**Back-translation:** a smaller (d_m) means that, after the same severe storage limit, that description of the parent looks more like the next rung. It is a test of descriptive efficiency across one exact scale transition, not a test of whether ARA can replace the sieve.

**AI additions:** the 36-slot ceiling, exact competitor set, uniform within-cell decoder, DCT basis, learned-quantile rule and strict-best endpoint are supplied by Sol.  
**Information discarded:** exact residue positions, modular phase, shed identity, full gap sequence and every relation finer than the stored summary.  
**First collapse risk:** treating the fixed ARA grid as the whole ARA state; it is only the deliberately compressed relational lens.  
**Dylan verdict:** `EXACT ENOUGH TO TEST`, converted under the low-energy rule from the explicit instruction to run the already stated next step.

## Frozen target

The exact held-out transition is

\[
19\longrightarrow23,
\qquad
P_{19\#}=9{,}699{,}690,
\qquad
P_{23\#}=223{,}092{,}870.
\]

The child must contain

\[
\varphi(23\#)=36{,}495{,}360
\]

cyclic gaps. It will be generated in ordered lift blocks so the full child residue array need not be retained.

For a gap sequence (g_i), define

\[
x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2),
\qquad
Z_i=(x_i,x_{i+1}).
\]

The primary target (Q_{23}) is the circular (24\times24) histogram of (Z_i), normalized to probability one. The parent input (P_{19}) is defined identically.

## Frozen budget unit

A **scalar slot** stores one real coefficient/probability, one learned boundary, or one integer category label. Fixed public algorithm code, frozen grid edges and the declared DCT basis do not consume slots. This is a transparent parameter-count proxy, not literal compressed bytes. Primary competitors must use at most 36 slots.

## Frozen eligible competitors

All predictions are constructed from the prime-19 parent only.

1. **ARA-linear-6 (`35` slots).** Aggregate the (24\times24) parent matrix into a fixed uniform (6\times6) grid on ([0,2]^2). The 36 cell probabilities have 35 free values. Decode each coarse-cell mass uniformly over its corresponding (4\times4) fine cells.
2. **Log-ratio-6 (`35` slots).** Partition each fine x-bin by the log-ratio coordinate (r=\log[x/(2-x)]), with frozen symmetric edges (( -\infty,-2R/3,-R/3,0,R/3,2R/3,+\infty )) and (R=\log32). Store the (6\times6) parent cell probabilities and decode uniformly over fine cells assigned to each log cell.
3. **DCT-6 (`36` slots).** Apply the orthonormal two-dimensional DCT-II to the (24\times24) parent matrix, retain the top-left (6\times6) coefficients, invert, clip negative reconstructed mass to zero and renormalize.
4. **Learned-quantile-5 (`28` slots).** From the already-open development wheels through primes 13, 17 and 19, freeze four shared fine-bin boundaries that divide their pooled x marginal as nearly as possible into fifths. Store 25 parent cell probabilities (24 free) plus four boundary labels. Decode uniformly inside each learned cell.
5. **Gap-IID (`2M-1 <= 36` slots).** Store the (M) distinct parent gap labels and (M-1) free marginal probabilities. Predict triples as (p(a)p(b)p(c)), then project them into the (24\times24) relation grid. If (2M-1>36), this model becomes ineligible and the frozen primary is invalid rather than silently changing its budget.
6. **Top-9 constellations (`36` slots).** Store the nine most frequent ordered parent gap triples: three integer labels and one probability per triple. Put the unrecorded residual probability uniformly over all 576 target cells, then add each stored triple probability to its mapped cell.

## Reference models outside the primary budget

- **Uniform (`0` slots):** (1/576) in every cell.
- **Raw-gap first-order Markov:** parent marginal plus dense transition rows, projected through (p(a)T(a,b)T(b,c)); declared slot count (M^2+M-1). It is a high-budget ordinary reference and cannot win or lose the <=36 primary.
- **Exact parent relation (`575` free probabilities):** the full (24\times24) parent matrix carried forward unchanged. It is the uncompressed local-relation ceiling, not an eligible compressor.

## Primary prediction and falsifier

Let (d_{ARA}) be the held-out JSD for ARA-linear-6 and let

\[
d_* = \min_{m\in\{log,DCT,learned,IID,constellation\}}d_m.
\]

**Signed prediction:**

\[
d_{ARA}<d_*
\]

and ARA must beat the best rival by at least one relative percent:

\[
\frac{d_*-d_{ARA}}{d_*}\ge0.01.
\]

**Falsifier:** PN1C's compression-advantage claim is `NOT SUPPORTED` if any eligible rival ties or beats ARA, if the margin is below 1%, if any eligible model exceeds the slot ceiling, or if an exact target/calibration check fails. No secondary endpoint may rescue the primary.

## Frozen secondary and robustness checks

1. Marginalize every predicted and target matrix along each axis; report the mean pair JSD. This is descriptive only.
2. Report (d_m), slot count and gain over the zero-slot uniform baseline per stored slot.
3. Repeat ARA/log/DCT comparisons at (4\times4) and (8\times8) retained summaries as a budget frontier; the 8×8 case is outside the primary ceiling. For a sensitivity log partition with k in {4, 8}, use the frozen internal edges R(2j/k-1), j=1,...,k-1, with R=log(32) and infinite outer edges; DCT retains the top-left k×k coefficients and ARA uses k×k uniform linear cells.
4. Recompute the 24×24 target separately on the first and second circular half. ARA must at least beat Gap-IID in both halves for robustness; failure does not change the frozen primary label but blocks a stable-compression claim.
5. Repeat the primary-resolution target with an independently coded streaming traversal and require elementwise count equality.
6. Reverse orientation (x\mapsto2-x), equivalently rotate both matrices by 180 degrees, and require every JSD to remain unchanged to (10^{-12}).

No alternative fine resolution, log boundary, learned boundary, decoder, top-K choice or DCT clipping rule may replace the frozen primary after the child is opened.

## Exact implementation checks

- protocol SHA-256 equals the registered hash;
- parent gap count and sum equal φ(19#) and 19#;
- child streamed gap count is 36,495,360;
- child cyclic gap sum is 223,092,870;
- all child gaps are positive even integers;
- child survivor count equals (22\times\varphi(19\#));
- independent target count matrix equals the primary target matrix exactly;
- every decoded prediction is finite, nonnegative and sums to one.

Exact checks are `RECONSTRUCTION / IMPLEMENTATION CALIBRATION`, not ARA evidence.

## Allowed conclusion ceiling

A pass would support the claim that this frozen linear 0–2 relation grid was the most efficient of these declared <=36-slot summaries for one finite sieve-rung transition. A failure would reject that compression-advantage claim while retaining PN1's earlier order-inheritance result. Neither outcome bears on RH, phi, prime unpredictability or physical universality.
