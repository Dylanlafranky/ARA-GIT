"""
ARA pyramid HOLD-GEOMETRY predictor  (don't revert -- let the layered sand hold)
================================================================================

Dylan (2026-05-29): in the dampened-moon regime the engine REVERTS to climatology
and flattens the long troughs (the 2020-23 triple-dip La Nina: held down for years).
Don't let it revert. Let the geometry -- the layered sand -- hold the state. And a
system pressing it lower can add BACKSPIN, so the eventual release snaps harder.

So in the LOW-moon regime we add a HOLD layer: anchor the forecast to the current
held anomaly (persistence of t0) instead of letting it fall back to the mean. The
engine and recharge then stack on top as deltas; the release spring is the backspin.

  HOLD     : a*(t0 - clim)   -- t0 = apex anomaly AT the origin (observed, causal).
             a>0 means the trough is HELD, not reverted.
  ENGINE   : b_eng*(eng - clim)
  RECHARGE : b_rech*(rech - clim)
  SPRING   : b_rel * tens_z * relu(rech-clim)  -- backspin snap on release

  pred = clim + a*(t0-clim) + b_eng*de + b_rech*dr [+ spring]

Per-REGIME (low/high moon) coeffs fit causally on origins < CAL_SPLIT, applied >=.
The hold coefficient is free to differ by regime -- prediction: a(low) >> a(high).

Correlation leads. Reported on the full holdout AND the 2017-2022 low-moon window
(where all skill collapsed), plus cross-event block-CV.

Usage: python3 ara_pyramid_hold_geometry.py nino34_long_anom.csv
"""

import sys
import numpy as np
import ara_pyramid_release_spring as M

CAL = M.CAL_SPLIT_YEAR


def walk(T, W, E, yr, mon):
    """Same as release_spring walk_forward but also stores t0 = apex at origin."""
    rec = {h: {"eng": [], "rech": [], "truth": [], "clim": [], "tens": [], "t0": [],
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
        tens = 0.0; k = i
        while k >= 0 and T[k] < clim:
            tens += (clim - T[k]); k -= 1
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
            r = rec[h]
            r["eng"].append(eng); r["rech"].append(rech); r["truth"].append(T[i + h])
            r["clim"].append(clim); r["tens"].append(tens); r["t0"].append(T[i])
            r["oy"].append(yr[i]); r["tyr"].append(yr[i + h]); r["tpress"].append(M.pressure_proxy(yr[i + h]))
    return rec


def blend_hold(eng, rech, clim, t0, low, truth, trn, spring=False, tens=None):
    de = eng - clim; dr = rech - clim; dt = truth - clim
    hold = t0 - clim
    pred = clim.copy(); info = {}
    tz = M._tens_z(tens, trn) if spring else None
    up = np.clip(dr, 0.0, None) if spring else None
    for nm, reg in (("lo", low), ("hi", ~low)):
        fit = reg & trn
        if fit.sum() < 16:
            pred[reg] = clim[reg] + de[reg]; info[nm] = None; continue
        cols = [de[fit], dr[fit], hold[fit]]
        if spring:
            cols.append((tz * up)[fit])
        A = np.column_stack(cols)
        co, *_ = np.linalg.lstsq(A, dt[fit], rcond=None)
        be = np.clip(co[0], 0.0, 1.5); br = np.clip(co[1], 0.0, 1.5); a = np.clip(co[2], 0.0, 1.2)
        p = clim[reg] + be * de[reg] + br * dr[reg] + a * hold[reg]
        if spring:
            bl = np.clip(co[3], 0.0, 2.0); p = p + bl * (tz * up)[reg]
            info[nm] = (a, be, br, bl)
        else:
            info[nm] = (a, be, br)
        pred[reg] = p
    return pred, info


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    M._dl("wwv_west.dat", "wwv_west.dat"); M._dl("wwv_east.dat", "wwv_east.dat")
    W = M.load_wwv("wwv_west.dat"); E = M.load_wwv("wwv_east.dat"); nino = M.load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys]); Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys]); mon = np.array([int(k[4:6]) for k in keys])
    rec = walk(T, Wv, Ev, yr, mon)

    print("ARA HOLD-GEOMETRY PREDICTOR  (don't revert; let the layered sand hold)\n")
    print("Correlation. FULL = all holdout targets 2017+;  LOWMOON = 2017-2022 window.\n")
    print(f"{'lead':>4} | {'handoff FULL':>12} {'hold FULL':>10} {'hold+spr FULL':>13}"
          f" | {'handoff LOW':>11} {'hold LOW':>9} {'hold+spr LOW':>12} | {'a lo/hi':>9}")
    for h in [6, 12, 18, 24, 30]:
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"]); cl = np.array(rec[h]["clim"])
        tr = np.array(rec[h]["truth"]); t0 = np.array(rec[h]["t0"]); tn = np.array(rec[h]["tens"])
        oy = np.array(rec[h]["oy"]); tyr = np.array(rec[h]["tyr"]); low = np.array(rec[h]["tpress"]) < 0
        trn = oy < CAL; tst = oy >= CAL
        hand = M.blend_handoff(eng, rech, cl, low, tr, trn)
        hold, ih = blend_hold(eng, rech, cl, t0, low, tr, trn)
        hsp, _ = blend_hold(eng, rech, cl, t0, low, tr, trn, spring=True, tens=tn)
        lw = tst & (tyr >= 2017) & (tyr < 2022)
        a_lo = ih["lo"][0] if ih["lo"] else float("nan"); a_hi = ih["hi"][0] if ih["hi"] else float("nan")
        print(f"{h:>4} | {M.corr(hand[tst],tr[tst]):>+12.3f} {M.corr(hold[tst],tr[tst]):>+10.3f}"
              f" {M.corr(hsp[tst],tr[tst]):>+13.3f} | {M.corr(hand[lw],tr[lw]):>+11.3f}"
              f" {M.corr(hold[lw],tr[lw]):>+9.3f} {M.corr(hsp[lw],tr[lw]):>+12.3f} | {a_lo:.2f}/{a_hi:.2f}")

    print("\nCross-event block-CV (leave-one-block-out), pooled correlation:")
    print(f"{'lead':>4} {'handoff':>8} {'hold':>8} {'hold+spr':>9}")
    for h in [6, 12, 24, 30]:
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"]); cl = np.array(rec[h]["clim"])
        tr = np.array(rec[h]["truth"]); t0 = np.array(rec[h]["t0"]); tn = np.array(rec[h]["tens"])
        oy = np.array(rec[h]["oy"]); low = np.array(rec[h]["tpress"]) < 0
        edges = np.quantile(oy, [1/3, 2/3]); blk = np.digitize(oy, edges)
        ph = np.full(len(oy), np.nan); pH = np.full(len(oy), np.nan); pS = np.full(len(oy), np.nan)
        for b in range(3):
            te = blk == b
            if te.sum() < 12 or (~te).sum() < 24:
                continue
            ph[te] = M.blend_handoff(eng, rech, cl, low, tr, ~te)[te]
            pH[te] = blend_hold(eng, rech, cl, t0, low, tr, ~te)[0][te]
            pS[te] = blend_hold(eng, rech, cl, t0, low, tr, ~te, spring=True, tens=tn)[0][te]
        print(f"{h:>4} {M.corr(ph,tr):>+8.3f} {M.corr(pH,tr):>+8.3f} {M.corr(pS,tr):>+9.3f}")
    print("\nRead: if hold > handoff in the LOWMOON window (and a_lo high), not reverting --")
    print("letting the layered geometry hold the trough -- is what rescues the dampened regime.")


if __name__ == "__main__":
    main()
