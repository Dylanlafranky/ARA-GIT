# ENSO Brown Leaf Marker to WWV Abnormality Diagnostic

## Question

Does a causal brown leaf-fall marker precede unusual behavior in measured
lower-rung WWV data? If so, when?

This is the clean first test of the proposed leaf-to-soil signature. It does
not add a synthetic energy packet to the prediction formula.

## Strict-Causal Checklist

| Check | Status |
| --- | --- |
| Brown marker uses only NINO values available at or before the origin month | Yes |
| WWV ordinary-motion baseline is fitted on the first 60% only | Yes |
| WWV baseline sees prior WWV values at lags 1, 2, 3, and 6 months only | Yes |
| Future WWV values are used only as scored outcomes | Yes |
| Synthetic leaf injection | No |
| Smoothing | No |
| FFT or Hilbert phase | No |
| Predictor modified | No |

The brown marker is still an inferred NINO-based proxy. It is not an
independently measured upper-rung falling packet. This test can detect a
correspondence, but it cannot by itself prove the physical cause.

## Measured Lower-Rung Outcomes

The script measures three kinds of unusual WWV motion after subtracting
ordinary WWV history:

| Outcome | Meaning |
| --- | --- |
| `orientation_abnormality` | unusual east-west WWV rebalancing |
| `battery_abnormality` | unusual motion in the combined WWV battery |
| `vector_abnormality` | combined west/east WWV surprise magnitude |

## Held-Out Delay Scan

The full held-out period contains a weak delayed ridge:

| WWV outcome | Exploratory peak delay | Correlation |
| --- | ---: | ---: |
| orientation abnormality | 31 months | 0.139 |
| battery abnormality | 32 months | 0.143 |
| vector abnormality | 32 months | 0.146 |

At 30 months the correlations are already positive:

| WWV outcome | 30-month correlation |
| --- | ---: |
| orientation abnormality | 0.127 |
| battery abnormality | 0.122 |
| vector abnormality | 0.128 |

This is a lead worth investigating. It is not a large effect.

## Split-Window Check

The WWV battery outcome is the cleanest of the three:

| Window | Exploratory peak delay | Battery correlation |
| --- | ---: | ---: |
| visible pre-cutoff period after marker warmup | 15 months | 0.211 |
| early held-out half | 31 months | 0.183 |
| late held-out half | 34 months | 0.206 |

The two held-out halves independently place the battery ridge near 31 to 34
months. That is interesting. However, the earlier visible period peaks nearer
15 months. The present test therefore does not establish one universal fixed
return delay.

## Timing-Control Caution

The brown marker is periodic. Its held-out autocorrelation is:

| Marker displacement | Autocorrelation |
| --- | ---: |
| 6 months | 0.540 |
| 24 months | -0.619 |
| 48 months | 0.866 |

A single wrong-time null is not enough. Sliding a periodic marker can move the
same cross-correlation ridge to a different coordinate. Some wrong-time
placements produce peaks as large as or larger than the real-marker peak when
the whole 0 to 60 month scan is searched.

The strong-event subset is also too small: the training-only 90th-percentile
threshold leaves only two held-out strong events. Those event means should not
drive interpretation.

## Conclusion

The measured WWV lower rung contains a **candidate delayed signature** after
the causal brown leaf marker. In the held-out data, the clearest candidate is
an unusual WWV battery response around 31 to 34 months later.

This does **not** yet prove that the brown leaf physically fell into WWV or
that 32 months is a stable ARA recycling delay. The marker is inferred from
NINO, periodic, and not stable across the earlier window.

The useful result is narrower:

> Looking for the effect in measured lower-rung abnormalities is more
> promising than injecting a fake leaf packet into the formula. WWV contains
> a delayed candidate ridge that deserves an independent-marker test.

## Next Test

Freeze the 30 to 34 month candidate window before further tuning. Then repeat
the test with an independently observed upper-rung event candidate and more
direct lower-rung feeder measurements, such as equatorial wind bursts or
thermocline changes. That will show whether the ridge survives without being
derived from NINO itself.

## Files

Script:

```text
TheFormula/Claude4.8/ara_enso_leaf_to_wwv_abnormality_test.py
```

Full machine-readable result:

```text
TheFormula/Claude4.8/ara_enso_leaf_to_wwv_abnormality_result.json
```
