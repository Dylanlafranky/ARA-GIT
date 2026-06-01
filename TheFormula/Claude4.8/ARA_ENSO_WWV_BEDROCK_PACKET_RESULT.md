# ENSO WWV Geometric Bedrock and Packet-Flow Diagnostic

## Question

Do differently sized raw WWV discharge events share a recurring geometric
bedrock, while the amount of WWV motion riding over that geometry varies?

This test separates:

```text
geometric bedrock = one real train-only WWV discharge episode
packet flow       = each episode's native WWV volume motion
```

It does not create an averaged waveform template.

## Strict-Causal Checklist

| Check | Status |
| --- | --- |
| Event onset uses current and previous raw monthly WWV battery values only | Yes |
| Event rule uses a train-only WWV battery median | Yes |
| Causal cooldown prevents repeated counting of the same discharge | Yes |
| Bedrock template is one real training event, selected as medoid | Yes |
| Held-out controls matched by calendar month and prior WWV battery level | Yes |
| Smoothing | No |
| FFT or Hilbert phase | No |
| Synthetic energy injection | No |
| Formula modified | No |

This is a descriptive geometry test. The raw months after an onset are scored
outcomes, not inputs to a forecast.

## Raw Event Rule

A WWV discharge episode starts when:

```text
previous WWV battery >= training median
previous monthly WWV motion >= 0
current monthly WWV motion < 0
```

After accepting an onset, the detector waits six months before accepting
another one.

| Record split | Discharge episodes |
| --- | ---: |
| training | 22 |
| held-out | 14 |
| held-out matched ordinary-month controls | 14 |

## Train-Only Raw Bedrock

The most representative real training event is March 1992:

```text
[-1.054, -0.711, -0.961, -0.590, +0.355, +0.273, +0.118]
```

These are raw monthly WWV battery increments in native loader units
(`source volume / 1e14`).

The visible shape is:

```text
four falling months
then recovery
```

That is a candidate geometric bedrock for this WWV discharge-turn family.

## Declared Seven-Month Test

The declared seven-month raw profile gives:

| Comparison | Mean cosine similarity to the real training medoid |
| --- | ---: |
| held-out WWV discharge events | `+0.296` |
| matched ordinary months | `+0.217` |
| event minus control | `+0.079` |

The paired sign-flip result is `p = 0.299`. The full seven-month profile is not
a decisive held-out result by itself.

## Descriptive Profile-Length Sensitivity

The raw falling front is clearer than the entire fall-and-recovery tail:

| Raw profile length | event similarity | matched control similarity | lift | paired sign-flip p |
| --- | ---: | ---: | ---: | ---: |
| 3 months | `+0.418` | `-0.229` | **`+0.647`** | `0.0002` |
| 5 months | `+0.345` | `-0.094` | **`+0.439`** | `0.0001` |
| 7 months | `+0.296` | `+0.217` | `+0.079` | `0.2988` |
| 9 months | `+0.297` | `-0.017` | **`+0.315`** | `0.0075` |

This panel is descriptive sensitivity, not a preselected winner. Multiple
profile lengths were inspected.

The cleanest supported statement is:

> Held-out WWV discharge events reproduce the initial raw falling geometry
> better than matched ordinary months. The later recovery tail varies more.

## Packet Size

The declared seven-month panel sorts held-out events by training-derived native
WWV-motion terciles:

| Packet group | event count | native total WWV motion | bedrock similarity |
| --- | ---: | ---: | ---: |
| small | 8 | `1.641` | `+0.193` |
| middle | 5 | `2.415` | `+0.362` |
| large | 1 | `3.384` | `+0.788` |

The ordering is suggestive, but the large group contains only one event.
Across the seven-month held-out events, native packet size and bedrock
similarity correlate at `+0.469`. This is not yet enough to claim that larger
packets always expose the geometry more clearly.

## Frozen Brown-Marker Overlay

For held-out WWV discharge-event packet size:

| Preceding frozen marker window | Correlation with native packet size |
| --- | ---: |
| possible lower upflow, 12 to 18 months | `-0.218` |
| possible recycled return, 30 to 34 months | `+0.247` |

This modestly favors the slower recycled-return interpretation for packet
size. It remains weak evidence.

## Interpretation

The test supports the idea that a recurring bedrock and variable flow can be
measured separately.

The raw bedrock is not a perfect seven-month waveform stamped identically each
time. The most repeatable part is the first few months of the discharge turn.
The recovery tail is more sensitive to surrounding state, available gap,
alignment, and packet amount.

This is compatible with:

```text
observed response
    = recurring handoff geometry
    x packet size
    x available gap
    x current gate / alignment state
```

The test does not yet prove the full mechanism or measure an energy fraction.
WWV is a volume proxy, not joules.

## Next Test

Freeze the `3 to 5 month` raw falling-front bedrock as a separate preregistered
shape. Test it on independent finer measurements beneath WWV:

```text
equatorial wind bursts
trade-wind stress
thermocline-depth changes
upper-ocean heat-content changes
```

Ask whether packet amount and available gap explain the variable tail after
the shared falling front.

## Files

Script:

```text
TheFormula/Claude4.8/ara_enso_wwv_bedrock_packet_test.py
```

Machine-readable result:

```text
TheFormula/Claude4.8/ara_enso_wwv_bedrock_packet_result.json
```
