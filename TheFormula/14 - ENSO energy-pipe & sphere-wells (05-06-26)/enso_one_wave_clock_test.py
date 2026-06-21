"""Test Dylan's unified one-wave CLOCK framing: treat ENSO as ONE wave; the side of the 1.0 line
(NINO centerline) you're on sets the drive direction, which holds until the next centerline crossing,
then flips. Phase/anti-phase = the two half-cycles of one clock. Does an explicit hold-until-crossing
predictor match/beat the symmetric engine-phase direction skill (~0.73 @18-24mo)? Strict-causal,
NINO3.4 1870+, gold engine = causal_bandpass(NINO,55mo). (Logic in /tmp run.)

RESULT — CONFIRMATION (not a new win):
 - Explicit crossing-clock reproduces engine-phase baseline EXACTLY: 100% identical direction calls at
   every horizon, same hit-rate (0.605/0.692/0.732/0.748/0.662/0.644 for h=6/12/18/24/36/48).
 - Reason: cos(phase) IS the clock — its sign = which side of centerline = drive direction; it holds
   until the projected phase passes a centerline crossing (cos sign-flip), then flips. So "one wave,
   side-of-line drives until next crossing" == the cosine phase projection. Validates the mental model.
 - Crossing intervals (half-cycles): mean 26.7mo, sd 7.2, CV 0.27 (= half the 55mo engine) -> fairly
   regular clock, why flip-timing holds to ~24mo then decays as timing errors accumulate.
 (First attempt underperformed only via mis-implementation: compared projection to current ENGINE
  value not current NINO, and dropped the slow level L.)
"""
