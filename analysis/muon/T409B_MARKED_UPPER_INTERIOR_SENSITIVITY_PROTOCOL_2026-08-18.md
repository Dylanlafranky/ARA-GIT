# T409B — Marked upper-interior sensitivity protocol

Frozen after T409 revealed that its broad R3 maximum sat exactly on the frozen lower boundary (`1.180`), but before the T409B sensitivity calculation.

## Reason for the sensitivity

The user's marked third line is visually near `x_mu≈1.35`. T409 searched the broad zone `[1.18,1.55]`; because the declining shoulder of R2 enters that zone, the maximum-density estimator selected the boundary at `1.180`. That is not an adequate operationalization of the marked interior line.

T409B preserves the T409 result and asks a narrower, explicitly post-hoc question: is there an actual local density crest inside the marked upper interior, and if so does its centre move chronologically beyond sampling noise?

## Frozen sensitivity estimator

- population: the same 2,109 held-out events;
- chronological blocks: the same six equal-count blocks per run;
- search interval: `[1.25,1.50]`;
- smoothing: Gaussian bandwidth `0.035 ARA`, grid step `0.001`;
- crest: the highest *strictly interior local maximum* in the search interval;
- a block crest is resolved only with at least five events in the interval and peak-to-median contrast at least `1.10`;
- if no interior local maximum exists, the block is unresolved rather than assigned to an interval edge.

## Null and reading

Use the same `5,000` global-order and within-run order shuffles as T409. Compare the marked crest's chronological motion statistic to the frozen T409 R1 and R2 values.

This sensitivity is descriptive/post-hoc evidence. It cannot upgrade the original visual observation to confirmatory status by itself.
