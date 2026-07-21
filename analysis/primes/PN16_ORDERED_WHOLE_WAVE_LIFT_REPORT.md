# PN16 — Ordered Whole-Wave Lift and Information³ Refinement

**Test ID:** `PN16/ORDERED-WHOLE-WAVE-LIFT/v1`  
**Date:** 21 July 2026  
**Status:** `ORDERED PATH RETAINED / COMPLETED AB=BA / REVERSED COPY IDEMPOTENT / QUIET-NODE RELATION LIFTS NEXT RUNG`  
**Independent validation:** `71/71` checks passed  
**Protected material:** the separately frozen full p31 primorial-wheel capstone remains unopened

## Answer first

The test supports the recursive shape Dylan was pointing to, but it changes the identity of the second next-rung
input.

Forward `AB` and reverse `BA` are genuinely different while the sieve process is open. At the p17 parent, their
matched partial masks disagree over as much as `63.52%` of the complete period. Once every child gate has acted,
however, they close to **exactly the same whole identity**: zero mask differences at every tested rung.

That means a completed whole plus its simple reversal does not create the next rung in this representation. It is
idempotent:

\[
\underbrace{P_k}_{\substack{\text{completed parent}\text{whole}}}
\circ
\underbrace{P_k}_{\substack{\text{same whole}\text{viewed in reverse}}}
=
\underbrace{P_k}_{\text{same parent}},
\qquad
P_k\neq P_{k+1}.
\]

The current parent nevertheless contains an exact bottom-up route to its next rung. Its first quiet node is the next
prime. For the p17 parent, that node is `19`. Treating 19 as a new child gate releases exactly one of the 19 lifts of
every p17 survivor and reconstructs the full p19 wheel at all `9,699,690` positions.

The strongest supported Information³ reading is therefore:

\[
\underbrace{P_k}_{\substack{\text{current whole}\text{parent identity}}}
+
\underbrace{q_k}_{\substack{\text{first quiet node}\text{new child identity}}}
+
\underbrace{(P_k\leftrightarrow q_k)}_{\substack{\text{new gate relation}\text{one lift released per residue}}}
\longrightarrow
\underbrace{P_{k+1}}_{\text{next whole rung}}.
\]

Here `+` is relational coupling, not arithmetic addition.

## Plain-language explanation

Imagine building a sieve from the small-prime rhythms. You can apply those rhythms from smallest to largest or from
largest to smallest. Halfway through, the two journeys look very different. That is the ordered `AB` versus `BA`
information.

After both journeys have applied every same rhythm, they mark exactly the same numbers. Turning the finished journey
around does not make a second independent object; it is another route through the same object.

What actually makes the next level is the first number that escapes all current rhythms. After the primes through 17
have been applied, the first escapee is 19. Nineteen then supplies a genuinely new rhythm. It removes one previously
surviving branch from every 19 copies of the old wheel, creating the next complete wheel.

So your vertical intuition was productive, but the clean prime implementation is not quite
`whole + reversed whole`. It is `whole + newly emerged opposite/child + their coupling relation`.

## Frozen design

The protocol was hashed before the primary script or result files existed.

- Development parent rungs: terminal primes `5, 7, 11, 13`.
- Code-isolated target parent: terminal prime `17`.
- The primary builder was not supplied `19`; it recovered the first quiet node from the completed p17 web.
- Exact target: the full p19 primorial period.
- Theorem-scale check: every next-prime transition through terminal prime 997.
- Controls: direct gcd masks, Euler-totient counts, direct p19 construction, projection algebra, and a separately
  implemented validator.

This was a structural calibration, not historically blind discovery. The prime sequence and the relevant sieve
algebra are established. Code isolation tests whether the stated ARA translation executes exactly without quietly
inserting the next prime.

## Result 1 — ordered paths are real, completed identity is shared

