# ENSO Recursive Gate Reservoir Test

## Question

Does the corrected recursive recycling model improve strict-causal ENSO
prediction when stored energy is released only at a local handoff gate?

This follows the clarified geometry:

```text
underlying physical ladder: x2, x4, x8, ...
Space-axis reading:         2
Time-axis reading:          2 cos(36 deg) = phi
```

The exact identity `2 cos(36 deg) = phi` is mathematical. The interpretation
that Time is a recursively projected physical octave remains a framework
conjecture.

Script:

```text
ara_enso_recursive_gate_reservoir_test.py
```

Machine-readable result:

```text
ara_enso_recursive_gate_reservoir_result.json
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
stored reservoir state calculated from earlier months
```

It does not see future NINO, future-origin features, a smoothed future
envelope, an analog lookup, or held-out tuning scores.

The `var_plus_*` results below are separate train-only statistical
diagnostics. They are not the direct physical formula.

## Repeated Gate

The same handoff rule is applied at both lower depths:

```text
handoff_gate(local, receiver)
    = recursive_ARA_boundary_pressure(local)
    * projected_phase_window(local, receiver, 36 deg)

release(store, gate)
    = (1 / phi^2) * gate * tanh(abs(store)) * store
```

Adjacent physical contacts reverse orientation. A two-depth return recovers
the original orientation after two reversals.

The store update is:

```text
one_store(t+1)
    = (1 - g^2) * one_store(t)
    + 2g * lower_packet(t)
    - one_release(t)

two_store(t+1)
    = (1 - g^2) * two_store(t)
    + 4g^2 * lower_packet(t)
    - two_release(t)

g = (2 - phi) / 2
```

`g^2` is a conservative first-pass irrecoverable-loss proxy. It is not
claimed as a discovered universal constant.

`WWV east - WWV west` is the observed one-rung coordinate. The lower packet
is still a latent proxy for the lower-lower rung. A better observed candidate
is still needed.

## Compared Variants

Only three reservoir variants were tested:

```text
fixed_release
    old reservoir: energy releases every tick

recursive_gate
    new reservoir: energy stores until the local recursive gate opens

recursive_gate_null
    same stores, but each gate opening is replaced by an earlier gate value
    chosen causally; this preserves rough scale while breaking timing
```

## Direct Formula Result

Headline held-out correlation:

| Horizon | Fixed release | Recursive gate | Causal gate-timing null |
| ---: | ---: | ---: | ---: |
| 3 months | `0.747` | `0.751` | `0.746` |
| 6 months | `0.345` | `0.355` | `0.345` |
| 9 months | `0.056` | `0.062` | `0.059` |
| 12 months | `-0.066` | `-0.061` | `-0.059` |
| 18 months | `-0.151` | `-0.146` | `-0.143` |
| 24 months | `-0.323` | `-0.334` | `-0.321` |

The dynamic gate has a small non-random timing contribution at `3-9 months`,
especially at `6 months`. It does not solve the direct predictor. The direct
formula remains weak beyond the short range.

## Raw Topology Diagnostic

The stronger train-only joint-topology diagnostic remains the better model:

| Horizon | Raw topology VAR | VAR + fixed release | VAR + recursive gate | VAR + gate null |
| ---: | ---: | ---: | ---: | ---: |
| 3 months | `0.854` | `0.849` | `0.844` | `0.820` |
| 6 months | `0.601` | `0.589` | `0.581` | `0.533` |
| 9 months | `0.449` | `0.425` | `0.424` | `0.383` |
| 12 months | `0.444` | `0.444` | `0.389` | `0.379` |
| 18 months | `0.407` | `0.390` | `0.309` | `0.372` |
| 24 months | `0.289` | `0.328` | `0.189` | `0.298` |

Breaking gate timing hurts the short-range diagnostic more than using the
real gate. This supports the narrower statement that the dynamic gate contains
some short-range timing information.

Adding the present gate state still does not improve the raw joint topology
diagnostic. At longer horizons it hurts. The gate is not yet the right route
selector for full ENSO prediction.

## Mechanical Check

The corrected gate behaves as an intermittent gate rather than a continuous
leak:

| State | Mean | Std dev | Maximum |
| --- | ---: | ---: | ---: |
| one-rung gate openness | `0.120` | `0.134` | `0.659` |
| two-rung gate openness | `0.055` | `0.082` | `0.542` |
| one-rung release | `-0.049` | `0.203` | `1.158` |
| two-rung release | `-0.010` | `0.045` | `0.231` |

An initial implementation bug allowed the first unavailable phase value to
propagate `NaN` through the stores. The gate now correctly stays closed when
phase is unavailable, and the reported run contains finite values throughout.

## Strict-Causal Checklist

Verified before reporting:

1. **Filtering:** no bandpass, FFT filter, `filtfilt`, or smoothing.
2. **Phase:** calculated from current level and one-step backward velocity.
3. **Normalization:** fitted on training data only, then applied to held-out
   origins.
4. **Feature selection:** declared before the run; no held-out selection.
5. **AR memory:** no future target and no future-origin feature.
6. **Gate recursion:** each store update at `t+1` uses state and observations
   from `t` or earlier.
7. **Null:** each randomized gate value is sampled from an earlier gate only.
8. **Split alignment:** training targets satisfy `origin + horizon < cutoff`;
   held-out origins satisfy `origin >= cutoff`.

## Interpretation

This test gives a useful narrow result:

```text
continuous release was too crude
dynamic gate timing contains some real short-range information
this WWV-based gate is not yet the complete route selector
```

The next useful refinement is not more free constants. It is to improve the
measured local state at the lower-lower rung and separate:

```text
gate opening
route selection: one-rung return versus two-rung return
cross-rung delay before the returned packet reaches the measured surface
upper-rung leaf-fall shock at the brown-to-green crossover
```

Those are distinct physical jobs. This first dynamic test only opens and
closes the route; it does not yet model its travel time.

## ENSO-Specific Observed Clue

The earlier green/brown ENSO work supplies a plausible observed upper-shock
candidate:

```text
green / gold band: faster quasi-biennial lower feed, roughly 24-33 months
brown band:        slower upper/down-flow, roughly 40-70 months
brown -> green crossover: intermittent falling packet or "leaf-fall"
```

This should not replace the lower WWV gate. It has a different role:

```text
WWV / green lower feed
    = frequent lower-rung input and return timing

brown-to-green leaf-fall
    = occasional dense packet falling from above
    = upper pressure / turbulence event
    = possible route-change or delay disturbance
```

The old `green_brown_E_events.py` and `green_brown_energy_flux.py` diagnostics
used zero-phase FFT bands and Hilbert envelopes. They are valid only as
descriptive clues, not as forecast inputs. Before the leaf-fall enters a
headline predictor, it needs a fresh strict-causal ablation using only
past-fitted brown/green state at each forecast origin and a causal-prior event
timing null.

Follow-up completed:

```text
ARA_ENSO_CAUSAL_LEAF_FALL_RESULT.md
ara_enso_causal_leaf_fall_ablation.py
```

The past-only leaf timing exposes a distinct `24 month` diagnostic lift versus
a closely scale-matched causal lag null, but a direct pressure subtraction does
not improve the physical formula. The next implementation should treat the
leaf as a route-and-delay selector rather than as a smooth amplitude term.
