"""
ARA pyramid PRESSURE predictor  (the 4th line: load-from-above -> amplitude)
============================================================================

The pyramid build, finished from the top.

The three base/apex grains (NINO apex T, warm-west WWV, cool-east WWV) and their
coupled rebound generate the DYNAMICS and the TIMING -- that work is done by the
seasonal three-body LIM (the capstone). The skill they earn is an oscillating
decay in lead time: strong near the surface, a trough ~9-18 mo, then a faint
RECURRENCE RING ~27 mo that shrinks ~x0.27 per ring (~ 1/phi^3). The rings are
real but small (~+0.26 corr) -- the LIM lets them ring down.

This script adds the FOURTH line: the load from above. In the sand picture the
coarsest grains overhead press DOWN on the apex; more downward pressure secures
the grain and drives a harder spring-back (Newton's third law) -- it sets HOW BIG
the rebound is, not WHEN it happens. Dylan's call: we are decent on *when*, so the
4th line targets AMPLITUDE only, and it presses from above (upper-downward).

Mechanism (honest, leak-free):
  The downward pressure is a DETERMINISTIC calendar wave evaluated at the TARGET
  time t+h -- annual (the seasonal lock) optionally plus a LUNAR wave (18.6-yr
  nodal, or 8.85-yr perigee). Because it is astronomical/calendar, it is known a
  priori for any future month: using it introduces NO leakage.

  We let the per-lead TRUST factor breathe with that pressure:

      pred = clim + beta(h, pressure_at_target) * (raw_pred - clim)
      beta = b0 + b1 cos(annual) + b2 sin(annual) [+ b3 cos(lunar) + b4 sin(lunar)]

  Coefficients fit by least squares on PAST origins only (< CAL_SPLIT_YEAR),
  applied causally to the held-out origins (>=). High-pressure target phase ->
  larger restored amplitude; low-pressure -> shrink toward climatology.

  The annual-only variant generalises the capstone's single per-lead beta. The
  lunar variants are the genuinely NEW degree of freedom: does an astronomical
  tide-like pressure lift the recurrence-ring amplitude beyond the annual clock?

Decisive metric: correlation first, then skill vs climatology, walk-forward,
strictly causal. Leak-check variant (--leaky) fits beta on ALL origins to confirm
the causal split is not hiding future information.

Data: PMEL WWV west/east (auto-download); NINO 3.4 monthly anomaly CSV.
Usage: python3 ara_pyramid_pressure_predictor.py nino34_long_anom.csv [--leaky]
"""

import os
import sys
import urllib.request
import numpy as np

PMEL = "https://www.pmel.noaa.gov/tao/wwv/data/"
WALK_START = 2005.0
MIN_TRAIN = 270
CAL_SPLIT_YEAR = 2016.0
HMAX = 30
NODAL_YR = 18.613      # lunar nodal precession
PERIGEE_YR = 8.847     # lunar perigee (anomalistic) precession


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
    """First-harmonic annual modulation of state and intercept (the 3-body clock)."""
    th = 2 * np.pi * (m - 1) / 12
    c, s = np.cos(th), np.sin(th)
    return np.column_stack([X, X * c[:, None], X * s[:, None], c, s, np.ones(len(X))])


