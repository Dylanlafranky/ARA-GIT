"""
TEST 2 — THE LAG-SHAPE TEST (structure vs leak; supersedes constant-matching)
==============================================================================
PRE-REGISTERED (2 Jul 2026): a memoryless leak (the e-null) forces the recycling
floor to fall LOG-LINEARLY across lags (same fraction lost every cycle).
A return path (cross-rung recycling architecture) BENDS the curve away from
exponential (slower-than-exponential tail, possibly non-monotone).
  - straight line in log space  -> e wins: no geometry in the shed
  - upward bend / bent tail     -> return path exists: the geometry shows
WHY THIS BEATS CONSTANT-MATCHING: a one-parameter exponential family passes
through EVERY loss value as tau varies, so any single measured loss (0.374 etc.)
matches both 1/e and 2-phi within error. Shape discriminates where values can't.
INPUT: series listed in CONFIG. Suggested: solar sunspots, star light curves,
any long clean oscillator (avoid gated data here; run those on your side).
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_utils import read_series, cycle_floor, dominant_period

# ---------------- CONFIG (edit me) ----------------
SERIES = {
    # "solar": ("data/sn_monthly.csv", 12.0),   # (path, samples per unit time)
}
KMAX = 5
USE_ENVELOPE = False    # True to test envelope recycling instead of raw signal
N_BOOT = 500            # block bootstrap for the bend statistic
# ---------------------------------------------------

def bend_statistic(floors):
    """Fit log-linear to floors(k); return (slope, curvature) where curvature>0
    = slower-than-exponential tail (the geometry's signature)."""
    ks = np.arange(1, len(floors) + 1)
    lf = np.log(floors)
    lin = np.polyfit(ks, lf, 1)
    resid = lf - np.polyval(lin, ks)
    quad = np.polyfit(ks, lf, 2)[0]          # curvature term
    return lin[0], quad, resid

def main():
    if not SERIES:
        print("Fill SERIES in CONFIG."); return
    print(f"{'series':<12}{'floors k=1..' + str(KMAX):<42}{'ln-slope':>9}{'curv':>8}{'verdict':>22}")
    for sid, (path, fs) in SERIES.items():
        x = read_series(path)
        f0 = 1.0 / dominant_period(x, fs)
        floors = [cycle_floor(x, fs, k, f0, USE_ENVELOPE) for k in range(1, KMAX + 1)]
        floors = [f for f in floors if np.isfinite(f) and f > 0.01]
        if len(floors) < 3:
            print(f"{sid:<12} floors unusable (too leaky or short)"); continue
        slope, curv, _ = bend_statistic(np.array(floors))
        # block bootstrap the curvature: resample halves of the series
        curvs = []
        for _ in range(N_BOOT):
            i = np.random.randint(0, len(x) // 2)
            seg = x[i:i + len(x) // 2]
            fl = [cycle_floor(seg, fs, k, f0, USE_ENVELOPE) for k in range(1, KMAX + 1)]
            fl = [f for f in fl if np.isfinite(f) and f > 0.01]
            if len(fl) >= 3:
                curvs.append(bend_statistic(np.array(fl))[1])
        lo, hi = (np.percentile(curvs, [2.5, 97.5]) if curvs else (np.nan, np.nan))
        verdict = ("BENT (return path)" if lo > 0 else
                   "LOG-LINEAR (e-null)" if lo <= 0 <= hi else "bent DOWN (super-exp)")
        fstr = " ".join(f"{f:.3f}" for f in floors)
        print(f"{sid:<12}{fstr:<42}{slope:>9.3f}{curv:>8.3f}{verdict:>22}  (curv CI {lo:.3f}..{hi:.3f})")
    print("\nNote: per-cycle loss = 1 - floor(k+1)/floor(k); report loss alongside")
    print("BOTH constants (1/e=0.368, 2-phi=0.382) if quoting values at all.")

if __name__ == "__main__":
    main()
