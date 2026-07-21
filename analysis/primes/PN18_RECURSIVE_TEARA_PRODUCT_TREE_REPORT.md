# PN18 - Recursive TE-ARA Product Tree at 700,000,000,000

**Test ID:** `PN18/RECURSIVE-TEARA-PRODUCT-TREE/v1`  
**Date:** 21 July 2026  
**Status:** `EXACT RECURSIVE CROSSWALK / +9 SEALED BEFORE PRIMALITY / 36 OF 36 CHECKS / OPERATIONAL REPACKAGING, NOT INFORMATION OR SPEED COMPRESSION`  
**Fresh anchor:** `700,000,000,000`  
**Sealed prediction:** `700,000,000,009`

## Answer first

The recursive TE-ARA construction recovered the exact next prime from a fresh large-number anchor.

Before target primality was opened, PN18:

1. generated all `66,650` lower prime children through the square-root boundary;
2. recursively paired them into one `1,205,845`-bit child-product parent;
3. recursively paired the local p29-wheel candidates into a second parent tree;
4. used GCD as the relation between those two hierarchies; and
5. sealed the first quiet leaf at correction `+9`.

The independently checked result is

\[
\underbrace{700{,}000{,}000{,}000}_{\text{fresh anchor}}
+
\underbrace{9}_{\text{sealed recursive correction}}
=
\underbrace{700{,}000{,}000{,}009}_{\text{first prime above the anchor}}.
\]

The repaired independent receipt passed `36/36` checks. Deterministic Miller-Rabin, full trial division, direct
root-GCD reconstruction and an independently rebuilt segmented sieve all agreed. Every offset `+1` through `+8`
was composite.

The scientific qualification is equally important: the recursion is exact, but it did not compress away the
required prime information or beat established local prime methods. It is a clean hierarchical representation of
primorial/product-tree/batch-GCD mathematics in ARA language.

## Plain-language explanation

PN17 kept every lower prime child as a separate collision rhythm. PN18 asked whether those children could be paired
upward into one reusable parent without flattening them.

They can. Multiplying the children preserves which prime gates are inside the parent. A nearby number is coupled to
that parent with a greatest-common-divisor calculation:

- if the GCD is larger than 1, at least one child strikes the number, so it is composite;
- if the GCD is 1, no required child strikes it, so it is prime at this scale.

At the target, the first two p29-wheel candidates (`+1` and `+3`) had collisions. The third (`+9`) was quiet. That
is why the recursive path returned `700,000,000,009`.

The catch is that the huge product integer still contains roughly the same amount of child information. Calling it
“one number” does not make it one small coordinate. This preserves the geometry; it does not yet supply the compact
ARA correction law being sought.

## Frozen mathematics

For

\[
L=\left\lfloor\sqrt{N+65{,}535}\right\rfloor,
\]

the child parent is

\[
\underbrace{G_L}_{\text{complete lower-child parent}}
=\prod_{q\le L}q.
\]

For a candidate-tree branch `I`, the candidate parent is

\[
\underbrace{M_I}_{\text{local candidate parent}}
=\prod_{t\in I}(N+t).
\]

Their informative relation is

\[
\underbrace{R_I}_{\text{shared child content}}
=\gcd(M_I,G_L).
\]

At a single leaf,

\[
\gcd(N+t,G_L)=1
\iff
N+t\text{ has no prime factor through its square-root boundary}
\iff
N+t\text{ is prime}.
\]

This is exact because every composite number has a prime factor no larger than its square root.

## Why the branch tree cannot skip everything

For an internal branch, `R_I>1` proves only that **at least one** leaf collides. It does not prove every leaf is
composite. A branch may contain both composite and prime candidates.

PN18 therefore descended left-to-right through unresolved branches. At the target it:

- built `20,697` candidate nodes from `10,349` p29-wheel candidates;
- visited `17` GCD nodes;
- reached `3` explicit candidate leaves; and
- used no internal all-quiet shortcut before the answer.

An ordinary p29-wheel scan also needed exactly `3` candidate tests. The tree did not reduce that target count.

## Development integrity

The unchanged recursive rule reproduced all five opened controls before the fresh target was run.

| Anchor | Lower children | Correction | Predicted first prime | Result |
|---:|---:|---:|---:|:---:|
| 100,000,000 | 1,229 | +7 | 100,000,007 | exact |
| 1,000,000,000 | 3,401 | +7 | 1,000,000,007 | exact |
| 10,000,000,000 | 9,592 | +19 | 10,000,000,019 | exact |
| 100,000,000,000 | 27,293 | +3 | 100,000,000,003 | exact |
| 400,000,000,000 | 51,526 | +19 | 400,000,000,019 | exact |

The fresh sixth anchor then sealed `+9` before primality validation.

## Information-cost audit

| Representation at the fresh target | Size |
|---|---:|
| Recursive child-product root | 1,205,845 bits / 150,731 bytes |
| Same 66,650 children as uint32 values | 266,600 bytes |
| One-bit odd-number sieve through 836,660 | 52,292 bytes |
| PN17-sized uint16 collision field | 131,072 bytes |
| Full candidate-product tree, ideal integer payload | 735,283 bytes |

