# FableConvo scripts — run index (2026-07-04)

Ran the self-contained / data-available scripts; outputs are the `*_output.txt`
files here (+ `PRIMES_ZETA_FIGURE.png`). Pendulum data staged from the already-
downloaded `.mat` files; stellar catalogs from the earlier `/tmp` downloads.

## Ran OK

- **numbers_as_waves_test** — leading-digit-below-5 fraction: 2^k ladder 0.699,
  Fibonacci 0.698, Benford log10(5)=0.699, uniform-random (bath) 0.448. One
  number cleanly separates ladder from bath, as claimed.
- **digital_rig_L1** — circle-map ground truth: locks land on Fibonacci ratios
  (5/8 MATCH); the 1/phi drive tracks Omega with NO lock (the open handover
  channel). Honest note in output: 5/8 lock folds to 135 deg, only ~2.5 deg from
  the golden 137.5 — a real fold ambiguity flagged by the script itself.
- **golden_stars_corrected** — RR0.61 club is 8.9% leaner (matched Wilcoxon
  p=8.8e-43) = REAL leaner class; but within-club gradient corr(dist-from-1/phi,
  R21) = -0.35 (partial -0.20) runs AGAINST "closer to phi = leaner". Same
  for/against split as before, on the fresh catalogs.
- **primes_zeta_verification** — 100k Riemann zeta zeros: nearest-neighbour
  spacing <0.1 is 0.0008 measured vs 0.0952 Poisson vs ~0.0011 GUE → matches
  GUE level-repulsion (the established Montgomery/Odlyzko fact), not Poisson.
- **test6_dissociation** (free-swing triple) — common-mode 19 vs arm3 8 at >=2s,
  but margins are razor-thin (common-past ~= arm3-past); weak, near-redundant.
- **test6b_driven** (driven triple) — variance collapses to one mode (~0.995);
  everything forecasts everything at ~1.000; common 9 vs arm3 0 but uninformative.
  Present-leader flips to arm1 under cart driving (real, sensible).

- **test5_tumbling_separatrix** (fixed upload; run via 8 batched calls, exact
  registered method — 24×90s ensemble, seed 42, rtol 1e-9, combined + scored).
  CONTROL: single-pendulum periods lengthen toward the separatrix (0.57→1.56s) =
  theorem-exact. Pre-registered predictions SUPPORTED: P1 period-stretch at the
  rotation↔libration crossing +86 ms (p=6.3e-21); P2 dwell-near-top +0.051
  (p=3.3e-32). Exploratory P3 (monotone slowdown / last-cycle-slowest) NOT
  supported (p=0.97). So the separatrix/singularity crossing shows the predicted
  period-stretch and top-dwelling; the exploratory extra does not hold.

## NOT run (with reason)

- (test5_tumbling_separatrix moved to "Ran OK" below — completed via batching.)
- **llm_master_capture**, **llm_whole_run_capture_resumable** — Colab GPU + Google
  Drive harvest jobs; can't run here (no GPU/Drive/Colab).
- **test_llm1_decoupled_substrate** — carries an explicit EXECUTION EMBARGO (no run
  on real activations until non-Anthropic review per LLM_WORK_SAFEGUARDS.md).
- **apply_llm_audit_edits** — a file-MUTATING script (rewrites LLM/*.md), not an
  output-producing analysis; not run without explicit go-ahead.
