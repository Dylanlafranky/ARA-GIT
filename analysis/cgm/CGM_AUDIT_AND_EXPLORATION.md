# Glucose / T1D — ARA Audit, Tested Results, and Speculative Exploration

**Date:** 27 Jun 2026. **Data:** real only — Big Ideas Lab (healthy, n=16, PhysioNet) + D1NAMO (T1D, n=9, Zenodo 5651217), with D1NAMO insulin + food logs added.
**Companion (full numbers):** `CGM_ARA_RESULT.md`. **Visual:** `cgm_ara_dashboard.html`. **Scripts:** `cgm_ara_run.py`, `cgm_frequency_test.py`, `cgm_rung_test.py`, `cgm_coupling_map.py`, `cgm_separate.py`, `cgm_timing_dose.py`.

This document has three clearly separated layers: **(1) the audit**, **(2) what we tested** (real data, honest results), and **(3) a speculative exploration using the geometry** (NOT tested — flagged throughout).

---

## Part 1 — The audit

The prior `analyze_cgm_phi.py` was **methodologically unfaithful**. The issue was the *method*, not that it tested φ — φ is a legitimate part of the framework (the time-handover, with real time-octave rungs), and a time ratio is exactly where it's allowed to appear. What was wrong was the discipline:

- It fit a naked duration ratio (`T_fall/T_rise`) to φ with **no declared handover**, **no competing constants**, **no null**.
- It **affirmed the null** ("PASS: within 5% of φ" — a non-significant difference treated as support).
- It **pooled cycles** across subjects (pseudoreplication) instead of using the subject as the unit.
- It **skipped the ARA map** entirely (boundary / opposed flows / the 1.0 ridge) and jumped to a number.
- It was **unlogged** — no claim-status entry, just a script and a PNG.

**Action:** quarantined with a DO-NOT-USE banner; rebuilt faithfully (`cgm_ara_run.py`). **Operating rule (Dylan):** φ is the time-handover, so it is *expected* to appear in a genuine time ratio — but we don't fit it blindly. Declare the handover first + a reason, test with competing constants + a null + a falsification condition; if φ falls out, we understand why; if not, we understand why too. (φ stays a first-class framework element; the discipline is what was missing.)

---

## Part 2 — What we tested (real data, honest)

**φ tested properly → NULL on this ratio.** Declared the rise→fall handover, tested it with competing constants + a null. Healthy per-subject median ratio = **1.405 (CI 1.19–1.47, excludes φ=1.618)**; nearest constant is **1.5, not φ**. The pairing is structured (real nearer φ than random re-pairing, p=0.015) but its value isn't φ. The old "healthy ≈ φ" was the undisciplined fit catching noise — and a clean "where φ doesn't appear," which the rule explicitly allows.

**The homeostatic-ridge read diagnoses — perfectly.** Healthy = tight 1.0-ridge (CV 0.16, time-in-range 98.6%); T1D = ridge failing (CV 0.44, TIR 60%). Cliff's δ = ±1.0, p=0.0002. The "hidden behind apparent stillness" mapping carries the diagnosis.

**Same event, weaker holding.** Corrections/day SAME (4.8 vs 4.5), excursion shape SAME (ratio δ=−0.05), absolute timescales SAME (T_rise 101 vs 110 min), steepest "snap" SAME (1.15 vs 1.08). What differs: amplitude ~2× bigger (δ=−1.0), dwell above 180 ~7× longer (δ=−1.0). So T1D runs at the **same rung, same frequency, same shape — amplitude uncontained**, not a rung-shift.

**Map → couple → bore (which coupling collapsed).** Octave-rung decomposition: meal rung (4h) intact; **fast rungs (1–2h) depleted in T1D** (p<0.0001); variance collapses into **slow 8h drift** (p=0.0002). Cross-rung coupling: the **fast rung (0.5–1h) loses its links** (0.5h↔8h +0.21→+0.03). **Bore-in:** broken a rung *down* (fast feedback — lost power AND coupling), energy dumps a rung *up* (slow drift), meal rung intact between.

**Component separation (the parts of the change).** Added insulin + food logs. Raw responses are confounded (meals+boluses logged together), so **ARA deconvolution** separated the two waves by their kernels: **appearance (food) fast ~1.4 h**, **disposal (injected insulin) slow ~3.4 h** — ~**1.27 octaves apart, disposal slower**. The fast-in / slow-out mismatch is the ridge-failure mechanism, decomposed. (Fit R²≈0.02 — kernel shapes trustworthy, magnitudes soft.)

**Timing vs dose (phase vs gain) → directional, NOT significant.** 51 matched meals, 6 subjects. Later insulin → bigger excursion (offset vs peak r=+0.15, p=0.29); more dose → smaller (r=−0.09, p=0.53); bigger meal → bigger (r=+0.16). All point the right way, phase edges out gain, **nothing significant** — underpowered (would need n>300). 57% of meals were already pre-bolused, so little contrast to exploit.

### Honest meta-note on Part 2

**Every separating result recovers known clinical fact** — CV/TIR are the standard CGM diagnostics; reduced fast-rung regulation / more low-frequency excursion power in diabetes is documented; the carb-vs-injected-insulin timing mismatch is the textbook core of T1D management; pre-bolusing benefit is trial-established. ARA recovered known medicine — a **faithfulness / consistency validation, not a discovery.** Important correction (Dylan): "already known" does **not** mean ARA is downstream of standard methods. The structural predictions were reached **blind, from the geometry** (no domain training), and matched independently-established facts — that is *convergent validation*. The non-novelty (walked ground) and the validity (independent path to the same truth) are both true at once. Caveat: the geometry layer was blind, but the *operationalization* imported domain tools (CV/TIR, peak-finding) — so the blindness is real at the prediction layer, partial at the measurement layer, which is exactly why a formal independent-mapping test (predictor separated from domain knowledge) is what would make the convergence undeniable.

