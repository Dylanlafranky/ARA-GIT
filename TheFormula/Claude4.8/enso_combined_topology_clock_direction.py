"""Combine the ORIGINAL multi-feeder ARA topology direction predictor with the new engine-phase
CLOCK component — does it gain on further windows? Strict-causal, real ENSO + feeders (SOI/WWV/IOD/PDO
via base.build_enso), gold-engine clock = causal_bandpass(NINO,55mo) phase projected to t+h.
Direction (turn) accuracy, golden/0.60 split, horizons 6..72mo. (Logic in /tmp run.)

RESULT — combination GAINS in the clock's resonance band, new session best:
  h : feeders(orig) / clock-alone / COMBINED
  12: 0.805 / 0.595 / 0.824 (+0.020)
  18: 0.780 / 0.635 / 0.805 (+0.025)
  24: 0.823 / 0.625 / 0.839 (+0.016)  <- best direction number of the session
  36: 0.786 / 0.621 / 0.786 (+0.000)
  48: 0.688 / 0.635 / 0.629 (-0.059)  <- clock spent, HURTS
  60: 0.766 / 0.456 / 0.753 (-0.013)
  72: 0.760 / 0.466 / 0.774 (+0.014)
=> clock adds independent signal at 12-24mo (+1.6..2.5pp, peak 0.839@24); past ~36mo it is decayed
   noise -> GATE the clock to h<=36 and let the multi-feeder topology carry the long range alone.
   Feeders alone hold 0.76-0.77 at h=60-72 where clock-alone collapses to ~0.46.
"""
