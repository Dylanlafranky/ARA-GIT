# MX3c dynamic daughter-rung result

**Tier:** DEVELOPMENT / ALREADY INSPECTED / SINGLE NOISE REALISATION  
**Primary daughter:** pressure/velocity-spread wave at frozen mode k0=5  
**Eligible slices:** 299

## Direction test

The pressure-derived angle has whole-eligible weighted resultant 0.1045 with the parent q,d tangent.
Circular-shift null p=0.9680; phase-randomised null p=0.9820. On the held-late block, after a constant
orientation offset was learned from parent direction in the training block, pressure resultant is
0.9036 and circular MAE is
2.4159 radians.

Best disclosed lag: -8 slices (-0.6080
time units), where positive means the daughter leads. Resultant: 0.1322.

## Held-late approximate-trapping models

All additions are compared with the same amplitude + fundamental-mode baseline.

| Added information | R-squared | Change |
|---|---:|---:|
| none | 0.7071 | 0.0000 |
| fixed 25-degree projection | 0.9475 | +0.2404 |
| full q,d parent coordinates | 0.8747 | +0.1676 |
| pressure magnitude only | 0.1972 | -0.5099 |
| raw pressure-directed reading | 0.9562 | +0.2491 |
| train-aligned pressure reading | 0.9566 | +0.2495 |
| pressure magnitude + dynamic reading | 0.8520 | +0.1450 |
| q,d + pressure magnitude | 0.5230 | -0.1841 |
| q,d + pressure dynamic | 0.8305 | +0.1234 |

## Matched-amplitude one-to-one comparison

| Coordinate | Paired Cohen dz | Mean post-minus-pre |
|---|---:|---:|
| pressure magnitude | -0.8276 | -0.068188 |
| raw pressure-directed reading | 0.1140 | 0.018124 |
| train-aligned pressure reading | 0.1104 | 0.016915 |
| fixed 25 degrees | 0.1190 | 0.017293 |
| approximate trapping | 0.8796 | 0.026457 |

## Verdict

The primary directional claim is not supported. The observed daughter/parent directional resultant is lower than
almost all circular-shift and phase-randomised nulls. The best disclosed lag is negative and lies at the tested
boundary, so the pressure angle lags rather than leads the parent turn. Its train-aligned orientation also rotates by
nearly pi in the held-late regime.

The high standalone pressure-directed R-squared does not rescue the directional claim. The pressure angle is nearly
constant through much of the eligible interval, making the dynamic reading another approximately fixed projection of
the already-informative q,d coordinates. It does not add to the full parent coordinate: q,d plus pressure direction
scores 0.8305, below q,d alone at
0.8747.

Pressure-mode magnitude is nevertheless a strong matched-amplitude state marker
(paired dz=-0.8276), but its held-late continuous-state R-squared is only
0.1972. That is evidence for pressure as an adjacent nonlinear-state observable,
not evidence that its spatial phase supplies the missing ARA viewing direction.

**Status:** `PRESSURE STATE MARKER POSITIVE / PRESSURE-DERIVED DYNAMIC ANGLE NULL / NEXT-RUNG HYPOTHESIS REMAINS OPEN WITH THIS OBSERVABLE REJECTED`.

## Fences

- Pressure is derived from the same particle distribution but is independent of the trapping diagnostic definition.
- The constant orientation offset uses parent tangent direction on training data; it never uses trapping.
- The archive and target were already inspected, so held-late scores remain development evidence.
- A fixed spatial-mode phase may not be the correct mathematical representation of an ARA rung angle.
- Full support still requires unchanged noise/seed/beam transfer.
