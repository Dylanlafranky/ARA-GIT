"""
TEST 3 — THE MODAL-ANGLE RACE (the meta-rung: circle vs line)
==============================================================
PRE-REGISTERED CANDIDATES (2 Jul 2026), for the distribution of damping angles
(0 deg = pure oscillation/circle-axis, 90 deg = pure decay/line):
  ~0-1 deg : "engines fight toward the circle" (what the golden stars read)
  ~17 deg  : golden-spiral pitch, arctan(2*ln(phi)/pi) — the framework's own
             DERIVED horse (phi per quarter-turn, zero free choices)
  36 deg   : pentagon-shear conjecture (= 2/5 of the quarter-arc; parked)
  no structure: the null
RULE (falsifiability): the framework must sign ONE horse before running; a
framework that owns every outcome forfeits the race. Per session notes, its
truest horse is 17 deg; Dylan may override in writing here: SIGNED_HORSE = ___
INPUT: series in CONFIG spanning system classes. Angle is computed from the
per-cycle autocorrelation decay (see kit_utils.damping_angle_deg).
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_utils import read_series, damping_angle_deg, dominant_period

SIGNED_HORSE = None   # "0-1" | "17" | "36"  — sign BEFORE running on real data

# ---------------- CONFIG (edit me) ----------------
SERIES = {
    # "solar":   ("data/sn_monthly.csv", 12.0, "engine"),
    # "star1":   ("data/kic5520878.csv", 48.9, "engine"),
    # "pend1":   ("data/pend_arm2.csv",  50.0, "conservative"),
    # "noise":   ("data/lotto_sums.csv",  1.0, "bath"),
}
# ---------------------------------------------------

CANDS = {"circle-fight (~0-1)": 0.5, "golden pitch (17)": 17.03, "pentagon (36)": 36.0}

def main():
    if not SERIES:
        print("Fill SERIES in CONFIG. Sign the horse first."); return
    print(f"SIGNED_HORSE = {SIGNED_HORSE}")
    print(f"{'series':<12}{'class':<14}{'angle(deg)':>11}{'floors used':<30}")
    rows = []
    for sid, (path, fs, cls) in SERIES.items():
        x = read_series(path)
        ang, floors = damping_angle_deg(x, fs)
        rows.append((sid, cls, ang))
        fstr = " ".join(f"{f:.2f}" for f in floors)
        print(f"{sid:<12}{cls:<14}{ang:>11.2f}  [{fstr}]")
    angles = np.array([a for _, _, a in rows if np.isfinite(a)])
    if len(angles) >= 4:
        print(f"\nDistribution: n={len(angles)} median={np.median(angles):.1f} "
              f"IQR={np.percentile(angles,25):.1f}..{np.percentile(angles,75):.1f}")
        for name, c in CANDS.items():
            print(f"  median distance to {name:<22}: {abs(np.median(angles)-c):.1f} deg")
        eng = np.array([a for _, c, a in rows if c == "engine" and np.isfinite(a)])
        if len(eng):
            print(f"  ENGINE class median: {np.median(eng):.1f} deg "
                  f"(framework's engines-hug-the-axis reading predicts small)")
    print("\nCaveat: angle assumes light damping + a single dominant mode; for")
    print("multi-band systems decompose first (canon: measure the angle before")
    print("trusting any position taken in the borderlands).")

if __name__ == "__main__":
    main()
