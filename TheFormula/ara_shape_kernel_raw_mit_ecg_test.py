"""
ara_shape_kernel_raw_mit_ecg_test.py

Strict-causal ARA shape-kernel test on raw MIT-BIH Normal Sinus Rhythm ECG.

This is the direct version of Dylan's idea:
  - each rung learns its own accumulate/release shape from past data only
  - each rung measures its own ARA from past data only
  - future ECG voltage is reconstructed by overlapping the rung projections
  - shape variants can bias the overlap toward higher/longer rungs

Dataset:
  F:/SystemFormulaFolder/mit-bih-normal-sinus-rhythm-database-1.0.0/16265.dat
  WFDB format 212, fs=128 Hz, channel 0 by default.

No WFDB package is required; the script reads the 212 format directly.
"""

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, find_peaks, lfilter

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
WORKSPACE_ROOT = REPO_ROOT.parent.parent

PHI = 1.6180339887498949
FS = 128.0
GRID_N = 101
GRID = np.linspace(0.0, 1.0, GRID_N)
FALLBACK_RELEASE = np.cos(np.pi * GRID)
FALLBACK_ACCUMULATE = -np.cos(np.pi * GRID)


def read_wfdb_212(path, max_samples=None):
    # Format 212 stores one sample from each of two channels in every 3 bytes.
    byte_count = None if max_samples is None else int(max_samples) * 3
    raw = np.fromfile(path, dtype=np.uint8, count=-1 if byte_count is None else byte_count)
    if len(raw) < 3:
        raise ValueError(f"Not enough bytes in {path}")
    raw = raw[: len(raw) - (len(raw) % 3)]
    b = raw.reshape(-1, 3).astype(np.int16)
    s0 = b[:, 0] + ((b[:, 1] & 0x0F) << 8)
    s1 = (b[:, 2] << 4) + ((b[:, 1] & 0xF0) >> 4)
    s0 = np.where(s0 >= 2048, s0 - 4096, s0).astype(float)
    s1 = np.where(s1 >= 2048, s1 - 4096, s1).astype(float)
    out = np.column_stack([s0, s1])
    return out[:max_samples] if max_samples is not None else out


def load_raw_ecg(record="16265", channel=0, minutes=30):
    root = WORKSPACE_ROOT / "mit-bih-normal-sinus-rhythm-database-1.0.0"
    dat_path = root / f"{record}.dat"
    hea_path = root / f"{record}.hea"
    max_samples = int(minutes * 60 * FS)
    raw = read_wfdb_212(dat_path, max_samples=max_samples)[:, channel]
    return raw, dat_path, hea_path


def estimate_heart_period_samples(x, fs=FS):
    z = (x - np.median(x)) / max(np.std(x), 1e-9)
    peaks, _ = find_peaks(z, distance=int(fs * 0.35), prominence=1.5)
    if len(peaks) < 5:
        peaks, _ = find_peaks(-z, distance=int(fs * 0.35), prominence=1.5)
    if len(peaks) < 5:
        return fs * 0.8, int(len(peaks))
    rr = np.diff(peaks)
    rr = rr[(rr > fs * 0.35) & (rr < fs * 1.6)]
    if len(rr) == 0:
        return fs * 0.8, int(len(peaks))
    return float(np.median(rr)), int(len(peaks))


def causal_bandpass_fixed_mean(arr, period, center_mean, bw=0.42, order=2):
    arr = np.asarray(arr, dtype=float)
    n = len(arr)
    f_c = 1.0 / float(period)
    nyq = 0.5
    lo = max(1e-6, (1.0 - bw) * f_c / nyq)
    hi = min(0.999, (1.0 + bw) * f_c / nyq)
    if lo >= hi:
        return np.zeros(n, dtype=float)
    b, a = butter(order, [lo, hi], btype="bandpass")
    return lfilter(b, a, arr - center_mean)


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


def kernel_from_bandpass(bp, period, max_cycles=120):
    bp = np.asarray(bp, dtype=float)
    if len(bp) < max(16, int(4 * period)):
        return fallback_kernel()

    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.025)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.45)))
    if len(peaks) < 5:
        return fallback_kernel()

    releases = []
    accumulates = []
    recent_peaks = peaks[-(max_cycles + 1) :]
    for p0, p1 in zip(recent_peaks[:-1], recent_peaks[1:]):
        if p1 <= p0 + 4:
            continue
        span = p1 - p0
        if span < 0.28 * period or span > 2.8 * period:
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
        norm = np.clip((seg - center) / amp, -1.35, 1.35)

        rel = interp_segment(norm[: trough + 1])
        acc = interp_segment(norm[trough:])
        if rel is not None and acc is not None:
            releases.append(rel)
            accumulates.append(acc)

    if len(releases) < 5 or len(accumulates) < 5:
        return fallback_kernel()

    release = gaussian_filter1d(np.median(np.vstack(releases), axis=0), 0.8)
    accumulate = gaussian_filter1d(np.median(np.vstack(accumulates), axis=0), 0.8)
    release[0], release[-1] = 1.0, -1.0
    accumulate[0], accumulate[-1] = -1.0, 1.0
    return {
        "release": np.clip(release, -1.25, 1.25),
        "accumulate": np.clip(accumulate, -1.25, 1.25),
        "n_cycles": int(len(releases)),
        "fallback": False,
    }


