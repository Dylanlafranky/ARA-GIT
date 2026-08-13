# T360 frozen protocol v4 — uniform active-trace recovery

**Frozen:** 12 August 2026, during source extraction QA and before metric or control calculation  
**Status:** v4 supersedes v3's trace-frame table; every other v2 declaration remains active  
**Reason:** the display makes a stronger uniform extraction available: the currently moving run is always red. Each run can therefore be recovered from the last active frame before reset under one colour rule, instead of depending on completed-path recolouring.

## Final frozen source-trace recovery

- Run 1: red trace, frame 22.
- Run 2: red trace, frame 44.
- Run 3: red trace, frame 67.
- Run 4: red trace, frame 101.
- Run 5: red trace, frame 122.

The extraction threshold and downstream interpolation are identical across all five paths. Completed white/cyan/green/yellow traces are descriptive source annotations only and are not scored. No ARA coordinate, event response, control comparison, gate, or verdict was inspected before this correction.
