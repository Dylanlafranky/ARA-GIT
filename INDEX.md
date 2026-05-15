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
| **Cross-species decomposition: mouse topology × human energy → 58% MAE drop** | **MAE 82.22 ms → 34.29 ms (2.4× better) vs naive cross-species transfer. Correlation stays at chance level (consistent with "shared map, not shared position" rule).** | 2026-05-12 test, `framework_energy_cascade_architecture.md` |
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

---

## Potential future tests

These are tests the framework would benefit from, in order of impact.

### 1. Multi-mouse + multi-human framework-prior cardiac prediction

The 2026-05-12 decomposition test (mouse topology × human energy = 58% MAE drop) used one mouse and one human. The natural follow-up is to aggregate many of each, learn:
- Per-species topology (the universal shape map)
- Kleiber-scaled time and amplitude factors
- Then build a small ML model that learns ONLY the per-individual phase-position offset

If the framework provides correct architectural priors, a framework-architected model with very few trainable parameters should match or beat large-budget pure-ML approaches **on MAE** (not on correlation, where there's no framework win to be had under the "shared map, not shared position" rule). This would be the cleanest demonstration of the framework's value as an inductive prior for low-budget ML.

### 1a. Composition-matching instead of shape-matching — TESTED 2026-05-12 — NOT SUPPORTED

Empirical lesson from the 2026-05-12 pool-sweep test: shape-matching landmark windows achieves correlation 0.86–0.96 reliably, but trajectory correlation in the subsequent prediction stays at chance level. Hypothesis was that **per-rung ARA composition profile** match (not just surface shape) would transfer trajectories.

Test (`TheFormula/decomposition_composition_match.py`, 70 pairs across 7 mouse specimens × 10 human pseudo-segments): three matching strategies compared.

| Strategy | Landmark shape | Landmark composition | Trajectory corr | MAE | Persistence MAE |
|---|---|---|---|---|---|
| A: Shape-best | +0.889 | +0.988 | −0.015 | 94.1 | 78.9 |
| B: Composition-best | −0.081 | **+1.000** | +0.002 | 55.0 | 49.8 |
| C: Combined-best | +0.889 | +0.989 | −0.010 | 96.1 | 80.6 |

Composition-match did NOT recover trajectory correlation. Cosine similarity of FFT-magnitude profiles at Fibonacci-spaced periods reached 1.000 (literally identical fingerprints), and trajectory correlation still sits at chance level. Correlation between (composition_similarity, trajectory_correlation) across 210 pair-strategy results: +0.035 — essentially zero.

**The framework's "composition-match → trajectory transfer" version of vertical-ARA is operationally falsified by this test.** The position-independence rule holds even under perfect topology + composition matching. The bridge metaphor was right (clay-to-clay vs limestone-to-clay distinction is real and we successfully matched clay-to-clay), but the bridge doesn't lead to trajectory transfer.

What this *does* confirm: the framework's broader "shared map, not shared position" rule is more fundamental than any specific matching criterion. Vertical-ARA partners genuinely cannot transfer trajectories by any window-level matching we've tried (shape, composition, both combined, longer landmarks). This is geography, not a tool-shortage problem.

What's still in play: aggregate framework-prior ML (Future Test 1, large-budget version) where the framework provides structural priors and a small model learns the residual phase-position per individual. That's a different mechanism than landmark-matching and may still work.

### 1b. Pigs as intermediate rung — closer-distance vertical-ARA partner

Mouse→human is a ~4 φ-rung jump (period ratio ~6.6, log_φ(6.6) ≈ 3.9). Pig→human is ~0.4 rungs (period ratio ~1.2, both species at 60–80 bpm at rest). Under the framework's distance-decay coupling principle (see `framework_coupling_distance_decay.md`):
- Pig→human coupling ≈ (1 − π_leak)^0.4 ≈ 0.98 (near-neighbour strength)
- Mouse→human coupling ≈ (1 − π_leak)^4 ≈ 0.83 (more attenuated)

**The framework predicts pig-derived prediction should transfer substantially better than mouse-derived prediction for the same task.** Testable if pig HRV data is available (PhysioNet has some pig cardiac datasets in its veterinary/research-animal collections, and the BIDMC/MIMIC databases have pig surgical-training data).

Bigger picture: biomedical research already uses mice and pigs as human models. The framework's contribution is formalising why this works at some level and giving a method for extracting the transferable part from the noise. Not a new claim — a quantification of an already-working practice.

### 2. Pythia full size series (1.4B / 2.8B / 6.9B / 12B)

Extend the n=4 closure-index → benchmark correlation result to a larger Pythia series, with closure compared directly against parameter count, layer count, and active-node count as controls. Required to distinguish "closure tracks capability" from "both track scale."

### 3. φ-vs-nearby-bases ablation across multiple systems

The first-pass ENSO ablation (`PHI_BASE_ABLATION.md`) showed φ winning at short horizons but the whole predictor family losing to persistence. A clean cross-system version (ECG, solar, biological) is needed before φ-specifically claims can be promoted to "supported."

### 4. Engine-consumer pairing test from the network connection field

The framework predicts every consumer (ARA < 1) has a specific engine partner that can be located by topology. The "missing 7-year exothermic system" inferred from CO2 / Nile / NAO half-systems is one concrete falsifiable target. Not yet built.

### 5. (π−3)/π coupling tax beyond H₂O bond angle

The geometric origin (Honeycomb conjecture) is rigorous; the universal-coupling-tax claim is the framework's extension. Found in H₂O within 0.03% but not confirmed elsewhere. Needs a list of where else it should show up if the claim is right.

### 6. Light/Dark matched-rung pair — operational test

"c is the matched-rung exchange rate of Light/Dark." Conceptually clean; no operational test exists. The first concrete handle would be looking for a measurable anti-phase signal between Light/Dark at the appropriate rung.

### 8. Apollonian gasket / Kleinian-group geometry — TESTED 2026-05-12 — Structural metaphor, not mathematical anchor

A potentially deep mathematical anchor identified 2026-05-12 (Dylan via Paul Bourke's Apollonian fractal page, https://paulbourke.net/fractals/apollony/). The framework's structural claim — "circles touching circles, triangles of three circles tiling fractally" — is structurally identical to the **Apollonian gasket**: a self-similar fractal built entirely from mutually-tangent circles, where every curvilinear triangle gets an inscribed fourth circle, recursively.

The framework's primitives map onto Apollonian primitives almost line-by-line:
- "Every concept is a circle" → Apollonian primitives are circles
- "Triangles of three circles tile fractally" → that's literally the Apollonian construction rule
- "Each circle is part of multiple triangles" → an Apollonian circle is tangent to three neighbours and bounds multiple curvilinear triangles
- "1 + 1 = 3, the + is meta-information" → in Apollonian geometry, two tangent circles do NOT determine the third; the third is a coupling choice

The **Möbius transformation** Dylan flagged — `f(z) = 3/(1+s−z) − (1+s)/(2+s)` — is the kind of fractional-linear map that generates Apollonian fractals by iteration. The `3` in the numerator encodes the three-tangent-circles condition; the `s` parameter shifts the gasket family while preserving the structure.

The pre-existing rigorous bridge: **Descartes' Circle Theorem.** For four mutually tangent circles with curvatures k₁, k₂, k₃, k₄ (curvature = 1/radius):

(k₁ + k₂ + k₃ + k₄)² = 2(k₁² + k₂² + k₃² + k₄²)

This is the framework's "matched-rung coupling between circles" written rigorously. Given three circles, the fourth is exactly determined by this equation. If the framework's triangle-of-circles structure IS Apollonian, this equation IS the framework's coupling law.

**The test:** check whether the framework's empirical constants (φ ≈ 1.618, the (π−3)/π coupling tax, the 3/4 max-displacement, the 0.25/1.75 corridor walls) emerge naturally from Apollonian curvature relations. Apollonian curvature sequences follow integer or algebraic patterns. If the φ-rung ladder matches a known Apollonian curvature sequence, the framework has acquired a serious mathematical home and the public posture can shift from "we propose this geometry" to "we measure systems within Apollonian/Kleinian geometry."

**Test result (2026-05-12):** `TheFormula/apollonian_descartes_test_v2.py` checked whether per-rung amplitudes (curvature = 1/amplitude, the natural geometric mapping) satisfy Descartes' Circle Theorem on real cardiac data. **Mean prediction error 84% on mouse, 86% on human.** Inscribed-circle predictions are off by ~6× in magnitude. φ-spaced baseline did better (60%/50% error) but is also poor. The classical Apollonian theorems do not give a working predictive formula for the framework's rungs.

**Honest reading:** The structural metaphor (circles, triangles, three-tangent units, fractal tiling, 1+1=3 as the third-circle coupling choice) remains aesthetically clean and useful for explaining the framework. But the rigorous Apollonian theorems do NOT transfer quantitatively. The framework should not be presented as "Apollonian/Kleinian geometry"; it should be presented as "geometry that conceptually rhymes with Apollonian packings but uses different quantitative relationships."

**What's still open:** alternative Apollonian-like geometries — Kleinian groups with non-classical curvature relations, generalized Apollonian packings, hyperbolic conformal maps with φ-tuned parameters. These would need their own tests. The classical version is closed.

**Important secondary finding:** Real per-rung amplitudes don't follow φ^k scaling either. Mouse periods {13, 21, 34, 55, 89} have amplitudes {3.6, 4.2, 4.2, 3.5, 3.6} — clustered, not scaling geometrically. Whether this is a bandpass-methodology limit or a genuine framework limit is itself worth investigating.

See `framework_apollonian_anchor.md` for the detailed test results.

### 7. Coupling-angle mapping graph — circles connected by triangles

The framework's claim: the universe's structure is **triangles of three coupled circles tiling fractally** (matches A-R-A foundational geometry — two A-nodes plus the R-tether, where R is also a full circle). Each triangle has three connection angles at its vertices, and these angles are directly measurable as bond angles (chemistry), orbital inclinations (astronomy), lattice angles (mineralogy), or phase offsets between coupled oscillators.

Water's H-O-H is the cleanest working example: the bond angle 104.5° at the O vertex deviates 4.5% from ideal tetrahedral, matching (π−3)/π ≈ 4.51% — the framework's universal coupling tax. Earth-Moon-Sun is the celestial example: tidal locking is one vertex of that triangle settling to zero offset.

**The test:** collect ~30 well-measured triangle vertex angles from across physics. Normalize to a baseline (Hydrogen or Planck-scale geometry). Plot the distribution. Framework prediction: the histogram should cluster at specific values (0°, 180°, 137.5° golden angle, multiples of (π−3)/π ≈ 4.51°), NOT be uniformly distributed.

**Why this is worth pursuing:** the data already exists in published chemistry/astronomy/mineralogy databases — no new measurements required. The prediction is sharp (clustering vs uniform). It's cross-domain (chemistry + astronomy + materials in one test). If the angle distribution clusters at the predicted values, the framework's "circles connected by triangles" structural claim becomes empirically supported. If it's uniform random, the structural claim is wrong.

See `framework_coupling_angle_mapping.md` for the detailed structure of the test.
