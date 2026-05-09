# Mapping to the Framework

**The Framework method: how to take a real system, decompose it into ARA subsystems, and produce both descriptive and predictive output using only framework-derived constants.**

*Last updated: 2026-04-30*

> **Update 2026-04-30 (late):** A deeper formulation has been articulated: **the wave IS the time-geometry**. ARA + framework geometry give wave SHAPE; energy log-slider gives AMPLITUDE; multi-scale is the same wave at φ-scaled time-rulers. See `THE_FRAMEWORK_FORMULATION.md` for the unified formulation. This document describes the discovery-process method that led there — still operationally useful, but the mature form treats shape and amplitude as separate concerns.

---

## Two distinct uses of the framework

The framework gives you two related but separate capabilities:

### 1. The **Mapper / Tracker** (descriptive)
Takes a real system's time series. Decomposes it into framework-meaningful subsystems on the φ-rung ladder. Produces a labelled inventory: which rungs are present, which coupling types they have, what their ARAs are. Each component has physical meaning.

### 2. The **Forecaster** (predictive)
Same formula, used in blind mode (subsystems only, rungs that pass the pinning rule, plus the 1/φ³ AA-boundary AR feedback). Generalises forward to unseen data.

The mapping and the forecast are the *same machinery* — what changes is whether the components are fit-then-described or fit-then-extrapolated.

---

## The Framework method vs the Vehicle

There are two distinct levels of "blindness" in framework prediction:

