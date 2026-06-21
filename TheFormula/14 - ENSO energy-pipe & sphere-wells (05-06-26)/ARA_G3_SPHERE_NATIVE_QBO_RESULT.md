# Sphere-native predictor (G3) on QBO — both versions vs real baselines (3 June 2026)

Two geometry-native predictors built in `TheFormula/ara_g3_experimental.py` (the **stable root trio is
untouched** — sandbox only). Tested on real QBO 30mb zonal wind (n=938, P=28 mo, golden split train 1/φ).

**Geometry used** (5-axis sphere from `3D models/ara_sphere_coordinate_3d.html`): X = mapping/ARA (DYNAMIC per
tick — the engine's `1+tanh(z/2)`), Y = rungs, Z = connection→info (per tick = standardized |own_spin|+|torque|,
i.e. local movement/coupling), φ = coupling efficiency (per-tick distance of dynamic ARA to the golden value
1.618), anti-φ = mirror (distance to 0.382). Per Dylan: ARA is per-tick, the prediction step is the SAME layered
sand engine, and the flow is tweaked by the topographic values with the rule **more info (higher Z) → closer to
the φ handover** (implemented as `phi_gate=sigmoid(Z)` and an `info_to_phi = phi_gate × roll` flow term).
**φ vs anti-φ:** used as TWO unsigned distance coordinates (most consistent with the engine's unsigned coupling
magnitudes).

- **Version A (geometry-native):** stable sand-engine features + the per-tick sphere coordinates + the info→φ
  flow term, through the same ridge readout.
- **Version B (bolt-on):** stable ARA prediction + elastic-wall bounce (elasticity 1/φ off ±1.5σ envelope walls)
  + regime gate (blend toward seasonal-naive near the ARA≈1 balance/transition band).

## Results (corr / MAE)

| method | h=3 | h=6 | h=12 | h=18 | h=24 |
|---|---|---|---|---|---|
| persistence | +0.693/8.5 | +0.128/15.4 | −0.686/23.1 | −0.329/20.1 | +0.387/11.3 |
| seasonal-naive | +0.408/11.5 | +0.403/11.5 | +0.397/11.5 | +0.387/11.7 | +0.383/11.8 |
| **lag-harmonic-ridge** (strongest baseline) | +0.877/5.3 | +0.750/7.2 | **+0.728/7.6** | **+0.562/9.3** | **+0.491/9.9** |
| home_ar | +0.875/5.4 | +0.730/7.6 | +0.715/7.8 | +0.508/9.9 | +0.361/11.2 |
| ARA stable (home+ara) | +0.877/5.4 | +0.753/7.3 | +0.729/7.7 | +0.505/10.1 | +0.356/11.3 |
| **G3-A geometry-native** | **+0.878/5.4** | **+0.769/7.1** | +0.705/8.0 | +0.502/10.1 | +0.319/11.6 |
| G3-B wall+regime | +0.831/6.2 | +0.686/8.0 | +0.673/8.2 | +0.496/10.0 | +0.348/11.3 |

## Honest read

- **G3-A is the first genuine geometry-native lift:** best of all methods at **h=6** (+0.769/7.13 — beats
  lag-harmonic-ridge and stable ARA on both corr and MAE) and tied-best at h=3. So the per-tick sphere
  coordinates + info→φ flow term added real signal at short horizons. It **fades at long horizons** (h=18–24),
  where the harmonic baseline wins.
- **G3-B is a dud on QBO** — worse than stable ARA at every horizon. Wall-bounce + regime-blend were tuned for
  ENSO's spread/noisy dynamics; QBO is a clean single oscillator that doesn't need them, and blending toward
  the (weak) seasonal-naive drags it down. (Elastic walls were a real win on ENSO before — system-specific.)
- **lag-harmonic-ridge remains the overall QBO champion** (long horizons). Neither G3 version dominates it.
- **Consistent with the concentration meta-rule:** QBO is concentrated (one clean cycle), so big wins aren't on
  offer and ARA-family methods should roughly *tie* the strong harmonic baseline — which they do. A small
  geometry-native edge at h=6 is the realistic ceiling here. **The real test of geometry-native is ENSO** (the
  spread/mountain system) where there is room above the baselines.

## Status / next
- G3-A shows promise at short horizons; G3-B not useful for concentrated systems. Neither graduates into the
  stable engine yet (must beat the strong baseline more broadly first).
