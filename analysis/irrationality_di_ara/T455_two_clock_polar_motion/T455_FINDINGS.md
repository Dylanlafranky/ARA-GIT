# T455 findings — two clocks and geographic polar motion

## Result first

T455 recovered a clear scale-linked geographic-pole wave, but the frozen test does **not** establish that this child is a scale-invariant live predictor of the Earth-clock handover. The full child passed 3 of 6 frozen gates. Its one-window holdout improvement over the clock-only model was -0.62% at 1 day, +2.37% at 7 days, -16.98% at 30 days and -12.86% at 90 days.

The stronger finding is geometric. The exact atomic-clock/Earth-rotation relation remains almost perfectly on the ARA ridge: its 0–2 coordinate ranges from 0.9999999904 to 1.0000000207. The ridge is therefore not an arbitrary fitted landmark; it follows directly from the very small difference between the SI day and the observed rotation day.

## What the pole child records

The geographic pole was measured as a typed Irrationality Di-ARA:

- **amount coordinate:** change in pole-displacement magnitude relative to the previous same-scale displacement;
- **traversal coordinate:** signed change in the direction of that displacement.

At 30- and 90-day grains, the amount coordinate continues to move around its 1.0 ridge while the traversal coordinate becomes almost entirely one-sided. The implied median traversal cycles in validation and holdout are approximately 374 days at 30 days and 384/373 days at 90 days. The independent spectrum has its strongest peak at 361.65 days. These are converging descriptions of the annual geographic-pole traversal wave.

This means the lower Di-ARA quadrants are not “missing.” At the coarser grains, they are the occupied children of this particular directional cut. The daily cut is much noisier and spreads through all four quadrants; the 30- and 90-day cuts expose the stable parent-facing direction.

## Prospective timing result

Using only the pole Di-ARA child, rather than absolute pole position, modestly improved the holdout Earth-clock forecast at a four-window horizon across all four grains:

| Grain | Horizon | Improvement over clock-only |
|---:|---:|---:|
| 1 day | 4 days | +0.39% |
| 7 days | 28 days | +0.97% |
| 30 days | 120 days | +1.23% |
| 90 days | 360 days | +5.81% |

The corresponding moving-block bootstrap mean-gain intervals are positive at all four grains. However, shifting the pole child by 365 days preserves almost the same broad advantage. That is decisive context: much of the forecast information belongs to a repeating annual parent carrier, not a uniquely live handover occurring only in the present pole state.

A post-result same-season diagnostic is still encouraging. Adding the live Di-ARA child to a clock-plus-365-day-seasonal baseline improved MAE by 0.58% at the 4-day horizon, 0.72% at 28 days, 0.12% at 120 days and 4.45% at 360 days. The 4-day, 28-day and 360-day block-bootstrap intervals were positive; the 120-day interval crossed zero. Because this comparison was designed after viewing the frozen result, it is a hypothesis for an independently frozen confirmation, not a rescued pass.

## ARA reading

Within ARA, the cleanest current interpretation is:

1. **Parent ridge:** the exact two-clock relation sits extremely close to 1 because the two day-length clocks are strongly coupled.
2. **Child traversal:** geographic polar motion supplies a directional child whose stable coarse-grain cycle is approximately annual.
3. **Child amount:** displacement magnitude oscillates around its own ridge rather than closing into a single monotonic relation.
4. **Scale transfer:** the 30- and 90-day cuts share geometry strongly; the daily cut is a different, noisy lower-scale expression.
5. **Unresolved identity:** the recovered annual carrier is not demonstrated to be Time itself. It is a real parent-scale Earth-system wave through which a smaller live-state contribution may travel.

The test therefore succeeds as a scale-invariant geometry calibration and fails as a confirmation that raw pole state is a universal live timing child.

## Best next test

Freeze T456 before looking at its holdout:

- retain the same exact two-clock target and the same four grains;
- give the clock-only model an explicit annual and semiannual seasonal parent;
- compare the current pole Di-ARA against the same pole state one year earlier;
- remove or condition on published atmospheric and oceanic angular-momentum excitation when available;
- require the **live-minus-same-season** pole contribution to transfer across grains and to retain its signed traversal orientation;
- keep absolute pole position separate from the relational Di-ARA child.

That asks the sharper question: after the known annual parent is accounted for, does the live geographic-pole child carry scale-consistent information about future Earth-rotation timing?

