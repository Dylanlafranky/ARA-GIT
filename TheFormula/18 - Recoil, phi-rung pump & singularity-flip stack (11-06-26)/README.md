# 18 — Recoil, phi-rung pump & singularity-flip stack (11-06-26)

**Thread:** Fixing the ENSO h=12 forecast — a φ-rung energy-pump upgrade, a recoil-spring + energy-sizing + φ-turn amplitude stack, the singularity-flip conjecture (used as a confidence layer), and three turning-point nulls. Dated 9–11 June 2026.

**Model logic / idea:** Forecast = geometry (engine-clock shape) + a self-correcting energy pump (the slower upstream reservoir, WWV, that leads the system), up-weighted by φ per φ-rung as the horizon climbs the φ-time-ladder, then capped at the decoherence wall (where the pump itself decoheres). On top: a recoil spring (equal-and-opposite restoring force), energy-sizing (swing size from loaded energy), and a φ-cycle turn (direction reverses every ~1.6 cycles) to fix amplitude. The singularity-flip conjecture: geometry inverts only when the trajectory laps a singularity (ARA → 0 or 2), like light through a pinhole — used as a coherence/confidence layer, not a value predictor.

**Systems tested:** ENSO/NINO3.4 (+ WWV) primarily; sunspots and QBO for the flip/coherence checks.

**What was tested:**
- φ-rung pump weighting `k(h)=φ^((h−h_coh)/T_rung)`, capped at the wall (`PHI_RUNG_PUMP_FORECAST_UPGRADE.md`).
- Recoil spring + energy-sizing + φ-turn stack (`RECOIL_ENERGY_PHITURN_STACK_RESULT.md`).
- Singularity-flip: per-rung phase-lock test, flip-at-energy-null test, coherence-preservation test, confidence layer (`SINGULARITY_FLIP_CONJECTURE.md`).
- Three turning-point fixes: anti-phase energy-brake, vertical-ARA fast-rung preview, 0.25/1.75 rails (`ENSO_TURNING_POINT_NULLS.md`).

**Key results:**
- **φ-rung pump:** ENSO h=12 geometry +0.278 → +0.340 (φ-rung-capped); mean gain over geometry doubles from +0.015 (fixed) to +0.034, biggest in the hard zone h=9–18, never worse than geometry. Universal recipe written (GEOMETRY + capped reservoir pump) but ENSO-validated only; T_rung/h_coh lightly tuned.
- **Recoil/energy/φ-turn stack:** the **amplitude fix is the real result** — at h=12 amp ratio walked 1.46 (overshoot) → 1.00 (dead on) while corr went +0.278 → +0.394. Recoil SIGN confirmed (negative = restoring spring, not a same-sign echo) but magnitude ≈1/φ not 1/φ³, and it acts as a prompt Hooke spring, not a delayed echo. φ-turn lands at ~28–30mo = 1.6×below-rung, BUT this also equals the engine half-cycle, so the φ reading isn't unique. D and T partly tuned on test (mild peek).
- **Singularity flip:** per-rung phase-lock is NULL; the singularity-gated version reconciles it (flip only on a 0/2 lap, so most rung steps don't flip). Flips DO sit at energy nulls (soft/geometric confirmation). The flip = coherence preservation for engines (transit→coherence-after: ENSO +0.72, sunspots +0.45/+0.53, QBO −0.21 the clean-clock exception). Used as a **confidence layer**: high-coherence third corr +0.479 vs low-coherence +0.354 (coherence predicts skill); direct value-incorporation HURT.
- **Three turning-point NULLS:** anti-phase energy-brake HURT (+0.340→+0.295, flipped ~49% of launches = coin toss); vertical-ARA fast-rung preview NO LEAD (fast/slow are anti-phase but *simultaneous*, −0.47 at lag 0; period ratio 3.9 not φ); 0.25/1.75 rails NOT the flip points (median flip-ARA ~1.17, scattered). Lesson: ENSO's energy is spread so no internal sub-rung leads the turn — only the external reservoir (WWV) genuinely leads.

**What was NOT tested / open:** Test the recoil-spring + φ-turn on a second system; separate "1.6 below-rung" from "engine half-cycle" with a system where those differ. The singularity-flip in its singularity-gated value form is still untested. Pump recipe not yet folded into the universal `ara_prediction_formula.py`.

**Key files:**
- `PHI_RUNG_PUMP_FORECAST_UPGRADE.md` — the universal pump recipe (headline).
- `RECOIL_ENERGY_PHITURN_STACK_RESULT.md` — the amplitude-fix stack.
- `SINGULARITY_FLIP_CONJECTURE.md` — the flip conjecture + confidence layer.
- `ENSO_TURNING_POINT_NULLS.md` — three recorded nulls (do-not-re-chase).
