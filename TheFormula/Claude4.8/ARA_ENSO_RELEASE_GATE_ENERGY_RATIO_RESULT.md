# ENSO Release-Gate and Native WWV-Motion Diagnostic

## Question

Does the possible `12 to 18 month` upward pulse concentrate near a lower-cycle
release/end state? Is it smaller than the later `30 to 34 month` battery
disturbance?

The two windows were frozen before scoring:

| Window | Proposed interpretation |
| --- | --- |
| 12 to 18 months | smaller/faster upward handoff into WWV |
| 30 to 34 months | slower retained-substrate or recycled disturbance |

## Strict-Causal Checklist

| Check | Status |
| --- | --- |
| Brown marker uses NINO values available at or before origin only | Yes |
| Frozen windows unchanged from the previous diagnostic | Yes |
| Gates use the current and previous measured month only | Yes |
| Native monthly WWV motion used without smoothing | Yes |
| Synthetic energy injection | No |
| Formula modified | No |
| FFT or Hilbert phase | No |
| Future value used to construct marker | No |

## Important Measurement Limit

WWV is a warm-water-volume proxy, not energy in joules. The ratios below are
ratios of measured WWV volume motion. They are **not** percentages of energy
passed upward or left behind.

The available record still does not contain a proven measured rung directly
beneath WWV.

## Transparent Release Gates

| Gate | Rule |
| --- | --- |
| IOD lateral magnitude release | active IOD magnitude moves toward zero |
| MJO candidate burst release | above-median MJO activity starts falling |
| WWV battery discharge | above-median WWV battery starts falling |

Each gate uses only the current and immediately previous month.

## Earlier Visible Period

The visible pre-cutoff period contains a sustained `12 to 18 month` WWV
discharge episode:

| Native WWV motion | Early `12–18m` | Late `30–34m` | Early / late |
| --- | ---: | ---: | ---: |
| total absolute battery motion | `2.636` | `1.717` | `1.535` |
| mean absolute battery motion per month | `0.377` | `0.343` | `1.096` |
| total absolute east-west orientation motion | — | — | `1.638` |

The earlier pulse lasts seven months, so its total motion is larger. Its
month-by-month motion is only about `1.10x` the later pulse.

The WWV battery-discharge gate is concentrated around that earlier pulse:

| WWV discharge measurement | Early `12–18m` | Late `30–34m` |
| --- | ---: | ---: |
| plain gate-open fraction | `0.273` | `0.276` |
| marker-weighted gate-open fraction | **`0.467`** | `0.250` |
| concentration lift | **`1.712x`** | `0.905x` |
| native motion, gate open / closed | `1.242x` | `1.067x` |

The marker-weighted early battery motion is signed negative (`-0.888`), which
is consistent with discharge in this earlier period.

The IOD and MJO release gates themselves do not concentrate strongly around the
marker-weighted early pulse in this simple one-month gate test.

## Held-Out Period

The earlier WWV-discharge signature does not repeat:

| Native WWV motion | Early `12–18m` | Late `30–34m` | Early / late |
| --- | ---: | ---: | ---: |
| total absolute battery motion | `2.152` | `1.681` | `1.280` |
| mean absolute battery motion per month | `0.307` | `0.336` | `0.914` |
| total absolute east-west orientation motion | — | — | `1.216` |

The held-out early pulse has slightly **less** WWV motion per month than the
later disturbance. None of the three simple release gates isolates a strong
held-out handoff:

| Gate | Early concentration lift | Late concentration lift |
| --- | ---: | ---: |
| IOD lateral magnitude release | `1.082x` | `0.742x` |
| MJO candidate burst release | `0.911x` | `1.142x` |
| WWV battery discharge | `0.797x` | `0.979x` |

## Conclusion

The earlier visible `12 to 18 month` pulse does look like a real WWV discharge
episode: broad, signed toward discharge, and concentrated at the WWV release
gate. That is compatible with an upward handoff.

However, the exact gate signature does not repeat in held-out time. The
current monthly proxy therefore does **not** establish a stable release law or
a logarithmic energy split.

The proposed “quarter left behind” idea is not measured here. In native WWV
volume motion, the early pulse is not one quarter of the later pulse. The data
may be measuring duration and battery reconfiguration rather than the energy
share passed between rungs.

The narrow supported statement is:

> One earlier era contains a WWV discharge-shaped handoff. A later era contains
> a different slower battery disturbance. The monthly WWV ruler distinguishes
> the episodes, but it does not yet measure a universal upward-versus-retained
> energy ratio.

## Next Test

Use a directly measured finer-grain candidate beneath WWV:

```text
equatorial wind-burst events
thermocline-depth changes
trade-wind stress
upper-ocean heat-content changes
```

Then ask whether those events precede the WWV discharge gate and whether the
handoff fraction is stable across cycles.

## Files

Script:

```text
TheFormula/Claude4.8/ara_enso_release_gate_energy_ratio_test.py
```

Machine-readable result:

```text
TheFormula/Claude4.8/ara_enso_release_gate_energy_ratio_result.json
```
