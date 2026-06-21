"""
ara_shape_kernel_ecg_test.py

Strict-causal ARA-shaped accumulate/release kernel test on ECG RR intervals.

This uses the repo's existing ECG convention:
  - subject: nsr001
  - signal: RR interval in ms
  - uniform grid: 10-second samples

Important scope note:
  This is ECG RR/HRV envelope prediction, not raw PQRST morphology prediction.

At each rolling origin t:
  - kernels are learned from rr[:t] only
  - rung ARA is measured from rr[:t] only
  - predictions are scored against future RR values only after prediction
"""

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
WORKSPACE_ROOT = REPO_ROOT.parent.parent

sys.path.insert(0, str(REPO_ROOT))
from ara_framework import _measure_rung, causal_bandpass

PHI = 1.6180339887498949
DT = 10.0
GRID_N = 101
GRID = np.linspace(0.0, 1.0, GRID_N)
FALLBACK_RELEASE = np.cos(np.pi * GRID)
FALLBACK_ACCUMULATE = -np.cos(np.pi * GRID)


def load_ecg_rr():
    path = WORKSPACE_ROOT / "TheFormula" / "nsr001_rr.csv"
    df = pd.read_csv(path)
    ecg_t = df["time_s"].values.astype(float)
    ecg_rr = df["rr_ms"].values.astype(float)
    t_uniform = np.arange(0, int(ecg_t[-1]) - 1, int(DT))
    rr_uniform = np.interp(t_uniform, ecg_t, ecg_rr)
    return rr_uniform, path


def fallback_kernel():
    return {
        "release": FALLBACK_RELEASE.copy(),
        "accumulate": FALLBACK_ACCUMULATE.copy(),
        "n_cycles": 0,
        "fallback": True,
    }


def interp_segment(values):
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        return None
    src = np.linspace(0.0, 1.0, len(values))
    return np.interp(GRID, src, values)


def kernel_from_bandpass(bp, period, max_cycles=80):
    bp = np.asarray(bp, dtype=float)
    if len(bp) < max(16, int(3 * period)):
        return fallback_kernel()

    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.45)))
    if len(peaks) < 4:
        return fallback_kernel()

    releases = []
    accumulates = []
    recent_peaks = peaks[-(max_cycles + 1) :]
    for p0, p1 in zip(recent_peaks[:-1], recent_peaks[1:]):
        if p1 <= p0 + 4:
            continue
        span = p1 - p0
        if span < 0.3 * period or span > 2.5 * period:
            continue

        seg = smoothed[p0 : p1 + 1]
        trough = int(np.argmin(seg))
        if trough < 2 or trough > len(seg) - 3:
            continue

        peak_level = float((seg[0] + seg[-1]) / 2.0)
        trough_level = float(seg[trough])
        amp = (peak_level - trough_level) / 2.0
        if amp <= 1e-9:
            continue
        center = (peak_level + trough_level) / 2.0
        norm = np.clip((seg - center) / amp, -1.25, 1.25)

        rel = interp_segment(norm[: trough + 1])
        acc = interp_segment(norm[trough:])
        if rel is not None and acc is not None:
            releases.append(rel)
            accumulates.append(acc)

    if len(releases) < 4 or len(accumulates) < 4:
        return fallback_kernel()

    release = gaussian_filter1d(np.median(np.vstack(releases), axis=0), 1.0)
    accumulate = gaussian_filter1d(np.median(np.vstack(accumulates), axis=0), 1.0)
    release[0], release[-1] = 1.0, -1.0
    accumulate[0], accumulate[-1] = -1.0, 1.0
    return {
        "release": np.clip(release, -1.2, 1.2),
        "accumulate": np.clip(accumulate, -1.2, 1.2),
        "n_cycles": int(len(releases)),
        "fallback": False,
    }


def measure_rung_ara_from_bp(bp, period):
    smoothed = gaussian_filter1d(np.asarray(bp, dtype=float), max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.45)))
    if len(peaks) < 3:
        return None

    aras = []
    for p0, p1 in zip(peaks[:-1], peaks[1:]):
        seg = smoothed[p0 : p1 + 1]
        if len(seg) < 5:
            continue
        trough_fraction = int(np.argmin(seg)) / max(1, len(seg) - 1)
        trough_fraction = max(0.15, min(0.85, trough_fraction))
        aras.append((1.0 - trough_fraction) / trough_fraction)
    if not aras:
        return None
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


