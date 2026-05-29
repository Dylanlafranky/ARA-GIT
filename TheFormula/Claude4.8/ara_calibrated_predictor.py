"""
ARA calibrated predictor — rides the skill-wave, stays honest in the trough
===========================================================================

Wraps the three-body pyramid LIM with a lead-dependent shrinkage calibration.
The raw LIM has skill that is not monotonic in lead time: strong near the
surface (~6 mo), a trough around 9-18 mo where it actively self-harms (commits
to swings it can't time, scoring worse than climatology), and a faint, NON-
STATIONARY re-emergence near ~27 mo.

The calibration learns, per lead, how much to trust the forecast (a shrinkage
factor toward climatology), on EARLY data only, and applies it causally to
later forecasts. Effect:
  * near field (<=~15 mo): trough self-harm removed — the negative skills flip
    to ~0 because the model shrinks to climatology where it is blind.
  * far field (>~18 mo): the re-emergence wanders between epochs (it's tied to
    the variable quasi-biennial period), so calibrating to it is unreliable.
    The calibrator does not claim skill it can't hold.

This does NOT break the ~6-month wall. It makes the forecaster honest about its
own lead-dependent confidence: confident near the surface, humble in the trough,
non-committal at the wandering re-emergence.

Decisive metric: skill vs climatology on held-out forecasts. Walk-forward,
strictly causal, leakage-guarded. Data: PMEL WWV west/east (auto-download);
NINO 3.4 monthly anomaly CSV.
"""

import os
import sys
import urllib.request
import numpy as np

PMEL = "https://www.pmel.noaa.gov/tao/wwv/data/"
WALK_START = 2005.0
MIN_TRAIN = 270
CAL_SPLIT_YEAR = 2016.0      # learn shrinkage on origins before this, apply after
HMAX = 36


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


def walk_forward_forecasts(T, W, E, yr):
    """Refit the 3-body LIM on past-only at every origin; forecast all leads."""
    rec = {h: {"pred": [], "truth": [], "clim": [], "oy": []} for h in range(1, HMAX + 1)}
    for i in range(len(T)):
        if yr[i] < WALK_START:
            continue
        idx = np.arange(0, i)
        if len(idx) < MIN_TRAIN:
            continue
        zW = (W - W[idx].mean()) / W[idx].std()
        zE = (E - E[idx].mean()) / E[idx].std()
        X = np.column_stack([T, zW, zE])
        M = np.linalg.lstsq(X[idx][:-1], X[idx][1:], rcond=None)[0].T
        clim = T[idx].mean()
        Mp = np.eye(3)
        for h in range(1, HMAX + 1):
            if i + h >= len(T):
                break
            Mp = Mp @ M
            rec[h]["pred"].append((Mp @ X[i])[0])
            rec[h]["truth"].append(T[i + h])
            rec[h]["clim"].append(clim)
            rec[h]["oy"].append(yr[i])
    return rec


def calibrate_and_score(rec):
    """Learn lead shrinkage on early origins, apply on late; report raw vs calibrated."""
    out = []
    for h in range(1, HMAX + 1):
        oy = np.array(rec[h]["oy"]); pr = np.array(rec[h]["pred"])
        tr = np.array(rec[h]["truth"]); cl = np.array(rec[h]["clim"])
        if len(oy) == 0:
            continue
        trn = oy < CAL_SPLIT_YEAR; tst = oy >= CAL_SPLIT_YEAR
        if tst.sum() < 20 or trn.sum() < 20:
            continue
        x = pr[trn] - cl[trn]; y = tr[trn] - cl[trn]
        beta = np.dot(x, y) / np.dot(x, x) if np.dot(x, x) > 0 else 0.0
        beta = max(0.0, min(1.0, beta))           # never anti-forecast, never amplify
        cal = cl[tst] + beta * (pr[tst] - cl[tst])
        raw = 1 - np.mean((pr[tst] - tr[tst]) ** 2) / np.mean((cl[tst] - tr[tst]) ** 2)
        clb = 1 - np.mean((cal - tr[tst]) ** 2) / np.mean((cl[tst] - tr[tst]) ** 2)
        out.append((h, raw, clb, beta))
    return out


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    _dl("wwv_west.dat", "wwv_west.dat"); _dl("wwv_east.dat", "wwv_east.dat")
    W = load_wwv("wwv_west.dat"); E = load_wwv("wwv_east.dat")
    nino = load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys])
    Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys])

    rec = walk_forward_forecasts(T, Wv, Ev, yr)
    rows = calibrate_and_score(rec)

    print("ARA CALIBRATED PREDICTOR — raw LIM vs lead-calibrated (held-out)")
    print(f"shrinkage learned on origins < {CAL_SPLIT_YEAR:.0f}, applied on origins >= it\n")
    print(f"{'lead':>4} {'raw skill':>10} {'calibrated':>11} {'trust β':>8}  note")
    for h, raw, clb, beta in rows:
        if h not in (1, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36):
            continue
        note = ""
        if raw < 0 <= clb:
            note = "trough self-harm removed"
        elif h >= 21 and clb < raw - 0.02:
            note = "re-emergence wandered (calib unreliable)"
        print(f"{h:>4} {raw:>+10.3f} {clb:>+11.3f} {beta:>8.2f}  {note}")
    print("\nReading: trust β near 1 = forecast trusted; near 0 = shrink to climatology.")
    print("Honest envelope: real skill to ~6 mo, calibrated humility through the")
    print("9-18 mo trough, no bankable claim at the wandering ~27 mo re-emergence.")


if __name__ == "__main__":
    main()