- Next: run G3-A (and G3-B) on **ENSO** — the low-concentration system where the geometry-native coupling has
  room to win. Code: `TheFormula/ara_g3_experimental.py`. Stable trio unchanged.

---

## G3-A geometry-native on ENSO (3 June 2026) — the spread/mountain test

Real NINO3.4 anomaly (n=1872 months, P=48, golden split, self-forecast). Same implementation as QBO
(dynamic ARA per tick, φ/anti-φ as two unsigned distances, info→φ flow tweak). vs all baselines:

| method | h=3 | h=6 | h=12 | h=18 | h=24 |
|---|---|---|---|---|---|
| persistence | +0.768/0.47 | +0.404/0.73 | −0.081/0.95 | −0.204/1.08 | −0.274/1.10 |
| seasonal-naive | +0.057 | +0.057 | +0.056 | +0.058 | +0.061 |
| lag-harmonic-ridge (strongest) | +0.798/0.42 | +0.499/0.60 | +0.168/0.66 | **+0.212/0.66** | **+0.160/0.67** |
| home_ar | +0.805/0.41 | +0.527/0.58 | +0.189/0.66 | +0.207/0.66 | +0.163/0.67 |
| ARA stable (home+ara) | +0.807/0.41 | +0.538/0.58 | +0.298/0.64 | +0.160/0.67 | −0.019/0.70 |
| **G3-A geometry-native** | +0.807/0.41 | **+0.573/0.56** | **+0.319/0.64** | +0.146/0.68 | −0.047/0.71 |

**GENUINE WIN at the mid-horizons.** G3-A beats both stable ARA AND the strongest baseline at:
- **h=6:** +0.573 vs ARA +0.538 (+0.035) vs lag-harmonic-ridge +0.499 (**+0.074 over the best baseline**).
- **h=12:** +0.319 vs ARA +0.298 (+0.021) vs lag-harmonic-ridge +0.168 (**+0.151 over the best baseline**).
- h=3: tied at the top (+0.807).
- h=18–24: **fades** — long horizons are driver-below territory (spring barrier, WWV/SOI the self-forecast
  can't see); the harmonic baseline edges ahead there.

**Read:** the geometry-native sphere coordinates + info→φ flow tweak add real signal exactly where the framework
has room — the coupled, low-concentration regime, at the operationally important 6–12 month ENSO window. This is
the first clear evidence that geometry-native is worth pursuing. It is NOT a wholesale win (long horizons still
need real drivers), and it must still be replicated and tested with feeders before graduating into the stable
engine. Contrast with QBO (concentrated): there G3-A could only tie/edge at h=6, exactly as the concentration
rule predicts. QBO concentrated → tie ceiling; ENSO spread → real mid-horizon win.

---

## G3-A geometry-consistent FEEDERS on ENSO (WWV/SOI) — honest negative (3 June 2026)

Built the geometry-consistent feeder version: each feeder (WWV, SOI) gets its OWN per-tick 5-axis sphere
(dynamic ARA, Z=info, φ/anti-φ, own flow); coupling routed by named relation — **WWV = driver-below, in-phase,
rung-scaled lead-lags; SOI = mirror/anti-φ, sign-flipped (2−ARA)**; learnable magnitude on geometric features,
rung-scaled gain (gW=√(48/6)=2.83, gS=√(48/3)=4 — "pebble/boulder"). Real WWV-west + SOI + NINO3.4, common
window 1980–2024 (n=552), golden split.

**SOI anti-phase CONFIRMED:** corr(SOI, NINO) = **−0.729** — SOI sits naturally as the mirror partner, exactly as
expected. The geometry held there.

**Result (corr; on the WWV-era window):**

| method | h=3 | h=6 | h=12 | h=18 | h=24 |
|---|---|---|---|---|---|
| ARA stable | +0.826 | +0.526 | +0.271 | +0.134 | +0.262 |
| home_ar | +0.824 | +0.513 | +0.200 | +0.201 | +0.352 |
| G3-A self | +0.826 | +0.511 | +0.261 | +0.035 | +0.236 |
| **G3-A + feeders** | +0.813 | +0.408 | +0.138 | −0.019 | +0.219 |

**Honest negatives:**
- **The per-feeder-sphere coupling HURT at every horizon** — worst row almost everywhere. **Long horizons
  (h=18–24) did NOT recover**; they degraded.
- **The earlier G3-A self mid-horizon win did NOT replicate on this shorter window** — here G3-A self ≈ slightly
  below stable ARA (h=6 +0.511 vs +0.526). So the geometry-native edge is **window-sensitive, not yet robust.**
- **Likely cause:** feature bloat / overfitting — ~16 rung-amplified feeder features added to ~26 base features
  on only ~340 training points, plus a crude `own_spin`-as-flow feeder proxy. The stable engine's LEANER feeder
  coupling (each feeder → a couple of torque scalars) already worked better (it reached ENSO 6-mo ≈+0.6).

**Lesson (bounds where geometry-native helps):** the TARGET's own sphere coordinates can add signal (full-window
ENSO mid-horizons), but **routing each FEEDER as a full separate sphere with learnable magnitude overfits and
loses to the simpler coupling.** Geometry-native is promising for the target's state, not (in this form) for
feeder injection. Neither graduates to the stable engine; the stable trio's feeder handling stays the recommended
path. SOI-as-mirror geometry validated.

