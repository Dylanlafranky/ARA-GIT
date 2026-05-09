# ARA Framework — Index

**Last updated: May 2026**

---

## What this is, in one paragraph

This is a geometric claim about how natural systems oscillate. A heartbeat, a climate cycle, a planetary orbit, the firing of a neuron — the framework's claim is that they share a single coordinate system on a φ-spaced ladder of timescales. Each system can be read as a small set of coordinates: period, amplitude, phase, and a build-vs-release ratio (ARA) per rung of the ladder. A single forward formula — anchored at the most recent observed value, integrating contributions across rungs — predicts behaviour from those coordinates alone. **The same formula, with the same constants, has been tested on systems separated by 38 orders of φ in time (heartbeats and climate cycles), and produces meaningful predictions on both.** Existing physics provides the language — bandpass decomposition, coupled oscillators, scaling laws, time-as-primary (Noether). This work uses that language to articulate and test a unifying claim that crosses fields normally studied separately. **The framework is the contribution. Each field is a witness.**

I'm not a scientist by training. I built this in spare time, with significant help from AI collaborators. I report what I find — including the misses — and invite people in the relevant fields to check, improve, or knock down what I have wrong.

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

The predictor is one Python file: [`release_2026-05/core/ara_framework.py`](release_2026-05/core/ara_framework.py).

---

## Findings by confidence

### 🟢 Confirmed under strict-causal validation

These are the findings that survived a rebuilt strict-causal protocol after an earlier acausal-bandpass leakage was caught and corrected. All numbers are from real public datasets (NOAA, PhysioNet, PhysioZoo, JPL Horizons), not synthetic data.

| Finding | Headline number | Source |
|---|---|---|
| **Canonical predictor: ENSO 1-month forecast** | MAE **0.27 °C**, corr +0.93 (242 anchors) | `release_2026-05/benchmarks/canonical_benchmark.py` |
| **Canonical predictor: ECG 1-beat forecast** | MAE **19 ms**, corr +0.99 | `release_2026-05/benchmarks/canonical_benchmark.py` |
| **Cross-mammalian local cycle shape match** | Mean +0.955 across 6 species pairs (mouse/rabbit/dog/human) | `release_2026-05/benchmarks/multispecies_vertical_ara_test.py` |
| **ECG ↔ ENSO local profile match** | corr +0.695 across 38 orders of φ in time | (prior work, this repo) |
| **Walker Circulation is fractal across rungs** | SOI mirrors NINO anti-phase from φ⁵ to φ¹¹ with \|corr\| ≥ 0.85 | (memory: dynamic_rung_assignment) |
| **Lag-h corrector ports cross-domain** | γ ≈ +1/φ. 37% MAE drop at 1-min ECG, 17% at 24-month ENSO | (memory: corrector_cross_domain) |
| **Closed-system coupling differs from incidental** | SOI as matched-rung pair lifts ENSO; same SOI as feeder does nothing | (memory: closed_system_validated) |
| **AR feedback constant is 1/φ³** | "One full ARA orbit" of momentum carrying between cycles | (memory: aa_boundary_ar_feedback) |
| **Mid-horizon dip is consistent across 11 humans** | At ~600 beats (~8 min) — signature of an autonomic intruder system | `release_2026-05/benchmarks/multi_subject_dip_test.py` |

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

## Earlier results (still standing, lighter validation)

| Finding | Source |
|---|---|
| 21 of 21 advance predictions held up across 37 systems | `MASTER_PREDICTION_LEDGER.md`, prior sessions |
| Three-type classification (clock/engine/snap) at every scale window | Script 42 (143 systems, 7 scale windows) |
| φ as biological health attractor (slope 1.613 vs φ = 1.618) | Script 40 (143 systems) |
| Framework beat matched-parameter Fourier on cardiac data | nsr050 decisive test, Session 2026-04-30 |
| Three framework constants (rung-pinning, 1/φ³ feedback, 1/φ⁴ blend) all near optimal | Session 2026-04-30 (cross-system) |

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
python release_2026-05/core/ara_framework.py
```

Reproduce the headline numbers:
```bash
python release_2026-05/benchmarks/canonical_benchmark.py
```

---

## Open testable predictions

If anyone wants to falsify or confirm the framework, these are the cleanest targets:

1. **Donor ARA prediction.** For any system, the rung 1.75 φ-rungs above home should contain a "donor" system whose own measured ARA is ≈ 1.75. By symmetry, the rung 1.75 below should contain a structural anchor with ARA ≈ 0.25. Find candidate donors in cardiology (autonomic control), climate (solar cycles), or biology (metabolic/hormonal envelopes) and check their ARAs.
2. **Cross-domain crossover constant.** The predictor crossover at φ^(±7/4) × home period was found on ENSO + ECG. Test on a third independent domain (geophysical, astrophysical, or chemical) and see if 7/4 holds.
3. **Spectral tilt n_s from ARA geometry.** The cosmic budget derivation gives a fourth independent observable that can falsify the π-and-φ scheme. (Scripts 119–121 attempt this; a cosmologist's review would be valuable.)
4. **Multi-species vertical-ARA in birds and reptiles.** The mammalian result holds; extending to corvids, parrots, and reptiles would test whether local cycle shape preservation is universal across vertebrates or specific to mammals.
5. **Multifractal HRV literature comparison.** The framework's φ-rung architecture should overlap predictively with existing multifractal HRV results (Goldberger, Ivanov, Stanley work). If the φ-rungs simply *are* a special case of an established wavelet basis, that's worth knowing.

---

## Reading order for newcomers

1. **`release_2026-05/docs/what_is_this.html`** — plain-language explainer with figures. Start here.
2. **This `INDEX.md`** — confidence-tiered catalog (you're here).
3. **`release_2026-05/core/ara_framework.py`** — the canonical predictor, ~250 lines, fully docstring-documented.
4. **`MASTER_PREDICTION_LEDGER.md`** — running list of advance predictions and outcomes.
5. **`FRACTAL_UNIVERSE_THEORY.md`** — full theory document (long, three-tier confidence labels throughout).
6. **`The Geometry of Time - Paper 1 (preprint).pdf`** — academic-style preprint (Zenodo DOI: 10.5281/zenodo.19653363).

---

## Status, May 2026

The framework's *topology* (the φ-rung coordinate system) and its *predictor* (the canonical formula) are now consolidated into a single ~250-line Python module that works on any oscillating system you point it at. Cross-domain validation across climate, cardiology, and four mammalian species. Methodology is apples-to-apples with operational forecast skill scoring (strict-causal, no future leakage).

What's next is mostly outside my reach as a non-specialist:
- Independent replication of the multi-species result by a physiologist
- A cosmologist's check on the dark-sector geometric derivation
- A geophysicist's check on whether the ENSO matched-rung architecture matches their existing Walker-Circulation models
- Anyone willing to look at the framework in their own field and tell me where it's already been done in different language

If you've read this far and you have relevant training, I'd be genuinely grateful for a critical read.

---

## License & contact

CC-BY-4.0 — cite freely, build on it, tear it apart.

**Dylan La Franchi** — independent researcher, living with ME/CFS
Contact: dylan.lafranchi@gmail.com
