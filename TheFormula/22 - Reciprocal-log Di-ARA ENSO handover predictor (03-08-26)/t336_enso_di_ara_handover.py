"""T336: frozen reciprocal/log Di-ARA handover replay on ENSO.

Read T336_ENSO_DI_ARA_HANDOVER_PROTOCOL_v1_FROZEN.md before changing this file.
The implementation is deterministic and writes machine-readable results only.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "Claude4.8"
NINO_PATH = DATA / "nino34_long_anom.csv"
WWV_WEST_PATH = DATA / "wwv_west.dat"
WWV_EAST_PATH = DATA / "wwv_east.dat"

OUT_JSON = HERE / "T336_ENSO_DI_ARA_HANDOVER_RESULTS.json"
OUT_CSV = HERE / "T336_ENSO_DI_ARA_HANDOVER_FORECASTS.csv"

HORIZONS = (3, 6, 9, 12)
STATE_LAGS = (0, 1, 2, 4, 8, 12)
OCTAVE_LAGS = (1, 2, 4)
BROKEN_SHIFT = 12
MIN_LAG = BROKEN_SHIFT + max(OCTAVE_LAGS)
WALK_START = 2008.0
HOLDOUT_START = 2017.0
RIDGE_ALPHA = 1.0
EPS = 1e-9
BOOT_SEED = 20260803
BOOT_REPS = 5000
BLOCK = 12


def load_nino(path: Path) -> dict[str, float]:
    out: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) == 2 and parts[0][:4].isdigit():
            value = float(parts[1])
            if value > -99.989:
                out[parts[0][:7].replace("-", "")] = value
    return out


def load_wwv(path: Path) -> dict[str, float]:
    out: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0].isdigit() and len(parts[0]) == 6:
            out[parts[0]] = float(parts[2]) / 1e14
    return out


def decimal_year(key: str) -> float:
    return int(key[:4]) + (int(key[4:6]) - 1) / 12.0


def standardize(values: np.ndarray, end: int) -> np.ndarray:
    hist = values[: end + 1]
    mean = float(np.mean(hist))
    scale = float(np.std(hist, ddof=0))
    if scale < EPS:
        scale = 1.0
    return (values - mean) / scale


def ridge_predict(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> float:
    mean = np.mean(x_train, axis=0)
    scale = np.std(x_train, axis=0, ddof=0)
    scale[scale < EPS] = 1.0
    xs = (x_train - mean) / scale
    xt = (x_test - mean) / scale
    y_mean = float(np.mean(y_train))
    yc = y_train - y_mean
    gram = xs.T @ xs + RIDGE_ALPHA * np.eye(xs.shape[1])
    beta = np.linalg.solve(gram, xs.T @ yc)
    return float(y_mean + xt @ beta)


def base_features(j: int, t: np.ndarray, w: np.ndarray, e: np.ndarray, months: np.ndarray) -> np.ndarray:
    vals: list[float] = []
    for series in (t, w, e):
        vals.extend(float(series[j - lag]) for lag in STATE_LAGS)
    angle = 2.0 * math.pi * (int(months[j]) - 1) / 12.0
    vals.extend((math.sin(angle), math.cos(angle)))
    return np.asarray(vals, dtype=float)


def diara_features(j: int, tz: np.ndarray, rz: np.ndarray, reservoir_shift: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    continuous: list[float] = []
    radius_only: list[float] = []
    turn_only: list[float] = []
    quadrants: list[float] = []
    for lag in OCTAVE_LAGS:
        z_now = complex(float(tz[j]), float(rz[j - reservoir_shift]))
        z_prev = complex(float(tz[j - lag]), float(rz[j - lag - reservoir_shift]))
        s = (abs(z_now) + EPS) / (abs(z_prev) + EPS)
        a = math.tanh(0.5 * math.log(s))
        delta = math.atan2((z_now * z_prev.conjugate()).imag, (z_now * z_prev.conjugate()).real) / math.pi
        continuous.extend((a, delta))
        radius_only.append(a)
        turn_only.append(delta)
        q = (2 if a >= 0.0 else 0) + (1 if delta >= 0.0 else 0)
        quadrants.extend(1.0 if k == q else 0.0 for k in range(4))
    return (
        np.asarray(continuous, dtype=float),
        np.asarray(radius_only, dtype=float),
        np.asarray(turn_only, dtype=float),
        np.asarray(quadrants, dtype=float),
    )


def raw_movement_features(j: int, tz: np.ndarray, rz: np.ndarray) -> np.ndarray:
    vals: list[float] = []
    for lag in OCTAVE_LAGS:
        vals.extend((float(tz[j] - tz[j - lag]), float(rz[j] - rz[j - lag])))
    return np.asarray(vals, dtype=float)


def feature_sets(j: int, t: np.ndarray, w: np.ndarray, e: np.ndarray, months: np.ndarray, origin: int) -> dict[str, np.ndarray]:
    tz = standardize(t, origin)
    rz = standardize(w + e, origin)
    base = base_features(j, t, w, e, months)
    di, rad, turn, quad = diara_features(j, tz, rz)
    broken, _, _, _ = diara_features(j, tz, rz, reservoir_shift=BROKEN_SHIFT)
    raw = raw_movement_features(j, tz, rz)
    return {
        "base_levels": base,
        "base_raw_movement": np.concatenate((base, raw)),
        "base_diara": np.concatenate((base, di)),
        "base_radius": np.concatenate((base, rad)),
        "base_turn": np.concatenate((base, turn)),
        "base_quadrant": np.concatenate((base, quad)),
        "base_broken_diara": np.concatenate((base, broken)),
    }


def score(rows: list[dict], model: str) -> dict[str, float | int]:
    pred = np.asarray([r[model] for r in rows], dtype=float)
    truth = np.asarray([r["truth"] for r in rows], dtype=float)
    current = np.asarray([r["current"] for r in rows], dtype=float)
    clim = np.asarray([r["climatology"] for r in rows], dtype=float)
    mse = float(np.mean((pred - truth) ** 2))
    clim_mse = float(np.mean((clim - truth) ** 2))
    corr = float(np.corrcoef(pred, truth)[0, 1]) if np.std(pred) > EPS else float("nan")
    actual_change = truth - current
    pred_change = pred - current
    mask = np.abs(actual_change) > EPS
    direction = float(np.mean(np.sign(pred_change[mask]) == np.sign(actual_change[mask])))
    return {
        "n": len(rows),
        "mse": mse,
        "skill_vs_climatology": 1.0 - mse / clim_mse,
        "mae": float(np.mean(np.abs(pred - truth))),
        "corr": corr,
        "direction": direction,
        "amplitude_ratio": float(np.std(pred) / np.std(truth)) if np.std(truth) > EPS else float("nan"),
    }


def block_bootstrap_improvement(rows: list[dict], challenger: str, baseline: str) -> dict[str, float]:
    truth = np.asarray([r["truth"] for r in rows], dtype=float)
    ch = np.asarray([r[challenger] for r in rows], dtype=float)
    ba = np.asarray([r[baseline] for r in rows], dtype=float)
    diff = (ba - truth) ** 2 - (ch - truth) ** 2
    observed = float(np.mean(diff))
    n = len(diff)
    starts = np.arange(n)
    rng = np.random.default_rng(BOOT_SEED)
    means = np.empty(BOOT_REPS, dtype=float)
    blocks_needed = int(math.ceil(n / BLOCK))
    for b in range(BOOT_REPS):
        idx: list[int] = []
        for start in rng.choice(starts, size=blocks_needed, replace=True):
            idx.extend((int(start) + k) % n for k in range(BLOCK))
        means[b] = float(np.mean(diff[np.asarray(idx[:n], dtype=int)]))
    low, high = np.quantile(means, (0.025, 0.975))
    return {
        "observed_mse_improvement": observed,
        "ci95_low": float(low),
        "ci95_high": float(high),
        "bootstrap_probability_positive": float(np.mean(means > 0.0)),
        "repetitions": BOOT_REPS,
        "block_months": BLOCK,
    }


def run() -> dict:
    nino = load_nino(NINO_PATH)
    west = load_wwv(WWV_WEST_PATH)
    east = load_wwv(WWV_EAST_PATH)
    keys = sorted(set(nino) & set(west) & set(east))
    t = np.asarray([nino[k] for k in keys], dtype=float)
    w = np.asarray([west[k] for k in keys], dtype=float)
    e = np.asarray([east[k] for k in keys], dtype=float)
    years = np.asarray([decimal_year(k) for k in keys], dtype=float)
    months = np.asarray([int(k[4:6]) for k in keys], dtype=int)

    model_names = (
        "base_levels",
        "base_raw_movement",
        "base_diara",
        "base_radius",
        "base_turn",
        "base_quadrant",
        "base_broken_diara",
    )
    all_rows: list[dict] = []

    for horizon in HORIZONS:
        for origin in range(MIN_LAG, len(keys) - horizon):
            if years[origin] < WALK_START:
                continue
            train_idx = np.arange(MIN_LAG, origin - horizon + 1, dtype=int)
            if len(train_idx) < 120:
                continue
            y_train = t[train_idx + horizon]
            train_feature_rows = [feature_sets(int(j), t, w, e, months, origin) for j in train_idx]
            test_features = feature_sets(origin, t, w, e, months, origin)
            row: dict[str, float | int | str] = {
                "origin": keys[origin],
                "target": keys[origin + horizon],
                "origin_year": float(years[origin]),
                "horizon": int(horizon),
                "split": "holdout" if years[origin] >= HOLDOUT_START else "evaluation",
                "truth": float(t[origin + horizon]),
                "current": float(t[origin]),
                "climatology": float(np.mean(y_train)),
                "persistence": float(t[origin]),
            }
            for model in model_names:
                x_train = np.vstack([f[model] for f in train_feature_rows])
                row[model] = ridge_predict(x_train, y_train, test_features[model])
            all_rows.append(row)

    by_split: dict[str, dict] = {}
    score_models = ("climatology", "persistence") + model_names
    for split in ("evaluation", "holdout"):
        by_split[split] = {}
        for horizon in HORIZONS:
            rows = [r for r in all_rows if r["split"] == split and r["horizon"] == horizon]
            by_split[split][str(horizon)] = {m: score(rows, m) for m in score_models}

    primary_rows = [r for r in all_rows if r["split"] == "holdout" and r["horizon"] == 6]
    bootstrap = {
        "vs_base_levels": block_bootstrap_improvement(primary_rows, "base_diara", "base_levels"),
        "vs_base_raw_movement": block_bootstrap_improvement(primary_rows, "base_diara", "base_raw_movement"),
    }
    primary = by_split["holdout"]["6"]
    di = primary["base_diara"]
    lv = primary["base_levels"]
    raw = primary["base_raw_movement"]
    broken = primary["base_broken_diara"]
    point_wins = (
        di["skill_vs_climatology"] > lv["skill_vs_climatology"]
        and di["mae"] < lv["mae"]
        and di["skill_vs_climatology"] > raw["skill_vs_climatology"]
        and di["mae"] < raw["mae"]
    )
    interval_positive = bootstrap["vs_base_raw_movement"]["ci95_low"] > 0.0
    intact_specific = not (
        broken["skill_vs_climatology"] >= di["skill_vs_climatology"]
        and broken["mae"] <= di["mae"]
    )
    if point_wins and interval_positive and intact_specific:
        verdict = "SUPPORTED_ON_FIXED_REPLAY"
    elif point_wins and intact_specific:
        verdict = "PROVISIONAL_ON_FIXED_REPLAY"
    else:
        verdict = "NOT_SUPPORTED_IN_THIS_FORM"

    results = {
        "test": "T336",
        "frozen_protocol": "T336_ENSO_DI_ARA_HANDOVER_PROTOCOL_v1_FROZEN.md",
        "data": {
            "first_common_month": keys[0],
            "last_common_month": keys[-1],
            "months": len(keys),
            "nino_path": str(NINO_PATH),
            "wwv_west_path": str(WWV_WEST_PATH),
            "wwv_east_path": str(WWV_EAST_PATH),
        },
        "constants": {
            "horizons": HORIZONS,
            "state_lags": STATE_LAGS,
            "octave_lags": OCTAVE_LAGS,
            "walk_start": WALK_START,
            "holdout_start": HOLDOUT_START,
            "ridge_alpha": RIDGE_ALPHA,
            "bootstrap_seed": BOOT_SEED,
        },
        "scores": by_split,
        "bootstrap_primary_h6_holdout": bootstrap,
        "gates": {
            "point_estimates_beat_levels_and_raw_movement": point_wins,
            "bootstrap_ci_above_zero_vs_raw_movement": interval_positive,
            "intact_not_matched_on_both_metrics_by_broken_relation": intact_specific,
        },
        "verdict": verdict,
    }

    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)
    OUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "verdict": result["verdict"],
        "primary_h6_holdout": result["scores"]["holdout"]["6"],
        "bootstrap": result["bootstrap_primary_h6_holdout"],
        "gates": result["gates"],
    }, indent=2))

