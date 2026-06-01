# ENSO Brown-Leaf Transit Forward Ablation

## Purpose

The preceding diagnostics asked:

```text
observe brown/green leaf drop at the tree
    -> look later in measured WWV soil
    -> estimate how long the packet takes to appear
```

They exposed a candidate `30 to 34 month` travel-time window.

This ablation freezes that window and asks whether it adds forward predictive
information. The main formula remains unchanged.

## Strict-Causal Checklist

| Check | Status |
| --- | --- |
| Leaf marker uses NINO values available at or before forecast origin only | Yes |
| WWV arrival window frozen at `30 to 34 months` | Yes |
| Arrived-packet state uses leaf markers observed `30 to 34 months` earlier only | Yes |
| Wrong-time controls use delayed earlier markers only | Yes |
| Future values used as features | No |
| Synthetic energy injection | No |
| Formula modified | No |
| Smoothing | No |
| FFT or Hilbert phase | No |

## Important Confirmation Limit

The `30 to 34 month` transit window was discovered from this same historical
record. This ablation is sample-wise causal, but it is not a fully independent
confirmation of that timing window.

The result is exploratory until it is scored on new or independent data.

## 1. Visible Leaf Now to Future WWV Soil

Target:

```text
mean measured WWV battery abnormality at origin + 30 to 34 months
```

| Model | Held-out correlation | MAE |
| --- | ---: | ---: |
| WWV state only | `-0.067` | `0.035` |
| WWV state plus real causal leaf marker | `-0.334` | `0.041` |
| leaf marker only | `-0.298` | `0.034` |

The direct marker-to-soil association changes sign:

| Period | Direct marker to soil correlation |
| --- | ---: |
| training | `-0.204` |
| held-out | `+0.296` |

Therefore the present marker does **not** generalize as a learned WWV-soil
arrival predictor. The historical WWV signature is interesting, but it is not
stationary enough to place into the formula as a fixed amplitude rule.

## 2. Packet Due Now to Downstream NINO

The arrived-packet state is:

```text
packet_due_now
    = mean(leaf markers observed 30 to 34 months earlier)
```

It is entirely causal. It asks whether an inferred packet reaching the soil now
changes the downstream ENSO path.

At the `30 month` NINO horizon:

| Model | Correlation | MAE | Direction |
| --- | ---: | ---: | ---: |
| raw ENSO topology state | `-0.223` | `1.010` | `0.697` |
| raw ENSO topology plus arrived packet | **`+0.062`** | `1.062` | `0.665` |

Correlation lift:

```text
+0.285
```

This improves shape correlation, but not MAE or direction. The arrived packet
should therefore be treated as a possible timing/correction channel, not a
standalone amplitude engine.

The packet by itself correlates `-0.174` with future NINO at this horizon. Its
value appears only in combination with the ordinary ENSO state.

### Wrong-Time Controls

At the `30 month` NINO horizon:

```text
real packet correction minus wrong-time-panel median = +0.177
real packet correction beats all declared wrong-time controls = yes
```

### Held-Out Halves

| Held-out period | Raw correlation | Plus arrived packet | Lift |
| --- | ---: | ---: | ---: |
| early half | `-0.281` | `+0.063` | `+0.345` |
| late half | `-0.223` | `+0.078` | `+0.301` |

### Block Bootstrap

A descriptive 12-month moving-block bootstrap gives:

```text
median correlation lift = +0.292
95% interval            = [+0.030, +0.514]
positive-lift fraction  = 0.986
```

This supports carrying the channel forward for testing.

## 3. Localized Return Ridge

The neighboring-horizon scan is descriptive, not a selected winner:

| NINO horizon | raw topology corr | plus arrived packet | lift |
| --- | ---: | ---: | ---: |
| 28 months | `-0.106` | `-0.031` | `+0.076` |
| 29 months | `-0.181` | `-0.029` | `+0.153` |
| 30 months | `-0.223` | `+0.062` | **`+0.285`** |
| 31 months | `-0.235` | `+0.017` | **`+0.253`** |
| 32 months | `-0.133` | `-0.014` | `+0.118` |
| 33 months | `-0.030` | `+0.022` | `+0.052` |
| 34 months | `-0.005` | `+0.069` | `+0.075` |
| 36 months | `-0.010` | `-0.066` | `-0.056` |

The correction is localized around the frozen arrival region rather than
appearing as one isolated point.

## 4. Leaf Seen Dropping Now to Long-Range NINO

Using the currently visible leaf marker directly gives only small exploratory
lifts:

| NINO horizon | raw corr | plus current leaf | lift |
| --- | ---: | ---: | ---: |
| 30 months | `+0.053` | `+0.088` | `+0.035` |
| 32 months | `+0.137` | `+0.179` | `+0.042` |
| 34 months | `+0.157` | `+0.173` | `+0.016` |

These do not beat all wrong-time controls. The current marker is not yet a
validated long-range NINO predictor by itself.

## Interpretation

The latest result is narrower than the simplest leaf analogy, but still useful:

```text
visible leaf drop now
    -> candidate packet enters transit
    -> soil signature is historically visible but nonstationary
    -> arrived packet may correct the later ENSO path near a localized ridge
```

The forward value is not yet an exact `32 month` soil forecast. The best current
use is as a possible state correction:

```text
ordinary ENSO state
    + packet due / recently arrived
    -> corrected route estimate
```

Because the transit window was discovered from the same historical record, the
channel should remain an exploratory diagnostic until new data or an
independent physical marker confirms it.

## Next Test

Do not hard-code the packet into the main formula yet.

Freeze:

```text
arrival window = 30 to 34 months
correction ridge = 29 to 31 months after inferred arrival
```

Then test the same packet clock against an independently observed leaf or soil
measurement:

```text
upper-ocean heat content
thermocline depth
trade-wind stress
equatorial wind bursts
```

If the independent channel reproduces the ridge, integrate the arrived-packet
state into the prediction formula as a route/timing correction.

## Files

Script:

```text
TheFormula/Claude4.8/ara_enso_leaf_transit_forward_ablation.py
```

Machine-readable result:

```text
TheFormula/Claude4.8/ara_enso_leaf_transit_forward_ablation_result.json
```