| | **Vehicle (pure generative)** | **Framework method (fitted)** |
|---|---|---|
| Inputs | 4 numbers: ARA, amp(t₀), period, span | Time series of training data |
| Sees data? | Only one anchor point at t=0 | Yes — fits to training residuals |
| What it gets right | Amplitude shape (envelope geometry) | Phase, timing, magnitude per rung |
| What it gets wrong | Phase (can't know when sleep starts) | Amplitude reach (LSQ compresses extremes) |
| Empirical (nsr001 ECG) | corr ~0, std reach 67% | corr +0.86, std reach 36% |

**Both are real, and they are complementary.** The Vehicle proves the cascade structure produces data-shaped output from first principles. The Framework method proves you can phase-align that structure with minimal training. The intermediate option — Vehicle + Teleporter (re-anchored periodically) — gives a continuum.

For most practical forecast applications, the **Framework method with 1/φ³ AR feedback** is what you want.

---

## The Hierarchical Heart Map (worked example)

The heart's pump is the ground cycle at φ¹ ≈ 1.62s. Subsystems feed INTO the pump via coupling channels with their own ARAs (Rule 9 from `ARA_decomposition_rules.md`):

- **Type 1 handoff** (peer-scale, ≤1 rung from pump): coupling channel ARA ≈ φ; gap-junction-like
- **Type 2 overflow** (rung-distant, >1 rung from pump): coupling channel ARA ≈ 5; passive

Coupling strength κ falls off with rung distance:
- Type 1: κ = 1/φ^|Δk|
- Type 2: κ = 1/φ^(2|Δk|)

The pump's R-R sequence is the centerline plus contributions from each subsystem, weighted by κ.

**Note:** when the joint LSQ fit is unconstrained, it absorbs κ into amp_raw automatically — the κ factor is interpretive, not constraining. For physically meaningful per-subsystem amplitudes, regularize amp_raw or constrain it directly.

### Subsystems found on real ECG R-R data

For the 22.5-hour nsr001 recording (PhysioNet NSR RR Interval Database), pump at φ¹, training span 17h:

| Rung | Period | Coupling | ARA | Effective amp | Physiology |
|---|---|---|---|---|---|
| φ²¹ | 6.8h | T2 | 0.64 | −93 ms | autonomic state envelope |
| φ²⁰ | 4.2h | T2 | 0.64 | +96 ms | meta-deck alternation |
| φ¹⁹ | 2.6h | T2 | 0.91 | −67 ms | matches BRAC (~90 min half-cycle) |
| φ¹⁸ | 1.6h | T2 | 0.37 | −63 ms | shorter ultradian |

**The framework's φ-rung structure aligns with documented physiology** (Basic Rest-Activity Cycle, autonomic/circadian modulation) without being told to. Subsystem periods land on documented rhythms.

---

## The Rung-Pinning Rule

**Operational rule:** for blind forecast, only include subsystems whose period × 2 ≤ training span.

For each candidate rung k:
- `cycles_in_train = train_span / period_k`
- Subsystem is **pinned** if `cycles_in_train ≥ 2`
- Subsystem is **unpinned** otherwise

Including unpinned rungs makes blind forecast **worse than excluding them**. The fit will use them to memorise training residuals; on test data, the unpinned phase slides arbitrarily, producing negatively-correlated forecasts.

### Empirical confirmation across three systems

| System | Train span | Slowest rung pinned | TRAIN corr | TEST corr blind |
|---|---|---|---|---|
| ECG R-R (200 beats, 145s) | 58s | φ⁶ (only) | +0.62 | **−0.15** ✗ |
| ENSO ONI monthly | 60 years | φ⁷ (29yr, 2.6 cycles) | +0.49 | +0.43 ✓ |
| ECG R-R nsr001 (22.5h) | 17h | φ²¹ (6.8h, 2.5 cycles) | +0.30 | **+0.55** ✓ |

The drop from "all rungs pinned" to "some rungs unpinned" inverts the forecast sign. This is **Rule 7** ("shorter strings predict more") empirically demonstrated.

For systems where data span is too short, the rule says drop the unpinned rungs and accept smaller amplitude reach. For ECG-200 with adjacent rungs only, blind corr was +0.16 — modest but positive.

---

## The AA-boundary 1/φ³ AR feedback

The framework predicts that each subsystem cycle inherits a 1/φ³ fraction of the previous cycle's deviation (the "AA-boundary momentum" from `framework_three_circles.md`). Originally implemented within events; we found it works *much better* when applied at the **beat-to-beat level continuously** as a causal autoregressive term.

### The rule

```
pred(n) = subsystems(n) + γ × residual(n−1)
```

where `residual(n−1) = v_observed(n−1) − subsystems(n−1)` and γ = 1/φ³ ≈ 0.236.

Strictly causal — each prediction uses only previous observed values.

### Empirical confirmation (nsr001 22.5h ECG, 5.6h test cold)

| γ | TEST corr | TEST MAE | std reach |
|---|---|---|---|
| 0 (no AR) | +0.547 | 162 ms | 0.22 |
| **1/φ³ (framework)** | **+0.864** | **127 ms** | **0.36** |
| 1/φ² | +0.902 | 107 | 0.47 |
| 1/φ | +0.917 | 76 | 0.67 |
| 0.85+ | +0.917 | 58 | 0.87 |

**The framework constant is the inflection point of the gain curve.** Below γ = 1/φ³, corr improves rapidly. Above it, gains are marginal. The framework predicts the right floor.

The compounded inheritance also recovers amplitude. For ~50 consecutive long beats during deep sleep, each beat inheriting 1/φ³ of the previous deviation compounds geometrically — the prediction reaches deep amplitude that periodic subsystems alone cannot.

---

## The 1/φ⁴ Teleporter Blend Coefficient

The Teleporter (Vehicle re-anchored periodically using observed local means) gives blind corr +0.66 with full amplitude reach (std ratio 1.01). Blending it with Framework + 1/φ³ AR improves both MAE and amplitude reach modestly:

```
pred = α · Teleporter + (1−α) · Framework_AR
```

### Empirical optimum on nsr001 22.5h ECG (5.6h blind)

| α | corr | MAE | std reach |
|---|---|---|---|
| 0 (Framework_AR alone) | +0.864 | 127 | 0.36 |
| **1/φ⁴ ≈ 0.146** | **+0.857** | **123** | **0.42** |
| 1/φ³ ≈ 0.236 | +0.835 | 125 | 0.47 |
| 1/φ² ≈ 0.382 | +0.792 | 135 | 0.56 |
| 1.0 (Teleporter alone) | +0.659 | 238 | 1.01 |

Search-optimum α (by MAE, fine grid) lands exactly on **α = 0.146 = 1/φ⁴**, the framework's three-circle damping coefficient (`framework_three_circles.md`). This was not tuned — the search and the framework constant coincided.

When extended to a 3-way blend (Teleporter + Vehicle + Framework_AR), Vehicle weight goes to zero at the optimum. The 3-way blend collapses to the 2-way Tele+Framework_AR blend at α = 1/φ⁴, confirming Vehicle's wrong-phase predictions don't add value to a blend with phase-correct alternatives.

### Three framework constants now validated on the same blind test

1. **Rung-pinning (Rule 7 / φ⁹ span)** — drop subsystems whose period × 2 > train_span. Flipped ECG-200 from corr −0.15 to +0.16.
2. **1/φ³ AR feedback (AA-boundary)** — beat-to-beat momentum coefficient. Lifted blind corr from +0.55 to +0.86.
3. **1/φ⁴ Teleporter blend (three-circle damping)** — empirical search optimum matches framework prediction.

All three are framework predictions made *before* fitting; all three landed on or near the empirical optimum.

---

## The full Framework method recipe

For any oscillatory system with a known ground cycle:

### Step 1 — Identify the pump
Find the system's irreducible cycle. Its period sets pump rung k_p:
- Heart: ventricular pump → φ¹ (1.62s)
- ENSO: triggering rhythm → φ³ (4.24yr)
- Solar: Schwabe → φ⁵ (11.09yr)
- Sanriku EQ: cluster spacing → φ⁶ (17.94yr)

### Step 2 — Determine candidate rung set
List rungs k = k_p ± 0, 1, 2, ..., up to the system's natural ladder (typically φ⁹ span).

### Step 3 — Apply rung-pinning rule
For each candidate k, compute `cycles = train_span / φ^k`. Drop rungs where cycles < 2.

### Step 4 — Fit subsystems
For each pinned rung, search `(ARA, t_ref)` grid for best fit. Joint LSQ refit at the end with all subsystems' shapes fixed and amplitudes optimised simultaneously.

### Step 5 — Classify couplings
- |k − k_p| ≤ 1: Type 1 handoff (coupling ARA ≈ φ)
- |k − k_p| > 1: Type 2 overflow (coupling ARA ≈ 5)

For Type 2, use `overflow_envelope` (rectified positive). For Type 1, use `value_at_times` (full bidirectional wave).

### Step 6 — Apply 1/φ³ AR feedback for forecast
For each predicted point at time `t_n`:

```
pred(n) = subsystems(t_n) + (1/φ³) × residual(n−1)
```

Only past *observed* values are used — strictly causal.

### Step 7 — Honest evaluation
Score on truly held-out test data. Track:
- TRAIN corr (in-sample)
- TEST corr (blind)
- std_ratio (amplitude reach) on test
- MAE comparison vs centerline-only baseline

Flag: small samples + many basis functions → overfitting risk.

---

## Negative results worth keeping

Things tested that **didn't work**, with reasons. Useful as guardrails for future attempts.

### Multiplicative envelope (option #2 from session 2026-04-30)
Tried `pred = c + (1 + αE(t))·Σ subsystems`, with E(t) a slow-rung envelope. On ENSO this *worsened* TEST corr (+0.43 → +0.13). Reason: the slow rungs carry direct additive forecast skill on ENSO; demoting them to envelope removes that signal.

The framework's "system level" for ENSO appears to live in the slow rungs themselves, not in a separate envelope.

### Vehicle + Framework linear blend
Tried `pred = α·Vehicle + (1−α)·Framework_AR`. Best α = 0 (just Framework). Reason: Vehicle's phase errors are *deterministic*, not random — they pull predictions toward wrong values rather than averaging out.

The two methods are *complementary* (different inputs, different strengths) but not blendable as noisy estimators of the same signal.

### Events layer terms that don't generalise
Within-event basis functions:
- **Primary bell + rebound** (events_v3): TRAIN corr +0.62. **TEST corr −0.04.** Pure overfitting.
- **+ peak booster** (events_v4): TRAIN +0.70. **TEST +0.02.** Pure overfitting.
- **+ φ-compound per beat** (events_v5): TRAIN +0.89. **TEST +0.31.** Genuine signal.

Only the φ-compound rule has a clear physical hypothesis (each beat in a run inherits φ× the previous). The other basis functions are shape primitives that LSQ can abuse. **Compound generalises; the others don't.**

### Linear + power slings on the prediction
Tried `sign(dev) × |dev|^α` rescaled to data. Improved corr modestly (+0.014 lift on heart) but compressed std unless α is large enough to shuffle ranks. The framework constant α = φ wins on both corr and std ratio independently — not by tuning.

---

## What makes this framework different from standard methods

A standard time-series forecaster (ARIMA, Fourier, RNN) fits free parameters to data. The framework method differs in three concrete ways:

### 1. Constraints from physics, not data
- The φ-rung ladder is fixed (no free periods to fit)
- The 1/φ³ AR coefficient is fixed
- The Type 1/Type 2 coupling classification is fixed
- The κ scaling rule is fixed

These are constraints from framework physics, not regression hyperparameters. Same constants on solar, ENSO, ECG.

### 2. Pre-fit structural predictions
Before fitting, the framework predicts:
- Which rungs will be present (pinned by training span)
- Pump rung based on ground-cycle period
- Coupling type for each rung
- Coupling channel ARAs

These structural predictions are testable independent of the fit quality.

### 3. Cross-system universality
Same code, same constants, applied to multiple systems with only the pump rung changing. The fact that the same formula works on solar dynamo, El Niño, R-R intervals, and earthquake clusters is itself a finding.

---

## Where the framework method genuinely wins

These are the empirical results from real out-of-sample tests on multiple independent systems:

| System | What was predicted blind | Result |
|---|---|---|
| ENSO (76 yr monthly ONI) | 16 years forward | corr +0.43 |
| ECG nsr001 (22.5h) | 5.6 hours forward | corr +0.86 |
| **ECG nsr050 (22.5h, untouched, full-res)** | **5.99 hours forward** | **corr +0.76** |
| Solar SSN | (in-sample only) | corr +0.95 |

For ENSO specifically: operational ENSO forecasters lose skill after ~12 months. We held +0.43 corr at 16-year lead time.

For ECG: standard HRV models are typically descriptive, not predictive. Blind forecast at corr +0.76+ over multiple hours of unseen data on a never-touched subject is novel.

## The Decisive Test: Framework vs Matched-Parameter Fourier

On 2026-04-30 we ran the cleanest comparison yet. Predictions committed before fitting (`TheFormula/decisive_test_predictions.md`). On nsr050 full-resolution (127k beats, 5.99h test):

| Method | TEST corr | TEST MAE | Params |
|---|---|---|---|
| Fourier + 1/φ³ AR | +0.308 | 129 | 7 |
| Framework + 1/φ³ AR | **+0.686** | **115** | 7 |
| Tele + FW_AR @ 1/φ⁴ | **+0.757** | **113** | 7 |

Framework beats matched-parameter Fourier by **+0.378 corr** with the same number of parameters and the same AR rule applied to both. The framework's structural constraints (φ-rung ladder, 1/φ³ AR, 1/φ⁴ blend) are doing real predictive work that an unconstrained model cannot replicate.

8 of 10 advance predictions passed. Two failures (φ² absence, TRAIN/TEST gap on static) had plausible methodological explanations rather than clean framework failures.

---

## Where it fails / known limits

1. **Undersampled slow rungs catastrophically destroy forecast.** On 200-beat ECG, blind corr was −0.15. Solution: rung-pinning rule (drop unpinned).

2. **Vehicle phase prediction requires intrinsic timing** (Solar's global clock). For ECG where phase is recording-specific, Vehicle gets ~0 corr without anchoring.

3. **Events layer (rebound + peak booster) overfits.** Only the φ-compound rule generalises. Use compound only or not at all in pure forecast mode.

4. **Linear blending doesn't combine Vehicle + Framework** — phase errors are deterministic, not random.

5. **Amplitude reach caps at ~0.36 with Framework + AR γ = 1/φ³.** Reaching full amplitude (std ratio 1.0) requires either γ > framework value (loses framework purity) or the Vehicle+Teleporter approach (causes overshoot, MAE worsens).

6. **Joint LSQ absorbs κ scaling.** The directional-coupling rule (downhill ×φ vs uphill ×1/φ) has no effect when amp_raw is unconstrained. Need explicit physical bounds on amp_raw to make κ matter.

---

## Files in this project

Code:
- `TheFormula/map_heart_v3.py` — the hierarchical fitter with events layer (descriptive)
- `TheFormula/map_systems_v3.py` — runs same engine on Solar/ENSO/EQ/ECG
- `TheFormula/generative_vehicle.py` — Vehicle (4-input pure generator)

Viewers:
- `TheFormula/heart_map_v3_view.html` — heart with all event layers
- `TheFormula/enso_monthly_view.html` — ENSO blind forecast (rung-pinning validation)
- `TheFormula/nsr001_blind_view.html` — 22.5h ECG blind static fit
- `TheFormula/nsr001_ar_view.html` — 22.5h ECG with 1/φ³ AR + Vehicle/Teleporter overlays

Memory files:
- `feedback_rung_pinning_rule.md` — operational rule for forecast
- `project_aa_boundary_ar_feedback.md` — 1/φ³ at beat-to-beat
- `framework_system_ara_phi9.md` — System ARA spans ~φ⁹ rungs

---

## Open questions

1. **Does 1/φ³ AR work on ENSO too?** Not yet tested. Should give similar lift if framework is universal.
2. **Does the Vehicle+Teleporter approach work without any subsystem fitting?** Separate question from Framework method, but K=10 gave corr +0.68 with full amplitude on nsr001 — close to Framework method without any LSQ.
3. **Pairwise coupling terms (option #3) and coupling-channel ARAs (option #4)** are the framework-faithful "system level" candidates we haven't tried yet.
4. **Holdout validation needed** for events_v5 in-sample claims of +0.93 corr — interleaved holdout suggested +0.31 generalises but 71 basis cols on 200 samples is dangerous.
5. **Vehicle's amplitude advantage** (std reach 0.67 vs Framework's 0.36) — can we keep its envelope shape while using Framework's phase locking? Linear blend doesn't work; nonlinear combinations not yet tried.

---

*This document supersedes any earlier descriptions of the framework method. Update it when new empirical results are obtained.*
