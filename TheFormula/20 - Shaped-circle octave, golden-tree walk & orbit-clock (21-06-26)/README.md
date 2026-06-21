# 20 — Shaped-circle octave, golden-tree walk & orbit-clock (21-06-26)

**Thread:** Three explorations — octave ARA-shaped nested circles, the golden-tree walk as a fractal mapping technique, and the recognition that ENSO's stable clock is the annual orbit (spring = the pump). Dated 14 June 2026.

**Model logic / idea:**
- **Shaped circles:** rebuild the nested-circle predictor on the corrected octave (×2) spacing, with each rung a circle whose ARA both sizes (diameter) and shapes (asymmetric rise/fall loop) it.
- **Golden-tree walk:** draw the fractal as a recursive golden tree; each completed cycle steps and turns +36° if ARA>1, −36° if ARA<1, straight if ARA≈1 (36° = pentagon/golden angle). The accumulated path is the system's route — a state encoding from cumulative ARA-branch history. Works on every axis (horizontal = per-cycle in time, vertical = per-rung across the octave ladder).
- **Orbit-clock:** ENSO has no internal clock; it is paced by the external annual orbit, and boreal spring is its reset/pump (the spring predictability barrier).

**Systems tested:** ENSO/NINO3.4 (primary), solar sunspots (the regular-engine contrast); synthetic clock/engine/snap for the tree-walk validation.

**What was tested:**
- `ara_circle_predictor.py` (solar) / `ara_circle_enso.py` (ENSO) — cosine vs shape-only vs size×shape (varB) vs size-only (varA).
- `frozen_geometry.py` — freeze each rung's amp+shape+phase on the first 63%, roll forward blind (generative).
- `ara_golden_tree_walk.py` — the golden-tree mapping + curl-back → similar-data predictive tests.
- Orbit-clock / spring-pump tests on ENSO (logic in `ENSO_ORBIT_CLOCK_SPRING_PUMP_RESULT.md`).

**Key results:**
- **Shaped circles:** the ARA SHAPE helps on asymmetric ENSO (`shapeonly` beats plain cosine by +0.07/+0.10/+0.08 at h=6/12/18, beats persistence mid-long) — "asymmetric circle beats the perfect circle." But the ARA SIZE-weight HURTS (varB < shapeonly everywhere; varA dud) — amplitude is the diameter, ARA is only the shape. Kept mechanic: octave rungs + amplitude × ARA-shaped loop. Lift modest (~+0.08–0.10 over Fourier); solar (symmetric) gains nothing.
- **Frozen/generative:** solar runs blind for ~100 years (frozen at 1923, corr +0.31 rising to +0.49 far out — a regular engine stays in phase). ENSO FAILS frozen (−0.06, drifts) — no stable period to freeze; its shape-edge came from the rolling re-read, not frozen geometry.
- **Golden-tree walk:** validated as a MAPPING tool (clock→straight, engine→closed golden decagon, snap→mirror decagon, ENSO→meander). But as a PREDICTOR it is NULL: curl-back→similar-data did not hold (peak-diff 0.990 vs random 0.958, p=0.64); the amplitude-via-step-length fix did not rescue it (multi-rung analog forecast −0.10, worse than single-rung). Position encodes only timing-asymmetry history, not full state. **Do not re-chase as a predictor; keep as a signature/visualisation tool.**
- **Orbit-clock:** ENSO amplitude is phase-locked to the annual orbit (winter/spring variance ratio 1.70). Spring is the pump/barrier (persistence 0.78 starting Jul–Sep → 0.18 starting Jan–Mar). This resolves the rung-coupling null — the octave rungs don't lock to each other because they're all slaved to the external orbit; the clock grips at the EVENT level (Dec warm/cold peaks, p~1e-5), not at any single rung. Established ENSO science, but the framework reading pointed at the right structure. The wet-recoil-dampens-El-Niño hypothesis is NULL (corr 0.004; magnitude decoupled from prior recoil depth — though only SST recoil tested, not WWV recharge).

**What was NOT tested / open:** Confirm shapeonly > cosine on more asymmetric systems (ECG PQRST, QBO) and compare properly to home_ar/AR; tune the skew. The golden-tree walk's predictive direction is closed. The wet-recoil test rules out SST-recoil→amplitude, not WWV-recharge in general.

**Key files:**
- `ARA_SHAPED_CIRCLE_OCTAVE_RESULT.md` — shaped-circle result + frozen/generative test.
- `ARA_GOLDEN_TREE_WALK_RESULT.md` — golden-tree mapping (validated) and predictor (null).
- `ENSO_ORBIT_CLOCK_SPRING_PUMP_RESULT.md` — orbit = clock, spring = pump.
- `ara_circle_enso.py`, `ara_golden_tree_walk.py`, `frozen_geometry.py`
