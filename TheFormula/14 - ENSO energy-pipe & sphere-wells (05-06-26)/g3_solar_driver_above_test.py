"""G3-A + SOLAR driver-above (clean 2:1 octave) — does a slow upper driver extend ENSO
predictability at the LONG year-marks (36-72mo), even if 18-24mo stays murky? (Dylan's call)
Strict-causal. Real NINO3.4 1870+ & SILSO monthly sunspots. Solar 133mo = 2:1 octave above
ENSO; octave phasor carried FORWARD to t+h (fixed period, train-safe) so it can reach long h.
Result mirrors /tmp run: solar adds ~nothing; 18-24 murky; 36-72 nudged from ~-0.04 to ~+0.04
(within noise); beyond 36mo ALL methods ~0 = genuine predictability floor.
"""
# (See /tmp/g3solar.py — identical logic; loaders for NINO + SILSO SN_m_tot.csv, build_self_system
#  ENSO P=48 horizons 3..72, baselines home_ar/lag-harmonic/stable-ARA/G3-A, solar fed as
#  trailing-mean level + cos/sin at 133mo & 66.5mo evaluated at t+h.)
