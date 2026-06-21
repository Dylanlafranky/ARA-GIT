# Peer Review Audit — GIT/ARA-GIT Repository

**Reviewer:** AI Peer Reviewer (Claude)
**Date:** 2026-06-20
**Scope:** All files and subfolders in `GIT/ARA-GIT/`
**Standard:** Nitpick and verify for correct or incorrect results

---

## Executive Summary

The repository is large (~2,300 files across 12+ subfolders) and represents an honest, ambitious, and sometimes messy open research notebook. The self-correction discipline is unusually strong — negative results are documented, inflated numbers are caught and corrected, and multiple "scratched" branches are preserved for the record. However, the audit uncovered several critical issues that undermine specific headline claims and one foundational inconsistency in the ARA definition itself.

**Verdict:** The repo's honesty about failures is its strongest feature. Its biggest liabilities are (1) a sign error in the golden-stars "backbone" claim, (2) 52 scripts using zero-phase filtering that could contaminate prediction inputs, and (3) documentation gaps that obscure the folded-circle geometry for cold readers.

---

## RETRACTED Finding — ARA Convention (originally Critical #1)

**Status: RETRACTED after author review (2026-06-20)**

The original audit flagged an apparent inconsistency between `HOW_TO_map_a_system.md` (formula: ARA = T_acc / T_rel) and scripts using T_rel / T_acc (e.g., `neural_ara_test.py`). This was a reviewer error caused by reading the ARA scale as a linear number line rather than its actual structure.

Per `ARA_SCALE.md` (now added to the repo root): the 0–2 scale is a **symmetric folded circle**, not a line. 0→1 and 1→2 are the same thing mirrored. Direction/labels are swappable — only the relation between the two measured things matters. ARA is the relation between two opposing waves put on a number; orientation is chosen by physics so the result sits in [0, 2].

Under this geometry, T_acc/T_rel and T_rel/T_acc are the same relation read from opposite poles of the circle. The neural script using T_rel/T_acc for snap systems (placing them near pole 0) is not a broken convention — it is the correct orientation for fast-release systems. The HOW_TO's formula (T_acc/T_rel) and its interpretation table ("ARA < 1: release is shorter than accumulation") are both correct — the formula gives one orientation, and snap systems use the other, with the circle's flip-symmetry making them equivalent.

Values > 2 indicate a coupled pair (not a single system), which correctly reframes the over-2 audit: those nodes need orientation correction, rung reassignment, or compound-system decomposition — not a formula change.

**Remaining documentation recommendation:** `HOW_TO_map_a_system.md` should link to `ARA_SCALE.md` prominently at Step 4, so that external reviewers encounter the folded-circle geometry before misreading the formula as a flat linear definition. The theory is internally consistent; the on-ramp needs this document visible early.

---

## CRITICAL Findings (must fix before any public citation)

### 1. Golden Stars Correlation Sign Error

**Location:** `EnergyRatio/club_pop.py` line 40, `EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md` line 34, `CLAIMS_STATUS.md` line 292

The claim: `corr(|Px/P1O − 1/φ|, R21) = −0.347` is interpreted as "closer to φ = leaner."

The math: a negative correlation between distance-from-phi (X) and R21 (Y) means when X increases (further from phi), Y decreases (lower R21 = leaner). **Further from phi = leaner** — the opposite of the claim.

The code comment says `[negative => closer to 1/phi = leaner]` which is mathematically incorrect. The population-level 3.6% gap (p=0.016) is unaffected — RR0.61 stars as a class ARE leaner than ordinary RRc. But the "within-club dose-response gradient toward exact φ," described as "the strongest, least-confoundable part" and "the backbone" of the result, **points against the hypothesis**.

**Recommendation:** Re-examine the within-club correlation. If the sign is confirmed as −0.347, the RESULT.md and CLAIMS_STATUS must be corrected to note the gradient goes the wrong way. The population-level claim survives; the dose-response "backbone" does not.

### 2. CLAIMS_STATUS.md Is Truncated

**Location:** `CLAIMS_STATUS.md` line 305

