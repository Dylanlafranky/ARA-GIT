"""
ARA BAND-HANDOFF predictor  (brown descends to its 0.25 floor, green rebounds up)
=================================================================================

Dylan (2026-05-29): the crests/troughs of the best forecast should sit ON the
brown/green metawave spine -- and the rebound is a HANDOFF, not a free spring.
Brown (the slow 0/singularity band) carries the system DOWN; as brown nears its
floor (the 0.25 ARA wall, i.e. brown deep in its own trough), GREEN (the fast
2/harmonic band) takes over and PULLS UP. That brown->green handoff at the floor
is the rebound mechanic.

Operationalised, strict-causal, on top of the gated two-band center:

  brown_comp(t), green_comp(t) : the causal projected oscillatory parts of each band
                                 (fit [1,t,green sins,brown sins] to past T[0..i]).
  floor_prox(t) = clip( (mean_past_brown - brown_comp(t)) / std_past_brown , 0, 3 )
                  -> how deep brown sits in its OWN trough (near the 0.25 floor).
  center        = trend + brown_comp + green_comp                  (the spine)
  REBOUND term  = floor_prox * green_comp   -> green's lift, amplified at brown's floor
  pred (low-moon) = center + b_eng*de + b_rech*dr + b_reb*(floor_prox*green_comp)
  pred (high-moon)= flat-climatology handoff (gate off)

If b_reb > 0 and it lifts skill over the plain two-band center, Dylan's handoff
mechanic is confirmed: green rebounds the system off brown's floor.

Strict causal: band fit on T[0..i]; brown mean/std from past only; handoff+rebound
betas fit on origins < CAL_SPLIT; held-out >= CAL_SPLIT. Correlation leads.

Usage: python3 ara_band_handoff.py nino34_long_anom.csv
"""

import sys
import numpy as np
import ara_pyramid_release_spring as M

CAL = M.CAL_SPLIT_YEAR
GREEN_MO = [27.9, 30.7]
BROWN_MO = [42.5, 54.0, 66.9]
NG = 2 * len(GREEN_MO)   # number of green sin/cos columns (after const+trend)


def design(t, periods, trend=True):
    cols = [np.ones_like(t)] + ([t] if trend else [])
    for P in periods:
        w = 2 * np.pi * t / P
        cols += [np.cos(w), np.sin(w)]
    return np.column_stack(cols)


def comps(t_scalar_arr, cob):
    """Split a design fit into trend, green_comp, brown_comp at given month indices."""
    D = design(t_scalar_arr, GREEN_MO + BROWN_MO)
    trend = D[:, :2] @ cob[:2]
    green = D[:, 2:2 + NG] @ cob[2:2 + NG]
    brown = D[:, 2 + NG:] @ cob[2 + NG:]
    return trend, green, brown