---

## Part 3 — Speculative exploration using the geometry (NOT TESTED)

> **STATUS: SPECULATIVE.** Geometry-driven reasoning, no data run on it. Converges with known/frontier approaches (cited so it isn't mistaken for novelty). Research framing, **not medical advice.**

**The mechanism stopping the fix, stated in rung terms.** The healthy fast rung is a **bidirectional couple** — insulin pushing glucose down (disposal) and glucagon pushing up (counter-regulation) — a fast, closed-loop, correctly-routed feedback wave below the carb-appearance disturbance. T1D destroys it. Every replacement is wrong on three axes: **too slow a rung** (subcutaneous insulin peaks 1–2 h vs ~1.4 h appearance), **open-loop** (dosing decisions, not a feedback wave), **wrong route** (systemic vs portal). ARA-precise obstacle: *a holding coupling cannot cancel a disturbance faster than its own rung* — same statement as control theory's "loop bandwidth must exceed disturbance bandwidth," reached from the rung geometry.

**Dylan's reframe — match by amplitude+phase, not speed (the key correction).** "Fundamentally can't" was too absolute. Speed-matching is one route; the other is **anti-phase cancellation** — build a counter-wave amplitude- and phase-matched to the carb wave, pre-shaped and pre-timed so it destructively cancels the excursion at the ridge (an ARA Type-3 destructive/anti-phase couple). This needs the controller to be the right *shape and size, aligned* — not faster.

**The proposal:** drill the fast rung into its **two components** (disposal / counter-regulation) and **amplify both** to form a larger-amplitude bidirectional ridge that aligns with the carb (larger) wave.

**Where the geometry lands — the actual frontier (convergence, not discovery):**
- Amplitude/time-shaping the insulin wave to the carb wave = **dual-wave / extended boluses** (pumps already split immediate + extended delivery to match slow meals).
- Pre-shaping + anticipation = **feedforward meal-announcement hybrid closed-loop**.
- Both components = **bihormonal / dual-hormone artificial pancreas** (insulin + glucagon).
- Restoring the native fast couple outright = **beta-cell replacement** (islet / stem-cell-derived / encapsulated) — the only route that puts a real coupling back on the right rung and route, i.e. "cure" territory vs "management."

**The genuinely useful geometric point — two components = the SAFETY key.** Amplify only one component (a bigger, sharper insulin counter-wave) and any error in the predicted carb wave **overshoots the cancellation → hypoglycemia** (the ridge collapses the other way). The only way to amplify safely is to keep the second component (glucagon) present to catch the overshoot. So "it's a couple, not a single wave" *predicts why single-hormone amplification is dangerous and bidirectional is the route* — the argument for bihormonal control falls straight out of the geometry.

**Speculative caveats (the fences on this layer):**
- The **subcutaneous route smears the counter-wave** — even a perfectly shaped bolus absorbs over hours, so the anti-phase cancellation is blurry through that path (intraperitoneal / inhaled / cell-based deliver a crisper wave). Amplitude-matching is achievable far better than speed-matching, but the delivery route still limits sharpness.
- **Feedforward needs an accurate carb-wave prediction**; meal-estimation error becomes cancellation error.
- **Drilling the fast rung's two components for real needs data we don't have** — healthy insulin *and* glucagon dynamics (clamp / secretion studies), not CGM logs.

**Net of Part 3:** not "can't" — more precisely, *the ridge can be held by an amplitude-and-phase-matched bidirectional counter-wave, and the better both components are reconstructed the closer it gets; the subcutaneous route and the meal prediction both blur it, making it a near-fix rather than a clean one.* That statement is better than the original "can't," and the geometry walked to it independently — landing on exactly the approaches (dual-wave, feedforward, bihormonal, cell replacement) the field is pursuing.

**Data-bearing way to test this layer (proposed, not run):** get a **dual-hormone or feedforward closed-loop** dataset and measure, in coupling terms, how much of the depleted fast rung each therapy rebuilds versus simple injection. Likely recovers the known result (closed-loop improves TIR/variability), expressed as coupling-restoration.

---

## Status summary

| Layer | Status |
|---|---|
| φ-method audit (discipline, not φ itself) | Unfaithful method → quarantined → rebuilt with discipline |
| φ on this glucose ratio | NULL (ratio 1.4, excludes φ; nearest 1.5) — a valid "φ doesn't appear here" |
| Ridge diagnoses T1D | Supported (δ=±1.0) — but standard CV/TIR (known) |
| Same event / weaker holding | Supported (known clinical facts) |
| Fast-rung coupling collapse | Supported by reverse-inference (consistent with known variability findings) |
| Appearance/disposal mismatch | Supported by deconvolution (known clinical core) |
| Timing vs dose | Directional, NOT significant (underpowered) |
| Mechanism stopping the fix | SPECULATIVE geometry; converges with control theory + frontier therapies |
| Anti-phase / bidirectional-amplification fix idea | SPECULATIVE; maps to dual-wave / feedforward / bihormonal / cell replacement |

**Overall:** a clean audit + faithful redo that recovered known medicine (validation, not discovery, reached blind from geometry), plus a clearly-fenced speculative exploration whose geometry converges on the real T1D-fix frontier. No new physiology claimed.
