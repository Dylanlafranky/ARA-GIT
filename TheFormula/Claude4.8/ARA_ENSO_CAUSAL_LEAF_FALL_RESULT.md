# ENSO Causal Leaf-Fall Ablation

## Question

Does the earlier brown-to-green crossover supply a useful observed upper-shock
channel for the strict-causal recursive reservoir?

This tests the ENSO-specific interpretation:

```text
WWV / green lower feed
    = frequent lower-rung input and return timing

brown-to-green leaf-fall
    = occasional dense packet falling from above
    = upper pressure / turbulence event
```

Script:

```text
ara_enso_causal_leaf_fall_ablation.py
```

Machine-readable result:

```text
ara_enso_causal_leaf_fall_ablation_result.json
```

## Formula Visibility

At forecast origin month `t`, the direct formula sees only current or earlier:

```text
NINO
SOI
WWV west
WWV east
IOD
PDO
stored recursive-gate reservoir state
past-only raw-NINO green/brown harmonic fit
```

It does not see future NINO, full-series FFT bands, Hilbert envelopes,
future-origin features, analog lookups, or held-out tuning scores.

This is a retrospective held-out forecast test with a fixed chronological
split. It is not a blind live forecast made before the held-out years occurred.

The `var_plus_*` rows below are separate train-only ridge diagnostics. They ask
whether the declared state exposes useful information. They are not the direct
physical formula.

## Causal Leaf Reader

The older green/brown descriptive scripts used full-series FFT band isolation
and Hilbert envelopes. Those remain descriptive evidence only. They are not
used here.

This test uses two geometry-declared periods:

```text
brown = home period       = 48 months
green = home period / phi = 29.666... months
```

At each month, the script refits the declared two-wave basis using only raw NINO
observed by that month. The current leaf pulse is:

```text
brown_shed
    = max(0, brown(t-1) - brown(t))

crossover_proximity
    = exp(-abs(brown(t) - green(t)))

leaf(t)
    = tanh(brown_shed) * crossover_proximity
```

The upper packet is applied as pressure and braking, not as steady fuel:

```text
leaf_brake = 1 + leaf / phi

pressure_with_leaf
    = (recursive_gate_pressure - g * leaf) / leaf_brake

g = (2 - phi) / 2
```

## Compared Variants

Only three variants were tested:

```text
recursive_gate
    lower recursive reservoir only

causal_leaf
    same lower reservoir plus real past-only leaf pressure

causal_leaf_null
    same leaf series delayed by one green rung:
    round(48 / phi) = 30 months
```

The null uses only earlier values. It keeps pulse shape and scale close while
moving the same leaf events to the wrong times.

## Direct Formula Result

Headline held-out correlation:

| Horizon | Recursive gate | + real causal leaf | + delayed leaf null |
| ---: | ---: | ---: | ---: |
| 3 months | `0.751` | `0.750` | `0.751` |
| 6 months | `0.354` | `0.353` | `0.355` |
| 9 months | `0.062` | `0.061` | `0.063` |
| 12 months | `-0.062` | `-0.062` | `-0.061` |
| 18 months | `-0.146` | `-0.146` | `-0.145` |
| 24 months | `-0.334` | `-0.334` | `-0.333` |

The current direct pressure insertion does essentially nothing. It is too
small and too blunt. The leaf should not yet be treated as a solved amplitude
term.

## State Diagnostic

Train-only raw-topology diagnostic plus each declared reservoir state:

| Horizon | Raw topology VAR | + recursive gate | + real causal leaf | + delayed leaf null |
| ---: | ---: | ---: | ---: | ---: |
| 3 months | `0.773` | `0.745` | `0.688` | `0.614` |
| 6 months | `0.377` | `0.364` | `0.378` | `0.355` |
| 9 months | `0.371` | `0.368` | `0.353` | `0.356` |
| 12 months | `0.401` | `0.315` | `0.202` | `0.367` |
| 18 months | `-0.080` | `-0.136` | `-0.199` | `-0.145` |
| 24 months | `0.061` | `-0.050` | **`0.115`** | `-0.032` |

The first-pass leaf state is not a general improvement. It harms several
intermediate horizons.

However, at `24 months`, the real leaf timing produces a distinct diagnostic
lift:

```text
recursive gate only:  -0.050
real causal leaf:     +0.115
delayed leaf null:    -0.032
```

That is consistent with an upper slower-rung event carrying longer-horizon
route or turbulence information. It is not yet proof: this is one
chronological split and a train-only readout, not a working physical forecast.

## Null Audit

The cleaned causal lag null has closely matched pulse scale:

| Segment | Series | Mean | Std dev | Maximum | Months above `0.05` |
| --- | --- | ---: | ---: | ---: | ---: |
| training | real leaf | `0.01540` | `0.02223` | `0.08791` | `14` |
| training | delayed null | `0.01499` | `0.02236` | `0.08791` | `14` |
| held-out | real leaf | `0.01372` | `0.01622` | `0.05322` | `2` |
| held-out | delayed null | `0.01163` | `0.01600` | `0.05322` | `2` |

The held-out real/null leaf correlation is `-0.561`, so the null moves the
events to materially different times without changing their basic scale.

An earlier random-prior null was rejected before reporting because its
held-out pulse scale did not match the real leaf series closely enough.

## Strict-Causal Checklist

Verified before reporting:

1. **Filtering:** no bandpass, FFT filter, `filtfilt`, or smoothing.
2. **Envelope:** no Hilbert transform and no future envelope.
3. **Leaf state:** each harmonic fit at month `t` uses raw NINO months `<= t`
   only.
4. **Periods:** declared from framework geometry before the run:
   `brown=48`, `green=48/phi`. No full-series spectral peak selection.
5. **Normalization:** fitted on the training segment only.
6. **Null:** delayed by `30` months; every null value comes from an earlier
   month only.
7. **Split alignment:** training targets satisfy `origin + horizon < cutoff`;
   held-out origins satisfy `origin >= cutoff`.

## Interpretation

The clean read is:

```text
the brown-to-green crossover is a plausible upper-shock marker
its useful information appears at the slower 24-month horizon
it is not correctly used by a simple direct pressure subtraction
```

The next useful test should stop treating the leaf as an amplitude correction.
Use it as a **route and delay selector**:

```text
normal months
    -> ordinary lower recursive return

leaf-fall month
    -> packet is diverted deeper or delayed
    -> later return uses the two-rung same-spin route
```

That is closer to the framework description and to the diagnostic result.

Follow-up route test completed:

```text
ARA_ENSO_LEAF_SAME_SPIN_ROUTE_RESULT.md
ara_enso_leaf_same_spin_route_ablation.py
```

After removing the raw-leaf shortcut from the diagnostic, the two-rung
same-spin route shows only a small `9-18 month` edge. It is compatible with the
geometry but not strong enough to confirm it.
