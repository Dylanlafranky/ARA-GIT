# T433B — Full event-centred Irrationality Di-ARA method bridge

**Status:** frozen after T433A exposed a window-grain problem and before T433B scoring  
**Date:** 26 August 2026 (Australia/Brisbane)

## Reason for the registered follow-up

T433A used the common interval shared by all five cuts, ending at `-0.032 s`.
That endpoint was imposed by the secondary T430 cumulative-budget history even
though T430 was explicitly excluded from the primary verdict. It therefore
tested a pre-handover bridge rather than the requested event-centred
Irrationality Di-ARA handover.

T433A remains unchanged. T433B corrects the population/window mismatch without
changing its bridge metric, controls, seed, FDR rule, event identities, or four
primary method families.

## Frozen identity and window

- One binary-black-hole event is one measured identity.
- H1/L1 are detector views, not the two black holes.
- Events: `GW170104`, `GW170608`, `GW170809`, `GW170814`, `GW170818`.
- Primary methods: T427 direct, T428 paired, T429 separated, T432 dynamic.
- Common interval: `-0.496 s` to `+0.245 s` relative to event GPS.
- T430 is omitted because its cumulative history has no post-event coverage.
- T431 remains omitted as non-independent of the T432 coordinate family.

## Frozen bridge and controls

Use the T433A orientation-invariant bridge unchanged:

1. centred seven-frame median per coordinate;
2. within-event ranked trajectory speed;
3. maximum rank association over lags `-64` to `+64 ms`;
4. Dice overlap of top-20% trajectory-speed landmarks at the selected lag;
5. derivative orientation and ridge-time separation as descriptive channels;
6. 2,000 null replicates combining wrong-event derangement and a circular
   shift of at least 128 ms;
7. Benjamini-Hochberg FDR over the six method pairs separately for association
   and landmark overlap.

A method pair passes only when both q-values are `<=0.05`. A broad bridge
requires at least three of six pairs.

## Interpretation

This is still an exploratory reuse of already opened histories. A pass shows a
reproducible bridge among different projections of the same detector event; it
does not identify literal internal components, prove a singularity flip, or
separate ARA organization from all shared source-morphology explanations.

