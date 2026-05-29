"""
ARA pyramid PRESSURE — block robustness + wide placebo
=======================================================

The causal walk-forward (ara_pyramid_pressure_predictor.py) showed the lunar
PERIGEE pressure (~8.85 yr) lifting the recurrence rings on the 2016+ holdout,
and beating a 200-draw random-period placebo. But that holdout is ~10 yr and
dominated by ONE El Nino (2023-24). This script applies two harder tests:

1. LEAVE-ONE-BLOCK-OUT (LOBO). Split the forecast origins into 3 event-blocks by
   time. For each held-out block, fit the pressure coefficients on the OTHER two
   blocks and score correlation on the held block. The moon-period must transfer
   across DIFFERENT El Ninos, not just the last one. (This is k-fold cross-
   validation for robustness, not a causal forecast — the causal result is
   already established; here we ask whether the lunar signal generalises.)

2. WIDE PLACEBO. 300 random periods over a broad 4-16 yr band, scored with the
   same LOBO machinery, pooled over all blocks. p(random >= moon) at each lead.

Lower WALK_START to 2003 to use the full WWV record (PMEL starts 1980-01;
MIN_TRAIN=270 months puts the first origin ~2002.7).

Usage: python3 ara_pyramid_pressure_blocktest.py nino34_long_anom.csv
"""

import sys
import numpy as np
import ara_pyramid_pressure_predictor as M

M.WALK_START = 2003.0   # squeeze full record; first origin ~2002.7 with MIN_TRAIN=270
LEADS = [12, 15, 24, 27, 30]
PERIGEE_YR = 8.847


def build_rec(nino_csv):
    M._dl("wwv_west.dat", "wwv_west.dat"); M._dl("wwv_east.dat", "wwv_east.dat")
    W = M.load_wwv("wwv_west.dat"); E = M.load_wwv("wwv_east.dat")
    nino = M.load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys])
    Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys])
    mon = np.array([int(k[4:6]) for k in keys])
    return M.walk_forward_seasonal(T, Wv, Ev, yr, mon)


def basis(tyr, tmon, period):
    th = 2 * np.pi * (tmon - 1) / 12
    cols = [np.ones(len(tyr)), np.cos(th), np.sin(th)]
    if period is not None:
        ph = 2 * np.pi * tyr / period
        cols += [np.cos(ph), np.sin(ph)]
    return np.column_stack(cols)


def lobo_corr(rec, h, period, edges):
    """Leave-one-block-out calibrated correlation per block + pooled."""
    oy = np.array(rec[h]["oy"]); pr = np.array(rec[h]["pred"]); tr = np.array(rec[h]["truth"])
    cl = np.array(rec[h]["clim"]); tyr = np.array(rec[h]["tyr"]); tmon = np.array(rec[h]["tmon"])
    if len(oy) == 0:
        return None
    blk = np.digitize(oy, edges)            # 0,1,2 by origin year
    dpr = pr - cl; dtr = tr - cl
    P = basis(tyr, tmon, period)
    pooled_p = np.full(len(oy), np.nan)
    per_block = {}
    for b in range(3):
        test = blk == b; train = ~test
        if test.sum() < 12 or train.sum() < 24:
            continue
        A = P * dpr[:, None]
        coef, *_ = np.linalg.lstsq(A[train], dtr[train], rcond=None)
        beta = np.clip(P[test] @ coef, 0.0, 1.5)
        cal = cl[test] + beta * dpr[test]
        pooled_p[test] = cal
        per_block[b] = M.corr(cal, tr[test])
    pooled = M.corr(pooled_p, tr)
    raw_per = {b: M.corr(pr[blk == b], tr[blk == b]) for b in range(3) if (blk == b).sum() >= 12}
    return per_block, pooled, raw_per


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    rec = build_rec(nino_csv)
    # three roughly-equal event blocks by origin year
    oy_all = np.array(rec[12]["oy"])
    edges = np.quantile(oy_all, [1/3, 2/3])
    print(f"Origins span {oy_all.min():.1f}-{oy_all.max():.1f}; block edges at "
          f"{edges[0]:.1f}, {edges[1]:.1f} (3 blocks, leave-one-out CV)\n")

    print("=== LEAVE-ONE-BLOCK-OUT correlation (moon-perigee pressure vs raw seasonal) ===")
    print(f"{'lead':>4} | {'block0 raw/moon':>16} | {'block1 raw/moon':>16} | "
          f"{'block2 raw/moon':>16} | {'pooled raw/moon':>16}")
    for h in LEADS:
        pb, pooled, rawb = lobo_corr(rec, h, PERIGEE_YR, edges)
        # raw pooled corr
        oy = np.array(rec[h]["oy"]); pr = np.array(rec[h]["pred"]); tr = np.array(rec[h]["truth"])
        raw_pool = M.corr(pr, tr)
        def cell(b):
            r = rawb.get(b, float("nan")); m = pb.get(b, float("nan"))
            return f"{r:+.2f}/{m:+.2f}"
        print(f"{h:>4} | {cell(0):>16} | {cell(1):>16} | {cell(2):>16} | "
              f"{raw_pool:+.2f}/{pooled:+.2f}")

    print("\n=== WIDE PLACEBO (300 random periods, 4-16 yr, LOBO pooled corr) ===")
    rng = np.random.default_rng(0)
    periods = rng.uniform(4, 16, 300)
    print(f"{'lead':>4} {'rawPool':>8} {'moonPool':>9} {'placeboMean':>12} "
          f"{'placebo95':>10} {'p(rand>=moon)':>14}")
    for h in LEADS:
        _, moon_pool, _ = lobo_corr(rec, h, PERIGEE_YR, edges)
        oy = np.array(rec[h]["oy"]); pr = np.array(rec[h]["pred"]); tr = np.array(rec[h]["truth"])
        raw_pool = M.corr(pr, tr)
        pls = []
        for p in periods:
            r = lobo_corr(rec, h, p, edges)
            if r is not None:
                pls.append(r[1])
        pls = np.array([x for x in pls if not np.isnan(x)])
        p_better = float(np.mean(pls >= moon_pool))
        print(f"{h:>4} {raw_pool:>+8.3f} {moon_pool:>+9.3f} {pls.mean():>+12.3f} "
              f"{np.percentile(pls,95):>+10.3f} {p_better:>14.2f}")

    print("\nRead: moon must beat raw in >=2 of 3 blocks AND beat most placebos pooled.")
    print("If it only wins in the 2020s block, it is the 2023 El Nino talking, not the moon.")


if __name__ == "__main__":
    main()
