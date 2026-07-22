# PN26 validator amendment v1.1 — frozen before corrected rerun

**Frozen:** 22 July 2026, after the v1 validator opened target truth but before the corrected validator was run  
**Primary prediction hash remains:** `e87db543fba85d9d891b144c0eb12f93b380594854015d9832bbe1cf8760607c`  
**Permitted change:** one input-bound correction only; no prediction, threshold, cohort or candidate change

## Failure found

The v1 primary correctly generated the complete declared child domain through

\[
\lfloor\sqrt{2S}\rfloor.
\]

The independent validator generated its prime table only through the smaller truth-testing bound

\[
\lfloor\sqrt{\max(N)}\rfloor.
\]

It then attempted to reconstruct the `sqrt(2S)` parent from that truncated table. The low and middle cohorts happened
to retain the same split boundary, but the high cohort did not; its reconstruction check failed. This is a validator
implementation defect, not a failed target prediction. The sealed prediction CSV is unchanged.

## Frozen correction

Validator v1.1 changes only the prime-table ceiling to

\[
\max\left(\lfloor\sqrt{\max(N)}\rfloor,
\lfloor\sqrt{2\max(S)}\rfloor\right)+2.
\]

It delegates every other calculation, target label, threshold and report field to the frozen v1 validator. It writes
new v1.1 artifacts and does not overwrite the failed v1 receipt.

## Interpretation rule

- If v1.1 reconstructs all three cohorts, the primary predictions retain their prospective status because they were
  sealed before either validator opened truth.
- The original v1 implementation failure remains part of the provenance record.
- P4 remains failed if its frozen 50-percentage-point margin is not reached. No threshold may be relaxed.
