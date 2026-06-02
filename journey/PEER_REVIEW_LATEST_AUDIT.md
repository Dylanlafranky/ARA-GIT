# Peer Review Audit — Latest Formula Models and ARA Mapping

**Date:** 2026-05-26
**Reviewer:** Claude (peer review, falsification focus)
**Scope:** Commits `8fe383c`, `6a5d077`, `3147c01` — 44 new Python scripts, 22 Mapping files, ~170 total new files

---

## Executive Summary

This batch contains the most mechanistically ambitious formula models to date (a full layered-sand rolling-sphere cascade) and the most honest mapping cleanup yet (the Over-2 Audit). The formula models are impressively detailed physical analogies, but they do not beat persistence on ENSO correlation at any horizon except h=3. The mapping work, by contrast, is a genuine scientific contribution: three catalog entries with absurd ARA values were traced to specific measurement errors and recomputed from first principles, and the galactic rotation entry was independently tested and downgraded.

**Bottom line for the formula models:** The layered-sand cascade is a structurally accurate "now machine." It produces +0.977 correlation with the current terrain state at every horizon, and the phase-delay diagnostic confirms +0.994 shifted correlation at h=12 — meaning the terrain description and shape are correct but the reading point is not advanced far enough across the sphere. The negative raw correlations at h=12/24 are a calibration/advance problem, not a structural failure. The wobble surface outperforms it precisely because the wobble lookup implicitly encodes the advance distance from historical outcomes. The remaining bottleneck is the contact-pressure-to-roll-distance conversion: the formula produces ~0.13 movement when ~0.74-1.03 is needed (ratio 0.12-0.18).

**Bottom line for the mapping:** The Over-2 Audit and quantum recomputations are the strongest quality-control work in the repo's history. The U-238 alpha ARA correction (from 1.41×10³⁸ to 0.990) is a textbook example of catching a units error. The galactic rotation test honestly concludes phi is not supported.

---

## I. Formula Model Audit

### A. Layered Sand Series (8 scripts)

These scripts encode a physical metaphor: a moving floor drives fine sand grains, each layer rolls opposite the layer beneath it, two lower contacts create wobble, upper coarse layers apply compression, and the measured coarse sphere rolls under a fixed reading point. The terrain on each sphere is recursive ARA sub-bands with local phi valleys.

**Causal guards:** All scripts use only `raw_delta(frame, series, anchor, period)` and `raw_value(frame, series, anchor)` where `anchor` is the origin month index. No future data enters the prediction. This is verified and clean.

**Scores (Single Formula, ENSO 6/12/24 focus):**

| Model | h=6 corr | h=12 corr | h=24 corr | h=6 MAE | h=12 MAE | h=24 MAE |
|---|---:|---:|---:|---:|---:|---:|
| Persistence | +0.351 | -0.067 | -0.274 | 0.737 | 0.925 | 1.027 |
| Wobble surface (legacy) | +0.557 | +0.072 | +0.026 | 0.536 | 0.630 | 0.658 |
| **Formula (fixed)** | **+0.388** | **-0.061** | **-0.281** | **0.710** | **0.905** | **1.021** |

**Critical findings:**

1. **The Formula is a structurally accurate "now machine" that under-rolls.** The formula correlates at +0.977 with the current terrain state, meaning it reads the current sphere correctly. The phase-delay diagnostic confirms shifted correlations of +0.994 at h=12 and +0.989 at h=24 — the terrain shape is accurate but arrives late by approximately the forecast horizon. The negative raw h=12/24 correlations are a consequence of under-movement (predictions barely depart from the current value) combined with ENSO mean-reversion, not of fundamentally wrong geometry.

2. **Amplitude ratio is 0.158 (focus 6/12/24) — this is the central bottleneck.** The formula produces predicted movements of ~0.13 when actual movements are 0.74-1.03 (ratio 0.12-0.18). The contact-pressure-to-roll-distance conversion in the cascade is far too weak. The `mean_abs_delta_ara` is ~0.004 and `mean_delta_phase` is ~22-90° but this phase advance doesn't translate into enough ARA movement on the sphere.

