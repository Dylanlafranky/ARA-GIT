"""
TEST 5 - TUMBLING PENDULUM / SEPARATRIX CROSSING (FIVE_BEST_TARGETS target 5)
REGISTERED 3 Jul 2026 - header written BEFORE the tumbling ensemble was run.
==============================================================================
INSTRUMENT: simulation of the REAL Kaheman et al. double pendulum (Zenodo
10.5281/zenodo.6633719), using the archive's own identified parameters
(EstimatedParameters_DoublePendulum.mat) and its own published EOM
(DoublePendulumODE_Mounted.m, ported verbatim). Per the registration in
FIVE_BEST_TARGETS.md, simulation is legitimate for THIS target only: the
equations are exact known physics; ground truth is not in question.
VALIDATION GATE (must pass before predictions are scored): simulated free
swing from the real run's initial state must reproduce the device's damping
character (kit damping-angle, same order) and dominant period (within ~10%).

THE MAPPING UNDER TEST: the framework's 0/2 poles and the 1.0 ridge, placed
on the libration/rotation boundary. Hanging rest = lock pole; over-the-top
= the boundary landmark; libration = circle-side; rotation (winding phase)
= line-side; the separatrix = the ridge. Crossing = ridge transit.

PRE-REGISTERED PREDICTIONS (arm 2, absolute angle phi2):
 P1 CRITICAL SLOWING AT THE RIDGE: cycles containing a libration<->rotation
    transition are locally the SLOWEST - cycle period in the transition
    cycle exceeds the median of its +-5 neighbours (Wilcoxon across events,
    one-sided). The ideal-pendulum separatrix theorem says period diverges;
    the QUESTION is whether coupling/chaos in the double pendulum destroys
    this signature. If it survives, the ridge carries its time-dilation.
 P2 POLE STALL: transition cycles spend a larger fraction of their time
    near the inverted configuration (|wrap(phi2 - pi)| < 0.75 rad) than
    their +-5 neighbours (Wilcoxon, one-sided).
 P3 RIDGE APPROACH IS SLOW, NOT BALLISTIC: in the majority of final
    captures (rotation -> libration, no later re-escape), mean winding
    speed over the last 3 rotation turns decreases monotonically into the
    crossing. RIVAL: chaotic knockover - capture from full speed - i.e.
    the ridge is crossed ballistically and the pole story is decoration.
FALSIFIERS: P1/P2 null = the separatrix loses its slowing under coupling
(the 0/2 singularity story fails its exact referee); P3 rival majority =
crossings are kicks, not handovers.
CYCLE DEFINITION (uniform across regimes): boundaries at upward passes of
wrap(phi2) through 0 (dphi2 > 0): one boundary per libration period, one
per rotation turn.
ENSEMBLE: 24 runs, hanging start, dphi1_0 = 0, dphi2_0 sampled log-uniform
in [25, 45] rad/s (seed 42), 90 s each, RK45 rtol 1e-9. All crossings in
both directions are events.
"""
import numpy as np
from scipy.integrate import solve_ivp

# identified parameters, EstimatedParameters_DoublePendulum.mat (verbatim)
m1, m2 = 9.38439748e-02, 1.37595970e-01
a1, a2 = 1.08565215e-01, 1.16779018e-01
L1     = 1.72719204e-01
I1, I2 = 4.37529430e-04, 1.26882939e-03
k1, k2 = 2.37142783e-04, 1.00000019e-05
g      = 9.80858023e+00

