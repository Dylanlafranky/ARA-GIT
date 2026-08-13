# T343 broken-control temporal-leakage audit

**Run:** 5 August 2026  
**Status:** post-result diagnostic; the frozen T343 score and protocol remain unchanged

## Result first

The circular-shift null is not a clean causal broken-pair control for a next-state target. For part of every shifted block it places later native axis values at earlier current states. Large shifts can place the actual next axis value directly in the predictor. The frozen `1/6` result remains the correct score for its registered construction, but its broken-pair gate must not be interpreted as a leakage-free causal test of intact coupling.

## Audit table

| domain | median frozen future share | frozen controls >5% direct target | eligible causal controls | median causal broken-intact delta | causal p | sensitivity pass |
|---|---:|---:|---:|---:|---:|---|
| pendulum | 47.89% | 0/1000 | 1000 | -0.132353 | 1.0000 | NO PASS |
| hydraulic | 53.32% | 327/1000 | 1000 | -0.138708 | 0.5345 | NO PASS |
| bubbles | 54.88% | 471/1000 | 365 | +0.051933 | 0.0027 | PASS |
| cold_room | 50.29% | 242/1000 | 1000 | +0.129962 | 0.0450 | PASS |
| acoustics | 50.70% | 471/1000 | 1000 | -0.133650 | 1.0000 | NO PASS |
| qutrit | 50.60% | 186/1000 | 1000 | +0.064351 | 0.0010 | PASS |
| river | 61.01% | 327/1000 | 0 | +nan | nan | NO PASS |

Positive causal delta means the past-only broken pairing had higher loss than the intact pairing on exactly the same retained transitions. Both calibration fitting and holdout scoring use the same no-wrap subset for that replicate.

## Evidence fence

This audit was conceived after the frozen result was visible. It cannot replace, rescue or overturn T343. It diagnoses the control and defines a better future design. The causal sensitivity is itself post-result and must be independently frozen on a new source battery before being used as confirmatory evidence.
