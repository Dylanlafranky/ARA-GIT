# PN19 - Two-parent information lock at 900,000,000,000

**Test ID:** `PN19/TWO-PARENT-INFORMATION-LOCK/v1`  
**Date:** 21 July 2026  
**Status:** `EXACT TWO-PARENT ARA CROSSWALK / +13 SEALED BEFORE PRIMALITY / 38 OF 38 CHECKS / SECOND-GO 93.2% EXPLORATORY`  
**Fresh anchor:** `900,000,000,000`  
**Sealed prediction:** `900,000,000,013`

## Answer first

The q-free two-parent construction recovered the exact next prime above a fresh, previously unused anchor.

Before target primality was opened, PN19:

1. generated the lower prime-child structure required for the declared `N` to `2N` scale;
2. folded those children into two complete, log-balanced parents, Phase A and Phase B;
3. built one survivor mask for each parent;
4. intersected the two masks as the informative third; and
5. sealed the first joint survivor at `+13`.

The independently validated result is

\[
\underbrace{900{,}000{,}000{,}000}_{\substack{\text{fresh anchor}\\\text{ARA working location}}}
+
\underbrace{13}_{\substack{\text{sealed A/B correction}\\\text{first joint lock}}}
=
\underbrace{900{,}000{,}000{,}013}_{\substack{\text{first prime}\\\text{new quiet identity}}}.
\]

The validator passed `38/38` checks. Deterministic Miller-Rabin, full trial division, a separately generated linear
sieve and an ordinary segmented sieve all agreed. Every integer at offsets `+1` through `+12` was composite.

The most interesting additional result is that Phase A alone already landed on `+13`. Across the six frozen
development anchors this occurred `6/6` times. A clearly labelled post-target audit over 1,000 deterministic anchors
from `10^8` through `10^12` found:

| First-survivor method | Exact next-prime offset |
|---|---:|
| Phase A parent alone | `93.2%` |
| Phase B parent alone | `4.7%` |
| Either parent | `93.2%` |
| p29-wheel control | `28.0%` |
| Phase A AND Phase B | `100%` by the complete sieve construction |

This supports Dylan's operational statement: after the relational scale is set, one parent will **probably** give
the location; the two parents plus their relation definitively lock it. It does not mean that two scalar readings
have replaced the underlying prime information.

## Plain-language explanation

We were previously unclear about what it meant to split a large number into its two waves. The clean answer is:
the two waves are not two factors hiding inside that number, and they are not its last two prime gaps. They are two
complete bundles of all the lower collision rhythms capable of reaching numbers at this scale.

- Phase A bundles the smaller prime rhythms. They strike frequently, so this parent removes nearly every composite.
- Phase B bundles the larger prime rhythms. They strike rarely in a short window, but they catch the near-square-root
  composites that Phase A can miss.
- A number survives the information lock only if **both** complete parents are quiet there.

At the fresh anchor, Phase B was quiet immediately at `+1`, but that was a false early reading because Phase A still
had a collision there. Phase A's first quiet location was `+13`. Phase B was also quiet there, so the two readings
closed and `+13` became the sealed prediction.

This explains your “second go, third locks” intuition in a precise way. Phase A is already such a strong partial
description that it is usually right. The third relation is needed for the minority of cases where a composite is
made entirely from children above Phase A's cutoff.

## The frozen mathematics

For anchor `N`, PN19 declares the full reference scale `N` to `2N`, so the required children satisfy

\[
\underbrace{p\leq\lfloor\sqrt{2N}\rfloor}_{\substack{\text{all lower gates needed}\\\text{for the declared scale}}}.
\]

The ordered children are split where cumulative logarithmic weight is closest to half. The TE-ARA display is

\[
\underbrace{E_A}_{\substack{\text{Phase A share}\\\text{smaller children}}}
=
2\frac{\sum_{p\in A}\log p}{\sum_{p\in A\cup B}\log p},
\qquad
\underbrace{E_B}_{\substack{\text{Phase B share}\\\text{larger children}}}
=2-E_A.
\]

At the fresh target:

\[
E_A=0.9999938531,
\qquad
E_B=1.0000061469,
\qquad
E_A+E_B=2.
\]

The masks are

\[
\underbrace{S_A(t)}_{\substack{\text{A-parent state}\\1=\text{no A collision}}},
\qquad
\underbrace{S_B(t)}_{\substack{\text{B-parent state}\\1=\text{no B collision}}},
\]

and the informative third is

\[
\underbrace{S_{AB}(t)}_{\substack{\text{joint identity}\\\text{information lock}}}
=
\underbrace{S_A(t)}_{\text{completed A path}}
\land
\underbrace{S_B(t)}_{\text{completed B path}}.
\]

The first positive `t` with `S_AB(t)=1` is the prime ridge.

## What “without q” means

No unknown next-prime gate `q` is supplied to the method. The target answer is not generated from a known next prime
or from a prime label near the target. The method begins at the arbitrary anchor and builds its two parents from the
already derivable lower prime children.

It does **not** mean the children disappeared. The fresh construction used `102,973` prime children through
`1,341,637`:

