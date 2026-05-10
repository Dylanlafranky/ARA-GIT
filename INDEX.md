# ARA Framework — Index

**Last updated: May 2026**

---

## What this is, in one paragraph

This is an open research notebook about a geometric hypothesis for oscillating systems. A heartbeat, a climate cycle, a planetary orbit, the firing of a neuron — the framework asks whether they can be mapped onto a shared φ-spaced ladder of timescales. Each system can be read as a small set of coordinates: period, amplitude, phase, and a build-vs-release ratio (ARA) per rung of the ladder. A single forward formula — anchored at the most recent observed value, integrating contributions across rungs — is being tested as a way to track or forecast behaviour from those coordinates. Existing physics provides the language: bandpass decomposition, coupled oscillators, scaling laws, and time-as-primary. The big interpretation is speculative; the useful question for reviewers is whether the φ-rung coordinate system carries real signal beyond simpler baselines.

I'm not a scientist by training. I built this in spare time, with significant help from AI collaborators. I report what I find — including the misses — and invite people in the relevant fields to check, improve, or knock down what I have wrong.

For the public-release audit, start with [`CLAIMS_STATUS.md`](CLAIMS_STATUS.md) and [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md). They list the claims I would quote carefully and the scripts that still need cleanup. The φ-vs-nearby-bases predictor ablation has now had a first-pass run; see [`PHI_BASE_ABLATION.md`](PHI_BASE_ABLATION.md) — φ wins at h=1, 3, 6 months among the eight tested bases on ENSO, but the whole predictor family underperforms persistence at every horizon, so the test is a partial-evidence result rather than a clean win for φ specifically.

---

## The framework in 30 seconds

**Topology coordinates.** Any oscillating system at any moment can be described as:
- `v_now` — the most recent observed value
- A list of pinned φ-rungs, each with `(period, amplitude, phase, ARA)`
- A `home_k` — the rung where the system naturally lives

**ARA scale (0 to 2).** ARA = build-time / release-time. A position on the space-time spectrum:
- 0 → pure space singularity (point/void, no dynamics)
- ~1.0 → balance point (atomic clocks, pure randomness — both arrive here)
- φ ≈ 1.618 → engine zone (self-sustaining systems)
- 1.75 → operational maximum, energy-donor systems sit here (e.g. solar magnetic cycle)
- 2.0 → pure time singularity (heat death, no structure)

**Three rung relations:**
- *Below* (faster): substrate that maintains the system
- *Same rung* (matched anti-phase pair): coupled exchange (NINO ↔ SOI, atria ↔ ventricles)
- *Above* (slower): energy donor that drives everything below

**Forward predictor.** Two regimes blended by a sigmoid at `h = home_period × φ^(±7/4)`:
- Short lead: anchor at v_now, integrate δ-contributions across rungs
- Long lead: structured wave from training mean, weighted by rung distance from home

The predictor is one Python file: [`ara_framework.py`](ara_framework.py).

---

## Findings by confidence

### Supported So Far / Needs Independent Replication

These are the findings that survived at least one stricter check after an earlier acausal-bandpass leakage was caught and corrected. They should be read as promising saved results, not as independent confirmations.

| Finding | Headline number | Source |
|---|---|---|
| **Canonical predictor: ENSO 1-month forecast** | Saved output: MAE about **0.28 C**, corr about **+0.90**; persistence skill caveat | `TheFormula/canonical_benchmark_data.js` |
| **Canonical predictor: ECG short-horizon forecast** | Saved output shows useful single-subject signal; best h=3 near corr **+0.96**, MAE about **35 ms** | `TheFormula/canonical_benchmark_data.js` |
| **Cross-mammalian local cycle shape match** | Some high pairwise matches; broad mean is sensitive to normalization and should be rerun | `TheFormula/multispecies_vertical_ara_data.js` |
| **ECG ↔ ENSO local profile match** | corr +0.695 across 38 orders of φ in time | (prior work, this repo) |
| **Walker Circulation is fractal across rungs** | SOI mirrors NINO anti-phase from φ⁵ to φ¹¹ with \|corr\| ≥ 0.85 | (memory: dynamic_rung_assignment) |
| **Lag-h corrector ports cross-domain** | γ ≈ +1/φ. 37% MAE drop at 1-min ECG, 17% at 24-month ENSO | (memory: corrector_cross_domain) |
| **Closed-system coupling differs from incidental** | SOI as matched-rung pair lifts ENSO; same SOI as feeder does nothing | (memory: closed_system_validated) |
| **AR feedback constant is 1/φ³** | "One full ARA orbit" of momentum carrying between cycles | (memory: aa_boundary_ar_feedback) |
| **Mid-horizon dip is consistent across 11 humans** | Recurring but heterogeneous dip structure; possible autonomic intruder wave | `TheFormula/multi_subject_dip_data.js` |

