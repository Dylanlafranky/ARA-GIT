# ARA Raw Terrain Address Lookup Result

**Date:** 2026-05-26

This test answers the amplitude concern in the sphere-orientation branch:

```text
do not average terrain neighbours into a smooth analogue forecast
predict the future sphere pose
look up the nearest raw stored terrain address
read that raw value
```

Top-1 raw address is the primary framework-faithful branch. Top-3 median and weighted top-3 are small interpolation controls, included to show what happens when smoothing creeps back in.

## Files

- `TheFormula/ara_raw_terrain_address_lookup.py`
- `TheFormula/ara_raw_terrain_address_lookup_result.json`
- `TheFormula/ara_raw_terrain_address_lookup_result.js`
- `TheFormula/ara_raw_terrain_address_lookup_viz.html`

## Tested Branches

```text
raw_address_top1:
  nearest raw stored terrain coordinate to the predicted future pose

raw_address_top3_median:
  median of the nearest three raw stored terrain values

raw_address_top3_weighted:
  inverse-distance weighted nearest three raw stored terrain values

roll_learned_average:
  previous learned orientation roll branch that averages terrain neighbours

wobble_surface_analog:
  current best direct terrain/wobble reference branch
```

## Leakage Guard

This is strict-causal:

- The learned future pose trains only on completed historical rows whose target is before current origin `t`.
- The raw address lookup reads only historical origin-surface points before current origin `t`.
- Top-1 raw lookup is the primary branch; top-3 median/weighted are interpolation controls.
- No lag ridge, native-value decoder, future geometry oracle, smoothing, or visual shift is used.
- Non-ready rows fall back to persistence.

## Key Result

Ready-only 6/12/24 focus:

| Model | MAE | Corr | Direction | Amplitude ratio |
|---|---:|---:|---:|---:|
| Wobble surface analog | 0.557 | +0.376 | 0.824 | 0.764 |
| Learned roll average | 0.593 | +0.254 | 0.816 | 0.792 |
| Raw address top-1 | 0.600 | +0.361 | 0.807 | 0.841 |
| Raw address top-3 weighted | 0.603 | +0.335 | 0.804 | 0.833 |
| Contact address top-1 | 0.840 | -0.057 | 0.651 | 0.236 |

The raw top-1 lookup does what it was supposed to do:

```text
Compared with the averaged learned roll:
  corr improves from +0.254 to +0.361
  amplitude ratio improves from 0.792 to 0.841
  MAE worsens slightly from 0.593 to 0.600
  direction dips slightly from 0.816 to 0.807
```

## Interpretation

The user objection was correct. Averaging terrain neighbours was washing out amplitude. The raw address lookup preserves more of the mountains/valleys on the fixed sphere map.

The top-3 controls are informative too. They still preserve amplitude better than the averaged roll, but they already weaken correlation relative to top-1:

```text
raw top-1 corr:          +0.361
raw top-3 weighted corr: +0.335
```

That supports the rule:

```text
terrain address lookup first
interpolation only as a diagnostic/control
do not make smoothing the main branch
```

## Current Read

Raw address lookup has not solved the full forecast. It still trails direct `wobble_surface_analog` on MAE and direction. But it nearly matches wobble on correlation and beats wobble on amplitude preservation:

```text
raw top-1:
  corr +0.361
  amplitude ratio 0.841

wobble surface:
  corr +0.376
  amplitude ratio 0.764
```

So the result is not "raw lookup wins everything." The stricter read is:

```text
The fixed terrain-address idea is real enough to preserve amplitude.
The next bottleneck is address precision: predicting the correct future pose/coordinate.
```

## Next Improvement

Use raw address lookup as the main terrain read, then improve the address itself:

```text
1. Learn future orientation from completed past roll.
2. Use that pose to select the raw address.
3. Add a local wobble/basin selector only after the address is chosen.
4. Keep top-1 as the primary output and report top-3 only as a smoothing control.
```

That keeps the physical model intact:

```text
fixed sphere terrain
moving future pose
raw map address
water-slice reading
```
