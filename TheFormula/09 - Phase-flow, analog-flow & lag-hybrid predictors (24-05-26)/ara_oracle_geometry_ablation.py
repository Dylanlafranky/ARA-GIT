"""
ara_oracle_geometry_ablation.py

Diagnostic-only ablation for the geometry decoder.

Question:

    Which actual future ARA-geometry fields let the decoder recover future
    NINO3.4?

This is not a forecast. It deliberately uses S(t+h), the true future geometry,
to measure the decoder ceiling and identify which geometry fields matter. The
next strict predictor should then try to forecast only those important fields
instead of averaging the entire future state vector.

Leakage guard for origin t and horizon h:

  - Geometry snapshots use only data[:anchor].
  - Decoder training uses only geometry anchors a < t.
  - The future geometry S(t+h) is used only as oracle diagnostic input.
  - No result from this script should be reported as forecast skill.
"""

from __future__ import annotations

import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_geometry_analog_flow_predictor import ORIGIN_STRIDE, compact_state_features
from ara_geometry_transport_test import (
    BASE,
    HOME_PERIOD,
    HORIZONS,
    MIN_TRAIN,
    RUNG_KS,
    START_YEAR,
    build_snapshot,
    clean_for_json,
    load_enso_frame,
    score_points,
    zscore_columns,
)


OUT_JSON = HERE / "ara_oracle_geometry_ablation_result.json"
OUT_JS = HERE / "ara_oracle_geometry_ablation_result.js"

RIDGE_ALPHA = 5.0
MIN_DECODER_TRAIN = max(MIN_TRAIN, 120)


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def round_float(value, digits=6):
    return round(finite(value), digits)


def matrix_from_cache(cache, anchors, keys):
    return np.asarray([[finite(cache[a].get(key, 0.0)) for key in keys] for a in anchors], dtype=float)


def fit_ridge_array(x, y, alpha=RIDGE_ALPHA):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    mean_x = x.mean(axis=0)
    std_x = x.std(axis=0)
    std_x[std_x < 1e-9] = 1.0
    xz = (x - mean_x) / std_x
    mean_y = y.mean(axis=0)
    yc = y - mean_y
    reg = float(alpha) * np.eye(xz.shape[1])
    try:
        beta = np.linalg.solve(xz.T @ xz + reg, xz.T @ yc)
    except np.linalg.LinAlgError:
        beta, *_ = np.linalg.lstsq(xz.T @ xz + reg, xz.T @ yc, rcond=None)
    return {"mean_x": mean_x, "std_x": std_x, "mean_y": mean_y, "beta": beta}


def predict_ridge_array(model, x):
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    xz = (x - model["mean_x"]) / model["std_x"]
    pred = model["mean_y"] + xz @ model["beta"]
    return np.asarray(pred, dtype=float).reshape(-1)


def point(origin_date, target_date, pred, actual, persistence):
    return {
        "origin": origin_date,
        "date": target_date,
        "pred": float(pred),
        "actual": float(actual),
        "persistence": float(persistence),
    }


def feature_group_for(key):
    for subsystem in ["nino", "soi", "pdo"]:
        if key.startswith(f"{subsystem}_phase_"):
            return f"{subsystem}_phase"
        if key.startswith(f"{subsystem}_boundary_distance") or key in {
            f"{subsystem}_ara_position",
            f"{subsystem}_ara_bounded",
        }:
            return f"{subsystem}_ara_boundary"
        if key == f"{subsystem}_orientation_release_balance" or key.startswith(f"{subsystem}_regime_"):
            return f"{subsystem}_regime_orientation"
        if key.startswith(f"{subsystem}_amplitude_") or key in {
            f"{subsystem}_rung_position",
            f"{subsystem}_home_distance",
            f"{subsystem}_weighted_k",
            f"{subsystem}_occupancy_entropy",
        }:
            return f"{subsystem}_energy_rung"

    for pair in ["nino_soi", "nino_pdo", "soi_pdo"]:
        if key.startswith(f"{pair}_partner_phase"):
            return f"{pair}_phase_gap"
        if key.startswith(f"{pair}_"):
            return f"{pair}_coupling"

    if key.startswith("enso_"):
        return "enso_aggregate"
    return "other"


def make_groups(keys):
    groups = defaultdict(list)
    for key in keys:
        groups[feature_group_for(key)].append(key)
    out = {name: sorted(values) for name, values in groups.items()}
    out["all_compact"] = sorted(keys)
    for name, values in list(groups.items()):
        minus = [key for key in keys if key not in set(values)]
        out[f"without_{name}"] = sorted(minus)
    return dict(sorted(out.items()))


