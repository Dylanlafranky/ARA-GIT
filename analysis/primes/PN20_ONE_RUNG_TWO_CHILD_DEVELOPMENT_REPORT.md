# PN20 — one-rung, two-child prime-location development audit

**Date:** 21 July 2026  
**Status:** **DEVELOPMENT NULL — fresh 87-bit anchor remains unopened**  
**Fresh-anchor SHA-256:** `47272ef39edb8a74c2beeeadb0b6ab2e919485575581210b9643c129a80054f1`  
**Scope:** seven previously opened anchors only: `10^8`, `10^9`, `10^10`, `10^11`, `4×10^11`, `7×10^11`, `9×10^11`

## Result first

The proposed compression—retain only the largest immediate Phase A child and largest immediate Phase B child, close them as `AB`, reflect as `BA`, then use two landmarks to locate the next prime ridge—did **not** locate the next prime under any of the three operational definitions tested.

- Numerically largest square-root children: **0/7** exact next primes.
- Unrestricted strongest A and strongest B paid-gate children: **0/7** exact; **0/7** predicted integers prime.
- Branch-aware strongest A-to-ridge and B-to-ridge children: **0/7** exact; only **3/7** estimates pointed forward; **1/7** predicted integers prime by chance.

The 87-bit anchor supplied for a genuinely blind test was therefore **not evaluated for primality, next-prime location, or neighboring truth**. Running it after this development result would turn it into another development case rather than a fair test.

## The intended ARA statement

For an integer `N` and immediate gate child `q`, the existing PN10B coordinate is

\[
\underbrace{A_q(N)}_{\substack{\text{ARA Phase A reading}\\\text{from the 0 pole}}}
=2\frac{N\bmod q}{q},
\qquad
\underbrace{B_q(N)}_{\substack{\text{ARA Phase B reading}\\\text{from the 2 pole}}}
=2-A_q(N).
\]

Every individual child therefore satisfies pure TE-ARA closure exactly:

\[
\underbrace{A_q}_{\text{one pole}}
+
\underbrace{B_q}_{\text{opposite pole}}
=
\underbrace{2}_{\text{pure TE-ARA}}.
\]

That exact equality is true for primes and composites alike. A nontrivial two-child test must therefore retain two **different directed children**, rather than relabel the two complementary halves of one child.

The branch-aware translation retained:

\[
\underbrace{a_N}_{\substack{\text{largest immediate child}\\\text{approaching 1 from 0}}}
=
\max_{q:A_q\le1} A_q,
\qquad
\underbrace{b_N}_{\substack{\text{largest immediate child}\\\text{approaching 1 from 2}}}
=
\max_{q:A_q\ge1}(2-A_q).
\]

It then compressed those two children to

\[
\underbrace{AB(N)}_{\substack{\text{completed child whole}\\\text{compressed state}}}
=\frac{a_N+b_N}{2},
\qquad
\underbrace{BA(N)}_{\text{reflected whole}}
=2-AB(N).
\]

At the proposed ridge, `AB=BA=1`.

## The two-landmark decoder

To make “work it out relationally from two landmarks” precise without seeing target answers, PN20 used the ordinary secant intersection with the ridge. Define

\[
\underbrace{s(N)}_{\text{signed distance from ridge}}=AB(N)-1.
\]

Using `N` and `2N` as the two fixed landmarks,

\[
\underbrace{\widehat P}_{\substack{\text{predicted ridge location}\\\text{before odd rounding}}}
=
N-s(N)\frac{2N-N}{s(2N)-s(N)}.
\]

A third ARA state was evaluated only at the already-fixed prediction as a confirmation diagnostic. It was not allowed to move the prediction.

## Development results