---

## φ-handover-ONLY feeder coupling on ENSO (lean, Z-driven lag) — neutral (3 June 2026)

New direction: drop the sand-flow for inter-sphere coupling; couple each feeder to the target by the **φ-handover
relation alone**, lean (2 features total). Each feeder keeps its own sphere; coupling =
`sign · eff_f(t) · feeder_value(t − max(0, lag−h))`, with **Z setting BOTH efficiency and timing**:
`eff = σ(Z_f)`, `lag_f(t) = round((P_target/φ)·eff)` (Z = slow trailing-|Δz| info level). Geometric rationale:
the golden handover hands forward the kept fraction 1/φ of the target's cycle, scaled by the driver's info via
the same σ(Z) gate — more info → tighter, more-golden handover → looks farther ahead. WWV in-phase driver-below
(+), SOI mirror/anti-φ (−), rung-scaled learnable magnitude. Real WWV/SOI/NINO, 1980–2024 (n=552).

**Lag behaved as designed:** WWV lead mean 15.6 mo (4–29), SOI 14.7 mo (4–29) — sensible ENSO driver lead,
info-modulated, near-static as expected (Z slow).

| method | h=3 | h=6 | h=12 | h=18 | h=24 |
|---|---|---|---|---|---|
| home_ar (plain AR) | +0.824 | +0.513 | +0.200 | **+0.201** | **+0.352** |
| ARA stable | +0.826 | +0.526 | +0.271 | +0.134 | +0.262 |
| G3-A self | +0.826 | +0.511 | +0.261 | +0.035 | +0.236 |
| G3-A + φ-handover feeders | +0.818 | +0.519 | +0.234 | +0.044 | +0.223 |

**Honest read:**
- **Lean φ-handover FIXED the overfitting** — no longer the worst row (vs the heavy sand-flow version which
  cratered to +0.408@h6, −0.019@h18). Overfit diagnosis confirmed: sand-flow + 16 rung-amplified features was
  the problem; 2 lean Z-gated features behave.
- **But it is NEUTRAL — adds no value and does NOT recover long horizons.** At every horizon ≈ or just below
  stable ARA / G3-A self. At h=18–24 the BEST method is **plain causal AR memory (home_ar +0.201/+0.352)** —
  the long-horizon signal is ordinary memory, not the geometry or the feeders.

**Verdict on the whole G3 arc (honest):** geometry-native has NOT yet produced a robust, replicating win.
- G3-A self beat baselines on the FULL ENSO window mid-horizons but NOT on the WWV-era window (window-sensitive).
- Feeder coupling: sand-flow = overfit/harmful; φ-handover = clean but neutral; neither beats stable ARA or plain
  AR, neither recovers long horizons.
- Nothing graduates into the stable trio (frozen). Stable engine + its existing feeder handling remain the
  recommended path. The Z-driven-lag idea is mechanically sound (sensible ~15-mo lead) but the coupling it drives
  doesn't outperform memory here.

---

## Spin-lock feeder coupling on ENSO (resonance + face-lock floor) — small h=3 win, no long recovery (3 June 2026)

