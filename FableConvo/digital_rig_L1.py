"""
DIGITAL BENCH RIG L1 - circle map ground truth (REGISTERED 2 Jul 2026, pre-run)
================================================================================
Claim: the ARA lock-vs-handover dichotomy, and the kit's phase-step instrument,
correctly read the known locking structure of forced-oscillator physics.
Test: circle map theta_{n+1} = theta_n + Omega - (K/2pi) sin(2pi theta_n), K=0.9.
Sweep Omega across [0.580, 0.680] (covers 3/5, 1/phi, 5/8, approaches 2/3).
Measure winding number W; detect plateaus (locks) vs smooth channel (handover).
PREDICTIONS (ground truth known - this is instrument alignment, NOT new physics):
 P1: plateaus (dW/dOmega ~ 0) at 3/5 and 5/8; NO plateau at 1/phi = 0.6180.
 P2: pulling - Omega detuned slightly off 3/5 still yields W = exactly 0.600;
     Omega at 1/phi yields W tracking Omega (no snap).
 P3 (the coastline, quantified): tongue widths at convergents >> any width at phi.
FALSIFIER: a plateau containing 1/phi at this K, or no plateaus at convergents.
"""
import numpy as np

K = 0.9
def winding(Omega, n_trans=2000, n_meas=20000):
    th = 0.1
    for _ in range(n_trans):
        th = th + Omega - K/(2*np.pi)*np.sin(2*np.pi*th)
    th0 = th
    for _ in range(n_meas):
        th = th + Omega - K/(2*np.pi)*np.sin(2*np.pi*th)
    return (th - th0)/n_meas

PHI = (1+5**0.5)/2
targets = {"3/5 = 0.600": 0.600, "1/phi = 0.6180": 1/PHI, "5/8 = 0.625": 0.625,
           "8/13 = 0.6154": 8/13, "2/3 = 0.6667": 2/3}

print("P2 - PULLING TEST (detune by +/-0.004; does W snap or track?)")
print(f"{'drive Omega':<16}{'W measured':>12}{'W*360 fold':>12}  verdict")
for name, c in targets.items():
    for d in (-0.004, 0.0, 0.004):
        om = c + d
        W = winding(om)
        fold = min(W*360 % 360, 360 - (W*360 % 360))
        snap = "LOCKED (snapped)" if abs(W - c) < 1e-4 and abs(d) > 0 else (
               "on target" if d == 0 else "tracking (no lock)")
        print(f"{name+f' {d:+.3f}':<16}{W:>12.5f}{fold:>12.1f}  {snap}")
    print()

print("P1/P3 - PLATEAU SCAN (fine sweep; plateau = many Omegas, same W)")
oms = np.arange(0.580, 0.6801, 0.0004)
Ws = np.array([winding(o, 1500, 12000) for o in oms])
# plateau detection: group consecutive Omegas with identical W (to 4 decimals)
from itertools import groupby
plateaus = {}
for w, grp in groupby(zip(oms, np.round(Ws, 4)), key=lambda t: t[1]):
    g = list(grp)
    if len(g) >= 3:
        width = g[-1][0] - g[0][0]
        plateaus[w] = plateaus.get(w, 0) + width
top = sorted(plateaus.items(), key=lambda kv: -kv[1])[:6]
print(f"{'locked W':>10}{'tongue width':>14}  nearest landmark")
land = {0.6: "3/5", 0.625: "5/8", 2/3: "2/3", 8/13: "8/13", 0.6154: "8/13", 1/PHI: "1/phi"}
for w, width in top:
    near = min(land, key=lambda x: abs(x - w))
    print(f"{w:>10.4f}{width:>14.4f}  {land[near]} ({'MATCH' if abs(w-near)<5e-4 else 'off'})")
# is 1/phi inside any plateau?
Wg = winding(1/PHI)
in_plateau = any(abs(Wg - w) < 5e-5 and abs(1/PHI - w) < wd for w, wd in plateaus.items())
print(f"\n1/phi drive: W = {Wg:.5f} (Omega = {1/PHI:.5f}) -> "
      f"{'INSIDE a lock plateau (FALSIFIES)' if in_plateau else 'tracks Omega, NO lock: the open channel'}")
print(f"fold check: W*360 folded = {min(Wg*360%360, 360-Wg*360%360):.1f} deg "
      f"(golden angle 137.5)")
print(f"\nFOLD AMBIGUITY NOTE: 5/8 lock folds to {min(0.625*360%360,360-0.625*360%360):.1f} deg - "
      f"only ~2.5 deg from golden 137.5!")
