"""
ara_multirung_feeder_ablation.py

Strict-causal ablation for the fractal feeder intuition:

    Does forecast lift come from lower-rung feeder information specifically,
    or from the full model bundle / extra features?

Models:

  - lag_ridge
  - home_only
  - home_plus_lower
  - home_plus_upper
  - home_plus_lower_upper
  - home_plus_shuffled_lower
  - home_plus_nonphi_lower

All ARA variants include the same lag/inertia base and the same home-rung
features.  The only difference is the added rung block.

Leakage guard:

  - Every feature at anchor t uses only data[:t].
  - Training for origin t and horizon h uses only anchors s where s+h<t.
  - Shuffled lower features are drawn only from already-allowed training
    anchors, never from the current/future target.
  - No result selects periods or horizons from forecast performance.
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_framework import _measure_rung, causal_bandpass
from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import (
    HOME_PERIOD,
    START_YEAR,
    clean_for_json,
    load_enso_frame,
    zscore_columns,
)
from ara_lag_phase_hybrid_predictor import extended_score, finite, format_score, point


PHI = (1.0 + math.sqrt(5.0)) / 2.0

OUT_JSON = HERE / "ara_multirung_feeder_ablation_result.json"
OUT_JS = HERE / "ara_multirung_feeder_ablation_result.js"

HORIZONS = [1, 3, 6, 12, 18, 24, 60]
ORIGIN_STRIDE = 3
MIN_TRAIN = 96
RIDGE_ALPHA = 12.0

HOME = float(HOME_PERIOD)
LOWER_PHI = [HOME / (PHI**2), HOME / PHI]
UPPER_PHI = [HOME * PHI, HOME * (PHI**2)]
LOWER_NONPHI_BASE = 2.0
LOWER_NONPHI = [HOME / (LOWER_NONPHI_BASE**2), HOME / LOWER_NONPHI_BASE]

SIGNALS = ["NINO", "SOI", "PDO"]
FEEDERS = ["SOI", "PDO"]
LAGS = [1, 3, 6, 12, 24]
ROLLING_WINDOWS = [6, 12, 24]

MODEL_KEYS = [
    "lag_ridge",
    "home_only",
    "home_plus_lower",
    "home_plus_upper",
    "home_plus_lower_upper",
    "home_plus_shuffled_lower",
    "home_plus_nonphi_lower",
]


def rounded(value, digits=6):
    return round(finite(value), digits)


def signal_delta(values, anchor, lag):
    idx = anchor - 1
    j = idx - int(lag)
    if j < 0:
        return 0.0
    return finite(values[idx] - values[j])


def rolling_features(values, anchor, window):
    idx = anchor
    start = max(0, idx - int(window))
    segment = np.asarray(values[start:idx], dtype=float)
    if len(segment) < 3:
        current = finite(values[idx - 1]) if idx > 0 else 0.0
        return current, 0.0, 0.0
    x = np.arange(len(segment), dtype=float)
    slope = float(np.polyfit(x, segment, 1)[0]) if len(segment) >= 3 else 0.0
    return float(np.mean(segment)), float(np.std(segment)), slope


def lag_features(series, anchor):
    out = {}
    for name in SIGNALS:
        raw = series[name]["raw"]
        z = series[name]["z"]
        out[f"lag_{name}_raw_current"] = finite(raw[anchor - 1])
        out[f"lag_{name}_z_current"] = finite(z[anchor - 1])
        out[f"lag_{name}_abs_current"] = abs(finite(raw[anchor - 1]))
        for lag in LAGS:
            out[f"lag_{name}_raw_delta_{lag}"] = signal_delta(raw, anchor, lag)
            out[f"lag_{name}_z_delta_{lag}"] = signal_delta(z, anchor, lag)
        for window in ROLLING_WINDOWS:
            mean, std, slope = rolling_features(z, anchor, window)
            out[f"lag_{name}_mean_{window}"] = mean
            out[f"lag_{name}_std_{window}"] = std
            out[f"lag_{name}_slope_{window}"] = slope
    return {key: finite(value) for key, value in out.items()}


def band_state(values, anchor, period):
    period = float(period)
    if anchor < max(16, int(math.ceil(4.0 * period))):
        return {
            "value": 0.0,
            "slope": 0.0,
            "amp": 0.0,
            "energy": 0.0,
            "theta": 0.0,
            "sin": 0.0,
            "cos": 1.0,
            "norm_value": 0.0,
        }
    arr = np.asarray(values[:anchor], dtype=float)
    bp = causal_bandpass(arr, period)
    rec = _measure_rung(bp, period, int(round(math.log(max(period, 1.001)) / math.log(PHI))))
    if rec is None:
        last = finite(bp[-1]) if len(bp) else 0.0
        prev = finite(bp[-2]) if len(bp) > 1 else last
        amp = 0.0
        theta = 0.0
    else:
        last = finite(bp[-1])
        prev = finite(bp[-2]) if len(bp) > 1 else last
        amp = finite(rec["amp"])
        theta = finite(rec["theta"])
    return {
        "value": last,
        "slope": last - prev,
        "amp": amp,
        "energy": amp * amp,
        "theta": theta,
        "sin": math.sin(theta),
        "cos": math.cos(theta),
        "norm_value": last / (amp + 1e-9),
    }


def projected_delta(state, horizon, period):
    amp = finite(state["amp"])
    theta = finite(state["theta"])
    period = float(period)
    return float(amp * (math.cos(theta + 2.0 * math.pi * horizon / period) - math.cos(theta)))


def phase_alignment(left_theta, right_theta):
    return math.cos(float(left_theta) - float(right_theta))


def block_features(state_cache, anchor, horizon, block_name, periods):
    out = {}
    for i, period in enumerate(periods):
        tag = f"{block_name}_p{i}"
        nino = state_cache[anchor]["NINO"][period]
        out[f"{tag}_period"] = float(period)
        for name in SIGNALS:
            st = state_cache[anchor][name][period]
            prefix = f"{tag}_{name.lower()}"
            out[f"{prefix}_value"] = st["value"]
            out[f"{prefix}_slope"] = st["slope"]
            out[f"{prefix}_amp"] = st["amp"]
            out[f"{prefix}_energy"] = st["energy"]
            out[f"{prefix}_norm_value"] = st["norm_value"]
            out[f"{prefix}_phase_sin"] = st["sin"]
            out[f"{prefix}_phase_cos"] = st["cos"]
            out[f"{prefix}_projected_delta"] = projected_delta(st, horizon, period)

        for feeder in FEEDERS:
            st = state_cache[anchor][feeder][period]
            align = phase_alignment(nino["theta"], st["theta"])
            energy_product = math.sqrt(max(nino["energy"], 0.0) * max(st["energy"], 0.0))
            feed_delta = projected_delta(st, horizon, period)
            prefix = f"{tag}_{feeder.lower()}_to_nino"
            out[f"{prefix}_alignment"] = align
            out[f"{prefix}_energy_product"] = energy_product
            out[f"{prefix}_signed_feed_delta"] = align * feed_delta
            out[f"{prefix}_support"] = energy_product * max(0.0, (1.0 + align) / 2.0)
            out[f"{prefix}_opposition"] = energy_product * max(0.0, (1.0 - align) / 2.0)
    return {key: finite(value) for key, value in out.items()}


def merge_dicts(*items):
    out = {}
    for item in items:
        out.update(item)
    return out


def build_state_cache(series, anchors, periods):
    cache = {}
    total = len(anchors)
    t0 = time.time()
    for i, anchor in enumerate(anchors, start=1):
        cache[anchor] = {}
        for name in SIGNALS:
            values = series[name]["z"]
            cache[anchor][name] = {period: band_state(values, anchor, period) for period in periods}
        if i % 50 == 0:
            print(f"  cached rung states {i:4d}/{total} in {time.time() - t0:.1f}s", flush=True)
    print(f"  cached rung states {total:4d}/{total} in {time.time() - t0:.1f}s")
    return cache


def build_feature_blocks(series, state_cache, anchors):
    blocks = {}
    for h in HORIZONS:
        blocks[h] = {}
        for anchor in anchors:
            lag = lag_features(series, anchor)
            home = block_features(state_cache, anchor, h, "home", [HOME])
            lower = block_features(state_cache, anchor, h, "lower_phi", LOWER_PHI)
            upper = block_features(state_cache, anchor, h, "upper_phi", UPPER_PHI)
            nonphi = block_features(state_cache, anchor, h, "lower_nonphi", LOWER_NONPHI)
            blocks[h][anchor] = {
                "lag": lag,
                "home": home,
                "lower": lower,
                "upper": upper,
                "nonphi_lower": nonphi,
            }
    return blocks


def variant_row(blocks_for_h, anchor, model_key, shuffled_lower_anchor=None):
    b = blocks_for_h[anchor]
    if model_key == "lag_ridge":
        return b["lag"]
    if model_key == "home_only":
        return merge_dicts(b["lag"], b["home"])
    if model_key == "home_plus_lower":
        return merge_dicts(b["lag"], b["home"], b["lower"])
    if model_key == "home_plus_upper":
        return merge_dicts(b["lag"], b["home"], b["upper"])
    if model_key == "home_plus_lower_upper":
        return merge_dicts(b["lag"], b["home"], b["lower"], b["upper"])
    if model_key == "home_plus_nonphi_lower":
        return merge_dicts(b["lag"], b["home"], b["nonphi_lower"])
    if model_key == "home_plus_shuffled_lower":
        source = shuffled_lower_anchor if shuffled_lower_anchor is not None else anchor
        return merge_dicts(b["lag"], b["home"], blocks_for_h[source]["lower"])
    raise KeyError(model_key)


def deterministic_shuffle(train_anchors, origin, horizon):
    rng = random.Random((int(origin) * 1009) + (int(horizon) * 9176) + 42)
    shuffled = list(train_anchors)
    rng.shuffle(shuffled)
    return dict(zip(train_anchors, shuffled))


def fit_predict_delta(train_rows, train_y, test_row):
    model = fit_ridge_model(train_rows, train_y, alpha=RIDGE_ALPHA)
    return float(predict_ridge_model(model, test_row)[0])


def score_model(points):
    return extended_score(points)


def improvement(score, base_score):
    return {
        "mae_delta_vs_home": finite(base_score.get("mae")) - finite(score.get("mae")),
        "corr_delta_vs_home": finite(score.get("corr")) - finite(base_score.get("corr")),
        "turn_delta_vs_home": finite(score.get("turn_accuracy")) - finite(base_score.get("turn_accuracy")),
    }


def summarize_focus(scores):
    focus = [6, 12, 24]
    out = {}
    for model in MODEL_KEYS:
        out[model] = {}
        for key in ["mae", "corr", "turn_accuracy", "enso_class_accuracy", "transition_mae"]:
            vals = [scores[model][str(h)].get(key) for h in focus if scores[model][str(h)].get(key) is not None]
            out[model][key] = float(np.mean(vals)) if vals else None
    return out


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    series = zscore_columns(frame)
    nino_raw = series["NINO"]["raw"]
    n = len(frame)

    all_periods = sorted({HOME, *LOWER_PHI, *UPPER_PHI, *LOWER_NONPHI})
    max_period = max(all_periods)
    max_h = max(HORIZONS)
    min_anchor = int(math.ceil(4.0 * max_period)) + 2
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01"))) + 1
    test_start = max(start_idx, min_anchor + MIN_TRAIN + max_h + 1)
    anchors = list(range(min_anchor, n + 1))

    print("ARA multi-rung feeder ablation")
    print("=" * 100)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()} n={n}")
    print(f"home period={HOME:.3f} months")
    print(f"lower phi periods={', '.join(f'{p:.2f}' for p in LOWER_PHI)}")
    print(f"upper phi periods={', '.join(f'{p:.2f}' for p in UPPER_PHI)}")
    print(f"nonphi lower periods={', '.join(f'{p:.2f}' for p in LOWER_NONPHI)}")
    print(f"test origins start: {dates[test_start - 1].date()} stride={ORIGIN_STRIDE}")
    print("strict guards: features use data[:t]; training s+h<t; shuffled lower from train anchors only")
    print()

    state_cache = build_state_cache(series, anchors, all_periods)
    print("  building horizon feature blocks...")
    blocks = build_feature_blocks(series, state_cache, anchors)
    print("  feature blocks ready")
    print()

    all_points = {model: {str(h): [] for h in HORIZONS} for model in MODEL_KEYS}

    for h in HORIZONS:
        origins = list(range(test_start, n - h + 1, ORIGIN_STRIDE))
        for origin in origins:
            target_anchor = origin + h
            train_anchors = [s for s in anchors if s + h < origin]
            if len(train_anchors) < MIN_TRAIN:
                continue
            actual = float(nino_raw[target_anchor - 1])
            current = float(nino_raw[origin - 1])
            origin_date = dates[origin - 1].strftime("%Y-%m-%d")
            target_date = dates[target_anchor - 1].strftime("%Y-%m-%d")
            y_train = [float(nino_raw[s + h - 1] - nino_raw[s - 1]) for s in train_anchors]

            shuffle_map = deterministic_shuffle(train_anchors, origin, h)
            shuffled_test_anchor = shuffle_map[train_anchors[-1]]

            for model in MODEL_KEYS:
                if model == "home_plus_shuffled_lower":
                    train_rows = [
                        variant_row(blocks[h], s, model, shuffled_lower_anchor=shuffle_map[s]) for s in train_anchors
                    ]
                    test_row = variant_row(blocks[h], origin, model, shuffled_lower_anchor=shuffled_test_anchor)
                else:
                    train_rows = [variant_row(blocks[h], s, model) for s in train_anchors]
                    test_row = variant_row(blocks[h], origin, model)
                pred_delta = fit_predict_delta(train_rows, y_train, test_row)
                pred = current + pred_delta
                all_points[model][str(h)].append(
                    point(
                        origin_date,
                        target_date,
                        pred,
                        actual,
                        current,
                        extras={
                            "origin_anchor": origin,
                            "target_anchor": target_anchor,
                            "train_n": len(train_anchors),
                        },
                    )
                )

        print(f"h={h:>2} months")
        home_score = score_model(all_points["home_only"][str(h)])
        for model in MODEL_KEYS:
            score = score_model(all_points[model][str(h)])
            imp = improvement(score, home_score) if model != "home_only" else None
            extra = ""
            if imp is not None and model != "lag_ridge":
                extra = f" | dMAE_vs_home={imp['mae_delta_vs_home']:+.4f} dCorr={imp['corr_delta_vs_home']:+.3f}"
            print(f"  {model:28s} {format_score(score)}{extra}")
        print()

    scores = {model: {str(h): score_model(all_points[model][str(h)]) for h in HORIZONS} for model in MODEL_KEYS}
    improvements = {
        model: {
            str(h): improvement(scores[model][str(h)], scores["home_only"][str(h)])
            for h in HORIZONS
            if model != "home_only"
        }
        for model in MODEL_KEYS
        if model != "home_only"
    }
    focus_summary = summarize_focus(scores)
    winners = {
        str(h): {
            "mae": min(MODEL_KEYS, key=lambda m: scores[m][str(h)].get("mae", float("inf"))),
            "corr": max(MODEL_KEYS, key=lambda m: scores[m][str(h)].get("corr", -float("inf"))),
        }
        for h in HORIZONS
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal multi-rung feeder ablation",
        "leakage_guard": [
            "Every feature at anchor t uses only data[:t].",
            "Training for origin t and horizon h uses only anchors s where s+h<t.",
            "Shuffled lower features are drawn only from allowed training anchors.",
            "No result selects periods or horizons from forecast performance.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "home_period_months": HOME,
        "home_period_definition": "fixed ENSO home period used in prior tests",
        "lower_phi_periods_months": LOWER_PHI,
        "upper_phi_periods_months": UPPER_PHI,
        "lower_nonphi_base": LOWER_NONPHI_BASE,
        "lower_nonphi_periods_months": LOWER_NONPHI,
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "ridge_alpha": RIDGE_ALPHA,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
            "min_anchor": int(min_anchor),
        },
        "models": {
            "lag_ridge": "Raw lag/inertia features only.",
            "home_only": "Lag/inertia plus home-rung NINO/SOI/PDO geometry.",
            "home_plus_lower": "Home plus phi-spaced lower/faster rungs.",
            "home_plus_upper": "Home plus phi-spaced upper/slower envelope rungs.",
            "home_plus_lower_upper": "Home plus both lower and upper phi rungs.",
            "home_plus_shuffled_lower": "Home plus lower phi features mismatched from causal past training anchors.",
            "home_plus_nonphi_lower": "Home plus base-2 lower/faster periods instead of phi lower rungs.",
        },
        "scores": clean_for_json(scores),
        "improvements_vs_home": clean_for_json(improvements),
        "focus_6_12_24": clean_for_json(focus_summary),
        "winners": clean_for_json(winners),
        "example_points": {
            model: {str(h): all_points[model][str(h)][:8] for h in HORIZONS}
            for model in MODEL_KEYS
        },
        "elapsed_seconds": rounded(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_MULTIRUNG_FEEDER_ABLATION = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Focus 6/12/24:")
    for model in MODEL_KEYS:
        s = focus_summary[model]
        print(
            f"  {model:28s} MAE={s['mae']:.4f} corr={s['corr']:+.3f}"
            f" turn={s['turn_accuracy']:.3f} transMAE={s['transition_mae']:.4f}"
        )
    print("Winners:")
    for h in HORIZONS:
        print(f"  h={h:>2}: mae={winners[str(h)]['mae']} corr={winners[str(h)]['corr']}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