def release_fraction(ara):
    ara = float(np.clip(ara if np.isfinite(ara) else 1.0, 0.3, 3.0))
    return 1.0 / (1.0 + ara)


def infer_phase_from_shape(bp, amp, ara, kernel):
    if len(bp) < 2 or amp <= 1e-9:
        return 0.0
    v = float(np.clip(bp[-1] / amp, -1.0, 1.0))
    falling = float(bp[-1] - bp[-2]) < 0.0
    split = release_fraction(ara)
    if falling:
        idx = int(np.argmin(np.abs(kernel["release"] - v)))
        return split * (idx / max(1, GRID_N - 1))
    idx = int(np.argmin(np.abs(kernel["accumulate"] - v)))
    return split + (1.0 - split) * (idx / max(1, GRID_N - 1))


def shape_value_at_phase(phase, ara, kernel):
    phase = float(phase % 1.0)
    split = release_fraction(ara)
    if phase < split:
        u = 0.0 if split <= 1e-9 else phase / split
        return float(np.interp(u, GRID, kernel["release"]))
    u = (phase - split) / max(1e-9, 1.0 - split)
    return float(np.interp(u, GRID, kernel["accumulate"]))


def safe_base(x):
    if not np.isfinite(x):
        return 1.05
    return max(1.05, float(x))


def period_seconds(base, k):
    return float(base**int(k))


def period_samples(base, k):
    return period_seconds(base, k) / DT


def rung_range(base, n_samples, min_seconds=50.0, max_rungs=64):
    max_seconds = min(4 * 3600.0, n_samples * DT / 3.0)
    k_lo = max(1, int(math.floor(math.log(min_seconds) / math.log(base))))
    k_hi = int(math.ceil(math.log(max_seconds) / math.log(base)))
    rungs = list(range(k_lo, k_hi + 1))
    if len(rungs) <= max_rungs:
        return rungs
    idx = np.linspace(0, len(rungs) - 1, max_rungs).round().astype(int)
    return sorted({rungs[i] for i in idx})


def estimate_system_ara(data, home_period_samples, anchors):
    vals = []
    for t in anchors:
        bp = causal_bandpass(data[:t], home_period_samples)
        ara = measure_rung_ara_from_bp(bp, home_period_samples)
        if ara is not None and np.isfinite(ara):
            vals.append(float(ara))
    if not vals:
        return 1.0, 0.0
    return float(np.mean(vals)), float(np.std(vals))


def extract_topology(data, t, rungs_k, home_k, base, home_kernel, home_ara, pin_factor=3):
    arr = np.asarray(data, dtype=float)
    rungs = []
    for k in rungs_k:
        period = period_samples(base, k)
        if period < 3 or pin_factor * period > t:
            continue
        bp = causal_bandpass(arr[:t], period)
        rec = _measure_rung(bp, period, k)
        if rec is None:
            continue
        ara = measure_rung_ara_from_bp(bp, period)
        if ara is None or not np.isfinite(ara):
            ara = home_ara
        local_kernel = kernel_from_bandpass(bp, period)
        rec["ara"] = float(ara)
        rec["phase_home"] = infer_phase_from_shape(bp, rec["amp"], ara, home_kernel)
        rec["phase_rung"] = infer_phase_from_shape(bp, rec["amp"], ara, local_kernel)
        rec["kernel_rung"] = local_kernel
        rungs.append(rec)
    return {
        "v_now": float(arr[t - 1]),
        "mean_train": float(np.mean(arr[:t])),
        "home_k": int(home_k),
        "rungs": rungs,
    }


def coord_weights(topo, decay_base=2.0):
    if not topo["rungs"]:
        return None
    ara_at = {s["k"]: s.get("ara") for s in topo["rungs"] if s.get("ara") is not None}
    home_ara = ara_at.get(topo["home_k"])
    if home_ara is None:
        home_ara = float(np.mean(list(ara_at.values()))) if ara_at else 1.0
    home_pos = topo["home_k"] + home_ara / 2.0
    distances = []
    for s in topo["rungs"]:
        ara_k = s.get("ara", home_ara)
        distances.append(abs((s["k"] + ara_k / 2.0) - home_pos))
    weights = np.array([decay_base ** (-d) for d in distances], dtype=float)
    if weights.sum() <= 0:
        return None
    return weights / weights.sum()


