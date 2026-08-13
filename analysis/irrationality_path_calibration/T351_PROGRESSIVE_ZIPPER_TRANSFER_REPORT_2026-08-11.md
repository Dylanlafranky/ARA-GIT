# T351 — Progressive zipper transfer

**Run date:** 11 August 2026  
**Evidence boundary:** synthetic known-referee causal instrument calibration  
**Primary verdict:** **NOT SUPPORTED**  
**Necessary non-identifiability boundary:** **PASSED**  
**Late-snap / false-seam controls:** **FAILED**

## Technical summary

The instrument did not fully recover the frozen progressive-zip signature. Candidate child geometry and independently measured lower-rung Connection were deliberately kept separate. The same visible phase path could not distinguish a true zip from a memory-only mimic, while the independent response channel could.

## What was tested

Two ordered lower-rung ARA strands approached pairwise contact behind a moving parent seam. The detector saw causal ARA phase geometry and rolling same-pair response coherence, but not the hidden edge strengths or regime labels. Progressive, memory-only, late-snap, false-seam, interrupted and reverse events were scored on untouched parameter combinations.

## Main results

- By 80% parent progress, progressive events carried a median **0.810** of their final independently measured Connection.
- Child order versus detected lock order had median Spearman **0.724**.
- Connection response followed candidate geometry by median **-0.0226** event durations.
- During a stationary parent-front interval, lower-rung Connection increased by median **0.038** while median front velocity was **0.000e+00**.
- Forward lock order versus chronological unlock order had median Spearman **-0.728**.
- Post-front response coherence was **1.000** for progressive zips and **0.000** for the memory-only mimic.
- Independent-response AUROC was **1.000**.

## The important negative result

Progressive and memory-only phase geometry was identical to maximum difference **0.000e+00**. Geometry-only AUROC was therefore **0.500**: chance, as frozen.

This answers the user's uncertainty directly. Approaching geometry can identify where a lock *could* form, but it cannot establish that a hidden Connection actually formed when an exact non-locking path mimic is possible. A connection-bearing consequence at a lower rung is required.

## ARA interpretation

The synthetic progressive case is consistent with:

`open parent traversal -> candidate child meeting -> local lock -> ordered retained Connection`.

The pause result isolates the proposed rung distinction: local children continued constructing Connection while the parent seam did not move. The reverse result recovered the zipper prediction that a reversed seam releases the accumulated locks in reverse order.

The result does **not** show that every physical system implements this zipper. It calibrates the signature and tells us what must be measured in real data: candidate proximity plus an independent lower-rung coupling response.

## Frozen controls

- Late-snap Connection share at 80% progress: **0.198**.
- Progressive minus false-seam same-pair response: **0.971**.
- Primary gates passed: **6/10**.
- Boundary gates passed: **3/3**.
- Control gates passed: **1/2**.

## Population and reproducibility

- Calibration configurations: **24**.
- Holdout configurations: **40**.
- Regime/mode event records: **384**.
- Causal time-series rows: **355200**.
- Protocol SHA-256: `8BF4382F69BB278F22E9848C346A36FBA001F60A7CB36AEFC2DD2CD90234DBBB`.
- Claim SHA-256: `2353B43F143969F565CFB10A4666508602A822786B49E7755CD59971DBC3ABC0`.

## Evidence boundary

This is generated calibration data with known referee states. Exact geometry identity in the mimic is constructed as a hard identifiability control. The independently observed response is noisy and causal, but still comes from a declared synthetic coupling process. Public-data testing must predeclare a domain-specific connection-bearing response before labels are opened.
