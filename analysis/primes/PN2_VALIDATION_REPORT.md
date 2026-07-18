# PN2 validation report

**Assessment:** `SHARE WITH CAVEATS / PRIMARY ARA ENDPOINTS NOT SUPPORTED / RESULT RELIABLE`

## What was validated

PN2 evaluated fixed-budget probabilistic survival after sieving through prime 29. Candidate and adjacent-edge outcomes
were compared against frozen analytic and raw-gap baselines on the untouched interval
`[100,000,000,110,000,000)`.

The test protocol SHA-256 was
`2F70766D0335C34C01ADCDABE512540415CAF37E6A176C546B16E955806DA664`. The frozen target configuration SHA-256
was `A31F256EE160529A1F5BC1B53E3EB5EA0321BBB0A063A10B03068F5B81DFA13F`.

## Reproduction result

The target analysis completed without accessing the p31 PN1H wheel. A separately coded validator, which does not
import the primary analysis script, reconstructed all primality labels and passed `476/476` checks.

The independent checks cover:

- protocol, executable, development-model and target-configuration hashes;
- complete target p29-wheel candidate sequence and independent segmented-sieve primality labels;
- all candidate and adjacent-edge features and event counts;
- every stored model probability, calibration statistic and log-loss score;
- both primary block deltas and 10,000-resample bootstrap intervals;
- every gap-class count and model expectation;
- all 20 location-calibration blocks;
- exact mapped-log-ratio equality controls;
- readable figure dimensions and the explicit `p31 accessed = false` guard.

## Findings safe to report

- The primary ARA Information^3 candidate model lost to PNT29 by `0.000160973` bits/candidate; its 95% block interval
  was `[-0.000191083,-0.000129918]`.
- The primary ARA edge model lost to conditional Hardy-Littlewood by `0.000036725` bits/edge; its 95% block interval
  was `[-0.000050887,-0.000022377]`.
- PNT29 had the best 20-block location MAPE (`0.2088%`).
- Conditional Hardy-Littlewood had the best eligible gap-class Poisson deviance (`20.7143`) and weighted absolute
  relative error (`0.7356%`).
- One 12-bin plain-ARA candidate sensitivity gained `0.000000772` bits/candidate over PNT29, but the gain disappeared
  at 8, 16 and 24 bins and was not the primary endpoint.
- The ARA mapped-log-ratio controls exactly reproduce their ordinary log-ratio equivalents and add no independent
  information.

## Important caveats

- The result rejects the declared local ARA survival models, not every possible ARA formulation.
- It is one target interval and one sieve budget; block resampling quantifies within-target spatial robustness but not
  universal transfer.
- The tiny bin-specific plain-ARA sensitivity is not robust and must not be used to redesign PN2 after inspection.
- Exact primorial-wheel results remain valid arithmetic results, but they are not evidence that local wheel position
  predicts survival beyond the sieve budget.
- A new survival test needs a fresh target and a predeclared cross-scale variable or residual mechanism.

## Reproducibility packet

- `PN2_PRIME_SURVIVAL_BRIDGE_PROTOCOL_v1_FROZEN.md`
- `PN2_TARGET_RUN_CONFIG_v1_FROZEN.json`
- `pn2_prime_survival_bridge.py`
- `pn2_independent_validator.py`
- `PN2_PRIME_SURVIVAL_BRIDGE_REPRODUCIBILITY.ipynb`
- `PN2_RESULTS.json`
- `PN2_INDEPENDENT_VALIDATION.json`
- `PN2_NOTEBOOK_EXECUTION_VALIDATION.json`
- `PN2_PRIME_SURVIVAL_BRIDGE_REPORT.md`