def measure_rung_ara_from_bp(bp, period):
    smoothed = gaussian_filter1d(np.asarray(bp, dtype=float), max(1, int(period * 0.025)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.45)))
    if len(peaks) < 3:
        return None
    aras = []
    for p0, p1 in zip(peaks[:-1], peaks[1:]):
        seg = smoothed[p0 : p1 + 1]
        if len(seg) < 5:
            continue
        trough_fraction = int(np.argmin(seg)) / max(1, len(seg) - 1)
        trough_fraction = max(0.08, min(0.92, trough_fraction))
        aras.append((1.0 - trough_fraction) / trough_fraction)
    if not aras:
        return None
    return float(np.mean(np.clip(aras, 0.15, 6.0)))


def release_fraction(ara):
    ara = float(np.clip(ara if np.isfinite(ara) else 1.0, 0.15, 6.0))
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


def read_amp_theta(bp_to_t, period):
    p_int = max(3, int(round(period)))
    if len(bp_to_t) < 2 * p_int + 5:
        return None
    last_cycle = bp_to_t[-p_int:]
    amp = float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)
    if amp < 1e-9:
        return None
    v_recent = float(bp_to_t[-1])
    v_prev = float(bp_to_t[-2])
    ratio = max(-0.99, min(0.99, v_recent / amp))
    theta = float(np.arccos(ratio) * (-1.0 if (v_recent - v_prev) > 0 else 1.0))
    return amp, theta


def make_rungs(home_period, base, offsets):
    out = []
    for off in offsets:
        period = home_period * (base ** off)
        if period >= 6:
            out.append({"offset": int(off), "period": float(period)})
    return out


def rung_weights(rungs, home_ara, decay_base=2.0, high_bias=0.0):
    home_pos = home_ara / 2.0
    raw = []
    for r in rungs:
        pos = r["offset"] + r["ara"] / 2.0
        dist = abs(pos - home_pos)
        raw.append((decay_base ** (-dist)) * (2.0 ** (high_bias * r["offset"])))
    weights = np.asarray(raw, dtype=float)
    if weights.sum() <= 0:
        return np.ones(len(rungs), dtype=float) / max(1, len(rungs))
    return weights / weights.sum()


def build_state(bp_by_label, t, home_ara):
    rungs = []
    shape_cycles = []
    for item in bp_by_label:
        bp = item["bp"][:t]
        period = item["period"]
        amp_theta = read_amp_theta(bp, period)
        if amp_theta is None:
            continue
        amp, theta = amp_theta
        kernel = kernel_from_bandpass(bp, period)
        ara = measure_rung_ara_from_bp(bp, period)
        if ara is None or not np.isfinite(ara):
            ara = home_ara
        phase = infer_phase_from_shape(bp, amp, ara, kernel)
        rungs.append(
            {
                "offset": item["offset"],
                "period": period,
                "amp": amp,
                "theta": theta,
                "ara": float(ara),
                "phase": float(phase),
                "kernel": kernel,
            }
        )
        shape_cycles.append(kernel["n_cycles"])
    return rungs, shape_cycles


def predict(rungs, h, mean_train, home_ara, mode, high_bias):
    if not rungs:
        return float("nan")
    weights = rung_weights(rungs, home_ara, decay_base=2.0, high_bias=high_bias)
    contrib = 0.0
    for w, r in zip(weights, rungs):
        if mode == "cosine":
            value = np.cos(r["theta"] + 2.0 * np.pi * h / r["period"])
        else:
            value = shape_value_at_phase(r["phase"] + h / r["period"], r["ara"], r["kernel"])
        contrib += w * r["amp"] * value
    return mean_train + contrib


def score(records):
    preds = np.asarray([x[0] for x in records], dtype=float)
    truths = np.asarray([x[1] for x in records], dtype=float)
    pers = np.asarray([x[2] for x in records], dtype=float)
    if len(preds) < 5:
        return {"n": int(len(preds))}
    corr = float(np.corrcoef(preds, truths)[0, 1]) if preds.std() > 1e-9 and truths.std() > 1e-9 else 0.0
    mae = float(np.mean(np.abs(preds - truths)))
    pers_mae = float(np.mean(np.abs(pers - truths)))
    r2p = float(1.0 - np.sum((truths - preds) ** 2) / np.sum((truths - pers) ** 2))
    direction = float(np.mean(np.sign(preds - pers) == np.sign(truths - pers)))
    return {"n": int(len(preds)), "corr": corr, "mae": mae, "pers_mae": pers_mae, "r2_persistence": r2p, "direction": direction}


