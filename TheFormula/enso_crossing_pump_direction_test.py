"""ENSO green/gold crossing-pump as a DIRECTION/timing predictor (Dylan's idea). Strict-causal.
Four-role map (data-derived): annual 12mo=CLOCK, gold 40-70mo=ENGINE, green 28mo=SNAP, semiann=HARMONIC.
Pump: fire at green*gold constructive crossing -> fill gold engine toward 2.0 (=2sigma) -> phi-time
handover (PHI^(-h/Pgold)) carries it forward over horizon. Predict SIGN of NINO change, not value.

RESULT (real NINO3.4 1870+, golden split):
  Direction hit-rate WELL above chance at long leads (h=18 0.73, h=24 0.74; chance 0.50; persistence
  ~0.42 because ENSO mean-reverts) WHILE value corr stays ~0 (floored). => direction survives the
  value-floor. BUT control (pump fill OFF = plain gold-cycle projection) matches it exactly
  (h=24: 0.749 vs 0.736) => the crossing/2.0-fill/phi-handover add NOTHING; all skill is the gold
  engine's forward-projectable PHASE. Win = direction-predictability; null = the specific pump mechanism.
Logic in /tmp run; see ARA_G3_SPHERE_NATIVE_QBO_RESULT.md for the table.
"""
