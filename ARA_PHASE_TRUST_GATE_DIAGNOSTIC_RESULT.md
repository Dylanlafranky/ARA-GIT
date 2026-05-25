# ARA Phase Trust-Gate Diagnostic Result

**Date:** 2026-05-25

This follow-up tests the sharper physical interpretation from the lag/phase hybrid:

```text
lag ridge = carried energy / native-unit inertia
ARA phase-flow = route / timing / turn geometry
coupling energy = trust/confidence or regime context, not direct amplitude correction yet
```

The question is:

```text
When lag and ARA phase-flow disagree, which one is more often right about direction/turn?
```

## Files

- `TheFormula/ara_phase_trust_gate_diagnostic.py`
- `TheFormula/ara_phase_trust_gate_diagnostic_result.json`
- `TheFormula/ara_phase_trust_gate_diagnostic_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- base lag and phase predictions use strict-causal training pairs `s+h<t`.
- the trust selector for origin `t` only uses previous records whose `target_anchor < t`.
- no future actual values are used to decide whether to trust lag or ARA at the current origin.

## Main Result

Across the 6/12/24-month focus window, lag still wins.

The simple causal trust selectors choose lag everywhere because completed past examples do not justify switching to phase under the current bucket rules.

| Model | Mean MAE | Mean corr | Turn acc | ENSO class acc | Transition MAE |
|---|---:|---:|---:|---:|---:|
| `lag_ridge` | `0.623` | `+0.283` | `0.767` | `0.474` | `0.683` |
| `ara_phase_regime_velocity` | `0.768` | `+0.211` | `0.691` | `0.414` | `0.865` |
| `selector_direction` | `0.623` | `+0.283` | `0.767` | `0.474` | `0.683` |
| `selector_mae` | `0.623` | `+0.283` | `0.767` | `0.474` | `0.683` |

## Disagreement Test

When lag and ARA phase-flow disagree in sign, lag is usually the better point forecast.

6/12/24-month disagreement windows:

| Subset | n | Lag turn acc | ARA turn acc | Lag MAE | ARA MAE | Lag-only correct | ARA-only correct |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag/ARA disagree | `53` | `0.634` | `0.366` | `0.635` | `0.891` | `0.634` | `0.366` |
| disagree + transition | `32` | `0.693` | `0.307` | `0.791` | `1.106` | `0.693` | `0.307` |

This answers the sharp question: in the current implementation, disagreement is **not** a reason to switch from lag to ARA phase as the point forecast.

## What Survives

ARA phase disagreement is still useful as a warning flag at 24 months.

At 24 months:

```text
lag wrong rate when lag/ARA disagree:     0.467
lag wrong rate when they do not disagree: 0.128
warning recall for lag-wrong cases:       0.538
```

So disagreement does mark a much riskier lag window, even though phase is not yet accurate enough to replace lag.

There is also a narrow transition signal at 24 months:

| 24-month transition subset | n | Lag turn acc | ARA turn acc | Lag boundary-cross acc | ARA boundary-cross acc | Lag MAE | ARA MAE |
|---|---:|---:|---:|---:|---:|---:|---:|
| actual ENSO class transition | `44` | `0.841` | `0.864` | `0.705` | `0.750` | `0.653` | `0.810` |

That is the useful survivor: ARA phase is not better on amplitude, but it may be detecting some 24-month transition direction/boundary structure.

## Interpretation

The physical decomposition still looks right, but the operational use is narrower:

```text
lag = default amplitude and point forecast
ARA phase = risk/turn/boundary warning channel
coupling energy = confidence/regime selector first, not amplitude correction
```

The current trust gate should not select ARA as a replacement value. A better next version should treat ARA as an uncertainty or boundary-warning layer:

```text
if lag and ARA agree:
    keep lag and raise confidence
if lag and ARA disagree:
    keep lag as the central forecast
    widen the interval
    flag elevated turn/boundary risk
if 24-month transition risk is high:
    let ARA influence class/turn probability, not raw amplitude
```

This is a useful negative result: ARA is not yet the driver; it is a diagnostic channel for where the lag driver may become unreliable.

Follow-up note: the energy/work decomposition test is recorded in `ARA_ENERGY_WORK_DECOMPOSITION_RESULT.md`. It found that energy-route alignment diagnoses cleaner versus riskier work states, especially at 24 months, but the first dissipation proxy and work/error selector do not improve the forecast.