def run():
    record = "16265"
    channel = 0
    raw, dat_path, hea_path = load_raw_ecg(record=record, channel=channel, minutes=30)
    train0 = int(5 * 60 * FS)
    scale_mean = float(np.mean(raw[:train0]))
    scale_std = float(np.std(raw[:train0])) + 1e-9
    x = (raw - scale_mean) / scale_std

    heart_period, n_peaks = estimate_heart_period_samples(raw[:train0], fs=FS)
    offsets = list(range(-3, 7))
    configs = [
        ("phi coord cosine", PHI, "cosine", 0.0),
        ("phi coord shape", PHI, "shape", 0.0),
        ("phi coord shape high0.5", PHI, "shape", 0.5),
        ("2 coord cosine", 2.0, "cosine", 0.0),
        ("2 coord shape", 2.0, "shape", 0.0),
        ("2 coord shape high0.5", 2.0, "shape", 0.5),
        ("2 coord shape high1.0", 2.0, "shape", 1.0),
    ]
    horizons = [8, 16, 32, 64, int(round(heart_period)), 128, 256]
    horizon_labels = {h: f"{1000*h/FS:.0f}ms" for h in horizons}
    horizon_labels[int(round(heart_period))] = "1beat"

    anchors = np.linspace(train0, int(25 * 60 * FS), 420).astype(int)
    cumsum = np.cumsum(np.insert(x, 0, 0.0))
    records = {name: {h: [] for h in horizons} for name, *_ in configs}
    cycle_counts = {name: [] for name, *_ in configs}

    print("Raw MIT-BIH ECG ARA shape-overlap test")
    print("=" * 110)
    print(f"record={record}, channel={channel}, fs={FS:.0f}Hz, source={dat_path}")
    print(f"samples={len(x)}, duration={len(x)/FS/60:.1f}min, origins={len(anchors)}")
    print(f"estimated heart period={heart_period:.1f} samples ({1000*heart_period/FS:.1f}ms), peaks in first 5min={n_peaks}")
    print()

    t0 = time.time()
    for cfg_name, base, mode, high_bias in configs:
        rung_defs = make_rungs(heart_period, base, offsets)
        bp_by_label = []
        for r in rung_defs:
            bp = causal_bandpass_fixed_mean(x, r["period"], center_mean=0.0)
            bp_by_label.append({"offset": r["offset"], "period": r["period"], "bp": bp})

        for i, t in enumerate(anchors, 1):
            home_period = heart_period
            home_bp = causal_bandpass_fixed_mean(x[:t], home_period, center_mean=0.0)
            home_ara = measure_rung_ara_from_bp(home_bp, home_period)
            if home_ara is None or not np.isfinite(home_ara):
                home_ara = 1.0
            mean_train = float((cumsum[t] - cumsum[0]) / t)
            state, counts = build_state(bp_by_label, t, home_ara)
            cycle_counts[cfg_name].extend(counts)
            for h in horizons:
                if t + h >= len(x):
                    continue
                pred = predict(state, h, mean_train, home_ara, mode=mode, high_bias=high_bias)
                if np.isfinite(pred):
                    records[cfg_name][h].append((pred, float(x[t + h]), float(x[t - 1])))

        print(f"  {cfg_name:26s} done in {time.time() - t0:.1f}s")

    summary = {name: {h: score(recs) for h, recs in by_h.items()} for name, by_h in records.items()}
    shape_summary = {
        name: {
            "mean_cycles": float(np.mean(vals)) if vals else 0.0,
            "min_cycles": int(np.min(vals)) if vals else 0,
            "max_cycles": int(np.max(vals)) if vals else 0,
        }
        for name, vals in cycle_counts.items()
    }

    print("\nMAE on standardized raw ECG voltage")
    print(f"  {'config':26s} " + " ".join(f"{horizon_labels[h]:>8s}" for h in horizons))
    for name in summary:
        row = [f"{name:26s}"]
        for h in horizons:
            s = summary[name][h]
            row.append(f" {s['mae']:>8.4f}" if "mae" in s else "        -")
        print("".join(row))

    print("\nWinners excluding persistence:")
    for h in horizons:
        cands = []
        for name, by_h in summary.items():
            if "mae" in by_h[h]:
                cands.append((by_h[h]["mae"], name))
        cands.sort(key=lambda x: x[0])
        if cands:
            best_mae, best_name = cands[0]
            pers_mae = summary[best_name][h]["pers_mae"]
            print(f"  {horizon_labels[h]:>6}: {best_name}  MAE={best_mae:.4f}  persistence={pers_mae:.4f}")

    out = {
        "date": "2026-05-21",
        "method": "strict-causal raw ECG rung-local ARA shape overlap",
        "record": record,
        "channel": channel,
        "source": str(dat_path),
        "header": str(hea_path),
        "fs": FS,
        "duration_minutes": len(x) / FS / 60,
        "origin_count": int(len(anchors)),
        "heart_period_samples": heart_period,
        "heart_period_ms": 1000.0 * heart_period / FS,
        "first_train_r_peaks": n_peaks,
        "scale_mean_raw": scale_mean,
        "scale_std_raw": scale_std,
        "horizons": {str(h): horizon_labels[h] for h in horizons},
        "shape_cycles": shape_summary,
        "scores": summary,
    }
    out_path = HERE / "ara_shape_kernel_raw_mit_ecg_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_SHAPE_KERNEL_RAW_MIT_ECG = " + json.dumps(out, default=str) + ";\n")
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    run()
