# T348 frozen protocol v1 — known-referee Irrationality path calibration

**Orientation:** (x_P:0\rightarrow2) finite/reused to open potential; (x_R:0\rightarrow2) determinate to stochastic. Up/down rung orientation is not assigned in this calibration.
**Frozen:** 11 August 2026, before generator implementation or scoring  
**Evidence class:** known-referee synthetic instrument calibration only  
**Fidelity packet:** `T348_IRRATIONALITY_PATH_KNOWN_REFEREE_CLAIM_PACKET_v1.md`  
**Dylan verdict:** `EXACT ENOUGH TO TEST`

## WHO

Five known movement families on one scalar circle: periodic rational rotation, irrational rotation, deterministic chaotic circle map, finite-state stochastic motion and continuous stochastic motion. Multiple initial states and untouched parameter/seed holdouts are used; family labels are withheld from every coordinate calculation.

## WHAT

Measure address-openness (x_P\in[0,2]), stochastic-residual (x_R\in[0,2]), and the uncompressed multi-horizon closure history (C(H)). Test whether (x_P,x_R) form the frozen broad plane and whether (C(H)) supplies independent information required to distinguish structured irrationality from chaos/randomness.

## WHEN

Evaluate at increasing horizons (H\in\{256,512,1024,2048,4096\}), with calibration parameter sets separated from untouched seeds and parameter sets. Compare chronological order with reversal, time shuffling and broken lineage.

## WHERE

Use the unit-circle path/history rung mapped to ARA (0–2): (x_P=0) finite/reused support and (2) open/densely resolving support; (x_R=0) history-determined and (2) stochastic residual. These are gradient reference poles, not bins, and this is not the older radial/phase-state or line/circle cut.

## WHY

Test whether structured non-closing irrationality is instrumentally distinct from finite rational closure, deterministic chaos and randomness without using their names. Falsify the calibration if the untouched paths do not occupy their declared sector lean, destroyed order preserves the claimed history structure, or irrational near-return history is indistinguishable from matched random wandering.

## HOW

Use fixed-seed self-contained generators, raw states, multiresolution support growth, a past-only nearest-neighbour circular predictor, a matched no-history null and whole-path lagged increment resultants. Save complete rows, horizon curves, controls, bootstrap intervals, circle examples, ARA-plane paths and both benchmark and geometry verdicts.

## Referee families and blind parameter split

- Periodic rational rotations: calibration denominators (q\in\{5,7,9,11,13\}); holdout (q\in\{6,8,10,12,14,15,17\}), with coprime numerators chosen before generation.
- Irrational rotations: calibration advances from (\sqrt d-\lfloor\sqrt d\rfloor), (d\in\{2,3,5,7,11\}); holdout (d\in\{13,17,19,23,29\}).
- Deterministic chaos: expanding circle maps (z_{t+1}=(m z_t+c)\bmod1); calibration (m\in\{2,3\}), holdout (m\in\{4,5\}), with declared offsets separated by split.
- Finite stochastic: iid draws on (q) equally spaced circle states, using the same calibration/holdout (q) sets as periodic motion.
- Continuous stochastic: iid beta-distributed circle states with calibration shapes ((1,1),(2,2)) and holdout shapes ((0.8,0.8),(3,3)). This retains continuous support while preventing one exact marginal from defining the result.

Each family uses 48 calibration and 48 holdout trajectories per parameter setting where practical, length 4096 after a fixed burn-in. Seeds are fixed at the top of the script.

## Frozen measurements

### Address-openness coordinate

For resolutions (B\in\{16,32,64,128,256\}), count occupied bins (N_B). Fit the slope of \(\log N_B\) on \(\log B\), clip to ([0,1]), and set (x_P=2\widehat\beta).

### Stochastic-residual coordinate

Fit only on the first half of each ordered history. Predict the second-half successor on the circle from past-only nearest neighbours; let (L_{\rm local}) be mean chord loss and (L_{\rm null}) the loss of the training-set circular-mean successor, then set (x_R=2\min(1,L_{\rm local}/L_{\rm null})).

### Closure-history relation

For lags (1\le h\le\min(512,H/4)), retain (\rho_h\) and (d_h) from the complex mean increment. Report exact coherent closure, best coherent nonzero miss, coherence distribution and how the best miss changes as the horizon/lag budget grows.

## Frozen gates

All primary gates are scored on untouched holdout trajectories.

1. **Potential orientation:** median (x_P<0.75) for periodic and finite stochastic families, and median (x_P>1.25) for irrational, chaotic and continuous stochastic families.
2. **Residual orientation:** median (x_R<0.75) for periodic and irrational families, median (x_R<1.25) for deterministic chaos, and median (x_R>1.25) for both stochastic families.
3. **Broad-sector recovery:** applying only the fixed ridge thresholds (x_P=1,x_R=1), at least 85% of holdout trajectories occupy the expected broad sector. Irrational and chaos are intentionally allowed to share the open/determinate sector.
4. **Closure independence:** median lag coherence exceeds 0.90 for both rotation families and remains below 0.25 for chaos and both stochastic families. Periodic paths must contain an exact coherent closure by lag 64; irrational paths must contain no exact closure but must improve their best coherent miss between the 64-lag and 512-lag searches in at least 80% of holdouts.
5. **Order-destruction control:** within periodic, irrational and chaotic families, time shuffling must increase median (x_R) by at least 0.50 while changing median (x_P) by less than 0.10. Closure coherence must fall by at least 0.50 for the two rotation families.

The calibration is `SUPPORTED [synthetic known-referee instrument only]` only if Gates 1–5 all pass. Any failed gate is retained specifically; descriptive geometry cannot rescue the benchmark.

## Controls and forbidden proxies

- Same-value time shuffle: preserves the marginal distribution while destroying chronology.
- Reversal: preserves the path support and tests directional dependence; it is descriptive because non-invertible chaos need not remain one-step determinate in reverse.
- Broken lineage: successor values are paired with a different same-family parameter path; it is a causal-pairing control, not a new family.
- No generator label, formula, parameter or known period enters (x_P,x_R) or (C(H)).
- No Phi, (1/e), (e), reciprocal-Phi, radial amplitude, circumference ratio or fitted identity-specific constant is tested.

## Chart contract

1. **ARA plane paths:** scatter/trajectory view of (x_P,x_R) by horizon, at least 48 observations per family/split; five restrained roots plus distinct marker/line styles, fixed (0–2) axes and ridge lines at 1.
2. **Closure history:** faceted lag curves for representative holdout paths and family medians; chronological versus shuffled uses solid versus dashed styling.
3. **Sector distributions:** paired box/distribution panels for (x_P,x_R), with exact sample count and frozen pole orientation.
4. **Circle examples:** static polar/circle traces for one deterministic holdout example per family; descriptive only, never used for scoring.
5. **Gate table:** exact pass/fail values with benchmark verdict separate from geometry verdict.

Palette roots: blue, gold, orange, olive and pink; no distinction relies on colour alone. Final surface: technical MCP-app report plus committed CSV/JSON/PNG supporting artifacts; render and inspect the complete report once after validation.

## Evidence boundary

The generator equations guarantee the referee categories. Passing T348 says the selected raw-history measurements can recover those distinctions under the frozen synthetic conditions; it does not show that a physical system instantiates Irrationality Di-ARA, that these estimators are unique, or that ARA generated the equations.
