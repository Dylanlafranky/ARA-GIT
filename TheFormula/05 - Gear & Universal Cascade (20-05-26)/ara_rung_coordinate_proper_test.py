"""
ara_rung_coordinate_proper_test.py

Canonical verification of the ARA-rung coordinate hypothesis using the same
strict-causal Butterworth/SOS tooling used by existing predictor tests.

Hypothesis:
  Subsystem position is a joint scale+ARA coordinate:
      pos_k = k + ARA_k / 2
  Distance across rungs is:
      d_k = |pos_k - pos_home|
  Contribution weights decay with that distance:
      w_k = 2^(-d_k)
"""

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, find_peaks, sosfilt

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
WORKSPACE_ROOT = REPO_ROOT.parent.parent

sys.path.insert(0, str(REPO_ROOT))
from ara_framework import Topology, _measure_rung, causal_bandpass

PHI = (1 + 5**0.5) / 2


def measure_rung_ara(arr_up_to_t, period, bw=0.85):
    arr = np.asarray(arr_up_to_t, dtype=float)
    if len(arr) < 3 * int(period):
        return None
    f_c = 1.0 / period
    nyq = 0.5
    lo = max(1e-6, (1 - bw) * f_c / nyq)
    hi = min(0.999, (1 + bw) * f_c / nyq)
    if lo >= hi:
        return None
    sos = butter(2, [lo, hi], btype="bandpass", output="sos")
    bp = sosfilt(sos, arr - np.mean(arr))
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2:
        return None
    aras = []
    for i in range(len(peaks) - 1):
        seg = smoothed[peaks[i] : peaks[i + 1] + 1]
        if len(seg) < 3:
            continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg) - 1)))
        aras.append((1 - f_t) / f_t)
    if not aras:
        return None
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


def extract_topology(data, t, rungs_k, home_k, rung_base, pin_factor=4):
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr):
        return None
    v_now = float(arr[t - 1])
    mean_train = float(np.mean(arr[:t]))
    rungs = []
    for k in rungs_k:
        period = rung_base ** int(k)
        if period < 2 or pin_factor * period > t:
            continue
        bp = causal_bandpass(arr[:t], period)
        rec = _measure_rung(bp, period, k)
        if rec is None:
            continue
        ara = measure_rung_ara(arr[:t], period)
        if ara is not None:
            rec["ara"] = float(ara)
        rungs.append(rec)
    return Topology(v_now=v_now, mean_train=mean_train, home_k=home_k, rungs=rungs)


def predict_old_kdiff(topo, h, weight_base):
    if topo is None or not topo.rungs:
        return float("nan")
    weights = np.array([weight_base ** (-abs(s["k"] - topo.home_k)) for s in topo.rungs], dtype=float)
    if weights.sum() <= 0:
        return float("nan")
    weights /= weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        contrib += weights[j] * s["amp"] * np.cos(s["theta"] + 2 * np.pi * h / s["period"])
    return topo.mean_train + contrib


def predict_old_coorddist(topo, h, decay_base=2.0):
    if topo is None or not topo.rungs:
        return float("nan")
    ara_at = {s["k"]: s.get("ara") for s in topo.rungs if s.get("ara") is not None}
    home_ara = ara_at.get(topo.home_k)
    if home_ara is None:
        avail = [a for a in ara_at.values() if a is not None]
        if not avail:
            home_ara = 1.0
        else:
            home_ara = float(np.mean(avail))
    home_pos = topo.home_k + home_ara / 2.0
    distances = []
    for s in topo.rungs:
        ara_k = s.get("ara", home_ara)
        pos_k = s["k"] + ara_k / 2.0
        distances.append(abs(pos_k - home_pos))
    weights = np.array([decay_base ** (-d) for d in distances], dtype=float)
    if weights.sum() <= 0:
        return float("nan")
    weights /= weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        contrib += weights[j] * s["amp"] * np.cos(s["theta"] + 2 * np.pi * h / s["period"])
    return topo.mean_train + contrib


def safe_base(x):
    if not np.isfinite(x):
        return 1.05
    return max(1.05, float(x))


