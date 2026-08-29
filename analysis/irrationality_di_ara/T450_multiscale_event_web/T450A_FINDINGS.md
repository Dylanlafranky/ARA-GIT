# T450A findings — pose-scale and observable-child discovery

## Result first

T450A did **not** recover a transferable fixed local rung shared across the measured pose children. Development produced one weak candidate: core span (head-to-abdomen extension/contraction) in a broad 0.32–1.28 second band, frozen at 64 frames or 0.640 seconds. It met the minimum fly-support rule (4/6) but failed chronology strength at the exact centre and failed untouched experiment-4 transfer (0/2 flies).

This is a useful calibration result. The pose children are measurable and show clear multiscale geometry, but this 60-second cut does not justify a universal biological micro/bout rung, a complete Di-ARA or a hidden time coordinate.

## Relational address

individual fly → recording-fraction parent → 60-second pose envelope → body-frame feature children → dyadic 10 ms–10.24 s scale surface → existing ten-minute/hour/day parents.

The six independent observed children were traversal speed, rotation speed, core bend, core span, internal articulation speed and left/right articulation balance. Behaviour and edge labels annotated the pose; they did not define the axes.

## Development result

- Six independent flies, four continuous 60-second envelopes each.
- The uncorrected selector placed almost every feature near 1.28 and 5.12 seconds. Same-scale timestamp permutations showed that the larger-scale agreement was mostly finite-window geometry: only 2–8 of 24 envelopes per nominal address exceeded their own 95th-percentile null.
- That issue was documented and corrected before experiment 4 was extracted. A fly could then nominate only a boundary whose four-envelope median exceeded the same feature/scale null.
- Only core span survived: four flies nominated boundaries within one octave of 0.640 seconds. Their actual addresses were 0.320, 0.320, 0.640 and 1.281 seconds.
- No temporal band was supported by three or more independent feature identities. A common pose-parent rung was therefore not recovered.
- At the frozen 0.640-second centre, 7/24 individual envelopes exceeded their own 95th-percentile timestamp null. The median observed geometry-change score was 1.715 versus a median null 95th percentile of 2.327.
- Reversing time produced the opposing signed-asymmetry direction in 10/24 envelopes. This is not strong evidence for a consistently directional chronological child.

## Untouched experiment-4 transfer

- Two later-regime flies, four envelopes each, received the development configuration unchanged.
- Fly 32 nominated core-span changes at 0.160 and 2.561 seconds. Both are two octaves from the frozen 0.640-second address.
- Fly 47 produced no above-null core-span nomination.
- Frozen transfer: 0/2 flies; the core-span band fails.

The holdout deformation is nevertheless visible and should not be discarded. Both holdout flies independently nominated traversal, at 0.640 and 1.281 seconds respectively. Fly 32 also concentrated articulation and left/right changes at 0.160 seconds; fly 47 nominated rotation at 0.080 seconds. These were not frozen development identities and cannot count as confirmation. They are a post-holdout hypothesis that the later regime may expose a more movement-heavy local child or simply a two-fly coincidence.

## Data quality

- All eight flies and all 32 envelopes are present.
- Core pose visibility: minimum 99.82% in development and 100% in holdout.
- Articulation visibility: minimum 99.62% in development and 99.98% in holdout.
- Left/right paired visibility: minimum 86.56% in development and 99.52% in holdout; it remains a required distortion control.
- The caches contain no collapse/death field. The frozen configuration predates both holdout caches.
- The final audit passes 19/19 checks.

## ARA reading

The supported development object is a **simple one-coordinate candidate child**: core extension/contraction around a local temporal band. Its coupled pole is not established, so it is not a Di-ARA. Ridge 1 in the visual report is the development median under the frozen robust display mapping, not a universal physical ridge.

The failure is informative for the approved lineage. It argues against freezing one population-wide pose rung from short windows. T450B should preserve each feature's full multiscale surface and ask whether longer within-fly histories organise those variable local bands into lifecycle periods without using collapse or death labels. The 10–60 second gap must be measured with longer windows rather than inferred from T450A.

## Artifacts

- `results/T450A_POSE_SCALE_DISCOVERY_REPORT.html` — self-contained technical visual report.
- `T450A_FROZEN_PROTOCOL.md` — exact Who/What/When/Where/Why/How and pre-holdout correction.
- `T450A_SELECTION_CORRECTION.md` — transparent record of the finite-window issue.
- `results/T450A_FROZEN_CONFIG.json` — frozen development configuration.
- `results/T450A_VALIDATION.json` — 19-check audit.
- CSV files in `results/` retain every development and holdout scale metric, nomination, ARA display coordinate, control and transfer decision.

