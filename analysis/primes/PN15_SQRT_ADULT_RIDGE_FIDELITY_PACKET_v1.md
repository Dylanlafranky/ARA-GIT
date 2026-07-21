# PN15 full-square-root child closure and adult-rung ridge - translation-fidelity packet v1

**Claim ID:** `PN15/SQRT-CHILD-ADULT-RIDGE/v1`  
**Declared:** 21 July 2026  
**Status:** frozen before scale-12 square-root gates or results were calculated  
**Dylan fidelity verdict:** `EXACT ENOUGH TO TEST` under explicit approval.

## F0 - frozen source

**USER PRIOR from the prime discussion:**

> "The whole of two half waves at 1.0."

**DYLAN CORRECTION retained from the TE-ARA discussion:** TE-ARA for an identity is always `2`; equal `1+1` is a
possible ridge allocation, not the universal definition of TE-ARA.

After PN14 recovered the `n^0.45 -> n^0.90` adult and its fresh growth ridge, Codex proposed:

> "The cleanest next test is the separately frozen full square-root boundary: two children near n^0.5 predict adult
> growth near 10, giving another precise ridge test without reusing the n^0.45 construction."

**USER APPROVAL:**

> "sure let's do that test"

**Identity/system being measured:** two adjacent prime residue cycles immediately below the complete factor boundary
`sqrt(N)`, their exact coprime adult period, and the relation between consecutive decimal-rung growth steps.

**Ordered poles and direction:** the two adjacent residue children are Phase A and Phase B for this local identity.
Up means multiplying the declared anchor `N` by ten. Pole names may be reversed if declared; the calculations retain
one order.

**Scale/rung origin:** anchors `N_d=4*10^d`. At each anchor, select the nine largest prime gates below `sqrt(N_d)`.
This is the exact integer factor-completeness boundary at the anchor, not a claim that every sampled integer later in
the fixed-pair phase walk has the same moving boundary.

**Invariant relational claim:**

1. each square-root child lies near the ARA factor coordinate `1.0`;
2. two such child periods close an adult near parent coordinate `2.0` through `q*r`;
3. because `q,r~N^0.5`, the adult period grows near `N^1`, or factor `10` per decimal rung;
4. consecutive adult growth multipliers should form a near-balanced `1.0` ridge;
5. equal relative child-pair phase should recover the same signed interaction curve on an untouched larger scale.

**Permitted decompression:** child factor coordinates, exact joint periods, scale growth, TE-ARA-normalised comparison
of growth steps, relative phase, signed child product, and separate raw/prime/composite curves.

**Forbidden substitutions/proxies:** calling all fixed-pair phase samples "at the full square-root boundary"; treating
the algebraic identity `q*r` as a novel prime theorem; changing the pair or boundary after scale 12 is seen; using
equal raw windows as equal adult phase; folding primes and composites into one curve; or treating a successful
arithmetic crosswalk as proof of universal physical ARA.

**Observable needed:** median adult period from eight adjacent square-root-gate pairs at scales 8-12, with scale 12
untouched; plus equal-relative-phase curves for one deterministically selected median-product pair.

**Known ambiguity / competing reading:** `sqrt(N)` is both the factor-completeness boundary and a fixed scale
landmark. The detailed phase walk holds the anchor pair fixed while raw `n` changes, so only the anchor itself has
the declared complete boundary. The report must not flatten those two readings.

**Wrong-object condition:** a moving pair chosen separately for each sampled `n`, a non-square-root exponent, a raw-
window amplitude comparison, or target-selected gates would be a different test.

## F1 - three-view translation

### Plain restatement

At a number's full factor boundary, each of the two chosen child cycles occupies about half the logarithmic parent
scale, which reads near `1.0` on ARA's `0-2` diameter. Their joint repeat occupies almost the whole parent scale,
near `2.0`. Moving the parent one decimal rung should make that adult repeat ten times longer; comparing one such
growth step with the next should therefore produce another `1.0/1.0` ridge.

### Mathematical representation

For anchor `N_d=4*10^d`, adjacent prime gates `q_(d,j),r_(d,j)<=sqrt(N_d)`, and factor coordinate

\[
x_N(p)=\frac{2\log p}{\log N},
\]

the child/adult relation is

\[
x_N(q)\approx1,\qquad x_N(r)\approx1,\qquad
x_N(qr)=x_N(q)+x_N(r)\approx2.
\]

For `J_d=median_j(q_(d,j)r_(d,j))` and `G_d=J_(d+1)/J_d`, the adult growth expectation is `G_d~10`. The two-entry
growth-ridge reading is

\[
R_d=\frac{2G_d}{G_d+G_{d+1}},\qquad 2-R_d,
\]

with exact equality at `1+1=2`.

### Back-translation without the source wording

Choose two clocks at half the parent's logarithmic size. Their coprime joint clock closes at almost the complete
parent size. When the parent scale gains one decimal place, the joint clock should also gain one decimal place.
Neighboring growth steps should consequently balance when normalised as a pair.

## Added assumptions and discarded information

**AI additions:** the median of eight adjacent pair products is the adult summary; scale 12 is the untouched target;
the pair closest to the median product is the fixed phase representative; 16 sectors and block width twice the
larger child period are sufficient for the phase-shape comparison; quantitative gates are in the frozen protocol.

**Information discarded:** other factor exponents, Phi, physical energy, moving-boundary phase walks, and any direct
claim of improved prime prediction are outside PN15.

**Alternative objects:** all nine children jointly rather than adjacent pairs; the first prime above `sqrt(N)` as an
anti-phase gate; a moving square-root pair; or a non-decimal scale ladder.

**First flattening risk:** the factor boundary is complete at `N_d`, while the fixed pair's adult cycle spans raw
positions away from `N_d`. The latter tests waveform transfer, not completeness at every sampled point.

## F3 - critical-field gate

| Field | Match | Note |
|---|---:|---|
| identity | 1 | adjacent square-root child cycles and their adult |
| poles | 1 | ordered residue children |
| direction | 1 | up is tenfold anchor scale |
| rung | 1 | `N_d=4*10^d`, boundary exponent `0.5` |
| observable | 1 | child/adult coordinates, growth ridge, phase shape |
| coupling | 1 | coprime pair closure |
| closure | 1 | `q*r`, coordinate sum near `2` |
| falsifier | 1 | frozen in companion protocol |

**Fidelity:** `1.00` as documentation fidelity, not truth probability.

