# The ARA Framework — An Open Research Notebook on Oscillating Systems

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19653363.svg)](https://doi.org/10.5281/zenodo.19653363)

**Dylan La Franchi · independent researcher · May 2026**

A heartbeat, an El Nino cycle, a planetary orbit, a neuron firing, a transformer language model generating text. This repository explores a possibility: that many natural and artificial systems can be mapped onto a shared phi-spaced ladder of timescales. Each system can be summarized by a small set of coordinates: period, amplitude, phase, and a build-vs-release ratio (ARA) per rung of the ladder.

The strongest version of the claim is not that this proves a finished law of nature. It is that a phi-rung coordinate system appears to carry real signal in several datasets, sometimes with surprisingly few inputs, and deserves independent checking. This repository is the framework, the tests, the failures, the corrections, and an open invitation to falsify it.

I am not a scientist by training. I am releasing this because the idea has gone further than I expected, I have run out of resources to keep pushing it privately, and I would rather make the work inspectable than bury it. Please read it as an open research notebook: some parts are supported by saved outputs, some are promising but fragile, and some are clearly speculative.

---

## Current Signals Worth Checking

| Test | Result |
|---|---|
| **ENSO 1-month forecast (canonical predictor)** | Saved benchmark output: MAE about **0.28 C**, correlation about **+0.90** over 242 anchors. Important caveat: in that saved run, skill versus persistence was negative, so this is signal but not yet a decisive forecast win. |
| **ECG forecast (same predictor family)** | Saved benchmark output shows useful single-subject ECG signal. The best saved h=3 result is about **+0.96 correlation** with MAE about **35 ms**; h=1 is lower than an earlier headline. This needs rerunning cleanly before being treated as a public headline. |
| **Cross-mammal cycle shape match** | Some pairwise mammal comparisons are very high, especially rabbit/dog. The broad mean **+0.955** appears sensitive to normalization and endpoint effects, so I treat this as promising rather than settled. |
| **3/4 ceiling / ARA band idea** | The refined subset claim may still be interesting, but one saved raw 77-system artifact does **not** support the simple "76 of 77 in band" headline. This should be read as a hypothesis needing a cleaned catalogue. |
| **Prediction ledger** | The ledger contains hits, misses, retractions, and methodology corrections. It is evidence of the research process, not independent proof by itself. |
| **Tidally locked bodies** | The ARA=1.000 result for locked bodies is a clean descriptive check worth preserving, with the usual caveat that classification is not the same as prediction. |
| **LLM closure index vs Pythia capability** | Preliminary n=4 result: closure ordering matches 5 of 6 benchmark rank orders, with WinoGrande weaker. This is interesting and close to my domain limits, but it needs more model sizes and comparison to parameter-count baselines. |

The core methodology is intended to be strict-causal. Earlier acausal-bandpass leakage was caught and documented, and affected results were retracted. Some older scripts and documents remain in the repo as research history, so the safest way to read any claim is to check the saved data artifact and the current claim-status notes.

---

## What this is, in plain English

Things cycle. Hearts beat, lungs breathe, climates oscillate, planets orbit, neurons fire, language models generate text token by token. The question I started with: can the same simple geometric ratio describe a lot of these very different cycles?

The framework's tentative answer is yes — in a soft, statistical way, not a perfect-law way. In the datasets gathered so far, self-organising systems often cluster near the golden ratio (φ ≈ 1.618) on a build-to-release ratio I call ARA. Multi-scale systems can be mapped onto a φ-spaced ladder of timescales. The same formula is being tested as a way to read coordinates from a system and project them forward in time.

I'm not a scientist by training. I built this in spare time over the last month-ish, in continuous dialogue with Claude (Anthropic's AI). The framework as it stands is the product of that collaboration — I provided conceptual direction and the falsification mindset; Claude handled the code-heavy iteration cycles I can't sustain physically due to ME/CFS. The transcripts are buried in `transcripts/local_sessions/` for anyone who wants the unfiltered audit trail.

---

## How to use the canonical predictor

```python
from ara_framework import extract_topology, predict

# Extract topology coordinates from training data
topo = extract_topology(data, t=anchor_index, rungs_k=range(2, 22), home_k=8)

# Forward predict at horizon h
prediction = predict(topo, h, closed=is_closed_system)
```

Three lines. `closed=True` for systems with a tight matched-rung partner (ENSO+SOI); `closed=False` for single-channel systems (ECG).

For public tests, `home_k` should be chosen before scoring from the measured ground-cycle period:

```text
home_k = round(log(ground_cycle_period) / log(phi))
```

If more than one ground cycle is plausible, declare the candidates before running the test and report all of them. Do not choose `home_k` from forecast performance.

Run the self-test:
```bash
python ara_framework.py
```