Entrainment picture (Dylan's "moon is a clock at 1.0"): feeders are phase/face-LOCKED to the main, spin is
relational. Final lean formulas (1 feature per feeder):
- **Resonance (rung-gap → relative spin):** r_f = P_main/P_feeder; weight g = √(r−1), **face-lock floor at r=1
  = no info** (the Moon). WWV r=8 (g=2.65), SOI r=16 (g=3.87).
- **Lock strength (φ-distance → tightness):** L_f(t) = σ(Z_f) — bounded info→φ gate (chosen over raw 1/φ_dist
  to avoid the close-limit blow-up).
- **Locked phasor projected forward:** cos(θ_f(t) + 2π·h/P_f), θ_f causal phase.
- **Coupling:** c_f = sign·g·L_f(t)·cos(θ_f+2πh/P_f); +WWV / −SOI mirror; learnable magnitude. Main keeps full sphere.
- **Degeneracy: handled** — no blow-up (face-lock floor sends weight→0 at the close/same-period limit; σ(Z) and
  capped √(r−1) are bounded). Confirmed g=2.65/3.87, well-behaved.

| method | h=3 | h=6 | h=12 | h=18 | h=24 |
|---|---|---|---|---|---|
| home_ar (plain AR) | +0.824 | +0.513 | +0.200 | +0.201 | **+0.352** |
| ARA stable | +0.826 | +0.526 | +0.271 | +0.134 | +0.262 |
| G3-A self | +0.826 | +0.511 | +0.261 | +0.035 | +0.236 |
| **G3-A + spin-lock** | **+0.834** | +0.521 | +0.259 | +0.032 | +0.221 |

**Read:** best feeder coupling of the arc — a **small genuine win at h=3 (+0.834, best of ALL methods)**, cleanly
behaved (no overfit, no blow-up). But **neutral at mid horizons and NO long-horizon recovery** — h=18–24 stay
below stable ARA and well below plain AR memory (home_ar +0.20/+0.35 remains the long champion). The feeders do
not crack the 18–24 mo wall.

**Arc summary (3 feeder couplings):** sand-flow (HARMFUL) → φ-handover (NEUTRAL) → spin-lock (small h=3 win,
neutral mid, no long recovery). Each refinement cleaner and slightly better, converging on the same ceiling:
**geometry buys a marginal short-horizon edge; long horizons stay memory-dominated.** Nothing graduates; stable
trio frozen; the face-lock=no-info insight is the keeper (degenerate feeders identified geometrically).

---

## PDO driver-ABOVE test — does a larger/slower system above ENSO recover h=18–24? (4 June 2026)

Dylan's hypothesis: the 18–24mo wall isn't memory-only — a larger, slower system *above* ENSO (like a slow
regulator over a fast one, insulin-style) starts governing at long horizons. Mirror of the driver-below work.

**Relation classified from real data (the universe-analogy step):** measured dominant periods —
PDO **346 mo ≈ 28.8 yr**, ENSO **66.9 mo ≈ 5.6 yr** → ratio **5.17**. Nearest integer resonance **5:1 (3.4% off)**;
nearest φ-power φ³ = 4.24 (**22% off**). So PDO↔ENSO is a **Mercury-like 5:1 spin-orbit resonance — the "snap"
class**, NOT a φ-engine and NOT a 1:1 clock. Snap → discrete quasi-static **regime bias** keyed to PDO's slow phase.
(PDO *also* has a 67 mo peak = same band as ENSO = 1:1 face-lock / no-independent-info; stripped by causal low-pass.)

**Test (strict-causal, real NINO3.4 1870+ & ERSST PDO, golden split):** G3-A self + PDO fed three ways —
(1) decadal (>120mo, trailing-mean) regime bias; (2) raw contemporaneous PDO + decadal + ARA-interaction;
(3) explicit 5:1 resonance phasor. Compared vs home_ar, lag-harmonic-ridge, stable ARA, G3-A.

| h | home_ar | lag-harm | stable ARA | G3-A | +PDO bias | +PDO raw | +PDO 5:1 |
|---|---|---|---|---|---|---|---|
| 3 | +0.816 | +0.812 | +0.807 | +0.807 | +0.806 | +0.808 | +0.798 |
| 6 | +0.543 | +0.535 | +0.538 | +0.573 | +0.571 | +0.575 | +0.543 |
| 9 | +0.272 | +0.266 | +0.339 | +0.385 | +0.384 | +0.389 | +0.362 |
| 12 | +0.133 | +0.134 | +0.298 | +0.319 | +0.319 | +0.340 | +0.319 |
| 15 | +0.083 | +0.082 | +0.237 | +0.235 | +0.235 | +0.253 | +0.237 |
| 18 | +0.087 | +0.084 | +0.160 | +0.146 | +0.146 | +0.145 | +0.159 |
| 24 | −0.006 | −0.001 | −0.019 | −0.047 | −0.048 | −0.087 | +0.025 |

**VERDICT — PDO driver-above is INERT.** All three coupling forms ≈ G3-A to the third decimal; ridge gives PDO
~zero weight. **h=18–24 did NOT recover.** At h=24 every method sits at ~0 — this reads as a genuine ENSO
predictability floor, not a missing upper driver (or at least PDO is not it). Dylan's driver-above hypothesis is
**not supported** for ENSO via PDO.

**Genuine positive that surfaced (worth its own follow-up):** in this long monthly config, **stable ARA / G3-A
clearly beat AR memory at the wall (h=9–18)** — e.g. h=12 ARA +0.298 / G3-A +0.319 vs home_ar +0.133, lag-harm
+0.134 (≈ +0.18 edge). This *contradicts* the earlier "home_ar dominates ENSO long horizons" note — the framework
coupling carries real mid-long-horizon signal here that plain memory and a seasonal-harmonic clock do not. Script:
TheFormula/g3_pdo_driver_above_test.py.

---

## SOLAR driver-ABOVE (clean 2:1 octave) — extended horizons to 72mo (4 June 2026)

After PDO (5:1 snap, oceanic) gave nothing, Dylan reframed: PDO is the slow *anti-phase* partner, not the driver.
The real driver-above should be a genuinely SLOWER-rung UPPER-ATMOSPHERE system. Candidate shortlist by rung fit
& repo data: **solar cycle 133mo = clean 2:1 octave above ENSO (1% off)** — the framework's *preferred* octave
spacing, vs PDO's odd 5:1. (Lunar nodal 18.6yr ~3:1 was secondary; QBO ruled out — faster, altitude-above but
rung-below.) Dylan's specific prediction: solar is "an extra jump up," so it **won't** fix the 18–24mo wall (stays
murky) but should **extend predictability at the long year-marks (36–72mo)**.

