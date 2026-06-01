# ENSO Cross-Rung Reservoir Ablation

## Question

Does an explicit lower-rung recycling path improve strict-causal ENSO
prediction?

The tested geometry keeps the two axis readings distinct while using one
underlying octave ladder:

```text
intrinsic octave ladder: x2, x4, x8, ...
Space-axis reading:      2
Time-axis reading:       2 cos(36 deg) = phi
```

The exact identity is mathematical. The interpretation that physical Time is
the same octave viewed through a fixed `36 degree` shear remains a framework
conjecture.

The Space-to-Time width mismatch is:

```text
G = 2 - phi
g = (2 - phi) / 2       # normalized one-pass diverted share
```

Script:

```text
ara_enso_cross_rung_reservoir_test.py
```

Machine-readable result:

```text
ara_enso_cross_rung_reservoir_result.json
```

## Minimal Tested Reservoir

This is a first proxy, not the complete cross-rung model.

```text
one_store(t+1)
    = (1 / phi) * one_store(t)
    + 2 * g * lower_packet(t)

two_store(t+1)
    = (1 / phi) * two_store(t)
    + 4 * g^2 * one_store(t)

one_release(t) = (1 / phi^2) * one_store(t)
two_release(t) = (1 / phi^2) * two_store(t)
```

`WWV east - WWV west` is used as the observed lower-reservoir orientation
signal. SOI is the matched atmospheric partner. IOD is an additional feeder.
PDO acts as upper-shell grip.

The four compared variants are:

```text
no reservoir
one-rung reservoir
one-rung + two-rung reservoir
one-rung + causal randomized-prior two-rung null
```

The null replaces each two-rung release with an earlier two-rung value only.
It preserves scale but breaks timing without accessing future data.

## Result

The minimal reservoir model did **not** improve correlation over the raw joint
topology state. The two-rung return did not distinguish itself from the causal
null.

Headline held-out correlation:

| Horizon | Raw joint topology | + one-rung | + one + two rungs | + null two-rung |
| ---: | ---: | ---: | ---: | ---: |
| 3 months | `0.854` | `0.847` | `0.849` | `0.835` |
| 6 months | `0.601` | `0.593` | `0.589` | `0.569` |
| 9 months | `0.449` | `0.426` | `0.425` | `0.407` |
| 12 months | `0.444` | `0.443` | `0.444` | `0.439` |
| 18 months | `0.407` | `0.400` | `0.390` | `0.393` |
| 24 months | `0.289` | `0.336` | `0.328` | `0.337` |

The 24-month lift is not attributable to the two-rung path because the causal
null is equally strong. It may reflect generic additional lagged state rather
than the proposed recycling geometry.

The direct fixed-pressure forecast is also poor. For example, at 12 months:

```text
direct no-reservoir corr = -0.063
direct one-rung corr     = -0.065
direct two-rung corr     = -0.066
```

## What This Rejects

This test rejects the specific minimal proxy:

```text
surface NINO spin + WWV east-west
    -> fixed phi-duty reservoir recurrence
    -> fixed one-rung minus / two-rung plus return
```

It does not reject cross-rung recycling generally. The likely missing pieces
are now more specific:

* the actual lower-lower system was latent rather than measured;
* reservoir release probably needs a gate, not release on every tick;
* the gate should depend on local ARA terrain and phase alignment;
* one-rung versus two-rung routing should be selected dynamically;
* the packet shed from the upper sphere may need a better observable than
  instantaneous NINO spin;
* WWV east-west may measure one reservoir coordinate without measuring the
  full lower topology.

## Strict-Causal Checklist

Verified before reporting:

1. **Filtering:** no bandpass, FFT filter, `filtfilt`, or smoothing.
2. **Phase / envelope:** no Hilbert transform or future envelope.
3. **Normalization:** means and standard deviations fitted on training data
   only, then applied to held-out data.
4. **Feature selection:** fixed declared inputs and phi-derived constants; no
   held-out selection.
5. **AR memory:** none.
6. **Rolling logic:** every reservoir update at `t+1` uses state and raw
   observations from `t` or earlier.
7. **Split alignment:** training targets satisfy `origin + horizon < cutoff`;
   held-out origins satisfy `origin >= cutoff`.

## Next Refinement

Do not add more constants. The next reservoir test should add a **dynamic gate**:

```text
release only when:
    lower reservoir phase reaches handoff window
    AND receiving sphere terrain is open
    AND orientation route is compatible
```

It should also seek an observed candidate for the lower-lower reservoir rather
than treating the two-rung state as purely latent.
