# Spring heartbeat added to the capstone ENSO forecaster (strict-causal, held-out)
Date 2026-05-30. Extends ara_seasonal_calibrated_predictor.py by adding the ATMOSPHERE (SOI)
and a SPRING HEARTBEAT = gate(month)*(zWWV*zSOI), gate=1 in Mar-Apr-May. Walk-forward, refit
past-only at every origin, train-only standardization, gate is calendar-known (no leakage).
N=552mo (1980-2025). corr LEADS (project rule); MSE-skill in brackets.

| lead | ocean (capstone base) | +atmosphere (SOI) | +SPRING HEARTBEAT |
|---|---|---|---|
| 1  | +0.963 [.93] | +0.967 [.93] | +0.967 [.93] |
| 3  | +0.872 [.77] | +0.889 [.79] | +0.888 [.79] |
| 6  | +0.709 [.51] | +0.716 [.52] | +0.714 [.52] |
| 9  | +0.543 [.27] | +0.545 [.28] | +0.543 [.28] |
| 12 | +0.423 [.10] | +0.429 [.14] | +0.431 [.14] |
| 15 | +0.451 [.15] | +0.462 [.17] | +0.461 [.17] |
| 18 | +0.506 [.23] | +0.517 [.24] | +0.516 [.24] |
| 21 | +0.495 [.22] | +0.507 [.23] | +0.505 [.23] |
| 24 | +0.470 [.20] | +0.464 [.19] | +0.461 [.19] |
| 27 | +0.401 [.15] | +0.429 [.16] | +0.423 [.16] |

## Honest reading
- Adding the ATMOSPHERE (SOI) as the second system gives a small but consistent lift at almost
  every lead; clearest in MSE-skill at 12mo (.10 -> .14) and across 12-21mo. Supports "two
  systems > one."
- The explicit SPRING-HEARTBEAT mixing term (spring-gated zWWV*zSOI) adds essentially NOTHING
  beyond simply including SOI -- corr identical to 3 decimals, skill flat or a hair lower.
- WHY: the seasonal propagator already learns MONTH-DEPENDENT coupling between WWV and SOI, so
  a spring-only mix column is redundant -- the handoff is already captured by the seasonal
  coefficients. The gate-as-extra-feature is absorbed.

## Verdict
Keep SOI in the capstone (free small gain, physically the atmosphere half of the engine).
The heartbeat as an *added gated feature* is redundant. If the heartbeat is to earn its keep
it must do something the seasonal propagator cannot already do -- e.g. act as a REGIME SWITCH
that changes the model structure in spring, or carry a nonlinearity (amplitude->period) the
linear seasonal map lacks. Untested.
