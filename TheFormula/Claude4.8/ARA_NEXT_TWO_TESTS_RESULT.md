# ARA Next Two Tests: Recycling Landmark + Joint ENSO Topology

## Scope

Two strict-causal follow-on tests were run after the first vector-pose prototype:

1. Does the repeated-recycling interpretation of the `2 - phi` landmark improve
   future-pose prediction?
2. Does ENSO direction prediction improve when the climate system is advanced
   as a connected multi-coordinate topology rather than one NINO line?

Scripts:

* `ara_recycling_landmark_ablation.py`
* `ara_joint_enso_topology_direction_test.py`

Machine-readable results:

* `ara_recycling_landmark_ablation_result.json`
* `ara_joint_enso_topology_direction_result.json`

## Test 1: Recycling Landmark Ablation

Both branches use the same origin-safe local recycling proxy:

```text
rho_t = abs(corr(recent trailing block, one-period-earlier trailing block))
```

The comparison is:

```text
simple:
    retention = rho

repeated:
    B = 2 - phi
    effective_loss = B * (1 - rho) / (1 - rho * B)
    retention = 1 - effective_loss
```

### Result

The repeated-recycling branch does **not** improve the direct future-pose
forecast. It is nearly neutral at short horizons and usually worse as the
forecast path gets longer.

Selected direct-pose scores are `correlation / MAE / direction accuracy`:

| System | Horizon | Simple retention | Repeated recycling |
| --- | ---: | --- | --- |
| Solar | 12 months | `0.613 / 52.258 / 0.547` | `0.614 / 52.277 / 0.547` |
| Solar | 96 months | `0.012 / 218.348 / 0.529` | `0.009 / 230.802 / 0.529` |
| ENSO | 12 months | `-0.025 / 1.071 / 0.534` | `-0.026 / 1.076 / 0.539` |
| ECG | 5 beats | `0.573 / 55.323 / 0.504` | `0.566 / 55.633 / 0.500` |
| ECG | 13 beats | `0.372 / 69.007 / 0.478` | `0.343 / 71.226 / 0.468` |

### Interpretation

`2 - phi` remains useful as the **one-pass bedrock shed landmark**. This test
does not support automatically converting the local autocorrelation proxy into
a repeated-pass retention value inside the predictor.

That does not falsify recycling. It rejects this mechanically incomplete shortcut:

```text
diverted energy immediately returns through the same junction
local trailing autocorrelation == fraction of shed energy returned
```

The corrected framework architecture routes recyclable energy downward into smaller,
faster rung systems before some works upward again. The falling packet becomes denser
relative to the capacity of the smaller receiving system. A two-rung-down route may
also be required to recover matching spin. Those quantities may be related without
being numerically identical.

See:

```text
../../EnergyRatio/ARA_CROSS_RUNG_RECYCLING_MODEL.md
```

## Test 2: Joint ENSO Topology

The joint topology contains six causal sphere coordinates:

| Node | Role |
| --- | --- |
| NINO3.4 | measured surface target |
| SOI | matched-rung partner |
| WWV west | faster lower feeder |
| WWV east | faster lower feeder |
| IOD | lower feeder |
| PDO | slower upper constraint |

Every node advances on its own sphere surface. The graph compares:

```text
independent: nodes advance without contact transfer
same:        contacts pull in the same orientation
parity:      every declared contact flips orientation
```

Direction accuracy is the primary score. Correlation and MAE remain recorded.

### Direct Mechanics Result

Blanket alternating parity is **not supported**.

| Horizon | Independent direction | Same-direction contact | Blanket parity |
| ---: | ---: | ---: | ---: |
| 3 months | `0.595` | `0.628` | `0.484` |
| 6 months | `0.580` | `0.627` | `0.439` |
| 12 months | `0.476` | `0.534` | `0.383` |
| 18 months | `0.525` | `0.580` | `0.420` |

The direct contact-transfer implementation remains preliminary, but it gives a
clear correction: not every observed ENSO edge should receive the same
orientation flip. Physical layer-to-layer roll, matched-rung anti-phase, and
index sign convention must be represented separately.

### Joint-State Diagnostic Result

The raw multi-coordinate causal climate state improves exact prediction over
NINO-only home lags from 3 to 18 months:

| Horizon | NINO home AR corr | Raw topology VAR corr |
| ---: | ---: | ---: |
| 3 months | `0.834` | `0.854` |
| 6 months | `0.554` | `0.601` |
| 9 months | `0.326` | `0.449` |
| 12 months | `0.331` | `0.444` |
| 18 months | `0.306` | `0.407` |

The arrived pose packet carries useful direction information:

| Horizon | Useful joint-pose branch | Direction accuracy |
| ---: | --- | ---: |
| 3 months | raw VAR + same-contact pose | `0.726` |
| 6 months | raw VAR + same-contact pose | `0.750` |
| 9 months | raw VAR + same-contact pose | `0.780` |
| 12 months | independent pose readout | `0.816` |
| 18 months | parity pose readout | `0.810` |
| 24 months | same-contact pose readout | `0.820` |

No single contact convention wins every horizon. This is evidence against a
global sign switch and in favor of typed edges or regime-dependent contact.

## Leakage Boundary

Both tests are strict-causal:

* topology inputs at origin `t` use raw observations from `t` or earlier;
* local recycling uses trailing blocks ending at `t`;
* graph advancement does not inspect future observations;
* chronological training origins satisfy `origin + horizon < cutoff`;
* held-out origins satisfy `origin >= cutoff`;
* direct formula scores are separated from train-only readout diagnostics.

## Best Next Step

The next mathematical refinement should be **typed contact edges plus explicit
lower-rung reservoirs**, not more global constants:

```text
lower physical contact:
    orientation flip through rolling layer contact

lower reservoir:
    receives recyclable diverted flow
    returns it upward after a causal delay

two-rung-down reservoir:
    candidate same-spin recycling route

matched-rung pair:
    anti-phase relation in its own measurement frame

upper slow shell:
    grip / brake / constraint, not a uniform directional push

index polarity:
    declared observation convention, separate from physical spin
```

Then rerun the same joint ENSO direction test. The current result says the
multi-coordinate architecture is useful, while the uniform parity rule is too
coarse.
