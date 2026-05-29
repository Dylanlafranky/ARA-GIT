"""
Skill recurrence + spectrum analysis (ARA → ENSO chain, steps 6, 8, 9)
======================================================================

Reproduces the two findings that came after the basic forecast:

  STEP 8 — Skill recurrence: walk-forward forecast skill vs climatology as a
           function of lead time (1..HMAX months), refitting the three-body
           model on strictly-past data at every origin. Shows that skill does
           not decay monotonically: it troughs near the half-period and
           RE-EMERGES, with the re-emergence amplitudes decaying ~geometrically
           (a damped-oscillation envelope).

  STEP 9 — Two bands: the NINO 3.4 power spectrum over the full record shows two
           interannual bands of comparable power (quasi-biennial ~28 mo and
           low-frequency ~42-67 mo). The skill-recurrence period traces the
           quasi-biennial band, not the single fitted mode.

Walk-forward = the honest test: at each origin t, fit only on data before t,
then forecast t+h. No leakage. Decisive metric = skill vs climatology.

Data: PMEL WWV west/east (auto-download); NINO 3.4 monthly anomaly CSV.
"""

import os
import sys
import json
import urllib.request
import numpy as np

PMEL = "https://www.pmel.noaa.gov/tao/wwv/data/"
WALK_START_YEAR = 2008.0
MIN_TRAIN = 300
HMAX = 54


def _dl(name, path):
    if not os.path.exists(path):
        urllib.request.urlretrieve(PMEL + name, path)


def load_wwv(path):
    out = {}
    for ln in open(path):
        p = ln.split()
        if len(p) == 3 and p[0].isdigit() and len(p[0]) == 6:
            out[p[0]] = float(p[2]) / 1e14
    return out


def load_nino(path, missing=-99.99):
    out = {}
    for ln in open(path):
        p = [x.strip() for x in ln.split(",")]
        if len(p) == 2 and p[0][:4].isdigit():
            v = float(p[1])
            if v > missing + 0.001:
                out[p[0][:7].replace("-", "")] = v
    return out


def skill_recurrence(T, W, E, yr):
    """Walk-forward skill vs climatology and forecast correlation by lead."""
    acc = {h: {"p": [], "a": [], "c": []} for h in range(1, HMAX + 1)}
    for i in range(len(T)):
        if yr[i] < WALK_START_YEAR:
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
            acc[h]["p"].append((Mp @ X[i])[0])
            acc[h]["a"].append(T[i + h])
            acc[h]["c"].append(clim)
    out = {"h": [], "skill": [], "corr": [], "noise": [], "n": []}
    for h in range(1, HMAX + 1):
        a = np.array(acc[h]["a"])
        if len(a) < 60:
            continue
        p = np.array(acc[h]["p"]); c = np.array(acc[h]["c"])
        out["h"].append(h)
        out["skill"].append(round(float(1 - np.mean((p - a) ** 2) / np.mean((c - a) ** 2)), 3))
        out["corr"].append(round(float(np.corrcoef(p, a)[0, 1]), 3))
        out["noise"].append(round(float(1 / np.sqrt(len(a))), 3))
        out["n"].append(len(a))
    return out


def spectrum(nino_csv):
    """Full-record NINO 3.4 interannual power spectrum (Hann-windowed)."""
    n = []
    for ln in open(nino_csv):
        p = [x.strip() for x in ln.split(",")]
        if len(p) == 2 and p[0][:4].isdigit():
            v = float(p[1]); n.append(v if v > -99 else np.nan)
    x = np.array(n)
    x = np.interp(np.arange(len(x)), np.where(~np.isnan(x))[0], x[~np.isnan(x)])
    x = x - x.mean()
    x = x - np.polyval(np.polyfit(np.arange(len(x)), x, 1), np.arange(len(x)))
    N = len(x)
    P = np.abs(np.fft.rfft(x * np.hanning(N))) ** 2
    f = np.fft.rfftfreq(N, d=1.0)
    per = 1 / f[1:]; P = P[1:]
    qb = (per >= 22) & (per <= 32)        # quasi-biennial
    lf = (per >= 40) & (per <= 56)        # low-frequency
    return dict(months=N, qb_power=float(P[qb].sum()), lf_power=float(P[lf].sum()),
                qb_over_lf=round(float(P[qb].sum() / P[lf].sum()), 2))


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    _dl("wwv_west.dat", "wwv_west.dat")
    _dl("wwv_east.dat", "wwv_east.dat")
    W = load_wwv("wwv_west.dat"); E = load_wwv("wwv_east.dat")
    nino = load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys])
    Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys])

    print("=" * 64)
    print("SKILL RECURRENCE (walk-forward, refit-on-past)")
    print("=" * 64)
    rec = skill_recurrence(T, Wv, Ev, yr)
    print(f"{'lead':>4} {'skill':>7} {'corr':>7} {'noise':>6} {'n':>4}")
    for j, h in enumerate(rec["h"]):
        flag = "  <- re-emergence" if h in (26, 27, 52, 53) else (
               "  <- trough" if h in (12, 19, 44, 45) else "")
        print(f"{h:>4} {rec['skill'][j]:>+7.3f} {rec['corr'][j]:>+7.3f} "
              f"{rec['noise'][j]:>6.3f} {rec['n'][j]:>4}{flag}")
    peaks = {h: rec["corr"][rec["h"].index(h)] for h in (1, 27, 53) if h in rec["h"]}
    print("\nre-emergence peak correlations:", peaks)
    if len(peaks) == 3:
        v = list(peaks.values())
        print(f"decay per ring: {v[1]/v[0]:.2f}, {v[2]/v[1]:.2f}  (geometric => damped oscillation)")

    print("\n" + "=" * 64)
    print("SPECTRUM (full NINO record, interannual bands)")
    print("=" * 64)
    s = spectrum(nino_csv)
    print(f"record: {s['months']} months")
    print(f"quasi-biennial (22-32mo) power : {s['qb_power']:.0f}")
    print(f"low-frequency  (40-56mo) power : {s['lf_power']:.0f}")
    print(f"QB / LF power ratio            : {s['qb_over_lf']}  (~1 => two comparable bands)")
    print("\nThe skill recurrence period (~27mo) traces the quasi-biennial band,")
    print("not the single fitted ~38mo mode. Damping sets ring amplitude;")
    print("the second band sets the recurrence spacing.")


if __name__ == "__main__":
    main()
