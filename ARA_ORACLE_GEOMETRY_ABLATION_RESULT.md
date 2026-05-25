# ARA Oracle Geometry Ablation Result

**Date:** 2026-05-24

This is a diagnostic follow-up to `ARA_GEOMETRY_ANALOG_FLOW_RESULT.md`.

The analog-flow predictor showed:

```text
future geometry -> decoder -> NINO
```

has signal, but:

```text
current geometry -> analog future geometry
```

is currently the weak link.

This script asks which actual future geometry fields carry the oracle decoder signal.

## Files

- `TheFormula/ara_oracle_geometry_ablation.py`
- `TheFormula/ara_oracle_geometry_ablation_result.json`
- `TheFormula/ara_oracle_geometry_ablation_result.js`

## Important Guardrail

This is not a forecast.

For origin `t` and horizon `h`:

- geometry snapshots use only `data[:anchor]`.
- decoder training uses only anchors `a < t`.
- actual future geometry `S(t+h)` is used only as an oracle diagnostic input.
- no score in this file should be quoted as strict predictive skill.

## Full Oracle Decoder

Using the full compact future geometry state:

| Horizon | MAE | Corr | Direction |
|---:|---:|---:|---:|
| 1 mo | `0.453` | `+0.793` | `0.522` |
| 3 mo | `0.533` | `+0.730` | `0.681` |
| 6 mo | `0.602` | `+0.690` | `0.824` |
| 12 mo | `0.630` | `+0.669` | `0.773` |
| 24 mo | `0.579` | `+0.765` | `0.871` |
| 60 mo | `0.845` | `+0.646` | `0.740` |

Mean across all horizons:

```text
MAE  = 0.607
corr = +0.715
direction = 0.735
```

Mean across the key 6/12/24 month transition band:

```text
MAE  = 0.604
corr = +0.708
direction = 0.822
```

## Strongest Group-Only Signals

Mean score across the 6/12/24 month band:

| Future geometry group only | Mean corr | Mean MAE | Read |
|---|---:|---:|---|
| `nino_phase` | `+0.622` | `0.553` | strongest single geometry group |
| `soi_phase` | `+0.608` | `0.550` | nearly as strong; confirms paired anti-phase geometry matters |
| `nino_pdo_coupling` | `+0.369` | `0.679` | slower/environmental coupling carries secondary signal |
| `nino_soi_coupling` | `+0.305` | `0.662` | coupled partner gate carries signal, but less than phase |
| `soi_energy_rung` | `+0.243` | `0.661` | counter-system energy/rung helps |
| `nino_energy_rung` | `+0.223` | `0.685` | modest alone, important in combination |

The big surprise is how much the future decoder can do from phase alone. Future NINO phase and future SOI phase are the cleanest oracle variables.

## Most Damaging Removals

These are the groups whose removal damages the full decoder most across the 6/12/24 month band:

| Removed group | Corr drop | MAE increase | Read |
|---|---:|---:|---|
| `nino_energy_rung` | `+0.062` | `+0.082` | not strongest alone, but important as amplitude/rung context |
| `soi_phase` | `+0.052` | `+0.028` | counter-phase is structurally important |
| `nino_phase` | `+0.052` | `-0.012` | important for correlation; MAE interaction is not monotonic |
| `nino_soi_coupling` | `+0.031` | `+0.019` | partner coupling gate contributes |
| `nino_regime_orientation` | `+0.020` | `+0.013` | build/release orientation helps but is not primary |

## Strongest Individual Fields

Mean score across the 6/12/24 month band:

| Future field | Mean corr | Mean MAE |
|---|---:|---:|
| `soi_phase_cos` | `+0.642` | `0.547` |
| `nino_phase_cos` | `+0.559` | `0.561` |
| `nino_pdo_coupling_energy_log` | `+0.470` | `0.614` |
| `soi_pdo_coupling_energy_log` | `+0.377` | `0.630` |
| `nino_amplitude_energy_log` | `+0.369` | `0.643` |
| `nino_soi_coupling_energy_log` | `+0.315` | `0.654` |
| `pdo_phase_cos` | `+0.275` | `0.649` |
| `nino_weighted_k` | `+0.247` | `0.657` |
| `nino_rung_position` | `+0.231` | `0.662` |
| `soi_amplitude_energy_log` | `+0.229` | `0.663` |

## Interpretation

The future geometry decoder is mostly reading:

```text
phase position
+ counter-system phase
+ coupling-energy context
+ NINO energy/rung context
+ build/release orientation
```

It is not mostly reading the broad ARA-boundary-distance fields. Removing `nino_ara_boundary` barely damages correlation and slightly improves all-horizon MAE, which suggests the boundary distances are currently noisy unless paired with better flow variables.

This narrows the next strict flow predictor:

```text
Do not predict all of S(t+h).

Predict:
1. NINO phase.
2. SOI phase.
3. NINO energy/rung state.
4. NINO-PDO and NINO-SOI coupling energy.
5. NINO build/release orientation.

Then decode.
```

That gives the next model a much smaller target and avoids averaging incompatible full-state vectors.
