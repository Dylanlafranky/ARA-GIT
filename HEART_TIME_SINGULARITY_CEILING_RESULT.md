# Heart time-singularity ceiling — how far ahead can the heart be forecast, asleep vs awake

**Date:** 2026-05-29
**Status:** Exploratory. Strict-causal, correlation-led. Small-n (2 sleep records, 2 awake records). One line of evidence — needs confirmation.
**Question (Dylan):** ENSO has a findable forecast wall set by its internal clock (QBO). Does the heart have one too, or is there a lot more recoverable? And what is the wall when *awake* vs *asleep* — is the ratio φ?

## Short version

- **The heart has no internal clock, so it has no internal wall.** Its forecast horizon is set by the slowest real driver you can measure (the horizon ladder), not by the heart itself. This is unlike ENSO, which carries its own quasi-deterministic QBO clock and therefore casts a fixed forecast shadow.
- **Asleep:** the sleeping heart stays usefully forecastable out to **~8 minutes**, and the skill is effectively **dead by ~17 minutes** (corr +0.014, indistinguishable from persistence). Adding slower drivers (breath, blood pressure, oxygen, sleep-stage) does **not** push the wall out — the ladder tops out. In calm sleep the slow drivers barely move, so they have nothing to lend.
- **Awake:** the resting-but-awake heart is far less forecastable. Skill is **~2× lower at short range** and **gone by ~3–4 minutes** — it goes slightly negative past 300 beats and never recovers. The awake brain is actively perturbing the heart, so there is much less self-structure to ride.
- **The sleep/awake ratio is NOT a clean φ (1.618).** The most stable single number — short-horizon skill amplitude — is an **octave (×2.0)**: the sleeping heart is one rung more predictable than the awake heart. The wall-distance ratio is noisier (~φ³–φ⁴, i.e. 4–7×) and threshold-sensitive, so we can't pin a clean constant there. **The octave finding is consistent with the framework's own correction: rungs are octave-spaced (×2); φ is the relational handover *through time*, not the rung spacing.**

## Why the heart differs from ENSO

ENSO sits on top of the QBO — a near-periodic stratospheric clock. That internal clock means ENSO's structure dissolves at a fixed multiple of its home period: a real, findable wall (its time-singularity).

The heart's bands are stochastic and broadband — there is no internal metronome. So the heart's forecast horizon is **borrowed** from whatever slow driver is acting on it (the horizon ladder from earlier work: RR self-memory → a few beats; breath → ~3–6 beats; blood pressure → ~20–40 beats; oxygen, *when it swings* → ~1 min). The "wall" is therefore a property of the **driver environment**, not the heart. Sleep is the regime where the slow drivers are calmest, which is exactly why the sleeping heart's wall is the cleanest to read — and why the slow-driver rungs add nothing there.

## Data & method (strict-causal)

- **Sleep:** PhysioNet `slpdb` records **slp59, slp66** — same-subject ECG + blood pressure + respiration + SpO₂ + scored sleep stage, ~3.7–4.0 h each. slp59 ≈ 16,892 beats (SpO₂ span 45 pts), slp66 ≈ 15,769 beats (SpO₂ span 17 pts).
- **Awake:** PhysioNet `fantasia` records **f1y01 (young), f1o01 (old)** — awake supine subjects watching a film, ECG + respiration, ~120 min each. f1y01 ≈ 8,703 beats, f1o01 ≈ 7,128 beats.
- RR per beat from `wfdb.processing.gqrs_detect` (C-based, fast over network), filtered 300–2000 ms. Hours of 250 Hz data loaded in 40-min chunks to stay inside the network timeout.
- Drivers sampled per beat from **backward-only** windows (no peeking ahead).
- Forecast: features `[1, rr[i], rr[i]−rr[i−15]]` plus `(value, slope)` per driver. Train first half / test second half, standardize on train statistics only, `lstsq`. Score = correlation of predicted vs actual RR at horizons 10/30/60/120/300/600/1200 beats. Persistence floor reported alongside.

## Result — sleeping heart (mean of slp59, slp66)

