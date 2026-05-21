"""
Generate visualization data for ENSO and Solar ARA shape-kernel forecasts.

The output is an HTML-friendly dataset with:
  - continuous actual series
  - strict-causal ARA/cosine predictions at target dates
  - persistence forecasts at the same target dates

This uses the same OLD-style shape projection from ara_shape_kernel_test.py,
which is the appropriate climate-timescale analogue of the shape-kernel method.
"""

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ara_shape_kernel_test import (
    PHI,
    WORKSPACE_ROOT,
    estimate_system_ara,
    extract_topology,
    kernel_from_bandpass,
    measure_rung_ara_from_bp,
    coord_weights,
    predict_cosine,
    predict_shape,
    rung_range,
    safe_base,
    shape_value_at_phase,
)
from ara_framework import causal_bandpass


def load_enso_with_dates():
    df = pd.read_csv(
        WORKSPACE_ROOT / "Nino34" / "nino34.long.anom.csv",
        skiprows=1,
        names=["date", "value"],
        header=None,
        sep=",",
        engine="python",
    )
    df["date"] = pd.to_datetime(df["date"].astype(str).str.strip(), errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()
    df = df[df["value"] > -50].reset_index(drop=True)
    return df["date"].dt.strftime("%Y-%m-%d").tolist(), df["value"].values.astype(float)


def load_solar_with_dates():
    df = pd.read_csv(
        WORKSPACE_ROOT / "SILSO_Solar" / "SN_m_tot_V2.0.csv",
        sep=";",
        header=None,
        names=["y", "m", "dy", "value", "s", "n", "mk"],
    )
    df["date"] = pd.to_datetime(
        {
            "year": pd.to_numeric(df["y"], errors="coerce"),
            "month": pd.to_numeric(df["m"], errors="coerce"),
            "day": 1,
        },
        errors="coerce",
    )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()
    df = df[df["value"] >= 0].reset_index(drop=True)
    return df["date"].dt.strftime("%Y-%m-%d").tolist(), df["value"].values.astype(float)


def score(points):
    if not points:
        return {"n": 0}
    pred = np.asarray([p["pred"] for p in points], dtype=float)
    pers = np.asarray([p["persistence"] for p in points], dtype=float)
    truth = np.asarray([p["actual"] for p in points], dtype=float)
    return {
        "n": int(len(points)),
        "mae_pred": float(np.mean(np.abs(pred - truth))),
        "mae_persistence": float(np.mean(np.abs(pers - truth))),
        "corr_pred": float(np.corrcoef(pred, truth)[0, 1]) if pred.std() > 1e-9 and truth.std() > 1e-9 else 0.0,
        "corr_persistence": float(np.corrcoef(pers, truth)[0, 1]) if pers.std() > 1e-9 and truth.std() > 1e-9 else 0.0,
    }


def make_config(label, base, weight_mode, decay_base, predictor, phase_mode, home_period, n, high_bias=0.0):
    return {
        "label": label,
        "rung_base": float(base),
        "weight_mode": weight_mode,
        "decay_base": float(decay_base),
        "predictor": predictor,
        "phase_mode": phase_mode,
        "high_bias": float(high_bias),
        "home_k": round(math.log(home_period) / math.log(base)),
        "rungs_k": rung_range(base, n),
    }


def predict_shape_ara_scale02(topo, h, home_kernel, phase_mode, high_bias=0.0):
    if topo is None or not topo.rungs:
        return float("nan")
    base_weights = coord_weights(topo, 2.0)
    if base_weights is None:
        return float("nan")
    weights = []
    for j, s in enumerate(topo.rungs):
        offset = s["k"] - topo.home_k
        amp_factor = max(float(s.get("amp", 0.0)), 1e-9)
        high_factor = 2.0 ** (high_bias * offset)
        weights.append(base_weights[j] * amp_factor * high_factor)
    weights = np.asarray(weights, dtype=float)
    if weights.sum() <= 0:
        return float("nan")
    weights /= weights.sum()

    pred02 = 0.0
    for j, s in enumerate(topo.rungs):
        kernel = home_kernel if phase_mode == "home" else s["kernel_rung"]
        phase = s["phase_home"] if phase_mode == "home" else s["phase_rung"]
        future_phase = phase + h / s["period"]
        # Shape value is -1..1; ARA-scale value is 0..2.
        pred02 += weights[j] * (1.0 + shape_value_at_phase(future_phase, s["ara"], kernel))
    return float(np.clip(pred02, 0.0, 2.0))


def build_system(name, dates, data, home_period, horizons, test_window, n_anchors=72):
    n = len(data)
    test_start = max(int(4 * home_period), n - test_window)
    anchors_for_ara = np.linspace(test_start, n - max(horizons) - 1, min(45, n_anchors)).astype(int)
    sys_ara, sys_ara_std = estimate_system_ara(data, home_period, anchors_for_ara)
    sys_base = safe_base(sys_ara)
    sys_base_plus = safe_base(1.0 + sys_ara)

    if name == "ENSO":
        configs = [
            make_config("2 + coord ARA-scale shape", 2.0, "coord", 2.0, "shape02", "rung", home_period, n),
            make_config("2 + coord ARA-scale shape high0.5", 2.0, "coord", 2.0, "shape02", "rung", home_period, n, high_bias=0.5),
            make_config("2 + coord shape-rung", 2.0, "coord", 2.0, "shape", "rung", home_period, n),
            make_config("phi + coord shape-rung", PHI, "coord", 2.0, "shape", "rung", home_period, n),
            make_config("phi + phi-k cosine", PHI, "k", PHI, "cos", "home", home_period, n),
        ]
        default_model = "2 + coord ARA-scale shape high0.5"
        default_horizon = "60"
    else:
        configs = [
            make_config("sysARA + coord shape-rung", sys_base, "coord", 2.0, "shape", "rung", home_period, n),
            make_config("phi + coord shape-home", PHI, "coord", 2.0, "shape", "home", home_period, n),
            make_config("2 + coord shape-rung", 2.0, "coord", 2.0, "shape", "rung", home_period, n),
        ]
        default_model = "sysARA + coord shape-rung"
        default_horizon = "60"

    scenarios = {}
    t0 = time.time()
    for h in horizons:
        anchors = np.linspace(test_start, n - h - 1, n_anchors).astype(int)
        topo_cache = {}
        for cfg in configs:
            points = []
            shape_cycles = []
            for t in anchors:
                data_for_topology = data
                inverse_scale = None
                if cfg["predictor"] == "shape02":
                    train_min = float(np.min(data[:t]))
                    train_max = float(np.max(data[:t]))
                    span = max(train_max - train_min, 1e-9)
                    data_for_topology = 2.0 * ((data - train_min) / span)
                    inverse_scale = (train_min, span)

                home_bp = causal_bandpass(data_for_topology[:t], home_period)
                home_kernel = kernel_from_bandpass(home_bp, home_period)
                home_ara = measure_rung_ara_from_bp(home_bp, home_period)
                if home_ara is None or not np.isfinite(home_ara):
                    home_ara = sys_ara

                key = (int(t), cfg["predictor"], round(cfg["rung_base"], 10), cfg["home_k"], tuple(cfg["rungs_k"]))
                if key not in topo_cache:
                    topo_cache[key] = extract_topology(
                        data_for_topology,
                        t,
                        cfg["rungs_k"],
                        cfg["home_k"],
                        cfg["rung_base"],
                        home_kernel,
                        home_ara,
                    )
                topo = topo_cache[key]
                if cfg["predictor"] == "cos":
                    pred = predict_cosine(topo, h, cfg["weight_mode"], cfg["decay_base"])
                elif cfg["predictor"] == "shape02":
                    pred02 = predict_shape_ara_scale02(topo, h, home_kernel, cfg["phase_mode"], cfg["high_bias"])
                    if inverse_scale is None:
                        pred = float("nan")
                    else:
                        train_min, span = inverse_scale
                        pred = train_min + 0.5 * pred02 * span
                else:
                    pred = predict_shape(topo, h, cfg["weight_mode"], cfg["decay_base"], home_kernel, cfg["phase_mode"])
                target = t + h - 1
                if np.isfinite(pred) and target < n:
                    points.append(
                        {
                            "origin_date": dates[t - 1],
                            "date": dates[target],
                            "actual": float(data[target]),
                            "pred": float(pred),
                            "persistence": float(data[t - 1]),
                            "home_ara": float(home_ara),
                            "shape_cycles": int(home_kernel["n_cycles"]),
                        }
                    )
                    shape_cycles.append(int(home_kernel["n_cycles"]))

            scenarios[f"{h}|{cfg['label']}"] = {
                "horizon": int(h),
                "model": cfg["label"],
                "model_base": cfg["rung_base"],
                "points": points,
                "score": score(points),
                "shape_cycles_mean": float(np.mean(shape_cycles)) if shape_cycles else 0.0,
            }
        print(f"{name} h={h} generated in {time.time() - t0:.1f}s")

    return {
        "name": name,
        "home_period": float(home_period),
        "sys_ara": float(sys_ara),
        "sys_ara_std": float(sys_ara_std),
        "sys_base": float(sys_base),
        "sys_base_plus": float(sys_base_plus),
        "default_model": default_model,
        "default_horizon": default_horizon,
        "horizons": [int(h) for h in horizons],
        "models": [c["label"] for c in configs],
        "series": [{"date": d, "value": float(v)} for d, v in zip(dates, data)],
        "scenarios": scenarios,
    }


def main():
    print("Generating ENSO/Solar shape-kernel visualization data...")
    enso_dates, enso = load_enso_with_dates()
    solar_dates, solar = load_solar_with_dates()

    enso_out = build_system("ENSO", enso_dates, enso, 47.0, [1, 6, 12, 60, 120], test_window=30 * 12, n_anchors=72)
    solar_out = build_system("Solar", solar_dates, solar, 132.0, [6, 12, 60, 132, 264], test_window=100 * 12, n_anchors=72)

    out = {
        "date": "2026-05-21",
        "method": "strict-causal ARA shape-kernel climate overlay",
        "note": "Predictions use data before origin only; actual target values are stored for display/scoring.",
        "systems": {
            "ENSO": enso_out,
            "Solar": solar_out,
        },
    }
    out_path = HERE / "ara_shape_kernel_climate_viz_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_SHAPE_CLIMATE_VIZ = " + json.dumps(out, default=str) + ";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()