def k_weights(topo, decay_base):
    if not topo["rungs"]:
        return None
    weights = np.array([decay_base ** (-abs(s["k"] - topo["home_k"])) for s in topo["rungs"]], dtype=float)
    if weights.sum() <= 0:
        return None
    return weights / weights.sum()


def predict_cosine(topo, h, weight_mode, decay_base):
    weights = coord_weights(topo, decay_base) if weight_mode == "coord" else k_weights(topo, decay_base)
    if weights is None:
        return float("nan")
    contrib = 0.0
    for j, s in enumerate(topo["rungs"]):
        contrib += weights[j] * s["amp"] * np.cos(s["theta"] + 2.0 * np.pi * h / s["period"])
    return topo["mean_train"] + contrib


def predict_shape(topo, h, weight_mode, decay_base, home_kernel, phase_mode):
    weights = coord_weights(topo, decay_base) if weight_mode == "coord" else k_weights(topo, decay_base)
    if weights is None:
        return float("nan")
    contrib = 0.0
    for j, s in enumerate(topo["rungs"]):
        if phase_mode == "home":
            kernel = home_kernel
            phase = s["phase_home"]
        else:
            kernel = s["kernel_rung"]
            phase = s["phase_rung"]
        contrib += weights[j] * s["amp"] * shape_value_at_phase(phase + h / s["period"], s["ara"], kernel)
    return topo["mean_train"] + contrib


def score(records):
    preds = np.asarray([r[0] for r in records], dtype=float)
    truths = np.asarray([r[1] for r in records], dtype=float)
    pers = np.asarray([r[2] for r in records], dtype=float)
    if len(preds) < 5:
        return {"n": int(len(preds))}
    corr = float(np.corrcoef(preds, truths)[0, 1]) if preds.std() > 1e-9 and truths.std() > 1e-9 else 0.0
    mae = float(np.mean(np.abs(preds - truths)))
    pers_mae = float(np.mean(np.abs(pers - truths)))
    r2p = float(1.0 - np.sum((truths - preds) ** 2) / np.sum((truths - pers) ** 2))
    direction = float(np.mean(np.sign(preds - pers) == np.sign(truths - pers)))
    return {"n": int(len(preds)), "corr": corr, "mae": mae, "pers_mae": pers_mae, "r2_persistence": r2p, "direction": direction}


