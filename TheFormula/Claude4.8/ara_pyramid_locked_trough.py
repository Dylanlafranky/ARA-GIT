"""
ARA pyramid LOCKED-TROUGH predictor  (the handoff)
==================================================

Dylan's refinement (2026-05-29): when the moon's downward grip is weak, it does
not vanish -- it stays a weak PHASE reference -- but the two base grains
(warm-west, cool-east WWV) couple HARDER to each other. Measured on 1980+: the
warm<->cool coupling is +0.48 in the low-moon half vs +0.42 in the high-moon half
(p=0.002), and in that low-moon half the pair is TIGHT and CALM (smaller, slower
tilt). Tight+calm = constrained = predictable. So the trough should be forecast
from the warm<->cool LOCK, not flatlined and not free-breathed.

This model runs TWO strictly-causal component forecasts at every origin/lead:

  ENGINE   : seasonal three-body LIM apex forecast (carries the energetic spike).
  RECHARGE : apex predicted from the origin warm/cool tilt -- lead-h regression of
             T(t+h) on [zW(t), zE(t)] fit on past. Carries the slow locked mode.

They are blended by the deterministic moon phase, with per-lead, per-REGIME trust
learned causally (fit on origins < CAL_SPLIT, applied to >=):

  pred = clim + b_eng(regime,h)*(engine-clim) + b_rech(regime,h)*(rech-clim)
  regime = low-moon (pressure proxy < 0) vs high-moon (>= 0)

Prediction under Dylan's idea: in the LOW-moon regime b_rech is substantial (the
lock predicts the trough) while b_eng falls; in HIGH-moon b_eng carries the spike.

Strict causal: base grains standardized on past only; LIM, recharge regression and
all trust coefficients fit on past only; moon phase is deterministic ephemeris.
Correlation leads; block-CV for cross-event robustness.

Usage: python3 ara_pyramid_locked_trough.py nino34_long_anom.csv
"""

import os
import sys
import urllib.request
import numpy as np

PMEL = "https://www.pmel.noaa.gov/tao/wwv/data/"
WALK_START = 2003.0
MIN_TRAIN = 270
CAL_SPLIT_YEAR = 2016.0
HMAX = 30
PERIGEE_YR = 8.847
# fitted lunar pressure combo from the moon-pressure stage (b3 cos + b4 sin)
PB3, PB4 = 0.724, -1.366


def _dl(n, p):
    if not os.path.exists(p):
        urllib.request.urlretrieve(PMEL + n, p)


def load_wwv(p):
    d = {}
    for ln in open(p):
        s = ln.split()
        if len(s) == 3 and s[0].isdigit() and len(s[0]) == 6:
            d[s[0]] = float(s[2]) / 1e14
    return d


def load_nino(p, miss=-99.99):
    d = {}
    for ln in open(p):
        s = [x.strip() for x in ln.split(",")]
        if len(s) == 2 and s[0][:4].isdigit():
            v = float(s[1])
            if v > miss + 0.001:
                d[s[0][:7].replace("-", "")] = v
    return d


def seasonal_features(X, m):
    th = 2 * np.pi * (m - 1) / 12
    c, s = np.cos(th), np.sin(th)
    return np.column_stack([X, X * c[:, None], X * s[:, None], c, s, np.ones(len(X))])


def pressure_proxy(yr):
    ph = 2 * np.pi * yr / PERIGEE_YR
    return PB3 * np.cos(ph) + PB4 * np.sin(ph)


def walk_forward(T, W, E, yr, mon):
    """Past-only at every origin: store ENGINE and RECHARGE apex forecasts per lead."""
    rec = {h: {"eng": [], "rech": [], "truth": [], "clim": [],
               "oy": [], "tyr": [], "tmon": [], "tpress": []}
           for h in range(1, HMAX + 1)}
    for i in range(len(T)):
        if yr[i] < WALK_START:
            continue
        idx = np.arange(0, i)
        if len(idx) < MIN_TRAIN:
            continue
        zW = (W - W[idx].mean()) / W[idx].std()
        zE = (E - E[idx].mean()) / E[idx].std()
        X = np.column_stack([T, zW, zE])
        clim = T[idx].mean()
        B = np.linalg.lstsq(seasonal_features(X[idx][:-1], mon[idx][:-1]),
                            X[idx][1:], rcond=None)[0]
        for h in range(1, HMAX + 1):
            if i + h >= len(T):
                break
            # ENGINE: seasonal LIM rolled forward h steps
            x = X[i].copy()
            for kk in range(h):
                mm = ((mon[i] - 1 + kk) % 12) + 1
                x = seasonal_features(x[None, :], np.array([mm]))[0] @ B
            eng = x[0]
            # RECHARGE: lead-h regression of apex on origin tilt, fit on past pairs
            past = idx[idx + h < i]            # origins whose target is also in past
            if len(past) >= 60:
                A = np.column_stack([np.ones(len(past)), zW[past], zE[past]])
                co = np.linalg.lstsq(A, T[past + h], rcond=None)[0]
                rech = co[0] + co[1] * zW[i] + co[2] * zE[i]
            else:
                rech = clim
            rec[h]["eng"].append(eng); rec[h]["rech"].append(rech)
            rec[h]["truth"].append(T[i + h]); rec[h]["clim"].append(clim)
            rec[h]["oy"].append(yr[i]); rec[h]["tyr"].append(yr[i + h])
            rec[h]["tmon"].append(mon[i + h]); rec[h]["tpress"].append(pressure_proxy(yr[i + h]))
    return rec


