# PN11 Phi vertical-handover protocol — v2 target freeze

**Test ID:** `PN11/PHI-VERTICAL-HANDOVER/v2`  
**Declared:** 21 July 2026, after the registered development run and before opening the target  
**Base protocol:** `PN11_PHI_VERTICAL_HANDOVER_PROTOCOL.md`  
**Reason for version:** development exposed an out-of-support hazard-window rule; no target value was inspected  
**Target:** unchanged at `[10,000,000,11,000,000)`

All identities, coordinates, populations, target boundaries, landmarks, tolerances, bootstrap settings, P1, P2, P4,
rating vocabulary and interpretation fences in v1 remain binding. Only P3 and its adequacy clause are replaced below.

## Frozen P3 replacement

A landmark's `+-0.025` hazard window is eligible for comparison when it contains at least 30 transition events.
Landmarks with fewer than 30 events are reported as outside adequate support and are not assigned an artificial zero
hazard rank.

### P3 — Phi transition-hazard advantage, v2

On the full fresh target and on each fixed half separately:

1. Phi's window contains at least 30 transition events;
2. at least two frozen rival windows also contain at least 30 transition events;
3. Phi has the highest transition hazard among those eligible windows.

If conditions 1 or 2 fail, P3 is `INCONCLUSIVE`. If they hold and another eligible landmark has a higher hazard, P3
fails. Ties including Phi do not pass.

## Why this is not outcome tuning

Development showed zero exposures at some registered boundary landmarks. Requiring 30 events at *every* landmark
would make P3 impossible even with arbitrarily strong Phi concentration. The amendment changes only whether an
unsupported control window can veto measurement. It does not change Phi, the target, the window width, the family
definition, the event coordinate, the set of rivals or the success requirement that Phi rank first. Development
already places Phi below another adequately populated hazard window, so the correction does not turn the development
result positive.