### 🟡 Provisional — single test, suggestive numerical match, or coincidence-flagged

| Claim | Status |
|---|---|
| **Predictor crossover at φ^(±7/4) × home period** | Empirical on ENSO + ECG. The 7/4 = 1.75 number recurs in: matter circle radius (11/2π log-decades), solar magnetic cycle ARA (7yr/4yr observation), LF/HF HRV ratio. Multiple independent appearances suggest meaning, but no single principled derivation yet. |
| **1.75 / 0.25 mirror pair as donor ARAs** | 1.75 = time-dominant feeder ARA (matches solar cycle). 0.25 = 2 − 1.75 = predicted space-dominant feeder ARA. Falsifiable but not yet directly tested across both sides. |
| **Cosmic budget Ω_b/Ω_dm/Ω_de from π and φ** | Numerical match within 0.5% of Planck values from two geometric inputs. A two-parameter scheme fitting two independent numbers can do this by construction; needs a physical mechanism to be more than coincidence. |
| **Information³ → cosmic budget mapping** | Datum/Signal/Meaning ↔ Dark Energy / Dark Matter / Baryonic. Ω_dm/Ω_de = 1/φ² is the datum-to-signal coupling. Suggestive structural claim. |
| **Three-circle architecture** (Quantum / Matter / Cosmic) | Discovered by unsupervised clustering across 130+ systems. 50% of systems sit in the triple-overlap (human scale). Real pattern in this catalogue, needs replication on different catalogues. |

### 🔴 Speculative — conceptual, no direct test

| Claim | Note |
|---|---|
| **Light/Dark as nested matched-rung pair inside Space/Time** | "Light is water, Dark is land" — c is the matched-rung exchange rate at the Light/Dark coast. Conceptually clean; no operational test built yet. |
| **(π−3)/π ≈ 4.5% as universal coupling tax** | Geometric origin (Honeycomb conjecture, Hales 1999) is rigorous; the universal-coupling-tax claim is the framework's extension. Found in H₂O bond angle (within 0.03%) but not confirmed elsewhere. |
| **1/α ≈ φ^(10 + 1/φ³)** | Numerical match within 0.5%. The 1/φ³ here is a constant we already validate in the AR feedback, which makes it not pure coincidence. Still pre-mechanism. |
| **7 yr exothermic system driving CO2/Nile/NAO** | Predicted by the network connection field analysis as a missing engine for several half-systems. Not yet identified in real data. |
| **Engine-consumer pairings as a falsifiable lattice** | The framework predicts every consumer (ARA < 1) has a specific engine partner that can be located by topology. Network connection field is the proposed mapping tool; not built. |

---

## Earlier results (historical / lighter validation)

| Finding | Source |
|---|---|
| 21 of 21 advance predictions held up across 37 systems | Historical ledger claim; useful audit trail, but not independent confirmation by itself |
| Three-type classification (clock/engine/snap) at every scale window | Script 42 (143 systems, 7 scale windows) |
| φ as biological health attractor (slope 1.613 vs φ = 1.618) | Script 40 (143 systems) |
| Framework beat matched-parameter Fourier on cardiac data | nsr050 decisive test, Session 2026-04-30 |
| Three framework constants (rung-pinning, 1/φ³ feedback, 1/φ⁴ blend) all near optimal | Session 2026-04-30 (cross-system) |

---

## LLM application — preliminary (May 2026)

