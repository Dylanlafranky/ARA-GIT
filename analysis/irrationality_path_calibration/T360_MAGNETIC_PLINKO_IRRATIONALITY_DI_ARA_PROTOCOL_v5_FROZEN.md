# T360 frozen protocol v5 — non-degenerate layout control

**Frozen:** 12 August 2026, after extraction QA and before any ARA metric, event response, control score, p-value, gate, or verdict calculation  
**Status:** v5 supersedes one degenerate control in v1; v2 and v4 remain the active extraction amendments  
**Reason:** permuting labels among magnet columns within the same row does not change the physical point set and therefore is not a wrong-geometry control.

## Replacement fourth wrong layout

Replace “within-row permutation of magnet columns” with **stagger inversion**:

- six-magnet rows are displaced laterally by `+0.1` lattice unit;
- five-magnet rows are displaced laterally by `-0.1` lattice unit;
- positions wrap on the declared `u in [0,1]` lattice.

This preserves row count and broad spacing while placing the alternating lattice phase in the wrong lateral relation to the observed path.

## G1 randomization implementation

The frozen one-sided G1 `p <= 0.05` requirement is implemented as the exact paired Wilcoxon signed-rank comparison of each usable event's real-layout alignment against the mean alignment of its four wrong layouts. This is the event-level paired randomization requested in v1 and avoids a Monte-Carlo-only result.

No scored output existed when this correction was frozen.