def score_feature_set(cache, dates, nino_raw, origins, horizon, keys):
    points = []
    if not keys:
        return {"n": 0}, points
    for origin in origins:
        target_anchor = origin + horizon
        if target_anchor > len(nino_raw):
            continue
        train_decoder = [a for a in cache if a < origin]
        if len(train_decoder) < MIN_DECODER_TRAIN:
            continue
        x_train = matrix_from_cache(cache, train_decoder, keys)
        y_train = np.asarray([float(nino_raw[a - 1]) for a in train_decoder], dtype=float)
        x_test = matrix_from_cache(cache, [target_anchor], keys)
        model = fit_ridge_array(x_train, y_train, RIDGE_ALPHA)
        pred = float(predict_ridge_array(model, x_test)[0])
        actual = float(nino_raw[target_anchor - 1])
        persistence = float(nino_raw[origin - 1])
        points.append(
            point(
                dates[origin - 1].strftime("%Y-%m-%d"),
                dates[target_anchor - 1].strftime("%Y-%m-%d"),
                pred,
                actual,
                persistence,
            )
        )
    return score_points(points), points


def mean_score(scores_by_horizon, horizons=None):
    horizons = horizons or HORIZONS
    vals = []
    for horizon in horizons:
        score = scores_by_horizon.get(str(horizon)) or scores_by_horizon.get(horizon)
        if score and "mae" in score:
            vals.append(score)
    if not vals:
        return {"n_horizons": 0}
    return {
        "n_horizons": int(len(vals)),
        "mean_mae": float(np.mean([v["mae"] for v in vals])),
        "mean_corr": float(np.mean([v["corr"] for v in vals])),
        "mean_direction": float(np.mean([v["direction"] for v in vals])),
        "mean_lift": float(np.mean([v["mae_lift_vs_persistence"] for v in vals])),
    }


def rank_groups(group_scores, full_scores):
    rows = []
    full_mean = mean_score(full_scores)
    full_mid = mean_score(full_scores, horizons=[6, 12, 24])
    for name, scores in group_scores.items():
        if name == "all_compact" or name.startswith("without_"):
            continue
        m = mean_score(scores)
        mm = mean_score(scores, horizons=[6, 12, 24])
        rows.append(
            {
                "group": name,
                "mean_corr_all": m.get("mean_corr"),
                "mean_mae_all": m.get("mean_mae"),
                "mean_lift_all": m.get("mean_lift"),
                "mean_corr_6_12_24": mm.get("mean_corr"),
                "mean_mae_6_12_24": mm.get("mean_mae"),
                "corr_gap_to_full_all": full_mean.get("mean_corr", 0.0) - m.get("mean_corr", 0.0),
                "corr_gap_to_full_6_12_24": full_mid.get("mean_corr", 0.0) - mm.get("mean_corr", 0.0),
            }
        )
    return sorted(rows, key=lambda item: (-(item["mean_corr_6_12_24"] or -999), item["mean_mae_6_12_24"] or 999))


