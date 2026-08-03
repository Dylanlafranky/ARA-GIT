# TheFormula — index of prediction-model threads

This folder holds the ARA framework's prediction-model experiments, organized into **23 numbered
thread subfolders**, one per method/logic family, in roughly chronological order. Each subfolder has
its own `README.md` (model logic, systems, what was tested, key results, what wasn't tested, key files).
The date in each folder name is the **last script method modified within that folder** (DD-MM-YY).

**Two caveats on the dates and paths:**
- A large early batch (~220 files, threads 01–03) all carry the same **09–10 May modified-date** from a
  bulk copy that reset timestamps, so their folder dates are not a reliable record of when that work was
  really done — only that nothing in them was touched after. Threads from mid-May onward have genuine
  progressive dates.
- Scripts were moved out of the flat root into subfolders. Many read their data from `Claude4.8/` (e.g.
  `nino34_long_anom.csv`, `SN_m_tot.csv`) via **relative paths** — if you re-run a script from inside its
  new subfolder, you may need to fix the path to the data. The data folders `Claude4.8/` and `__pycache__/`
  were left where they were.

## The threads

| # | Thread | Last | Headline |
|---|---|---|---|
| 01 | Compass & Vehicle predictors | 20-05 | Predictor-as-rolling-vehicle / direction-only "compass"; direction reliable (~76–82%), amplitude is the open-system noise problem → many blend/gate variants. |
| 02 | Cross-system ENSO forecasting & Formula v4 | 20-05 | "Formula v4" = shape (ARA-geometry) × energy (log-amplitude slider); cross-system transfer (heart/ECG → ENSO); moved to strict-causal, direction-first scoring. |
| 03 | System mapping & topology navigators | 10-05 | Inverse (extract k, θ, ARA, amp per φ-rung) + forward navigators mapping ENSO/ECG/solar/EQ onto a shared ARA coordinate map. Diagnostic, not benchmarked. |
| 04 | Cross-system shape-matching atlas | 15-05 | Cross-system cycle-shape matches scored by Fourier distance vs null panels (guards the sine-null that collapsed lung↔forest). Houses canonical `ara_mapper.py`. |
| 05 | Gear & Universal Cascade | 20-05 | Coupled rungs as meshed gears → system-agnostic `UniversalCascade` (φ²/2φ coupling, 1/φ³ feedback) tested on ENSO+ECG with no per-system tuning. |
| 06 | ARA shape-kernel & geometry-transport | 21-05 | Replace cosine with a learned accumulate/release **shape kernel**; transport geometry-state forward. Establishes the leak-guarded benchmark harness reused by 07–10. |
| 07 | Triangle-balance, causal-flow & phi-distance friction | 22-05 | System-neutral triad feature engine; make inferred flow `alpha` predictable; friction = \|ARA − φ\| (flow peaks at φ). All causal. |
| 08 | Tick-engine & ENSO-12m nasal geometry-state | 23-05 | Constrained one-tick state-advance engine (phase_flow = ARA/(ARA+friction)); ENSO-12mo geometry-state predictor; nasal-cycle→ENSO vertical-transfer test. |
| 09 | Phase-flow, analog-flow & lag-hybrid predictors | 24-05 | **Best-documented.** Lag ridge wins MAE every horizon (12mo MAE 0.623); ARA phase-flow carries shape/timing (wins *correlation* at 24mo +0.347 vs +0.167) but not MAE → ARA's value is risk/turn warning, not point prediction. |
| 10 | Morphed-sphere terrain, watershed & layered-sand | 26-05 | ARA-state as sphere/eroding-terrain position; forecast by analog-matching old terrain paths (no decoder). Terrain analog beats persistence (12mo corr +0.275 vs +0.003); fixed "layered-sand" formula under-rolls amplitude (0.05–0.20× — the open problem). |
| 11 | ECG topology, hybrid-CTR & pressure-accumulator | 28-05 | Self-consistency audits of the ECG/heart ARA topology + hybrid CTR predictor + pressure-accumulator. Diagnostic stage; heart synthesis lands in 12. |
| 12 | Heart ceiling, two-band ECG & solar flywheel | 29-05 | Universal two-band/octave/φ-handover engine across heart+ENSO+solar. "Same engine, different battery": ENSO stores (flywheel, forecastable), heart spends (pump, no clock). |
| 13 | Five-axis neighbourhood & standard-baseline benchmark | 13-06 | The **honest benchmark**: ARA beat strong local baselines on only 6/34 horizons. Concentration meta-rule: ARA wins where energy is spread (ENSO +0.071), ties on concentrated clocks (QBO/solar). |
| 14 | ENSO energy-pipe & sphere-wells | 05-06 | Energy-channel characterisation: pipe headroom φ/2=0.809 never filled; overflow toward the 2.0 singularity; sphere-position residence law. Many feeder/driver-above mechanisms NULL. |
| 15 | Energy-geometry unified forecaster | 06-06 | "Energy and geometry are one measurement." Energy calls direction short (0.75@3mo), geometry takes over long, hand off in time. 2−ARA energy rule beats linear 5/6 horizons. |
| 16 | ENSO forecast-of-record & magnitude-from-reservoir | 08-06 | Timestamped/hashed pre-outcome ENSO forecast (warming to weak El Niño ~+0.4–0.45 °C late 2026, direction). Magnitude partly predictable from reservoir-at-crossing (+0.34–0.40 OOS). |
| 17 | River-landscape & thalweg regime map | 09-06 | "The wave IS the topography." Conserved φ-thalweg validated (calm fast lane, advantage grows with energy); terrain position predicts regime. NULL as a value predictor. |
| 18 | Recoil, phi-rung pump & singularity-flip stack | 11-06 | φ-rung pump + recoil-spring + φ-turn stack: ENSO h=12 to +0.394, real win is the **amplitude fix** (1.46→1.00). Recoil = restoring spring ≈1/φ. Turning-point fixes NULL (only external WWV leads). |
| 19 | Frozen-sphere mold-then-roll | 14-06 | **Honest negative.** Leak-free vehicle, but on VALUE it rides the feeder, not the geometry — plain linear recharge regression matches the nested sphere; φ-handover near-inert. Edge is direction + confidence. |
| 20 | Shaped-circle octave, golden-tree walk & orbit-clock | 21-06 | ARA-shape helps asymmetric ENSO (+0.08–0.10 over Fourier); size-weight hurts. Golden-tree walk validated as a *map*, NULL as a predictor. ENSO's stable clock = the annual orbit (Dec peaks, p~1e-5). |
| 21 | Double-helix relation & closure-defect predictor | 11-07 | First hash-locked test of the new two-strand math. Formal FAIL: 0/6 matched wins on nsr047 but 5/6 on nsr053; relation channel helps replication long-horizon MAE, does not generalize, and raw AR remains stronger. |
| 22 | Reciprocal/log Di-ARA ENSO handover | 03-08 | **Architecture-invalid as an ARA test.** The imposed `T+iR` encoding failed the 6-month point-value gate (skill 0.411 vs raw movement 0.431), but same-rung perpendicularity and the ENSO identity were never established. Implementation negative only; framework question untested. |
| 23 | Di-ARA traversal direction predictor | 03-08 | **Architecture-invalid as an ARA test.** This inherited T336's imposed geometry (0.735 vs raw movement 0.744 balanced accuracy). Implementation negative only; no ARA handover inference. |

## The throughline

Read in order, the threads trace one honest arc: many model metaphors (vehicle → cascade → shape-kernel →
sphere/terrain → frozen-sphere → shaped-circle), repeatedly bumping the **same value-ceiling** — geometry
built from a signal's own past **ties** AR/Fourier/persistence on point-value but does not beat them. What
*does* survive every honest re-test is the **direction + confidence + turn-warning** edge, and the
**concentration meta-rule** (ARA helps only where energy is spread, e.g. ENSO; ties on concentrated clocks
like QBO/solar). The strongest positive forecasting results are the terrain-analog (thread 10) and the
amplitude-fix recoil/pump stack (thread 18); the most important negative results are the standard-baseline
benchmark (13) and the frozen-sphere value-ceiling (19).
