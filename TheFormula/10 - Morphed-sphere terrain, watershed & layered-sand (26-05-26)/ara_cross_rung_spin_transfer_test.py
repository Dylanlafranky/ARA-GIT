"""
ara_cross_rung_spin_transfer_test.py

Strict-causal test of the subtler cross-rung feeder theory:

    lower/faster rungs feed by spin, phase pressure, and crossover timing
    home rung carries the visible ENSO cycle state
    upper/slower rungs hold reservoir/envelope constraints

This is intentionally different from ara_multirung_feeder_ablation.py, which
tested lower rungs as direct value/amplitude feature blocks.

Claims tested:

  1. Faster-spin claim:
     lower phase turn rate > home phase turn rate > upper phase turn rate.

  2. Feeder-timing claim:
     lower spin/phase pressure helps rank future boundary/event and transition
     risk better than lag-only risk features.

  3. Orientation claim:
     lower-home alignment/opposition changes transfer cleanliness and lag-risk.

  4. Energy-envelope claim:
     upper/slower reservoir features help amplitude-size prediction more than
     lower/faster spin features.

Leakage guard:

  - Every feature at origin t uses only data[:t].
  - Base lag prediction at origin t uses only anchors s where s+h<t.
  - Risk/amplitude/time-to-transition models for origin t train only on
    previous records whose required outcomes would already be known.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import HOME_PERIOD, START_YEAR, clean_for_json, load_enso_frame, zscore_columns
from ara_lag_phase_hybrid_predictor import enso_class, extended_score, finite, format_score, point
from ara_multirung_feeder_ablation import band_state, lag_features
from ara_transition_risk_and_uncertainty_model import auc_score


PHI = (1.0 + math.sqrt(5.0)) / 2.0

OUT_JSON = HERE / "ara_cross_rung_spin_transfer_result.json"
OUT_JS = HERE / "ara_cross_rung_spin_transfer_result.js"

HOME = float(HOME_PERIOD)
LOWER_PERIODS = [HOME / (PHI**3), HOME / (PHI**2), HOME / PHI]
HOME_PERIODS = [HOME]
UPPER_PERIODS = [HOME * PHI, HOME * (PHI**2)]
ALL_PERIODS = sorted({*LOWER_PERIODS, *HOME_PERIODS, *UPPER_PERIODS})

SIGNALS = ["NINO", "SOI", "PDO"]
FEEDERS = ["SOI", "PDO"]
HORIZONS = [3, 6, 12, 18, 24]
ORIGIN_STRIDE = 3
MIN_TRAIN = 96
MIN_RISK_TRAIN = 36
RIDGE_ALPHA_LAG = 12.0
RIDGE_ALPHA_RISK = 8.0
RIDGE_ALPHA_REGRESSION = 10.0
TIME_TO_TRANSITION_WINDOW = 24
HIGH_ERROR_QUANTILE = 0.75
EPS = 1e-9

RISK_TARGETS = [
    "lag_abs_error_high",
    "lag_turn_failure",
    "boundary_crossing",
    "enso_class_transition",
    "home_phase_turn",
]

FEATURE_GROUPS = [
    "lag_only",
    "lag_plus_lower_spin",
    "lag_plus_upper_envelope",
    "lag_plus_alignment",
    "lag_plus_all_spin_transfer",
]


def rounded(value, digits=6):
    if value is None:
        return None
    return round(finite(value), digits)


def sign(value):
    value = finite(value)
    if value > EPS:
        return 1
    if value < -EPS:
        return -1
    return 0


def angle_diff(a, b):
    return math.atan2(math.sin(float(a) - float(b)), math.cos(float(a) - float(b)))


def phase_velocity(cache, anchor, signal, period, lag=1):
    prior = anchor - int(lag)
    if prior not in cache:
        return 0.0
    return angle_diff(cache[anchor][signal][period]["theta"], cache[prior][signal][period]["theta"]) / float(lag)


def phase_acceleration(cache, anchor, signal, period, lag=3):
    prior = anchor - int(lag)
    if prior not in cache:
        return 0.0
    return phase_velocity(cache, anchor, signal, period, lag) - phase_velocity(cache, prior, signal, period, lag)


def turn_density(cache, anchor, signal, periods, window=12):
    vals = []
    start = max(min(cache), anchor - int(window) + 1)
    for period in periods:
        for a in range(start + 1, anchor + 1):
            if a in cache and (a - 1) in cache:
                vals.append(abs(phase_velocity(cache, a, signal, period, 1)))
    return float(np.sum(vals)) if vals else 0.0


def velocity_sign_change_density(cache, anchor, signal, periods, window=12):
    count = 0
    total = 0
    start = max(min(cache), anchor - int(window) + 2)
    for period in periods:
        prev = None
        for a in range(start, anchor + 1):
            if a not in cache or (a - 1) not in cache:
                continue
            current = sign(phase_velocity(cache, a, signal, period, 1))
            if prev is not None:
                count += 1 if current != 0 and prev != 0 and current != prev else 0
                total += 1
            prev = current
    return float(count) / float(max(1, total))


def mean_period_feature(cache, anchor, signal, periods, key):
    vals = [finite(cache[anchor][signal][period].get(key, 0.0)) for period in periods]
    return float(np.mean(vals)) if vals else 0.0


def group_spin_features(cache, anchor, group_name, periods):
    out = {}
    for signal_name in SIGNALS:
        velocities_1 = [phase_velocity(cache, anchor, signal_name, p, 1) for p in periods]
        velocities_3 = [phase_velocity(cache, anchor, signal_name, p, 3) for p in periods]
        accelerations = [phase_acceleration(cache, anchor, signal_name, p, 3) for p in periods]
        energies = [finite(cache[anchor][signal_name][p].get("energy", 0.0)) for p in periods]
        amps = [finite(cache[anchor][signal_name][p].get("amp", 0.0)) for p in periods]
        out[f"{group_name}_{signal_name}_mean_phase_velocity_1"] = float(np.mean(velocities_1))
        out[f"{group_name}_{signal_name}_abs_phase_velocity_1"] = float(np.mean(np.abs(velocities_1)))
        out[f"{group_name}_{signal_name}_mean_phase_velocity_3"] = float(np.mean(velocities_3))
        out[f"{group_name}_{signal_name}_phase_acceleration_3"] = float(np.mean(accelerations))
        out[f"{group_name}_{signal_name}_turn_density_12"] = turn_density(cache, anchor, signal_name, periods, 12)
        out[f"{group_name}_{signal_name}_sign_change_density_12"] = velocity_sign_change_density(
            cache, anchor, signal_name, periods, 12
        )
        out[f"{group_name}_{signal_name}_mean_amp"] = float(np.mean(amps))
        out[f"{group_name}_{signal_name}_mean_energy"] = float(np.mean(energies))
        out[f"{group_name}_{signal_name}_frequency_pressure"] = float(
            np.mean([abs(v) * (HOME / p) for v, p in zip(velocities_1, periods)])
        )
    return {key: finite(value) for key, value in out.items()}


def phase_lock_features(cache, anchor):
    out = {}
    for lower_period in LOWER_PERIODS:
        for feeder in FEEDERS:
            lower = cache[anchor][feeder][lower_period]
            home = cache[anchor]["NINO"][HOME]
            lv = phase_velocity(cache, anchor, feeder, lower_period, 1)
            hv = phase_velocity(cache, anchor, "NINO", HOME, 1)
            diff = angle_diff(lower["theta"], home["theta"])
            align = math.cos(diff)
            orientation = sign(lv) * sign(hv)
            prefix = f"lower_{feeder}_p{int(round(lower_period * 100))}_to_home"
            out[f"{prefix}_phase_lead"] = diff
            out[f"{prefix}_phase_lock"] = align
            out[f"{prefix}_orientation_agreement"] = orientation
            out[f"{prefix}_frequency_pressure"] = abs(lv) * (HOME / lower_period)
            out[f"{prefix}_aligned_pressure"] = max(0.0, align * orientation) * abs(lv) * (HOME / lower_period)
            out[f"{prefix}_opposed_pressure"] = max(0.0, -align * orientation) * abs(lv) * (HOME / lower_period)

    locks = [value for key, value in out.items() if key.endswith("_phase_lock")]
    orientations = [value for key, value in out.items() if key.endswith("_orientation_agreement")]
    aligned_pressures = [value for key, value in out.items() if key.endswith("_aligned_pressure")]
    opposed_pressures = [value for key, value in out.items() if key.endswith("_opposed_pressure")]
    out["lower_home_mean_phase_lock"] = float(np.mean(locks)) if locks else 0.0
    out["lower_home_abs_phase_lock"] = float(np.mean(np.abs(locks))) if locks else 0.0
    out["lower_home_orientation_agreement"] = float(np.mean(orientations)) if orientations else 0.0
    out["lower_home_aligned_pressure"] = float(np.sum(aligned_pressures))
    out["lower_home_opposed_pressure"] = float(np.sum(opposed_pressures))
    out["lower_home_pressure_balance"] = out["lower_home_aligned_pressure"] - out["lower_home_opposed_pressure"]
    return {key: finite(value) for key, value in out.items()}


def class_distance(value):
    value = finite(value)
    if value > 0.0:
        return abs(0.5 - value)
    return abs(-0.5 - value)


def current_boundary_features(series, anchor):
    nino = series["NINO"]["raw"]
    current = finite(nino[anchor - 1])
    return {
        "current_nino": current,
        "current_abs_nino": abs(current),
        "current_boundary_distance": class_distance(current),
        "current_near_boundary": 1.0 if abs(abs(current) - 0.5) <= 0.25 else 0.0,
    }


def upper_envelope_features(cache, anchor):
    out = group_spin_features(cache, anchor, "upper", UPPER_PERIODS)
    energies = []
    amps = []
    slopes = []
    for signal_name in SIGNALS:
        for period in UPPER_PERIODS:
            st = cache[anchor][signal_name][period]
            energies.append(finite(st["energy"]))
            amps.append(finite(st["amp"]))
            slopes.append(finite(st["slope"]))
    out["upper_reservoir_energy"] = float(np.sum(energies))
    out["upper_reservoir_amp"] = float(np.sum(amps))
    out["upper_envelope_slope"] = float(np.mean(slopes)) if slopes else 0.0
    return {key: finite(value) for key, value in out.items()}


def build_feature_sets(series, cache, anchor):
    lag = lag_features(series, anchor)
    lower = group_spin_features(cache, anchor, "lower", LOWER_PERIODS)
    home = group_spin_features(cache, anchor, "home", HOME_PERIODS)
    upper = upper_envelope_features(cache, anchor)
    align = phase_lock_features(cache, anchor)
    boundary = current_boundary_features(series, anchor)

    lower["lower_crossover_density"] = lower.get("lower_NINO_turn_density_12", 0.0) / (
        1.0 + boundary["current_boundary_distance"]
    )
    lower["lower_burst_count_near_boundary"] = (
        lower.get("lower_NINO_sign_change_density_12", 0.0)
        + lower.get("lower_SOI_sign_change_density_12", 0.0)
        + lower.get("lower_PDO_sign_change_density_12", 0.0)
    ) * boundary["current_near_boundary"]

    return {
        "lag_only": lag,
        "lag_plus_lower_spin": {**lag, **boundary, **lower, **home},
        "lag_plus_upper_envelope": {**lag, **boundary, **upper, **home},
        "lag_plus_alignment": {**lag, **boundary, **home, **align},
        "lag_plus_all_spin_transfer": {**lag, **boundary, **lower, **home, **upper, **align},
        "_parts": {"lag": lag, "lower": lower, "home": home, "upper": upper, "align": align, "boundary": boundary},
    }


def fit_predict(train_rows, train_y, row, alpha):
    model = fit_ridge_model(train_rows, train_y, alpha=alpha)
    return float(predict_ridge_model(model, row)[0])


def clip_prob(value):
    return float(min(0.98, max(0.02, finite(value, 0.5))))


def predict_prob(train_rows, train_y, row):
    labels = [float(v) for v in train_y]
    if len(set(int(v) for v in labels)) < 2:
        return float(np.mean(labels)) if labels else 0.5
    return clip_prob(fit_predict(train_rows, labels, row, RIDGE_ALPHA_RISK))


def risk_metric(records, group, target):
    usable = [r for r in records if r.get("risk_ready") and f"prob_{group}_{target}" in r]
    if not usable:
        return {"n": 0}
    labels = np.asarray([int(r[target]) for r in usable], dtype=int)
    probs = np.asarray([finite(r[f"prob_{group}_{target}"], 0.5) for r in usable], dtype=float)
    event_rate = float(np.mean(labels))
    top_cut = float(np.quantile(probs, 0.75))
    bottom_cut = float(np.quantile(probs, 0.25))
    top = labels[probs >= top_cut]
    bottom = labels[probs <= bottom_cut]
    top_rate = float(np.mean(top)) if len(top) else None
    bottom_rate = float(np.mean(bottom)) if len(bottom) else None
    return {
        "n": int(len(usable)),
        "event_rate": event_rate,
        "mean_probability": float(np.mean(probs)),
        "brier": float(np.mean((probs - labels) ** 2)),
        "auc": auc_score(labels, probs),
        "top_quartile_event_rate": top_rate,
        "bottom_quartile_event_rate": bottom_rate,
        "top_vs_base_lift": top_rate / event_rate if top_rate is not None and event_rate > EPS else None,
        "top_vs_bottom_lift": top_rate / bottom_rate if top_rate is not None and bottom_rate is not None and bottom_rate > EPS else None,
    }


def regression_metric(records, group, target):
    usable = [r for r in records if r.get("risk_ready") and f"pred_{group}_{target}" in r]
    if not usable:
        return {"n": 0}
    pred = np.asarray([finite(r[f"pred_{group}_{target}"]) for r in usable], dtype=float)
    actual = np.asarray([finite(r[target]) for r in usable], dtype=float)
    mae = float(np.mean(np.abs(pred - actual)))
    corr = (
        float(np.corrcoef(pred, actual)[0, 1])
        if len(pred) >= 5 and pred.std() > EPS and actual.std() > EPS
        else None
    )
    return {
        "n": int(len(usable)),
        "mae": mae,
        "corr": corr,
        "pred_std": float(np.std(pred)),
        "actual_std": float(np.std(actual)),
    }


def transfer_cleanliness(records):
    if not records:
        return {
            "n": 0,
            "lag_mae": None,
            "lag_turn_failure_rate": None,
            "boundary_crossing_rate": None,
            "class_transition_rate": None,
            "home_phase_turn_rate": None,
            "mean_time_to_transition": None,
        }
    return {
        "n": int(len(records)),
        "lag_mae": float(np.mean([r["lag_abs_error"] for r in records])),
        "lag_turn_failure_rate": float(np.mean([r["lag_turn_failure"] for r in records])),
        "boundary_crossing_rate": float(np.mean([r["boundary_crossing"] for r in records])),
        "class_transition_rate": float(np.mean([r["enso_class_transition"] for r in records])),
        "home_phase_turn_rate": float(np.mean([r["home_phase_turn"] for r in records])),
        "mean_time_to_transition": float(np.mean([r["time_to_transition"] for r in records])),
    }


def alignment_subset_metrics(records):
    ready = [r for r in records if "lag_abs_error" in r]
    if not ready:
        return {}
    pressure = np.asarray(
        [finite(r["feature_parts"]["align"].get("lower_home_pressure_balance", 0.0)) for r in ready],
        dtype=float,
    )
    orientation = np.asarray(
        [finite(r["feature_parts"]["align"].get("lower_home_orientation_agreement", 0.0)) for r in ready],
        dtype=float,
    )
    high_aligned_cut = float(np.quantile(pressure, 0.75))
    high_opposed_cut = float(np.quantile(pressure, 0.25))
    return {
        "pressure_aligned_positive": transfer_cleanliness([r for r in ready if r["feature_parts"]["align"].get("lower_home_pressure_balance", 0.0) >= 0.0]),
        "pressure_opposed_negative": transfer_cleanliness([r for r in ready if r["feature_parts"]["align"].get("lower_home_pressure_balance", 0.0) < 0.0]),
        "pressure_top_quartile_aligned": transfer_cleanliness(
            [r for r in ready if r["feature_parts"]["align"].get("lower_home_pressure_balance", 0.0) >= high_aligned_cut]
        ),
        "pressure_bottom_quartile_opposed": transfer_cleanliness(
            [r for r in ready if r["feature_parts"]["align"].get("lower_home_pressure_balance", 0.0) <= high_opposed_cut]
        ),
        "orientation_agree_nonnegative": transfer_cleanliness(
            [r for r, value in zip(ready, orientation) if value >= 0.0]
        ),
        "orientation_oppose_negative": transfer_cleanliness(
            [r for r, value in zip(ready, orientation) if value < 0.0]
        ),
    }


def future_boundary_crossing(record):
    return enso_class(record["actual"]) != "neutral"


def class_transition(record):
    return enso_class(record["actual"]) != enso_class(record["current"])


def home_phase_turn(cache, record):
    origin = record["origin_anchor"]
    target = record["target_anchor"]
    if origin not in cache or target not in cache:
        return False
    current_v = phase_velocity(cache, origin, "NINO", HOME, 3)
    future_v = phase_velocity(cache, target, "NINO", HOME, 3)
    return sign(current_v) != 0 and sign(future_v) != 0 and sign(current_v) != sign(future_v)


def time_to_transition(values, origin, max_window=TIME_TO_TRANSITION_WINDOW):
    current_class = enso_class(values[origin - 1])
    for step in range(1, max_window + 1):
        idx = origin - 1 + step
        if idx >= len(values):
            break
        if enso_class(values[idx]) != current_class:
            return float(step)
    return float(max_window + 1)


def add_lag_predictions(records, series, horizon):
    for record in records:
        origin = record["origin_anchor"]
        train = [r for r in records if r["origin_anchor"] + horizon < origin]
        if len(train) < MIN_TRAIN:
            record["lag_pred"] = record["current"]
            continue
        train_rows = [r["feature_sets"]["lag_only"] for r in train]
        train_y = [r["actual"] - r["current"] for r in train]
        pred_delta = fit_predict(train_rows, train_y, record["feature_sets"]["lag_only"], RIDGE_ALPHA_LAG)
        record["lag_pred"] = record["current"] + pred_delta


def add_outcome_labels(records, cache, series, horizon):
    nino = series["NINO"]["raw"]
    for i, record in enumerate(records):
        record["lag_abs_error"] = abs(record["lag_pred"] - record["actual"])
        origin = record["origin_anchor"]
        past = [r for r in records[:i] if r["target_anchor"] < origin and "lag_abs_error" in r]
        if past:
            threshold = float(np.quantile([r["lag_abs_error"] for r in past], HIGH_ERROR_QUANTILE))
        else:
            threshold = float("inf")
        record["lag_abs_error_high"] = bool(record["lag_abs_error"] >= threshold)
        record["lag_abs_error_high_threshold"] = threshold if math.isfinite(threshold) else None
        record["lag_turn_failure"] = bool(sign(record["lag_pred"] - record["current"]) != sign(record["actual"] - record["current"]))
        record["boundary_crossing"] = bool(future_boundary_crossing(record))
        record["enso_class_transition"] = bool(class_transition(record))
        record["home_phase_turn"] = bool(home_phase_turn(cache, record))
        record["future_amplitude_size"] = abs(record["actual"] - record["current"])
        record["time_to_transition"] = time_to_transition(nino, origin, TIME_TO_TRANSITION_WINDOW)


def add_causal_models(records):
    for record in records:
        origin = record["origin_anchor"]
        risk_past = [r for r in records if r["target_anchor"] < origin and "lag_abs_error_high" in r]
        ttt_past = [
            r
            for r in records
            if r["origin_anchor"] + TIME_TO_TRANSITION_WINDOW < origin and "time_to_transition" in r
        ]
        if len(risk_past) < MIN_RISK_TRAIN:
            record["risk_ready"] = False
            continue
        record["risk_ready"] = True
        for group in FEATURE_GROUPS:
            train_rows = [r["feature_sets"][group] for r in risk_past]
            row = record["feature_sets"][group]
            for target in RISK_TARGETS:
                record[f"prob_{group}_{target}"] = predict_prob(train_rows, [r[target] for r in risk_past], row)
            record[f"pred_{group}_future_amplitude_size"] = max(
                0.0,
                fit_predict(
                    train_rows,
                    [r["future_amplitude_size"] for r in risk_past],
                    row,
                    RIDGE_ALPHA_REGRESSION,
                ),
            )
            if len(ttt_past) >= MIN_RISK_TRAIN:
                record[f"pred_{group}_time_to_transition"] = max(
                    1.0,
                    min(
                        TIME_TO_TRANSITION_WINDOW + 1.0,
                        fit_predict(
                            [r["feature_sets"][group] for r in ttt_past],
                            [r["time_to_transition"] for r in ttt_past],
                            row,
                            RIDGE_ALPHA_REGRESSION,
                        ),
                    ),
                )


def point_records(records):
    return [point(r["origin_date"], r["target_date"], r["lag_pred"], r["actual"], r["current"]) for r in records]


def spin_rate_summary(cache, origins):
    out = {}
    for group_name, periods in [("lower", LOWER_PERIODS), ("home", HOME_PERIODS), ("upper", UPPER_PERIODS)]:
        out[group_name] = {}
        for signal_name in SIGNALS:
            rates = []
            signs = []
            for origin in origins:
                if origin not in cache:
                    continue
                vals = [phase_velocity(cache, origin, signal_name, p, 1) for p in periods]
                rates.append(float(np.mean(np.abs(vals))))
                signs.extend([sign(v) for v in vals if sign(v) != 0])
            out[group_name][signal_name] = {
                "mean_abs_turn_rate": float(np.mean(rates)) if rates else None,
                "median_abs_turn_rate": float(np.median(rates)) if rates else None,
                "positive_spin_fraction": float(np.mean([s > 0 for s in signs])) if signs else None,
                "n": int(len(rates)),
            }
    for signal_name in SIGNALS:
        lower = out["lower"][signal_name]["mean_abs_turn_rate"]
        home = out["home"][signal_name]["mean_abs_turn_rate"]
        upper = out["upper"][signal_name]["mean_abs_turn_rate"]
        out[f"{signal_name}_monotonic_lower_gt_home_gt_upper"] = bool(
            lower is not None and home is not None and upper is not None and lower > home > upper
        )
    return out


def aggregate_focus(metrics_by_h, horizons, model_key=None):
    selected = [metrics_by_h[str(h)] for h in horizons]
    out = {}
    keys = sorted({key for item in selected for key in item.keys()})
    for key in keys:
        vals = [item[key] for item in selected if item.get(key) is not None]
        if key == "n":
            out[key] = int(sum(vals))
        else:
            out[key] = float(np.mean(vals)) if vals else None
    return out


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    series = zscore_columns(frame)
    nino_raw = series["NINO"]["raw"]
    n = len(frame)
    max_h = max(HORIZONS)
    min_anchor = int(math.ceil(4.0 * max(ALL_PERIODS))) + 2
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01"))) + 1
    test_start = max(start_idx, min_anchor + MIN_TRAIN + TIME_TO_TRANSITION_WINDOW + max_h + 1)
    all_anchors = list(range(min_anchor, n + 1))

    print("ARA cross-rung spin transfer test")
    print("=" * 100)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()} n={n}")
    print(f"lower={', '.join(f'{p:.2f}' for p in LOWER_PERIODS)}")
    print(f"home={HOME:.2f}")
    print(f"upper={', '.join(f'{p:.2f}' for p in UPPER_PERIODS)}")
    print(f"test origins start: {dates[test_start - 1].date()} stride={ORIGIN_STRIDE}")
    print("strict guards: features use data[:t]; base lag s+h<t; risk/ttt train only known past outcomes")
    print()

    cache = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        cache[anchor] = {
            signal_name: {period: band_state(series[signal_name]["z"], anchor, period) for period in ALL_PERIODS}
            for signal_name in SIGNALS
        }
        if i % 50 == 0:
            print(f"  cached spin states {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  cached spin states {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s")
    print()

    test_origins = list(range(test_start, n - max_h + 1, ORIGIN_STRIDE))
    spin_summary = spin_rate_summary(cache, test_origins)

    records_by_h = {}
    lag_scores = {}
    risk_metrics = {}
    amplitude_metrics = {}
    time_to_transition_metrics = {}
    alignment_metrics = {}

    for h in HORIZONS:
        records = []
        origins = list(range(min_anchor + max_h + 1, n - h + 1, ORIGIN_STRIDE))
        for origin in origins:
            target_anchor = origin + h
            if target_anchor > n:
                continue
            feature_sets = build_feature_sets(series, cache, origin)
            records.append(
                {
                    "horizon": int(h),
                    "origin_anchor": int(origin),
                    "target_anchor": int(target_anchor),
                    "origin_date": dates[origin - 1].strftime("%Y-%m-%d"),
                    "target_date": dates[target_anchor - 1].strftime("%Y-%m-%d"),
                    "is_test": bool(origin >= test_start),
                    "current": float(nino_raw[origin - 1]),
                    "actual": float(nino_raw[target_anchor - 1]),
                    "feature_sets": {key: val for key, val in feature_sets.items() if key != "_parts"},
                    "feature_parts": feature_sets["_parts"],
                }
            )

        add_lag_predictions(records, series, h)
        add_outcome_labels(records, cache, series, h)
        add_causal_models(records)
        eval_records = [r for r in records if r["is_test"]]
        records_by_h[str(h)] = eval_records
        lag_scores[str(h)] = extended_score(point_records(eval_records))

        risk_metrics[str(h)] = {
            group: {target: risk_metric(eval_records, group, target) for target in RISK_TARGETS}
            for group in FEATURE_GROUPS
        }
        amplitude_metrics[str(h)] = {
            group: regression_metric(eval_records, group, "future_amplitude_size") for group in FEATURE_GROUPS
        }
        time_to_transition_metrics[str(h)] = {
            group: regression_metric(eval_records, group, "time_to_transition") for group in FEATURE_GROUPS
        }
        alignment_metrics[str(h)] = alignment_subset_metrics(eval_records)

        print(f"h={h:>2} months")
        print(f"  lag central: {format_score(lag_scores[str(h)])}")
        for group in FEATURE_GROUPS:
            b = risk_metrics[str(h)][group]["boundary_crossing"]
            tr = risk_metrics[str(h)][group]["enso_class_transition"]
            amp = amplitude_metrics[str(h)][group]
            ttt = time_to_transition_metrics[str(h)][group]
            print(
                f"  {group:28s}"
                f" boundary_auc={b.get('auc') if b.get('auc') is not None else float('nan'):+.3f}"
                f" trans_auc={tr.get('auc') if tr.get('auc') is not None else float('nan'):+.3f}"
                f" amp_mae={amp.get('mae') if amp.get('mae') is not None else float('nan'):.3f}"
                f" amp_corr={amp.get('corr') if amp.get('corr') is not None else float('nan'):+.3f}"
                f" ttt_mae={ttt.get('mae') if ttt.get('mae') is not None else float('nan'):.3f}"
                f" ttt_corr={ttt.get('corr') if ttt.get('corr') is not None else float('nan'):+.3f}"
            )
        print()
        align_now = alignment_metrics[str(h)]
        if align_now:
            pos = align_now["pressure_top_quartile_aligned"]
            neg = align_now["pressure_bottom_quartile_opposed"]
            print(
                "  transfer pressure quartiles:"
                f" aligned_lag_mae={pos['lag_mae']:.3f} aligned_turn_fail={pos['lag_turn_failure_rate']:.3f}"
                f" opposed_lag_mae={neg['lag_mae']:.3f} opposed_turn_fail={neg['lag_turn_failure_rate']:.3f}"
            )
            print()

    focus_horizons = [6, 12, 24]
    focus = {
        "lag_scores": aggregate_focus(lag_scores, focus_horizons),
        "risk_metrics": {},
        "amplitude_metrics": {},
        "time_to_transition_metrics": {},
        "alignment_metrics": {},
    }
    for group in FEATURE_GROUPS:
        focus["risk_metrics"][group] = {
            target: aggregate_focus({h: risk_metrics[h][group][target] for h in risk_metrics}, focus_horizons)
            for target in RISK_TARGETS
        }
        focus["amplitude_metrics"][group] = aggregate_focus(
            {h: amplitude_metrics[h][group] for h in amplitude_metrics}, focus_horizons
        )
        focus["time_to_transition_metrics"][group] = aggregate_focus(
            {h: time_to_transition_metrics[h][group] for h in time_to_transition_metrics}, focus_horizons
        )
    focus["alignment_metrics"] = {
        subset: aggregate_focus({h: alignment_metrics[h][subset] for h in alignment_metrics}, focus_horizons)
        for subset in next(iter(alignment_metrics.values())).keys()
    }

    slim_examples = {
        h: [
            {
                "origin": r["origin_date"],
                "target": r["target_date"],
                "current": rounded(r["current"]),
                "actual": rounded(r["actual"]),
                "lag_pred": rounded(r["lag_pred"]),
                "boundary_crossing": r["boundary_crossing"],
                "enso_class_transition": r["enso_class_transition"],
                "home_phase_turn": r["home_phase_turn"],
                "time_to_transition": rounded(r["time_to_transition"]),
                "lower_home_orientation_agreement": rounded(
                    r["feature_parts"]["align"].get("lower_home_orientation_agreement")
                ),
                "lower_home_pressure_balance": rounded(r["feature_parts"]["align"].get("lower_home_pressure_balance")),
            }
            for r in records[:10]
        ]
        for h, records in records_by_h.items()
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal cross-rung spin transfer test",
        "leakage_guard": [
            "Every feature at origin t uses only data[:t].",
            "Base lag prediction at origin t uses only anchors s where s+h<t.",
            "Risk/amplitude/time-to-transition models for origin t train only on previous records whose required outcomes would already be known.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly and transition/risk labels",
        "periods": {
            "lower": LOWER_PERIODS,
            "home": HOME_PERIODS,
            "upper": UPPER_PERIODS,
        },
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "time_to_transition_window_months": TIME_TO_TRANSITION_WINDOW,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
            "min_anchor": int(min_anchor),
        },
        "spin_rate_summary": clean_for_json(spin_summary),
        "lag_central_scores": clean_for_json(lag_scores),
        "risk_metrics": clean_for_json(risk_metrics),
        "amplitude_metrics": clean_for_json(amplitude_metrics),
        "time_to_transition_metrics": clean_for_json(time_to_transition_metrics),
        "alignment_metrics": clean_for_json(alignment_metrics),
        "focus_6_12_24": clean_for_json(focus),
        "example_records": clean_for_json(slim_examples),
        "elapsed_seconds": rounded(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_CROSS_RUNG_SPIN_TRANSFER = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Spin-rate summary:")
    for signal_name in SIGNALS:
        lower = spin_summary["lower"][signal_name]["mean_abs_turn_rate"]
        home = spin_summary["home"][signal_name]["mean_abs_turn_rate"]
        upper = spin_summary["upper"][signal_name]["mean_abs_turn_rate"]
        print(
            f"  {signal_name:4s}: lower={lower:.4f} home={home:.4f} upper={upper:.4f}"
            f" monotonic={spin_summary[f'{signal_name}_monotonic_lower_gt_home_gt_upper']}"
        )
    print("Focus 6/12/24 boundary AUC / amplitude corr / time-to-transition corr:")
    for group in FEATURE_GROUPS:
        b = focus["risk_metrics"][group]["boundary_crossing"]
        amp = focus["amplitude_metrics"][group]
        ttt = focus["time_to_transition_metrics"][group]
        print(
            f"  {group:28s}"
            f" boundary_auc={b.get('auc') if b.get('auc') is not None else float('nan'):+.3f}"
            f" lift={b.get('top_vs_base_lift') if b.get('top_vs_base_lift') is not None else float('nan'):.3f}"
            f" amp_corr={amp.get('corr') if amp.get('corr') is not None else float('nan'):+.3f}"
            f" ttt_corr={ttt.get('corr') if ttt.get('corr') is not None else float('nan'):+.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
