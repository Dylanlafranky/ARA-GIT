# PN37 — Full Child ARA and Child-Level Phi Protocol v1 (Frozen)

**Protocol date:** 2026-07-23 (Australia/Brisbane)  
**Status:** method-locked on an already opened prime interval; post-hoc structural test, not a blind prediction  
**Question:** does the parent-level ridge conceal asymmetric lower factor-gate children, and is Phi preferentially occupied at that child grain?

## Scope

Use the complete PN10B target interval

\[
[4{,}000{,}000{,}000,\;4{,}001{,}000{,}000).
\]

Retain every prime `p` in that interval. For each `p`, retain **every** lower prime gate

\[
q\leq\sqrt p.
\]

This differs from PN10B's registered nine-paid-gate proxy. PN37 opens the complete factor-child field for each prime. The raw child-pair table is not written because it would contain hundreds of millions of rows; the deterministic script writes lossless count reconciliations plus per-parent and per-gate summaries and can regenerate any individual child relation.

## Native child ARA definition

For each parent prime `p` and lower gate `q`, define

\[
\underbrace{A_q(p)}_{\substack{\text{phase since the previous}\\\text{multiple of child gate }q}}
=2\frac{p\bmod q}{q},
\qquad
\underbrace{B_q(p)}_{\substack{\text{phase until the next}\\\text{multiple of child gate }q}}
=2-A_q(p).
\]

Every child therefore has exact local TE-ARA closure

\[
A_q(p)+B_q(p)=2.
\]

Because `p` is prime and `q< p`, `p mod q` is never zero. A child can nevertheless be close to either singularity, the 1.0 ridge, or another declared landmark.

## Parent summaries

For every prime `p`, record:

- number of complete lower children `q <= sqrt(p)`;
- child centroid `mean_q A_q(p)`;
- mean child distance from the ridge `mean_q |A_q(p)-1|`;
- mean and minimum distance to the Phi landmark pair;
- number and share of children occupying the nearest available Phi residue pair.

These are summaries of the full child vector, not replacements for it. A centroid near 1.0 may be produced by cancellation among strongly asymmetric children.

## Gate summaries

For every lower prime gate `q`, record:

- eligible parent count;
- mean `A_q`, mean ridge distance, and mean Phi-pair distance;
- observed occupancy of the nearest available Phi residue pair;
- the exact uniform-nonzero-residue expectation for that gate;
- corresponding quantities for the matched landmark controls below.

## Child-level Phi test

Let

\[
\phi_R=\phi\approx1.61803398875,
\qquad
\phi_L=2-\phi\approx0.38196601125.
\]

Exact hits are impossible because every `A_q(p)` is rational while Phi is irrational. For each gate `q`, select the valid nonzero residue nearest each of the two Phi targets. The primary Phi occupancy statistic is

\[
\frac{\text{observed prime-child hits on those residues}}
{\text{expected hits under uniform nonzero residues modulo }q}.
\]

Also compare the observed mean continuous distance to the Phi pair with its exact discrete nonzero-residue expectation at the same gate.

### Matched landmark controls

Apply the identical two-sided rule to these predeclared mirror pairs:

- `quarter`: `(0.25, 1.75)`;
- `third`: `(1/3, 5/3)`;
- `half`: `(0.5, 1.5)`;
- `two_thirds`: `(2/3, 4/3)`.

Phi is not promoted merely for being close to some child readings. A child-level Phi preference requires a material null-adjusted effect that is stronger and more stable than these equally sized controls.

## Weighting

Report both:

1. **child-pair weighted:** every `(p,q)` relation has equal weight;
2. **gate balanced:** every gate `q` has equal weight after its own observed-minus-expected effect is calculated.

Gate `q=2` is retained for completeness but excluded from the primary Phi comparison because every prime in the interval is odd and its only nonzero residue gives `A=1`; it cannot distinguish any two-sided interior landmark.

## Interpretation gates

- A pooled or median parent centroid near 1.0 supports parent-level cancellation but does not imply quiet children.
- Broad child asymmetry supports decompression of the parent identity, not prime prediction by itself.
- Phi is `not supported` if its null-adjusted occupancy/distance is negligible, unstable across gates, or no stronger than matched landmarks.
- Phi is `descriptively supported at child level` only if both occupancy and continuous-distance comparisons are directionally favorable and outperform all four controls. This still remains post-hoc until transferred unchanged to an untouched interval.
- No result may be described as a computational advantage over established prime methods; generating the full child field is a factor-sieve decomposition.

## Required validation

The run must verify:

1. all retained parents are prime by the complete segmented least-factor source;
2. every child gate satisfies `q <= sqrt(p)`;
3. every remainder is nonzero;
4. every sampled or streamed closure satisfies `A+B=2` to floating tolerance;
5. summed per-parent child counts equal summed per-gate counts and the global pair total;
6. Phi hit totals reconcile between parent and gate accumulators;
7. every output row count matches its declared population.