3. **The wobble surface outperforms because it implicitly encodes advance distance.** When the wobble surface matches a current terrain signature to a historical one, the matched historical outcome already includes the correct amount of future movement. This is the advance operator the layered-sand formula is missing. The formula describes the terrain and the forces; the wobble surface provides the actual roll distance from empirical analogues.

4. **The parameter search partially fixes amplitude but not direction.** Fitting 16 parameters on pre-2017 data improves holdout amplitude ratio from 0.143 to 0.905 — proving the right magnitude of roll IS reachable within this architecture. But holdout 6-month correlation goes negative (-0.236) and holdout 24-month is weak (-0.091), suggesting the optimizer found a global scaling that moves predictions the right amount but not consistently in the right direction. The next step should constrain the search to fewer parameters (primarily the roll-distance scaling) while keeping the already-accurate terrain geometry fixed.

5. **Topological formula variants.** The topological version (replacing per-sphere terrain with recursive ARA/sub-ARA topology) performs similarly. The `topological_phi_wobble` variant shows an interesting improvement at h=24 (corr +0.374), but this uses a golden-angle precession clock — a deterministic function of time alone. This needs careful checking: if the wobble axis is purely temporal, the h=24 improvement could be capturing a seasonal/4-year cycle that happens to align with the test window rather than genuine geometric signal.

### B. Sphere/Terrain Series (12+ scripts)

This series builds up from terrain-arrival predictors through sphere atlases, orientation roll, fractal terrain readers, and recursive grids.

**Key result — Recursive Sphere Grid (verified by rerun):**

| Model | h=6 corr | h=12 corr | h=24 corr | h=6 MAE | h=12 MAE | h=24 MAE |
|---|---:|---:|---:|---:|---:|---:|
| Persistence | +0.351 | -0.067 | -0.274 | 0.737 | 0.925 | 1.027 |
| grid_phi_water | +0.355 | -0.079 | -0.275 | 0.706 | 0.873 | 0.992 |

The recursive grid produces MAE improvements over persistence (especially at h=12 and h=24), but the correlation improvements are negligible. The grid is essentially pulling predictions toward phi valleys in ARA space, which produces smaller errors on average (because the phi valleys are near the center of the distribution) without capturing the directional dynamics.

### C. Comparison with Prior Best Models

For context against the earlier-audited models:

| Model | h=1 corr | h=12 corr | h=24 corr | h=60 corr |
|---|---:|---:|---:|---:|
| Lag ridge (baseline) | +0.970 | +0.139 | +0.223 | negative |
| Triangle Balance Universal | +0.967 | +0.331 | +0.331 | -0.289 |
| Shape Kernel (2+coord) | +0.630 | +0.117 | — | +0.272 |
| **Layered Sand Formula** | **+0.749** | **-0.061** | **-0.281** | — |
| **Layered Sand (fitted)** | — | **+0.194** | **-0.091** | — |

The layered sand formula is a step backward from Triangle Balance Universal at every comparable horizon. The fitted version improves h=12 but worsens h=24 relative to the unfitted version's already-negative correlation.

---

## II. ARA Mapping Audit

### A. Over-2 Audit — Excellent Quality Control

The Over-2 Audit (`Mapping/ARA_OVER2_AUDIT.md`) is the best self-cleaning work in the repo. It finds 45 out of 234 nodes have ARA > 2, traces all of them to the older hand-curated catalogue layer (none in measured_fit or state_geometry layers), and classifies them:

- 15 extreme (ARA > 10): snap/overflow or rung mismatch
- 30 moderate (ARA 2-10): need reverse orientation, subsystem split, or rung adjustment
- 3 fixed with recomputation (U-238 alpha, Na fluorescence, H Lyman-alpha)

The retest rules are sound and well-defined.

