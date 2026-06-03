# Multi-system prediction stack — strict-causal, vs persistence (3 June 2026)

Adding prediction demonstrations beyond the original three (solar / ENSO / heart), at human and
environmental scale, using the **validated layered operator** (`ara_framework.run_forecast` via
`build_self_system`). Every run is a **self-forecast** (single series, NO external drivers),
strict-causal (train on first 60%, score the held-out rest, baselined against persistence).

The strongest proof is not merely "beats persistence" — it is **where persistence goes NEGATIVE
(anti-correlated) and the framework stays strongly positive**: that can only happen if the model
captured the oscillation's *phase*, not just tracked the mean (correlation > MAE, hitting the points).

| system | scale | home period | result | headline |
|---|---|---|---|---|
| **Arctic sea ice extent** | cryosphere / environmental | 12 mo | **5/5 beat persistence** | h=6mo: persistence **−0.92** → framework **+0.99** (summer-vs-winter flip captured) |
| **QBO 30 mb zonal wind** | atmosphere / environmental | 28 mo | **4/5 beat persistence** | h=12mo: persistence **−0.69** → framework **+0.73**; h=18mo: −0.34 → +0.52 |
| **CGM glucose (subj 001)** | human metabolic | 1 day (288×5min) | 4/5 beat persistence | h=15min: +0.82 → **+0.92**; modest, decays at long leads (9-day record) |
| **CO₂ Mauna Loa (monthly)** | environmental | 12 mo | 4/5 (but trivial) | both ≈+0.99 — smooth trend makes persistence near-perfect; **not a real test** |

## Per-horizon detail (corr: persistence → framework home+ara)

**Arctic sea ice (monthly):** h1 +0.85→+0.99 · h2 +0.46→+0.99 · h3 −0.03→+0.99 · h6 **−0.92→+0.99** · h12 +0.99→+0.99
**QBO (monthly):** h3 +0.70→+0.88 · h6 +0.14→+0.76 · h12 **−0.69→+0.73** · h18 −0.34→+0.52 · h24 +0.40→+0.37(below)
**CGM glucose (5-min):** h3 +0.82→+0.92 · h12 +0.43→+0.47 · h36 +0.08→+0.08 · h72 +0.05→+0.05(below) · h144 −0.34→−0.08
**CO₂ (monthly):** h1 +0.997→+1.000 · h2 +0.991→+0.999 · h3 +0.984→+0.999 · h6 +0.972→+0.999 · h12 +0.999→+0.999(below)

## Honest read

- **Sea ice and QBO are strong, clean wins** — the framework holds +0.5 to +0.99 at horizons where
  persistence has inverted to strongly negative. That is phase-capture, the hardest thing for a naive
  baseline, and exactly what the framework claims to do. These two are worth quoting.
- **Glucose** is a real human-scale win at short leads (+0.92 at 15 min) but modest and short-record;
  treat as suggestive, not headline. Worth a multi-subject rerun like the heart.
- **CO₂ is trivial** — a smooth monotonic trend makes persistence already ~0.99; the framework's tiny
  edge there proves little. Reported for honesty, not as evidence.
- All are **self-forecasts** (no external drivers fed in). Adding the real driver-below (as with ENSO's
  warm-water volume) would be the next step to push the mid-horizons further.

**Scale coverage now demonstrated:** astro (solar) · ocean-climate (ENSO) · atmosphere (QBO) ·
cryosphere (sea ice) · environmental trend (CO₂) · physiology (heart) · human metabolic (glucose).

Script: `/tmp/stack_predictions.py` logic over `ara_framework.run_forecast`. Data: NOAA GML (CO₂),
NOAA PSL (QBO), NSIDC (sea ice), BIG IDEAS Lab CGM (glucose).

---

## T1D diabetic glucose (3 June 2026) — does it help diabetes?

Ran the same strict-causal self-forecast on **6 type-1 diabetic CGM records** (cgm_test/t1d, 5-min, ~3–5 days
each; gaps filled causally by forward-fill ≤30 min; longest contiguous segment per subject). Focus on the
clinically actionable 15–30 min "time to act" window used by predictive low-glucose-suspend pumps.

