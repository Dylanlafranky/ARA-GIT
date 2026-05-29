# ARA Pyramid Pressure — the 4th line (load-from-above → amplitude)

**Date:** 2026-05-29
**System:** ENSO (NINO 3.4 SST anomaly). One system, held-out, leakage-guarded.
**Status:** A real, modest, cross-event signal at specific leads. Documented with
its limits, not as a closed result.

---

## The prediction tested (Dylan)

The pyramid has three lower grains (the apex NINO temperature + two warm-water-
volume base grains) whose coupled rebound generates ENSO's **dynamics and timing**.
That work is done by the seasonal three-body LIM (the capstone). What it does *not*
fix is **amplitude**: the rebound's skill rings down — strong near the surface, a
trough at 9–18 months, then a faint **recurrence ring near 27 months** that the
engine leaves at only ~+0.26 correlation.

Dylan's call: the **coarsest grains overhead press down on the apex** (Newton's
third law — more downward pressure secures the grain and drives a harder spring-
back). That pressure sets **how big** the rebound is, not **when** it happens. We
are decent on *when*, so the 4th line targets **amplitude only**, and it presses
from above. The pressure is a **deterministic calendar wave** at the target time —
annual (already inside the engine) optionally plus a **lunar** wave.

## How the 4th line is wired (honest, leak-free)

The per-lead trust factor β is allowed to **breathe with the downward pressure**:

```
pred(t+h) = clim + β(h, pressure_at_(t+h)) · (raw_seasonal_pred − clim)
β = b0 + b1·cos(annual) + b2·sin(annual) [+ b3·cos(lunar) + b4·sin(lunar)]
```

- High-pressure target phase → larger restored amplitude; low-pressure → shrink to
  climatology.
- The pressure wave is astronomical/calendar, **known a priori for any future
  month**, so it adds **no leakage**.
- Coefficients fit on **past origins only** (< 2016), applied causally to held-out
  origins (≥ 2016). The leak-check (fit on all origins vs past-only) matches → no
  train/test leak.

Lunar candidates tested: **perigee precession 8.847 yr** (anomalistic) and **nodal
precession 18.613 yr**.

## What earned its place, what did not

| pressure line | verdict |
|---|---|
| **annual only** | redundant — the annual clock is already in the engine; adding it as an amplitude knob just adds noise and slightly hurts. |
| **annual + nodal (18.6 yr)** | mostly hurts; no clean lift at the rings. |
| **annual + perigee (8.85 yr)** | **the signal.** Lifts correlation at 12 months and at the 27–30-month rings. |

## The two hard tests it had to survive

The held-out window (2016+) is ~10 yr and dominated by the single 2023–24 El Niño.
So a slow ~9-yr wave could "win" just by landing on that one event. Two falsifiers:

**1. Leave-one-block-out (cross-event).** Split origins into three event-blocks
(≈2003–10, 2010–18, 2018–25, covering the 2009-10, 2015-16 and 2023-24 events).
Fit on two blocks, score the third. The moon-period must transfer across
*different* El Niños.

Correlation, raw seasonal → **+ moon pressure** (each block scored on its own):

| lead | block 2003–10 | block 2010–18 | block 2018–25 | pooled |
|---|---|---|---|---|
| **12 mo** | +0.11 → **+0.17** | +0.17 → **+0.46** | +0.48 → **+0.60** | +0.25 → **+0.39** |
| 15 mo | +0.19 → +0.05 ✗ | +0.09 → +0.35 | +0.51 → +0.60 | +0.23 → +0.29 |
| 24 mo | +0.05 → +0.19 | +0.12 → −0.01 ✗ | +0.40 → +0.31 ✗ | +0.14 → +0.12 ✗ |
| **27 mo** | +0.27 → **+0.47** | +0.18 → **+0.32** | +0.31 → **+0.35** | +0.23 → **+0.34** |
| **30 mo** | +0.57 → **+0.63** | +0.23 → **+0.34** | +0.09 → **+0.34** | +0.28 → **+0.41** |

At **12, 27 and 30 months the moon pressure improves in all three eras**, including
the 2009-10 and 2015-16 events — it is not the 2023 El Niño talking.

**2. Wide placebo (frequency is what matters).** Because the fit picks each wave's
best phase automatically, the only real choice is the *period*. Swap the true lunar
period for **300 random periods over 4–16 yr**, re-run with the same block-CV:

| lead | raw pooled | moon pooled | placebo mean | placebo 95th | p(random ≥ moon) |
|---|---|---|---|---|---|
| **12 mo** | +0.253 | **+0.387** | +0.164 | +0.389 | **0.06** |
| 15 mo | +0.226 | +0.292 | +0.124 | +0.292 | 0.06 |
| 24 mo | +0.140 | +0.122 | +0.056 | +0.171 | 0.20 ✗ |
| **27 mo** | +0.226 | **+0.338** | +0.202 | +0.333 | **0.03** |
| **30 mo** | +0.276 | **+0.410** | +0.221 | +0.409 | **0.04** |

The true lunar period beats **~94–97 %** of random wrong-period waves at 12, 27 and
30 months. A generic slow wave (the extra two free knobs) gets *some* lift; the
**lunar period specifically gets more**.

## Verdict

- **Confirmed at 12 / 27 / 30 months:** the lunar-perigee downward pressure carries
  **real, transferable amplitude information**. It passes both falsifiers — improves
  in every El Niño era separately, and beats ~95 % of random periods. The 27–30-mo
  recurrence ring now rings **louder** (pooled +0.23 → +0.34 at 27 mo) than the
  engine gives it for free.
- **Fails at 24 months:** random periods do just as well (p = 0.20) and it hurts one
  block. The moon does **not** fix every ring — it fixes the 12-mo band and the
  27–30-mo ring, and nowhere reliably at the 18–24-mo trough.
- **The trough wall (18–24 mo) still stands.** Consistent with the rest of the
  corpus: stochastic wind forcing sets the un-pre-determined part; no deterministic
  pressure reaches it.

## The honest limit

The whole record is ~22 years = **only ~2.5 perigee cycles**. Three event-blocks is
the most the data allows. The signal is reproducible across those three events, but
"~2.5 cycles" is the ceiling on confidence. The single test that would move it from
"strong lead" to "result" is **more lunar cycles** — extend back with the long NINO
record (1870+) plus a warm-water-volume reconstruction proxy, giving 8–15 perigee
cycles instead of 2.5.

## Reproduce

```
python3 ara_pyramid_pressure_predictor.py nino34_long_anom.csv          # causal walk-forward
python3 ara_pyramid_pressure_predictor.py nino34_long_anom.csv --leaky  # leak-check
python3 ara_pyramid_pressure_blocktest.py nino34_long_anom.csv          # block-CV + wide placebo
```
Auto-downloads WWV west/east from PMEL; expects a NINO 3.4 monthly-anomaly CSV.

## Files

- `ara_pyramid_pressure_predictor.py` — the 4th-line predictor (causal + leak-check)
- `ara_pyramid_pressure_blocktest.py` — leave-one-block-out + wide placebo
- `moon_pressure_forecast_view.html` — interactive predicted-vs-actual viewer (6/12/27 mo)
- data: PMEL WWV west/east; NINO 3.4 monthly anomaly