### B. U-238 Alpha Recomputation — Verified, Excellent

**Original catalog ARA:** 1.41 × 10³⁸ (absurd)
**Error found:** Catalog used the *half-life* (4.47 Gyr = 1.41×10¹⁷ s) as the oscillation period instead of the actual nuclear oscillation period.
**Corrected ARA:** 0.990 (verified by rerun)
**Method:** Classical trajectory integration (velocity-Verlet) in Woods-Saxon + Coulomb potential. The script finds inner/outer turning points, integrates one full oscillation (~5.4×10⁻²² s), and decomposes into accumulation (outward, KE→PE) and release (inward, PE→KE) phases.

**Peer review notes:**

- The physics is correctly implemented. Woods-Saxon parameters (V₀=50 MeV, a=0.65 fm, R₀=1.25 fm) are standard.
- ARA ≈ 0.990 means the nuclear oscillation is nearly symmetric, which is physically reasonable — the potential well is roughly symmetric about its minimum.
- The action/π calculation (1.17×10⁻³⁴ J·s ≈ ℏ) is a nice consistency check.
- One caution: this is a classical trajectory in a quantum system. The alpha particle is quantum-mechanically tunneling through the Coulomb barrier; it doesn't classically oscillate inside the well in the usual sense. The classical turning-point decomposition is a valid proxy for the accumulation/release time ratio, but calling it a "nuclear oscillation period" should be qualified. The actual quantum state is a quasi-bound state with a complex energy, not a periodic classical orbit.

### C. Na/H Fluorescence Recomputation — Clean but Trivially Symmetric

**Original errors:** Na fluorescence ARA was 4.78×10⁷, H Lyman-alpha was 2.36×10⁶ — both from dividing natural lifetime by optical oscillation period (wrong rung).
**Corrected ARA:** 1.000000 for both, across all pump regimes.
**Method:** Optical Bloch equations for a resonant two-level atom.

**Peer review notes:** The ARA = 1.0 result is correct but potentially uninteresting for the framework. A two-level atom driven at resonance is symmetric by construction — the Rabi oscillation has equal time above and below the equator of the Bloch sphere. The original error was meaningful (wrong rung), but the corrected value just confirms that a symmetric system has ARA = 1. This doesn't test the framework's predictive content; it only cleans up a bad entry.

### D. Galactic Rotation Phi Test — Honest Negative Result

**Result:** Phi is NOT supported as the ARA of galactic rotation.
**Measured:** κ/Ω ≈ 1.33-1.38, which is closer to √2 (flat rotation curve) than to φ (1.618).
**Action recommended:** Remove the galactic rotation MW entry as a measured phi node; replace carrier ARA with 1.0.

This is exactly the kind of honest self-falsification the repo needs more of. The test uses real Gaia DR3 Cepheid rotation-curve data, the methodology is transparent, and the conclusion is stated clearly. Well done.

### E. Galactic Structure Time-Phi Test — Plausible but Not Proven

The follow-up tests whether spiral-arm crossing geometry recovers phi. It finds the structure layer is "more phi-plausible" but depends on an assumed pattern speed of ~16.6 km/s/kpc. This sits within the literature range but is not independently constrained. The conclusion appropriately hedges: "plausible but unproven."

---

## III. Cross-Cutting Issues

### 1. Formula Complexity vs. Performance

The layered-sand series represents the most complex formula architecture yet: 5 sand layers + 2 upper layers, each with forward/lateral/twist spin vectors, contact transfer with wobble, recursive terrain reads, and upper compression. Despite this complexity, it performs *worse* than the much simpler Triangle Balance Universal at 12 and 24 months. This is a classic complexity trap: adding more physically-motivated moving parts doesn't help if the individual transfer functions (contact gain, speed ratio, terrain pull) aren't calibrated to the right scales.

**Recommendation:** Before adding more mechanical detail, establish that each layer's contribution can be independently validated. Does adding the floor layer measurably improve over starting from the fine layer? Does upper compression measurably improve over no upper pressure? These ablations are more valuable than the full 16-parameter search.