The framework's coupling-graph and Information³ closure tools were applied to the Pythia language-model size series (70M, 160M, 410M, 1B, deduped variants). Pythia is open and benchmarked extensively, which makes it a clean test bed for asking whether the framework's metrics correlate with capability.

### 🟢 Closure index predicts Pythia benchmark capability

| Pythia size | closure index (triangles per active component / loose-thread fraction) | LAMBADA acc | ARC-easy | SciQ |
|---|---|---|---|---|
| 70m-deduped | 80 | 0.192 | 0.385 | 0.606 |
| 160m-deduped | 756 | 0.342 | 0.440 | 0.720 |
| 410m-deduped | 877 | 0.524 | 0.517 | 0.826 |
| 1b-deduped | **6,284** | **0.580** | **0.585** | **0.870** |

**Spearman rank correlation = +1.000** on LAMBADA, PIQA, ARC-easy, ARC-challenge, and SciQ in this n=4 run. WinoGrande is weaker at **ρ = +0.800**, so the average across all six is about **+0.967** rather than a universal perfect-rank result. **Pearson r vs log(closure) = +0.886 to +0.997** across the five monotonic benchmarks. Source: `LLM_CLOSURE_VS_CAPABILITY.md`, `TheFormula/llm_closure_vs_capability.html`, raw evals from EleutherAI/pythia at step 143000.

### 🟢 Coupling-graph approach surfaces interpretable LLM structure

Same 30-second analysis on Pythia-70M reveals: dead layers (4–6 have zero variance during this generation), within-layer clusters (L2 heads H0/H1/H2/H5/H6 correlate >0.95), cross-layer information-flow circuits (L0H6 ↔ L2H3 at +0.986), and anti-phase pairs (layer-norm L3 ↔ L2H5 at −0.974). Source: `TheFormula/llm_node_map_visualization.html`.

### 🟡 Layer depth, not parameter count, drives hierarchical organisation

Within/across-layer correlation ratio peaks at Pythia-410M (24 layers, ratio 1.51) and reverts at Pythia-1B (16 layers, ratio 1.07) despite 2.4× more parameters. Spectral decay shows the same pattern: peaks at 410M, drops at 1B. The framework's interpretation is that depth is what gives the network usable φ-rungs for hierarchy. Source: `LLM_SIZE_SERIES_RESULT.md`.

### 🟡 ARA signature distinguishes cognitive content type

Eight prompt types (story, code, math, emotion, factual, dialogue, poetry, abstract) produce eight distinguishable ARA signatures during generation. Code is most engine-like (mean ARA 1.57, peak 1.91 at paragraph scale). Emotion and dialogue closest to balance (1.255). Multi-sentence-structured content (code, story, math, poetry) peaks at long-range rungs; sentence-organised content (emotion, factual, dialogue, abstract) peaks at sentence-scale. Source: `TheFormula/llm_ara_per_concept_visualization.html`.

### 🔴 φ-deep × φ-wide all-closed prediction (untested)

The framework's prediction for the optimal LLM architecture: layer depth and width both at φ-rung optimum, with all components participating in closed Information³ structure. Predicted consequence: hallucinations (drift from training) substantially eliminated within knowledge; out-of-knowledge content surfaces as honest uncertainty rather than confident fiction; cost is reduced creative-generation flexibility. Falsifiable in principle by training models with different aspect ratios at fixed parameter count. Source: speculative section of `LLM_CLOSURE_VS_CAPABILITY.md`.

### Files

- `release_2026-05/llm/llm_size_series.py` (or current location `TheFormula/llm_size_series.py`)
- `TheFormula/llm_node_map.py`, `llm_ara_per_concept.py`, `llm_ara_test_v3_dynamic.py`
- All `llm_*_data.js` and `llm_*_visualization.html` companions
- `LLM_CLOSURE_VS_CAPABILITY.md`, `LLM_SIZE_SERIES_RESULT.md`, `LLM_INFO_CUBED_RESULT.md`, `LLM_ARA_PILOT_RESULT.md`

### Honest framing

n=4 model sizes is small. The rank result is striking but limited by sample size and confounded by scale. Adding Pythia-1.4B / 2.8B / 6.9B / 12B is the natural confirming experiment, with closure compared directly against parameter count, layer count, and active-node count.