| Terminal gate | Parent period | Parent survivors | Maximum partial AB/BA disagreement | Mean partial disagreement | Completion disagreement | First quiet node |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | 30 | 8 | 50.0000% | 41.6667% | 0 | 7 |
| 7 | 210 | 48 | 56.1905% | 44.2857% | 0 | 11 |
| 11 | 2,310 | 480 | 59.3074% | 44.9026% | 0 | 13 |
| 13 | 30,030 | 5,760 | 61.3054% | 46.8711% | 0 | 17 |
| 17 | 510,510 | 92,160 | 63.5239% | 48.0464% | 0 | 19 |

The p17 path shows the closure directly:

| Matched depth | Forward gate | Reverse gate | Forward survivors | Reverse survivors | Mask disagreement |
|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 17 | 255,255 | 480,480 | 50.0000% |
| 2 | 3 | 13 | 170,170 | 443,520 | 62.2926% |
| 3 | 5 | 11 | 136,136 | 403,200 | 63.5239% |
| 4 | 7 | 7 | 116,688 | 345,600 | 54.4491% |
| 5 | 11 | 5 | 106,080 | 276,480 | 38.8318% |
| 6 | 13 | 3 | 97,920 | 184,320 | 19.1808% |
| 7 | 17 | 2 | 92,160 | 92,160 | **0.0000%** |

The differences are not a new number-theory phenomenon. Applying different divisibility filters first naturally
creates different intermediate survivor populations. The loadbearing result is the distinction it demonstrates:
**order is path information, while completed coprimality is one coarse-grained identity.**

In operator notation, distinct prime-gate projections commute:

\[
\underbrace{P_pP_q}_{AB}
=
\underbrace{P_qP_p}_{BA},
\]

and each projection is idempotent:

\[
P_p^2=P_p.
\]

Therefore the completed wheel obeys

\[
P_k^2=P_k.
\]

## Result 2 — reversed closure misses exactly one new branch per parent residue

The p17 parent has