def walk(T, W, E, yr, mon):
    tmo = np.arange(len(T), dtype=float)
    rec = {h: {"eng": [], "rech": [], "truth": [], "clim": [], "center": [],
               "green": [], "floor": [], "oy": [], "tyr": [], "tpress": []}
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
        cob = np.linalg.lstsq(design(tmo[idx], GREEN_MO + BROWN_MO), T[idx], rcond=None)[0]
        # past brown stats for floor proximity (causal)
        _, _, brown_past = comps(tmo[idx], cob)
        bmu, bsd = brown_past.mean(), brown_past.std() + 1e-9
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
            tt = np.array([tmo[i + h]])
            tr_, gr_, br_ = comps(tt, cob)
            center = float(tr_[0] + gr_[0] + br_[0])
            floor = float(np.clip((bmu - br_[0]) / bsd, 0.0, 3.0))
            r = rec[h]
            r["eng"].append(eng); r["rech"].append(rech); r["truth"].append(T[i + h])
            r["clim"].append(clim); r["center"].append(center)
            r["green"].append(float(gr_[0])); r["floor"].append(floor)
            r.setdefault("brown", []).append(float(br_[0]))
            r.setdefault("trend", []).append(float(tr_[0]))
            r["oy"].append(yr[i]); r["tyr"].append(yr[i + h]); r["tpress"].append(M.pressure_proxy(yr[i + h]))
    return rec


def arr(rec, h):
    g = lambda k: np.array(rec[h][k])
    low = g("tpress") < 0
    return (g("eng"), g("rech"), g("clim"), g("truth"), g("center"),
            g("green"), g("floor"), g("oy"), g("tyr"), low)


def blend(eng, rech, clim, center, green, floor, low, truth, trn, rebound=True):
    de = eng - clim; dr = rech - clim
    eff = np.where(low, center, clim)          # gate: low-moon on spine, else flat
    reb = floor * green                         # green lift, amplified at brown floor
    dt = truth - eff
    pred = eff.copy(); binfo = {}
    for nm, reg in (("lo", low), ("hi", ~low)):
        fit = reg & trn
        if fit.sum() < 12:
            pred[reg] = eff[reg] + de[reg]; binfo[nm] = None; continue
        cols = [de[fit], dr[fit]]
        if rebound and nm == "lo":
            cols.append(reb[fit])
        A = np.column_stack(cols)
        co, *_ = np.linalg.lstsq(A, dt[fit], rcond=None)
        be = np.clip(co[0], 0.0, 1.5); br = np.clip(co[1], 0.0, 1.5)
        p = eff[reg] + be * de[reg] + br * dr[reg]
        if rebound and nm == "lo":
            breb = np.clip(co[2], -1.5, 1.5); p = p + breb * reb[reg]
            binfo[nm] = (be, br, breb)
        else:
            binfo[nm] = (be, br)
        pred[reg] = p
    return pred, binfo


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    M._dl("wwv_west.dat", "wwv_west.dat"); M._dl("wwv_east.dat", "wwv_east.dat")
    W = M.load_wwv("wwv_west.dat"); E = M.load_wwv("wwv_east.dat"); nino = M.load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys]); Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys]); mon = np.array([int(k[4:6]) for k in keys])
    rec = walk(T, Wv, Ev, yr, mon)

    print("ARA BAND-HANDOFF  (brown -> floor -> green rebound; gated to held-down regime)\n")
    print("Correlation. FULL = holdout 2017+;  LOW = 2017-2022 dead zone.  CORRELATION LEADS.\n")
    print(f"{'lead':>4} | {'hand FULL':>10} {'2band FULL':>10} {'reb FULL':>9}"
          f" | {'hand LOW':>9} {'2band LOW':>10} {'reb LOW':>8} | {'b_reb lo':>9}")
    for h in [6, 12, 18, 24, 30]:
        eng, rech, cl, tr, ctr, grn, flr, oy, tyr, low = arr(rec, h)
        trn = oy < CAL; tst = oy >= CAL
        hand = M.blend_handoff(eng, rech, cl, low, tr, trn)
        tb, _ = blend(eng, rech, cl, ctr, grn, flr, low, tr, trn, rebound=False)
        rb, bi = blend(eng, rech, cl, ctr, grn, flr, low, tr, trn, rebound=True)
        lw = tst & (tyr >= 2017) & (tyr < 2022)
        breb = bi["lo"][2] if (bi["lo"] and len(bi["lo"]) > 2) else float("nan")
        print(f"{h:>4} | {M.corr(hand[tst],tr[tst]):>+10.3f} {M.corr(tb[tst],tr[tst]):>+10.3f}"
              f" {M.corr(rb[tst],tr[tst]):>+9.3f} | {M.corr(hand[lw],tr[lw]):>+9.3f}"
              f" {M.corr(tb[lw],tr[lw]):>+10.3f} {M.corr(rb[lw],tr[lw]):>+8.3f} | {breb:>+9.2f}")

    print("\nCross-event block-CV (leave-one-block-out), pooled correlation:")
    print(f"{'lead':>4} {'handoff':>8} {'2band':>8} {'rebound':>9}")
    for h in [6, 12, 24, 30]:
        eng, rech, cl, tr, ctr, grn, flr, oy, tyr, low = arr(rec, h)
        edges = np.quantile(oy, [1/3, 2/3]); blk = np.digitize(oy, edges)
        ph = np.full(len(oy), np.nan); pt = np.full(len(oy), np.nan); pr = np.full(len(oy), np.nan)
        for b in range(3):
            te = blk == b
            if te.sum() < 12 or (~te).sum() < 24:
                continue
            ph[te] = M.blend_handoff(eng, rech, cl, low, tr, ~te)[te]
            pt[te] = blend(eng, rech, cl, ctr, grn, flr, low, tr, ~te, rebound=False)[0][te]
            pr[te] = blend(eng, rech, cl, ctr, grn, flr, low, tr, ~te, rebound=True)[0][te]
        print(f"{h:>4} {M.corr(ph,tr):>+8.3f} {M.corr(pt,tr):>+8.3f} {M.corr(pr,tr):>+9.3f}")
    print("\nRead: reb > 2band in the LOW window with b_reb>0 means green rebounding off brown's")
    print("floor is real -- the crest/trough handoff Dylan described, beyond the linear spine.")


if __name__ == "__main__":
    main()