**Test (strict-causal, NINO3.4 1870+ & SILSO monthly sunspots, golden split, horizons to 72mo):** solar fed as
causal trailing-mean level + octave phasor (133mo & 66.5mo) carried FORWARD to t+h (fixed period = train-safe, so
the slow octave can actually reach long horizons).

| h | home_ar | lag-harm | stable ARA | G3-A | G3-A+solar |
|---|---|---|---|---|---|
| 3 | +0.816 | +0.812 | +0.807 | +0.807 | +0.802 |
| 6 | +0.543 | +0.535 | +0.538 | +0.573 | +0.550 |
| 9 | +0.272 | +0.266 | +0.339 | +0.385 | +0.349 |
| 12 | +0.133 | +0.134 | +0.298 | +0.319 | +0.279 |
| 18 | +0.087 | +0.084 | +0.160 | +0.146 | +0.156 |
| 24 | −0.006 | −0.001 | −0.019 | −0.047 | −0.004 |
| 36 | −0.019 | −0.021 | +0.087 | +0.033 | +0.056 |
| 48 | −0.005 | −0.001 | −0.078 | −0.078 | −0.041 |
| 60 | +0.057 | +0.056 | −0.011 | −0.040 | +0.029 |
| 72 | −0.066 | −0.067 | −0.000 | −0.035 | +0.037 |

**VERDICT — solar driver-above is INERT (Dylan half-right).** (1) **18–24mo wall: stays murky** — exactly as Dylan
predicted; solar doesn't touch it. (2) **Long year-marks 36–72mo: NOT recovered.** Solar nudges them from
slightly-negative (~−0.04) to slightly-positive (~+0.04), but that's **within noise** and at h=60 the plain
baselines (+0.057) already match/beat G3-A+solar (+0.029). At short h solar even slightly *hurts*. No usable
long-horizon signal.

**The robust cross-cutting finding (two slow drivers now, ocean + atmosphere, both null):** **beyond ~36mo, EVERY
method — framework, AR memory, seasonal clock, ocean driver (PDO), atmosphere driver (solar) — sits at ~0.** Two
independent slow driver-above candidates on *different* rung relations (5:1 snap, 2:1 octave) both add nothing. This
is strong evidence the long-horizon ENSO wall is a **genuine predictability floor of the target's value**, not a
missing-driver problem. The driver-above thread is closed for ENSO point-value forecasting. (Direction/regime
prediction remains a separate, untested target.) Script: TheFormula/g3_solar_driver_above_test.py.

