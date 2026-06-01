# ENSO Frozen Two-Flow Window Diagnostic

## Question

Do the two candidate WWV response windows behave like different flows?

The windows were frozen before scoring:

| Window | Proposed interpretation |
| --- | --- |
| 12 to 18 months | smaller/faster energy already below WWV moving upward |
| 30 to 34 months | slower recycled return after the brown leaf drop |

This is a diagnostic association test. It does not modify the predictor or
inject a synthetic energy pulse.

## Strict-Causal Checklist

| Check | Status |
| --- | --- |
| Brown marker uses NINO values available at or before the origin month only | Yes |
| Frozen windows selected before this comparison | Yes |
| WWV abnormality uses raw monthly WWV residuals after a training-only history baseline | Yes |
| Future WWV values used only as scored outcomes | Yes |
| Synthetic energy injection | No |
| Formula modified | No |
| Smoothing | No |
| FFT or Hilbert phase | No |
| Partial end-of-record windows accepted | No |

## Available Measurements

The current aligned record does **not** contain a proven measured rung directly
below WWV.

The test therefore separates:

| Channel | Honest role in this test |
| --- | --- |
| WWV west/east | measured lower-rung battery being examined |
| MJO maximum raw daily RMM amplitude per month | measured finer/faster activity candidate; not proven to be the direct WWV-below rung |
| IOD | measured lateral feeder comparison |
| QBO 30/50 hPa vector | slower timing control; not the rung directly below WWV |

WWV is monthly. To retain sharp MJO activity rather than smooth it away, the
script uses the largest raw daily RMM amplitude inside each month.

The public MJO RMM file also changes processing method in 2014. Its comparison
across eras is supporting evidence only.

## Result

### Earlier Visible Period

The pre-cutoff period after marker warmup shows a clear broad `12 to 18 month`
WWV response:

| Measurement | 12 to 18 month result |
| --- | ---: |
| WWV battery window correlation | **+0.424** |
| WWV vector window correlation | **+0.362** |
| WWV signed orientation correlation | **+0.459** |
| battery peak | 15 months, `+0.211` |
| half-peak width | all 7 months |

The WWV battery response is aligned with measured candidate feeder activity:

| Candidate channel | Contemporaneous alignment with WWV battery |
| --- | ---: |
| MJO finer/faster activity candidate | `+0.277` |
| IOD lateral feeder comparison | **`+0.573`** |
| QBO slower-clock control | `+0.096` |

This has the shape expected of a smaller/faster upflow: broad but directional,
with substantially more alignment to active feeder channels than to the
slower QBO control.

### Held-Out Period

The `12 to 18 month` branch does **not** repeat in held-out data:

| Measurement | 12 to 18 month held-out result |
| --- | ---: |
| WWV battery window correlation | `-0.255` |
| WWV vector window correlation | `-0.250` |
| WWV signed orientation correlation | `-0.147` |

Instead, the held-out data shows a broad `30 to 34 month` WWV response:

| Measurement | 30 to 34 month held-out result |
| --- | ---: |
| WWV battery window correlation | **`+0.296`** |
| WWV vector window correlation | **`+0.261`** |
| battery peak | 33 months, `+0.143` |
| half-peak width | all 5 months |

That later pulse is not aligned with the measured candidate feeder channels:

| Candidate channel | Contemporaneous alignment with WWV battery |
| --- | ---: |
| MJO finer/faster activity candidate | `-0.070` |
| IOD lateral feeder comparison | `-0.246` |
| QBO slower-clock control | `-0.060` |

## Interpretation

The test supports a **two-shape distinction**, but not yet a universal law.

The earlier visible `12 to 18 month` response looks like active feeder upflow:
it is directional and aligns with MJO/IOD activity. The later held-out `30 to
34 month` response looks different: it disturbs the WWV battery without the
same contemporaneous finer-feeder alignment. That is compatible with a slower
recycled return or falling-packet disturbance.

However:

1. The early upflow branch has not repeated in held-out time.
2. The lower rung directly beneath WWV is not independently measured here.
3. The brown leaf marker is still inferred from NINO.
4. The MJO file changes processing method in 2014.
5. Overlapping monthly windows are descriptive, not independent events.

The correct claim is:

> The current ENSO record contains two distinguishable WWV response shapes.
> One earlier visible branch has feeder-like alignment. A later held-out
> branch perturbs the WWV battery without that alignment. This is consistent
> with separate upward feeder and slower recycling channels, but it does not
> yet prove their physical identities.

## Next Test

The next useful measurement is a genuinely independent finer ocean/atmosphere
channel beneath WWV, sampled at a finer grain:

```text
equatorial wind bursts
thermocline depth
trade-wind stress
upper-ocean heat-content changes
```

Freeze the same `12 to 18 month` and `30 to 34 month` windows and test whether:

```text
early pulse -> stronger feeder alignment and orientation
late pulse  -> broader WWV battery disturbance with weaker feeder alignment
```

## Files

Script:

```text
TheFormula/Claude4.8/ara_enso_two_flow_window_test.py
```

Machine-readable result:

```text
TheFormula/Claude4.8/ara_enso_two_flow_window_result.json
```
