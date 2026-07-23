# PN42 — Prime as a Completed TE-ARA Singularity

**Date:** 2026-07-23  
**Status:** Post-PN41 conceptual clarification; untested forward algorithm  
**Purpose:** Preserve the precise unresolved operation before parking the prime thread

## Dylan's correction

A prime should not be flattened into only a `1.0` ridge. The ridge and singularity can be two directional readings
of the same cross-rung event:

- laterally, the completed parent boundary appears as the `1.0` contact ridge between spheres;
- vertically, completion is the parent's `2 -> 0` singularity crossing;
- after the crossing, the prime becomes a new `0` source or factor gate for subsequent integers.

The proposed sequence is:

\[
\underbrace{\text{lower factor-wave accumulation}}_{\text{children filling the parent}}
\longrightarrow
\underbrace{\mathrm{TE\!\text{-}\!ARA}=2}_{\text{completed multiplicative sphere}}
\longrightarrow
\underbrace{\text{prime}}_{\substack{\text{ridge viewed laterally}\\
\text{singularity viewed vertically}}}
\longrightarrow
\underbrace{\text{new factor source}}_{\text{next-rung }0}.
\]

The asymmetric children underneath a prime do not need to read `1.0` individually. Their coarse-grained parent is
the object proposed to complete its TE-ARA capacity.

## Proposed forward calculation

For a chosen integer `N`, define a label-free ARA phase `a(N)` and a local geometric rate `v(N)`. Then the nearest
terminal singularity would be estimated by

\[
\boxed{
\widehat p
=
N+\frac{2-a(N)}{v(N)}
}
\]

where:

- `a(N)` is the current number's position on its multiplicative ARA diameter;
- `2-a(N)` is the remaining distance to the completed-sphere singularity;
- `v(N)` converts one integer step into local ARA motion;
- `p-hat` is the predicted integer location of the `2 -> 0` crossing.

The reversed orientation may place the active terminal at `0`; pole labels must therefore be frozen before each
test.

## Exact unresolved bridge

The hypothesis becomes computationally new only if `a(N)` and `v(N)` can be calculated:

1. from `N` and independently defined local child relations;
2. without knowing the next prime;
3. without testing every prime factor through `sqrt(N)`;
4. without embedding a sieve, primality test, or nearby-prime label in the coordinate; and
5. with less work than the established comparison methods.

Dylan proposes that only the dominant Phase-A and Phase-B child relations should be required because the geometry
is fractal. Their exact label-free selection rule remains undefined. That selection rule, not another large prime
scan, is the next mathematical problem.

## Relation to completed tests

- PN7B found a near-`1.0` population parent while most individual gap children were asymmetric.
- PN37 opened the full factor-child field and confirmed that parent cancellation can conceal broad child
  asymmetry.
- PN41 constructed an exact nearest-survivor thalweg that terminates at the first prime, but its registered local
  Phi split was not supported and its exact endpoint still required complete factor-gate arithmetic.
- PN41's replicated one-third local handover describes an internal route; it is not identified here as the terminal
  prime singularity.

These results motivate the distinction but do not prove the new forward rule.

## Later MX10 cross-domain correspondence

MX10 independently exposed the same child-to-parent closure form on a physical-field axis. Increasing spatial block
width moved upward from resolved electric-field children into one coarser parent. Opposed child orientations became
hidden in the parent account, while the parent did not need to reverse its own signed A/B orientation.

This matches the prime distinction proposed here:

- **lateral/intra-rung:** a retained A/B orientation can cross and flip;
- **vertical/inter-rung:** multiple children close into one parent identity, making their separate differences
  unrecoverable from the parent alone.

Corollary 8.5a now formalises the second as a non-injective child-to-parent ARA singularity. This strengthens the
cross-domain mathematical correspondence. It does not supply the missing label-free \(a(N)\), \(v(N)\), or dominant
child rule and therefore does not change PN42's computational status.

## Security boundary

Locating or generating primes is not itself a cryptographic break. A security-relevant result would require a
verified shortcut for recovering hidden factors of arbitrary cryptographic semiprimes, solving an equivalent hard
problem, or deriving private keys from public information. PN42 currently supplies none of those capabilities.

## Resume condition

Keep the prime thread parked until there is a precise, label-free proposal for both:

\[
a(N)\quad\text{and}\quad v(N),
\]

including the rule that selects the two dominant children. Freeze that rule before evaluating nearby prime labels.
