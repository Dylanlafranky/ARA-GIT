# ENSO Leaf-Fall Same-Spin Route Ablation

## Question

Does the causal upper leaf packet settle more coherently two physical rungs
down, where spin orientation matches again, than one rung down in the adjacent
counterspinning layer?

This tests the framework refinement:

```text
contact transfer is not automatically coherent absorption

orientation(k)     = +1
orientation(k - 1) = -1
orientation(k - 2) = +1
```

A leaf may touch the adjacent counterspinning sphere while falling through it,
but settle as stored recyclable energy only in a matching-spin sphere.

Script:

```text
ara_enso_leaf_same_spin_route_ablation.py
```

Machine-readable result:

```text
ara_enso_leaf_same_spin_route_ablation_result.json
```

## Formula Visibility

At origin month `t`, the direct formula sees only current or earlier:

```text
NINO
SOI
WWV west
WWV east
IOD
PDO
stored recursive-gate reservoir state
past-only raw-NINO causal leaf pulse
```

It does not see future NINO, FFT bands, Hilbert envelopes, future-origin
features, analog lookups, or held-out tuning scores.

This is a retrospective held-out test with a fixed chronological split. It is
not a live blind forecast made before the held-out years occurred.

The `var_plus_*` rows are train-only ridge diagnostics. They are not the direct
physical formula.

## Tested Routing Rule

The ordinary lower packet remains unchanged. The upper leaf is added to only
one selected store:

```text
one-rung opposite-spin route:
    one_store += 2g * leaf

two-rung same-spin route:
    two_store += 4g^2 * leaf

g = (2 - phi) / 2
```

The packet does not change the ENSO surface immediately. It waits in the
selected store until that store's existing recursive ARA gate opens:

```text
release(store, gate)
    = (1 / phi^2) * gate * tanh(abs(store)) * store
```

## Compared Routes

The ordinary recursive gate is the required reference. Three declared leaf
routes were tested:

```text
leaf_one_rung_opposite
    leaf settles one rung down despite opposite orientation

leaf_two_rung_same
    leaf bypasses the adjacent store and settles two rungs down

leaf_two_rung_same_null
    same two-rung route, but leaf timing delayed by one green rung:
    round(48 / phi) = 30 months
```

The null uses earlier leaf values only.

## Important Diagnostic Fix

An initial run exposed the raw causal leaf pulse directly to the statistical
readout. That let the readout recognize leaf timing without testing the
storage route. The shortcut was removed before reporting.

The final diagnostic can see routed storage and gated release only. It cannot
see the raw leaf pulse or its deposit directly.

## Direct Formula Result

The leaf packets are too small to move the direct formula materially at this
monthly resolution:

| Horizon | Ordinary gate | One rung opposite | Two rungs same | Two-rung null |
| ---: | ---: | ---: | ---: | ---: |
| 6 months | `0.354` | `0.354` | `0.354` | `0.354` |
| 12 months | `-0.062` | `-0.061` | `-0.062` | `-0.062` |
| 24 months | `-0.334` | `-0.334` | `-0.334` | `-0.334` |

Correlation is shown. There is no direct-formula confirmation.

## Routed-State Diagnostic

Train-only raw-topology diagnostic plus routed reservoir state:

| Horizon | Raw topology VAR | Ordinary gate | One rung opposite | Two rungs same | Two-rung null |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3 months | `0.773` | `0.745` | **`0.749`** | `0.745` | `0.739` |
| 6 months | `0.377` | `0.364` | **`0.365`** | `0.363` | `0.362` |
| 9 months | `0.371` | `0.368` | `0.359` | **`0.373`** | `0.360` |
| 12 months | `0.401` | `0.315` | `0.293` | **`0.333`** | `0.312` |
| 18 months | `-0.080` | `-0.136` | `-0.137` | **`-0.117`** | `-0.140` |
| 24 months | `0.061` | `-0.050` | **`-0.045`** | `-0.049` | `-0.061` |