def corr(a, b):
    a = np.asarray(a); b = np.asarray(b); m = ~np.isnan(a) & ~np.isnan(b)
    if m.sum() < 3:
        return float("nan")
    return float(np.corrcoef(a[m], b[m])[0, 1])


def skill(pred, truth, clim):
    pred = np.asarray(pred); m = ~np.isnan(pred)
    return 1 - np.mean((pred[m] - truth[m]) ** 2) / np.mean((clim[m] - truth[m]) ** 2)


def regime_blend(eng, rech, clim, lowmoon, truth, train_mask):
    """Fit per-regime trust on train_mask; return blended prediction for all samples."""
    de = eng - clim; dr = rech - clim; dt = truth - clim
    pred = clim.copy()
    for reg_mask in (lowmoon, ~lowmoon):
        fit = reg_mask & train_mask
        if fit.sum() < 12:
            apply = reg_mask
            pred[apply] = clim[apply] + de[apply]   # fallback: engine only
            continue
        A = np.column_stack([de[fit], dr[fit]])
        co, *_ = np.linalg.lstsq(A, dt[fit], rcond=None)
        be = np.clip(co[0], 0.0, 1.5); br = np.clip(co[1], 0.0, 1.5)
        pred[reg_mask] = clim[reg_mask] + be * de[reg_mask] + br * dr[reg_mask]
    return pred


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    _dl("wwv_west.dat", "wwv_west.dat"); _dl("wwv_east.dat", "wwv_east.dat")
    W = load_wwv("wwv_west.dat"); E = load_wwv("wwv_east.dat")
    nino = load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys])
    Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys])
    mon = np.array([int(k[4:6]) for k in keys])
    rec = walk_forward(T, Wv, Ev, yr, mon)

    print("ARA LOCKED-TROUGH PREDICTOR  (handoff: engine spike <-> recharge lock)\n")
    print(f"{'lead':>4} {'engineCorr':>11} {'blendCorr':>10} {'engineSkill':>12} {'blendSkill':>11}"
          f" {'b_eng lo/hi':>12} {'b_rech lo/hi':>13}")
    leads = [1, 3, 6, 9, 12, 15, 18, 24, 27, 30]
    for h in leads:
        if not rec[h]["truth"]:
            continue
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"])
        cl = np.array(rec[h]["clim"]); tr = np.array(rec[h]["truth"])
        oy = np.array(rec[h]["oy"]); pres = np.array(rec[h]["tpress"])
        low = pres < 0
        trn = oy < CAL_SPLIT_YEAR; tst = oy >= CAL_SPLIT_YEAR
        if tst.sum() < 20:
            continue
        blend = regime_blend(eng, rech, cl, low, tr, trn)
        # report regime betas (fit on train) for transparency
        de = eng - cl; dr = rech - cl; dt = tr - cl
        bt = {}
        for nm, rm in (("lo", low), ("hi", ~low)):
            f = rm & trn
            if f.sum() >= 12:
                co, *_ = np.linalg.lstsq(np.column_stack([de[f], dr[f]]), dt[f], rcond=None)
                bt[nm] = (np.clip(co[0], 0, 1.5), np.clip(co[1], 0, 1.5))
            else:
                bt[nm] = (float("nan"), float("nan"))
        print(f"{h:>4} {corr(eng[tst], tr[tst]):>+11.3f} {corr(blend[tst], tr[tst]):>+10.3f}"
              f" {skill(eng[tst], tr[tst], cl[tst]):>+12.3f} {skill(blend[tst], tr[tst], cl[tst]):>+11.3f}"
              f"   {bt['lo'][0]:.2f}/{bt['hi'][0]:.2f}    {bt['lo'][1]:.2f}/{bt['hi'][1]:.2f}")

    # cross-event block CV (leave-one-block-out), pooled corr
    print("\nCross-event block-CV (leave-one-block-out), pooled correlation:")
    print(f"{'lead':>4} {'engine':>8} {'blend':>8}")
    for h in [6, 12, 24, 27, 30]:
        if not rec[h]["truth"]:
            continue
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"])
        cl = np.array(rec[h]["clim"]); tr = np.array(rec[h]["truth"])
        oy = np.array(rec[h]["oy"]); pres = np.array(rec[h]["tpress"]); low = pres < 0
        edges = np.quantile(oy, [1/3, 2/3]); blk = np.digitize(oy, edges)
        pooled = np.full(len(oy), np.nan)
        for b in range(3):
            te = blk == b
            if te.sum() < 12 or (~te).sum() < 24:
                continue
            pooled[te] = regime_blend(eng, rech, cl, low, tr, ~te)[te]
        print(f"{h:>4} {corr(eng, tr):>+8.3f} {corr(pooled, tr):>+8.3f}")
    print("\nRead: blend > engine at the rings, and b_rech(lo) > b_rech(hi), means the")
    print("warm<->cool LOCK is doing the trough forecasting in the low-moon regime.")


if __name__ == "__main__":
    main()
