# TheFormula Main-Thread Results Audit

**Date:** 2026-07-11  
**Scope:** The 20 numbered method threads in `TheFormula/`, checked against their READMEs, detailed result reports, saved JSON/JS score files, `CLAIMS_STATUS.md`, and the master prediction ledger.

## How to read this audit

The numbered folders are not 20 independent replications of one frozen model. They are related development threads, often using the same ENSO or ECG periods while the model was being changed. “Strict-causal” means that a forecast origin does not read future samples, but repeated development against the same held-out period can still tune ideas to that period.

Results are therefore separated into:

- **Predictive:** held-out point, direction, amplitude, or transition prediction.
- **Structural/diagnostic:** a measurable relation or useful state map, but not an exact forecast.
- **Provisional:** interesting result that needs an untouched replication or stronger baseline.
- **Null/negative:** the proposed mechanism failed or a simpler control explained the gain.

The 30 May correction also applies throughout: the vertical rung spacing is **octave/log-2**, while phi remains a proposed handover/coupling landmark. Earlier “phi-rung spacing” language is superseded.

## Thread-by-thread results

| # | Thread | Best result actually present | Honest status |
|---:|---|---|---|
| 01 | Compass & Vehicle | Direction accuracy reaches **82.9% at 6 months**, but value correlation is only **+0.174**. Other tested horizons are mostly about 73–76% direction. | Promising direction clue on a small reused ENSO window; amplitude/value remained weak. |
| 02 | Cross-system ENSO / Formula v4 | Historical ECG calculation: ARA+AR **+0.686 corr, 115 ms MAE** versus matched Fourier+AR **+0.308, 129 ms**. | Exact reproduction succeeded, but this was online one-beat prediction, not a six-hour cold forecast. A frozen four-subject replication produced an ARA win on both Fourier metrics in only 1/4 records; persistence beat both methods throughout. |
| 03 | System Mapping & Navigators | Extracts `(k, phase, ARA, amplitude)` and places subsystem relations on a shared map. | Diagnostic only; no benchmarked forward forecast. Sparse earthquake mapping is unreliable. |
| 04 | Shape-Matching Atlas | ECG–ENSO ranks **3/10** against null shapes with gross corr **+0.081**; lightning–neuron ranks 5th. Lung–forest’s +0.985 loses to a +0.995 sine null. | Important negative: high normalized-shape correlation is often generic periodicity. |
| 05 | Gear & Universal Cascade | Leak-free honest champion at ENSO h=12: **+0.532 corr, 0.675 MAE**, versus structural baseline **+0.370/0.728** and persistence **−0.082/0.928**. | Real exploratory improvement, but chosen after many variants on the same window. Needs untouched replication. |
| 06 | Shape Kernel & Geometry Transport | Geometry-only h=24 improves MAE from persistence **1.174 to 0.715**, but lag ridge reaches **0.632**. Solar h=6 gives the only small harness win over AR: **24.99 vs 25.99 MAE**. | Geometry contains signal, but direct value transport loses to causal memory. |
| 07 | Triangle Balance / Flow / Friction | No point-forecast win. Literal `friction = abs(ARA - phi)` over-advances the state. A gear-minus-sync difference near **0.045** recurs diagnostically. | Useful rejection/refinement. Phi-distance may modulate friction but is not the whole law. |
| 08 | Tick Engine / Nasal Transfer | Nasal dominance–ENSO coupled geometry: **+0.992 held-out, rank 1/9**. The 12-month nasal/ARA prior gets MAE **0.739 vs persistence 0.946**, corr **+0.201**. Formula tick’s cleanest point win is Solar h=24: **+0.776 corr/35.08 MAE** versus lag **+0.523/43.32**. | Strong relation-class result; partial transition prior. Exact cross-system value prediction remains unsolved. |
| 09 | Phase / Analog / Lag-Hybrid Flow | ENSO h=24 phase-only corr **+0.347** versus lag **+0.167**, but MAE loses **0.762 vs 0.617**. Phase/lag disagreement identifies risk; event-risk AUC reaches **0.757**. | Strong phase/risk information, not superior point value. Free hybrids and gates generally hurt. |
| 10 | Morphed Sphere / Terrain / LayeredSand | Terrain analog: **0.602 MAE, +0.275 corr, 0.769 turn accuracy**, versus persistence **0.896, +0.003**. | Good strict-causal persistence win without a decoder, but not tested there against a strong lag/AR control. Later frozen work removes the unique value claim. |
| 11 | ECG Topology / CTR / Accumulator | Filtered CTR over h=6/12/24: **0.629 MAE, +0.144 corr, 74.2% direction**, versus persistence **0.876, −0.047**. Adding topology worsens it: hybrid **0.749 MAE, −0.033 corr**. ECG topology beats persistence **0/54 subjects**. | CTR contains some signal; the topology forecast itself is a clear negative. |
| 12 | Heart Ceiling / Two-Band / Solar Flywheel | Solar self-forecast: **+0.853 vs cycle-ago +0.685** at 1 year and **+0.752 vs +0.687** at 8 years; it meets the cycle-ago floor near 11 years. | Strong raw forecast on one stable clock, about 25 cycles. ARA-specific value is the sub-cycle gain over cycle-ago. |
| 13 | Five-Axis / Standard Baseline | The one `home_plus_ara` stack wins **6/34 corr** and **8/34 MAE** comparisons. Best clean local lift is ENSO h=12, about **+0.071 corr**. | Narrow benchmark of one operator, not all TheFormula. Concentration rule is suggestive but based on ENSO/QBO/Solar. |
| 14 | ENSO Energy Pipe / G3 | G3-A reaches ENSO h=6 **+0.573 vs baseline +0.499** and h=12 **+0.319 vs +0.168**. | Large-looking mid-horizon lift, but it does not replicate on the shorter WWV-era window. Long-lead direction comes from forward phase; the proposed crossing-pump mechanism adds nothing. |
| 15 | Energy–Geometry Unified | `2 - ARA_energy` beats base/linear at 5/6 horizons: h=6 **0.555 vs 0.542**, h=9 **0.316 vs 0.309**, while linear falls to 0.297. | Small, near-noise transformation result. The original 0.75 direction headline was later demoted after leak/strawman checks; honest reservoir direction is about 0.59–0.71 and worse than the full formula. |
| 16 | Forecast of Record / Magnitude | Shape×magnitude at a true 6-month lead: **+0.506 corr vs persistence +0.410**; change corr **+0.458**, direction **0.629**, MAE **0.615 vs 0.653**. Reservoir-at-crossing predicts next warm-peak magnitude about **+0.34–0.40 OOS** across 64 onsets. | One of the better strict-causal ENSO results. Single domain. The issued late-2026 forecast is pending, not a completed result. |
| 17 | River Landscape / Phi-Thalweg | In high-energy ENSO states, phi-lane error is **0.69 vs middle 1.00**, a **31% reduction**, with the advantage growing with energy at h=9–18. | Strong confidence/regime diagnostic on ENSO, not a point-value predictor. Sunspots are null. |
| 18 | Recoil / Pump / Singularity Flip | Final h=12 stack improves **+0.278 to +0.394** and amplitude ratio **1.46 to 1.00**. The safer fixed-recoil step gives **+0.340 to +0.354**; fitted recoil reaches +0.374. | Useful amplitude engineering, but final delay/turn constants were partly selected on the test window. Phi-turn is non-unique because it also matches the engine half-cycle. |
| 19 | Frozen Sphere | Driver-fed sphere reaches **+0.39/+0.32** at h=12/24 versus AR **+0.10/+0.13**, but plain linear recharge gives **+0.42/+0.28**. Self-contained geometry loses to AR everywhere. | Clean important negative: the feeder carries the value skill; the geometry does not uniquely improve it. |
| 20 | Shaped Circle / Golden Tree / Orbit Clock | On ENSO, asymmetric shape beats cosine by **+0.07/+0.10/+0.08** at h=6/12/18; h=12 is **+0.184 vs +0.083**. Frozen solar shape gives **+0.313 vs cosine +0.270** across about 100 years. | Real shape increment against a restricted cosine/Fourier control, not yet against AR/lag-harmonic. ARA size-weighting and golden-tree prediction are null. |

