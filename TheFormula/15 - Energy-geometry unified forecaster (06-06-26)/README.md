# 15 — Energy-geometry unified forecaster (06-06-26)

**Thread:** "Energy and geometry are one measurement" — a unified three-output ENSO forecaster (value / direction / confidence) built on the reframe that geometry is *how we measure energy*. Dated 7 June 2026.

**Model logic / idea:** Energy and geometry are not two channels. The geometry is the way the energy is read: at short horizon the read is coherent (clear energy), as horizon grows it decoheres to the bare phase skeleton (the clock). So one quantity, measured well then poorly. Direction comes from energy (the warm-water-volume recharge reservoir leads SST) at short range and from geometry/phase at long range — they hand off **in time**. Energy should be injected into the correlation through its ARA (the **2−ARA** rule), not linearly.

**Systems tested:** ENSO/NINO3.4 (+ SOI/WWV/IOD, feeder era 1980+, test 2016–2025); cross-checks on heart and solar.

**What was tested:**
- `energy_determines_direction.py` — energy-only vs phase-clock direction hit-rate by horizon.
- `energy_ara_2minus_input.py` — inject energy via 2−ARA vs linearly vs base.
- Plot scripts for the geometry/energy split and the unified three-output forecaster.

**Key results:**
- **Energy calls direction short-range:** energy-only hit-rate 0.75 @3mo, beating the phase clock out to ~12mo; phase/geometry takes over at 18–24mo. They hand off in time (same split as the IOD-short/PDO-long stitch).
- **The 5–12mo geometry sag is a SURFACE spectral valley, filled by the SUBSURFACE reservoir.** The ENSO combination mode (×annual, ~9.6/17.8mo) is present but carries negligible energy — adding it did nothing. So the gap is a layer handoff: geometry reads the empty surface, energy reads the full subsurface (WWV).
- **2−ARA rule confirmed:** the ARA energy transform beats both base and linear at 5/6 horizons, decisively at h=9 where linear HURTS (0.297<0.309) but ARA HELPS (0.316). Gains small (~+0.01–0.015) but consistent and interpretable.
- **Three-output forecaster:** VALUE (strong short, decays ~36mo), DIRECTION (energy-clear short → geometry-skeleton long), CONFIDENCE (energy predicts the randomness envelope). Energy→confidence holds on heart (+0.21–0.29) but is weak on solar (~0, a concentrated clock with no spare energy) — it works exactly where the framework wins.
- Irreducible ARA-1.0 random core underneath all three outputs (same barrier as the lotto).

**What was NOT tested / open:** Gains are near-noise (~+0.01); the unified forecaster is ENSO-led with only short heart/solar cross-checks (heart series short, 526 beats). Not folded into the universal formula as a default here.

**Key files:**
- `ENERGY_GEOMETRY_UNIFIED_RESULT.md` — the full result and synthesis (headline doc).
- `energy_determines_direction.py`
- `energy_ara_2minus_input.py`
