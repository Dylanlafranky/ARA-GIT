"""T337: frozen Di-ARA signed-traversal direction replay on ENSO."""

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

OUT_JSON = HERE / "T337_DI_ARA_ENSO_DIRECTION_RESULTS.json"
OUT_CSV = HERE / "T337_DI_ARA_ENSO_DIRECTION_SCORES.csv"

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


def ridge_score(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> float:
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
        product = z_now * z_prev.conjugate()
        delta = math.atan2(product.imag, product.real) / math.pi
        continuous.extend((a, delta))
        radius_only.append(a)
        turn_only.append(delta)
        quadrant = (2 if a >= 0.0 else 0) + (1 if delta >= 0.0 else 0)
        quadrants.extend(1.0 if k == quadrant else 0.0 for k in range(4))
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
    diara, radius, turn, quadrant = diara_features(j, tz, rz)
    broken, _, _, _ = diara_features(j, tz, rz, reservoir_shift=BROKEN_SHIFT)
    raw = raw_movement_features(j, tz, rz)
    return {
        "base_levels": base,
        "base_raw_movement": np.concatenate((base, raw)),
        "base_turn": np.concatenate((base, turn)),
        "base_diara": np.concatenate((base, diara)),
        "base_radius": np.concatenate((base, radius)),
        "base_quadrant": np.concatenate((base, quadrant)),
        "base_broken_diara": np.concatenate((base, broken)),
    }


def auc_rank(scores: np.ndarray, labels: np.ndarray) -> float:
    positive = scores[labels > 0]
    negative = scores[labels < 0]
    if len(positive) == 0 or len(negative) == 0:
        return float("nan")
    comparisons = positive[:, None] - negative[None, :]
    return float((np.sum(comparisons > 0) + 0.5 * np.sum(comparisons == 0)) / comparisons.size)


def score_rows(rows: list[dict], model: str) -> dict[str, float | int]:
    scores = np.asarray([r[model] for r in rows], dtype=float)
    labels = np.asarray([r["label"] for r in rows], dtype=float)
    predictions = np.where(scores >= 0.0, 1.0, -1.0)
    pos = labels > 0
    neg = labels < 0
    pos_recall = float(np.mean(predictions[pos] == labels[pos])) if np.any(pos) else float("nan")
    neg_recall = float(np.mean(predictions[neg] == labels[neg])) if np.any(neg) else float("nan")
    return {
        "n": len(rows),
        "positive_n": int(np.sum(pos)),
        "negative_n": int(np.sum(neg)),
        "balanced_accuracy": 0.5 * (pos_recall + neg_recall),
        "accuracy": float(np.mean(predictions == labels)),
        "positive_recall": pos_recall,
        "negative_recall": neg_recall,
        "auc": auc_rank(scores, labels),
    }


def block_bootstrap_balanced(rows: list[dict], challenger: str, baseline: str) -> dict[str, float | int]:
    labels = np.asarray([r["label"] for r in rows], dtype=float)
    ch = np.asarray([1.0 if r[challenger] >= 0.0 else -1.0 for r in rows])
    ba = np.asarray([1.0 if r[baseline] >= 0.0 else -1.0 for r in rows])
    n = len(rows)
    starts = np.arange(n)
    rng = np.random.default_rng(BOOT_SEED)
    means = np.empty(BOOT_REPS, dtype=float)
    blocks_needed = int(math.ceil(n / BLOCK))

    def balanced(pred: np.ndarray, truth: np.ndarray) -> float:
        pos = truth > 0
        neg = truth < 0
        return 0.5 * (float(np.mean(pred[pos] == truth[pos])) + float(np.mean(pred[neg] == truth[neg])))

    observed = balanced(ch, labels) - balanced(ba, labels)
    for rep in range(BOOT_REPS):
        idx: list[int] = []
        for start in rng.choice(starts, size=blocks_needed, replace=True):
            idx.extend((int(start) + k) % n for k in range(BLOCK))
        take = np.asarray(idx[:n], dtype=int)
        means[rep] = balanced(ch[take], labels[take]) - balanced(ba[take], labels[take])
    low, high = np.quantile(means, (0.025, 0.975))
    return {
        "observed_balanced_accuracy_improvement": float(observed),
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
    t = np.asarray([nino[key] for key in keys], dtype=float)
    w = np.asarray([west[key] for key in keys], dtype=float)
    e = np.asarray([east[key] for key in keys], dtype=float)
    years = np.asarray([decimal_year(key) for key in keys], dtype=float)
    months = np.asarray([int(key[4:6]) for key in keys], dtype=int)

    learned_models = (
        "base_levels",
        "base_raw_movement",
        "base_turn",
        "base_diara",
        "base_radius",
        "base_quadrant",
        "base_broken_diara",
    )
    rows: list[dict] = []

    for horizon in HORIZONS:
        for origin in range(MIN_LAG, len(keys) - horizon):
            if years[origin] < WALK_START:
                continue
            change = float(t[origin + horizon] - t[origin])
            if abs(change) <= EPS:
                continue
            train_idx = np.arange(MIN_LAG, origin - horizon + 1, dtype=int)
            train_changes = t[train_idx + horizon] - t[train_idx]
            keep = np.abs(train_changes) > EPS
            train_idx = train_idx[keep]
            y_train = np.sign(train_changes[keep])
            if len(train_idx) < 120 or len(np.unique(y_train)) < 2:
                continue
            train_features = [feature_sets(int(j), t, w, e, months, origin) for j in train_idx]
            test_features = feature_sets(origin, t, w, e, months, origin)
            past_change = float(t[origin] - t[origin - horizon])
            past_score = past_change if abs(past_change) > EPS else 1.0
            row: dict[str, float | int | str] = {
                "origin": keys[origin],
                "target": keys[origin + horizon],
                "origin_year": float(years[origin]),
                "horizon": int(horizon),
                "split": "holdout" if years[origin] >= HOLDOUT_START else "evaluation",
                "change": change,
                "label": float(np.sign(change)),
                "past_trend": past_score,
            }
            for model in learned_models:
                x_train = np.vstack([features[model] for features in train_features])
                row[model] = ridge_score(x_train, y_train, test_features[model])
            rows.append(row)

    scores: dict[str, dict] = {}
    score_models = ("past_trend",) + learned_models
    for split in ("evaluation", "holdout"):
        scores[split] = {}
        for horizon in HORIZONS:
            selected = [r for r in rows if r["split"] == split and r["horizon"] == horizon]
            scores[split][str(horizon)] = {model: score_rows(selected, model) for model in score_models}

    primary_rows = [r for r in rows if r["split"] == "holdout" and r["horizon"] == 6]
    bootstrap = {
        "vs_base_levels": block_bootstrap_balanced(primary_rows, "base_turn", "base_levels"),
        "vs_base_raw_movement": block_bootstrap_balanced(primary_rows, "base_turn", "base_raw_movement"),
    }
    primary = scores["holdout"]["6"]
    turn = primary["base_turn"]
    levels = primary["base_levels"]
    raw = primary["base_raw_movement"]
    broken = primary["base_broken_diara"]
    substantive = (
        turn["balanced_accuracy"] >= levels["balanced_accuracy"] + 0.02
        and turn["balanced_accuracy"] >= raw["balanced_accuracy"] + 0.02
    )
    accuracy_guard = turn["accuracy"] >= levels["accuracy"] and turn["accuracy"] >= raw["accuracy"]
    interval_positive = bootstrap["vs_base_raw_movement"]["ci95_low"] > 0.0
    lineage_specific = broken["balanced_accuracy"] < turn["balanced_accuracy"]
    if substantive and accuracy_guard and interval_positive and lineage_specific:
        verdict = "SUPPORTED_ON_FIXED_REPLAY"
    elif substantive and accuracy_guard and lineage_specific:
        verdict = "PROVISIONAL_ON_FIXED_REPLAY"
    else:
        verdict = "NOT_SUPPORTED_IN_THIS_FORM"

    result = {
        "test": "T337",
        "frozen_protocol": "T337_DI_ARA_ENSO_DIRECTION_PROTOCOL_v1_FROZEN.md",
        "data": {
            "first_common_month": keys[0],
            "last_common_month": keys[-1],
            "months": len(keys),
        },
        "constants": {
            "horizons": HORIZONS,
            "octave_lags": OCTAVE_LAGS,
            "walk_start": WALK_START,
            "holdout_start": HOLDOUT_START,
            "ridge_alpha": RIDGE_ALPHA,
            "bootstrap_seed": BOOT_SEED,
        },
        "scores": scores,
        "bootstrap_primary_h6_holdout": bootstrap,
        "gates": {
            "turn_beats_levels_and_raw_by_0_02_balanced_accuracy": substantive,
            "ordinary_accuracy_not_lower": accuracy_guard,
            "bootstrap_ci_above_zero_vs_raw_movement": interval_positive,
            "intact_turn_beats_broken_full_relation": lineage_specific,
        },
        "verdict": verdict,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    fieldnames = list(rows[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
