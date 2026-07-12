# Blood Glucose — a framework-faithful ARA reading

**Status:** real data, per-subject, honest. Replaces the undisciplined φ test in `analyze_cgm_phi.py` (now quarantined).
**Data:** Healthy = Big Ideas Lab Glycemic Variability (PhysioNet, n=16, Dexcom G6, mg/dL); T1D = D1NAMO (Zenodo 5651217, n=9, FreeStyle, mmol/L→mg/dL). 7/9 T1D usable (2 had too few clean cycles).
**Script:** `cgm_ara_run.py` · **Visual:** `cgm_ara_dashboard.html`

## Why re-run

The prior `analyze_cgm_phi.py` was **methodologically unfaithful** — not because it looked for φ (φ is a legitimate part of the framework, the time-handover, with real time-octave rungs), but because it tested φ **without the required discipline**: it fit a duration ratio (`T_fall/T_rise`) to φ with no declared handover, affirmed-the-null ("PASS within 5%"), pooled cycles (pseudoreplication), and skipped the actual ARA map. Per the operating rule — *φ is the time-handover, so it's allowed/expected in a genuine time ratio; we don't fit it blindly — we declare the handover, test with competing constants + a null, and either way understand the result* — this is the disciplined redo.

## Mapping (declared before measuring)

Boundary = one person's glucose regulation over the CGM record. Observable = CGM, 5-min. Opposed flows = appearance/absorption (rise) vs disposal/clearance (fall). **1.0 ridge** = fasting homeostasis (appearance ≈ disposal, level held). **Handover** = the rise→fall switch at each meal peak. **φ as a declared candidate:** `T_fall/T_rise` is a genuine time-handover ratio, so φ is a legitimate thing to expect here; predicted to appear in healthy (intact internal insulin handover) and degrade in T1D (broken/external handover).

## Results

**φ does NOT fall out (null).** Healthy per-subject median ratio = **1.405 (95% CI 1.19–1.47)** — the CI **excludes φ = 1.618**. Nearest round constant is **1.5** (dist 0.095) vs φ (0.213). The rise→fall pairing *is* structured (real ratio nearer φ than random re-pairing, p = 0.015), but its value isn't φ. Honest reading: the time-handover is real and coupled, but it sits at ~1.4, not φ — meal response is largely externally clocked and insulin kinetics set the ratio. The old "healthy ≈ φ" was an artifact of the undisciplined fit (here, on this externally-clocked ratio, φ simply isn't the value — which the framework's own rule anticipates).

**The handover ratio does NOT diagnose (prediction null).** Healthy vs T1D per-subject median ratios overlap: Mann-Whitney p = 0.87, Cliff's δ = −0.05. The framework's "T1D handover degrades the ratio" prediction fails — handover *timing* is not where diabetes shows.

**The homeostatic ridge DOES diagnose (holds, perfectly).** The "hidden behind apparent stillness" read separates the groups cleanly:

| metric | healthy (median) | T1D (median) | Cliff's δ | MW p |
|---|---|---|---|---|
| variability CV | 0.16 | 0.44 | **−1.0** | 0.0002 |
| time-in-range 70–180 | 98.6% | 60.1% | **+1.0** | 0.0002 |
| throughput (norm. flux) | 0.0176 | 0.0184 | −0.30 | 0.27 |

CV and time-in-range give **perfect separation** (δ = ±1.0). Healthy glucose is a tight 1.0-ridge held in range; T1D is the ridge failing.

