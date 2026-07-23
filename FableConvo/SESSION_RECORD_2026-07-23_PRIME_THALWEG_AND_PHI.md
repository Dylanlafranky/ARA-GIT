# Session Record — Prime Thalweg and Phi

**Date:** 2026-07-23  
**Thread:** Prime infrastructure, valley geometry, and a direct Phi test

## Dylan's geometric proposal

Dylan reframed the prime child-band picture as a wave-pool or river terrain. Composite factor collisions provide
the surrounding ridges. The fast or least-obstructed route should run through a valley or thalweg, hand over into a
larger channel, and eventually arrive at a prime. His intuition was that the missing handover geometry might be
Phi-shaped.

This was treated as a serious but bounded hypothesis, not dismissed as “Phi hunting” and not promoted from visual
resemblance alone.

## Translation into a frozen test

The operational thalweg was defined through natural factor gates. At each gate that killed the current candidate,
the old channel's position `U` was measured inside its new surviving interval `[L,R]`:

\[
f=(U-L)/(R-L),\qquad m=\min(f,1-f).
\]

The mirrored golden landmark `2-phi` was preregistered against quarter, third, two-fifths, and half controls. The
test used two fresh million-integer targets and 1,000 deterministic anchors per target.

## Result

The river metaphor exposed a real exact path, but its local handover was not Phi-shaped in this coordinate.

- Target A: folded mean `0.330044`, median `1/3`, optimum `0.334`.
- Target B: folded mean `0.330008`, median `1/3`, optimum `0.334`.
- Phi was farther from the handovers than the `1/3` control in both targets, with both paired-bootstrap intervals
  wholly on the losing side.
- All frozen Phi-support gates failed.

The unexpected replicated landmark was one third. This is compatible with Dylan's triangle / `Information^3`
language as an ARA interpretation, but it is not yet evidence for an ARA-specific mechanism because discrete
survivor-gap arithmetic can naturally generate rational splits.

## Important distinction retained

The negative result applies only to the frozen **local interval split**. It does not test a golden curvature of the
whole thalweg, a cross-rung drift, or another independently defined temporal handover. Those cannot replace PN41
after reveal; any such proposal requires a new frozen test.

The exact prime endpoint remains established sieve arithmetic expressed through a new terrain/path lens. PN41 does
not establish a faster prime algorithm.

## Durable references

- `analysis/primes/PN41_PRIME_THALWEG_PHI_REPORT_2026-07-23.md`
- `analysis/primes/PN41_PRIME_THALWEG_PHI_PROTOCOL_v1_FROZEN.md`
- `analysis/primes/pn41_prime_thalweg_phi.py`
- `analysis/primes/PN41_PRIME_THALWEG_PHI_VALIDATION.json`

## Final clarification before parking

Dylan identified the likely scale error behind calling a prime only a ridge. His proposed object is the completed
multiplicative TE-ARA sphere: the boundary reads as `1.0` laterally but as the `2 -> 0` singularity vertically, and
the prime then becomes a new `0`-source gate. The desired algorithm is therefore to calculate a nearby number's ARA
phase and its distance to that singularity, rather than search for a ridge label.

This was preserved without treating it as a completed algorithm. The missing definitions are the label-free phase
`a(N)`, local scale `v(N)`, and an independent rule selecting the two dominant children. See
`analysis/primes/PN42_PRIME_AS_TEARA_SINGULARITY_NOTE_2026-07-23.md`.
