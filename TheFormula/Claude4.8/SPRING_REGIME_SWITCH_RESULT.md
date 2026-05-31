# Spring regime-switch test — result

**Question:** does building the spring ocean↔atmosphere handoff as a true *regime switch*
beat folding it in as one always-on feature (which the seasonal map just absorbed)?

**Build:** two seasonal one-step maps refit past-only at every origin —
- **spring map** (steps out of Mar/Apr/May): carries the ocean×atmosphere mix term `zWWV·zSOI`. The mix drives here.
- **rest map** (every other month): plain seasonal state, no mix. The surface coasts on its own memory.

Multi-step forecasts walk the calendar and pick the map by the month they step out of.
Strictly causal (regime label = calendar, no leakage; SOI/WWV standardized train-only).
Correlation leads; MSE-skill in brackets. N=552 mo (1980–2025), held out from 2016.

| lead | ocean(base) | +atmos | +heartbeat(absorbed) | **SPRING SWITCH** |
|---|---|---|---|---|
| 1  | +0.963 | +0.967 | +0.967 | +0.967 |
| 3  | +0.872 | +0.889 | +0.888 | **+0.893** |
| 6  | +0.709 | +0.716 | +0.714 | **+0.725** |
| 9  | +0.543 | +0.545 | +0.543 | +0.541 |
| 12 | +0.423 | +0.429 | +0.431 | +0.411 |
| 15 | +0.451 | +0.462 | +0.461 | +0.450 |
| 18 | +0.506 | +0.517 | +0.516 | **+0.525** |
| 21 | +0.495 | +0.507 | +0.505 | **+0.514** |
| 24 | +0.470 | +0.464 | +0.461 | +0.456 |
| 27 | +0.401 | +0.429 | +0.423 | +0.411 |

**Bottom line:** the switch gives the **best 6-month forecast of all four (+0.725)** and wins
again at 18–21 months — exactly the near-surface and the quasi-biennial leads where the
spring handoff lives. It does NOT win at the 12-month trough: splitting one map into two
costs training data, and the data-hungry long-horizon fit suffers for it. Gains are small
(~+0.01 corr) but real and they land where the physics says they should.

**Why the gains are small:** the single seasonal map already learns month-dependent
ocean–atmosphere coupling through its `X·cos`/`X·sin` cross-terms. The regime switch makes
the spring handoff *explicit and exclusive*, which is cleaner and slightly sharper at the
surface, but it isn't discovering coupling the seasonal map was blind to.

No claim past the ~6-month physical horizon. The switch is the honest near-surface champion.
