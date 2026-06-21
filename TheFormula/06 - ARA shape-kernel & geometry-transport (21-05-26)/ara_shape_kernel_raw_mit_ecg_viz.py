"""
Generate a compact visualization dataset for the raw MIT ECG ARA shape test.

The test summary file stores metrics only. This script recomputes a small,
strict-causal prediction trace for a readable ECG window so the HTML view can
overlay:
  - actual raw ECG
  - ARA shape prediction
  - persistence forecast
"""

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ara_shape_kernel_raw_mit_ecg_test import (
    FS,
    PHI,
    build_state,
    causal_bandpass_fixed_mean,
    estimate_heart_period_samples,
    load_raw_ecg,
    make_rungs,
    measure_rung_ara_from_bp,
    rung_weights,
    shape_value_at_phase,
)


def predict_act_shape(state, h, current_value, home_ara, high_bias):
    if not state:
        return float("nan")
    weights = rung_weights(state, home_ara, decay_base=2.0, high_bias=high_bias)
    delta = 0.0
    for w, r in zip(weights, state):
        now = shape_value_at_phase(r["phase"], r["ara"], r["kernel"])
        future = shape_value_at_phase(r["phase"] + h / r["period"], r["ara"], r["kernel"])
        delta += w * r["amp"] * (future - now)
    return current_value + delta


def build_trace():
    raw, dat_path, _ = load_raw_ecg(record="16265", channel=0, minutes=30)
    train0 = int(5 * 60 * FS)
    scale_mean = float(np.mean(raw[:train0]))
    scale_std = float(np.std(raw[:train0])) + 1e-9
    x = (raw - scale_mean) / scale_std
    heart_period, n_peaks = estimate_heart_period_samples(raw[:train0], fs=FS)

    target_start = int(10 * 60 * FS)
    target_end = target_start + int(18 * FS)
    actual_pad = int(0.75 * FS)
    actual_idx = np.arange(target_start - actual_pad, target_end + actual_pad)

    configs = [
        {
            "key": "125ms",
            "label": "125ms - phi shape high0.5",
            "h": 16,
            "base": PHI,
            "high_bias": 0.5,
        },
        {
            "key": "500ms",
            "label": "500ms - phi shape high0.5",
            "h": 64,
            "base": PHI,
            "high_bias": 0.5,
        },
        {
            "key": "1beat",
            "label": "1 beat - 2.0 shape high1.0",
            "h": int(round(heart_period)),
            "base": 2.0,
            "high_bias": 1.0,
        },
        {
            "key": "1000ms",
            "label": "1000ms - 2.0 shape high1.0",
            "h": 128,
            "base": 2.0,
            "high_bias": 1.0,
        },
    ]

    horizons = {}
    t0 = time.time()
    for cfg in configs:
        rung_defs = make_rungs(heart_period, cfg["base"], list(range(-3, 7)))
        bp_by_label = []
        for r in rung_defs:
            bp = causal_bandpass_fixed_mean(x, r["period"], center_mean=0.0)
            bp_by_label.append({"offset": r["offset"], "period": r["period"], "bp": bp})

        points = []
        for target in range(target_start, target_end, 16):
            origin = target - cfg["h"]
            if origin <= train0:
                continue
            home_bp = causal_bandpass_fixed_mean(x[:origin], heart_period, center_mean=0.0)
            home_ara = measure_rung_ara_from_bp(home_bp, heart_period)
            if home_ara is None or not np.isfinite(home_ara):
                home_ara = 1.0

            state, cycle_counts = build_state(bp_by_label, origin, home_ara)
            pred_z = predict_act_shape(state, cfg["h"], x[origin - 1], home_ara, cfg["high_bias"])
            if not np.isfinite(pred_z):
                continue

            points.append(
                {
                    "t": float(target / FS),
                    "actual": float(raw[target]),
                    "pred": float(pred_z * scale_std + scale_mean),
                    "persistence": float(raw[origin - 1]),
                    "origin_t": float(origin / FS),
                    "shape_cycles_mean": float(np.mean(cycle_counts)) if cycle_counts else 0.0,
                    "home_ara": float(home_ara),
                }
            )

        actual = np.asarray([p["actual"] for p in points], dtype=float)
        pred = np.asarray([p["pred"] for p in points], dtype=float)
        pers = np.asarray([p["persistence"] for p in points], dtype=float)
        horizons[cfg["key"]] = {
            "label": cfg["label"],
            "h_samples": int(cfg["h"]),
            "h_ms": float(1000.0 * cfg["h"] / FS),
            "base": float(cfg["base"]),
            "high_bias": float(cfg["high_bias"]),
            "points": points,
            "mae_pred": float(np.mean(np.abs(pred - actual))) if len(points) else None,
            "mae_persistence": float(np.mean(np.abs(pers - actual))) if len(points) else None,
            "shape_cycles_mean": float(np.mean([p["shape_cycles_mean"] for p in points])) if points else 0.0,
        }
        print(f"{cfg['label']} generated with {len(points)} points in {time.time() - t0:.1f}s")

    return {
        "date": "2026-05-21",
        "source": str(dat_path),
        "record": "16265",
        "channel": 0,
        "fs": FS,
        "scale": "raw ADC counts",
        "prediction_type": "ACT-style ARA shape delta from current value",
        "window": {
            "start_s": float(target_start / FS),
            "end_s": float(target_end / FS),
        },
        "heart_period_samples": float(heart_period),
        "heart_period_ms": float(1000.0 * heart_period / FS),
        "first_train_r_peaks": int(n_peaks),
        "actual_trace": {
            "t": [float(i / FS) for i in actual_idx],
            "y": [float(raw[i]) for i in actual_idx],
        },
        "horizons": horizons,
    }


if __name__ == "__main__":
    data = build_trace()
    out_path = HERE / "ara_shape_kernel_raw_mit_ecg_viz_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_RAW_ECG_VIZ = " + json.dumps(data, default=str) + ";\n")
    print(f"Saved -> {out_path}")
