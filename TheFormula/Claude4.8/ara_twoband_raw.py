"""
ARA TWO-BAND RAW-ANCHOR predictor  (sharpen the near term toward the raw state)
==============================================================================

Dylan (2026-05-29): the gated spine forecast is smooth; the real NINO is jagger and
more dynamic. Most of the jaggedness is fast (<18mo) noise we rightly drop, BUT near
term we lean on the long-run structure when we should lean on the RAW current value.
So (the trick that worked on ECG): carry the raw gap forward and let it relax.

  anchor_resid = T[i] - center0(i)          # how far the RAW now sits off the spine
  decay(h)     = PHI ** (-(h-1)/TAU)         # full near, ~0 by long lead
  pred_raw(h)  = pred_gated(h) + decay(h)*anchor_resid

At h=1 the forecast starts at the raw current anomaly; by ~12mo decay->0 and it is
exactly the gated spine again -- so it smooths back out where the horizon is anyway.
Strict causal: T[i] and center0 are origin-time observables; decay is deterministic.
Correlation leads. Reported across SHORT leads to show where raw helps and where it fades.

Usage: python3 ara_twoband_raw.py nino34_long_anom.csv
"""

import sys
import numpy as np
import ara_pyramid_release_spring as M
import ara_twoband_center as C

CAL = M.CAL_SPLIT_YEAR
PHI = (1 + 5 ** 0.5) / 2


def walk_raw(T, W, E, yr, mon, periods):
    """C.walk plus the origin-time raw value t0 and the spine value at the origin center0."""
    tmo = np.arange(len(T), dtype=float)
    rec = {h: {"eng": [], "rech": [], "truth": [], "clim": [], "center": [],
               "t0": [], "center0": [], "oy": [], "tyr": [], "tpress": []}
           for h in range(1, M.HMAX + 1)}
    for i in range(len(T)):
        if yr[i] < M.WALK_START:
            continue
        idx = np.arange(0, i)
        if len(idx) < M.MIN_TRAIN:
            continue
        zW = (W - W[idx].mean()) / W[idx].std()
        zE = (E - E[idx].mean()) / E[idx].std()
        X = np.column_stack([T, zW, zE]); clim = T[idx].mean()
        cob = np.linalg.lstsq(C.design(tmo[idx], periods), T[idx], rcond=None)[0]
        center0 = float(C.design(np.array([tmo[i]]), periods)[0] @ cob)
        B = np.linalg.lstsq(M.seasonal_features(X[idx][:-1], mon[idx][:-1]), X[idx][1:], rcond=None)[0]
        for h in range(1, M.HMAX + 1):
            if i + h >= len(T):
                break
            x = X[i].copy()
            for kk in range(h):
                mm = ((mon[i] - 1 + kk) % 12) + 1
                x = M.seasonal_features(x[None, :], np.array([mm]))[0] @ B
            eng = x[0]
            past = idx[idx + h < i]
            if len(past) >= 60:
                A = np.column_stack([np.ones(len(past)), zW[past], zE[past]])
                co = np.linalg.lstsq(A, T[past + h], rcond=None)[0]
                rech = co[0] + co[1] * zW[i] + co[2] * zE[i]
            else:
                rech = clim
            center = float(C.design(np.array([tmo[i + h]]), periods)[0] @ cob)
            r = rec[h]
            r["eng"].append(eng); r["rech"].append(rech); r["truth"].append(T[i + h])
            r["clim"].append(clim); r["center"].append(center)
            r["t0"].append(T[i]); r["center0"].append(center0)
            r["oy"].append(yr[i]); r["tyr"].append(yr[i + h]); r["tpress"].append(M.pressure_proxy(yr[i + h]))
    return rec


def scores_raw(rec, h):
    a = lambda k: np.array(rec[h][k])
    return (a("eng"), a("rech"), a("clim"), a("truth"), a("center"),
            a("t0"), a("center0"), a("oy"), a("tyr"), a("tpress") < 0)


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    M._dl("wwv_west.dat", "wwv_west.dat"); M._dl("wwv_east.dat", "wwv_east.dat")
    W = M.load_wwv("wwv_west.dat"); E = M.load_wwv("wwv_east.dat"); nino = M.load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys]); Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys]); mon = np.array([int(k[4:6]) for k in keys])

    rec = walk_raw(T, Wv, Ev, yr, mon, C.GREEN_MO + C.BROWN_MO)

    print("ARA TWO-BAND RAW-ANCHOR  (decaying raw gap on top of the gated spine)\n")
    print("Correlation on holdout 2017+. base = gated spine; +raw = with decaying raw anchor.\n")
    for TAU in [PHI**3, PHI**4, PHI**5]:
        print(f"--- TAU = {TAU:.1f} mo (decay e-fold) ---")
        print(f"{'lead':>4} | {'base FULL':>10} {'+raw FULL':>10} | {'base ampl%':>10} {'+raw ampl%':>10}")
        for h in [1, 2, 3, 6, 9, 12, 18, 24, 30]:
            eng, rech, cl, tr, ctr, t0, c0, oy, tyr, low = scores_raw(rec, h)
            trn = oy < CAL; tst = oy >= CAL
            base = C.blend_gated(eng, rech, cl, ctr, low, tr, trn)
            decay = PHI ** (-(h - 1) / TAU)
            raw = base + decay * (t0 - c0)
            ar_b = base[tst].std() / tr[tst].std()
            ar_r = raw[tst].std() / tr[tst].std()
            print(f"{h:>4} | {M.corr(base[tst],tr[tst]):>+10.3f} {M.corr(raw[tst],tr[tst]):>+10.3f}"
                  f" | {ar_b:>10.0%} {ar_r:>10.0%}")
        print()

    print("Read: +raw should lift correlation AND amplitude at short lead, then converge")
    print("to base by ~12mo (decay->0). If it never helps, the raw gap carries no signal.")


if __name__ == "__main__":
    main()
