# Mix ocean+atmosphere at the spring gate -> stronger NINO prediction (strict-causal)
Date 2026-05-30. Dylan: take the two systems (ocean WWV + atmosphere SOI), do the mixing,
get a stronger prediction. Channels real (PMEL/NOAA WWV anomaly, NOAA/PSL SOI, NINO3.4).

## Method (strict-causal, corr-led)
Predict NINO3.4(t+h) from data at time t only. Walk-forward: fit coefficients + standardize
on TRAIN (first 60%), score correlation on TEST (last 40%), no overlap. Features: WWV(t),
SOI(t), the blend WWV*SOI (mixing term), and a spring gate (smooth bump at Apr) x mixing.
Baseline = persistence NINO(t)->NINO(t+h) on the same test rows. N=552 mo (1980+, ~46yr).

## Result (test-set correlation)
| horizon | persist | WWV only | SOI only | WWV+SOI | +MIX | +GATED-MIX |
|---|---|---|---|---|---|---|
| 6 mo  | +0.377 | -0.020 | +0.313 | +0.370 | +0.363 | +0.372 |
| 12 mo | **-0.045** | +0.185 | +0.034 | +0.201 | **+0.218** | +0.216 |

## Reading
- At 6 mo the surface still has memory; persistence (+0.38) is the thing to beat, and the
  two-system blend matches it (+0.37) but doesn't exceed it.
- At 12 mo the surface goes amnesiac across the spring barrier (persistence = -0.045). Here
  MIXING THE TWO SYSTEMS WINS: WWV+SOI+mix = +0.218 vs persistence -0.045 (a +0.26 lift), and
  beats either system alone (WWV +0.185, SOI +0.034). The battery (WWV) and the wind (SOI)
  carry the memory the surface lost. => Dylan's claim holds: two systems mixed > one system,
  and the gain shows up exactly where the surface clock breaks.

## Honest caveats
- Most of the lift is from USING BOTH systems vs one. The explicit product "mixing" term adds
  a small extra at 12mo (+0.017 over additive). The spring-gate multiplicative feature adds
  nothing beyond the mix in this simple form (gate as a regime-selector untried).
- +0.218 at 12mo is modest vs operational ENSO models (~0.5-0.6 with full dynamics), but it is
  real, out-of-sample, and from just two indices + a blend. Relative ranking is the result.
