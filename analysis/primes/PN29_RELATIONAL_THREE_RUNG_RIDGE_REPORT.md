# PN29 relational three-rung ridge — result

> **Interpretive amendment, 22 July 2026:** PN29 kept all child-pair orientations fixed and therefore omitted the ARA singularity flips later clarified by the user. Its arithmetic and result remain valid for that static representation, but it is not a complete reversible-ARA test. See `PN29_DYNAMIC_FLIP_AMENDMENT_2026-07-22.md` and the corrected fresh test `PN30_DYNAMIC_RELATIONAL_FLIP_REPORT.md`.

**Date:** 22 July 2026  
**Status:** **partial / child-filter support**  
**Scope:** 493 odd integers from 15 through 999; no sieve

## Plain-language result

This test kept every operation inside the dimensionless ARA coordinate system:

1. Convert each child pair `(1,13)`, `(3,11)`, `(5,9)` to its own total-2 coordinate.
2. Average the three pair coordinates to obtain the child rung \(R_0\).
3. Move upward by halving the displacement from 1.0 at each rung:

\[
R_1=1+\frac{R_0-1}{2},
\qquad
R_2=1+\frac{R_0-1}{4}.
\]

No coordinate was added to a raw integer, no rounding was used, and no number-line offset was introduced.

For 35:

\[
1.0343776\rightarrow1.0171888\rightarrow1.0085944.
\]

The calculation was frozen for every odd integer below 1,000 before primality was determined independently by direct trial division.

## Overall comparison

| Population | Count | Mean upper-rung distance | Median distance |
|---|---:|---:|---:|
| Primes | 162 | 0.010884 | 0.006119 |
| Odd composites | 331 | 0.078056 | 0.073838 |

The rank AUC was **0.8635**: a randomly chosen prime was closer to the ridge than a randomly chosen odd composite about 86% of the time. The one-sided permutation result was `p=0.00010`.

That looks strong until the child-factor control is applied.

## Unresolved-composite control

There were 59 composites not divisible by any declared nontrivial child label `{3,5,9,11,13}`.

| Population | Mean upper-rung distance | Median distance |
|---|---:|---:|
| Primes | 0.010884 | 0.006119 |
| Unresolved composites | 0.006152 | 0.005961 |

Against these composites, primes were actually slightly **farther** from the ridge:

- AUC: **0.4442**;
- one-sided p-value for primes being closer: **0.9947**.

## Interpretation

The overall ridge signal is real arithmetic structure, but it is produced by the declared child-factor web. Numbers divisible by 3, 5, 9, 11, or 13 often move away from the combined ridge, and most of those numbers are composite. Primes above 13 necessarily avoid those divisors, so they occupy the unresolved region.

Once composites that also avoid those child divisors are used as the control, the prime-specific ridge advantage disappears.

Therefore the supported statement is:

> The relational three-child coordinate detects whether a number is coupled to the declared small child factors.

The unsupported statement is:

> The coordinate identifies primes independently of those child factors.

The upward `/2` then `/2` transport is internally consistent and preserves the child ordering without mixing ARA units with integers. However, because

\[
D_2=\frac{D_0}{4},
\]

it cannot add new classification information; it only expresses the same child relation at a coarser rung.

This is why the test is recorded as **partial / child-filter support**, not prime-ridge confirmation.

## Audit trail

- Frozen protocol: `PN29_RELATIONAL_THREE_RUNG_RIDGE_PROTOCOL_v1_FROZEN.md`
- Frozen coordinates: `PN29_RELATIONAL_THREE_RUNG_FROZEN_COORDINATES.csv`
- Scored values: `PN29_RELATIONAL_THREE_RUNG_SCORED.csv`
- Results: `PN29_RELATIONAL_THREE_RUNG_RESULTS.json`
- Independent validation: `PN29_RELATIONAL_THREE_RUNG_VALIDATION.json`
- Executed notebook: `PN29_RELATIONAL_THREE_RUNG_RIDGE_REPRODUCIBILITY.ipynb`
