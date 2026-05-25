# ARA Geometry Analog Flow Result

**Date:** 2026-05-24

This test implements the proposed separation:

```text
raw signal
-> ARA mapper
-> geometry state S(t)
-> similar-state search
-> transition vector dS
-> future geometry S(t+h)
-> decoder
-> NINO3.4 forecast
```

The script is:

- `TheFormula/ara_geometry_analog_flow_predictor.py`

Outputs:

- `TheFormula/ara_geometry_analog_flow_predictor_result.json`
- `TheFormula/ara_geometry_analog_flow_predictor_result.js`

## Leakage Guard

For origin `t` and horizon `h`:

- `S(t)` is built only from `data[:t]`.
- Analog transition examples use only anchors `s` where `s + h < t`.
- Decoder training uses only observed geometry anchors `a < t`.
- Direct geometry-to-value regression is included only as a control.
- `oracle_actual_future_geometry_decoder` decodes the true future geometry and is diagnostic only.

## Main Result

The decoder separation is useful, but the current analog transition operator is too blunt.

At 12 and 24 months, the oracle future-geometry decoder is strong:

| Horizon | Oracle future-geometry decoder | Persistence | Read |
|---:|---:|---:|---|
| 12 mo | MAE `0.630`, corr `+0.669` | MAE `0.998`, corr `-0.106` | Future geometry decodes NINO well if the future geometry is known |
| 24 mo | MAE `0.579`, corr `+0.765` | MAE `1.152`, corr `-0.281` | Decoder ceiling is high at the transition scale |

But the strict forecast branch:

```text
current S(t) -> analog dS -> estimated S(t+h) -> decoder
```

does not yet estimate the future geometry accurately enough.

## Score Table

| Horizon | Model | MAE | Corr | Direction | MAE lift vs persistence |
|---:|---|---:|---:|---:|---:|
| 1 | persistence | `0.209` | `+0.956` | `0.029` | `+0.000` |
| 1 | analog flow decoder | `0.463` | `+0.808` | `0.449` | `-0.254` |
| 1 | raw analog baseline | `0.199` | `+0.962` | `0.536` | `+0.011` |
| 1 | lag ridge | `0.172` | `+0.966` | `0.681` | `+0.038` |
| 3 | persistence | `0.483` | `+0.761` | `0.014` | `+0.000` |
| 3 | analog flow decoder | `0.649` | `+0.618` | `0.406` | `-0.166` |
| 3 | raw analog baseline | `0.450` | `+0.781` | `0.580` | `+0.033` |
| 3 | lag ridge | `0.370` | `+0.824` | `0.696` | `+0.113` |
| 6 | persistence | `0.770` | `+0.356` | `0.000` | `+0.000` |
| 6 | analog flow decoder | `0.896` | `+0.270` | `0.456` | `-0.125` |
| 6 | raw analog baseline | `0.708` | `+0.350` | `0.676` | `+0.062` |
| 6 | lag ridge | `0.602` | `+0.477` | `0.691` | `+0.168` |
| 12 | persistence | `0.998` | `-0.106` | `0.000` | `+0.000` |
| 12 | analog flow decoder | `1.056` | `-0.061` | `0.530` | `-0.058` |
| 12 | raw analog baseline | `0.784` | `-0.076` | `0.727` | `+0.214` |
| 12 | lag ridge | `0.649` | `+0.205` | `0.818` | `+0.349` |
| 24 | persistence | `1.152` | `-0.281` | `0.000` | `+0.000` |
| 24 | analog flow decoder | `1.103` | `-0.118` | `0.548` | `+0.049` |
| 24 | raw analog baseline | `0.959` | `-0.398` | `0.710` | `+0.193` |
| 24 | lag ridge | `0.617` | `+0.167` | `0.790` | `+0.535` |
| 60 | persistence | `0.867` | `-0.146` | `0.000` | `+0.000` |
| 60 | analog flow decoder | `1.020` | `-0.303` | `0.520` | `-0.152` |
| 60 | raw analog baseline | `0.790` | `-0.191` | `0.720` | `+0.078` |
| 60 | lag ridge | `0.704` | `-0.459` | `0.720` | `+0.164` |

Lag ridge is still the best strict forecast at every horizon in this run.

## Interpretation

This supports the architecture but not the simple analog-flow implementation.

What held up:

- Geometry-state decoding has real signal when the future geometry state is correct.
- The decoder branch is worth keeping separate.
- Direct geometry-to-value regression remains too mushy and performs poorly.
- Raw analog matching is useful for MAE and turn direction, but it does not recover reliable correlation at the longer ENSO horizons.

What failed:

- Nearest-neighbour analog movement through the compact ARA state does not yet recover the right future geometry.
- The analog flow decoder underperforms persistence at 1, 3, 6, 12, and 60 months, and only gives a small MAE lift at 24 months with negative correlation.
- The non-ARA log-flow control also fails, so the analog-flow shell alone is not enough.

## Working Conclusion

The clean version of the idea is now:

```text
Prediction bottleneck = future geometry flow
not
geometry-to-native decoder
```

The next version should not simply search for similar whole states. It should predict the parts of `S(t+h)` separately:

- regime / turn probability.
- phase movement.
- ARA-position movement.
- amplitude / feeder pressure.
- partner phase gap.

Then the decoder can translate that predicted geometry back into NINO. This keeps the framework strict while giving the transition operator enough structure to avoid whole-state averaging.

## Follow-Up Ablation

`ARA_ORACLE_GEOMETRY_ABLATION_RESULT.md` now checks which actual future geometry fields carry the oracle decoder signal.

The strongest group-only oracle signals at the 6/12/24 month transition band are:

- `nino_phase`: mean corr `+0.622`, MAE `0.553`.
- `soi_phase`: mean corr `+0.608`, MAE `0.550`.
- `nino_pdo_coupling`: mean corr `+0.369`, MAE `0.679`.
- `nino_soi_coupling`: mean corr `+0.305`, MAE `0.662`.

The most damaging removal from the full decoder is `nino_energy_rung`, with corr drop `+0.062` and MAE increase `+0.082` across 6/12/24 months.

So the next flow operator should predict a small set of future geometry variables first: NINO phase, SOI phase, NINO energy/rung, NINO-PDO coupling energy, NINO-SOI coupling energy, and NINO build/release orientation.