---

## Green/gold crossing-PUMP as a DIRECTION predictor — direction survives the value-floor (4 June 2026)

Dylan's reframe: stop hunting external drivers; the lever may be INTERNAL — ENSO as a pump firing at the crossing
of its own green band (24–33mo) and gold band (40–70mo), predicting TRANSITION TIMING/SIGN, not value. Plus his
four-role taxonomy (every system has a snap/clock/engine/harmonic).

**Four-role map (data-derived, real NINO3.4):** annual **12mo = CLOCK** (the 1:1 seasonal face-lock); semiannual
**6.7mo = HARMONIC**; green/quasi-biennial **27.9mo = SNAP**; gold/quasi-quadrennial **66.9mo = ENGINE** (the
recharge–discharge oscillator). (Refines Dylan's earlier "gold=clock" → data says gold=engine, annual=clock; he
deferred to the data read.)

**Pump built per Dylan's spec:** fire at green×gold constructive crossing → fill the gold ENGINE toward **2.0**
(=2σ saturation) → **φ-time handover** PHI^(−h/Pgold) carries the fill forward over the horizon distance. Output =
**sign of NINO change**, strict-causal (one-sided `causal_bandpass`, causal phase/amp, train-only σ & threshold).

| h | pump direction | value corr (floor) | persistence-dir | chance |
|---|---|---|---|---|
| 6 | 0.614 | +0.102 | 0.500 | 0.50 |
| 12 | 0.666 | −0.003 | 0.453 | 0.50 |
| 18 | **0.727** | −0.017 | 0.445 | 0.50 |
| 24 | **0.736** | +0.022 | 0.409 | 0.50 |
| 36 | 0.662 | +0.010 | 0.450 | 0.50 |
| 48 | 0.620 | −0.017 | 0.412 | 0.50 |
| 60 | 0.641 | −0.055 | 0.475 | 0.50 |

**WIN — direction survives the value-floor.** At 18–24mo we call ENSO's swing-sign ~73–74% (chance 0.50; N≈690 so
2σ≈0.04 → highly significant; persistence is *below* chance ~0.41 because ENSO mean-reverts) while value corr ≈ 0.
**Direction and value are different targets; direction is predictable 1.5–2yr out where value is dead.** This
validates the broader "predict the transition, not the number" thesis and is the most useful long-lead ENSO result
in the whole arc.

**NULL — the specific pump mechanism adds nothing.** Control = same forward projection with the pump fill OFF
(plain gold-cycle phase projection): h=12 0.692, h=18 0.732, h=24 0.749, h=48 0.645 — **matches/slightly beats the
full pump at every horizon.** So the crossing, the 2.0 fill, and the φ-handover contribute zero; **all the skill is
the gold ENGINE's forward-projectable PHASE.** The lever isn't a pump firing at a crossing — it's that the slow
build/release engine turns at a knowable rate, so knowing its phase tells you which way ENSO is about to move. The
green-snap crossing doesn't time it better than the engine's own clock. Script:
TheFormula/enso_crossing_pump_direction_test.py.

---

## 0.382 shed-handoff to PDO (gold engine sheds 1/φ² to PDO at the pump) — NOT supported (4 June 2026)

Dylan: "when the cross pumps, PDO takes over for 0.38 energy" — i.e. at each pump the gold ENGINE sheds 1/φ²≈0.382
to PDO (keeps 1/φ), so PDO = cumulative leaky integral of ENSO's shed; PDO is the downstream SINK, explaining why
PDO didn't *forecast* ENSO. Formalized: engine=causal_bandpass(NINO,55mo); E=amp²; shed flux=max(0,−dE/dt);
PDO_recon=leaky-integrate(0.382·sign(NINO)·shed, τ). Strict-causal, real NINO3.4 1870+ & ERSST PDO.

**RESULT — handoff NOT supported (3 independent reasons):**
1. Signed reconstruction peaks at only **r≈0.26 and pins at the +60mo lag boundary** (artifact, not a real handoff
   lag); unsigned ≈0. Plain low-pass NINO (+0.49) tracks PDO *better* than the shed reconstruction.