## Strongest results by category

### Strongest raw forecast

Thread 12’s solar self-forecast inside one solar cycle. It beats both persistence and the cycle-ago clock, although the Sun’s regularity—not ARA alone—supplies much of the predictability.

### Resolved historical ARA-versus-Fourier result

Thread 02’s cardiac comparison, +0.686 versus +0.308, was reproduced exactly on `nsr050`. The original code used every true test beat to update the next prediction, so it was causal online prediction rather than the reported 5.99-hour cold forecast. On the frozen `nsr051`–`nsr054` replication set, ARA beat Fourier on both metrics in 1/4 records. The mean ARA-minus-Fourier difference was -0.142 correlation and +11.4 ms MAE, favouring Fourier. One-step persistence beat ARA decisively on every record. Full protocol and results: `02 - Cross-system ENSO forecasting & Formula v4 (20-05-26)/POST_LEAK_CARDIAC_REPLICATION_2026-07-11.md`.

### Strongest strict-causal ENSO point result

Thread 16’s shape×reservoir magnitude model: +0.506 versus persistence +0.410, with predicted-change corr +0.458.

### Strongest cross-scale structural result

Thread 08’s paired nasal–ENSO geometry: +0.992 and rank 1/9 against the fixed null family. This supports a shared relation class, not nasal causation of ENSO.