def run_one(data, name, home_period, horizons, n_anchors=60, test_window=None):
    n = len(data)
    if test_window is None:
        test_window = min(30 * 12, n // 3)
    test_start = max(int(4 * home_period), n - test_window)
    anchor_idxs = np.linspace(test_start, n - max(horizons) - 1, n_anchors).astype(int)

    # System ARA at home period from training-only anchors.
    home_ara_samples = []
    for t in anchor_idxs:
        ara = measure_rung_ara(data[:t], home_period)
        if ara is not None and np.isfinite(ara):
            home_ara_samples.append(ara)
    if home_ara_samples:
        sys_ara = float(np.mean(home_ara_samples))
        sys_ara_std = float(np.std(home_ara_samples))
    else:
        sys_ara = 1.0
        sys_ara_std = 0.0
    sys_base = safe_base(sys_ara)
    sys_base_plus = safe_base(1.0 + sys_ara)

    def rung_range(base):
        k_lo = max(2, int(math.log(3.0) / math.log(base)))
        k_hi = int(math.log(min(720.0, n / 4.0)) / math.log(base)) + 1
        return list(range(k_lo, k_hi + 1))

    cfgs = [
        ("phi-sub + phi-k", PHI, "k", PHI),
        ("phi-sub + 2-k", PHI, "k", 2.0),
        ("phi-sub + coord", PHI, "coord", 2.0),
        ("2-sub + 2-k", 2.0, "k", 2.0),
        ("2-sub + coord", 2.0, "coord", 2.0),
        ("sysARA-sub + coord", sys_base, "coord", 2.0),
        ("1+sysARA-sub + coord", sys_base_plus, "coord", 2.0),
    ]

    configs = []
    for label, rung_base, mode, param in cfgs:
        home_k = round(math.log(home_period) / math.log(rung_base))
        configs.append(
            dict(
                label=label,
                rung_base=rung_base,
                mode=mode,
                param=param,
                home_k=home_k,
                rungs_k=rung_range(rung_base),
            )
        )

    out = {c["label"]: {h: {"p": [], "t": []} for h in horizons} for c in configs}
    pers = {h: {"p": [], "t": []} for h in horizons}

    for t in anchor_idxs:
        for c in configs:
            topo = extract_topology(data, t, c["rungs_k"], c["home_k"], c["rung_base"])
            if topo is None:
                continue
            for h in horizons:
                if t + h >= n:
                    continue
                truth = float(data[t + h - 1])
                if c["mode"] == "k":
                    pred = predict_old_kdiff(topo, h, c["param"])
                else:
                    pred = predict_old_coorddist(topo, h, decay_base=c["param"])
                if np.isfinite(pred):
                    out[c["label"]][h]["p"].append(pred)
                    out[c["label"]][h]["t"].append(truth)
        for h in horizons:
            if t + h >= n:
                continue
            pers[h]["p"].append(float(data[t - 1]))
            pers[h]["t"].append(float(data[t + h - 1]))

    summary = {}
    for c in configs:
        label = c["label"]
        summary[label] = {}
        for h in horizons:
            P = np.array(out[label][h]["p"], dtype=float)
            T = np.array(out[label][h]["t"], dtype=float)
            if len(P) < 5:
                summary[label][h] = dict(n=int(len(P)))
                continue
            mae = float(np.mean(np.abs(P - T)))
            corr = float(np.corrcoef(P, T)[0, 1]) if np.std(P) > 1e-9 and np.std(T) > 1e-9 else float("nan")
            summary[label][h] = dict(n=int(len(P)), mae=mae, corr=corr)

    pers_summary = {}
    for h in horizons:
        P = np.array(pers[h]["p"], dtype=float)
        T = np.array(pers[h]["t"], dtype=float)
        if len(P) < 5:
            pers_summary[h] = dict(n=int(len(P)))
            continue
        mae = float(np.mean(np.abs(P - T)))
        corr = float(np.corrcoef(P, T)[0, 1]) if np.std(P) > 1e-9 and np.std(T) > 1e-9 else float("nan")
        pers_summary[h] = dict(n=int(len(P)), mae=mae, corr=corr)

    print(f"\n=== {name} ===")
    print(f"  home_period={home_period:.1f}, sys_ara={sys_ara:.3f} +/- {sys_ara_std:.3f}, sys_base={sys_base:.3f}, 1+sys_base={sys_base_plus:.3f}")
    print(f"  {'config':28s} " + " ".join(f"h={h:>5}" for h in horizons))
    for label in summary:
        row = [f"{label:28s}"]
        for h in horizons:
            s = summary[label][h]
            row.append(f" {s['mae']:>7.3f}" if "mae" in s else "       -")
        print("".join(row))
    row = [f"{'persistence':28s}"]
    for h in horizons:
        s = pers_summary[h]
        row.append(f" {s['mae']:>7.3f}" if "mae" in s else "       -")
    print("".join(row))

    print("\n  Winners excluding persistence:")
    for h in horizons:
        cands = []
        for label in summary:
            if "mae" in summary[label][h]:
                cands.append((summary[label][h]["mae"], label))
        cands.sort(key=lambda x: x[0])
        if cands:
            print(f"    h={h:>5}: {cands[0][1]}  MAE={cands[0][0]:.3f}")

    return dict(
        system=name,
        home_period=home_period,
        sys_ara=sys_ara,
        sys_ara_std=sys_ara_std,
        sys_base=sys_base,
        sys_base_plus=sys_base_plus,
        horizons=horizons,
        scores=summary,
        persistence=pers_summary,
    )


print("Loading ENSO and solar datasets from workspace root...")
nino = pd.read_csv(
    os.path.join(WORKSPACE_ROOT, "Nino34", "nino34.long.anom.csv"),
    skiprows=1,
    names=["d", "v"],
    header=None,
    sep=",",
    engine="python",
)
NINO = pd.to_numeric(nino["v"], errors="coerce").dropna().values.astype(float)
NINO = NINO[NINO > -50]

silso = pd.read_csv(
    os.path.join(WORKSPACE_ROOT, "SILSO_Solar", "SN_m_tot_V2.0.csv"),
    sep=";",
    header=None,
    names=["y", "m", "dy", "v", "s", "n", "mk"],
)
SUN = pd.to_numeric(silso["v"], errors="coerce").dropna().values.astype(float)
SUN = SUN[SUN >= 0]

enso_res = run_one(NINO, "ENSO", 47.0, [1, 6, 12, 60, 120], n_anchors=60, test_window=30 * 12)
solar_res = run_one(SUN, "Solar SILSO", 132.0, [6, 12, 60, 132, 264], n_anchors=60, test_window=100 * 12)

OUT = os.path.join(HERE, "ara_rung_coordinate_proper_data.js")
with open(OUT, "w", encoding="utf-8") as f:
    f.write(
        "window.ARA_RUNG_COORDINATE_PROPER = "
        + json.dumps(
            {
                "date": "2026-05-20",
                "method": "strict-causal Butterworth/SOS ARA-rung coordinate test",
                "coordinate": "k + ARA_k/2 with 2^(-distance) decay",
                "enso": enso_res,
                "solar": solar_res,
            },
            default=str,
        )
        + ";\n"
    )
print(f"\nSaved -> {OUT}")

