# Q16 translation-fidelity amendment v2 — raw member structure

**Claim ID / version:** `Q16-ARA2-RAW-v2`  
**Supersedes before calculation:** `Q16-ARA2-RAW-v1`  
**Reason:** byte-decoder audit showed that the v1 phrase “paired `_1` and `_2` readouts” misidentified acquisition
bucket suffixes as two parent channels.

The relational object, four-child order, parent contrasts, forbidden conventional geometry and Dylan fidelity
verdict remain unchanged from v1.

## DYLAN PRIOR retained

Two complete ARA parents, each containing Phase A and Phase B, couple to produce four ordered children. The raw
observations must be allowed to reveal that geometry before established quantum coordinates name it.

## Corrected observable

Each archive contains nine sequential physical acquisition settings. Every binary acquisition member contains:

- five consecutive raw current segments;
- forty repeated readouts inside each segment;
- a record-specific sample length;
- repeated measurement/bucket members.

The earlier decoder ignored segment `0` and interpreted segments `1–4` through target-specific state thresholds.
Q16 v2 instead:

1. renames the nine physical settings `K0…K8`, preserving order but not quantum meaning;
2. retains **all five** segments `G0…G4`;
3. treats measurement/bucket members as repeated records, not separate physical axes;
4. uses the minimum common record count: `40` earliest development records and `40` latest holdout records per
   child and setting;
5. forms `45` raw ARA diameter cuts (`9 settings × 5 segments`);
6. keeps the raw sample distributions and native activity for every cut.

## Corrected plain restatement

The test looks at four prepared identities through forty-five raw current windows. It does not assume that any
instrument bucket is one of the two ARA parents, and it does not throw away the first current segment. The two
parent directions must emerge from how all four children differ across the same forty-five windows and must survive
into later records.

## Wrong-object gate

Using `_1/_2` suffixes as the ARA parents is `WRONG OBJECT`. Dropping raw segment `G0` before checking its geometry
is also forbidden. The v1 protocol was never run and receives no result or evidential status.

## Fidelity verdict

`EXACT ENOUGH TO TEST`

This amendment removes an AI decoder assumption and returns to Dylan’s declared two-parent/four-child object without
changing its geometry.