### Strongest specifically geometric increment

Thread 20’s asymmetric shaped circle, adding about +0.08–0.10 correlation over a symmetric cosine on ENSO. It still needs an AR/lag-harmonic comparison and a new asymmetric system.

### Strongest confidence/regime result

Thread 17’s high-energy phi-thalweg, reducing conditional ENSO error by about 31%.

### Most important negative

Thread 19: once a proper linear feeder control is included, frozen sphere geometry does not improve exact value. This locates the current mathematical bottleneck in the coupling/aggregation law rather than in the existence of the local shape.

## Overall conclusion

The strongest surviving contribution is currently:

```text
phase/direction + regime/confidence + amplitude conditioning
```

TheFormula has not yet produced one universal ARA coupling operator that consistently beats AR, lag-harmonic, or appropriate physical feeder models on exact values.

The historical cardiac target listed below has now been completed. Its post-leak result was negative as a general forecasting claim. Any later combined experiment should use the remaining ingredients only after a new protocol is frozen:

1. The completed matched-Fourier cardiac protocol as a documented negative control.
2. The asymmetric shaped-circle term.
3. The phase/anti-phase relational coupling term from the new ARA mathematics.
4. A closure-defect/temporal-handover term for movement into the next cycle.

The equations, features, baselines, target subjects, and failure criteria must be committed before the untouched subject is scored.

## Immediate follow-up: Thread 21 double-helix test

That proposed experiment was subsequently frozen, hash-locked, and run on the same date as Thread 21.

- Primary `nsr047`: **0/6** matched wins; mean ARA-over-circle correlation lift `-0.0006`.
- Replication `nsr053`: **5/6** matched wins; mean lift `+0.0007`; h=48 MAE improved by `11.25 ms`.
- Transition-direction improvement failed the preregistered partial-support threshold on both records.
- The causal prefix audit passed exactly.
- Ordinary AR remained stronger than the raw geometric models.

**Preregistered verdict: FAIL.** The phase/anti-phase relation may carry a subject-dependent long-horizon correction, but the fixed closure-defect and shaped-projection rule does not yet generalize.
