# Independent validation of T359

**All exported arithmetic reproduced:** YES  
**Frozen gates reproduced:** YES  
**Overall frozen result:** FAIL / INCONCLUSIVE

Pair medians, record medians, source/preregistration hashes and every gate were reconstructed without importing the T359 analysis program.

## Gate result

- G0: FAIL
- G1: PASS
- G2: PASS
- G3: PASS
- G4: FAIL
- G5: FAIL
- G6: PASS
- overall: FAIL

## Diagnostic reading

The constructed event phase is strictly monotone and all 11 record-median periods lie inside 1.5–4.0 seconds. G0 failed only because the two shorter uncoupled source records supplied median event counts of 23 and 28 rather than the frozen minimum of 30.

That technical count miss does not rescue the complete result: G4 and G5 independently failed. The event normalization made the coupled, uncoupled and wrong-record sequences almost equally deterministic (`x_R≈0`, best coherence `≈1`). It therefore recovered closure and non-closure locations but removed the coupling-specific information needed to identify the relation.

T359 is useful calibration but not a supported physical transfer.