2. **0.382 is not identifiable here:** a single shed fraction is correlation-scale-invariant — corr was flat
   (−0.248) for f=0.2, 0.382, 0.5, 0.6. Correlation cannot single out 1/φ².
3. **DECISIVE — lead/lag runs the WRONG way.** A handoff needs ENSO to LEAD PDO. Low-pass NINO vs PDO peaks at
   **lag −5 to −15 mo → PDO LEADS / is simultaneous with ENSO**, not downstream of it.

**Read:** ENSO's gold-engine shed does not build PDO and the timing contradicts ENSO→PDO. This *reinforces* the
earlier reframe rather than rescuing it — NINO & PDO share a strong contemporaneous corr (+0.41) with PDO slightly
leading = **PDO is the slow background partner ENSO sits inside, not an upstream driver nor a downstream sink.** The
earlier PDO forecast-null and this shed-null tell one consistent story. The surviving keeper of the whole arc is
unchanged: **the gold engine's forward-projectable phase → direction callable ~0.73 at 18–24mo while value is
floored.** Script: TheFormula/enso_pdo_shed_handoff_test.py.

---

## PDO every-second-wave ALTERNATION gate — NOT supported (4 June 2026)

Dylan sharpened (distinct from the energy-handoff): PDO "takes over" = reversed trough/crest every ~2nd ENSO wave
(period-doubling), PDO's slow phase selecting which alternation state. Payoff question: does it LIFT the
gold-engine-phase direction skill (~0.73)? Strict-causal, NINO3.4 1870+ & ERSST PDO; 78 gold-engine extrema.

1. **NO period-doubling.** Event-magnitude lag-1 autocorr = **+0.63** (consecutive events SIMILAR; true alternation
   needs negative lag-1). Subharmonic power (95–130mo)/engine(45–70mo) = **0.14**. Sign-flip fraction = 0.42 (<0.5).
2. **PDO phase does NOT select the state.** corr(PDO, alternation state) = **−0.016**; sign(PDO) predicts state at
   **0.468** (below chance).
3. **+PDO gate HURTS direction:** h=12 0.551 / h=18 0.560 / h=24 0.545 vs engine-phase baseline 0.692 / 0.732 /
   0.749 — drags toward chance everywhere.

**Verdict:** the every-2nd-wave / PDO-gated reversal isn't in the data; ENSO events are broadband-irregular but not
cleanly period-doubled, and PDO selects no state. Consistent with every PDO result this session — no ENSO-predictive
information in any framing (driver-above / energy-sink / alternation-gate). Engine-phase direction (~0.73 @18–24mo)
stands alone. (Caveat: real decadal ENSO amplitude modulation exists in the literature, just not as this clean
2-cycle PDO-gated reversal.) Script: TheFormula/enso_pdo_alternation_test.py.

---

## Golden-duty centerline ASYMMETRY (0.68/0.32) — NOT supported (4 June 2026)

Dylan: ENSO crosses the 1-line and "goes the other way" with a 1/φ / 1/φ² (0.618/0.382) split above/below, not
50/50; does honoring it sharpen the turn calls? Strict-causal, NINO3.4 1870+, gold engine 55mo.

1. **Engine is SYMMETRIC about the centerline:** time duty 0.510/0.490, amp/area 0.500/0.500, rise/fall
   0.505/0.495, segment durations 27.3/26.1mo → 0.511. Nowhere near 0.618/0.382. (Bandpass symmetrizes; the fairer
   raw-NINO test shows the *known* mild El Niño skew — time-above ≈0.46 — but amp-duty 0.50, i.e. mild skew, NOT a
   golden duty.)
2. **Free-fit duty scatters** across horizons (0.575, 0.550, 0.350, 0.325, 0.400) — no convergence on 1/φ or 1/φ².
3. **Golden-duty phase warp gives no real lift:** direction hit-rate moves only ~+0.01–0.017 (within noise,
   2σ≈0.04), and the best-fit duty isn't golden.

**Verdict:** the 0.68/0.32 centerline asymmetry isn't in ENSO's engine (symmetric); the real ENSO skew is mild and
non-golden; honoring an asymmetry doesn't sharpen reversal timing. Symmetric engine-phase direction (~0.73 @18–24mo)
remains the keeper. Script: TheFormula/enso_golden_duty_asymmetry_test.py.