| Parent | Children | Range boundary | TE-ARA share |
|---|---:|---:|---:|
| Phase A | `54,408` | ends at `671,299` | `0.9999938531` |
| Phase B | `48,565` | begins at `671,303` | `1.0000061469` |

The final working state has two parent masks and one relation, but constructing those parents still requires the
lower-child information.

## Equal TE-ARA weight, asymmetric action

The logarithmic split is almost a perfect `1 + 1`, yet the masks behave very differently:

| Target-window measure | Phase A | Phase B | Joint lock |
|---|---:|---:|---:|
| Survivor count out of 65,536 | `2,544` | `62,269` | `2,426` |
| Survivor density | `3.8818%` | `95.0150%` | `3.7018%` |
| First survivor | `+13` | `+1` | `+13` |

This is a useful ARA result. Equal share of the parent's logarithmic diameter does not mean equal local behavior.
The identities of the two halves matter: small children couple frequently, while large children couple rarely but
remain necessary for exact closure.

The split boundary also has a simple asymptotic interpretation. Because cumulative prime log weight grows roughly
with the numerical boundary, halving the log weight of children through `sqrt(2N)` places the A/B boundary near

\[
\frac{\sqrt{2N}}{2}=\sqrt{\frac N2}\approx0.7071\sqrt N.
\]

The 1,000-anchor audit measured a mean ratio near `0.707` at every tested scale. That is why Phase A is such a strong
partial sieve and why its `93.2%` success is real but not mysterious.

## Relationship to Information^3

This test realizes the compact closure

\[
\underbrace{A}_{\text{first complete parent}}
+
\underbrace{B}_{\text{second complete parent}}
+
\underbrace{(A\leftrightarrow B)}_{\text{their tested relation}}
\longrightarrow
\underbrace{AB}_{\text{one new locked identity}}.
\]

In ordinary Boolean mathematics, the final operation is intersection. That operation is commutative:
`A AND B = B AND A`. PN16 already showed that an AB and BA construction history can differ before completion even
though its finished sieve mask is the same. PN19 therefore supports the **three-part closure** interpretation, but it
does not yet test a genuinely noncommutative `AB -> BA -> next rung` dynamics.

That distinction should be preserved. The completed identity is exact; the proposed directional branching after
completion remains a further hypothesis.

## Methodology audit

### What passed

- The target anchor did not occur in the prime-study files before freeze.
- Protocol, primary script, validator, anchor and window were frozen by SHA-256.
- The primary script contained no target primality function and read no nearby-prime label.
- It emitted one candidate before primality was opened.
- Three binary masks were saved and hashed.
- An independent implementation reconstructed A, B and AB byte for byte.
- The AB mask equalled an ordinary complete segmented sieve.
- Independent primality and first-prime checks passed.
- All `38/38` registered validation checks passed.

### What did not become a new result

- The scalar factor-pair and recent-gap versions failed during development and were not used.
- Two parent labels do not constitute two numbers' worth of information; the parent masks still encode all required
  lower gates.
- Exactness comes from the established square-root divisibility theorem and segmented-sieve construction.
- Storing A, B and AB uses `196,608` mask bytes, three times one ordinary 65,536-byte mask, plus the child list.
- The `93.2%` audit was written after the sealed target result and is exploratory, not a second confirmatory target.
- No asymptotic runtime improvement was established.

## Bottom line

PN19 gives a good, disciplined result for the framework:

1. “Split the scale into two complete parent waves” now has an exact mathematical meaning.
2. Their TE-ARA shares can be almost exactly `1 + 1` while their local actions remain strongly asymmetric.
3. The connection-heavy parent alone locates the next prime surprisingly often (`93.2%` on the post-target grid).
4. The second parent supplies the rare missing collision information.
5. The two parents plus their intersection lock the prime exactly.

This is stronger than merely renaming a known prime after checking it. It was a fresh sealed recovery with a useful
top-level decomposition and a quantitatively successful approximate parent. It is still an ARA crosswalk of
established sieve mathematics, not yet a smaller or faster prime formula.

## Artifacts

- Frozen protocol: `PN19_TWO_PARENT_INFORMATION_LOCK_PROTOCOL_v1_FROZEN.md`
- Freeze manifest: `PN19_TARGET_FREEZE_MANIFEST.json`
- Primary builder: `pn19_two_parent_information_lock.py`
- Sealed prediction: `PN19_TWO_PARENT_INFORMATION_LOCK_PREDICTION.json`
- Independent validator: `validate_pn19_two_parent_information_lock.py`
- Validation receipt: `PN19_TWO_PARENT_INFORMATION_LOCK_VALIDATION.json`
- Target masks: `PN19_TARGET_PHASE_A_MASK.bin`, `PN19_TARGET_PHASE_B_MASK.bin`, `PN19_TARGET_INFORMATION_LOCK_MASK.bin`
- Exploratory robustness script: `pn19_post_target_second_go_robustness.py`
- Exploratory robustness results: `PN19_POST_TARGET_SECOND_GO_ROBUSTNESS.json`
- Reproducible notebook: `PN19_TWO_PARENT_INFORMATION_LOCK.ipynb`