def ode(t, y):
    p1, p2, d1, d2 = y
    c, s = np.cos(p1 - p2), np.sin(p1 - p2)
    den = (I1*I2 + L1**2*a2**2*m2**2 + I2*L1**2*m2 + I2*a1**2*m1
           + I1*a2**2*m2 - L1**2*a2**2*m2**2*c**2 + a1**2*a2**2*m1*m2)
    dd1 = -(I2*d1*k1 + I2*d1*k2 - I2*d2*k2 + a2**2*d1*k1*m2 + a2**2*d1*k2*m2
        - a2**2*d2*k2*m2 + L1*a2**3*d2**2*m2**2*s
        - (L1*a2**2*g*m2**2*np.sin(p1))/2 - I2*L1*g*m2*np.sin(p1)
        - (L1*a2**2*g*m2**2*np.sin(p1 - 2*p2))/2 - I2*a1*g*m1*np.sin(p1)
        + (L1**2*a2**2*d1**2*m2**2*np.sin(2*p1 - 2*p2))/2
        + L1*a2*d1*k2*m2*c - L1*a2*d2*k2*m2*c + I2*L1*a2*d2**2*m2*s
        - a1*a2**2*g*m1*m2*np.sin(p1)) / den
    dd2 = (I1*d1*k2 - I1*d2*k2 + L1**2*d1*k2*m2 - L1**2*d2*k2*m2
        + a1**2*d1*k2*m1 - a1**2*d2*k2*m1 + L1**3*a2*d1**2*m2**2*s
        + L1**2*a2*g*m2**2*np.sin(p2) + I1*a2*g*m2*np.sin(p2)
        + (L1**2*a2**2*d2**2*m2**2*np.sin(2*p1 - 2*p2))/2
        + L1*a2*d1*k1*m2*c + L1*a2*d1*k2*m2*c - L1*a2*d2*k2*m2*c
        - L1**2*a2*g*m2**2*c*np.sin(p1) + I1*L1*a2*d1**2*m2*s
        + a1**2*a2*g*m1*m2*np.sin(p2) + L1*a1**2*a2*d1**2*m1*m2*s
        - L1*a1*a2*g*m1*m2*c*np.sin(p1)) / den
    return [d1, d2, dd1, dd2]

def wrap(a): return (a + np.pi) % (2*np.pi) - np.pi

def simulate(y0, T, fs=500):
    t = np.arange(0, T, 1/fs)
    sol = solve_ivp(ode, (0, T), y0, t_eval=t, rtol=1e-9, atol=1e-11,
                    method="RK45", max_step=0.01)
    return sol.t, sol.y

def cycles_and_events(t, p2u):
    """Cycle boundaries: upward passes of wrap(p2) through 0. Returns per-cycle
    (t_start, period, winding_turns, stall_frac) and transition flags."""
    w = wrap(p2u); d = np.gradient(p2u, t)
    up = np.where((w[:-1] < 0) & (w[1:] >= 0) & (d[1:] > 0))[0]
    rows = []
    for i in range(len(up) - 1):
        s, e = up[i], up[i+1]
        turns = (p2u[e] - p2u[s]) / (2*np.pi)
        near_top = np.mean(np.abs(wrap(p2u[s:e] - np.pi)) < 0.75)
        rows.append([t[s], t[e]-t[s], turns, near_top])
    rows = np.array(rows)
    rot = np.abs(rows[:, 2]) > 0.5          # winding cycle vs bounded cycle
    trans = np.where(rot[:-1] != rot[1:])[0]  # boundary between cycle i,i+1
    return rows, rot, trans

# === CORRECTION (3 Jul, before re-scoring; original nulls RETRACTED) ========
# The archive's convention: theta = 0 is INVERTED, theta = +-pi is HANGING
# (proved by release test: y0 = 0.1 rad falls and tumbles; real free-swing
# data rests at -3.1404). First-pass detector had boundaries at the TOP and
# 'stall' measured at the BOTTOM. Corrected below; interval-based cycles now
# handle both winding directions (the first detector missed negative turns).
def intervals(t, p2u):
    """Bottom passes = wrap(p2 - pi) zero crossings (either direction).
    Interval class: |winding| > 4 rad => rotation turn (period = interval);
    else half-libration (period = 2 x interval). Returns rows
    [t0, period_est, turns, stall_frac_near_top, is_rot] and transitions."""
    w = wrap(p2u - np.pi)
    sign_flip = np.signbit(w[:-1]) != np.signbit(w[1:])
    genuine = np.abs(np.diff(w)) < np.pi        # exclude +-pi wrap jumps
    cross = np.where(sign_flip & genuine)[0]
    rows = []
    for i in range(len(cross) - 1):
        s, e = cross[i], cross[i+1]
        if e - s < 3: continue
        delta = p2u[e] - p2u[s]
        rot = abs(delta) > 4.0
        stall = np.mean(np.abs(wrap(p2u[s:e])) < 0.75)   # near TOP (theta=0)
        per = (t[e]-t[s]) if rot else 2*(t[e]-t[s])
        rows.append([t[s], per, delta/(2*np.pi), stall, float(rot)])
    rows = np.array(rows)
    rot = rows[:, 4].astype(bool)
    trans = np.where(rot[:-1] != rot[1:])[0]
    return rows, rot, trans

