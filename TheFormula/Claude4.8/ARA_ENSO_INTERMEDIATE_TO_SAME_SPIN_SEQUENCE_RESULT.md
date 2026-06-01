# ENSO Intermediate-Disturbance to Same-Spin Sequence Diagnostic

## Question

Does the completed ENSO history show the proposed route signature?

```text
visible upper leaf marker
    -> adjacent anti-phase use / cancellation / dissipation
    -> smaller surviving same-spin deposit
    -> possible later recycled return
```

The present loader does not contain a directly observed lower-lower same-spin
ENSO coordinate. This test therefore uses measured WWV carefully:

| Frozen window | Measured proxy | Proposed role |
| --- | --- | --- |
| `12 to 18 months` | WWV east-west orientation disturbance | candidate intermediate disturbance |
| `30 to 34 months` | WWV battery disturbance | candidate later deposit proxy |

This is a descriptive proxy test, not a predictor or causal proof.

## Strict-Causal Checklist

| Check | Status |
| --- | --- |
| Leaf marker uses NINO values available at or before each origin | Yes |
| Leaf events are local marker peaks after fixed warmup | Yes |
| Earlier and later windows were frozen by prior diagnostics | Yes |
| WWV residual baseline uses training-only WWV history | Yes |
| Ordinary controls use the same era, season, and prior WWV battery level | Yes |
| January 2024 prospective outcome used | No |
| Smoothing | No |
| FFT or Hilbert phase | No |
| Synthetic energy injection | No |
| Formula modified | No |

The seven historical leaf peaks with completed later windows are:

```text
1996-06
1999-08
2004-02
2007-12
2011-09
2015-06
2019-06
```

The January 2024 event remains prospective and untouched.

## Historical Result

### 1. Candidate intermediate disturbance

The earlier WWV east-west orientation disturbance does not separate from
matched ordinary origins:

| Mean absolute orientation abnormality | Value |
| --- | ---: |
| leaf-event origins | `0.432` |
| matched ordinary origins | `0.439` |
| event minus control | `-0.008` |
| events above paired control | `4 / 7` |

The signed native orientation motion is negative for `5 / 7` events, but the
sign is mixed. This monthly proxy does not isolate one stable observed
anti-phase polarity.

### 2. Candidate later deposit

The later WWV battery-deposit proxy has only a small excess:

| Mean absolute battery abnormality | Value |
| --- | ---: |
| leaf-event origins | `0.119` |
| matched ordinary origins | `0.111` |
| event minus control | `+0.009` |
| events above paired control | `4 / 7` |

That is too small and inconsistent to establish a recurring same-spin deposit.

### 3. Smaller surviving packet rule

Using comparable native WWV battery motion per month:

| Read | Value |
| --- | ---: |
| mean later / earlier motion ratio at leaf events | `1.251` |
| mean later / earlier motion ratio at matched controls | `1.137` |
| leaf events with later motion smaller than earlier motion | `2 / 7` |

The measured WWV proxy does **not** show a reliably smaller later packet.

The early candidate disturbance also does not scale positively into the later
candidate deposit:

```text
corr(early WWV orientation disturbance, later WWV battery deposit)
    = -0.380
```

## Interpretation

The simple monthly-WWV sequence is not supported:

```text
WWV early orientation proxy
    -> smaller WWV later battery proxy
```

This does not establish that the physical route is absent. It establishes a
measurement boundary:

```text
WWV cannot currently be used as both
    the adjacent anti-phase rung
and
    the lower-lower same-spin reservoir
```

The later same-spin deposit may be:

```text
below the current measured WWV ruler
mixed with other WWV flows
temporally blurred by monthly sampling
altered by additional feeders and gates
```

The prospective January 2024 branch remains valid as a raw WWV observation.
It should not be promoted into an exact `0.382` ratio claim unless an
independent incoming-flow proxy and a distinct lower-lower coordinate are
declared.

## Next Measurement

The next useful step is not a fitted coefficient. It is an independently
observed lower-lower or intermediate channel:

```text
equatorial wind bursts
trade-wind stress
thermocline-depth changes
upper-ocean heat-content changes
finer-than-monthly measurements where available
```

## Files

Script:

```text
TheFormula/Claude4.8/ara_enso_intermediate_to_same_spin_sequence_test.py
```

Machine-readable result:

```text
TheFormula/Claude4.8/ara_enso_intermediate_to_same_spin_sequence_result.json
```