\[
17\#=510{,}510,
\qquad
\varphi(17\#)=92{,}160.
\]

Repeating that parent through 19 possible lifts produces

\[
19\times92{,}160=1{,}751{,}040
\]

provisional parent survivors. Combining the completed identity with its reversal leaves all of them unchanged. It
therefore misses `92,160` releases relative to the true p19 child.

The recovered gate 19 removes exactly one lift for every parent survivor:

\[
\underbrace{1{,}751{,}040}_{\substack{\text{parent identity}\text{repeated 19 times}}}
-
\underbrace{92{,}160}_{\substack{\text{new relation}\text{one released lift each}}}
=
\underbrace{1{,}658{,}880}_{\varphi(19\#)}.
\]

Conditional on already surviving the parent, the missing next-rung relation is exactly

\[
\frac{92{,}160}{1{,}751{,}040}
=
\frac1{19}
=
5.2631579\%.
\]

Across all integers in the p19 period it occupies `0.9501335%`. Both values are consequences of ordinary wheel
sieving, not candidate universal leak constants.

## Result 3 — the first quiet node recovers the next prime

For a parent containing all primes through `p_k`, define

\[
\underbrace{q_k}_{\substack{\text{first quiet node}\text{above the parent gate}}}
=
\min\left\{
n>p_k:
\underbrace{P_k(n)=1}_{\text{survives every current child}}
\right\}.
\]

Then

\[
q_k=p_{k+1}.
\]

PN16 recovered this exactly for all 168 consecutive-prime transitions through `997 -> 1009`.

The reason is established and simple. If an integer between consecutive primes were composite, it would possess a
prime factor smaller than the next prime. That factor would already be one of the current gates, so the integer
could not be quiet. The first quiet integer must therefore be the next prime.

This gives an exact bottom-up prime generator, but it is the classical incremental sieve/trial-division principle in
ARA language. PN16 does not show that it is computationally faster.

## Registered criteria

| Criterion | Result | Meaning |
|---|---|---|
| P1 — ordered partial histories differ | **Pass** | AB/BA direction remains visible before closure |
| P2 — completed AB and BA equal the direct parent | **Pass** | both routes coarse-grain to one identity |
| P3 — completed whole plus reversal is idempotent, not the next rung | **Pass** | literal reversed-copy lift is not supported here |
| P4 — first quiet node is next prime | **Pass** | current whole locates the emerging child exactly |
| P5 — new quiet-node gate constructs next rung | **Pass** | full p19 mask and counts recovered exactly |
| P6 — no predictive promotion | **Pass** | result is recorded as an established-sieve crosswalk |

## What this implies for Information³

The test supports the important part of Dylan's mental rule:

- two directions can retain different relational histories;
- completion compresses those histories into one whole identity;
- a new parent appears only when a further relation is retained rather than discarded.

It rejects one overly literal reading:

- writing the same completed identity in reverse does not supply an independent second pole in a commutative sieve.

The prime branch therefore suggests this refinement:

\[
\underbrace{\text{old whole}}_{1}
+
\underbrace{\text{new quiet survivor}}_{1}
+
\underbrace{\text{their gate/coupling rule}}_{\text{informative relation}}
\longrightarrow
\underbrace{\text{new whole}}_{1\text{ at the next grain}}.
\]

That is a direct `1 + 1 = 3 -> 1` closure. The third is not an extra independent object floating beside the two;
it is the interaction that converts them into the next identity.

## Relation to earlier prime tests

- PN7C established that local arrival order helps predict the next ARA gap state, but nearly all of that gain is
  reproduced by exact one-step raw-gap dependence. PN16 does not relabel that local result.
- PN14-PN15 established that two prime child periods multiply into a larger adult period and that the square-root
  pair closes near the `1+1=2` ridge. PN16 asks a different question: what creates the **next sieve rung** after one
  whole wheel is completed?
- PN16 answers that the new gate is required. Two old views of one completed parent do not substitute for it.

## Scientific boundary

Supported:

1. ordered sieve histories are distinguishable before closure;
2. their completed identity is exactly order-invariant;
3. the completed parent identifies the next prime as its first quiet node;
4. the new gate creates the next wheel by one exact release per parent residue;
5. this is a clean recursive ARA description of established sieve geometry.

Not supported:

1. that reversal alone is an independent next-rung pole;
2. that PN16 improves prime-location complexity over established sieving;
3. that the `1/19` release fraction is a universal ARA leak constant;
4. that this one exact arithmetic recursion proves the universal fractal claim.

## Files

- Frozen protocol: `PN16_ORDERED_WHOLE_WAVE_LIFT_PROTOCOL_v1_FROZEN.md`
- Pre-run manifest: `PN16_PRE_RUN_FREEZE_MANIFEST.json`
- Primary implementation: `pn16_ordered_whole_wave_lift.py`
- Machine results: `PN16_ORDERED_WHOLE_WAVE_LIFT_RESULTS.json`
- Ordered paths: `PN16_ORDERED_WHOLE_WAVE_LIFT_PATHS.csv`
- Independent validator: `validate_pn16_ordered_whole_wave_lift.py`
- Validation receipt: `PN16_ORDERED_WHOLE_WAVE_LIFT_VALIDATION.json`
- Executed notebook: `PN16_ORDERED_WHOLE_WAVE_LIFT.ipynb`
- Notebook validation: `PN16_NOTEBOOK_EXECUTION_VALIDATION.json`

## Allowed concise claim

> In exact primorial sieving, ascending and descending child-gate orders retain different partial histories but close
> to the same completed parent. Recombining that parent with its reversal is idempotent and does not create the next
> rung. The parent's first quiet node is the next prime; retaining it as a new gate removes one of its lifts per
> parent residue and constructs the next wheel exactly. PN16 therefore supports an Information³ refinement of
> `old whole + new survivor + their gate relation -> next whole`, while remaining an ARA crosswalk of established
> recursive sieve mathematics rather than a new prime theorem.