| Anchor `N` | Branch `AB(N)` | Branch `AB(2N)` | Predicted integer | Actual next prime | Result |
|---:|---:|---:|---:|---:|:---|
| 100,000,000 | 0.704053 | 0.784806 | 466,486,663 | 100,000,007 | miss |
| 1,000,000,000 | 0.976103 | 0.742818 | no forward crossing | 1,000,000,007 | miss |
| 10,000,000,000 | 0.834639 | 0.663381 | no forward crossing | 10,000,000,019 | miss |
| 100,000,000,000 | 0.653751 | 0.642343 | no forward crossing | 100,000,000,003 | miss |
| 400,000,000,000 | 0.703787 | 0.845852 | 1,234,020,887,773 | 400,000,000,019 | miss |
| 700,000,000,000 | 0.830214 | 0.940023 | 1,782,334,652,941 | 700,000,000,009 | miss |
| 900,000,000,000 | 0.870863 | 0.640615 | no forward crossing | 900,000,000,013 | miss |

The actual prime gaps were only `3–19`. The two-child secant estimates either pointed backward or overshot by hundreds of millions to more than a trillion. This is not a near miss caused by odd rounding.

## Why the written confirmation expression collapses

If the proposed expression is read using ordinary precedence,

\[
\frac{2AB}{2}-AB+1=AB-AB+1=1.
\]

It is identically `1` for every input. If it is instead read as

\[
\frac{2AB}{2-AB}+1,
\]

then any `AB≈1` returns approximately `3`. In the first numerical-largest-child audit it returned a gap of `3` for every development anchor and hit only the one anchor whose true gap happened to be `3`.

Plainly: these expressions can confirm that a normalized identity was compressed to the ridge, but cannot recover **where on the integer line** that identity occurs.

## What failed—and what did not

This result does **not** disprove the general ARA framework, the exact prime parent ridge, or the claim that a parent can contain two rung-relative children. It rejects this narrower operational claim:

> Two selected immediate child amplitudes, compressed to `AB/BA`, plus the landmarks `N` and `2N`, are sufficient to locate the next prime in two or three evaluations.

The loss is identifiable. Many different integers map to the same normalized statement `AB=1`, `BA=1`. Once scale, gate identity, phase velocity, and the untested sibling constraints are discarded, the map is many-to-one. A unique integer cannot be reconstructed from that collapsed state.

The smallest non-collapsing replacement would have to retain at least:

1. the two selected child identities (`q_A`, `q_B`), not only their amplitudes;
2. their signed directions or local phase velocities;
3. a location-scale coordinate linking the compressed child whole back to `N`;
4. a frozen rule showing why the remaining immediate siblings cannot introduce a factor collision first.

That is still compatible with a one-rung sufficient statistic, but it is more information than the two scalar values `1` and `1`.

## Computational-cost disclosure

The final state retained two children, but selecting them inspected nine immediate siblings. That selection cost must not be described as two arithmetic steps. Likewise, producing the prime gates `q` is part of the method's cost even if `q` is hidden from the final notation.

## Relation to earlier prime tests

- **PN10/PN10B:** the exact parent `1.0` prime ridge remains valid, but assigning it requires completed factor survival through `sqrt(N)`.
- **PN15:** two gates deliberately chosen just below `sqrt(N)` necessarily approach `1+1`; this is a scale crosswalk, not a prime locator.
- **PN16:** ordered `AB` and `BA` paths differ while open, but their completed masks coincide; the full sieve representation retained more than two scalar child values.
- **PN19:** the two-parent mask result is an exact sieve reconstruction using many descendants. It is a valid control/crosswalk, not a prior test of literal two-child compression.

## Files

- `pn20_one_rung_development.py` / `PN20_ONE_RUNG_DEVELOPMENT.json` — numerical-largest-child translation.
- `pn20_directional_two_child_development.py` / `PN20_DIRECTIONAL_TWO_CHILD_DEVELOPMENT.json` — unrestricted directional extrema.
- `pn20_branch_two_child_development.py` / `PN20_BRANCH_TWO_CHILD_DEVELOPMENT.json` — branch-aware final development translation.
- `PN20_ONE_RUNG_TWO_CHILD_REPRODUCIBILITY.ipynb` — executable analytical companion.
- `validate_pn20_one_rung_two_child.py` / `PN20_ONE_RUNG_TWO_CHILD_VALIDATION.json` — independent recomputation and validation.

