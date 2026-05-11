# Claims Status

**Public-release note, May 2026**

This repository is an open research notebook, not a finished proof. I am releasing it because the framework produced enough signal to deserve outside review, and because the failures and corrections are part of the value of the work.

The safest way to read any claim here is:

1. Check the saved data artifact or script output.
2. Ask whether the result is descriptive, tracking, or true forecasting.
3. Compare against simple baselines such as persistence, Fourier/AR models, parameter count, or a non-phi log ladder.
4. Treat the larger "geometry of time" interpretation as a hypothesis, not as established fact.

## Strongest Current Claims

These are the claims I think are most worth outside replication.

| Claim | Current Status | Why it is worth checking |
|---|---|---|
| Phi-rung decomposition can extract useful topology from oscillating time series | Supported but not independently replicated | The same small predictor family shows signal on ENSO and ECG saved outputs. Some headline numbers need cleanup, but the signal is not obviously empty. |
| ENSO has matched-rung anti-phase structure with SOI/Walker circulation | Supported as structural mapping | Dynamic per-rung outputs show strong anti-phase correlations across several rungs. This is closer to a domain-structure claim than a point-forecast claim. |
| **Cross-species topology+energy decomposition reduces practical prediction error** | **Supported on one mouse↔human pair (2026-05-12)** | The framework's "topology from species A × energy from species B" architecture gave a 58% MAE reduction on mouse→human RR-interval prediction vs naive cross-species transfer (34.29 ms vs 82.22 ms). Correlation stayed at chance level for both — see caveat below. |
| ECG mid-horizon dips may mark an unmodeled physiological wave | Provisional | Multi-subject data show heterogeneous but recurring dip structure. Needs better physiology review and clean cross-subject rerun. |
| LLM closure metrics correlate with Pythia benchmark capability | Preliminary | n=4 is too small, but the internal-activation metric rank-orders 5 of 6 benchmark sets. Needs larger Pythia sweep and parameter-count controls. |
| Phi may be doing real work as a non-locking log-scale basis | Hypothesis with partial support | The mathematical motivation is coherent, but the repo should include direct phi-vs-nearby-log-base ablations next to public headlines. |

### Caveat on the decomposition claim

The 58% MAE win is real and reproducible, but the correlation is at chance level. Both methods are linear rescalings of the same mouse-derived shape, so they cannot differ on correlation — the framework's contribution lives entirely in **magnitude calibration**, not in **position tracking**. This is consistent with the framework's own "vertical-ARA partners share map not position" rule. Standard ML evaluation (R², Pearson) would miss this signal entirely; MAE is the metric that surfaces it. See `MASTER_PREDICTION_LEDGER.md` (2026-05-12 entry) and `framework_energy_cascade_architecture.md` for the full test.

## Claims To Soften Or Recheck Before Quoting

These claims should not be used as strong public headlines until rerun cleanly.

| Claim | Current Issue | Safer Wording |
|---|---|---|
| "ENSO corr +0.93 and MAE 0.27 prove forecast skill" | Saved output supports about corr +0.90 and MAE about 0.28, but persistence skill is negative in the saved h=1 artifact. | "The canonical predictor shows short-lead ENSO signal, but needs stronger baseline comparison." |
| "ECG 1-beat corr +0.99 and MAE 19 ms" | Saved canonical artifact I reviewed showed h=1 lower than this; h=3 looked stronger. | "Single-subject ECG results show useful signal, with best saved short-horizon correlation near +0.96." |
| "76 of 77 systems sit in the 3/4 ceiling band" | A saved raw 77-system artifact shows many values outside [0.25, 1.75]. The refined subset may be different, but the simple headline is not safe. | "A refined ARA-band hypothesis remains interesting, but the catalogue needs cleaning and explicit inclusion rules." |
| "Cross-mammal mean +0.955 proves universal local-cycle shape" | Some comparisons appear inflated by normalization/endpoints, especially mouse/human scaling. | "Some mammal cycle-shape comparisons are high; the result needs a normalization-robust rerun." |
| "LLM closure perfectly predicts capability" | n=4, WinoGrande is weaker, and parameter count is a major confound. | "Preliminary closure metric rank-orders several Pythia benchmark scores; needs scale controls." |
| "Same formula works on every domain" | Some scripts fail, some outputs are exploratory, and several claims are trackers rather than blind generators. | "The same framework is being tested across domains, with mixed but interesting results." |

## Speculative Interpretation

The phrase "geometry of time" belongs here. It is the interpretation that motivates the work, not the current level of proof.

Defensible public wording:

> I interpret these results as possible evidence that phi describes a privileged geometry for packaging change across time. This remains an open hypothesis.

Avoid as a headline:

> This proves the universe runs on phi.

## What Would Falsify The Framework?

The framework becomes much less plausible if:

- A clean phi-vs-nearby-log-bases sweep shows phi is ordinary or worse. **(First-pass test run, see below.)**
- A preregistered `home_k` rule removes the predictive signal.
- Persistence/AR/Fourier baselines beat the canonical predictor across most tested systems. **(They currently do on ENSO at h=1; see below.)**
- The LLM closure metric adds nothing beyond parameter count and layer count on a larger model series.
- The ARA catalogue no longer clusters meaningfully after independent duration sourcing and fixed inclusion rules.

## Update — May 10 2026: φ-vs-bases predictor ablation on ENSO

A first-pass version of the φ-vs-bases ablation has been run; see [`PHI_BASE_ABLATION.md`](PHI_BASE_ABLATION.md) for the full result and caveats.

Short version: at horizons 1, 3, and 6 months, **φ has the lowest MAE among the eight tested bases (`{sqrt(2), 1.5, 1.6, φ, 1.7, e, φ^1.05, 2.0}`)**. At h=12 months, base 2.0 narrowly beats φ. The differences between the top three bases are 0.001–0.014 MAE — within the standard error at n=60 anchors. **All bases including φ underperform persistence at every horizon**, so the right reading is "among predictors that don't beat persistence, φ is the best one at short horizons." That supports the framework's structural claim weakly and undercuts it strongly: φ being *the* best base does not establish that φ is *uniquely* required, especially when the whole predictor family is below the persistence baseline.

That is the spirit I want this repository to invite: not belief, not dismissal, but clear tests.
