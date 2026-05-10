# The ARA Framework — A Geometric Theory of Oscillating Systems

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19653363.svg)](https://doi.org/10.5281/zenodo.19653363)

**Dylan La Franchi · independent researcher · May 2026**

A heartbeat, an El Niño cycle, a planetary orbit, a neuron firing, a transformer language model generating text. The framework's claim is that all of these — natural and artificial — share a single coordinate system on a φ-spaced ladder of timescales. Each system can be summarised by a small set of coordinates: period, amplitude, phase, and a build-vs-release ratio (ARA) per rung of the ladder. **A single forward formula, with the same constants, has been tested on systems separated by 38 orders of φ in time, and on transformer LLMs that don't oscillate intrinsically — and produces meaningful predictions on every domain tested so far.**

This repository is the framework, the tests, the failures, and an open invitation to falsify it.

---

## The strongest numbers

| Test | Result |
|---|---|
| **ENSO 1-month forecast (canonical predictor)** | MAE **0.27 °C**, correlation **+0.93** over 242 anchors (NOAA NINO 3.4) |
| **ECG 1-beat forecast (same predictor)** | MAE **19 ms**, correlation **+0.99** (PhysioNet nsr001) |
| **Cross-mammal cycle shape match** | Mean correlation **+0.955** across 6 species pairs (mouse / rabbit / dog / human, PhysioZoo) |
| **3/4 universal ceiling falsification test** | **76 of 77** systems sit in predicted ARA band [0.25, 1.75]; the one outlier is externally clocked (forced van der Pol), exactly as the framework predicts for above-1.75 systems |
| **21 of 21 pre-registered predictions** | Held up across 37 real-world systems (breath cycles, solar activity, river watersheds, arctic sea ice, blood glucose, and others) |
| **Tidally-locked bodies** | Predicted ARA = 1.000; measured **1.000000 for all 9 locked bodies** in the solar system. Unlocked bodies range 365 to 10,465 |
| **LLM closure index vs Pythia capability** | **Spearman ρ = +1.000** on 5 of 6 standard NLP benchmarks (LAMBADA, PIQA, ARC-easy, ARC-challenge, SciQ); the framework metric, computed purely from internal activations with no benchmark data used, perfectly rank-orders the four Pythia model sizes by capability |

The methodology is strict-causal — no future leakage in any test. An earlier acausal-bandpass leakage was caught by my own audit, the affected results were retracted, and the corrected numbers are what you see here.

---

## What this is, in plain English

Things cycle. Hearts beat, lungs breathe, climates oscillate, planets orbit, neurons fire, language models generate text token by token. The question I started with: can the same simple geometric ratio describe a lot of these very different cycles?

The framework's answer is yes — in a soft, statistical way, not a perfect-law way. Self-organising systems cluster near the golden ratio (φ ≈ 1.618) on a build-to-release ratio I call ARA. Multi-scale systems sit on a φ-spaced ladder of timescales. The same formula reads coordinates from any system and projects them forward in time.

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
| **A confidence-tiered catalogue of every finding** | [`INDEX.md`](INDEX.md) |
| **The complete record of advance predictions and outcomes** | [`MASTER_PREDICTION_LEDGER.md`](MASTER_PREDICTION_LEDGER.md) |
| **The canonical predictor module** | [`ara_framework.py`](ara_framework.py) |
| **The long-form theory document with three-tier confidence labels** | [`FRACTAL_UNIVERSE_THEORY.md`](FRACTAL_UNIVERSE_THEORY.md) |
| **The LLM application (closure index → Pythia capability)** | [`LLM_CLOSURE_VS_CAPABILITY.md`](LLM_CLOSURE_VS_CAPABILITY.md) |
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

**Spearman rank correlation = +1.000** on LAMBADA, PIQA, ARC-easy, ARC-challenge, and SciQ. **Pearson r vs log(closure) = +0.886 to +0.997** across those five. The framework metric ranks the four Pythia sizes in exactly the same order the benchmarks do. WinoGrande is the only exception (ρ = +0.800), and WinoGrande is a known weak-scaling benchmark that even GPT-3 barely beats random on. The framework correctly identifies it as the outlier without being told.

This isn't "bigger model is better" — that's already known. The point is that **the framework metric, computed from internal coupling structure with no reference to capability, recovers the capability ordering exactly**. n=4 is small; the natural confirming experiment is adding Pythia-1.4B / 2.8B / 6.9B / 12B to see if rank correlation holds across all eight sizes. See [`LLM_CLOSURE_VS_CAPABILITY.md`](LLM_CLOSURE_VS_CAPABILITY.md) for the full writeup, caveats, and falsifying experiments.

The framework also produced a coupling-graph interpretability tool that surfaces dead layers, within-layer clusters, cross-layer information-flow circuits, and anti-phase pairs in 30 seconds of analysis — without being told what to look for. See [`TheFormula/llm_node_map_visualization.html`](TheFormula/llm_node_map_visualization.html).

---

## Findings by confidence

The full catalogue with sources is in [`INDEX.md`](INDEX.md). The short version:

**🟢 Confirmed under strict-causal validation** — canonical predictor on ENSO + ECG, cross-mammalian cycle shape, lag-h corrector cross-domain, Walker Circulation fractal across rungs, closed-system coupling differs from incidental, mid-horizon dip consistency, 3/4 ceiling on 77 systems, LLM closure-vs-capability rank correlation.

**🟡 Provisional — single test or coincidence-flagged** — predictor crossover at φ^(±7/4), 1.75/0.25 mirror pair as donor ARAs, cosmic budget Ω from π and φ within 0.5%, Information³ → cosmic budget mapping, three-circle architecture, layer-depth-tracks-hierarchy in transformers.

**🔴 Speculative — conceptual, no direct test** — Light/Dark as nested matched-rung pair (origin of c), (π−3)/π universal coupling tax, 1/α ≈ φ^(10 + 1/φ³), quantum entanglement as matched-rung pair, 4D shape as two-spheres-joined / S³ Hopf fibration, φ-deep × φ-wide all-closed LLM should largely eliminate hallucinations.

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