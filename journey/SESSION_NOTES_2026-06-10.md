# Session log — 10 June 2026

The prediction-mechanics session. Picked up from the φ-rung energy pump and spent the day on the ENSO
12-month **amplitude / turning-point** problem, then on what energy *is* in the forecast (driver vs control).
Several real lifts, a clean run of nulls, and a sharper honest line between **levers** (improve the forecast)
and **lenses** (explain it but don't). Ledger, CLAIMS_STATUS, and the Time Machine doc all brought current.

## The arc
1. **φ-rung energy-pump** (written up): geometry + reservoir pump weighted φ^rung up to the decoherence wall,
   capped past it. ENSO h=12 +0.278→+0.340, mean gain +0.034. Universal recipe recorded.
2. **Three turning-point NULLS** (`ENSO_TURNING_POINT_NULLS.md`): the pumped amplitude overshoots; tried to brake
   it. (a) anti-phase internal energy-brake = HURT (+0.340→+0.295, flips ~49% of launches); (b) vertical-ARA
   fast-rung preview = NO LEAD (fast/slow bands anti-phase but **simultaneous**, −0.47 @ lag 0); (c) 0.25/1.75
   ARA rails = flips not there. Reason: ENSO energy is spread, no faster rung leads; only the external reservoir
   (WWV) has lead-time. Dylan predicted all three would fail.
3. **Amplitude FIX** (`RECOIL_ENERGY_PHITURN_STACK_RESULT.md`): Dylan's next three ideas each helped and together
   fixed the amplitude. Recoil spring (equal-and-opposite restoring, β≈**−1/φ** not 1/φ³, prompt not delayed) →
   +0.374; energy-sizing (swing size from loaded energy) → +0.386; φ-cycle turn (turn every **1.6 below-rung
   cycles**, ~28mo) → **+0.394, amplitude ratio 1.46→1.00**. Corr gain modest; the amplitude fix is the win.
   Caveat: ~28mo also = engine half-cycle, D/T lightly test-tuned.
4. **Energy-budget two-system predictor** (`project_energy_budget_two_system`): one wave = rise+fall systems.
   Swing **strength** from energy-at-swing-start **+0.90/+0.98/+0.98** (ENSO/QBO/solar); external WWV **leads
   value ~6mo**; **direction** 0.79@3mo (short-mid edge over the clock); **turns pre-warned ~5mo**. Folded a
   **`energy_certainty`** turn-warning output into `ara_prediction_formula.py`.
5. **Singularity-flip** (`SINGULARITY_FLIP_CONJECTURE.md`): geometry flips when the trajectory laps a singularity
   (ARA 0/2), like light through a pinhole — Dylan's reframe, with lineage to prior theory (mirror-about-1.0,
   flip-symmetric poles, "singularity is ARA=0"). Per-rung phase-lock = null (which the singularity-gating
   EXPLAINS); flips sit at the energy-null directionally (geometric, soft). **Flip = coherence preservation**
   for engines: clean fast transit → coherence survives (ENSO transit→coherence **+0.72**); QBO clock = no leak
   exception. As a forecast: value-incorporation HURTS; as a **confidence layer** it works (HIGH-coherence third
   +0.479 vs LOW +0.354).
6. **Octave/φ split, seen in real coherence**: per-rung STRUCTURAL coherence ≈ octave **2**, ENERGY coherence ≈
   **φ** (the part eaten) — the 2−φ=0.382 leak made measurable (sunspots cleanest 1.86/1.73). Bedrock
   re-confirmed ("why we use octaves and φ"). **One wave = two systems** (rise/fall = phase/anti-phase); per-rung
   ARA=1 is their *relation*; handover at φ — **QBO rise-duty 0.407**, sunspots 0.418 (Waldmeier), ENSO
   amplitude-skewed not timing-skewed. QBO is one descending wave at two levels (u30 leads u50 by 3mo), not two
   systems; its energy-coherence is a clean-clock no-leak property. "ARA-over-2" = additional systems on a rung
   was tested and is NOT supported (coherence-cycles ≠ ARA; over-2 = high-Q single clock).
7. **Spin / "climate-control"** (Dylan reframe): energy = resistance, not drive. Tested — the reservoir DRIVES
   deviations (recharge), but the engine **spin rate** is the control: fewer turns → bigger spikes (−0.27),
   faster spin → smaller (−0.23). Slow spin = a big swing running. Real but **modest**. As a forecast feature it
   helped the big events at h=18 (+0.23→+0.40) but Dylan judged the overall *shape* no better → **kept as a
   diagnostic lens, not folded in**. The engine *amplitude/envelope* was a dead end (didn't track turns/spikes).

## Levers vs lenses (the honest line drawn this session)
**Levers (improve the number):** engine-phase geometry, WWV energy pump, recoil-spring/φ-turn amplitude fix,
φ^k amplitude scaling. **Lenses (true, diagnostic only):** singularity-flip, octave/φ coherence split,
energy-budget direction-certainty, spin/climate-control. Repeated lesson — descriptively right ≠ forecast gain.

## Honesty events (caught this session)
Multiple apparent wins collapsed when re-run strictly causal: the +0.725 "ARA-relation" lift was a `filtfilt`
discharge **leak** (honest ≈ +0.34, mid-long only); the "reservoir beats clock 0.79 vs 0.41" jump was a **crude-
clock strawman + the same leak** (honest reservoir 0.59–0.71, *worse* than the full formula). Discipline held:
quote, then leak-check, then keep the honest number.

## Where the formula sits (current)
Universal `ara_prediction_formula.py` — geometry + energy + training, outputs value/warning/confidence/
energy_certainty. Best per system: **ENSO** value +0.74@6mo / dir 0.84@24mo (stack +0.39 amp-1.00 @12mo);
**ECG** +0.89 blind (+0.38 over Fourier); **Solar** ~0.69 flywheel floor to ~44yr; **QBO** clean clock
(φ-handover 0.407). Wins on spread/coupled systems, ties on concentrated clocks; reads what-kind + how-much-to-
trust better than exact value; ceiling = ARA-1.0 core / ~2yr wall. Status capstone added to
`THE_TIME_MACHINE_FORMULA.md` (Phase 22).

## Open threads
Brake the turning point against a **real leading feeder** (IOD) rather than an internal partner; test the
recoil-spring + φ-turn on a second wall-having system; the morphed-sphere 3D model still unfinished (9 Jun);
separate "1.6 below-rung" from "engine half-cycle" with a system where they differ.