def rank_dropouts(group_scores, full_scores):
    rows = []
    full_mean = mean_score(full_scores)
    full_mid = mean_score(full_scores, horizons=[6, 12, 24])
    for name, scores in group_scores.items():
        if not name.startswith("without_"):
            continue
        group = name[len("without_") :]
        m = mean_score(scores)
        mm = mean_score(scores, horizons=[6, 12, 24])
        rows.append(
            {
                "removed_group": group,
                "mean_corr_all_without": m.get("mean_corr"),
                "mean_mae_all_without": m.get("mean_mae"),
                "corr_drop_all": full_mean.get("mean_corr", 0.0) - m.get("mean_corr", 0.0),
                "mae_increase_all": m.get("mean_mae", 0.0) - full_mean.get("mean_mae", 0.0),
                "corr_drop_6_12_24": full_mid.get("mean_corr", 0.0) - mm.get("mean_corr", 0.0),
                "mae_increase_6_12_24": mm.get("mean_mae", 0.0) - full_mid.get("mean_mae", 0.0),
            }
        )
    return sorted(rows, key=lambda item: (-(item["corr_drop_6_12_24"] or -999), -(item["mae_increase_6_12_24"] or -999)))


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    series = zscore_columns(frame)
    nino_raw = series["NINO"]["raw"]
    n = len(frame)
    max_h = max(HORIZONS)
    min_anchor = max(4 * max(RUNG_KS), int(4 * BASE ** max(RUNG_KS)), 48)
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01"))) + 1
    test_start = max(start_idx, min_anchor + MIN_DECODER_TRAIN + max_h + 1)
    all_anchors = list(range(min_anchor, n + 1))

    print("ARA oracle geometry ablation")
    print("=" * 96)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}")
    print(f"diagnostic only: decoder sees actual future geometry S(t+h)")
    print(f"test origins start: {dates[test_start - 1].date()}  stride={ORIGIN_STRIDE}")
    print()

    cache = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        cache[anchor] = compact_state_features(build_snapshot(series, anchor))
        if i % 100 == 0:
            print(f"  cached states {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  cached states {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s")
    print()

    keys = sorted({key for item in cache.values() for key in item})
    groups = make_groups(keys)

    group_scores = {name: {} for name in groups}
    group_examples = {}
    for name, group_keys in groups.items():
        print(f"Scoring {name} ({len(group_keys)} fields)")
        for horizon in HORIZONS:
            origins = list(range(test_start, n - horizon + 1, ORIGIN_STRIDE))
            score, points = score_feature_set(cache, dates, nino_raw, origins, horizon, group_keys)
            group_scores[name][str(horizon)] = score
            if name in {"all_compact", "nino_phase", "nino_ara_boundary", "nino_soi_phase_gap", "enso_aggregate"}:
                group_examples.setdefault(name, {})[str(horizon)] = points[:5]

    individual_scores = {}
    print("Scoring individual fields")
    for key in keys:
        individual_scores[key] = {}
        for horizon in HORIZONS:
            origins = list(range(test_start, n - horizon + 1, ORIGIN_STRIDE))
            score, _ = score_feature_set(cache, dates, nino_raw, origins, horizon, [key])
            individual_scores[key][str(horizon)] = score

    full_scores = group_scores["all_compact"]
    group_rank = rank_groups(group_scores, full_scores)
    dropout_rank = rank_dropouts(group_scores, full_scores)
    individual_rank = sorted(
        [
            {
                "field": key,
                **mean_score(scores),
                "mid": mean_score(scores, horizons=[6, 12, 24]),
            }
            for key, scores in individual_scores.items()
        ],
        key=lambda item: (-(item["mid"].get("mean_corr") or -999), item["mid"].get("mean_mae") or 999),
    )

    out = {
        "date": "2026-05-24",
        "method": "oracle future-geometry decoder ablation",
        "diagnostic_only": True,
        "leakage_guard": [
            "Geometry snapshots use only data[:anchor].",
            "Decoder training uses only anchors a<t.",
            "Actual future geometry S(t+h) is used only as oracle diagnostic input.",
            "No score here is a strict forecast score.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "base": BASE,
        "home_period_months": HOME_PERIOD,
        "rungs_k": RUNG_KS,
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "ridge_alpha": RIDGE_ALPHA,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
        },
        "feature_groups": groups,
        "full_compact_summary": {
            "all_horizons": mean_score(full_scores),
            "horizons_6_12_24": mean_score(full_scores, horizons=[6, 12, 24]),
        },
        "group_scores": group_scores,
        "group_rank_by_mid_corr": group_rank,
        "dropout_rank_by_mid_damage": dropout_rank,
        "individual_scores": individual_scores,
        "individual_rank_by_mid_corr": individual_rank[:30],
        "example_points": group_examples,
        "elapsed_seconds": round_float(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_ORACLE_GEOMETRY_ABLATION = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print()
    print("Full compact oracle:")
    for horizon in HORIZONS:
        score = full_scores[str(horizon)]
        print(
            f"  h={horizon:>2} MAE={score.get('mae', float('nan')):.3f} "
            f"corr={score.get('corr', float('nan')):+.3f} "
            f"dir={score.get('direction', float('nan')):.3f}"
        )
    print()
    print("Top group-only fields by mean corr at 6/12/24:")
    for row in group_rank[:10]:
        print(
            f"  {row['group']:28s} corr={row['mean_corr_6_12_24']:+.3f} "
            f"MAE={row['mean_mae_6_12_24']:.3f}"
        )
    print()
    print("Most damaging removals at 6/12/24:")
    for row in dropout_rank[:10]:
        print(
            f"  remove {row['removed_group']:22s} "
            f"corr_drop={row['corr_drop_6_12_24']:+.3f} "
            f"mae_increase={row['mae_increase_6_12_24']:+.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
