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

---

## Seasonal influenza (3 June 2026) — disease outbreak cycle

Real CDC ILINet national weekly %ILI, 2010w40–2024w20 (711 weeks, via Delphi Epidata API). Strict-causal
self-forecast, golden split, annual cycle P=52 weeks. **Strong win, 5/5 horizons — same phase-capture signature
as sea ice / QBO:**

| ahead | persistence | framework |
|---|---|---|
| 2 wk | +0.908 | +0.911 |
| 1 mo (4 wk) | +0.768 | +0.805 |
| 2 mo (8 wk) | +0.443 | **+0.587** |
| 3 mo (13 wk) | +0.097 | **+0.431** |
| **6 mo (26 wk)** | **−0.329** | **+0.405** |

At 6 months persistence is anti-correlated (winter-peak → summer-trough) while the framework holds +0.41 — the
season's phase, captured. **Robust through the 2020–22 COVID flu collapse** (a large real anomaly in the series).
This is the 3–6 month window where vaccine distribution and hospital staffing are decided.

**Honest fences:** predicts seasonal *timing/shape*, NOT *strain dominance* (a different antigenic problem) nor
fully the *year-to-year amplitude* (bad vs mild season). National aggregate, self-forecast (no climate/school
drivers). The driver-below for flu would be temperature/humidity/school-term — adding them is the next step.

**Data note for the other two of Dylan's three picks:** *Dengue/malaria* are seasonal and partly fetchable
(WHO/PAHO, country surveillance) but messier than flu; *retail/holiday consumption* is cleanly fetchable (US
Census / FRED non-seasonally-adjusted retail sales has a strong December cycle); *locust/pest* records are
sparse and irregular (FAO + satellite) — the hardest to get as a clean series. Flu run first as the flagship.

---

## Retail / holiday consumption cycle (3 June 2026)

Real US Advance Retail Sales, NOT seasonally adjusted (FRED `RSXFSN`, 1992–2024, 396 months). Two readings:

- **Raw sales: trend-dominated, weak test (2/5).** Sales grew 127k→691k, so persistence is already ~0.86–0.96
  at every horizon (same "trivial" issue as CO₂). The framework wins only at h=1–2.
- **The holiday CYCLE itself: clean 5/5 win.** Removing the growth trend *causally* (seasonal index =
  value ÷ trailing-12-month mean — uses only past, no leakage) isolates the holiday oscillation (Dec spike ~1.29,
  Jan trough ~0.81). Forecasting that:

| ahead | persistence | framework |
|---|---|---|
| 1 mo | +0.100 | **+0.481** |
| 2 mo | **−0.185** | **+0.442** |
| 3 mo | −0.036 | +0.196 |
| **6 mo** | **−0.045** | **+0.777** |
| 12 mo | +0.765 | +0.825 |

Phase-capture again: at 6 months persistence is ~0 (June↔December) while the framework holds +0.78. **The
consumption cycle is strongly predictable once separated from the growth trend** — which is the honest framing:
the framework reads the *cycle*; the trend is a separate slow component you isolate first (causally).

---

## Dengue (3 June 2026) — partial / weaker

Real PAHO dengue incidence, Brazil, 2014–2023 (Delphi Epidata `paho_dengue`, latest-issue per epiweek, 322 wk).
Self-forecast, P=52 wk. **1/4 horizons — annual phase only:** h=26 wk (6 mo) persistence +0.072 → framework
**+0.608**; but h=4/8/13 the framework is *worse* (0.37/0.23/0.20 vs 0.85/0.69/0.49). Dengue incidence spans
~600× (1.7→1065), with epidemic onset/magnitude driven by rainfall, serotype switches, and waning immunity —
irregular external drivers the self-forecast can't see. So the framework reads the **annual season** but not the
**epidemic dynamics.** Contrast flu (one regular driver, 5/5) vs dengue (many irregular drivers, 1/4) — the gap
is itself informative: more driver-dependent + spikier = harder for a self-forecast, needs the drivers fed in.

## Cancer-timing direction — data scope (3 June 2026)

The "framework reads the timing/dynamics, biologists supply the cause" bridge (chronotherapy + adaptive therapy)
needs real time-series. Scoped candidates and fetchability:
- **Cell cycle as an oscillator** (prerequisite: does it have a measurable ARA?) → cleanest source is
  **synchronized cell-cycle expression time-series** (Spellman/Cho yeast cell cycle, on GEO) — findable but not
  a one-call API like FRED/Epidata.
- **Tumor growth curves** (xenograft caliper series over time) → exist as paper supplementary data; need assembly.
- **Drug-resistance evolution** (to test our pace↔adaptation result: fast cycle + low copy-fidelity → fastest
  resistance) → cell-line evolution experiments / GDSC-adjacent; need locating.
- None are trivially fetchable in-sandbox; this is the clear *data* next-step. First honest test = cell-cycle
  ARA on a synchronized-cell expression series (demonstrate the cycle is measurable before any therapy-timing claim).
- HARD FENCE: any cancer work here is exploratory dynamics-mapping and hypothesis generation — never clinical,
  never advice, never a prediction about a person. Not medical advice.
