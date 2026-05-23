# ARA Temporal Friction And Pocket Tests - 2026-05-23

## Why this was run

The latest prediction work kept circling the same missing operator:

```text
geometry(t) -> future geometry(t+h) -> value(t+h)
```

Directly regressing geometry to a future value was too blunt. The next question was whether the missing operator is a temporal-flow law: how far the current geometry is allowed to move through its natural phase advance.

The working formula was:

```text
flow = ARA / (ARA + temporal_friction)
```

That led to two hypotheses:

1. Temporal friction may be related to distance from phi, because phi is the least-locking / lowest-friction packing route through time.
2. A negative phi-distance coefficient may not be a bad fit; it may mark a temporal pocket where opposing time waves cancel part of the friction and allow a surge.

## Files

Core result files:

- `TheFormula/ara_retroactive_flow_test.py`
- `TheFormula/ara_retroactive_flow_data.js`
- `TheFormula/ara_temporal_friction_diagnostic.py`
- `TheFormula/ara_temporal_friction_data.js`
- `TheFormula/ara_causal_friction_prediction_test.py`
- `TheFormula/ara_causal_friction_prediction_data.js`
- `TheFormula/ara_phi_distance_friction_test.py`
- `TheFormula/ara_phi_distance_friction_data.js`
- `TheFormula/ara_phi_distance_bk_fit_test.py`
- `TheFormula/ara_phi_distance_bk_fit_data.js`
- `TheFormula/ara_temporal_pocket_diagnostic_test.py`
- `TheFormula/ara_temporal_pocket_diagnostic_data.js`
- `TheFormula/ara_enso_coupled_pocket_visibility_test.py`
- `TheFormula/ara_enso_coupled_pocket_visibility_data.js`

Related state-geometry files:

- `TheFormula/ara_geometry_state_transition_test.py`
- `TheFormula/ara_geometry_state_transition_data.js`
- `TheFormula/ara_gear_coupled_transition_test.py`
- `TheFormula/ara_gear_coupled_transition_data.js`

## Leakage Guard

All causal tests used closed-window training:

```text
At origin t and horizon h:
  - coefficient/transition training uses only windows s where s+h < t
  - decoder training uses only geometry anchors a < t
  - future geometry at t+h is used only as an oracle diagnostic or as a past target after it is closed
```

The temporal-pocket diagnostic also follows this rule. Its `k` marker is causal; the future surge is scored only as an outcome.

## Result 1 - Retroactive Flow Is Real, But It Is Not A Single Constant

The retroactive flow diagnostic solved the best scalar natural-flow alpha:

```text
future_geometry ~= current_geometry + alpha * (natural_advance - current_geometry)
```

For ENSO, the mean alpha was consistently around `0.6-0.7`:

| Horizon | Mean alpha |
|---:|---:|
| 1 month | 0.606 |
| 3 months | 0.721 |
| 6 months | 0.722 |
| 12 months | 0.652 |
| 24 months | 0.665 |
| 60 months | 0.632 |

This is close to `phi - 1 = 0.618`, especially as a broad attractor. But the state-by-state residuals were not constant, so a fixed phi-flow is not enough.

Interpretation:

```text
There is a real natural-flow direction in ARA geometry.
Phi-like flow is a useful baseline.
The missing piece is state-dependent temporal friction / cancellation.
```

## Result 2 - Gear Coupling Exposes The Energy Pi-Leak

The gear-style anti-phase transition tested:

```text
incoming_phase = 2 * release_fraction(target_ara) - source_phase
```

The direct forecast did not beat causal lag. But the gear-minus-sync alignment difference sat near:

```text
0.0448 to 0.0471
```

That is very close to:

```text
(pi - 3) / pi = 0.045070341
```

This supports Dylan's distinction:

| Quantity | Value | Current interpretation |
|---|---:|---|
| `pi - 3` | `0.141592654` | topology strand / crack / geometric non-closure |
| `(pi - 3) / pi` | `0.045070341` | normalized energy leakage through that strand per coupling/tick |

