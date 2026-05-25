# ARA Raw Watershed Phase-Delay Result

**Date:** 2026-05-25

This is a diagnostic-only scan for the lower-spin watershed visualiser.

It asks:

```text
If the generated wave is compared against truth shifted by N months,
which shift gives the best match?
```

Negative shift means:

```text
the generated wave resembles earlier truth
therefore the generated wave is visually late
```

## Files

- `TheFormula/ara_raw_watershed_phase_delay_diagnostic.py`
- `TheFormula/ara_raw_watershed_phase_delay_result.json`
- `TheFormula/ara_raw_watershed_phase_delay_result.js`
- `TheFormula/ara_raw_watershed_lower_spin_viz.html`

## Main Result

The fixed lower-spin formula is mostly late by the forecast horizon.

| Horizon | Fixed formula best corr shift | Zero-shift corr | Shifted corr |
|---:|---:|---:|---:|
| `3m` | `-3m` | `+0.759` | `+0.998` |
| `6m` | `-6m` | `+0.382` | `+0.997` |
| `12m` | `-12m` | `-0.052` | `+0.994` |
| `18m` | `-18m` | `-0.126` | `+0.992` |
| `24m` | `-24m` | `-0.260` | `+0.989` |

This confirms the visual read:

```text
the fixed formula has a reasonable shape
but it is mainly drawing the origin/current water slice
then labeling it as the future
```

The same diagnostic gives a trivial perfect shift for persistence, which is the warning sign. If a model's best shift is exactly `-h`, it is not really advancing the wave; it is carrying the current state forward.

The learned lower-spin decoder is less purely delayed:

| Horizon | Decoder best corr shift | Zero-shift corr | Shifted corr |
|---:|---:|---:|---:|
| `3m` | `-2m` | `+0.818` | `+0.926` |
| `6m` | `-4m` | `+0.507` | `+0.698` |
| `12m` | `+1m` | `+0.243` | `+0.281` |
| `18m` | `-40m` | `+0.115` | `+0.266` |
| `24m` | `-48m` | `-0.027` | `+0.435` |

So the decoder corrects some of the short-horizon delay, but long horizons still show unstable timing.

## Interpretation

The user read is supported:

```text
shape is decent
directional mistakes compound then self-correct
the fixed formula reveals the shape too late
```

Mechanically, the fixed formula is not yet predicting the future topology arriving under the slice. It is mostly measuring the current contact/tributary state and carrying it forward.

The next formula should explicitly advance the topology/contact state:

```text
lower_spin_torque(t)
  -> estimate contact/arrival lead time
  -> project topology state forward by that lead
  -> then decode water-slice value
```

The visualiser now includes a **Visual Shift** control. Negative shifts move the generated wave earlier. The **Best** button uses this diagnostic's best-correlation shift for the active model/horizon.
