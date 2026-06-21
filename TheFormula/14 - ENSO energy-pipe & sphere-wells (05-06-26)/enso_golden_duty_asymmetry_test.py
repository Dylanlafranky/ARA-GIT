"""Test Dylan's golden-duty centerline asymmetry: ENSO crosses the 1-line and "goes the other way"
with ~0.618/0.382 (1/phi, 1/phi^2) split above/below rather than 50/50; does honoring the asymmetry
sharpen turn/direction calls vs the symmetric engine-phase (~0.73 @18-24mo)? Strict-causal, NINO3.4
1870+, gold engine = causal_bandpass(NINO,55mo). (Logic in /tmp run.)

RESULT — NOT supported:
 1) engine SYMMETRIC about centerline: time 0.510/0.490, amp/area 0.500/0.500, rise/fall 0.505/0.495,
    segment durs 27.3/26.1mo (0.511). Not 0.618/0.382. (Bandpass symmetrizes; raw NINO has known mild
    El Nino skew time-above~0.46 but amp-duty 0.50 -> mild skew, NOT golden.)
 2) free-fit duty scatters (0.575,0.550,0.350,0.325,0.400) -> no convergence on 1/phi or 1/phi^2.
 3) golden-duty phase warp lifts direction only ~+0.01-0.017 (within noise 2sigma~0.04); best-fit
    duty not golden. Symmetric engine-phase remains the keeper.
"""
