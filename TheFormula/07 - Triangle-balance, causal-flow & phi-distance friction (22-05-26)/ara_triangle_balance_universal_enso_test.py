"""
ara_triangle_balance_universal_enso_test.py

Strict-causal test runner for the generic ARA triangle-balance feature engine.

The core logic is system-neutral: a caller supplies a dataframe and a TriadConfig
that names the target, counter, and third system. This file uses ENSO as the
first configured triad:

    target  = NINO
    counter = SOI, read as -SOI
    third   = PDO

The test also scans per-rung anti-phase interactions so we can see which target
ARA rung carries the forecast pressure at each horizon.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_geometry_transport_test import (
    BASE,
    HOME_PERIOD,
    HORIZONS,
    MIN_TRAIN,
    RUNG_KS,
    START_YEAR,
    build_snapshot,
    clean_for_json,
    fit_predict_ridge,
    lag_feature_dict,
    load_enso_frame,
    score_points,
)
from ara_triangle_balance_core import (
    TriadConfig,
    add_meta_wave_gate_features,
    add_minimal_meta_wave_gate_features,
    add_per_rung_antiphase_features,
    counter_balance_features,
    rotating_counter_balance_features,
    rotating_triangle_balance_features,
    triangle_balance_features,
    triangle_fixed_delta,
)


ENSO_TRIAD = TriadConfig(
    target="NINO",
    counter="SOI",
    third="PDO",
    counter_sign=-1.0,
    third_sign=1.0,
    third_to_target_sign=1.0,
    third_to_counter_sign=-1.0,
    closure_third_weight=0.5,
)

MODEL_KEYS = [
    "triangle_balance_fixed",
    "triangle_balance_ridge",
    "triangle_balance_snap_ridge",
    "triangle_minimal_meta_gate_ridge",
    "triangle_meta_wave_gate_ridge",
    "triangle_rotating_counter_snap_ridge",
    "triangle_per_rung_antiphase_ridge",
    "counter_balance_snap_ridge",
    "counter_meta_wave_gate_ridge",
    "counter_rotating_snap_ridge",
    "lag_ridge",
]


def format_score(score):
    if "mae" not in score:
        return "n/a"
    return (
        f"MAE={score['mae']:.4f} vs pers={score['persistence_mae']:.4f} "
        f"lift={score['mae_lift_vs_persistence']:+.4f} corr={score['corr']:+.3f} "
        f"dir={score['direction']:.3f}"
    )


def date_label(value):
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)


def causal_zscore_columns(frame):
    """Expanding z-score: every row uses only values available up to that row."""
    out = {}
    for name in frame.columns:
        vals = frame[name].values.astype(float)
        means = np.empty(len(vals), dtype=float)
        stds = np.empty(len(vals), dtype=float)
        zvals = np.empty(len(vals), dtype=float)
        for idx in range(len(vals)):
            history = vals[: idx + 1]
            mean = float(np.mean(history))
            std = float(np.std(history)) + 1e-9
            means[idx] = mean
            stds[idx] = std
            zvals[idx] = (vals[idx] - mean) / std
        out[name] = {
            "raw": vals,
            "mean": float(means[-1]),
            "std": float(stds[-1]),
            "z": zvals,
            "mean_by_anchor": means,
            "std_by_anchor": stds,
        }
    return out


def make_point(origin_date, target_date, actual_raw, persistence_raw, pred_delta_z, scale_std, actual_delta_z):
    return {
        "origin": origin_date,
        "date": target_date,
        "pred": float(persistence_raw + pred_delta_z * scale_std),
        "actual": float(actual_raw),
        "persistence": float(persistence_raw),
        "pred_delta_z": float(pred_delta_z),
        "actual_delta_z": float(actual_delta_z),
    }


def summarize_triangle(rows):
    if not rows:
        return {"ara": None, "rationality": None, "time": None}
    return {
        key: float(np.mean([row[key] for row in rows]))
        for key in ["ara", "rationality", "time"]
    }


def add_rung_beta_totals(totals, counts, keys, beta, rung_ks):
    for rung_k in rung_ks:
        prefix = f"rung_k{rung_k}_"
        value = 0.0
        for key, coeff in zip(keys, beta):
            if key.startswith(prefix):
                value += abs(float(coeff))
        totals[rung_k] += value
    counts[0] += 1


def summarize_rung_betas(totals_by_horizon, counts_by_horizon, rung_ks):
    out = {}
    for horizon, totals in totals_by_horizon.items():
        count = max(1, counts_by_horizon[horizon][0])
        raw = {f"k{k}": float(totals[k] / count) for k in rung_ks}
        ranked = sorted(raw.items(), key=lambda item: item[1], reverse=True)
        out[str(horizon)] = {
            "mean_abs_standardized_beta_by_rung": raw,
            "ranked": [{"rung": rung, "mean_abs_beta": value} for rung, value in ranked],
        }
    return out


def run_triad_prediction_test(
    frame,
    config,
    *,
    system_label,
    target_label=None,
    output_variable_name=None,
    output_path=None,
    horizons=HORIZONS,
    rung_ks=RUNG_KS,
    base=BASE,
    home_period=HOME_PERIOD,
    start_year=START_YEAR,
    min_train=MIN_TRAIN,
):
    started = time.time()
    target_label = target_label or config.target
    output_variable_name = output_variable_name or "ARA_TRIANGLE_BALANCE_UNIVERSAL"
    output_path = Path(output_path) if output_path is not None else HERE / "ara_triangle_balance_universal_data.js"

    dates = list(frame.index)
    series = causal_zscore_columns(frame)
    missing = [name for name in [config.target, config.counter, config.third] if name not in series]
    if missing:
        raise KeyError(f"Missing triad columns: {', '.join(missing)}")

    zseries = {name: series[name]["z"] for name in [config.target, config.counter, config.third]}
    target_raw = series[config.target]["raw"]
    target_z = series[config.target]["z"]
    n = len(frame)
    max_h = max(horizons)
    min_anchor = max(4 * max(rung_ks), int(4 * base ** max(rung_ks)), 48)
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{start_year}-01-01")))
    test_start = max(start_idx + 1, min_anchor + min_train + max_h + 1)
    last_origin = n - max_h
    all_anchors = list(range(min_anchor, n + 1))

    print("Generic ARA triangle-balance prediction test", flush=True)
    print("=" * 96, flush=True)
    print(f"system: {system_label}", flush=True)
    print(f"sample: {date_label(dates[0])} -> {date_label(dates[-1])}  n={n}", flush=True)
    print(
        f"target={config.target}, counter={config.counter} x {config.counter_sign:+.1f}, "
        f"third={config.third} x {config.third_sign:+.1f}",
        flush=True,
    )
    print("normalization: expanding causal z-score, with raw target deltas scaled at each origin", flush=True)
    print("leakage guard: at origin t, train only on anchors s where s+h<t", flush=True)
    print(
        f"test origins start: {date_label(dates[test_start - 1])}  "
        f"longest-horizon last origin: {date_label(dates[last_origin - 1])}",
        flush=True,
    )
    print(flush=True)

    snapshots = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        snapshots[anchor] = build_snapshot(series, anchor)
        if i % 100 == 0:
            print(f"  snapshots {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  snapshots {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(flush=True)

    feature_cache = {h: {} for h in horizons}
    for h in horizons:
        for anchor in all_anchors:
            snap = snapshots[anchor]
            triangle_snap = triangle_balance_features(
                snap,
                zseries,
                anchor,
                h,
                config,
                include_snap=True,
                base=base,
                home_period=home_period,
            )
            feature_cache[h][anchor] = {
                "triangle": triangle_balance_features(
                    snap,
                    zseries,
                    anchor,
                    h,
                    config,
                    include_snap=False,
                    base=base,
                    home_period=home_period,
                ),
                "triangle_snap": triangle_snap,
                "triangle_minimal_meta_gate": add_minimal_meta_wave_gate_features(
                    triangle_snap,
                    snap,
                    h,
                    config,
                    home_period=home_period,
                ),
                "triangle_meta_wave_gate": add_meta_wave_gate_features(
                    triangle_snap,
                    snap,
                    h,
                    config,
                    home_period=home_period,
                ),
                "triangle_rotating_counter_snap": rotating_triangle_balance_features(
                    snap,
                    zseries,
                    anchor,
                    h,
                    config,
                    include_snap=True,
                    base=base,
                    home_period=home_period,
                ),
                "triangle_per_rung_antiphase": add_per_rung_antiphase_features(
                    triangle_snap,
                    snap,
                    h,
                    config,
                    rung_ks=rung_ks,
                ),
                "counter_snap": counter_balance_features(
                    snap,
                    zseries,
                    anchor,
                    h,
                    config,
                    include_snap=True,
                    base=base,
                    home_period=home_period,
                ),
                "counter_meta_wave_gate": add_meta_wave_gate_features(
                    counter_balance_features(
                        snap,
                        zseries,
                        anchor,
                        h,
                        config,
                        include_snap=True,
                        base=base,
                        home_period=home_period,
                    ),
                    snap,
                    h,
                    config,
                    home_period=home_period,
                ),
                "counter_rotating_snap": rotating_counter_balance_features(
                    snap,
                    zseries,
                    anchor,
                    h,
                    config,
                    include_snap=True,
                    base=base,
                    home_period=home_period,
                ),
                "lag": lag_feature_dict(target_z, anchor),
            }

    all_points = {model: {h: [] for h in horizons} for model in MODEL_KEYS}
    triangle_summary_rows = {h: [] for h in horizons}
    rung_beta_totals = {h: {k: 0.0 for k in rung_ks} for h in horizons}
    rung_beta_counts = {h: [0] for h in horizons}

    for h in horizons:
        origins = list(range(test_start, n - h + 1))
        for origin in origins:
            train_anchors = [s for s in all_anchors if s + h < origin]
            if len(train_anchors) < min_train:
                continue

            target_anchor = origin + h
            actual_raw = float(target_raw[target_anchor - 1])
            persistence_raw = float(target_raw[origin - 1])
            scale_std = float(series[config.target]["std_by_anchor"][origin - 1])
            actual_delta_z = float((actual_raw - persistence_raw) / scale_std)

            origin_date = date_label(dates[origin - 1])
            target_date = date_label(dates[target_anchor - 1])

            tri_snap = feature_cache[h][origin]["triangle_snap"]
            fixed_delta_z = triangle_fixed_delta(tri_snap)
            all_points["triangle_balance_fixed"][h].append(
                make_point(
                    origin_date,
                    target_date,
                    actual_raw,
                    persistence_raw,
                    fixed_delta_z,
                    scale_std,
                    actual_delta_z,
                )
            )
            triangle_summary_rows[h].append(
                {
                    "ara": tri_snap["triangle_ara"],
                    "rationality": tri_snap["triangle_rationality"],
                    "time": tri_snap["triangle_time"],
                }
            )

            train_y = [
                float((target_raw[s + h - 1] - target_raw[s - 1]) / series[config.target]["std_by_anchor"][s - 1])
                for s in train_anchors
            ]
            for model, variant in [
                ("triangle_balance_ridge", "triangle"),
                ("triangle_balance_snap_ridge", "triangle_snap"),
                ("triangle_minimal_meta_gate_ridge", "triangle_minimal_meta_gate"),
                ("triangle_meta_wave_gate_ridge", "triangle_meta_wave_gate"),
                ("triangle_rotating_counter_snap_ridge", "triangle_rotating_counter_snap"),
                ("triangle_per_rung_antiphase_ridge", "triangle_per_rung_antiphase"),
                ("counter_balance_snap_ridge", "counter_snap"),
                ("counter_meta_wave_gate_ridge", "counter_meta_wave_gate"),
                ("counter_rotating_snap_ridge", "counter_rotating_snap"),
                ("lag_ridge", "lag"),
            ]:
                pred_delta_z, keys, beta = fit_predict_ridge(
                    [feature_cache[h][s][variant] for s in train_anchors],
                    train_y,
                    feature_cache[h][origin][variant],
                )
                if model == "triangle_per_rung_antiphase_ridge":
                    add_rung_beta_totals(rung_beta_totals[h], rung_beta_counts[h], keys, beta, rung_ks)
                all_points[model][h].append(
                    make_point(
                        origin_date,
                        target_date,
                        actual_raw,
                        persistence_raw,
                        pred_delta_z,
                        scale_std,
                        actual_delta_z,
                    )
                )

        print(f"h={h:>2} months")
        for model in MODEL_KEYS:
            print(f"  {model:38s} {format_score(score_points(all_points[model][h]))}")
        best = min(MODEL_KEYS, key=lambda m: score_points(all_points[m][h]).get("mae", float("inf")))
        print(f"  best: {best}")
        print()

    scores = {model: {h: score_points(all_points[model][h]) for h in horizons} for model in MODEL_KEYS}
    triangle_summary = {str(h): summarize_triangle(triangle_summary_rows[h]) for h in horizons}
    rung_beta_summary = summarize_rung_betas(rung_beta_totals, rung_beta_counts, rung_ks)
    winners = {
        str(h): min(MODEL_KEYS, key=lambda m: scores[m][h].get("mae", float("inf")))
        for h in horizons
    }

    out = {
        "date": "2026-05-22",
        "method": "strict-causal generic ARA triangle-balance test with per-rung anti-phase scan",
        "leakage_guard": "At origin t, training uses only anchors s with s+h<t. Features use only current triad values, current ARA geometry, causal past motion, and expanding z-scores available at the relevant anchor.",
        "normalization": "expanding causal z-score; target deltas are raw future-minus-origin values scaled by the origin's historical standard deviation",
        "system": system_label,
        "target": target_label,
        "triad_config": {
            "target": config.target,
            "counter": config.counter,
            "third": config.third,
            "counter_sign": config.counter_sign,
            "third_sign": config.third_sign,
            "third_to_target_sign": config.third_to_target_sign,
            "third_to_counter_sign": config.third_to_counter_sign,
            "closure_third_weight": config.closure_third_weight,
        },
        "base": base,
        "home_period": home_period,
        "rungs_k": rung_ks,
        "horizons_months": horizons,
        "min_train_examples": min_train,
        "models": {
            "triangle_balance_fixed": "Parameter-free triangle pressure from ARA/Rationality/Time coordinates.",
            "triangle_balance_ridge": "Causal ridge on generic triangle coordinates and pressure terms without snap.",
            "triangle_balance_snap_ridge": "Causal ridge on generic triangle coordinates and pressure terms with snap.",
            "triangle_minimal_meta_gate_ridge": "Small meta-cycle gate: blends same-side continuation pressure with counter pressure using the ARA valve split.",
            "triangle_meta_wave_gate_ridge": "Triangle+snap model with meta-cycle same/counter gates and ARA valve split features.",
            "triangle_rotating_counter_snap_ridge": "Triangle+snap model where the counter relation sign rotates smoothly from +1 to -1 to +1 over the current target active period.",
            "triangle_per_rung_antiphase_ridge": "Triangle+snap features with one anti-phase interaction block per target rung.",
            "counter_balance_snap_ridge": "Control: generic target/counter/third counter-balance snap model.",
            "counter_meta_wave_gate_ridge": "Counter-balance snap model with meta-cycle same/counter gates and ARA valve split features.",
            "counter_rotating_snap_ridge": "Counter-balance snap model with the same rotating counter relation sign.",
            "lag_ridge": "Control: causal target lags and slopes.",
        },
        "scores": scores,
        "winners": winners,
        "triangle_summary": triangle_summary,
        "rung_beta_summary": rung_beta_summary,
        "points": all_points,
        "elapsed_seconds": round(time.time() - started, 3),
    }

    with output_path.open("w", encoding="utf-8") as f:
        f.write(f"window.{output_variable_name} = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {output_path}")
    return out


def run_enso():
    return run_triad_prediction_test(
        load_enso_frame(),
        ENSO_TRIAD,
        system_label="ENSO",
        target_label="NINO3.4 anomaly",
        output_variable_name="ARA_TRIANGLE_BALANCE_UNIVERSAL_ENSO",
        output_path=HERE / "ara_triangle_balance_universal_enso_data.js",
    )


if __name__ == "__main__":
    run_enso()
