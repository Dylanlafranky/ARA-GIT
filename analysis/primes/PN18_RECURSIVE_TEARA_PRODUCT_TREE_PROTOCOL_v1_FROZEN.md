# PN18 recursive TE-ARA product-tree protocol

**Test ID:** `PN18/RECURSIVE-TEARA-PRODUCT-TREE/v1`  
**Frozen:** 21 July 2026, Australia/Brisbane  
**Fresh target anchor:** `700,000,000,000`  
**Local window:** `65,536` integers beginning at the anchor  
**Status at freeze:** no PN18 target candidate or nearby target prime has been calculated  
**Data source:** deterministic integer arithmetic; no external prime table  
**Protected material:** the p31 full primorial wheel and unrelated R12 prime-gap target remain unopened

## Question

PN17 found the exact first prime above an arbitrary large anchor by retaining 51,526 separate lower-child phase
lanes. It was an exact ARA crosswalk of a segmented sieve, but a simple averaged Phase A/Phase B coordinate erased
the location.

PN18 tests the next proposal:

> Can the lower children be recursively paired into a reusable whole, and can that whole locate the first quiet
> local ridge without constructing a 65,536-position collision field?

This is a test of **lossless hierarchical compression**, not scalar averaging.

## Frozen construction

Let the anchor be `N`, the fixed window be `W=65,536`, and

\[
L=\left\lfloor\sqrt{N+W-1}\right\rfloor.
\]

### Child hierarchy

Generate every prime child `q <= L` and pair adjacent children recursively by multiplication. The parent at the top
is

\[
\underbrace{G_L}_{\substack{\text{complete lower-child parent}\\
\text{one reusable integer}}}
=
\prod_{q\le L}q.
\]

Unique factorization means the root retains the complete set of child gates mathematically. It does **not** mean
that recovering the individual children from the root is computationally cheap.

### Candidate hierarchy

The local candidates are first restricted by the fixed p29 wheel:

\[
\mathcal T_N=
\left\{t\in\{1,\ldots,W-1\}:\gcd(N+t,29\#)=1\right\}.
\]

No p31 wheel is permitted. Pair adjacent candidate integers recursively. For a branch `I`, its parent is

\[
\underbrace{M_I}_{\text{candidate-branch parent}}
=
\prod_{t\in I}(N+t).
\]

### The informative third

Couple a candidate branch to the lower-child parent with

\[
\underbrace{R_I}_{\substack{\text{shared child relation}\\
\text{between the two parents}}}
=
\gcd(M_I,G_L).
\]

The exact meanings are:

- `R_I=1`: every candidate in the branch is quiet with respect to every child through the square-root boundary;
- `R_I>1`: at least one candidate in the branch has a child collision;
- at a single candidate leaf, `gcd(N+t,G_L)=1` if and only if the candidate is prime for this block.

Because `R_I>1` does not say whether **all** leaves collide, the search must descend left-to-right until it reaches
the first quiet leaf. It may not skip an unresolved mixed branch.

The sealed correction is

\[
\Delta_{\rm PN18}(N)
=
\min\left\{t\in\mathcal T_N:\gcd(N+t,G_L)=1\right\}.
\]

The predicted integer is `N + Delta_PN18`.

## ARA reading

At every tree level, two completed children are coupled into one parent. The two top-level objects are:

1. the accumulated lower-child connection hierarchy `G_L`;
2. the local candidate/traversal hierarchy `M_I`.

Their GCD relation `R_I` is the informative third. A quiet leaf is the factor-ridge identity at which no lower
connection gate reaches the candidate. This is the same exact ridge used by PN17, approached through recursive
parents rather than a flat collision field.

## Development integrity

Before the fresh target, the unchanged construction is checked on these already-opened anchors:

- `100,000,000 -> 100,000,007`;
- `1,000,000,000 -> 1,000,000,007`;
- `10,000,000,000 -> 10,000,000,019`;
- `100,000,000,000 -> 100,000,000,003`;
- `400,000,000,000 -> 400,000,000,019` (the opened PN17 anchor).

These labels are integrity controls only. No parameter is fitted from them.

## Separation and freeze

1. Freeze this protocol.
2. Freeze and hash the primary builder and independent validator.
3. Freeze the fresh anchor and window in a manifest before any PN18 target output exists.
4. Run the primary builder. It may create lower prime children and use product/GCD arithmetic, but it must not call
   a target primality-test function or read a nearby-target prime label.
5. Seal and hash its single predicted integer.
6. Only then run the independently written validator, including deterministic Miller-Rabin, trial division and a
   separately generated segmented-sieve reconstruction.

## Registered endpoints

### P1 - development integrity

All five opened anchors must reproduce their established first-prime corrections.

### P2 - fresh one-shot candidate

The primary builder emits exactly one first-quiet candidate for `700,000,000,000`, before target primality is
opened.

### P3 - independent target truth

The candidate must independently be prime, and every integer between the anchor and candidate must be composite.

### P4 - exact equivalence

Independent segmented-sieve and direct GCD reconstruction must return the same correction.

### P5 - hierarchy and query accounting

Record child count, tree levels, root bit length and byte length, candidate-tree nodes, visited GCD nodes, visited
candidate leaves, odd-scan count and p29-wheel count.

### P6 - information-cost audit

Compare the root product with:

- the child list stored as unsigned 32-bit integers;
- a one-bit odd-number sieve through `L`;
- PN17's 131,072-byte collision field; and
- transient candidate-product-tree size.

The root is not called a genuine information reduction merely because one integer replaces a list. Its bit length
and construction cost count.

### P7 - established-method control

State explicitly that the mathematics is a primorial/product-tree/batch-GCD primality construction. A complete pass
does not establish a new primality theorem or faster asymptotic algorithm.

## Allowed result classes

- **Exact recursive crosswalk:** P1-P7 pass. The hierarchy preserves the PN17 ridge and seals the fresh result, but
  remains an established product-tree/GCD construction.
- **Operational compression only:** exact result, fewer explicit phase lanes or no local collision mask, but no
  reduction in total information or computation.
- **Target failure:** development passes but the fresh candidate is composite or not the first prime.
- **Implementation failure:** any freeze, hash, equivalence or reconstruction check fails.

The universal ARA fractal claim is not decided by one arithmetic result. PN18 tests one precise recursive
coarse-graining proposal.
