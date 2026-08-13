# T360 frozen protocol v3 — source-trace recolouring correction

**Frozen:** 12 August 2026, during extraction QA and before metric or control calculation  
**Status:** v3 supersedes the trace-colour sentence in v2; every other v2 declaration remains active  
**Reason:** the public display recolours completed paths when the next run begins. V2 incorrectly listed the final colours as chronological colours.

## Correct source-trace recovery

- Run 1: its complete active red trace at frame 22.
- Run 2: the cyan completed trace in final frame 122.
- Run 3: the green completed trace in final frame 122.
- Run 4: the yellow completed trace in final frame 122.
- Run 5: the active red trace in final frame 122.

The white curve in frame 122 is not scored. Active-marker motion and the run resets establish the ordering above. This correction changes source bookkeeping only; no metric, gate, control, or result was inspected before it was frozen.