### 2. The Wobble Surface Remains Underappreciated

Across multiple test generations, the simple wobble surface analog (nearest-neighbour lookup on a local 3-axis wobble terrain) consistently outperforms the more theoretically elaborate models. At focus 6/12/24, wobble surface gets MAE 0.608 and corr +0.218, while the full layered-sand formula gets MAE 0.879 and corr +0.015. The wobble surface is doing something right — probably because it encodes actual historical outcomes rather than theoretically-derived terrain. Understanding *why* the wobble surface works should take priority over building more complex forward formulas.

### 3. Parameter Count Inflation

The formula models in this batch have progressively more free parameters: the topological formula alone tests 8 model variants with distinct terrain readers, rotation modes, phi-wobble clocks, saturation gates, and manual/wavecycle parameter sets. The parameter search has 16 continuous parameters with wide bounds. This makes overfitting increasingly likely and makes it harder to distinguish geometric signal from calibration artifacts.

### 4. Leakage Guards Remain Strong

Credit where due: every script in this batch maintains strict causal guards. The leakage_guard arrays in the output JSON are detailed and accurate. No script reads future data for prediction. This is consistently the strongest aspect of the codebase.

---

## IV. Verified Claims

| Claim | Status |
|---|---|
| U-238 catalog ARA was wrong due to half-life/period confusion | **Verified** — rerun confirmed ARA = 0.990 |
| Galactic rotation carrier is not phi | **Verified** — κ/Ω ≈ 1.33-1.38, closer to √2 |
| Layered sand formula is strict-causal | **Verified** — code review confirms no future data leakage |
| Na/H fluorescence ARA = 1.0 | **Verified** — symmetric by construction |
| Parameter search improves holdout amplitude | **Verified** — amplitude ratio 0.143 → 0.905 on holdout |
| Recursive grid MAE improves over persistence | **Verified** — rerun confirmed MAE improvements at 12/24 months |

## V. Flagged Issues

| Issue | Severity | Detail |
|---|---|---|
| Formula under-rolls severely (amp ratio 0.158) | High | The central mechanical claim — that contact pressure drives measurable roll — is not working at the current parameter scale |
| Formula h=12/24 correlation is negative | High | Predictions are directionally wrong on average at the horizons where the framework should add most value |
| 16-parameter fit with negative holdout corr at 6m/24m | Medium | Suggests the optimizer found a magnitude fix without a direction fix |
| Phi-wobble h=24 improvement needs null test | Medium | Golden-angle precession is purely temporal; the h=24 lift could be a seasonal artifact |
| U-238 classical trajectory in quantum system | Low | Should note this is a classical proxy for a quantum quasi-bound state |
| 45/234 atlas nodes still above ARA=2 | Low (improving) | The Over-2 Audit acknowledges this; 3 are now fixed, 42 remain |

---

## VI. Recommended Next Steps

1. **Ablate the layered-sand formula layer by layer.** Before more parameter searches, prove that each layer adds signal. Start with: floor-only, floor+fine, floor+fine+medium, etc.

2. **Investigate why wobble surface beats everything.** The wobble surface analog has been the quiet champion across multiple generations. Understanding its success could inform better forward formulas.

3. **Constrain the parameter search.** Instead of 16 free parameters with wide bounds, fix the physically-motivated ones (parity = -1, phi-based period ratios) and only search 3-4 scaling parameters.

4. **Run the phi-wobble h=24 against a non-phi temporal clock.** If a random or rational-angle precession produces similar h=24 improvement, the phi-wobble is capturing seasonal structure, not geometric truth.

5. **Continue the Over-2 recomputations.** The U-238 and fluorescence fixes are excellent. The remaining 42 above-2 nodes should be systematically recomputed, especially the extreme ones (mode-locked laser at 1.25×10⁵, Q-switched at 2×10⁴).