The two-rung same-spin route has a small, directionally consistent edge at
`9-18 months` versus the ordinary gate, the one-rung route, and its delayed
timing null. It does not clearly win at short range or at `24 months`.

The raw joint-topology diagnostic remains stronger overall.

## Mechanical Audit

The routed packet is finite and small:

| Route | Added store | Deposit std dev | Store-change std dev | Release-change std dev | Surface-pressure-change std dev |
| --- | --- | ---: | ---: | ---: | ---: |
| one rung opposite | one-rung store | `0.00633` | `0.04816` | `0.00400` | `0.00266` |
| two rungs same | two-rung store | `0.00242` | `0.02269` | `0.00090` | `0.00062` |

The two-rung surface pressure remains correlated `0.99999987` with the
ordinary recursive-gate pressure. That explains why the direct forecast barely
moves.

## Strict-Causal Checklist

Verified before reporting:

1. **Filtering:** no bandpass, FFT filter, `filtfilt`, or smoothing.
2. **Envelope:** no Hilbert transform.
3. **Leaf pulse:** calculated from a fresh past-only harmonic fit at each
   origin month.
4. **Periods:** declared before the run: `brown=48`, `green=48/phi`.
5. **Storage:** every update at `t+1` uses state and observations from `t` or
   earlier.
6. **Null:** delayed by `30` months; every null value comes from an earlier
   month only.
7. **Diagnostic:** raw leaf values and deposits are excluded from the readout,
   so it must use routed storage and release consequences.
8. **Split:** training targets satisfy `origin + horizon < cutoff`; held-out
   origins satisfy `origin >= cutoff`.

## Interpretation

This test does not establish the same-spin routing law.

It does produce a small hint in the expected slower window:

```text
one-rung opposite route: slightly better near 3-6 months
two-rung same-spin route: slightly better near 9-18 months
```

That shape is compatible with a deeper packet taking longer to return. The
effect is too small and indirect to call confirmed.

The clean next requirement is better measurement, not a larger arbitrary
coefficient:

```text
identify an observed lower-lower reservoir candidate
or use a finer target where the falling packet is not averaged into a month
```

An explicit route-dependent travel delay can be tested after an observed
lower-lower coordinate is available.

## Frozen Longer-Window Extension

The same script was rerun at slower predeclared horizons:

```text
30, 36, 48, 60 months
```

Nothing else changed. The route equation, leaf reader, storage law, gate
equations, chronological split, and `30 month` wrong-time null were frozen.

Train-only raw-topology diagnostic plus routed reservoir state:

| Horizon | Held-out months | Raw topology VAR | Ordinary gate | One rung opposite | Two rungs same | Two-rung null |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 30 months | `188` | `0.053` | `0.212` | **`0.235`** | `0.201` | `0.231` |
| 36 months | `182` | `0.120` | `0.163` | `0.177` | `0.150` | **`0.194`** |
| 48 months | `170` | `0.117` | `0.068` | **`0.083`** | `0.065` | `0.063` |
| 60 months | `158` | `-0.268` | `-0.144` | `-0.153` | **`-0.137`** | `-0.145` |

The slower windows do not reveal a distinct two-rung same-spin return. The
two-rung route stays close to the ordinary gate and the wrong-time null.

The one-rung route has a slightly larger edge around `30-48 months`, but it is
also modest and is not consistently separated from the null. At `60 months`,
the two-rung route is slightly less negative than its comparisons, but the
difference is too small to interpret as a return event.

### Longer-window conclusion

This monthly ENSO proxy does not isolate the proposed two-octave return. That
does not make the orientation geometry invalid. It means the present observed
state cannot discriminate among:

```text
two-rung return already partly encoded in the ordinary equation
upper packet too small after monthly averaging
wrong lower-lower reservoir proxy
real route more complex than a single one-rung versus two-rung switch
```

Do not add a larger fitted packet coefficient to manufacture separation. The
next useful step is measurement: identify a real lower-lower ENSO coordinate
or use finer-than-monthly SST and feeder data.
