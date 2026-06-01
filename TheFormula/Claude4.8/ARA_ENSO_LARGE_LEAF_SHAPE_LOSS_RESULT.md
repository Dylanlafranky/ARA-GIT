# ENSO Large-Leaf Cycle and Temporal-Shape-Loss Diagnostic

## Question

Are larger brown-leaf drops associated with:

```text
one full brown cycle
or
three brown cycles
or
a system visibly winding down and losing temporal shape?
```

This is a descriptive diagnostic, not a predictor.

## Strict-Causal Checklist

| Check | Status |
| --- | --- |
| Leaf marker uses NINO values available at or before each month only | Yes |
| Temporal-shape loss compares raw recent NINO with earlier raw NINO only | Yes |
| Future WWV soil data used only as scored outcome | Yes |
| Smoothing | No |
| FFT or Hilbert phase | No |
| Synthetic energy injection | No |
| Formula modified | No |

## Raw Temporal-Shape-Loss Reader

The diagnostic reads:

```text
shape_loss(period, width, t)
    = 1 - corr(
        raw NINO segment ending at t,
        raw NINO segment period months earlier
      )
```

This is closer to the proposed "system winding down" idea than a one-step
forecast error. It asks whether the present raw shape still resembles its
previous pass.

## Leaf-Peak Spacing

After causal-marker warmup, eight visible inferred leaf peaks appear:

```text
1996-06
1999-08
2004-02
2007-12
2011-09
2015-06
2019-06
2024-01
```

Their gaps are:

```text
[38, 54, 46, 45, 45, 48, 55] months
```

| Summary | Value |
| --- | ---: |
| mean gap | `47.3 months` |
| standard deviation | `5.4 months` |
| declared brown period | `48 months` |

This is consistent with a roughly one-brown-cycle visible shedding rhythm.
It is **not** independent proof of that rhythm because the causal leaf marker
itself contains a declared `48 month` brown geometry.

## One-Cycle Shape Loss

For the seven peaks with an observable future WWV soil window:

| Raw shape segment width | shape loss -> visible leaf-marker size | shape loss -> future WWV soil dump |
| --- | ---: | ---: |
| 6 months | `+0.396` | `-0.695` |
| 12 months | **`+0.573`** | `+0.004` |
| 18 months | **`+0.637`** | `+0.009` |
| 24 months | **`+0.650`** | `+0.055` |

The `12 to 24 month` raw reader gives a moderate hint:

> A cycle that has lost resemblance to its previous pass tends to produce a
> larger visible inferred leaf marker.

However, that shape loss does not yet predict the size of the later WWV soil
disturbance.

## Three-Cycle Shape Loss

The three-cycle (`144 month`) comparison is unstable:

| Raw shape segment width | shape loss -> visible leaf-marker size | shape loss -> future WWV soil dump |
| --- | ---: | ---: |
| 6 months | `-0.026` | `+0.413` |
| 12 months | `-0.168` | `+0.285` |
| 18 months | `+0.049` | `-0.059` |
| 24 months | `+0.048` | `-0.092` |

The present record does not support a stable three-cycle rule. Seven completed
soil outcomes are too few to test a rare-event recurrence honestly.

## Prospective Event

The latest inferred peak occurred in:

```text
2024-01
```

Its raw one-cycle shape-loss reading over the preceding `18 months` is:

```text
1.202
```

Its proposed `30 to 34 month` WWV soil window has not occurred yet. Preserve
this event prospectively:

```text
expected soil-observation window:
2026-07 through 2026-11
```

Do not tune the marker or the window after seeing that future outcome.

The separate prospective packet-ratio note preserves the proposed `2 - phi`
comparison without conflating the ARA-width landmark with a measured energy
percentage:

```text
TheFormula/Claude4.8/ARA_ENSO_2024_PACKET_RATIO_PROSPECTIVE_NOTE.md
```

## Conclusion

The current evidence supports a modest refinement:

```text
roughly once per brown cycle:
    visible inferred shedding opportunity

larger visible marker:
    more likely when raw temporal shape has degraded relative to the previous cycle

later WWV soil amount:
    still depends on packet size, available gap, route, and gate state
```

The three-cycle "large death dump" remains a plausible rare-event hypothesis,
but the current ENSO record is too short to establish it.

## Files

Script:

```text
TheFormula/Claude4.8/ara_enso_large_leaf_shape_loss_test.py
```

Machine-readable result:

```text
TheFormula/Claude4.8/ara_enso_large_leaf_shape_loss_result.json
```
