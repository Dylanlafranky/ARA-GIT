# Q38 Translation Fidelity — Fixed-Anchor Phase Cycle

**Test ID:** `Q38-FIXED-ANCHOR-PHASE-CYCLE-v1`  
**Date:** 27 July 2026  
**ARA status:** prospective operational test of a Phase-A → Phase-B → Phase-A
cycle across a measured determinant pinch

## User geometry

Dylan's interpretation of the Q37 offset pattern is:

> The relation may have traversed the whole Phase B and emerged on the other
> side as Phase A. The nearly level `-0.107, -0.111, -0.110` region may be
> the rounded edge of an ARA sphere before the sudden positive return.

The intended geometry is not “Phase B must remain permanently visible.”
It is a complete ordered cycle:

\[
\mathrm{Phase\ A}
\longrightarrow
\mathrm{pinch/singularity}
\longrightarrow
\mathrm{Phase\ B}
\longrightarrow
\mathrm{Phase\ A}.
\]

## Required correction to Q37

Q37 compared moving pairs \(C_{t-k}\) and \(C_{t+k}\). Its offset sequence
therefore cannot distinguish motion of the exit from motion of the approach.
Q38 must:

1. establish one fixed Phase-A anchor from the approach side only;
2. keep that anchor unchanged;
3. follow only the post-pinch tensors;
4. require the negative and positive states to occur in the declared order;
5. exclude direction readings whose tensor magnitude is too close to zero.

## ARA-to-math translation

| ARA term | Q38 operational quantity |
|---|---|
| Phase-A anchor | highest-amplitude approach tensor among offsets `-7..-3` |
| Singularity/pinch | development-qualified determinant-closure trough |
| Phase-B entry | reliable post-pinch anchor cosine at most `-0.25` |
| Strong Phase-B appearance | reliable post-pinch anchor cosine at most `-0.50` |
| Phase-A return | later reliable anchor cosine at least `+0.25` |
| Identity remains measurable | post tensor amplitude at least `10%` of anchor for direction; at least `50%` at return |
| Completed local cycle | Phase-B entry followed by Phase-A return |
| Rounded traversal | ordered continuous score combining anti-depth and return height |

## Scale and direction lock

- **Measured identity:** one raw connected \(3\times3\) pair-relation tensor.
- **Parent event:** one complete-loop lineage's determinant pinch.
- **Approach direction:** fixed anchor before the pinch.
- **Exit direction:** successive tensors after the pinch.
- **Orientation:** negative cosine is operational anti-orientation; positive
  cosine is return toward the anchor orientation.
- **Time grain:** deposited simulator slices, not physical seconds.

## What counts as support

Support requires an ordered negative basin and positive return in a majority
of eligible events and lineages, with continuous-score separation from
time-, pair- and network-matched controls. A negative point alone is not a
cycle. A later positive point without a prior negative basin is not a cycle.

## What does not count

- the moving-reference Q37 curve itself;
- selecting the best anchor or post window after opening Q38 values;
- orientation at a near-zero tensor without the amplitude reliability floor;
- an unordered set containing both positive and negative readings;
- a time, pair or network control showing the same cycle frequency;
- a forced complement such as \(x+(2-x)=2\);
- physical Phase B, a literal spacetime singularity or a topological sphere.

## Honest interpretation boundary

A passing Q38 result would establish a reproducible fixed-anchor
anti-orientation-and-return path in an untouched simulator archive. It would
be a strong operational crosswalk for Dylan's A→B→A cycle. It would not by
itself prove that the path is a universal ARA sphere, a hidden quantum phase
or a physical singularity crossing.

