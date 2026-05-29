"""
ARA BROWN-CENTER predictor  (don't revert to a flat line -- revert to the heartbeat)
====================================================================================

Dylan (2026-05-29): the brown low-frequency band IS the Pacific's own time cycle
(the ~3-7yr recharge sloshing). So the forecast should not fall back to a FLAT
climatology mean -- it should fall back to the BROWN WAVE. Map the engine/recharge
ups-and-downs on top of a moving center that rides brown.

  center(origin, h)  = past-only mean + brown band PROJECTED to the target month.
  pred               = center + b_eng*(eng-clim) + b_rech*(rech-clim)   (per regime)

CAUSAL brown projection: at each origin i, fit [1, t, and cos/sin at the brown
periods 42/54/67 mo] to the PAST anomaly T[0..i] by least squares, evaluate the
fit at i+h. No future data. This is the honest test of Dylan's "center on the
heartbeat" idea -- the descriptive full-record overlay already lined up (-0.65 at
24mo); the question is whether the CAUSAL projection beats the flat line.

Strict causal: brown sinusoid amplitudes fit on T[0..i] only; handoff betas fit on
origins < CAL_SPLIT; held-out origins >= CAL_SPLIT. Correlation leads. Reported on
the full holdout, the 2017-2022 dead zone, and cross-event block-CV.

Usage: python3 ara_brown_center.py nino34_long_anom.csv
"""

import sys
import numpy as np
import ara_pyramid_release_spring as M
import ara_pyramid_hold_geometry as H

CAL = M.CAL_SPLIT_YEAR
BROWN_PERIODS_MO = [42.0, 54.0, 67.0]   # brown LF band, in months


def brown_design(t_months):
    cols = [np.ones_like(t_months), t_months]
    for P in BROWN_PERIODS_MO:
        w = 2 * np.pi * t_months / P
        cols += [np.cos(w), np.sin(w)]
    return np.column_stack(cols)


def walk_brown(T, W, E, yr, mon):
    """Like H.walk but also stores a CAUSAL projected brown center per (origin, lead)."""
    tmo = np.arange(len(T), dtype=float)   # month index = time axis for sinusoids
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
        # CAUSAL brown center: fit low-freq sinusoids to PAST T only.
        Apast = brown_design(tmo[idx])
        cob, *_ = np.linalg.lstsq(Apast, T[idx], rcond=None)
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
            center = float(brown_design(np.array([tmo[i + h]])) @ cob)
            r = rec[h]
            r["eng"].append(eng); r["rech"].append(rech); r["truth"].append(T[i + h])
            r["clim"].append(clim); r["center"].append(center)
            r["oy"].append(yr[i]); r["tyr"].append(yr[i + h]); r["tpress"].append(M.pressure_proxy(yr[i + h]))
    return rec


def blend_browncenter(eng, rech, clim, center, low, truth, trn):
    """Same per-regime eng/rech trust as handoff, but anchored to the brown center."""
    de = eng - clim; dr = rech - clim; dt = truth - center
    pred = center.copy()
    for reg in (low, ~low):
        fit = reg & trn
        if fit.sum() < 12:
            pred[reg] = center[reg] + de[reg]; continue
        A = np.column_stack([de[fit], dr[fit]])
        co, *_ = np.linalg.lstsq(A, dt[fit], rcond=None)
        be = np.clip(co[0], 0.0, 1.5); br = np.clip(co[1], 0.0, 1.5)
        pred[reg] = center[reg] + be * de[reg] + br * dr[reg]
    return pred


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    M._dl("wwv_west.dat", "wwv_west.dat"); M._dl("wwv_east.dat", "wwv_east.dat")
    W = M.load_wwv("wwv_west.dat"); E = M.load_wwv("wwv_east.dat"); nino = M.load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys]); Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys]); mon = np.array([int(k[4:6]) for k in keys])
    rec = walk_brown(T, Wv, Ev, yr, mon)

    print("ARA BROWN-CENTER  (forecast reverts to the brown heartbeat, not a flat line)\n")
    print("Correlation. FULL = holdout 2017+;  LOW = 2017-2022 dead zone.  CORRELATION LEADS.\n")
    print(f"{'lead':>4} | {'hand FULL':>10} {'brownC FULL':>12} | {'hand LOW':>9} {'brownC LOW':>11}"
          f" | {'centerProj corr':>15}")
    for h in [6, 12, 18, 24, 30]:
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"]); cl = np.array(rec[h]["clim"])
        tr = np.array(rec[h]["truth"]); ctr = np.array(rec[h]["center"])
        oy = np.array(rec[h]["oy"]); tyr = np.array(rec[h]["tyr"]); low = np.array(rec[h]["tpress"]) < 0
        trn = oy < CAL; tst = oy >= CAL
        hand = M.blend_handoff(eng, rech, cl, low, tr, trn)
        bc = blend_browncenter(eng, rech, cl, ctr, low, tr, trn)
        lw = tst & (tyr >= 2017) & (tyr < 2022)
        cproj = M.corr(ctr[tst], tr[tst])   # does the causal brown center alone track truth?
        print(f"{h:>4} | {M.corr(hand[tst],tr[tst]):>+10.3f} {M.corr(bc[tst],tr[tst]):>+12.3f}"
              f" | {M.corr(hand[lw],tr[lw]):>+9.3f} {M.corr(bc[lw],tr[lw]):>+11.3f} | {cproj:>+15.3f}")

    print("\nCross-event block-CV (leave-one-block-out), pooled correlation:")
    print(f"{'lead':>4} {'handoff':>8} {'brownC':>8}")
    for h in [6, 12, 24, 30]:
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"]); cl = np.array(rec[h]["clim"])
        tr = np.array(rec[h]["truth"]); ctr = np.array(rec[h]["center"])
        oy = np.array(rec[h]["oy"]); low = np.array(rec[h]["tpress"]) < 0
        edges = np.quantile(oy, [1/3, 2/3]); blk = np.digitize(oy, edges)
        ph = np.full(len(oy), np.nan); pb = np.full(len(oy), np.nan)
        for b in range(3):
            te = blk == b
            if te.sum() < 12 or (~te).sum() < 24:
                continue
            ph[te] = M.blend_handoff(eng, rech, cl, low, tr, ~te)[te]
            pb[te] = blend_browncenter(eng, rech, cl, ctr, low, tr, ~te)[te]
        print(f"{h:>4} {M.corr(ph,tr):>+8.3f} {M.corr(pb,tr):>+8.3f}")
    print("\nRead: brownC > handoff means re-centering on the causal brown wave (not the flat")
    print("mean) helps. centerProj corr shows how far the projected heartbeat itself stays alive.")


if __name__ == "__main__":
    main()
