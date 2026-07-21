# PN13 decimal-rung leak law — translation-fidelity packet v1

**Claim ID:** `PN13/DECIMAL-RUNG-LEAK/v1`  
**Declared:** 21 July 2026  
**Status:** frozen before the PN13 development and target values were calculated  
**Dylan fidelity verdict:** `EXACT ENOUGH TO TEST` under the low-energy explicit-approval rule: after the proposed
test was back-translated as an additional decimal place on each independently declared structural rung, while
controlling ordinary `1/sqrt(N)` cancellation, Dylan replied, “Yes, can we test that. It might be the rule we have
been hunting.”

## F0 — frozen source

**USER PRIOR:**

> “Is it just an extra digit for each rung?”

After the distinction between a numerical decimal shift and a demonstrated rung law was stated:

> “Yes, can we test that. It might be the rule we have been hunting.”

**Identity/system being measured:** the recurring small uncancelled remainder in the prime ARA work, represented in
two already-defined appearances: PN12's circular ladder-step vector and PN10B's signed adjacent-child coupling.

**Ordered poles and direction:**

- PN12 arm: positive circular direction is increasing normalised next-child phase; up is a tenfold increase in the
  prime-ladder rung index while the measurement window remains fixed at 4,000 steps.
- PN10B arm: Phase A is `A=2(n mod q)/q`, Phase B is `2-A`, and signed child coupling is
  `(A_j-1)(A_(j+1)-1)`; up is a tenfold increase in the raw-integer scale while interval width and child count remain
  fixed.

**Scale/rung origin:** a multiplication by ten in the independently declared scale coordinate is the testable
decimal-rung proxy. This packet does **not** assume that every ARA octave is intrinsically base ten.

**Invariant relational claim:** after one upward decimal-scale rung, the same signed residual retains its orientation
or sign while its magnitude is divided by ten. Reversing one rung multiplies it by ten.

**Permitted decompression:**

1. the PN12 signed two-dimensional mean step vector, not only its unsigned length;
2. the PN10B signed mean of adjacent child products at prime nodes;
3. separate reporting of magnitude, sign/direction, uncertainty and controls;
4. reporting whether the same pattern belongs to surviving composites as well as primes.

**Forbidden substitutions/proxies:**

- comparing unrelated values only because their printed decimals resemble one another;
- introducing division by ten after seeing a new target;
- increasing sample size while calling its ordinary `1/sqrt(N)` shrinkage a structural rung;
- discarding the vector direction and freely choosing a new direction at every rung;
- changing the nine-child definition, the `n^0.45` paid-gate boundary or the interval width between integer scales;
- treating failure of either prime proxy as a refutation of the full ARA framework.

**Observable needed:**

1. fixed-width PN12 vector windows beginning at prime-ladder indices `10^3`, `10^4` and `10^5`;
2. fixed-width PN10B child-coupling intervals beginning at `4*10^8`, `4*10^9` and `4*10^10`.

**Known ambiguity / competing reading:** “rung” may mean structural ladder height, raw-number magnitude, aggregation
depth or another ARA octave. PN13 deliberately tests two explicit decimal-scale readings and does not merge them.

**Wrong-object condition:** if sample count changes between rungs, if only unsigned magnitudes are matched, or if
different formulas are selected at different scales, the test no longer measures this packet's claim.

## F1 — three-view translation

### Plain restatement

The suggested rule is that the same small leftover does not merely recur near `0.014`. When we climb one declared
decimal rung without changing how we measure it, the leftover should keep pointing the same way and gain one leading
zero: roughly `0.14 -> 0.014 -> 0.0014`. If it instead stays around the noise size or changes direction, the apparent
decimal relation was not a rung law in that reading.

### Mathematical representation

For a signed observable `L_k` measured on decimal rung `k`, the primary relation is

\[
\underbrace{L_{k+1}}_{\substack{\text{same residual}\text{one rung up}}}
=
\underbrace{10^{-1}}_{\substack{\text{one additional}\text{decimal place}}}
\underbrace{L_k}_{\substack{\text{residual on}\text{the prior rung}}}.
\]

For PN12, `L_k` is a complex/signed circular vector. For PN10B, `L_k` is a signed scalar coupling mean.

### Back-translation without the source wording

Measure one identity in exactly the same way at neighboring tenfold scales. The proposed transfer operator preserves
which side/direction the imbalance occupies but leaves only ten percent of its previous magnitude at the larger
scale. A change in averaging depth is held fixed so ordinary cancellation cannot impersonate the transfer.

## Added assumptions and discarded information

**AI additions:** base-ten scaling is used as an explicit rung proxy; the same nine-child coupling remains comparable
across integer decades; the PN12 fixed-window vector and PN10B coupling are two eligible appearances of the proposed
same law.

**Information discarded:** the full sphere, all child identities beyond the nine PN10B gates, Phi handover geometry,
and non-decimal/log-variable octave definitions are outside this test.

**Alternative objects:** a rule in aggregation depth rather than structural scale; a curved carrier whose direction
changes; a non-base-ten octave; a Pi-derived constant with no rung recurrence.

**First reversal/flattening risk:** replacing the signed vector by its nonnegative length can make unrelated
directions look like the same residual. Both are therefore reported.

## F3 — critical-field gate

| Field | Match | Note |
|---|---:|---|
| identity | 1 | same previously defined PN12/PN10B residual appearances |
| poles | 1 | orientation/sign retained |
| direction | 1 | up is declared separately in both arms |
| rung | 1 | decimal-scale proxy stated, not universalised |
| observable | 1 | fixed before new targets |
| coupling | 1 | PN10B adjacent-child product unchanged |
| closure | 1 | same residual must scale by `1/10` |
| falsifier | 1 | ratios, directions and rival laws frozen in the protocol |

**Fidelity:** `1.00` as documentation fidelity. This is not a truth probability.