The root is `43.5%` smaller than a naïve uint32 child list. However, it is:

- `2.88x` the size of the one-bit odd sieve;
- `1.15x` the size of PN17's local collision field; and
- accompanied by a much larger candidate tree when the full recursive search hierarchy is retained.

Unique factorization makes the root mathematically lossless. It does not make extracting all children from the root
cheap. The practical construction still generated the children first.

## Descriptive implementation timing

Five post-target repeats on the same Python environment gave these medians:

| Method | Median seconds | Qualification |
|---|---:|---|
| Segmented sieve from scratch | 0.1153 | includes child generation and local marking |
| PN18 recursive trees from scratch | 1.8570 | includes child root and full candidate tree |
| Sequential root-GCD query | 0.00227 | child root already built |
| p29 wheel + deterministic Miller-Rabin | 0.0000888 | three candidates through +9 |

These are implementation timings, not asymptotic benchmarks. They nevertheless rule out a speed claim for the
current Python construction: PN18 was about `16x` slower than the local segmented sieve from scratch. The reusable
root makes later GCD queries cheap relative to rebuilding a sieve, but the tested Miller-Rabin scan was still much
faster for this one local answer.

## ARA interpretation

The supported ARA reading is:

\[
\underbrace{G_L}_{\substack{\text{lower-child}\\\text{connection parent}}}
+
\underbrace{M_I}_{\substack{\text{candidate}\\\text{traversal parent}}}
+
\underbrace{\gcd(G_L,M_I)}_{\substack{\text{their informative}\\\text{coupling relation}}}
\longrightarrow
\underbrace{\text{quiet or collision identity}}_{\text{local factor ridge}}.
\]

This is a strong example of the proposed `1 + 1 = 3 -> 1` recursion:

- two child identities pair into a parent at every multiplication level;
- two completed parent hierarchies meet through a relation;
- the relation classifies the local leaf as collision or quiet.

What PN18 does **not** yet supply is a small TE-ARA state such as a few phase coordinates from which `+9` follows.
The million-bit parent retained the complete child inventory. The geometry was coarse-grained structurally, but not
informationally.

## Registered endpoint verdicts

| Endpoint | Verdict |
|---|---|
| P1 - five development anchors | **Pass: 5/5 exact** |
| P2 - one fresh candidate sealed before primality | **Pass: +9** |
| P3 - candidate prime and first above anchor | **Pass** |
| P4 - root-GCD and segmented-sieve equivalence | **Pass** |
| P5 - hierarchy/query accounting | **Pass** |
| P6 - honest information-cost audit | **Pass: no genuine compression found** |
| P7 - established-method control | **Pass: product-tree/batch-GCD crosswalk** |

## Validator amendment

The originally frozen validator completed its mathematics but failed while writing the receipt: it attempted to
serialize the full million-bit child root as a decimal JSON integer, exceeding Python's 4,300-digit safety limit.
No original validation file was produced.

The original validator was retained unchanged. A hashed v1.1 amendment replaced only that giant JSON field with its
bit length, byte length and SHA-256. The sealed `+9` prediction and its hash were unchanged. The v1.1 receipt then
passed `36/36` checks. This is recorded as a post-prediction serialization repair, not hidden as a clean first run.

## Scientific conclusion

Supported:

1. the PN17 child geometry can be recursively paired without losing its exact prime ridge;
2. the resulting child parent can be reused to classify nearby candidates by GCD;
3. a fresh `+9` prediction was sealed before target primality and independently confirmed;
4. the two-parent-plus-relation form is a mathematically exact Information^3/TE-ARA crosswalk here.

Not supported:

1. that the complete child web has been reduced to a small ARA coordinate;
2. that the product root contains less information than efficient established sieve representations;
3. that the candidate tree skips the ordinary local candidate work;
4. that the current method is faster than segmented sieving or standard primality tests;
5. that this arithmetic crosswalk proves ARA's universal fractal claim.

The most accurate concise result is:

> PN18 recursively paired the full lower-prime child inventory into a product parent and sealed +9 as the first
> quiet GCD ridge above 700,000,000,000 before target primality was checked. Independent validation confirmed
> 700,000,000,009 as the first prime above the anchor. The recursion is exact and ARA-shaped, but its million-bit
> parent and candidate tree repackage established product-tree/sieve information rather than compressing or
> accelerating it.

## Files

- `PN18_RECURSIVE_TEARA_PRODUCT_TREE_PROTOCOL_v1_FROZEN.md`
- `PN18_TARGET_FREEZE_MANIFEST.json`
- `pn18_recursive_teara_product_tree.py`
- `PN18_RECURSIVE_TEARA_PRODUCT_TREE_PREDICTION.json`
- `PN18_TARGET_CHILD_PRODUCT_ROOT.bin`
- `validate_pn18_recursive_teara_product_tree.py` (original frozen validator)
- `PN18_VALIDATOR_SERIALIZATION_AMENDMENT.json`
- `validate_pn18_recursive_teara_product_tree_v1_1.py`
- `PN18_RECURSIVE_TEARA_PRODUCT_TREE_VALIDATION.json`
- `pn18_cost_audit.py`
- `PN18_COST_AUDIT.json`