The file ends mid-sentence: `- **Carrier to strip the stuck muon = octave-up (2×`

The Fusion Theory update (1 June 2026) is incomplete. Any claims in the missing tail are unauditable.

**Recommendation:** Restore the complete file from git history.

---

## HIGH-Priority Findings

### 3. sosfiltfilt in 52 Python Scripts

52 `.py` files use `sosfiltfilt` (zero-phase filtering), which is inherently acausal — it processes the signal forward AND backward, allowing future data to influence each filtered sample. When used on prediction inputs (not just descriptive measurement), this leaks future information.

Two scripts have already been rewritten to avoid it (`universal_cascade_v3.py` uses `lfilter`; `frozen_sphere_fractal_selfcontained_predictor.py` explicitly avoids filtfilt). The remaining 50 scripts using sosfiltfilt for prediction-related work need auditing to determine whether the filtering feeds into prediction targets or only descriptive/diagnostic outputs.

### 4. INDEX.md Has 36 Broken Links

36 of the `.md` files referenced in `INDEX.md` do not exist in the repository (e.g., `ARA_LAYERED_SAND_FULL_FORMULA_RESULT.md`, `ARA_MAPPING_ATLAS_RESULT.md`, `ARA_PHASE_FLOW_RESULT.md`). These appear to be from research branches that were removed without updating the index.

### 5. FRACTAL_UNIVERSE_THEORY.md — "Zero Failures" Contradicted Internally

The opening claims "zero prediction failures across 37 systems," but the same document reports Script 87 scored 6/10 and Script 93 scored 3/10. A later self-correction section acknowledges the GMM/unsupervised claim is overstated.

### 6. THE_FRAMEWORK_FORMULATION.md — Phi-Power vs. Octave Contradiction

The body states rung spacing is phi-powers, then a May 29 update corrects this to octave (x2) spacing, but the original phi-power table is left unedited. Both versions coexist in the same document. Two internal file paths are also wrong (`musings/` should be `journey/musings/`, `geometry-of-time/` should be `archive/misc_notes/`).

---

## MEDIUM-Priority Findings

### 7. 5 RESULT.md Files Have No Surviving Reproducible Script

- `ENERGY_GEOMETRY_UNIFIED_RESULT.md` — all scripts reference `/tmp/` scratch paths
- `MULTI_SYSTEM_PREDICTION_STACK_RESULT.md` — script at `/tmp/stack_predictions.py`
- `MAGNITUDE_LAG_AND_DECOMPOSITION_RESULT.md` — scripts attributed to wrong directory
- `RECOIL_ENERGY_PHITURN_STACK_RESULT.md` — references nonexistent `ara_prediction_formula.py`
- `ARA_CONCENTRATION_META_RULE_RESULT.md` — no standalone script

### 8. Retrodiction/ Has Zero Reproducible Evidence