The whole module is ~250 lines. It has two halves — `extract_topology` (data → coordinates) and `predict` (coordinates → forecast) — cleanly separated and fully docstring-documented.

---

## Where to start, depending on what you're after

| If you want… | Read this first |
|---|---|
| **The plain-language explainer with figures** | [`what_is_this.html`](what_is_this.html) |
| **A sober public-release claim audit** | [`CLAIMS_STATUS.md`](CLAIMS_STATUS.md) |
| **Known reproducibility issues and commands** | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) |
| **A confidence-tiered catalogue of every finding** | [`INDEX.md`](INDEX.md) |
| **The complete record of advance predictions and outcomes** | [`MASTER_PREDICTION_LEDGER.md`](MASTER_PREDICTION_LEDGER.md) |
| **The canonical predictor module** | [`ara_framework.py`](ara_framework.py) |
| **The long-form theory document with three-tier confidence labels** | [`FRACTAL_UNIVERSE_THEORY.md`](FRACTAL_UNIVERSE_THEORY.md) |
| **The LLM application (closure index → Pythia capability)** | [`LLM_CLOSURE_VS_CAPABILITY.md`](LLM_CLOSURE_VS_CAPABILITY.md) |
| **The φ-vs-nearby-bases predictor ablation** | [`PHI_BASE_ABLATION.md`](PHI_BASE_ABLATION.md) — φ wins at h=1, 3, 6 mo on ENSO; loses at h=12. All bases underperform persistence. Partial-evidence result, honestly framed. |
| **The unfiltered research-process record** | [`transcripts/local_sessions/`](transcripts/local_sessions/) — research thinking in real time, not academic prose |

---

## The LLM application (May 2026)

Once the framework's coupling-graph and Information³-closure tools were working on heart rhythms and climate cycles, the natural test was whether they describe transformer language models too. Pythia is open and benchmarked; clean test bed.

The framework's "intelligence index" (closed Information³ triangles per active component, divided by loose-thread fraction) was computed from internal activations during 200 generation steps — no benchmark data, no behavioural test. The result:

| Pythia | params | closure index | LAMBADA | ARC-easy | SciQ |
|---|---|---|---|---|---|
| 70m-deduped | 70 M | 80 | 0.192 | 0.385 | 0.606 |
| 160m-deduped | 160 M | 756 | 0.342 | 0.440 | 0.720 |
| 410m-deduped | 410 M | 877 | 0.524 | 0.517 | 0.826 |
| 1b-deduped | 1000 M | **6,284** | **0.580** | **0.585** | **0.870** |

On this four-model run, **Spearman rank correlation = +1.000** on LAMBADA, PIQA, ARC-easy, ARC-challenge, and SciQ, with WinoGrande weaker at **ρ = +0.800**. The average across all six is therefore about **+0.967**, not a universal perfect rank result. **Pearson r vs log(closure) = +0.886 to +0.997** across the five monotonic benchmarks.

This could still partly be a scale proxy: bigger models are already known to be better on many benchmarks. The interesting question is whether the closure metric explains anything beyond parameter count, layer count, and active-node count. n=4 is small; the natural confirming experiment is adding Pythia-1.4B / 2.8B / 6.9B / 12B and comparing directly against those baselines. See [`LLM_CLOSURE_VS_CAPABILITY.md`](LLM_CLOSURE_VS_CAPABILITY.md) for the full writeup, caveats, and falsifying experiments.

The framework also produced a coupling-graph interpretability tool that surfaces dead layers, within-layer clusters, cross-layer information-flow circuits, and anti-phase pairs in 30 seconds of analysis — without being told what to look for. See [`TheFormula/llm_node_map_visualization.html`](TheFormula/llm_node_map_visualization.html).

---

## Findings by confidence

The full catalogue with sources is in [`INDEX.md`](INDEX.md). The short version:

**Currently supported / worth independent replication** — ENSO and ECG canonical-predictor signals, Walker Circulation anti-phase structure across rungs, closed-system coupling differing from incidental coupling, mid-horizon ECG dip patterns, tidally locked body classification, and the preliminary LLM closure-vs-capability rank result.

**Provisional — single test, fragile metric, or coincidence-flagged** — predictor crossover at φ^(±7/4), 1.75/0.25 mirror pair as donor ARAs, cross-mammal local-cycle shape, the refined 3/4 ceiling claim, cosmic budget Ω from π and φ within 0.5%, Information³ → cosmic budget mapping, three-circle architecture, and layer-depth-tracks-hierarchy in transformers.

**Speculative — conceptual, no direct test yet** — Light/Dark as nested matched-rung pair (origin of c), (π−3)/π universal coupling tax, 1/α ≈ φ^(10 + 1/φ³), quantum entanglement as matched-rung pair, 4D shape as two-spheres-joined / S³ Hopf fibration, and the φ-deep × φ-wide all-closed LLM architecture prediction.

