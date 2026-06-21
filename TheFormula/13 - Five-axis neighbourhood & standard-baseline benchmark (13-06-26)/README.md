# 13 — Five-axis neighbourhood & standard-baseline benchmark (13-06-26)

**Thread:** The honest benchmarking session — ARA vs strong local baselines across many systems, a five-axis "neighbourhood" ablation on ENSO, a multi-system prediction stack, and the energy-concentration meta-rule that explains the win/loss pattern. Dated 3–13 June 2026.

**Model logic / idea:** Stop comparing only to persistence; run ARA's layered operator against genuinely strong baselines (seasonal-naive, harmonic clock, lag+harmonic ridge, causal AR). The "five-axis neighbourhood" idea models a home sphere (NINO3.4) surrounded by a 5-axis × 2-direction × 3-depth lattice of contacts (SOI, WWV west/east, reservoir). The meta-rule: **ARA only beats the strong baselines when energy is SPREAD across coupled rungs (low concentration); when one wave dominates, a single-cycle clock already captures it and ARA ties.**

**Systems tested:** ENSO/NINO3.4 (+ SOI/WWV), QBO, solar sunspots, Arctic sea ice, influenza/ILINet, retail holiday cycle, CGM glucose (T1D), dengue, CO₂.

**What was tested:**
- `ara_forecast_standard_baseline_comparison.py` — ARA `home_plus_ara` vs 6 baselines on 34 system/horizon cells.
- `ara_enso_five_axis_neighbourhood_test.py` + `ara_five_axis_neighbourhood.py` — the 30-contact surrounding lattice on ENSO.
- `ara_g3_experimental.py` — geometry-native sandbox predictor (stable trio untouched).
- Multi-system stack runs (logic captured in `MULTI_SYSTEM_PREDICTION_STACK_RESULT.md`).

**Key results (honest):**
- **Standard-baseline benchmark:** ARA `home_plus_ara` beat the best local non-ARA baseline on correlation at only **6/34** horizons and on MAE at **8/34**. The real ARA-over-baseline wins are small ENSO lifts (e.g. +0.071 corr at h=12); sea ice, flu, retail, solar mostly become seasonal/lag/harmonic baseline wins once those controls are added. **Standard-baseline superiority is NOT established.**
- **Five-axis neighbourhood (ENSO):** best variant beat the best non-ARA correlation baseline at only 1/5 horizons (won h=3 +0.839); current wiring does not yet add enough over causal memory at long horizons.
- **Concentration meta-rule:** confirmed and monotonic across ENSO/QBO/solar — ENSO (band-conc 0.135, 1-mode R² 0.023) is the only real win (+0.071); QBO/Solar (concentrated, conc ~0.5) tie. The framework *predicts its own win/loss pattern*.
- **Multi-system stack:** strong phase-capture *vs persistence* (sea ice h=6 −0.92→+0.99; QBO h=12 −0.69→+0.73; flu h=26wk −0.33→+0.41; glucose +0.92 at 15min, fails past 30min where meal/insulin drivers take over). CO₂ trivial (persistence already ~0.99). These are persistence-inversion demos, not standard-baseline wins.

**What was NOT tested / open:** Operational archive benchmarks (SWPC panel, IRI/NMME/CFSv2, Sea Ice Outlook, FluSight WIS, OhioT1DM, PhysioNet) are all still pending — explicitly fenced as not done. Dengue and cancer-timing directions are scoped but data-blocked (need external drivers).

**Key files:**
- `ARA_FORECAST_STANDARD_BASELINE_COMPARISON_RESULT.md` — the 34-cell benchmark (headline honest result).
- `ARA_CONCENTRATION_META_RULE_RESULT.md` — when/why ARA beats the baseline.
- `ARA_ENSO_FIVE_AXIS_NEIGHBOURHOOD_RESULT.md` — the surrounding-lattice ablation.
- `MULTI_SYSTEM_PREDICTION_STACK_RESULT.md` — phase-capture-vs-persistence across 7 scales.
- `ara_forecast_standard_baseline_comparison.py`, `ara_g3_experimental.py`
