"""
TEST 7 — THE LOTTERY-TO-STAR LINE (fluctuation-dissipation across the atlas)
=============================================================================
PRE-REGISTERED (2 Jul 2026): the shed and the jitter are one door (FDT).
For each system: x-axis = per-cycle loss (the shed, 1 - floor(2)/floor(1));
y-axis = bath share (irreducible residual of the best strictly-causal memory
model = Mori-Zwanzig orthogonal part). PREDICTION: monotone increasing
(Spearman rho > 0 with p < 0.05 across the atlas). Endpoints already pinned by
prior repo results: fair lottery = all bath; golden stars = almost none.
FALSIFIER: flat or negative rank relation -> the interfering wave is NOT the
return current of the shed, and something stranger is in the forecasts.
This is the diamond/state-space plot: (position, variance) — first empirical
map of the four corners (lock/harmonic/silence/everything).
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_utils import read_series, cycle_floor, bath_share, dominant_period

# ---------------- CONFIG (edit me) ----------------
SERIES = {
    # "solar":  ("data/sn_monthly.csv", 12.0),
    # "star1":  ("data/kic5520878.csv", 48.9),
    # "enso":   ("data/nino34.csv",     12.0),
    # "pend2":  ("data/pend_arm2.csv",  50.0),
    # "lotto":  ("data/lotto_sums.csv",  1.0),   # the all-bath anchor
}
# ---------------------------------------------------

def main():
    if not SERIES:
        print("Fill SERIES in CONFIG."); return
    print(f"{'series':<12}{'floor1':>8}{'floor2':>8}{'shed':>8}{'bath':>8}")
    pts = []
    for sid, (path, fs) in SERIES.items():
        x = read_series(path)
        f0 = 1.0 / dominant_period(x, fs)
        f1 = cycle_floor(x, fs, 1, f0)
        f2 = cycle_floor(x, fs, 2, f0)
        shed = 1 - f2 / f1 if (np.isfinite(f1) and np.isfinite(f2) and f1 > 0.02) else 1.0
        shed = min(max(shed, 0.0), 1.0)
        bath = bath_share(x, fs)
        pts.append((sid, shed, bath))
        print(f"{sid:<12}{f1:>8.3f}{f2:>8.3f}{shed:>8.3f}{bath:>8.3f}")
    if len(pts) >= 4:
        from scipy.stats import spearmanr
        s = [p[1] for p in pts]; b = [p[2] for p in pts]
        rho, pval = spearmanr(s, b)
        print(f"\nSpearman(shed, bath) = {rho:+.3f}  (p = {pval:.4f}, n = {len(pts)})")
        print("PREDICTION ON RECORD: rho > 0 (big shed <-> big jitter).")
        print("Golden stars should be the quietest point; lottery the loudest.")
    else:
        print("\nNeed >= 4 systems for the rank test; add more to SERIES.")
    print("\nCaveat: 'temperature' differs across systems, so this is a RANK")
    print("prediction only; scatter is expected, monotonicity is the claim.")

if __name__ == "__main__":
    main()