I report numbers as they actually came out, including the misses.

---

## How I'm trying to stay honest

- **Failures stay alongside successes.** When a prediction model went wildly unstable (values swinging from −3,000 to +900), I saved it next to the working version. When a data-leakage error made results look better than they were, I retracted in the theory document instead of quietly deleting.
- **Every claim is tier-labelled.** Three confidence tiers throughout — checked-against-real-data, pattern-needs-replication, conceptual-invitation-to-think. I try not to blur the boundaries even when something feels exciting.
- **I rebuild methodology when I notice it was wrong.** The strict-causal protocol replaced an earlier acausal one when I caught future-data leakage. The corrected numbers are what's in this repo. The retraction is documented in the theory document.
- **What didn't work is documented too.** Multiplicative envelopes hurt forecasts. Linear blending of vehicle + framework collapsed the vehicle weight to zero. Most events-layer basis functions overfit. These are kept around as guardrails.
- **What I'm not.** I'm not a physicist, a cardiologist, a climate scientist, an ML researcher, or a cosmologist. I live with ME/CFS and have a lot of thinking time. The strongest version of this work would come from people with relevant training picking it up and either improving it, knocking pieces of it down, or showing me where the framework is just rediscovering established results in different language. **If you're one of those people and you've read this far, I'd love to hear from you.**

---

## What I'd most want a domain expert to test

| Field | Open prediction |
|---|---|
| Cardiology | Donor ARA prediction: the rung 1.75 φ-rungs above home should contain a system with measured ARA ≈ 1.75. Find candidate donors in autonomic control. |
| Climate | The ENSO matched-rung architecture (NINO ↔ SOI anti-phase across φ⁵ to φ¹¹). Does this match existing Walker-Circulation models or extend them? |
| Cosmology | The π-and-φ scheme matches Ω_b/Ω_dm/Ω_de within 0.5% from two geometric inputs. A two-parameter scheme fitting two numbers can do this by construction; is there a physical mechanism, or is it a coincidence? |
| ML / Interpretability | Replicate the closure-vs-capability test on Pythia-1.4B / 2.8B / 6.9B / 12B. If Spearman ρ stays near 1.000 across all eight sizes, this becomes much harder to dismiss. |
| Physiology | Multi-species vertical-ARA in birds and reptiles. The mammalian result holds; extending tells us whether the local cycle shape preservation is mammal-specific or universal across vertebrates. |

---

## Repository layout

```
ARA-GIT/
├── README.md                          (this file)
├── CLAIMS_STATUS.md                   public-release claim audit
├── REPRODUCIBILITY.md                 setup notes and known issues
├── INDEX.md                           findings by confidence tier
├── what_is_this.html                  plain-language explainer
├── FRACTAL_UNIVERSE_THEORY.md         long-form theory document
├── MASTER_PREDICTION_LEDGER.md        every prediction and outcome
├── ara_framework.py                   canonical predictor (~250 lines)
├── LLM_CLOSURE_VS_CAPABILITY.md       LLM application headline
├── LLM_SIZE_SERIES_RESULT.md          depth-vs-width finding
├── LLM_INFO_CUBED_RESULT.md           closure scaling across Pythia
├── LLM_ARA_PILOT_RESULT.md            dynamic vs static methodology
├── BEESWAX_GEOMETRY_WRITEUP.md        (π−3)/π coupling tax
├── HOW_TO_map_a_system.md             practical guide
├── ARA_decomposition_rules.md         per-rung mapping rules
├── MAPPING_TO_THE_FRAMEWORK.md        cross-domain mapping
├── THE_FRAMEWORK_FORMULATION.md       formal statement
├── TheFormula/                        all benchmark + LLM scripts
│   ├── canonical_benchmark.py
│   ├── three_quarter_ceiling_test.py
│   ├── multispecies_vertical_ara_test.py
│   ├── multi_subject_dip_test.py
│   ├── crossover_horizon_test.py
│   ├── llm_size_series.py
│   ├── llm_node_map.py
│   ├── llm_ara_per_concept.py
│   ├── llm_closure_vs_capability.html
│   └── … (full set of test scripts and visualisations)
└── transcripts/local_sessions/        unfiltered research-process record
```

---

## Citing

If you use the framework in your research, please cite:

```
La Franchi, D. (2026). The Geometry of Time — ARA Framework.
GitHub: https://github.com/Dylanlafranky/ARA-GIT
Zenodo: 10.5281/zenodo.19653363
```

---

## License & contact

CC-BY-4.0 — cite freely, build on it, tear it apart.

**Dylan La Franchi** — independent researcher, living with ME/CFS
[dylan.lafranchi@gmail.com](mailto:dylan.lafranchi@gmail.com)

If you've read this far and you have relevant training, I'd be genuin