Earlier notes often called both of these "pi-leak." Going forward they should be separated:

```text
pi - 3          = geometry leak / topology remainder
(pi - 3) / pi  = energy leak / normalized coupling tax
```

## Result 3 - `friction = |ARA - phi|` Is Not Supported Literally

The pure phi-distance friction test tried:

```text
friction = |ARA - phi|
```

That performed badly. The reason is mechanical: near phi, friction approaches zero, so the model over-advances the geometry.

The better simple version was:

```text
friction = 1 + |ARA - phi|
```

This improved over fixed friction at several ENSO horizons, but it still did not beat lag or the oracle future-geometry decoder.

Interpretation:

```text
Phi-distance is not temporal friction by itself.
Phi-distance is a modulation around a baseline temporal resistance.
```

## Result 4 - `B + k*|ARA-phi|` Is Mixed Across Domains

The next test fit:

```text
temporal_friction = B + k * |ARA - phi|
```

It was run as a single-signal, universal architecture on:

- ENSO NINO3.4
- SILSO monthly solar sunspots
- ECG `nsr001` RR intervals at 10-second resolution

The unconstrained fit often made `k` negative. At first that looked mathematically ugly, because a literal drag model expects `k >= 0`. But the better interpretation is:

```text
positive k = phi-distance acts like drag
negative k = resonance/collision cancels effective friction
```

A constrained physical fit (`B >= 0`, `k >= 0`) often collapsed to `k = 0`, and a stricter floor (`B >= 1 + pi-leak`) often did the same. So the data does not support "phi-distance always adds drag." It supports "phi-distance participates in a drag/cancellation balance."

Forecast summary:

- ENSO: geometry/friction models contain signal, but lag still wins.
- Solar: geometry/friction works best around the 60-month horizon; several geometry models beat persistence and lag there.
- ECG RR: short and mid horizons show some signal, but long horizons remain weak.

## Result 5 - Temporal Pockets Are Partly Supported, Not Universal

The temporal-pocket diagnostic treated negative `k` as a possible causal pocket marker:

```text
pocket_strength = max(0, -k)
```

It then asked whether stronger pocket markers correspond to:

- larger same-horizon movement
- larger next-horizon movement
- release-boundary states
- anti-phase rung collision / gear-contact geometry

The result is mixed.

### Supportive pockets

Solar at the 132-month horizon:

| Metric | Value |
|---|---:|
| negative-k share | 1.00 |
| corr(pocket, absolute same-horizon delta) | +0.355 |
| corr(pocket, anti-phase energy) | +0.333 |
| strong-pocket / weak-pocket delta ratio | 3.41 |

ECG RR at the 6-sample horizon (`60s`):

| Metric | Value |
|---|---:|
| negative-k share | 1.00 |
| corr(pocket, absolute same-horizon delta) | +0.102 |
| corr(pocket, absolute next-horizon delta) | +0.477 |
| corr(pocket, gear-contact energy) | +0.181 |
| strong-pocket / weak-pocket same-horizon delta ratio | 1.36 |
| strong-pocket / weak-pocket next-horizon delta ratio | 2.71 |

These are consistent with the temporal-pocket idea: the cancellation marker appears near anti-phase/contact geometry and is followed by larger movement.

### Non-supportive or weak pockets

ENSO did not show the same pattern:

- h=1, h=3, h=12, and h=24 mostly showed negative or weak correlations between pocket strength and future movement.
- h=60 was only weakly positive for same-horizon movement and next movement.

Solar h=60 also did not support a surge interpretation despite strong geometry forecast skill.

Interpretation:

```text
Negative k is not a universal surge marker.
It may mark a temporal pocket only when the system is near a compatible collision/contact state.
```

The next version should not use `k < 0` alone. It should require a conjunction:

```text
temporal_pocket =
  negative phi-distance coefficient
  AND anti-phase/contact geometry
  AND release/snap boundary proximity
```

## Result 6 - ENSO Pocket Visibility Depends On Coupling Completeness

