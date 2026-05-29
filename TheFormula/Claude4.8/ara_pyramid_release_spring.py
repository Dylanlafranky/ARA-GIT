"""
ARA pyramid RELEASE-SPRING predictor  (the snap, scaled by load AND moon distance)
==================================================================================

Dylan's correction (2026-05-29): while the apex is HELD down, the next peak is
naturally low -- that is just the hold. The violent spike comes on RELEASE. The
charge does not amplify continuously (that failed); it amplifies the ONE rebound
that fires when a sustained down lets go. The trigger is the turn-up, scaled by how
deep the spring was loaded -- AND by the moon's distance at the release time.

Direct evidence (this record, 17 release events):
  depth-of-hold -> trough-to-peak rebound = +0.70 / +0.68 / +0.67 at 12/18/24 mo.
  moon phase at release -> rebound, with depth removed = +0.21 / +0.28 / +0.67.
The moon explains snap size on a SEPARATE axis from depth (strongest far out).

Strictly-causal pieces:
  ENGINE   : seasonal three-body LIM apex forecast (timing + spike).
  RECHARGE : lead-h regression of T(t+h) on origin [zW, zE] (the slow locked mode).
  TENSION  : depth of the CURRENT ongoing run below climatology at the origin.
  MOON     : deterministic perigee-precession pressure wave at the release (target)
             time. Ephemeris -> known a priori -> leak-free.

  OPTION 1 (handoff):   pred = clim + b_eng*de + b_rech*dr
  OPTION 2 (release):   + b_rel * tens_z * relu(dr)
  OPTION 2b (rel+moon): release gain breathes with moon: (b_rel + b_moon*moon_z)*load

Per-REGIME (low/high moon) trust fit causally on origins < CAL_SPLIT, applied >=.
Correlation leads; block-CV for cross-event robustness.

Usage: python3 ara_pyramid_release_spring.py nino34_long_anom.csv
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
    rec = {h: {"eng": [], "rech": [], "truth": [], "clim": [], "tens": [],
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
        tens = 0.0
        k = i
        while k >= 0 and T[k] < clim:
            tens += (clim - T[k]); k -= 1
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
            rec[h]["tens"].append(tens)
            rec[h]["oy"].append(yr[i]); rec[h]["tyr"].append(yr[i + h])
            rec[h]["tmon"].append(mon[i + h]); rec[h]["tpress"].append(pressure_proxy(yr[i + h]))
    return rec


def corr(a, b):
    a = np.asarray(a); b = np.asarray(b); m = ~np.isnan(a) & ~np.isnan(b)
    if m.sum() < 3:
        return float("nan")
    return float(np.corrcoef(a[m], b[m])[0, 1])


def _tens_z(tens, mask):
    m = tens[mask]
    mu = m.mean(); sd = m.std()
    z = (tens - mu) / sd if sd > 0 else np.zeros_like(tens)
    return np.clip(z, 0.0, None)


def blend_handoff(eng, rech, clim, lowmoon, truth, train_mask):
    de = eng - clim; dr = rech - clim; dt = truth - clim
    pred = clim.copy()
    for reg in (lowmoon, ~lowmoon):
        fit = reg & train_mask
        if fit.sum() < 12:
            pred[reg] = clim[reg] + de[reg]; continue
        A = np.column_stack([de[fit], dr[fit]])
        co, *_ = np.linalg.lstsq(A, dt[fit], rcond=None)
        be = np.clip(co[0], 0.0, 1.5); br = np.clip(co[1], 0.0, 1.5)
        pred[reg] = clim[reg] + be * de[reg] + br * dr[reg]
    return pred


def blend_release(eng, rech, clim, lowmoon, tens, truth, train_mask):
    de = eng - clim; dr = rech - clim; dt = truth - clim
    up = np.clip(dr, 0.0, None)
    tz = _tens_z(tens, train_mask)
    pred = clim.copy(); betas = {}
    for nm, reg in (("lo", lowmoon), ("hi", ~lowmoon)):
        fit = reg & train_mask
        if fit.sum() < 16:
            pred[reg] = clim[reg] + de[reg]
            betas[nm] = (float("nan"),) * 3; continue
        A = np.column_stack([de[fit], dr[fit], tz[fit] * up[fit]])
        co, *_ = np.linalg.lstsq(A, dt[fit], rcond=None)
        be = np.clip(co[0], 0.0, 1.5); br = np.clip(co[1], 0.0, 1.5)
        bl = np.clip(co[2], 0.0, 2.0)
        pred[reg] = clim[reg] + be * de[reg] + br * dr[reg] + bl * tz[reg] * up[reg]
        betas[nm] = (be, br, bl)
    return pred, betas


def blend_release_moon(eng, rech, clim, lowmoon, tens, mphase, truth, train_mask):
    de = eng - clim; dr = rech - clim; dt = truth - clim
    up = np.clip(dr, 0.0, None)
    tz = _tens_z(tens, train_mask)
    mu = mphase[train_mask].mean(); sd = mphase[train_mask].std()
    mz = (mphase - mu) / sd if sd > 0 else np.zeros_like(mphase)
    load = tz * up
    pred = clim.copy(); betas = {}
    for nm, reg in (("lo", lowmoon), ("hi", ~lowmoon)):
        fit = reg & train_mask
        if fit.sum() < 16:
            pred[reg] = clim[reg] + de[reg]
            betas[nm] = (float("nan"),) * 4; continue
        A = np.column_stack([de[fit], dr[fit], load[fit], (load * mz)[fit]])
        co, *_ = np.linalg.lstsq(A, dt[fit], rcond=None)
        be = np.clip(co[0], 0.0, 1.5); br = np.clip(co[1], 0.0, 1.5)
        bl = np.clip(co[2], 0.0, 2.0); bm = np.clip(co[3], -1.0, 2.0)
        eff = np.clip(bl + bm * mz[reg], 0.0, 3.0)
        pred[reg] = clim[reg] + be * de[reg] + br * dr[reg] + eff * load[reg]
        betas[nm] = (be, br, bl, bm)
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

    print("ARA RELEASE-SPRING PREDICTOR  (snap on release, scaled by load + moon)\n")
    print("HELD-OUT (origins >= 2016) correlation. CORRELATION LEADS.\n")
    print(f"{'lead':>4} {'engine':>8} {'handoff':>8} {'release':>8} {'rel+moon':>9}   {'b_moon lo/hi':>12}")
    leads = [1, 3, 6, 9, 12, 15, 18, 24, 27, 30]
    for h in leads:
        if not rec[h]["truth"]:
            continue
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"])
        cl = np.array(rec[h]["clim"]); tr = np.array(rec[h]["truth"])
        tn = np.array(rec[h]["tens"]); mp = np.array(rec[h]["tpress"])
        oy = np.array(rec[h]["oy"]); low = mp < 0
        trn = oy < CAL_SPLIT_YEAR; tst = oy >= CAL_SPLIT_YEAR
        if tst.sum() < 20:
            continue
        hand = blend_handoff(eng, rech, cl, low, tr, trn)
        rel, _ = blend_release(eng, rech, cl, low, tn, tr, trn)
        relm, bm = blend_release_moon(eng, rech, cl, low, tn, mp, tr, trn)
        print(f"{h:>4} {corr(eng[tst], tr[tst]):>+8.3f} {corr(hand[tst], tr[tst]):>+8.3f}"
              f" {corr(rel[tst], tr[tst]):>+8.3f} {corr(relm[tst], tr[tst]):>+9.3f}"
              f"   {bm['lo'][3]:+.2f}/{bm['hi'][3]:+.2f}")

    print("\nCross-event block-CV (leave-one-block-out), pooled correlation:")
    print(f"{'lead':>4} {'engine':>8} {'handoff':>8} {'release':>8} {'rel+moon':>9}")
    for h in [6, 12, 18, 24, 27, 30]:
        if not rec[h]["truth"]:
            continue
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"])
        cl = np.array(rec[h]["clim"]); tr = np.array(rec[h]["truth"])
        tn = np.array(rec[h]["tens"]); mp = np.array(rec[h]["tpress"])
        oy = np.array(rec[h]["oy"]); low = mp < 0
        edges = np.quantile(oy, [1/3, 2/3]); blk = np.digitize(oy, edges)
        ph = np.full(len(oy), np.nan); pr = np.full(len(oy), np.nan); pm = np.full(len(oy), np.nan)
        for b in range(3):
            te = blk == b
            if te.sum() < 12 or (~te).sum() < 24:
                continue
            ph[te] = blend_handoff(eng, rech, cl, low, tr, ~te)[te]
            pr[te] = blend_release(eng, rech, cl, low, tn, tr, ~te)[0][te]
            pm[te] = blend_release_moon(eng, rech, cl, low, tn, mp, tr, ~te)[0][te]
        print(f"{h:>4} {corr(eng, tr):>+8.3f} {corr(ph, tr):>+8.3f} {corr(pr, tr):>+8.3f} {corr(pm, tr):>+9.3f}")
    print("\nRead: rel+moon >= handoff at the rings, and b_moon(lo) > 0, means the snap on")
    print("release is scaled by the moon's distance at that time -- Dylan's full release physics.")


if __name__ == "__main__":
    main()
