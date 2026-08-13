# Independent validation of T358

**Export arithmetic reproduced:** YES  
**Frozen gates reproduced:** YES  
**Primary phase interface valid:** NO

The saved pair medians, record medians, six frozen gates, preregistration hashes and source archive checksum were independently reproduced without importing the analysis program.

## Data-interface audit

Across records, the median adjacent-step phase-backtrack fraction ranged from 0.459 to 0.464; the maximum channel value ranged from 0.465 to 0.470. A valid one-way cycle clock should be overwhelmingly monotone; the audit threshold was 0.10.

This threshold was not a frozen outcome gate, so the registered G1-G6 verdict is not rewritten. It does change the scientific reading: T358 faithfully shows that this particular derivative phase-plane cut failed the registered test, but it does not faithfully establish that the oscillators lacked the proposed ARA relation. The intended physical question remains inconclusive until the same archive is read with a physical event clock defined from the raw waveform.

## Recomputed frozen gates

- G1: FAIL
- G2: FAIL
- G3: PASS
- G4: PASS
- G5: FAIL
- G6: PASS
- overall: FAIL
