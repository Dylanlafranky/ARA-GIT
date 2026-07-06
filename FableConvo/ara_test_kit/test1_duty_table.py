"""
TEST 1 — THE GOLDEN-DUTY TWO-COLUMN TABLE (the decisive phi experiment)
========================================================================
PRE-REGISTERED PREDICTIONS (on record 2 Jul 2026, before running):
  Column A (self-organizing engines, classified by the optimization-freedom rule
  BEFORE measuring): duty distribution peaks at 1/phi^2 = 0.382.
  Column B (dead matter / forced clocks / substrates): no golden peak.
  Competing constants reported ALWAYS: 1/e=0.368, 3/8=0.375, 1/phi^2=0.382, 2/5=0.400.
OUTCOME MEANINGS:
  peak at 0.382 -> golden non-locking handover reached (phi survives, decisively)
  peak at 0.400 or 0.375 -> Fibonacci-rung rational capture (lock, not golden)
  peak at 0.368 -> memoryless leak (no geometry)
  broad/no peak -> duty band was never a landmark
INPUT (choose one):
  (a) duties.csv with rows: id,class,duty   (class in {A,B}; duty in (0,1))
      -> produce this with YOUR canonical pipeline for gated-data systems.
  (b) a folder of series CSVs listed in SERIES below -> duty computed here
      (generic extractor; for canonical results use your ara_mapper instead).
Folding: duty d and 1-d are the same asymmetry (flip symmetry); we fold to
min(d, 1-d) so the golden target is 0.382 and symmetric systems sit at 0.5.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_utils import read_series, duty_fraction, CONSTANTS

# ---------------- CONFIG (edit me) ----------------
DUTIES_CSV = "duties.csv"          # option (a); set to None to use SERIES
SERIES = {                          # option (b): id: (path, fs, class)
    # "solar":  ("data/sn_monthly.csv", 12.0, "A"),   # per year
    # "qbo":    ("data/qbo_monthly.csv", 12.0, "A"),
    # "pend1":  ("data/pend_arm3.csv",  50.0, "B"),
}
N_BOOT = 2000
# ---------------------------------------------------

def load():
    rows = []
    if DUTIES_CSV and os.path.exists(DUTIES_CSV):
        for line in open(DUTIES_CSV):
            p = line.strip().split(",")
            if len(p) >= 3:
                try: rows.append((p[0], p[1].strip().upper(), float(p[2])))
                except ValueError: pass
    for sid, (path, fs, cls) in SERIES.items():
        d, n = duty_fraction(read_series(path), fs)
        if np.isfinite(d):
            rows.append((sid, cls, d)); print(f"  computed {sid}: duty={d:.4f} (n={n} cycles)")
    return rows

def kde_peak(vals, grid=None, bw=0.012):
    vals = np.asarray(vals)
    if grid is None: grid = np.linspace(0.25, 0.5, 501)
    dens = np.exp(-0.5*((grid[:,None]-vals[None,:])/bw)**2).sum(1)
    return grid[np.argmax(dens)], grid, dens/dens.max()

def main():
    rows = load()
    if not rows:
        print("No data. Fill DUTIES_CSV or SERIES in CONFIG."); return
    for cls in ("A", "B"):
        d = np.array([min(v, 1-v) for _, c, v in rows if c == cls])
        if len(d) == 0: print(f"\nColumn {cls}: (empty)"); continue
        peak, grid, dens = kde_peak(d)
        boots = [kde_peak(np.random.choice(d, len(d)))[0] for _ in range(N_BOOT)]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        print(f"\nColumn {cls}: n={len(d)}  mean={d.mean():.4f}  sd={d.std():.4f}")
        print(f"  KDE peak = {peak:.4f}  (bootstrap 95% CI {lo:.4f}..{hi:.4f})")
        print(f"  {'constant':<32}{'value':>8}{'|peak-c|':>10}{'inside CI?':>12}")
        for name, c in CONSTANTS.items():
            print(f"  {name:<32}{c:>8.4f}{abs(peak-c):>10.4f}{str(lo<=c<=hi):>12}")
        print(f"  symmetric 0.5 distance: {abs(peak-0.5):.4f}")
    print("\nVERDICT RULE: the winning constant must be inside the CI while its")
    print("rivals are outside; if several are inside, the sample cannot")
    print("discriminate (crowded neighborhood) -> report as such, do NOT pick phi.")

if __name__ == "__main__":
    main()
