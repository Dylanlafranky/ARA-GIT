# T390 — frozen 7.5-spin population release protocol

Date frozen: 2026-08-15 (Australia/Brisbane)

## Question

Is the neutrino-producing muon decay rate unusually concentrated when the frozen population spin child has accumulated exactly 7.5 turns?

## W5H and identity boundary

- **Who / where:** the same 300 K silver positive-muon population and the same 96 ISIS EMU detector histograms used by T382/T383/T389. No medium or source identity changes.
- **What:** detector-summed charged-daughter counts, treated as a population-level timestamp proxy for the decay `mu+ -> e+ + nu_e + anti-nu_mu`. The neutrinos are not directly detected.
- **When:** 0.25 to 10.00 microseconds so that the 63 G 7.5-turn landmark is included. The frozen parent lifetime, child cadence and phase origin come from the already-scored T382 calibration; they are not re-fitted to improve T390.
- **Where in ARA:** the parent is the detector-summed surviving/decaying population envelope. The candidate child landmark is 7.5 accumulated spin turns. T390 asks whether release through the parent is concentrated at that child cadence; it does not assume the answer.
- **Why:** T383 tested cross-field invariance at one shared parent coordinate and rejected it. It did not test the different claim that the population release rate itself changes at each field's own 7.5-turn time.
- **How:** fit only each run's nuisance amplitude and background around the frozen parent lifetime. Form observed/expected release ratios and Pearson residuals. Score a fixed `+/- 1/8`-turn window around the field-specific 7.5-turn time in the untouched 63 G, 160 G and 400 G holdouts.

## Frozen controls and gates

The primary statistic is the pooled observed/expected charged-daughter count ratio in the three 7.5-turn windows.

1. The 7.5-turn pooled ratio must exceed 1.
2. It must be larger than every pooled ratio at the other same-family half-integer landmarks `0.5,1.5,...,8.5` that fall inside the analysis range for all three holdouts.
3. It must exceed the 97.5th percentile of equal-width integer, quarter-turn, three-quarter-turn and field-permutation timing controls.
4. Each holdout field must show a positive local Pearson-residual mean in its own 7.5-turn window.
5. A detector-block bootstrap 95% interval for the pooled excess ratio minus 1 must lie above zero.

All five are required for a primary pass. The exact rank and effect size are retained even if the frozen gate fails.

## Claim boundary

The aggregate histogram can test whether decay events are enriched near a population spin landmark. It cannot show that an individual muon deterministically waits 7.5 turns, cannot identify which neutrino carried which energy, and cannot distinguish a physical spin-timed release from residual detector-acceptance modulation unless the summed-detector and detector-resampling controls also pass.