All 8+ image references in result documents are broken (no PNG files committed). Plot scripts write to hardcoded dead session paths. The README is stale (lists 5 files that don't exist, omits 3 that do). All 5 scripts import from broken paths.

### 9. Gait Ratio Double-Counting in Significance Test

In `analysis/gait/significance_test.py`, measured gaitndd data gives stance/swing = 1.355 (16.3% from phi — a miss by the framework's own 5% criterion). The literature compilation gives ~1.597 (a hit). Both are counted as separate systems, inflating the phi-hit count. Additionally, the "Walk speed = 1.618" entry is an interpolated curve crossing, not a measured system ratio.

### 10. LLM Paper Skeleton's Central Experiment Was Falsified

`LLM/RESONANCE_IS_ALL_YOU_NEED_SKELETON.md` identifies closure-predicts-hallucination as the load-bearing experiment, but `LLM/LLM_CLOSURE_HALLUCINATION_RESULT.md` subsequently scratched this (3/4 model sizes showed confabulation with HIGHER closure). The skeleton has not been updated.

### 11. Missing EEG Data File

`Mapping/eeg_ara_test.py` requires `eeg_seg.npy` from PhysioNet slpdb, which is not in the repo. Results are saved in JSON but cannot be independently reproduced from the repo alone.

### 12. Solar Flywheel — "Dead On" Overstates 3.1% Deviation

`SOLAR_FLYWHEEL_RESULT.md` describes a rise fraction of 0.394 vs ideal phi-based 0.382 as "dead on." The 3.1% deviation is within interesting range but "dead on" is an overstatement for a framework that values precision.

---

## LOW-Priority Findings

### 13. MASTER_PREDICTION_LEDGER — Spearman rho = 1.000 Missing Sample Size

Prediction #9 (civilizational advancement) shows Spearman rho = 1.000 with no sample size stated. For n ≤ 5, perfect rank correlation is trivially achievable.

### 14. Wiki-Style Links in Markdown

`ENERGY_PER_CYCLE_LOGIC.md` and `ARA_Battery_Theory.md` use `[[wiki-style]]` links that don't resolve as standard markdown.

### 15. eval() in Atlas Builder

`Mapping/ara_mapping_atlas_build.py` uses `eval()` on line 155 to parse JS literals. Not a scientific error, but a security concern if ever run on untrusted input.

### 16. Cross-Document Redundancy

The ENSO 12m state predictor result appears in both `ARA_TICK_RECURSION_AND_COUPLING_RESULT.md` and `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md` without cross-referencing which is canonical.

### 17. Supporting Audit Corrections Not Applied

Three prior audit files in `Supporting/` correctly identify issues but the recommended corrections have mostly not been applied to source documents.

---

## Positive Findings (credit where due)

- **Zero LOO usage** across all 317+ scripts — consistent with project methodology.
- **Multiple negative/null results honestly reported** — the repo does not cherry-pick wins.
- **Self-corrections are documented inline** — inflated numbers are caught and revised, with the history preserved.
- **Rejected branches are kept** (complex-demodulation leak, filtfilt-inflated results, 3 turning-point nulls) rather than quietly deleted.
- **Train/test splits in audited prediction scripts are clean** — expanding window or phi-split, training strictly precedes test.
- **U-238 alpha computation is verified** — Woods-Saxon + Coulomb parameters match Krane textbook values, computed half-life matches known U-238 half-life (4.47 Gyr), action/π ≈ ℏ.
- **Fluorescence Bloch equations are correct** — Einstein A coefficients match NIST ASD for Na D-line and H Lyman-alpha.
- **The galactic rotation script correctly REJECTED a prior phi claim** based on actual rotation curve data — good scientific practice.
- **Claims hedging is generally appropriate** in CLAIMS_STATUS.md — the "Strongest Claims" vs "Claims To Soften" distinction is honest and useful.

---

## Summary by Area

| Area | Files Examined | Verified | Issues | Critical |
|---|---|---|---|---|
| Root documents | 15 | 8 clean | 36 broken links, 1 truncated, 1 phi-vs-octave coexistence | 1 (truncation) |
| CLAIMS_STATUS | 1 | Mostly honest | Truncated, golden-stars sign error propagated | 1 |
| TheFormula/ | ~77 RESULT.md, ~317 .py | ~11 clean | 5 missing scripts, ~50 filtfilt scripts | 0 |
| Mapping/ | 15 key files | 8 verified | ~~ARA convention~~ (RETRACTED), 26 boilerplate fixes | 0 |
| EnergyRatio/ | 22 | Population claim OK | Dose-response sign error | 1 |
| Retrodiction/ | 11 | Claims modest | Zero reproducible evidence | 0 |
| LLM/ | 68 | Self-correction strong | Paper skeleton stale | 0 |
| analysis/ | ~16 subdirs | Mixed | Gait double-counting, missing outputs | 0 |
| Supporting/ | 8 | Honest audits | Corrections not applied | 0 |

---

*This audit was conducted as a single-pass review, with one finding (ARA convention) retracted after author clarification revealed the reviewer had misread the folded-circle geometry as a linear scale. A full verification would require running all scripts against real data and comparing outputs to saved artifacts.*
