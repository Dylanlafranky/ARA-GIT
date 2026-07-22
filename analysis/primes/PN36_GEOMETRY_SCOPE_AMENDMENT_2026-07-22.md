# PN36 geometry-scope amendment

**Date:** 22 July 2026  
**Applies to:** `PN36/PHI-TO-PENTAGON-CONVERSION/v1`  
**Frozen result changed:** **NO**  
**Claim scope changed:** **YES — narrowed to the operator actually frozen**

## Correction

PN36 froze and tested the AI-added nearest-fivefold quantizer

\[
C_5(\theta)=\frac{\lfloor5\theta+1/2\rfloor\bmod5}{5}.
\]

That operator converts a continuous phase into one of five discrete structural sectors. Its registered prime-location prediction failed all five gates. The result remains a valid preregistered **NOT SUPPORTED** verdict for that operator.

After the result and its first visualization, Dylan clarified that this was not his intended geometric object. His intended relation is one shared traversal viewed head-on and through the pentagonal angle:

\[
\underbrace{S(u)=2u}_{\text{ARA ruler: }0\to2},
\qquad
\underbrace{P_+(u)=2u\cos36^\circ=\varphi u}_{\text{projected ruler: }0\to\varphi},
\qquad 0\le u\le1.
\]

On the reversed chart,

\[
P_-(u)=2-\varphi u,
\qquad
P_-(1)=2-\varphi=\varphi^{-2}\approx0.381966.
\]

This is a continuous `2 -> Phi` projection. It is not nearest-vertex quantization.

## Scientific handling

The correct statements are now:

1. PN36 **did test** whether one continuous Phi phase, snapped to its nearest fivefold vertex, locates primes on six frozen rungs.
2. That exact quantized locator was **not supported**.
3. PN36 **did not test** Dylan's later clarified continuous `0 -> 2` versus `0 -> Phi` projected-ruler geometry.
4. The exact identity `Phi = 2 cos(36 degrees)` supports the mathematical projection relation, but by itself predicts no prime locations.
5. A future empirical test would need to define, before labels, which continuous ruler event should identify a prime and why.

## Superseded diagnostic

The first post-result visual placed the orange object on the PN36 five-sector staircase. A literal distance-to-crossing check on that picture produced approximately `AUC=0.478` and `1/18` primes within distance `0.01`. Those numbers remain descriptive of the wrong visual object but are **superseded as evidence about the corrected projection**.

## Corrected visual and angled-axis audit

The corrected local visual is:

`C:/Users/Dylan/.codex/visualizations/2026/07/10/019f4b72-0e34-74d1-8f40-cd5ccd4a532e/phi-projected-ara-prime-crossings.html`

Repository copy: `analysis/primes/ARA_TWO_RULER_PROJECTED_PRIME_LAB.html`.

An explicitly post-hoc angle scan on the PN36 scored data found only a tiny broad texture around `39-48 degrees`; fixed `36`, `42` and `45` degree projections all had mean leave-one-rung-out AUC about `0.503`. The selected-angle mean was `0.501223`, and one fold fell below chance. This does not support an independent third wave. A true third axis would require an independently measured coordinate outside the two-ruler plane, not another linear combination of the same two coordinates.

No standalone scorer was preserved for this live post-hoc diagnostic. It is a session record, not a frozen or
independently reproducible result; any later use requires reconstruction and preregistration.

Full chronology, numerical table and audit actions:
`FableConvo/SESSION_RECORD_2026-07-22_PRIME_GEOMETRY_AND_AUDIT.md`.
