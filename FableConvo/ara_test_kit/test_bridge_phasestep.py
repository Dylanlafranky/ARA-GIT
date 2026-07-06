"""
THE BRIDGE TEST — handover phase-step per cycle (duty = arc fraction?)
=======================================================================
PRE-REGISTERED (2 Jul 2026): IF duty is the arc fraction of a golden handover
rotation, THEN in systems showing the golden duty, the between-band relative
phase must ADVANCE ~137.5 deg per dominant cycle (golden angle; the golden cut
splits the circle 0.382/0.618 and equidistribution turns arc into time-share
BY THEOREM). Rivals: 144 deg (pentagram/2-5 Fibonacci lock), 180 (anti-phase
lock), uniform/random (no handover structure at all).
OUTCOMES:
  step ~137.5 AND duty ~0.382 -> the bridge stands; phi rests on a theorem
  step ~144                    -> Fibonacci rational capture (lock, not golden)
  step random, duty still 0.39 -> duty has another cause; bridge wrong
INPUT: two-band systems. Bands via kit_utils.two_bands (transparent, simple);
substitute the canonical mapper's band split for authoritative runs.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scipy.signal import hilbert
from kit_utils import read_series, two_bands, bandpass, ANGLES

# ---------------- CONFIG (edit me) ----------------
SERIES = {
    # "qbo":   ("data/qbo_monthly.csv", 12.0),
    # "solar": ("data/sn_monthly.csv",  12.0),
}
# ---------------------------------------------------

def phase_step_deg(x, fs):
    """Relative phase advance (deg) of fast band vs slow band, per SLOW cycle."""
    fa, fb = two_bands(x, fs)              # fa = slow, fb = fast
    pa = np.unwrap(np.angle(hilbert(bandpass(x, fs, fa))))
    pb = np.unwrap(np.angle(hilbert(bandpass(x, fs, fb))))
    rel = pb - pa                          # relative phase (rad), unwrapped
    n_slow = (pa[-1] - pa[0]) / (2 * np.pi)
    if n_slow < 5:
        return np.nan, fa, fb, n_slow
    step = np.degrees((rel[-1] - rel[0]) / n_slow) % 360.0
    step = min(step, 360.0 - step)         # fold: 137.5 and 222.5 are one cut
    return step, fa, fb, n_slow

def main():
    if not SERIES:
        print("Fill SERIES in CONFIG."); return
    print(f"{'series':<12}{'f_slow':>10}{'f_fast':>10}{'cycles':>8}{'step(deg)':>11}  nearest")
    steps = []
    for sid, (path, fs) in SERIES.items():
        x = read_series(path)
        step, fa, fb, n = phase_step_deg(x, fs)
        if not np.isfinite(step):
            print(f"{sid:<12} too few slow cycles ({n:.1f})"); continue
        folded = {k: min(abs(step - v), abs(step - (360 - v))) for k, v in ANGLES.items()}
        nearest = min(folded, key=folded.get)
        steps.append(step)
        print(f"{sid:<12}{fa:>10.4f}{fb:>10.4f}{n:>8.1f}{step:>11.1f}  {nearest} ({folded[nearest]:.1f} off)")
    if steps:
        print(f"\nmedian step = {np.median(steps):.1f} deg  "
              f"(golden 137.5 | pentagram 144 | anti-phase 180)")
        print("Report the duty of the SAME systems alongside (test1) — the bridge")
        print("claim is the CONJUNCTION: golden step AND golden duty, together.")
    print("\nCaveat: step is sensitive to band selection; run with your canonical")
    print("decomposition as well and report both. If the two disagree, the band")
    print("split (not phi) is the live issue.")

if __name__ == "__main__":
    main()