| horizon | time | persist | heart | +breath | +pressure | +oxygen | +sleep-stage |
|---|---|---|---|---|---|---|---|
| 10   | 8s   | +0.418 | +0.449 | +0.461 | +0.450 | +0.446 | +0.452 |
| 30   | 25s  | +0.334 | +0.398 | +0.403 | +0.418 | +0.416 | +0.423 |
| 60   | 50s  | +0.308 | +0.379 | +0.397 | +0.410 | +0.398 | +0.404 |
| 120  | 1.7m | +0.265 | +0.300 | +0.315 | +0.332 | +0.307 | +0.314 |
| 300  | 4m   | +0.193 | +0.212 | +0.223 | +0.213 | +0.194 | +0.197 |
| 600  | 8m   | +0.112 | +0.129 | +0.092 | +0.080 | +0.082 | +0.081 |
| 1200 | 17m  | +0.020 | +0.014 | +0.002 | +0.002 | −0.025 | −0.075 |

Useful skill (heart clearly above persistence) holds through ~4–8 min, then collapses to the persistence floor and to ~0 by 17 min. Breath adds a small positive lift at short/mid horizons; blood pressure helps mid-horizon (consistent with the third-leg result); oxygen and sleep-stage add ~0 or hurt — in calm sleep they barely move.

## Result — awake heart (mean of f1y01, f1o01)

| horizon | time | persist | heart | +breath |
|---|---|---|---|---|
| 10   | 8s   | +0.221 | +0.224 | +0.225 |
| 30   | 22s  | +0.089 | +0.113 | +0.107 |
| 60   | 45s  | +0.061 | +0.079 | +0.079 |
| 120  | 1.5m | +0.068 | +0.101 | +0.102 |
| 300  | 3.8m | +0.007 | −0.062 | −0.047 |
| 600  | 7.5m | −0.005 | −0.029 | −0.019 |
| 1200 | 15m  | −0.029 | +0.047 | +0.037 |

The awake heart starts at roughly half the short-horizon skill of the sleeping heart and crosses into noise by ~3–4 minutes. The flicker at 1200 beats is not recovered structure; it is noise at the limit of a 2-record sample.

## The sleep/awake ratio — is it φ?

Honest answer: **not φ¹.** Two ways to read the ratio:

- **Short-horizon skill amplitude** (the most reliable point, ~8 s): sleep/awake = **2.00 — a clean octave.** At ~25 s and ~50 s the ratio drifts to 3.5–4.8, but those points are already noisier.
- **Wall distance** (where skill crosses a fixed threshold): threshold-sensitive. At a +0.05 crossing, sleep ≈ 14 min vs awake ≈ 2.2 min → ratio ≈ **6.4 (≈ φ⁴)**; at +0.10 the awake curve collapses so early the ratio blows up to ~20. Too unstable to claim a constant.

So the defensible statement is: **the sleeping heart is about one octave (×2) more forecastable than the awake heart at short range, and its wall sits several φ-powers further out.** This is *consistent with the corrected framework*, where rungs are octave-spaced and φ is the relational handover through time — not a contradiction of it. Sleep vs wake is a **relational-state** change (brain steps back; heart runs nearer its own self-sustaining engine), and the front-end signature of that change reads as a rung step (octave), exactly as the two-band ECG work predicted.

## Honest scope / caveats

- n = 2 sleep + 2 awake subjects. Lifts and walls are modest and noisy; this is a single exploratory line, not a confirmation.
- Sleep and awake are different cohorts/datasets (slpdb vs fantasia), different ages — the comparison conflates dataset with state. A cleaner test is the **same subjects measured across a full sleep→wake cycle** (e.g. MMASH 24 h RR + cortisol/melatonin/activity — ideal circadian driver, but distributed as CSV, not WFDB `pn_dir`-accessible, so not run here).
- Strict-causal throughout: train/test split, backward-only driver windows, standardize on train, persistence floor reported. No leakage found.
- The "calm sleep" caveat matters: this is precisely the regime where slow drivers are weakest, so "the ladder tops out" is partly a statement about *this* regime. A high-arousal or apneic night could behave differently.

## Files
- `TheFormula/heart_ceiling_slp_chunk.py` — chunked RR + driver detector for slpdb (40-min chunks)
- `TheFormula/heart_ceiling_slp_merge.py` — merge chunks, attach per-beat sleep stage (causal step-hold), clean SpO₂
- `TheFormula/heart_ceiling_ladder.py` — strict-causal ladder forecast (heart → +breath → +pressure → +oxygen → +sleep-stage)
- `TheFormula/heart_ceiling_awake_chunk.py` — chunked RR detector for fantasia (awake)
- `TheFormula/heart_ceiling_awake_sweep.py` — strict-causal awake horizon sweep (heart, +breath)
- `TheFormula/heart_ceiling_ratio.py` — sleep/awake wall + amplitude ratio vs φ-powers
- `TheFormula/heart_ceiling_ladder_result.json`, `heart_ceiling_awake_result.json` — result data
