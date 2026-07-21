# PN17 one-shot local ARA ridge protocol

**Test ID:** `PN17/ONE-SHOT-LOCAL-INVERSE-RIDGE/v1`  
**Frozen:** 21 July 2026, Australia/Brisbane  
**Target anchor:** `400,000,000,000`  
**Status at freeze:** no PN17 target candidate or nearby target prime has been calculated  
**Data source:** deterministic integer arithmetic; no external prime table  
**Protected material:** the p31 full primorial wheel and the unrelated R12 prime-gap target remain unopened

## Dylan's proposed direction

Start at an arbitrary number near the desired scale, decompress that number into its lower-rung children, compare
the observed child geometry with the pure prime ridge, and calculate one local correction. Do not generate the prime
sequence upward from 2 and do not supply the desired next prime as a gate.

The target search diameter is conceptually

\[
[0,2N_0]
\]

with the chosen anchor `N_0` at the `1.0` reference. The actual numerical calculation is deliberately restricted to
one raw local block of `65,536` integers beginning at `N_0`; failure to find a ridge in that block is a registered
failure rather than permission to retune the window.

## Loadbearing distinction between two ridge statements

### Contact equality

Every prime node can be drawn as the contact between its incoming and outgoing prime-gap spheres. If each side is
normalized by its own diameter, both reach the contact at normalized progress `1`. This is geometric closure but it
does not preserve the two raw gap sizes.

### Raw gap equality

The stronger statement

\[
g_i^-=g_i^+
\]

is not true for most primes. Existing PN7B R11 evidence records an exact equal-gap share of `2.0937%`. PN17 will
therefore not use unknown outgoing prime gaps to construct its prediction. The equal-gap reflection is retained as a
falsification/control, not silently promoted to the target rule.

### Quiet factor ridge

The exact prime ridge tested here is instead the factor-sphere boundary:

\[
\text{candidate }m\text{ is prime}
\iff
\text{no prime child }q\leq\sqrt m\text{ collides with }m.
\]

This is the established square-root completeness rule in ARA child coordinates.

## Child decomposition available before the target label

For every prime child gate

\[
q\leq\sqrt{N_0+65{,}535},
\]

the anchor supplies the complete raw phase

\[
\underbrace{A_q(N_0)}_{\substack{\text{distance since}\
\text{the previous child collision}}}
=
2\frac{N_0\bmod q}{q},
\qquad
\underbrace{B_q(N_0)}_{\substack{\text{distance to}\
\text{the next child collision}}}
=2-A_q(N_0).
\]

Thus every child obeys pure local TE-ARA closure `A_q+B_q=2`. Crucially, PN17 retains the complete vector of child
identities and phases. It does not average them into one scalar before locating the ridge.

For offset `t`, define the child collision field

\[
\underbrace{C_{N_0}(t)}_{\substack{\text{number of lower children}\
\text{colliding at the offset}}}
=
\sum_{q\leq\sqrt{N_0+65{,}535}}
\mathbf 1[(N_0+t)\bmod q=0].
\]

The frozen one-shot correction is

\[
\underbrace{\Delta_{\rm ARA}(N_0)}_{\substack{\text{signed local correction}\
\text{from the anchor to a quiet ridge}}}
=
\min\{t\in\{1,\ldots,65{,}535\}:C_{N_0}(t)=0\}.
\]

The predicted integer is

\[
\widehat p=N_0+\Delta_{\rm ARA}(N_0).
\]

This uses the whole child geometry in one local calculation. It performs no primality-labelled scan and consumes no
known prime above the child ceiling.

## Development anchors

The identical rule is first reconstructed at four already-opened decimal anchors:

- `100,000,000`;
- `1,000,000,000`;
- `10,000,000,000`;
- `100,000,000,000`.

Their nearby prime labels are development-only integrity controls. No parameter is fitted from them.

## Target separation

1. Freeze this protocol.
2. Freeze and hash the primary builder and independent validator.
3. Run the primary builder. It may generate only the lower child inventory and local collision field; it must not
   call a primality-test function for the predicted target.
4. Hash the sealed prediction packet.
5. Only then run the independent validator, which uses a separately written deterministic primality test and a
   separately generated child inventory.

## Frozen endpoints

### P1 — development integrity

The first zero of the collision field must equal the established next prime at all four development anchors.

### P2 — one-shot target prediction

The target builder must emit exactly one integer `p_hat` from the frozen correction without reading a nearby-prime
table or using target primality labels.

### P3 — target ridge validity

Independent validation must establish that `p_hat` is prime and that every integer strictly between `N_0` and
`p_hat` is composite. This makes it the first prime above the arbitrary anchor.

### P4 — child-vector reconstruction

The stored correction must equal an independently reconstructed local segmented-sieve correction at every position
through `p_hat`.

### P5 — baseline accounting

Record:

- odd candidates that ordinary upward scanning would test before reaching `p_hat`;
- p29-wheel candidates before reaching `p_hat`;
- the number of lower child phases used by the full-decompression method; and
- the fact that a standard segmented sieve uses the same collision mask.

PN17 may not claim a computational speed advantage if it has only renamed that standard mask.

### P6 — scalar ridge sufficiency is not assumed

`A_q+B_q=2` for each child does not by itself identify `Delta`, because normalization discards raw child period and
phase. PN17 tests the complete child vector. A future scalar TE-ARA shortcut requires an independently frozen
aggregation/coupling law and must beat the full-vector and standard baselines on untouched anchors.

## Equal-gap falsification control

Using the already-opened R11 actual-prime gap record, report the past-only equality predictor

\[
\widehat g_i^+=g_i^-.
\]

This is the simplest literal conversion of “the next prime has equal incoming and outgoing raw Phase A/B gaps.” Its
exact-hit rate, absolute error and near-hit shares are descriptive controls. They cannot be used to alter the target
formula.

## Allowed result classes

- **Exact local crosswalk:** P1-P5 pass. The method computes the first local prime in one fully decompressed child
  field, while remaining algebraically the established segmented sieve.
- **Target failure:** development passes but the target candidate is composite or not the first prime.
- **Implementation failure:** any hash, reconstruction or separation condition fails.

Even a complete pass does not establish that a scalar TE-ARA imbalance alone predicts prime distance, a faster prime
algorithm, or the universal fractal claim.
