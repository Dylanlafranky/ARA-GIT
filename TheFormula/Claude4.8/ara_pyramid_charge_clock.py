"""
ARA pyramid CHARGE-CLOCK predictor  (the loaded spring)
=======================================================

Dylan's physics (2026-05-29): the trough is not just a quiet low -- it is a
SPRING LOADING. If the apex is held DOWN for an extended stretch (low-moon, weak
downward grip, the warm/cool pair recharging hard against each other), charge
ACCUMULATES. The longer it stays down, the more violent the next spike. Down ->
up is mandatory; a long down makes the comeback bigger.

So the recharge component should not just carry the slow locked mode -- its
rebound amplitude should GROW with how long/how deep the system has been charging.

This model runs the same TWO strictly-causal forecasts as the locked-trough handoff:

  ENGINE   : seasonal three-body LIM apex forecast (the energetic spike, timing).
  RECHARGE : apex predicted from origin warm/cool tilt -- lead-h regression of
             T(t+h) on [zW(t), zE(t)] fit on past pairs (the slow locked mode).

and adds a CHARGE CLOCK, computed from PAST-ONLY observed apex:

  charge(t) = decayed accumulation of time-and-depth spent BELOW climatology.
              charge[i] = DECAY*charge[i-1] + max(0, clim_i - T[i])

The blend lets the recharge rebound breathe with the charge: a charged spring
(long down) releases a bigger swing. Per-REGIME (low/high moon) trust fit causally
on origins < CAL_SPLIT, applied to >=:

  pred = clim + b_eng*(eng-clim) + b_rech*(rech-clim) + b_chg*charge_z*(rech-clim)

The charge interaction b_chg > 0 means: Dylan is right -- a longer/deeper down
loads a more violent rebound, and the locked recharge mode carries it.

Strict causal: base grains standardized on past only; LIM, recharge regression,
charge accumulation (backward-looking) and all trust coefficients fit on past
only; charge standardized on the training mask; moon phase is deterministic
ephemeris. Correlation leads; block-CV for cross-event robustness.

Usage: python3 ara_pyramid_charge_clock.py nino34_long_anom.csv
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
PB3, PB4 = 0.724, -1.366
CHARGE_DECAY = 0.90        # ~10-month e-fold memory of the loading spring


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
    """Past-only at every origin. Store ENGINE, RECHARGE, and CHARGE per lead."""
    rec = {h: {"eng": [], "rech": [], "truth": [], "clim": [], "charge": [],
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
        # CHARGE CLOCK: backward-looking accumulation of depth-below-clim up to i.
        # uses only T[0..i] -> strictly causal.
        chg = 0.0
        for j in range(i + 1):
            chg = CHARGE_DECAY * chg + max(0.0, clim - T[j])
        B = np.linalg.lstsq(seasonal_features(X[idx][:-1], mon[idx][:-1]),
                            X[idx][1:], rcond=None)[0]
        for h in range(1, HMAX + 1):
            if i + h >= len(T):
                break
            x = X[i].copy()
            for kk in range(h):
                mm = ((mon[i] - 1 + kk) % 12) + 1
                x = seasonal_features(x[None, :], np.array([mm]))[0] @ B
            eng = x[0]
            past = idx[idx + h < i]
            if len(past) >= 60:
                A = np.column_stack([np.ones(len(past)), zW[past], zE[past]])
                co = np.linalg.lstsq(A, T[past + h], rcond=None)[0]
                rech = co[0] + co[1] * zW[i] + co[2] * zE[i]
            else:
                rech = clim
            rec[h]["eng"].append(eng); rec[h]["rech"].append(rech)
            rec[h]["truth"].append(T[i + h]); rec[h]["clim"].append(clim)
            rec[h]["charge"].append(chg)
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


def std_on(charge, mask):
    """Standardize charge using ONLY the training mask stats (causal)."""
    mu = charge[mask].mean(); sd = charge[mask].std()
    if sd <= 0:
        return np.zeros_like(charge)
    return (charge - mu) / sd


def blend_handoff(eng, rech, clim, lowmoon, truth, train_mask):
    """Locked-trough handoff: per-regime [eng, rech] trust. No charge."""
    de = eng - clim; dr = rech - clim; dt = truth - clim
    pred = clim.copy()
    for reg in (lowmoon, ~lowmoon):
        fit = reg & train_mask
        if fit.sum() < 12:
            pred[reg] = clim[reg] + de[reg]
            continue
        A = np.column_stack([de[fit], dr[fit]])
        co, *_ = np.linalg.lstsq(A, dt[fit], rcond=None)
        be = np.clip(co[0], 0.0, 1.5); br = np.clip(co[1], 0.0, 1.5)
        pred[reg] = clim[reg] + be * de[reg] + br * dr[reg]
    return pred


def blend_charge(eng, rech, clim, lowmoon, charge, truth, train_mask):
    """Charge clock: recharge rebound breathes with the loaded spring.
    pred = clim + b_eng*de + b_rech*dr + b_chg*charge_z*dr (per regime)."""
    de = eng - clim; dr = rech - clim; dt = truth - clim
    cz = std_on(charge, train_mask)
    pred = clim.copy()
    betas = {}
    for nm, reg in (("lo", lowmoon), ("hi", ~lowmoon)):
        fit = reg & train_mask
        if fit.sum() < 16:
            pred[reg] = clim[reg] + de[reg]
            betas[nm] = (float("nan"), float("nan"), float("nan"))
            continue
        A = np.column_stack([de[fit], dr[fit], cz[fit] * dr[fit]])
        co, *_ = np.linalg.lstsq(A, dt[fit], rcond=None)
        be = np.clip(co[0], 0.0, 1.5); br = np.clip(co[1], 0.0, 1.5)
        bc = np.clip(co[2], -1.0, 1.5)        # charge gain: + means longer-down -> bigger swing
        eff = np.clip(br + bc * cz[reg], 0.0, 2.5)
        pred[reg] = clim[reg] + be * de[reg] + eff * dr[reg]
        betas[nm] = (be, br, bc)
    return pred, betas


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

    print("ARA CHARGE-CLOCK PREDICTOR  (loaded spring: long down -> violent spike)\n")
    print("HELD-OUT (origins >= 2016) correlation. CORRELATION LEADS.\n")
    print(f"{'lead':>4} {'engine':>8} {'handoff':>8} {'charge':>8}   {'b_chg lo/hi':>12}")
    leads = [1, 3, 6, 9, 12, 15, 18, 24, 27, 30]
    store = {}
    for h in leads:
        if not rec[h]["truth"]:
            continue
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"])
        cl = np.array(rec[h]["clim"]); tr = np.array(rec[h]["truth"])
        chg = np.array(rec[h]["charge"])
        oy = np.array(rec[h]["oy"]); pres = np.array(rec[h]["tpress"]); low = pres < 0
        trn = oy < CAL_SPLIT_YEAR; tst = oy >= CAL_SPLIT_YEAR
        if tst.sum() < 20:
            continue
        hand = blend_handoff(eng, rech, cl, low, tr, trn)
        chrg, bt = blend_charge(eng, rech, cl, low, chg, tr, trn)
        store[h] = (eng, hand, chrg, tr, cl, oy)
        print(f"{h:>4} {corr(eng[tst], tr[tst]):>+8.3f} {corr(hand[tst], tr[tst]):>+8.3f}"
              f" {corr(chrg[tst], tr[tst]):>+8.3f}   {bt['lo'][2]:+.2f}/{bt['hi'][2]:+.2f}")

    print("\nCross-event block-CV (leave-one-block-out), pooled correlation:")
    print(f"{'lead':>4} {'engine':>8} {'handoff':>8} {'charge':>8}")
    for h in [6, 12, 24, 27, 30]:
        if not rec[h]["truth"]:
            continue
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"])
        cl = np.array(rec[h]["clim"]); tr = np.array(rec[h]["truth"])
        chg = np.array(rec[h]["charge"])
        oy = np.array(rec[h]["oy"]); pres = np.array(rec[h]["tpress"]); low = pres < 0
        edges = np.quantile(oy, [1/3, 2/3]); blk = np.digitize(oy, edges)
        ph = np.full(len(oy), np.nan); pc = np.full(len(oy), np.nan)
        for b in range(3):
            te = blk == b
            if te.sum() < 12 or (~te).sum() < 24:
                continue
            ph[te] = blend_handoff(eng, rech, cl, low, tr, ~te)[te]
            pc[te] = blend_charge(eng, rech, cl, low, chg, tr, ~te)[0][te]
        print(f"{h:>4} {corr(eng, tr):>+8.3f} {corr(ph, tr):>+8.3f} {corr(pc, tr):>+8.3f}")
    print("\nRead: charge >= handoff at the rings, and b_chg(lo) > 0, means a longer/deeper")
    print("down loads a more violent rebound -- Dylan's loaded-spring physics confirmed.")


if __name__ == "__main__":
    main()