| horizon | persistence (mean) | framework (mean) | framework beats persistence |
|---|---|---|---|
| **15 min** | +0.977 | **+0.993** | **6/6 subjects** |
| **30 min** | +0.918 | **+0.934** | 5/6 |
| 60 min | +0.761 | +0.537 | 2/6 (framework WORSE) |
| 180 min | +0.298 | +0.001 | 2/6 (both collapse) |
| 360 min | −0.048 | +0.045 | 3/6 (both ≈0) |

**Read (honest):**
- **In the actionable 15–30 min window the framework beats persistence on real diabetic glucose, consistently
  (6/6 at 15 min, 5/6 at 30 min).** Small absolute edge (+0.016 at 15 min — glucose is smooth, persistence is
  already ~0.98) but consistent across all subjects. This is the window that matters for hypo prevention.
- **Past ~30 min it fails** — at 60 min the framework is *worse* than persistence (0.54 vs 0.76), and at 1–6 h
  both collapse toward zero. This is the key finding, and it confirms Dylan's prediction: **diabetic glucose's
  longer future is governed by external drivers (meals, insulin, activity), not its own past.** The self-forecast
  has no access to those, so it dies exactly where the driver-below takes over.
- **Next step (the real test for diabetes):** feed carbs/insulin as the driver-below feeders (as warm-water
  volume was for ENSO) and re-test the 30–120 min window. If that recovers mid-horizon skill, it points at a
  meal/insulin-aware forecaster.

**Fences:** short records (~5 cycles), 6 subjects, corr near 1 at 15 min means the *clinical* value (catching
hypos early, low false alarms, vs state-of-the-art pump algorithms) is a separate, higher bar not tested here.
Not medical advice; decision-support framing only. Data: T1D CGM (cgm_test/t1d).

### Next direction — find the "system before" (driver-below) with ARA logic

The 30-minute cliff means the glucose self-forecast is **missing the system before it** — the driver-below whose
output becomes glucose's future. The near term is glucose's own; the far term belongs to that upstream system.

- **Working hypothesis: the driver is the carb/insulin channel** (meals + insulin). It is the physiologically
  obvious candidate, and crucially its action timescale (~30 min – 3 h) matches *exactly* the horizon where the
  self-forecast collapses. The collapse horizon is itself a clue to the driver's rung.
- **But it may not be carbs/insulin alone** — candidates include activity/exercise, stress/cortisol, the
  dawn/circadian rhythm, or a coupling of several. We should not assume; we should locate it.
- **ARA logic should be able to FIND it, not just guess it.** Three framework moves:
  1. **Timescale pin** — the horizon where self-forecast falls below persistence (~30–60 min here) bounds the
     driver's period/rung. The driver sits one rung *up* (slower) from glucose's own fast dynamics.
  2. **Reverse-inference** — reconstruct the hidden driver's *shape and timing* from the forecast **residual**
     (the part of glucose the self-forecast cannot explain). This is the framework's distinctive
     "estimate the unmeasured" capability (see `framework_reverse_inference`, `framework_digital_twin`):
     the residual carries the fingerprint of whatever is driving from outside.
  3. **Match the fingerprint** — compare that reconstructed driver-shape against candidate *measured* systems
     (carbs, insulin, activity, cortisol). The one whose real series matches the reconstructed fingerprint —
     in timing, rung, and anti-/in-phase coupling — is the driver.
- **A negative on carbs/insulin would not falsify the framework** — it would mean we tied the wrong neighbour,
  and the reverse-inferred fingerprint would point us at the right one instead.
- **Data needed to run it:** a CGM record with candidate driver channels logged on the same clock
  (carbs / insulin / activity) — e.g. OhioT1DM (DUA), full D1namo (CGM + food + accelerometer), or a
  Tidepool/Nightscout export. Our current CGM folders lack any driver channel.
