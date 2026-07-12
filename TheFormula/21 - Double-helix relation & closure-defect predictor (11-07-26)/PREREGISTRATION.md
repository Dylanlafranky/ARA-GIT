# ARA Double-Helix Relation and Closure-Defect Predictor

**Frozen before scoring:** 2026-07-11  
**Status:** prospective local holdout test  
**Primary record:** PhysioNet NSR RR `nsr047`  
**Replication record:** PhysioNet NSR RR `nsr053`  
**Development/smoke-test record:** `nsr001` only

## Prediction being tested

The new mathematical mapping says that an ARA cycle has two dynamic strands:

1. the current phase strand;
2. the anti-phase strand, transported forward by half a cycle and inverted;
3. a relation created by those two strands, not a third independent strand.

A circle that returns exactly to the same state is closed. A real cycle advancing through time does not return exactly; its full-cycle difference is the local helix pitch or **closure defect**.

The prediction is:

> On an asymmetric oscillatory RR signal, using the phase/anti-phase relation plus the full-cycle closure defect will improve held-out multi-step prediction over the same rolling circular/Fourier state without those terms. The improvement should be concentrated near quadrant transitions. If the relation and closure terms do not improve either value, direction, or transition calls, this mathematical translation is rejected in its present form.

## Frozen data protocol

- Load RR intervals from the local PhysioNet Normal Sinus Rhythm RR database with `wfdb.rdann(record, "ecg")`.
- Convert annotation intervals to milliseconds.
- Keep intervals in `[300, 2000]` ms.
- Downsample by the median of consecutive blocks of 10 RR intervals.
- Use the first 70% for training and the final 30% for held-out scoring.
- Periods, ARA rise/release fractions, standardisation, clipping bounds, and regression coefficients use training data only.
- No centered smoothing, `filtfilt`, future endpoint padding, test-selected shift, or test-selected parameter is allowed.
- Primary and replication records are scored in the same run after the code and this document are frozen.

## Frozen scale extraction

- Select the three strongest training-only spectral periods between 8 and 512 downsampled steps.
- Enforce at least 20% separation between selected periods.
- A local rolling harmonic state is fitted causally over a window of four times the largest selected period.
- The same selected periods and local state estimates are used by the circular baseline and ARA model.

## Mathematical state

For each selected period `P`, define the locally fitted phase state

```text
u(t) = [x(t), q(t)]
```

where `x` is the fitted oscillatory component and `q` is its quadrature coordinate.

Transport the observed half-cycle state into the current orientation:

```text
v(t) = -u(t - P/2)
```

The relation strength is the non-negative alignment of the two transported strands:

```text
kappa(t) = clip(cosine_similarity(u(t), v(t)), 0, 1)
```

The two-strand consensus is

```text
m(t) = [u(t) + v(t)] / 2
```

and the full-cycle closure defect is

```text
c(t) = u(t) - u(t - P).
```

The ARA state advanced by horizon `h` is fixed as

```text
u0(t)       = [1 - kappa(t)] u(t) + kappa(t) m(t)
u_hat(t+h)  = R(2*pi*h/P) [u0(t) + (h/P)c(t)]
```

where `R` is the ordinary two-dimensional rotation matrix. There is no fitted relation weight and no fitted closure-defect weight.

## ARA-shaped projection

The training signal supplies a release fraction `r` for each period from peak-to-trough duration divided by peak-to-peak duration. The projection is a piecewise cosine:

```text
peak -> trough occupies fraction r
trough -> next peak occupies fraction 1-r
```

When `r = 0.5`, the function is exactly an ordinary cosine. Thus the circular baseline is nested inside the ARA shape.

The four quadrants are the two binary signs:

```text
sign(position relative to centre) x sign(direction of movement).
```

Quadrant-transition accuracy is a secondary outcome fixed before scoring.

## Models

1. `persistence`: current RR value.
2. `ar_ridge`: causal RR lags only.
3. `rolling_circle`: the same three causal local harmonic states projected as ordinary circles.
4. `shape_only`: rolling states with ARA-shaped projection, without relation/closure correction.
5. `relation_only`: phase/anti-phase consensus and closure defect with circular projection.
6. `ara_helix`: relation, closure defect, and ARA-shaped projection together.
7. `ar_plus_circle`: causal lags plus the rolling-circle forecast through a train-only ridge readout.
8. `ar_plus_ara`: the same causal lags plus the ARA-helix forecast through the same ridge readout.

The decisive matched comparison is `ar_plus_ara` versus `ar_plus_circle`.

## Horizons and metrics

Frozen horizons, measured in downsampled 10-beat steps:

```text
1, 3, 6, 12, 24, 48
```

Primary metrics:

- Pearson correlation;
- mean absolute error;
- direction accuracy for `sign(y(t+h)-y(t))`.

Secondary metrics:

- four-quadrant state accuracy;
- transition-only direction accuracy;
- amplitude ratio `std(predicted change)/std(actual change)`.

## Pass and failure conditions

Primary pass:

- `ar_plus_ara` beats `ar_plus_circle` on both correlation and MAE at at least three of six horizons on the primary record; and
- mean correlation lift is positive on both primary and replication records.

Partial support:

- value metrics do not pass, but transition-only direction improves by at least 0.05 on both records.

Failure:

- mean correlation lift is zero or negative on either record and transition-only direction does not improve by 0.05 on both; or
- apparent gains disappear under the causal/leak audit.

No equation, period count, horizon, record, or pass threshold may be changed after scoring without creating a separately named version 2 test.