def walk_forward_seasonal(T, W, E, yr, mon):
    """Refit seasonal 3-body LIM on past-only at every origin; record raw forecasts."""
    rec = {h: {"pred": [], "truth": [], "clim": [], "oy": [], "tyr": [], "tmon": []}
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
            x = X[i].copy()
            for kk in range(h):
                mm = ((mon[i] - 1 + kk) % 12) + 1
                x = seasonal_features(x[None, :], np.array([mm]))[0] @ B
            rec[h]["pred"].append(x[0]); rec[h]["truth"].append(T[i + h])
            rec[h]["clim"].append(clim); rec[h]["oy"].append(yr[i])
            rec[h]["tyr"].append(yr[i + h]); rec[h]["tmon"].append(mon[i + h])
    return rec


def pressure_basis(tyr, tmon, lunar):
    """Deterministic downward-pressure wave at TARGET time. Always annual; +lunar."""
    th = 2 * np.pi * (tmon - 1) / 12
    cols = [np.ones(len(tyr)), np.cos(th), np.sin(th)]
    if lunar == "nodal":
        ph = 2 * np.pi * tyr / NODAL_YR
        cols += [np.cos(ph), np.sin(ph)]
    elif lunar == "perigee":
        ph = 2 * np.pi * tyr / PERIGEE_YR
        cols += [np.cos(ph), np.sin(ph)]
    return np.column_stack(cols)


def corr(a, b):
    a = np.asarray(a); b = np.asarray(b); m = ~np.isnan(a)
    if m.sum() < 3:
        return float("nan")
    return float(np.corrcoef(a[m], b[m])[0, 1])


def skill(pred, truth, clim):
    pred = np.asarray(pred); m = ~np.isnan(pred)
    return 1 - np.mean((pred[m] - truth[m]) ** 2) / np.mean((clim[m] - truth[m]) ** 2)


def pressure_calibrate(rec, lunar, leaky=False):
    """beta breathes with the deterministic target-time pressure wave.
    Fit coeffs on origins < CAL_SPLIT (or ALL if leaky); apply causally to >=."""
    rows = []
    for h in range(1, HMAX + 1):
        oy = np.array(rec[h]["oy"]); pr = np.array(rec[h]["pred"])
        tr = np.array(rec[h]["truth"]); cl = np.array(rec[h]["clim"])
        tyr = np.array(rec[h]["tyr"]); tmon = np.array(rec[h]["tmon"])
        if len(oy) == 0:
            continue
        trn = np.ones(len(oy), bool) if leaky else (oy < CAL_SPLIT_YEAR)
        tst = oy >= CAL_SPLIT_YEAR
        if tst.sum() < 20 or trn.sum() < 20:
            continue
        dpr = pr - cl                       # forecast deviation from climatology
        dtr = tr - cl                       # truth deviation
        P = pressure_basis(tyr, tmon, lunar)
        # design: dtr ~ (dpr * pressure_basis) . coeffs   => beta(target) = P . coeffs
        A = P * dpr[:, None]
        coef, *_ = np.linalg.lstsq(A[trn], dtr[trn], rcond=None)
        beta = P @ coef                     # per-sample trust = pressure-modulated
        beta = np.clip(beta, 0.0, 1.5)      # allow amplitude RESTORE (>1), no flip
        cal = cl + beta * dpr
        rows.append((h,
                     corr(pr[tst], tr[tst]),          # raw seasonal corr
                     corr(cal[tst], tr[tst]),         # pressure-calibrated corr
                     skill(pr[tst], tr[tst], cl[tst]),
                     skill(cal[tst], tr[tst], cl[tst]),
                     float(np.mean(beta[tst]))))
    return rows


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    leaky = "--leaky" in sys.argv
    _dl("wwv_west.dat", "wwv_west.dat"); _dl("wwv_east.dat", "wwv_east.dat")
    W = load_wwv("wwv_west.dat"); E = load_wwv("wwv_east.dat")
    nino = load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys])
    Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys])
    mon = np.array([int(k[4:6]) for k in keys])

    rec = walk_forward_seasonal(T, Wv, Ev, yr, mon)
    variants = {
        "annual":          pressure_calibrate(rec, None, leaky),
        "annual+nodal":    pressure_calibrate(rec, "nodal", leaky),
        "annual+perigee":  pressure_calibrate(rec, "perigee", leaky),
    }

    tag = "  [LEAK-CHECK: beta fit on ALL origins]" if leaky else ""
    print(f"ARA PYRAMID PRESSURE PREDICTOR{tag}")
    print("held-out (>=2016) correlation, then skill vs climatology. CORRELATION LEADS.\n")
    leads = [1, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
    for name, rows in variants.items():
        d = {h: r for h, *r in [(row[0], *row[1:]) for row in rows]}
        print(f"--- pressure = {name} ---")
        print(f"{'lead':>4} {'rawCorr':>8} {'pressCorr':>10} {'rawSkill':>9} {'pressSkill':>11} {'meanBeta':>9}")
        for h in leads:
            if h not in d:
                continue
            rc, pc, rs, ps, mb = d[h]
            star = "  <-- ring" if h in (24, 27, 30) else ""
            print(f"{h:>4} {rc:>+8.3f} {pc:>+10.3f} {rs:>+9.3f} {ps:>+11.3f} {mb:>9.2f}{star}")
        print()
    print("Read: pressCorr/pressSkill > rawCorr/rawSkill at the rings (h>=24) means the")
    print("downward-pressure line lifted the recurrence amplitude. Lunar variants beating")
    print("annual would mean an astronomical tide-pressure is doing real work.")


if __name__ == "__main__":
    main()
