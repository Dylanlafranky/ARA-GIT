# PN11 Phi vertical-handover protocol — v3 final target freeze

**Test ID:** `PN11/PHI-VERTICAL-HANDOVER/v3`  
**Declared:** 21 July 2026, after development and before opening target `[10,000,000,11,000,000)`  
**Base contract:** v1 plus the v2 supported-window amendment  
**Only v3 change:** overall handling when a decisive distance criterion fails but a secondary hazard is underpopulated

## Final rating order

1. If P1 fails, return `IMPLEMENTATION FAILURE`.
2. If there are fewer than 1,000 target families, return `INCONCLUSIVE`.
3. If P2 or P4 fails, return `NOT SUPPORTED`; an underpopulated P3 cannot conceal a clean failure of another primary
   registered criterion.
4. If P2 and P4 pass but P3 lacks its frozen support requirements, return `INCONCLUSIVE`.
5. If P1-P4 pass, return `SUPPORTED`; otherwise return `NOT SUPPORTED`.

This amendment cannot improve the development result: Phi already loses P2 and P4 there. It prevents missing hazard
events from overriding a separately adequate falsifier. No coordinate, target, landmark, tolerance or pass direction
changed.

