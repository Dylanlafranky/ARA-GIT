# ARA Test Kit — local run, 2026-07-02

Wired to real workspace data via `run_local_kit.py`; raw log in `KIT_RESULTS_local.txt`.
Systems: solar sunspots (SILSO), ENSO Niño-3.4, PDO = engines (A); QBO, pendulum
arm2/arm3 = forced/clock/substrate (B); white-noise control (bath, test 7 only).
**All generic-extractor runs.** The kit README says authoritative duty/band results
need the canonical `ara_mapper.py`; treat the below as a first pass, not a verdict.

## Per-test outcome (honest)

**Test 1 — duty table.** Column B (dead/clock) peaks at **0.496 ≈ 0.5** with no golden
peak — exactly as pre-registered for the forced column. Column A (engines) peaked at
**0.413**, closest to 2/5 = 0.400, with **no constant inside the CI** and n=3 (far too
few). So the decisive 0.382 engine-peak is **not shown here** — but the run is
underpowered *and* uses the generic extractor (biased toward 0.5). Verdict: **Column B
confirms; Column A inconclusive/underpowered — needs canonical mapper + many more engines.**

**Test 2 — lag shape.** Solar and ENSO floors fall **log-linear (e-null)** — no
return-path bend on the raw signal; PDO floors too short to fit (CI = nan). Verdict:
**no bend detected as run.** Caveat: this was raw-signal autocorrelation, not the
envelope; the solar flywheel signature lives in the envelope — rerun with USE_ENVELOPE.

**Test 3 — modal angle.** Signed horse = **17°** (pre-registered from README). Data read
**~0°** across the board (engine median 0.0°). So the signed 17° horse **fails**; the
rival "circle-fight ~0–1°" matches. BUT floors are degenerate/non-monotone on these
noisy series, so the angle estimator is unreliable here. Verdict: **17° not supported;
~0° matched but weakly measured — needs clean single-mode series or envelope fit.**
(Also: I set the horse from the README; you may want to re-sign it yourself.)

**Test 7 — FDT line.** Spearman(shed, bath) = **+0.11, p = 0.81, n = 7** — positive but
not significant. Endpoints behave (noise = loud/all-bath 1.02; pendulum = quiet 0.00),
but the middle scatters and the `shed` measure degenerates on low-autocorr series
(ENSO floor1 ≈ 0). Verdict: **line not supported as run;** endpoints consistent, needs
cleaner shed estimator + more systems.

**Bridge — phase-step.** Only ENSO resolved two bands (step **174.5° ≈ anti-phase 180°**,
not golden 137.5°); solar/QBO/PDO failed the generic two-band split ("too few slow
cycles"). Verdict: **no golden step seen; band split is the live issue** — needs the
canonical decomposition.

**Test 8 — cascade.** With placeholder hysteresis, **equal-log ≥ golden at every stage
count** (e.g. n=3: 0.892 vs 0.889), gap widening with n. Golden spacing **does not win**.
Verdict: **equal-log/octave family wins as parameterised — but placeholder params;**
needs sourced ln(Pa/Pd) before it means anything.

## Bottom line

As run on real data with the *generic* instruments, the kit is **mostly null/inconclusive
for the φ predictions**, with one clean pre-registered hit: **the forced column sits at
0.5 (no golden duty), as predicted.** Falsification is a first-class outcome here (the
kit's own words), but most of these nulls are **measurement-limited** (generic extractor
bias, degenerate floors, failed band splits, n=3) rather than clean falsifications.

**To make any of these authoritative:** (1) swap in canonical `ara_mapper.py` for duty
and band-split; (2) add many more engines to Column A; (3) rerun test 2/3 on the
envelope / clean single-mode series; (4) you re-sign the test-3 horse; (5) source real
hysteresis for test 8. Until then: Column-B-at-0.5 is the only result to lean on.