**Refinement (honest):** the predicted "extra hidden throughput in healthy" nulled — flux is ~equal across groups. The difference is **containment**, not flux rate: both run similar throughput, but the healthy ridge keeps it inside a tight band (opposing flows cancel) while T1D loses containment (flows don't cancel → excursions).

## Honest fences

- The metrics that separate the groups (CV, time-in-range) are **standard CGM/diabetes measures**. ARA's ridge framing *recovers the correct diagnostic* and points at the right measurement — it does **not** beat clinical practice or find something standard metrics miss. This is consistency + correct measurement-selection, not a new discovery. (Same lesson as the driven pendulum.)
- n=16 healthy / 7–9 T1D; different sensors/cohorts (matched absolute detection: 10 mg/dL prominence, 15 mg/dL amplitude, applied identically after unit conversion).
- Research demonstration, **not** clinical or medical advice.

## Rung + coupling bore-in (map the area → find couplings → bore)

Octave-rung decomposition (normalised power) + cross-rung amplitude-envelope coupling, healthy vs T1D (`cgm_coupling_map.py`, `cgm_dashboard_data.py`):

- **Rung power (shape):** meal rung (4h) intact (0.318 vs 0.286, p=0.67); **fast rungs depleted in T1D** (1h 0.073→0.011, 2h 0.232→0.082, both p<0.0001); variance **collapses into the slow 8h rung** (0.363→0.629, p=0.0002).
- **Couplings that collapse:** every top healthy-minus-T1D coupling involves the **fast rung (0.5–1h) losing its cross-scale links** (0.5h↔8h +0.21→+0.03; 1h↔8h +0.28→+0.15; 0.5h↔2h +0.40→+0.28).
- **Bore-in:** the collapsed coupling wave is a rung **down** (fast ~1h feedback — lost both power and cross-scale coupling); the uncontained energy dumps a rung **up** (slow 8h drift); the meal rung sits intact between. Matches the prediction (fast endogenous feedback) and Dylan's "broken up or down" reframe.
- **Decomposition of the failure:** same corrections/day (4.8 vs 4.5, δ=0.2), same peak-slope/snap (1.15 vs 1.08, δ=−0.11); but ~2× amplitude (δ=−1.0), ~1.5× mean fall-rate (δ=−1.0), ~7× dwell above 180 (δ=−1.0). Same event, weaker holding.

Fences: 0.5h rung at CGM resolution floor; coupling reverse-inferred from glucose alone (no insulin channel); n=7 T1D; loss of fast-rung glucose regulation is likely known in the glucose-variability literature — this is the framework's procedure correctly locating the broken coupling, not a new physiological finding.

## Component bore-in — separating the parts of the change (D1NAMO insulin + food)

Added the real component channels (T1D). Raw event responses are confounded — meals and boluses are logged together, sparse (70 food / 75 insulin events). So **ARA deconvolution** (ridge FIR: glucose = conv(food, h_food) + conv(insulin, h_insulin)) was used to **separate the coincident waves by their differing kernels** (Dylan's idea):

- **Appearance (food):** rise peaking ~**1.4 h** (85 min), +2 mg/dL per 100 kcal.
- **Disposal (injected insulin):** fall reaching trough ~**3.4 h** (205 min), −2.8 mg/dL per unit.
- The two waves separate by ~**1.27 octaves**, with **disposal SLOWER than appearance**.

Reading: in T1D the disposal control (injected rapid-acting insulin) runs ~1.3 octaves *slower* than the appearance it must counter — **fast-in / slow-out mismatch** → glucose escapes the band. That's the ridge-failure mechanism, decomposed into its two component waves. Dylan's "separate them with ARA" worked. His "broken wave is a log *down*" refers to the healthy *fast endogenous* feedback (unmeasurable here); what's measurable in T1D is the slow external substitute, and the appearance/disposal *mismatch* is the finding.

Fences: fit R²≈0.02 (food+insulin explain only a small slice of glucose — basal/hepatic/activity/unlogged dominate), so kernel **shapes** are the takeaway, magnitudes soft; "calories" is a crude carb proxy; coincident events are collinear → regularized/partial separation; T1D-only; the healthy fast feedback stays inferred.

## Net

A clean "see what breaks" outcome: the φ candidate, tested with discipline, comes back **null on this ratio** (φ isn't there; ~1.4, CI excludes φ; ratio doesn't diagnose) — exactly the kind of "where φ should *not* appear" the rule asks us to allow. The framework-faithful **ridge map holds** — the diagnosis falls out of ridge containment (CV/TIR), exactly the "hidden behind apparent stillness" hypothesis — but via standard metrics, so the win is faithful mapping and correct measurement-pointing, not novelty.