# single pendulum (uncoupled CONTROL - separatrix theorem exact here)
sa, sm, sI, sk, sg = 1.47754901e-01, 1.47584572e-01, 1.09118505e-04, 2.23940125e-04, 9.81001310e+00
def ode_single(t, y):
    return [y[1], (sa*sg*sm*np.sin(y[0]) - sk*y[1])/(sm*sa**2 + sI)]

# === MAIN: control -> ensemble -> scoring (self-contained, seed 42) =========
if __name__ == "__main__":
    # SELF-LOGGING (added after two empty output files on the user's machine):
    # everything printed, INCLUDING any crash traceback, is also written to
    # test5_results.txt in the current directory. Run plainly:
    #   python test5_tumbling_separatrix.py
    import sys, traceback
    class _Tee:
        def __init__(self, path):
            self.f = open(path, "w"); self.stdout = sys.stdout
        def write(self, x):
            self.f.write(x); self.f.flush(); self.stdout.write(x)
        def flush(self):
            self.f.flush(); self.stdout.flush()
    sys.stdout = sys.stderr = _Tee("test5_results.txt")
    try:
        from scipy.stats import wilcoxon
        try:
            from scipy.stats import binomtest
        except ImportError:                      # older scipy fallback
            from scipy.stats import binom_test
            class _BT:
                def __init__(self, p): self.pvalue = p
            def binomtest(k, n, p, alternative):
                return _BT(binom_test(k, n, p, alternative=alternative))
    except Exception:
        traceback.print_exc(); raise
    print("== CONTROL: single pendulum (theorem exact) ==")
    from scipy.integrate import solve_ivp as _si
    tt = np.arange(0, 120, 1/500)
    sol = _si(ode_single, (0,120), [np.pi, 25.0], t_eval=tt, rtol=1e-10, atol=1e-12)
    rows, rot, trans = intervals(sol.t, sol.y[0])
    i = trans[-1]
    print("periods into capture:", np.round(rows[max(0,i-4):i+3,1], 3))
    print("== ENSEMBLE: 24 x 90 s, dphi2_0 log-uniform [25,45], seed 42 ==")
    rng = np.random.default_rng(42)
    speeds = np.exp(rng.uniform(np.log(25), np.log(45), 24))
    runs = []
    for v in speeds:
        t, y = simulate([0.0, 0.0, 0.0, float(v)], 90, fs=500)
        runs.append(intervals(t, y[1]))
    dP, dS = [], []
    for rows, rot, trans in runs:
        P, S = rows[:,1], rows[:,3]
        for i in trans:
            lo, hi = max(0, i-5), min(len(P), i+7)
            nb, nbS = np.r_[P[lo:i], P[i+2:hi]], np.r_[S[lo:i], S[i+2:hi]]
            if len(nb) < 4: continue
            dP.append(np.mean(P[i:i+2]) - np.median(nb))
            dS.append(np.mean(S[i:i+2]) - np.median(nbS))
    dP, dS = np.array(dP), np.array(dS)
    print(f"P1 n={len(dP)} median dP {np.median(dP)*1000:+.0f} ms  p={wilcoxon(dP, alternative='greater').pvalue:.2e}")
    print(f"P2 n={len(dS)} median dS {np.median(dS):+.3f}    p={wilcoxon(dS, alternative='greater').pvalue:.2e}")
    slow = n = last_slowest = 0
    for rows, rot, trans in runs:   # EXPLORATORY version (see RESULTS doc)
        for i in trans:
            if rot[i] and not rot[i+1] and i >= 2 and rot[i-2] and rot[i-1]:
                p3 = rows[i-2:i+1, 1]; n += 1
                slow += (p3[0] < p3[1] < p3[2]); last_slowest += (p3[2] == p3.max())
    print(f"P3(exploratory) n={n} monotone {slow} last-slowest {last_slowest} "
          f"(chance 1/6, 1/3) p={binomtest(last_slowest, n, 1/3, 'greater').pvalue:.2f}")

    # (self-logging active; if you are reading a traceback above in
    # test5_results.txt, send that file back as-is.)
