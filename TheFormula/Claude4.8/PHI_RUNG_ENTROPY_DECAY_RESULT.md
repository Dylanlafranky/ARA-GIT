# Does information decay 1/φ per φ-rung? (predictability vs entropy)

**Date:** 2026-05-30
**Script:** `phi_rung_entropy_decay_test.py` → `phi_rung_entropy_decay_result.json`

## The claim being tested

Space packs in octaves (ratio ×2); time packs in φ (ratio ×1.618). The shortfall
**2 − φ = 1/φ² = 0.382** is "packet loss" / entropy. With the exact golden identity
**1/φ + 1/φ² = 1**, the prediction is: per φ-rung of forward time a signal should
**forward ~1/φ = 0.618** of its information and **shed ~1/φ² = 0.382**.

Operationally: as the horizon multiplies by φ, retained predictability should fall to
~0.618 of the previous rung.

## How it was measured (model-free, real data)

Two independent measures, sampled at φ-spaced horizons h₀·φⁿ:

- **Entropy** — auto-mutual-information I(xₜ ; xₜ₊ₕ), the entropy the past removes from
  the future. Binned estimator (8 equiprobable bins, Miller–Madow bias correction,
  shuffle-derived noise floor). Always ≥ 0, captures nonlinear structure. This is the
  "actual entropy" leg.
- **Forecast skill** — lagged autocorrelation envelope |ρ(h)|, which is exactly the
  correlation a persistence/AR forecast achieves at horizon h (no train/test leakage).

Data: ENSO Niño3.4 monthly anomaly (NOAA, 1870+, N≈1870); SILSO monthly sunspot number
(1749+, N≈3330); ECG RR intervals (PhysioNet nsrdb 16265, per-beat).

**Important equivalence:** a *constant* retention per φ-rung is mathematically the same as
a **power-law** decay in h (exponent = log_φ(retention); retention 0.618 ⇔ exponent −1).
Ordinary systems decay **exponentially**, where per-rung retention shrinks with horizon.
So "constant per-rung retention" is itself a real, separate test from "the constant = 0.618".

## Results

| System | Entropy retention / φ-rung | Decay shape (power-law vs exp) | Near 0.618? |
|---|---|---|---|
| **ENSO** | 0.60–0.65 (short anchors h₀=4–6 mo), drifts to ~0.79 at h₀≥9 | power-law wins, but modest R² (0.16–0.63) | **Yes**, at short horizons only |
| **ECG RR** | **0.79** (rock-stable across h₀=3–10) | **power-law, R²≈0.96** | No — sheds only ~0.21/rung |
| **Solar** | 0.80–0.96 | exponential / flat | No — flywheel |

Forecast (autocorrelation) leg agrees in direction but retains more and is noisier
(ENSO ~0.86, ECG ~0.79–0.98, Solar ~1.0).

## Honest read

**What holds:** The *shape* prediction — information decays as a **power law per φ-rung
(constant fraction, fractal memory)** rather than exponentially — is genuinely supported
in the two dissipative systems: ECG strongly (R²≈0.96, stable), ENSO moderately. This is a
non-trivial property; most systems decay exponentially.

**What does not hold as a universal:** The *specific value* 1/φ = 0.618 is **not** a
constant across systems. Only **ENSO** lands on it, and only at short horizons (h₀=4–6 mo);
its retention drifts upward at longer anchors. **ECG** forwards ~0.79 (sheds ~0.21, not
0.382). **Solar** holds almost everything (~0.9), consistent with its known
"flywheel / storer" signature — a memory-storing oscillator is the principled exception,
not a counterexample to the framework's own taxonomy.

**Bottom line:** The geometry (power-law, fractal per-rung loss) shows up in real entropy
for the dissipative systems. The exact "0.618 forwarded / 0.382 shed" split is one
system's value (ENSO at short range), not a measured universal constant. Reported without
tuning toward 0.618; the value is anchor-sensitive and that sensitivity is shown above.

## Caveats / researcher degrees of freedom
- Retention depends on the anchor h₀ and the fitted regime; the anchor sweep is reported
  rather than a single cherry-picked number.
- AMI absolute scale depends on bin count; ratios are more robust than levels.
- Solar's strong 11-yr cycle keeps mutual information high at all lags (no clean decay
  regime), so its "retention ~1" is expected, not informative about packet loss.
- Single ECG record; would need many records to claim the 0.79 value is general.
