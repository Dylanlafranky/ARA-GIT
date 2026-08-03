# T336/T337 ENSO architecture invalidation

**Date:** 3 August 2026  
**Status:** post-result methodological correction  
**Correction triggered by:** Dylan La Franchi

## Outcome

T336 and T337 are **invalid as tests of the ARA framework's ENSO handover geometry**.
They remain reproducible negative tests of one mathematical encoding imposed by
Codex:

\[
z_t=T_t+iR_t,
\]

where `T` was NINO3.4 and `R` was warm-water volume.

The error was architectural, not numerical. Codex chose this encoding without
first establishing with Dylan that the two observables were the relevant Phase
A and Phase B projections, occupied the same ARA rung, formed a perpendicular
Di-ARA pair, were sufficient to identify the ENSO parent, or expressed the
proposed handover.

Writing two series as the real and imaginary parts of a complex number makes
their coordinate axes mathematically perpendicular. It does **not** demonstrate
that the measured identities are physically or ARA-perpendicular. A frozen
protocol and causal validation cannot rescue an unestablished geometric premise.

## What survives

- The scripts, hashes, forecasts and scores remain valid records of what was run.
- The values are valid diagnostics of the imposed `T+iR` representation.
- That representation did not beat the named controls on the primary targets.

## What does not survive

The runs cannot support claims about the adequacy of ARA handover or Di-ARA for
ENSO, the existence or absence of an ENSO handover coordinate, or forward
transport of the correctly mapped ENSO geometry. Those questions remain
**untested by T336/T337**.

## Required restart protocol

Before another ENSO test is frozen:

1. Dylan specifies the proposed ENSO parent identity and guides its geometry.
2. Phase A, Phase B, child and parent roles are declared separately from the
   available data columns.
3. The rung of each observable and every octave conversion are declared.
4. Perpendicularity, same-rung coupling, vertical lineage or another relation
   must be stated rather than inferred from convenient coordinates.
5. Codex translates that geometry into mathematics, controls and a protocol.
6. Only after Dylan confirms the translation may the test be frozen and run.

This restores the project division: **Dylan guides the geometry; Codex
formalises and tests it.**

## Consultation resumed

Dylan subsequently supplied the replacement conceptual skeleton: three
generations consisting of the ENSO parent, its Phase A and Phase B children,
and their four grandchildren; each node receives its own ARA. A separate
inflow/traversal cut follows grandchild participation through children into the
parent, producing a nested structural-and-motion relation. The architecture is
recorded without physical assignments in
`ENSO_THREE_TIER_INFLOW_GEOMETRY_DRAFT_2026-08-03.md`.