def run():
    rr, source_path = load_ecg_rr()
    n = len(rr)
    home_seconds_phi = PHI**19
    home_period_phi = home_seconds_phi / DT
    horizons = [6, 30, 180, 360, 720]
    horizon_labels = {6: "1min", 30: "5min", 180: "30min", 360: "1h", 720: "2h"}
    min_train = 3000
    step = 6
    anchors = list(range(min_train, n - max(horizons), step))

    sys_ara, sys_ara_std = estimate_system_ara(rr, home_period_phi, anchors[:: max(1, len(anchors) // 40)])
    sys_base = safe_base(sys_ara)
    sys_plus_base = safe_base(1.0 + sys_ara)

    configs = [
        ("phi + phi-k cosine", PHI, "k", PHI, "cos", "home"),
        ("phi + coord cosine", PHI, "coord", 2.0, "cos", "home"),
        ("phi + coord shape-home", PHI, "coord", 2.0, "shape", "home"),
        ("phi + coord shape-rung", PHI, "coord", 2.0, "shape", "rung"),
        ("2 + coord cosine", 2.0, "coord", 2.0, "cos", "home"),
        ("2 + coord shape-home", 2.0, "coord", 2.0, "shape", "home"),
        ("2 + coord shape-rung", 2.0, "coord", 2.0, "shape", "rung"),
        ("1+sysARA + coord shape-rung", sys_plus_base, "coord", 2.0, "shape", "rung"),
    ]

    config_records = []
    for label, base, weight_mode, decay_base, predictor, phase_mode in configs:
        home_k = round(math.log(home_seconds_phi) / math.log(base))
        config_records.append(
            {
                "label": label,
                "base": base,
                "weight_mode": weight_mode,
                "decay_base": decay_base,
                "predictor": predictor,
                "phase_mode": phase_mode,
                "home_k": home_k,
                "rungs_k": rung_range(base, n),
            }
        )

    records = {c["label"]: {h: [] for h in horizons} for c in config_records}
    shape_cycle_counts = []
    t0 = time.time()

    print("ECG RR/HRV shape-kernel test")
    print("=" * 104)
    print(f"source={source_path}")
    print(f"samples={n}, dt={DT:.0f}s, duration={n * DT / 3600:.2f}h, origins={len(anchors)}")
    print(f"home_period={home_seconds_phi:.1f}s ({home_period_phi:.1f} samples), sys_ara={sys_ara:.3f} +/- {sys_ara_std:.3f}")
    print()

    for idx, t in enumerate(anchors, 1):
        home_bp = causal_bandpass(rr[:t], home_period_phi)
        home_kernel = kernel_from_bandpass(home_bp, home_period_phi)
        shape_cycle_counts.append(home_kernel["n_cycles"])
        home_ara = measure_rung_ara_from_bp(home_bp, home_period_phi)
        if home_ara is None or not np.isfinite(home_ara):
            home_ara = sys_ara

        topo_cache = {}
        for c in config_records:
            key = (round(c["base"], 10), c["home_k"], tuple(c["rungs_k"]))
            if key not in topo_cache:
                topo_cache[key] = extract_topology(rr, t, c["rungs_k"], c["home_k"], c["base"], home_kernel, home_ara)
            topo = topo_cache[key]
            for h in horizons:
                if t + h >= n:
                    continue
                if c["predictor"] == "cos":
                    pred = predict_cosine(topo, h, c["weight_mode"], c["decay_base"])
                else:
                    pred = predict_shape(topo, h, c["weight_mode"], c["decay_base"], home_kernel, c["phase_mode"])
                if np.isfinite(pred):
                    records[c["label"]][h].append((pred, float(rr[t + h - 1]), float(rr[t - 1])))

        if idx % 150 == 0:
            print(f"  processed {idx}/{len(anchors)} origins in {time.time() - t0:.1f}s")

    summary = {label: {h: score(recs) for h, recs in by_h.items()} for label, by_h in records.items()}

    print("\nMAE vs future RR interval (ms)")
    print(f"  {'config':31s} " + " ".join(f"{horizon_labels[h]:>8s}" for h in horizons))
    for label in summary:
        row = [f"{label:31s}"]
        for h in horizons:
            s = summary[label][h]
            row.append(f" {s['mae']:>8.2f}" if "mae" in s else "        -")
        print("".join(row))

    print("\nWinners excluding persistence:")
    for h in horizons:
        cands = []
        for label, by_h in summary.items():
            if "mae" in by_h[h]:
                cands.append((by_h[h]["mae"], label))
        cands.sort(key=lambda x: x[0])
        if cands:
            best_mae, best_label = cands[0]
            pers_mae = summary[best_label][h]["pers_mae"]
            print(f"  {horizon_labels[h]:>5}: {best_label}  MAE={best_mae:.2f}ms  persistence={pers_mae:.2f}ms")

    out = {
        "date": "2026-05-21",
        "method": "strict-causal ARA accumulate/release shape kernel test",
        "scope": "ECG RR/HRV envelope, not raw PQRST morphology",
        "source": str(source_path),
        "dt_seconds": DT,
        "duration_hours": n * DT / 3600,
        "origin_count": len(anchors),
        "home_period_seconds": home_seconds_phi,
        "home_period_samples": home_period_phi,
        "system_ara": sys_ara,
        "system_ara_std": sys_ara_std,
        "sys_base": sys_base,
        "sys_plus_base": sys_plus_base,
        "shape_cycles_mean": float(np.mean(shape_cycle_counts)),
        "shape_cycles_min": int(np.min(shape_cycle_counts)),
        "shape_cycles_max": int(np.max(shape_cycle_counts)),
        "horizons": {str(h): horizon_labels[h] for h in horizons},
        "scores": summary,
    }

    out_path = HERE / "ara_shape_kernel_ecg_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_SHAPE_KERNEL_ECG = " + json.dumps(out, default=str) + ";\n")
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    run()
