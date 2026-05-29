"""
ARA TWO-BAND CENTER predictor  (gated metawave floor: green+brown, phase-aligned)
=================================================================================

Dylan (2026-05-29): the moving center isn't brown alone -- it's the TWO-BAND
METAWAVE from the green/brown note: GREEN quasi-biennial (~28 mo) and BROWN
low-frequency (~42-67 mo), which the bispectrum showed are PHASE-COUPLED (b^2~0.34,
combination tone 15-20 mo). So project BOTH bands together -- preserving their
relative phase -- as the held-down floor, and GATE it to the low-moon regime where
the flat line fails. Normal (high-moon) times keep the flat climatology.

  center_lo(origin,h) = past-only [mean + trend + green sinusoids + brown sinusoids],
                        all fit jointly on T[0..i] (phase-aligned), evaluated at i+h.
  center_hi           = flat climatology (unchanged -> exactly the handoff there).
  pred                = center + b_eng*(eng-clim) + b_rech*(rech-clim)   per regime.

Strict causal: band amplitudes fit on T[0..i] only; handoff betas fit on origins
< CAL_SPLIT; held-out >= CAL_SPLIT. Correlation leads. Reported full holdout, the
2017-2022 dead zone, and cross-event block-CV. Compared to handoff and brown-only.

Usage: python3 ara_twoband_center.py nino34_long_anom.csv
"""

import sys
import numpy as np
import ara_pyramid_release_spring as M

CAL = M.CAL_SPLIT_YEAR
GREEN_MO = [27.9, 30.7]            # quasi-biennial band peaks
BROWN_MO = [42.5, 54.0, 66.9]     # low-frequency band peaks


def design(t, periods, trend=True):
    cols = [np.ones_like(t)] + ([t] if trend else [])
    for P in periods:
        w = 2 * np.pi * t / P
        cols += [np.cos(w), np.sin(w)]
    return np.column_stack(cols)


def walk(T, W, E, yr, mon, periods):
    """Walk-forward; store causal projected center using the given band periods."""
    tmo = np.arange(len(T), dtype=float)
    rec = {h: {"eng": [], "rech": [], "truth": [], "clim": [], "center": [],
               "oy": [], "tyr": [], "tpress": []} for h in range(1, M.HMAX + 1)}
    for i in range(len(T)):
        if yr[i] < M.WALK_START:
            continue
        idx = np.arange(0, i)
        if len(idx) < M.MIN_TRAIN:
            continue
        zW = (W - W[idx].mean()) / W[idx].std()
        zE = (E - E[idx].mean()) / E[idx].std()
        X = np.column_stack([T, zW, zE]); clim = T[idx].mean()
        cob = np.linalg.lstsq(design(tmo[idx], periods), T[idx], rcond=None)[0]
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
            center = float(design(np.array([tmo[i + h]]), periods) @ cob)
            r = rec[h]
            r["eng"].append(eng); r["rech"].append(rech); r["truth"].append(T[i + h])
            r["clim"].append(clim); r["center"].append(center)
            r["oy"].append(yr[i]); r["tyr"].append(yr[i + h]); r["tpress"].append(M.pressure_proxy(yr[i + h]))
    return rec


def blend_gated(eng, rech, clim, center, low, truth, trn):
    """Low-moon anchors to the metawave center; high-moon stays on the flat line."""
    de = eng - clim; dr = rech - clim
    eff_center = np.where(low, center, clim)
    dt = truth - eff_center
    pred = eff_center.copy()
    for reg in (low, ~low):
        fit = reg & trn
        if fit.sum() < 12:
            pred[reg] = eff_center[reg] + de[reg]; continue
        A = np.column_stack([de[fit], dr[fit]])
        co, *_ = np.linalg.lstsq(A, dt[fit], rcond=None)
        be = np.clip(co[0], 0.0, 1.5); br = np.clip(co[1], 0.0, 1.5)
        pred[reg] = eff_center[reg] + be * de[reg] + br * dr[reg]
    return pred


def scores(rec, h):
    eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"]); cl = np.array(rec[h]["clim"])
    tr = np.array(rec[h]["truth"]); ctr = np.array(rec[h]["center"])
    oy = np.array(rec[h]["oy"]); tyr = np.array(rec[h]["tyr"]); low = np.array(rec[h]["tpress"]) < 0
    return eng, rech, cl, tr, ctr, oy, tyr, low


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    M._dl("wwv_west.dat", "wwv_west.dat"); M._dl("wwv_east.dat", "wwv_east.dat")
    W = M.load_wwv("wwv_west.dat"); E = M.load_wwv("wwv_east.dat"); nino = M.load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys]); Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys]); mon = np.array([int(k[4:6]) for k in keys])

    rec_tb = walk(T, Wv, Ev, yr, mon, GREEN_MO + BROWN_MO)   # two-band metawave
    rec_br = walk(T, Wv, Ev, yr, mon, BROWN_MO)              # brown only (comparison)

    print("ARA TWO-BAND CENTER  (gated metawave floor: green+brown phase-aligned, low-moon only)\n")
    print("Correlation. FULL = holdout 2017+;  LOW = 2017-2022 dead zone.  CORRELATION LEADS.\n")
    print(f"{'lead':>4} | {'hand FULL':>10} {'2band FULL':>11} | {'hand LOW':>9} {'brownGate LOW':>13}"
          f" {'2bandGate LOW':>13} | {'2band ctrProj':>13}")
    for h in [6, 12, 18, 24, 30]:
        eng, rech, cl, tr, ctr, oy, tyr, low = scores(rec_tb, h)
        _, _, _, _, ctrb, _, _, _ = scores(rec_br, h)
        trn = oy < CAL; tst = oy >= CAL
        hand = M.blend_handoff(eng, rech, cl, low, tr, trn)
        g2 = blend_gated(eng, rech, cl, ctr, low, tr, trn)
        gb = blend_gated(eng, rech, cl, ctrb, low, tr, trn)
        lw = tst & (tyr >= 2017) & (tyr < 2022)
        print(f"{h:>4} | {M.corr(hand[tst],tr[tst]):>+10.3f} {M.corr(g2[tst],tr[tst]):>+11.3f}"
              f" | {M.corr(hand[lw],tr[lw]):>+9.3f} {M.corr(gb[lw],tr[lw]):>+13.3f}"
              f" {M.corr(g2[lw],tr[lw]):>+13.3f} | {M.corr(ctr[tst],tr[tst]):>+13.3f}")

    print("\nCross-event block-CV (leave-one-block-out), pooled correlation:")
    print(f"{'lead':>4} {'handoff':>8} {'2band':>8}")
    for h in [6, 12, 24, 30]:
        eng, rech, cl, tr, ctr, oy, tyr, low = scores(rec_tb, h)
        edges = np.quantile(oy, [1/3, 2/3]); blk = np.digitize(oy, edges)
        ph = np.full(len(oy), np.nan); pg = np.full(len(oy), np.nan)
        for b in range(3):
            te = blk == b
            if te.sum() < 12 or (~te).sum() < 24:
                continue
            ph[te] = M.blend_handoff(eng, rech, cl, low, tr, ~te)[te]
            pg[te] = blend_gated(eng, rech, cl, ctr, low, tr, ~te)[te]
        print(f"{h:>4} {M.corr(ph,tr):>+8.3f} {M.corr(pg,tr):>+8.3f}")
    print("\nRead: 2bandGate vs brownGate in the LOW window shows whether phase-aligning green")
    print("to brown (the coupled metawave) is a better held-down floor than brown alone.")


if __name__ == "__main__":
    main()