After the first pocket diagnostic, Dylan suggested that ENSO may not show visible surge pockets because it is already a strongly coupled/resonant measured system. NINO3.4 is not a lone surface readout; it is part of the NINO/SOI/Walker exchange. If that exchange is already well coupled, a temporal pocket may be absorbed as damping instead of appearing as a visible surge.

The follow-up test split ENSO origins by NINO/SOI coupling completeness and tested two causal pocket markers:

- `single_nino_k`: `k` fit from NINO-only geometry.
- `coupled_enso_k`: `k` fit from full NINO/SOI/PDO geometry.

The coupling metric used only origin-time geometry: same-rung anti-phase energy, center anti-phase, center proximity, and energy balance.

### Main coupling result

Low NINO/SOI closure had larger measured NINO movement than high closure at every horizon:

| Horizon | Low-closure / high-closure absolute movement |
|---:|---:|
| 1 month | 1.10 |
| 3 months | 1.13 |
| 6 months | 1.27 |
| 12 months | 1.59 |
| 24 months | 1.58 |
| 60 months | 1.28 |

This supports the coupling-completeness part of the hypothesis:

```text
strong NINO/SOI closure -> movement is buffered/damped
weak NINO/SOI closure   -> movement is more visible in NINO
```

### Pocket-specific interaction

The pocket interaction was mixed at short horizons, but it appeared at the longer ENSO windows.

For the NINO-only pocket marker:

| Horizon | Low-closure pocket -> movement | High-closure pocket -> movement |
|---:|---:|---:|
| 12 months | +0.059 | -0.326 |
| 24 months | +0.216 | -0.215 |

For the full coupled-ENSO pocket marker:

| Horizon | Low-closure pocket -> movement | High-closure pocket -> movement |
|---:|---:|---:|
| 24 months | +0.232 | -0.236 |
| 60 months | +0.154 | -0.043 |

Interpretation:

```text
In ENSO, negative-k pockets are not generally visible as surges.
They become more surge-like when NINO/SOI closure is weak.
They become damping-like when NINO/SOI closure is strong.
```

This is consistent with the idea that ENSO's measured rung is already coupled and resonant. Solar and ECG RR may show cleaner visible pockets because those measured series are partial surface readouts of deeper coupled systems, while NINO/SOI includes more of the counter-system directly.

## Current Formula Sketch

The latest interpretation is:

```text
temporal_friction =
    baseline_time_resistance
  + pi_leak_energy
  + system_inefficiency
  + phi_distance_drag
  - resonance_cancellation
```

Where:

- `baseline_time_resistance` is the floor that prevents friction going to zero.
- `pi_leak_energy = (pi - 3) / pi` is the normalized coupling/tick leakage.
- `system_inefficiency` is dataset/state-specific residual friction.
- `phi_distance_drag` is the cost of being away from the least-locking phi route.
- `resonance_cancellation` is the temporary low-friction pocket created when opposing waves collide compatibly.

For `ARA = 2.0`, the interpretation is not "no friction." It is resonance:

```text
ARA = 2.0 still has entropy/friction,
but two opposing waves can cancel part of it,
arriving at a low-friction result by collision rather than by phi packing.
```

## Status

Supported:

- ARA future geometry is decodable; oracle future-geometry decoders are strong.
- Retroactive natural flow exists and sits near phi-like flow.
- The normalized energy pi-leak signal around `0.045` appears in gear-vs-sync diagnostics.
- `1 + |ARA - phi|` is better than pure `|ARA - phi|`.

Not supported as stated:

- "Temporal friction is just `|ARA - phi|`."
- "Negative k always means a surge."
- "The current forward geometry transport beats lag on ENSO."

Promising but provisional:

- Negative `k` as a temporal-pocket marker when paired with anti-phase/contact geometry.
- ENSO pocket visibility depends on coupling completeness: low NINO/SOI closure exposes movement, high closure damps it.
- The distinction between topology pi-leak (`pi - 3`) and energy pi-leak (`(pi - 3)/pi`).
- A friction law that includes both phi-distance drag and resonance cancellation.
