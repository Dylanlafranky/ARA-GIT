"""
ara_triangle_amplitude_gate_test.py

Strict-causal test for the triangle-location amplitude idea:

    larger future movement should occur when a system is pulled away from its
    coupled pair edge and toward a slower / third-corner donor region.

This script deliberately separates amplitude from direction:
  - diagnostic: does the triangle-pull coordinate predict |future delta|?
  - gate: can triangle-pull features rescale an existing ARA decoder's delta?

The feature builder is single-signal and therefore runs on ENSO, Solar, and ECG
without hardcoding NINO/SOI/PDO.  ENSO's richer named subsystem triangle remains
a separate follow-up; this is the universal topography check.
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

from ara_geometry_transport_test import clean_for_json, fit_predict_ridge, score_points
from ara_phi_distance_bk_fit_test import (
    PI_LEAK_ENERGY,
    PHI,
    label_for,
    load_ecg_rr,
    load_enso,
    load_solar,
    read_signal_state,
)


BASE_MODELS = [
    "fixed_1_plus_pi_leak_phi_distance_decoder",
    "learned_bk_phi_distance_decoder",
    "lag_ridge",
]


def load_js_data(path: Path):
    text = path.read_text(encoding="utf-8")
    payload = text.split("=", 1)[1].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    return json.loads(payload)


def finite(value, default=0.0):
    try:
        value = float(value)
    except Exception:
        return float(default)
    if not math.isfinite(value):
        return float(default)
    return value


def corr(x, y):
    x = np.asarray([finite(v, float("nan")) for v in x], dtype=float)
    y = np.asarray([finite(v, float("nan")) for v in y], dtype=float)
    good = np.isfinite(x) & np.isfinite(y)
    x = x[good]
    y = y[good]
    if len(x) < 5 or float(np.std(x)) < 1e-12 or float(np.std(y)) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def summarize(values):
    vals = np.asarray([finite(v, float("nan")) for v in values], dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return {"n": 0}
    return {
        "n": int(len(vals)),
        "mean": float(np.mean(vals)),
        "std": float(np.std(vals)),
        "p25": float(np.percentile(vals, 25)),
        "p50": float(np.percentile(vals, 50)),
        "p75": float(np.percentile(vals, 75)),
    }


def quantile(values, q, default=0.0):
    vals = np.asarray([finite(v, float("nan")) for v in values], dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return float(default)
    return float(np.percentile(vals, q * 100.0))


def norm01(value, scale):
    scale = finite(scale)
    if scale <= 1e-12:
        return 0.0
    return max(0.0, min(1.0, finite(value) / scale))


def phase_anti(phase_a, phase_b):
    diff = abs((finite(phase_a) - finite(phase_b)) % 1.0)
    diff = min(diff, 1.0 - diff)
    return 0.5 * (1.0 - math.cos(2.0 * math.pi * diff))


def phase_sync(phase_a, phase_b):
    diff = abs((finite(phase_a) - finite(phase_b)) % 1.0)
    diff = min(diff, 1.0 - diff)
    return 0.5 * (1.0 + math.cos(2.0 * math.pi * diff))


def universal_triangle_features(state, spec):
    """Single-signal triangle location from current rung topography only."""
    rungs = list(state.get("rungs", []))
    if not rungs:
        return {
            "triangle_pull": 0.0,
            "third_corner": 0.0,
            "pair_edge": 0.0,
            "pair_distance": 1.0,
            "donor_occupancy": 0.0,
            "faster_occupancy": 0.0,
            "home_occupancy": 0.0,
            "center_position_offset": 0.0,
            "center_ara": finite(state.get("center_ara", 1.0), 1.0),
            "phi_distance": abs(finite(state.get("center_ara", 1.0), 1.0) - PHI),
        }

    base = finite(getattr(spec, "base", 2.0), 2.0)
    home_position = finite(state.get("home_position", state.get("center_position", 0.0)))
    center_position = finite(state.get("center_position", home_position))
    center_ara = finite(state.get("center_ara", 1.0), 1.0)

    donor = 0.0
    faster = 0.0
    home = 0.0
    donor_distance = 0.0
    faster_distance = 0.0
    release_occ = 0.0
    accumulate_occ = 0.0

    for rung in rungs:
        occ = finite(rung.get("occupancy", 0.0))
        pos = finite(rung.get("position", 0.0))
        dist = pos - home_position
        if dist > 0.25:
            donor += occ
            donor_distance += occ * dist
        elif dist < -0.25:
            faster += occ
            faster_distance += occ * abs(dist)
        else:
            home += occ
        if finite(rung.get("is_release", 0.0)) > 0.5:
            release_occ += occ
        else:
            accumulate_occ += occ

    donor_distance = donor_distance / max(donor, 1e-12)
    faster_distance = faster_distance / max(faster, 1e-12)

    anti_energy = 0.0
    sync_energy = 0.0
    contact_energy = 0.0
    for i, left in enumerate(rungs):
        for right in rungs[i + 1 :]:
            left_occ = finite(left.get("occupancy", 0.0))
            right_occ = finite(right.get("occupancy", 0.0))
            if left_occ <= 0.0 or right_occ <= 0.0:
                continue
            position_gap = abs(finite(left.get("position", 0.0)) - finite(right.get("position", 0.0)))
            scale_gate = base ** (-position_gap)
            occ_gate = math.sqrt(left_occ * right_occ)
            anti = phase_anti(left.get("phase", 0.0), right.get("phase", 0.0))
            sync = phase_sync(left.get("phase", 0.0), right.get("phase", 0.0))
            release_split = 1.0 if finite(left.get("is_release", 0.0)) != finite(right.get("is_release", 0.0)) else 0.5
            contact = occ_gate * scale_gate
            anti_energy += contact * anti * release_split
            sync_energy += contact * sync
            contact_energy += contact

    pair_edge_raw = anti_energy + 0.5 * contact_energy
    donor_drive_raw = donor * (1.0 + donor_distance) * (0.5 + 0.5 * max(0.0, min(1.0, center_ara / 2.0)))
    faster_anchor_raw = faster * (1.0 + faster_distance)
    current_offset_raw = max(0.0, center_position - home_position)

    total = pair_edge_raw + donor_drive_raw + faster_anchor_raw + home + 1e-12
    pair_coord = pair_edge_raw / total
    third_coord = donor_drive_raw / total
    fast_coord = faster_anchor_raw / total

    triangle_pull = third_coord * (1.0 - pair_coord)
    pair_distance = 1.0 - min(1.0, pair_coord * 3.0)
    release_imbalance = abs(release_occ - accumulate_occ)

    return {
        "triangle_pull": float(triangle_pull),
        "third_corner": float(third_coord),
        "pair_edge": float(pair_coord),
        "pair_distance": float(pair_distance),
        "fast_corner": float(fast_coord),
        "donor_occupancy": float(donor),
        "faster_occupancy": float(faster),
        "home_occupancy": float(home),
        "donor_distance": float(donor_distance),
        "faster_distance": float(faster_distance),
        "anti_phase_edge": float(anti_energy),
        "sync_edge": float(sync_energy),
        "contact_edge": float(contact_energy),
        "release_imbalance": float(release_imbalance),
        "center_position_offset": float(current_offset_raw),
        "center_ara": float(center_ara),
        "phi_distance": float(abs(center_ara - PHI)),
        "pi_leak_energy": float(PI_LEAK_ENERGY),
    }


def add_triangle_breath_features(feature_cache, spec):
    """Add causal oscillator features from the triangle-pull trace itself."""
    anchors = sorted(feature_cache)
    pulls = []
    period_samples = max(8, int(round(float(spec.home_period) / max(1.0, float(spec.anchor_stride)))))
    window = max(8, 2 * period_samples)
    for idx, anchor in enumerate(anchors):
        pull = finite(feature_cache[anchor].get("triangle_pull", 0.0))
        pulls.append(pull)
        hist = np.asarray(pulls[max(0, idx + 1 - window) : idx + 1], dtype=float)
        mean = float(np.mean(hist)) if len(hist) else pull
        std = float(np.std(hist)) if len(hist) > 2 else 0.0
        if std < 1e-9:
            std = 1.0
        prev = pulls[idx - 1] if idx > 0 else pull
        prev3 = pulls[max(0, idx - 3)]
        position_z = (pull - mean) / std
        velocity_z = (pull - prev) / std
        slow_velocity_z = (pull - prev3) / (std * max(1, idx - max(0, idx - 3)))
        breath_energy = math.sqrt(position_z * position_z + velocity_z * velocity_z)
        phase = (math.atan2(velocity_z, position_z) / (2.0 * math.pi)) % 1.0
        expansion_gate = 0.5 + 0.5 * math.tanh(velocity_z)
        slow_expansion_gate = 0.5 + 0.5 * math.tanh(slow_velocity_z)
        circular_gate = 0.5 + 0.5 * math.sin(2.0 * math.pi * phase)
        feature_cache[anchor].update(
            {
                "breath_period_samples": float(period_samples),
                "breath_position_z": float(position_z),
                "breath_velocity_z": float(velocity_z),
                "breath_slow_velocity_z": float(slow_velocity_z),
                "breath_energy": float(breath_energy),
                "breath_phase": float(phase),
                "breath_expansion_gate": float(expansion_gate),
                "breath_slow_expansion_gate": float(slow_expansion_gate),
                "breath_circular_gate": float(circular_gate),
                "breath_pull": float(pull * expansion_gate),
                "breath_slow_pull": float(pull * slow_expansion_gate),
                "breath_signed_pull": float(pull * math.tanh(velocity_z)),
                "breath_contracting_pull": float(pull * (1.0 - expansion_gate)),
            }
        )


def static_only_features(features):
    return {
        key: value
        for key, value in features.items()
        if not key.startswith("breath_")
    }


def point_by_key(points):
    return {f"{p['origin']}|{p['date']}": p for p in points}


def make_point(origin, date, pred, actual, persistence, extras=None):
    out = {
        "origin": origin,
        "date": date,
        "pred": float(pred),
        "actual": float(actual),
        "persistence": float(persistence),
    }
    if extras:
        out.update(extras)
    return out


def run_dataset(spec, fit_dataset):
    label_to_anchor = {label_for(spec.dates, idx): idx for idx in range(1, len(spec.dates) + 1)}
    base_points = fit_dataset["points"]["learned_bk_phi_distance_decoder"]

    n = len(spec.values)
    max_h = max(spec.horizons)
    max_period = max(float(spec.base**k) for k in spec.rungs_k)
    min_anchor = max(int(math.ceil(4.0 * max_period)), int(4 * max(spec.rungs_k)), 48)
    test_start = max(
        spec.start_index_floor,
        min_anchor + spec.min_train + max_h + 1,
    )
    base_anchors = list(range(min_anchor, n - max_h + 1, spec.anchor_stride))

    scored_origins = set()
    for h in spec.horizons:
        for point in base_points.get(str(h), []):
            anchor = label_to_anchor.get(point["origin"])
            if anchor is not None:
                scored_origins.add(anchor)

    unique_origins = set(base_anchors) | scored_origins

    print(
        f"\n{spec.name}: building {len(unique_origins)} causal topography states "
        f"(test start {label_for(spec.dates, test_start)})",
        flush=True,
    )
    state_cache = {}
    feature_cache = {}
    t0 = time.time()
    for i, anchor in enumerate(sorted(unique_origins), start=1):
        state = read_signal_state(spec.values, anchor, spec)
        state_cache[anchor] = state
        feature_cache[anchor] = universal_triangle_features(state, spec)
        if i % 100 == 0:
            print(f"  states {i:4d}/{len(unique_origins)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  states {len(unique_origins):4d}/{len(unique_origins)} in {time.time() - t0:.1f}s", flush=True)
    add_triangle_breath_features(feature_cache, spec)

    historical_rows = {h: {} for h in spec.horizons}
    for h in spec.horizons:
        for anchor in base_anchors:
            if anchor + h > n or anchor not in feature_cache:
                continue
            actual = float(spec.values[anchor + h - 1])
            persistence = float(spec.values[anchor - 1])
            actual_delta = actual - persistence
            features = dict(static_only_features(feature_cache[anchor]))
            breath_features = dict(feature_cache[anchor])
            common_updates = {
                "origin_anchor": float(anchor),
                "horizon": float(h),
                "recent_delta_1": float(spec.values[anchor - 1] - spec.values[max(0, anchor - 2)]),
                "recent_delta_3": float(spec.values[anchor - 1] - spec.values[max(0, anchor - 4)]),
                "recent_abs_delta_1": abs(float(spec.values[anchor - 1] - spec.values[max(0, anchor - 2)])),
                "recent_abs_delta_3": abs(float(spec.values[anchor - 1] - spec.values[max(0, anchor - 4)])),
            }
            features.update(common_updates)
            breath_features.update(common_updates)
            historical_rows[h][anchor] = {
                "origin_anchor": anchor,
                "actual_abs_delta": abs(actual_delta),
                "features": features,
                "breath_features": breath_features,
            }

    scores = {model: {} for model in BASE_MODELS}
    scores["triangle_abs_ridge_with_learned_direction"] = {}
    scores["triangle_gate_learned_bk"] = {}
    scores["triangle_gate_fixed_pi"] = {}
    scores["triangle_breath_abs_ridge_with_learned_direction"] = {}
    scores["triangle_breath_gate_learned_bk"] = {}
    diagnostics = {}
    points_out = {model: {str(h): [] for h in spec.horizons} for model in scores}
    feature_rows = {str(h): [] for h in spec.horizons}

    for h in spec.horizons:
        h_key = str(h)
        learned = fit_dataset["points"]["learned_bk_phi_distance_decoder"].get(h_key, [])
        fixed_pi = fit_dataset["points"]["fixed_1_plus_pi_leak_phi_distance_decoder"].get(h_key, [])
        lag = fit_dataset["points"]["lag_ridge"].get(h_key, [])
        fixed_map = point_by_key(fixed_pi)
        lag_map = point_by_key(lag)

        rows = []
        for p in learned:
            origin_anchor = label_to_anchor.get(p["origin"])
            if origin_anchor is None or origin_anchor not in feature_cache:
                continue
            key = f"{p['origin']}|{p['date']}"
            fp = fixed_map.get(key)
            lp = lag_map.get(key)
            if fp is None or lp is None:
                continue
            actual = finite(p["actual"])
            persistence = finite(p["persistence"])
            learned_delta = finite(p["pred"]) - persistence
            fixed_delta = finite(fp["pred"]) - persistence
            lag_delta = finite(lp["pred"]) - persistence
            actual_delta = actual - persistence
            features = dict(static_only_features(feature_cache[origin_anchor]))
            breath_features = dict(feature_cache[origin_anchor])
            current_updates = {
                "learned_abs_delta": abs(learned_delta),
                "fixed_pi_abs_delta": abs(fixed_delta),
                "lag_abs_delta": abs(lag_delta),
                "learned_delta_sign": math.copysign(1.0, learned_delta) if abs(learned_delta) > 1e-12 else 0.0,
                "fixed_pi_delta_sign": math.copysign(1.0, fixed_delta) if abs(fixed_delta) > 1e-12 else 0.0,
                "origin_anchor": float(origin_anchor),
                "horizon": float(h),
            }
            features.update(current_updates)
            breath_features.update(current_updates)
            rows.append(
                {
                    "origin_anchor": origin_anchor,
                    "origin": p["origin"],
                    "date": p["date"],
                    "actual": actual,
                    "persistence": persistence,
                    "actual_delta": actual_delta,
                    "actual_abs_delta": abs(actual_delta),
                    "learned_pred": finite(p["pred"]),
                    "learned_delta": learned_delta,
                    "fixed_pi_pred": finite(fp["pred"]),
                    "fixed_pi_delta": fixed_delta,
                    "lag_pred": finite(lp["pred"]),
                    "lag_delta": lag_delta,
                    "features": features,
                    "breath_features": breath_features,
                }
            )

        if not rows:
            continue

        abs_values = [r["actual_abs_delta"] for r in rows]
        pull_values = [r["features"]["triangle_pull"] for r in rows]
        breath_pull_values = [r["breath_features"]["breath_pull"] for r in rows]
        expansion_values = [r["breath_features"]["breath_expansion_gate"] for r in rows]
        third_values = [r["features"]["third_corner"] for r in rows]
        pair_values = [r["features"]["pair_edge"] for r in rows]
        residual_values = [
            r["actual_abs_delta"] / (abs(r["learned_delta"]) + 1e-9)
            for r in rows
            if abs(r["learned_delta"]) > 1e-9
        ]
        lo = quantile(pull_values, 0.25)
        hi = quantile(pull_values, 0.75)
        low = [r for r in rows if r["features"]["triangle_pull"] <= lo]
        high = [r for r in rows if r["features"]["triangle_pull"] >= hi]
        low_abs = float(np.mean([r["actual_abs_delta"] for r in low])) if low else 0.0
        high_abs = float(np.mean([r["actual_abs_delta"] for r in high])) if high else 0.0
        blo = quantile(breath_pull_values, 0.25)
        bhi = quantile(breath_pull_values, 0.75)
        blow = [r for r in rows if r["breath_features"]["breath_pull"] <= blo]
        bhigh = [r for r in rows if r["breath_features"]["breath_pull"] >= bhi]
        blow_abs = float(np.mean([r["actual_abs_delta"] for r in blow])) if blow else 0.0
        bhigh_abs = float(np.mean([r["actual_abs_delta"] for r in bhigh])) if bhigh else 0.0

        diagnostics[h_key] = {
            "n": int(len(rows)),
            "corr_triangle_pull_abs_delta": corr(pull_values, abs_values),
            "corr_breath_pull_abs_delta": corr(breath_pull_values, abs_values),
            "corr_breath_expansion_abs_delta": corr(expansion_values, abs_values),
            "corr_third_corner_abs_delta": corr(third_values, abs_values),
            "corr_pair_edge_abs_delta": corr(pair_values, abs_values),
            "corr_triangle_pull_learned_abs_ratio": corr(
                [r["features"]["triangle_pull"] for r in rows if abs(r["learned_delta"]) > 1e-9],
                residual_values,
            ),
            "low_pull_abs_delta": low_abs,
            "high_pull_abs_delta": high_abs,
            "high_low_abs_delta_ratio": float(high_abs / low_abs) if low_abs > 1e-12 else 0.0,
            "low_breath_abs_delta": blow_abs,
            "high_breath_abs_delta": bhigh_abs,
            "high_low_breath_abs_delta_ratio": float(bhigh_abs / blow_abs) if blow_abs > 1e-12 else 0.0,
            "triangle_pull": summarize(pull_values),
            "breath_pull": summarize(breath_pull_values),
            "breath_expansion_gate": summarize(expansion_values),
            "third_corner": summarize(third_values),
            "pair_edge": summarize(pair_values),
        }

        for row in rows:
            extras = {
                "triangle_pull": row["features"]["triangle_pull"],
                "third_corner": row["features"]["third_corner"],
                "pair_edge": row["features"]["pair_edge"],
                "pair_distance": row["features"]["pair_distance"],
                "donor_occupancy": row["features"]["donor_occupancy"],
                "anti_phase_edge": row["features"]["anti_phase_edge"],
                "contact_edge": row["features"]["contact_edge"],
                "breath_pull": row["breath_features"]["breath_pull"],
                "breath_phase": row["breath_features"]["breath_phase"],
                "breath_expansion_gate": row["breath_features"]["breath_expansion_gate"],
                "breath_energy": row["breath_features"]["breath_energy"],
            }
            points_out["learned_bk_phi_distance_decoder"][h_key].append(
                make_point(row["origin"], row["date"], row["learned_pred"], row["actual"], row["persistence"], extras)
            )
            points_out["fixed_1_plus_pi_leak_phi_distance_decoder"][h_key].append(
                make_point(row["origin"], row["date"], row["fixed_pi_pred"], row["actual"], row["persistence"], extras)
            )
            points_out["lag_ridge"][h_key].append(
                make_point(row["origin"], row["date"], row["lag_pred"], row["actual"], row["persistence"], extras)
            )
            feature_rows[h_key].append(
                {
                    "origin": row["origin"],
                    "date": row["date"],
                    "actual_abs_delta": row["actual_abs_delta"],
                    **extras,
                }
            )

        for row in rows:
            train = [
                r
                for anchor, r in historical_rows[h].items()
                if anchor + h < row["origin_anchor"]
            ]
            if len(train) < spec.min_train:
                continue

            train_features = [r["features"] for r in train]
            train_breath_features = [r["breath_features"] for r in train]
            train_abs = [r["actual_abs_delta"] for r in train]

            abs_pred, _, _ = fit_predict_ridge(train_features, train_abs, row["features"])
            abs_pred = max(0.0, finite(abs_pred))
            breath_abs_pred, _, _ = fit_predict_ridge(train_breath_features, train_abs, row["breath_features"])
            breath_abs_pred = max(0.0, finite(breath_abs_pred))
            learned_sign = math.copysign(1.0, row["learned_delta"]) if abs(row["learned_delta"]) > 1e-12 else 0.0
            abs_ridge_pred = row["persistence"] + learned_sign * abs_pred
            breath_abs_ridge_pred = row["persistence"] + learned_sign * breath_abs_pred
            abs_common = {
                "triangle_pull": row["features"]["triangle_pull"],
                "third_corner": row["features"]["third_corner"],
                "pair_edge": row["features"]["pair_edge"],
                "abs_pred": abs_pred,
                "breath_pull": row["breath_features"]["breath_pull"],
                "breath_phase": row["breath_features"]["breath_phase"],
                "breath_expansion_gate": row["breath_features"]["breath_expansion_gate"],
                "breath_abs_pred": breath_abs_pred,
            }
            points_out["triangle_abs_ridge_with_learned_direction"][h_key].append(
                make_point(row["origin"], row["date"], abs_ridge_pred, row["actual"], row["persistence"], abs_common)
            )
            points_out["triangle_breath_abs_ridge_with_learned_direction"][h_key].append(
                make_point(row["origin"], row["date"], breath_abs_ridge_pred, row["actual"], row["persistence"], abs_common)
            )

            gate_train = [r for r in rows if r["origin_anchor"] + h < row["origin_anchor"]]
            min_gate_train = max(8, min(24, len(rows) // 4))
            if len(gate_train) < min_gate_train:
                continue

            eps = np.percentile([abs(r["learned_delta"]) for r in gate_train], 25) * 0.25 + 1e-9
            train_gate_learned = [
                max(0.0, min(3.0, r["actual_abs_delta"] / (abs(r["learned_delta"]) + eps)))
                for r in gate_train
            ]
            gate_features = [r["features"] for r in gate_train]
            gate_breath_features = [r["breath_features"] for r in gate_train]
            gate_learned, _, _ = fit_predict_ridge(gate_features, train_gate_learned, row["features"])
            gate_learned = max(0.0, min(3.0, finite(gate_learned, 1.0)))
            gate_learned_pred = row["persistence"] + row["learned_delta"] * gate_learned
            breath_gate_learned, _, _ = fit_predict_ridge(
                gate_breath_features,
                train_gate_learned,
                row["breath_features"],
            )
            breath_gate_learned = max(0.0, min(3.0, finite(breath_gate_learned, 1.0)))
            breath_gate_learned_pred = row["persistence"] + row["learned_delta"] * breath_gate_learned

            eps_fixed = np.percentile([abs(r["fixed_pi_delta"]) for r in gate_train], 25) * 0.25 + 1e-9
            train_gate_fixed = [
                max(0.0, min(3.0, r["actual_abs_delta"] / (abs(r["fixed_pi_delta"]) + eps_fixed)))
                for r in gate_train
            ]
            gate_fixed, _, _ = fit_predict_ridge(gate_features, train_gate_fixed, row["features"])
            gate_fixed = max(0.0, min(3.0, finite(gate_fixed, 1.0)))
            gate_fixed_pred = row["persistence"] + row["fixed_pi_delta"] * gate_fixed

            common = {
                "triangle_pull": row["features"]["triangle_pull"],
                "third_corner": row["features"]["third_corner"],
                "pair_edge": row["features"]["pair_edge"],
                "abs_pred": abs_pred,
                "gate_learned": gate_learned,
                "gate_fixed_pi": gate_fixed,
                "breath_pull": row["breath_features"]["breath_pull"],
                "breath_phase": row["breath_features"]["breath_phase"],
                "breath_expansion_gate": row["breath_features"]["breath_expansion_gate"],
                "breath_gate_learned": breath_gate_learned,
            }
            points_out["triangle_gate_learned_bk"][h_key].append(
                make_point(row["origin"], row["date"], gate_learned_pred, row["actual"], row["persistence"], common)
            )
            points_out["triangle_breath_gate_learned_bk"][h_key].append(
                make_point(row["origin"], row["date"], breath_gate_learned_pred, row["actual"], row["persistence"], common)
            )
            points_out["triangle_gate_fixed_pi"][h_key].append(
                make_point(row["origin"], row["date"], gate_fixed_pred, row["actual"], row["persistence"], common)
            )

        for model in scores:
            scores[model][h_key] = score_points(points_out[model][h_key])

        print(f"  h={h:>4}: pull corr={diagnostics[h_key]['corr_triangle_pull_abs_delta']:+.3f} "
              f"breath corr={diagnostics[h_key]['corr_breath_pull_abs_delta']:+.3f} "
              f"high/low={diagnostics[h_key]['high_low_abs_delta_ratio']:.2f} "
              f"gateLearned={scores['triangle_gate_learned_bk'][h_key].get('mae', float('nan')):.4f} "
              f"breathGate={scores['triangle_breath_gate_learned_bk'][h_key].get('mae', float('nan')):.4f} "
              f"baseLearned={scores['learned_bk_phi_distance_decoder'][h_key].get('mae', float('nan')):.4f}",
              flush=True)

    return {
        "config": {
            "name": spec.name,
            "unit": spec.unit,
            "home_period": spec.home_period,
            "base": spec.base,
            "rungs_k": spec.rungs_k,
            "horizons": spec.horizons,
            "min_train": spec.min_train,
        },
        "diagnostics": diagnostics,
        "scores": scores,
        "feature_rows": feature_rows,
        "points": points_out,
    }


def run(out_path=HERE / "ara_triangle_amplitude_gate_data.js"):
    started = time.time()
    fit_data = load_js_data(HERE / "ara_phi_distance_bk_fit_data.js")
    datasets = {}
    for spec in [load_enso(), load_solar(), load_ecg_rr()]:
        datasets[spec.name] = run_dataset(spec, fit_data["datasets"][spec.name])

    out = {
        "date": "2026-05-23",
        "method": "strict-causal universal topography triangle amplitude gate",
        "hypothesis": "future movement amplitude grows when the current state is farther from the coupled edge and closer to the slower/third-corner donor region",
        "leakage_guard": "state features use only origin-time causal geometry; amplitude/gate fits use only completed windows s+h<t",
        "base_models": BASE_MODELS,
        "derived_models": {
            "triangle_abs_ridge_with_learned_direction": "Causal ridge predicts |future delta| from triangle topography; direction is inherited from learned B+k decoder.",
            "triangle_gate_learned_bk": "Causal ridge predicts an amplitude multiplier for learned B+k delta.",
            "triangle_gate_fixed_pi": "Causal ridge predicts an amplitude multiplier for fixed 1+pi-leak+phi-distance delta.",
            "triangle_breath_abs_ridge_with_learned_direction": "Causal ridge predicts |future delta| from triangle topography plus the triangle-pull breath oscillator; direction is inherited from learned B+k decoder.",
            "triangle_breath_gate_learned_bk": "Causal ridge predicts an amplitude multiplier for learned B+k delta using triangle topography plus breath phase/velocity.",
        },
        "datasets": datasets,
        "elapsed_seconds": time.time() - started,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("window.ARA_TRIANGLE_AMPLITUDE_GATE = ")
        json.dump(clean_for_json(out), f, indent=2)
        f.write(";\n")

    print("\nSummary", flush=True)
    print("-" * 100, flush=True)
    for name, data in datasets.items():
        print(name, flush=True)
        for h in data["config"]["horizons"]:
            h_key = str(h)
            diag = data["diagnostics"].get(h_key, {})
            learned = data["scores"]["learned_bk_phi_distance_decoder"].get(h_key, {})
            gate = data["scores"]["triangle_gate_learned_bk"].get(h_key, {})
            breath_gate = data["scores"]["triangle_breath_gate_learned_bk"].get(h_key, {})
            abs_ridge = data["scores"]["triangle_abs_ridge_with_learned_direction"].get(h_key, {})
            breath_abs = data["scores"]["triangle_breath_abs_ridge_with_learned_direction"].get(h_key, {})
            print(
                f"  h={h:>4}: corr(pull,|delta|)={diag.get('corr_triangle_pull_abs_delta', 0.0):+.3f} "
                f"corr(breath,|delta|)={diag.get('corr_breath_pull_abs_delta', 0.0):+.3f} "
                f"high/low={diag.get('high_low_abs_delta_ratio', 0.0):.2f} "
                f"learned MAE={learned.get('mae', float('nan')):.4f} "
                f"gate MAE={gate.get('mae', float('nan')):.4f} "
                f"breath-gate MAE={breath_gate.get('mae', float('nan')):.4f} "
                f"abs-ridge MAE={abs_ridge.get('mae', float('nan')):.4f} "
                f"breath-abs MAE={breath_abs.get('mae', float('nan')):.4f}",
                flush=True,
            )

    print(f"\nWrote {out_path}", flush=True)
    print(f"Done in {time.time() - started:.1f}s", flush=True)


if __name__ == "__main__":
    run()
