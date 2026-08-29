#!/usr/bin/env python3
"""T423 nested temporal-architecture test for a candidate parent Di-ARA."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
MUON = HERE.parent
T421 = MUON / "T421_child_singularity_parent_ridge"
PROTOCOL = HERE / "T423_FROZEN_PROTOCOL.md"
RESULTS = HERE / "results"
FREEZE = HERE / "T423_DEVELOPMENT_FREEZE.json"

SEED = 423
RIDGE_PENALTY = 1e-3
BOOTSTRAPS = 10000
SHIFT_DRAWS = 1000
EPS = 1e-12
STAGES = ("development", "validation", "holdout")

BASE_FEATURES = (
    "U", "R", "dU", "dR", "elapsed_us", "parent_lifespan_ARA",
    "field_turn_log2", "rf_flag", "direction_code",
)
M1_FEATURES = BASE_FEATURES + ("H", "dH", "H_distance")
M2_FEATURES = M1_FEATURES + ("Q", "dQ", "Q_distance")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], header: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        fields: list[str] = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
    elif header:
        fields = header
    else:
        raise ValueError(f"empty CSV requires a header: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def clean(value):
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stage_source(stage: str) -> Path:
    return T421 / "results" / f"T421_{stage.upper()}_TIMELINE.csv"


def group_rows(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        groups.setdefault((str(row["run"]), str(row["period"])), []).append(row)
    for key in groups:
        groups[key].sort(key=lambda item: float(item["time_us"]))
    return groups


def array(rows: list[dict], key: str) -> np.ndarray:
    return np.asarray([float(row[key]) for row in rows], dtype=float)


def at(values: np.ndarray, position: float) -> float:
    if position < 0 or position > len(values) - 1:
        return float("nan")
    left = int(math.floor(position))
    right = min(left + 1, len(values) - 1)
    fraction = position - left
    return float(values[left] + fraction * (values[right] - values[left]))


def crossings(values_a: np.ndarray, values_b: np.ndarray) -> list[dict]:
    difference = values_a - values_b
    found: list[dict] = []
    for index in range(1, len(difference)):
        left, right = float(difference[index - 1]), float(difference[index])
        if left == 0.0:
            fraction = 0.0
        elif right == 0.0:
            fraction = 1.0
        elif left * right > 0.0:
            continue
        else:
            fraction = -left / (right - left)
        if not 0.0 <= fraction <= 1.0:
            continue
        position = index - 1 + fraction
        direction_code = 1 if left < right else -1
        if found and abs(position - float(found[-1]["position"])) < 1e-9:
            continue
        found.append({
            "position": float(position),
            "direction_code": int(direction_code),
            "direction": "R_to_U" if direction_code > 0 else "U_to_R",
            "coordinate": at(values_a, position),
        })
    return found


def child_intervals(rows: list[dict]) -> list[dict]:
    u, r, time = array(rows, "openness_U"), array(rows, "closure_R"), array(rows, "time_us")
    child = crossings(u, r)
    intervals: list[dict] = []
    for index in range(len(child) - 1):
        start, end = child[index], child[index + 1]
        if int(start["direction_code"]) == int(end["direction_code"]):
            continue
        start_position, end_position = float(start["position"]), float(end["position"])
        start_time, end_time = at(time, start_position), at(time, end_position)
        if end_time <= start_time:
            continue
        first = rows[0]
        intervals.append({
            "split": first["split"], "run": first["run"], "period": first["period"],
            "rf_flag": int(float(first["rf_flag"])), "temperature_K": float(first["temperature_K"]),
            "field_G": float(first["field_G"]), "frequency_MHz": float(first["frequency_MHz"]),
            "field_turn_log2": float(first["field_turn_log2"]),
            "interval_index": index,
            "interval_id": f"{first['run']}|{first['period']}|{index}",
            "start_position": start_position, "end_position": end_position,
            "start_time_us": start_time, "end_time_us": end_time,
            "duration_us": end_time - start_time,
            "start_direction_code": int(start["direction_code"]),
            "start_direction": start["direction"], "end_direction": end["direction"],
            "start_coordinate": float(start["coordinate"]), "end_coordinate": float(end["coordinate"]),
            "has_return_C1": int(index + 2 < len(child) and int(child[index + 2]["direction_code"]) == int(start["direction_code"])),
        })
    return intervals


def stable_shift(interval_id: str, length: int) -> int:
    if length <= 2:
        return 1
    raw = int(hashlib.sha256(interval_id.encode("utf-8")).hexdigest()[:8], 16)
    return 1 + raw % (length - 1)


def prediction_rows_for_group(rows: list[dict], intervals: list[dict]) -> list[dict]:
    time = array(rows, "time_us")
    u, r = array(rows, "openness_U"), array(rows, "closure_R")
    h, q = array(rows, "parent_H"), array(rows, "signed_parent_Q")
    wrong_h, wrong_q = array(rows, "wrong_parent_H"), array(rows, "wrong_signed_Q")
    parent = array(rows, "parent_lifespan_ARA")
    output: list[dict] = []
    for interval in intervals:
        start = int(math.ceil(float(interval["start_position"])))
        stop = int(math.floor(float(interval["end_position"])))
        indices = np.arange(start, stop + 1, dtype=int)
        if len(indices) < 2:
            continue
        ph, pq = h[indices], q[indices]
        shift = stable_shift(str(interval["interval_id"]), len(indices))
        variants = {
            "H_reverse": ph[::-1], "Q_reverse": pq[::-1],
            "H_shift": np.roll(ph, shift), "Q_shift": np.roll(pq, shift),
        }
        for local_index, index in enumerate(indices):
            if index <= 0 or float(time[index]) >= float(interval["end_time_us"]):
                continue
            record = {
                **interval,
                "sample_index": int(index), "time_us": float(time[index]),
                "elapsed_us": float(time[index]) - float(interval["start_time_us"]),
                "remaining_us": float(interval["end_time_us"]) - float(time[index]),
                "parent_lifespan_ARA": float(parent[index]),
                "U": float(u[index]), "R": float(r[index]),
                "dU": float(u[index] - u[index - 1]), "dR": float(r[index] - r[index - 1]),
                "H": float(h[index]), "Q": float(q[index]),
                "dH": float(h[index] - h[index - 1]), "dQ": float(q[index] - q[index - 1]),
                "H_distance": abs(float(h[index]) - 1.0), "Q_distance": abs(float(q[index]) - 1.0),
                "wrong_H": float(wrong_h[index]), "wrong_Q": float(wrong_q[index]),
                "wrong_dH": float(wrong_h[index] - wrong_h[index - 1]),
                "wrong_dQ": float(wrong_q[index] - wrong_q[index - 1]),
                "wrong_H_distance": abs(float(wrong_h[index]) - 1.0),
                "wrong_Q_distance": abs(float(wrong_q[index]) - 1.0),
                "direction_code": int(interval["start_direction_code"]),
                "parent_shift_reads": int(shift),
            }
            for prefix in ("reverse", "shift"):
                hh = float(variants[f"H_{prefix}"][local_index])
                qq = float(variants[f"Q_{prefix}"][local_index])
                if local_index == 0:
                    dh = dq = 0.0
                else:
                    dh = hh - float(variants[f"H_{prefix}"][local_index - 1])
                    dq = qq - float(variants[f"Q_{prefix}"][local_index - 1])
                record[f"{prefix}_H"] = hh
                record[f"{prefix}_Q"] = qq
                record[f"{prefix}_dH"] = dh
                record[f"{prefix}_dQ"] = dq
                record[f"{prefix}_H_distance"] = abs(hh - 1.0)
                record[f"{prefix}_Q_distance"] = abs(qq - 1.0)
            output.append(record)
    return output


def build_stage_rows(stage: str) -> tuple[list[dict], list[dict], dict[tuple[str, str], list[dict]]]:
    source = stage_source(stage)
    rows = read_csv(source)
    groups = group_rows(rows)
    intervals: list[dict] = []
    predictions: list[dict] = []
    for key, group in sorted(groups.items()):
        current = child_intervals(group)
        intervals.extend(current)
        predictions.extend(prediction_rows_for_group(group, current))
    return intervals, predictions, groups


def matrix(rows: list[dict], features: tuple[str, ...], source: str = "correct") -> np.ndarray:
    output = []
    for row in rows:
        values = []
        for feature in features:
            if source == "correct" or feature in BASE_FEATURES:
                key = feature
            elif feature in ("H", "dH", "H_distance", "Q", "dQ", "Q_distance"):
                key = f"{source}_{feature}"
            else:
                key = feature
            values.append(float(row[key]))
        output.append(values)
    return np.asarray(output, dtype=float)


def fit_ridge(rows: list[dict], features: tuple[str, ...]) -> dict:
    x = matrix(rows, features)
    y = np.asarray([float(row["remaining_us"]) for row in rows], dtype=float)
    x_mean, x_scale = np.mean(x, axis=0), np.std(x, axis=0)
    x_scale[x_scale < EPS] = 1.0
    z = (x - x_mean) / x_scale
    design = np.column_stack((np.ones(len(z)), z))
    penalty = np.eye(design.shape[1]) * RIDGE_PENALTY
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    return {
        "features": list(features), "x_mean": x_mean.tolist(), "x_scale": x_scale.tolist(),
        "beta": beta.tolist(), "ridge_penalty": RIDGE_PENALTY, "training_rows": len(rows),
    }


def predict(model: dict, rows: list[dict], source: str = "correct") -> np.ndarray:
    features = tuple(model["features"])
    x = matrix(rows, features, source=source)
    z = (x - np.asarray(model["x_mean"])) / np.asarray(model["x_scale"])
    design = np.column_stack((np.ones(len(z)), z))
    return np.maximum(0.0, design @ np.asarray(model["beta"]))


def score_predictions(stage: str, rows: list[dict], models: dict) -> tuple[list[dict], list[dict]]:
    if not rows:
        return [], []
    predictions = {
        "M0": predict(models["M0"], rows),
        "M1": predict(models["M1"], rows),
        "M2": predict(models["M2"], rows),
        "M2_wrong": predict(models["M2"], rows, "wrong"),
        "M2_reverse": predict(models["M2"], rows, "reverse"),
        "M2_shift": predict(models["M2"], rows, "shift"),
    }
    detailed: list[dict] = []
    for index, source in enumerate(rows):
        record = dict(source)
        for name, values in predictions.items():
            record[f"prediction_{name}"] = float(values[index])
            record[f"absolute_error_{name}"] = abs(float(values[index]) - float(source["remaining_us"]))
        detailed.append(record)
    grouped: dict[str, list[dict]] = {}
    for row in detailed:
        grouped.setdefault(str(row["interval_id"]), []).append(row)
    interval_scores: list[dict] = []
    for interval_id, members in sorted(grouped.items()):
        first = members[0]
        result = {
            "split": stage, "interval_id": interval_id, "run": first["run"], "period": first["period"],
            "rf_flag": int(first["rf_flag"]), "field_G": float(first["field_G"]),
            "direction": first["start_direction"], "duration_us": float(first["duration_us"]),
            "prediction_rows": len(members),
        }
        for name in predictions:
            result[f"mae_{name}"] = float(np.median([float(row[f"absolute_error_{name}"]) for row in members]))
        result["advantage_M0_over_M1"] = result["mae_M0"] - result["mae_M1"]
        result["advantage_M0_over_M2"] = result["mae_M0"] - result["mae_M2"]
        result["advantage_M1_over_M2"] = result["mae_M1"] - result["mae_M2"]
        result["advantage_wrong_over_M2"] = result["mae_M2_wrong"] - result["mae_M2"]
        result["advantage_reverse_over_M2"] = result["mae_M2_reverse"] - result["mae_M2"]
        result["advantage_shift_over_M2"] = result["mae_M2_shift"] - result["mae_M2"]
        interval_scores.append(result)
    return detailed, interval_scores


def segment_positions(start: float, end: float) -> np.ndarray:
    positions = [start]
    positions.extend(float(value) for value in range(int(math.ceil(start)), int(math.floor(end)) + 1) if start < value < end)
    positions.append(end)
    return np.asarray(sorted(set(positions)), dtype=float)


def parent_event_for_interval(rows: list[dict], interval: dict, h_values: np.ndarray | None = None, q_values: np.ndarray | None = None) -> dict:
    h = array(rows, "parent_H") if h_values is None else h_values
    q = array(rows, "signed_parent_Q") if q_values is None else q_values
    time = array(rows, "time_us")
    positions = segment_positions(float(interval["start_position"]), float(interval["end_position"]))
    q_segment = np.asarray([at(q, value) for value in positions])
    h_segment = np.asarray([at(h, value) for value in positions])
    time_segment = np.asarray([at(time, value) for value in positions])
    candidates: list[dict] = []
    for index in range(1, len(positions)):
        left, right = q_segment[index - 1] - 1.0, q_segment[index] - 1.0
        if left == 0.0:
            fraction = 0.0
        elif right == 0.0:
            fraction = 1.0
        elif left * right > 0.0:
            continue
        else:
            fraction = float(-left / (right - left))
        position = float(positions[index - 1] + fraction * (positions[index] - positions[index - 1]))
        q_direction = 1 if left < right else -1
        h_at = at(h, position)
        candidates.append({
            "parent_position": position, "parent_time_us": at(time, position),
            "parent_H": h_at, "parent_Q": at(q, position),
            "parent_H_distance": abs(h_at - 1.0), "q_direction_code": q_direction,
            "q_direction": "below_to_above" if q_direction > 0 else "above_to_below",
        })
    base = dict(interval)
    base["q_crossing_count"] = len(candidates)
    base["interval_H_distance"] = float(np.median(np.abs(h_segment - 1.0)))
    if not candidates:
        base.update({
            "parent_position": float("nan"), "parent_time_us": float("nan"),
            "parent_H": float("nan"), "parent_Q": float("nan"),
            "parent_H_distance": float("nan"), "q_direction_code": 0,
            "q_direction": "none", "relation_sign": 0,
            "parent_phase_fraction": float("nan"), "parent_ridge_exposure": float("nan"),
        })
        return base
    selected = min(candidates, key=lambda item: float(item["parent_H_distance"]))
    base.update(selected)
    base["relation_sign"] = int(selected["q_direction_code"]) * int(interval["start_direction_code"])
    base["parent_phase_fraction"] = (
        float(selected["parent_time_us"]) - float(interval["start_time_us"])
    ) / max(float(interval["duration_us"]), EPS)
    base["parent_ridge_exposure"] = base["interval_H_distance"] - float(selected["parent_H_distance"])
    return base


def parent_events(groups: dict[tuple[str, str], list[dict]], intervals: list[dict]) -> list[dict]:
    by_group: dict[tuple[str, str], list[dict]] = {}
    for interval in intervals:
        by_group.setdefault((str(interval["run"]), str(interval["period"])), []).append(interval)
    output: list[dict] = []
    for key, members in sorted(by_group.items()):
        rows = groups[key]
        for interval in members:
            output.append(parent_event_for_interval(rows, interval))
    return output


def freeze_orientation(events: list[dict]) -> int:
    signs = [int(row["relation_sign"]) for row in events if int(row["relation_sign"]) != 0]
    if not signs:
        return 1
    positive, negative = signs.count(1), signs.count(-1)
    return 1 if positive >= negative else -1


def decorate_expected(events: list[dict], orientation_sign: int) -> list[dict]:
    output = []
    for row in events:
        record = dict(row)
        record["frozen_orientation_sign"] = orientation_sign
        record["expected_orientation"] = int(int(row["relation_sign"]) == orientation_sign)
        record["opposite_orientation"] = int(int(row["relation_sign"]) == -orientation_sign)
        output.append(record)
    return output


def aggregate_by_field(rows: list[dict], key: str, period: str | None = None) -> tuple[float, dict[float, float]]:
    values: dict[float, list[float]] = {}
    for row in rows:
        if period is not None and str(row["period"]) != period:
            continue
        value = float(row[key])
        if math.isfinite(value):
            values.setdefault(float(row["field_G"]), []).append(value)
    field = {name: float(np.median(items)) for name, items in values.items()}
    return (float(np.median(list(field.values()))) if field else float("nan")), field


def field_bootstrap(rows: list[dict], key: str, seed: int, period: str | None = None) -> dict:
    estimate, field = aggregate_by_field(rows, key, period)
    values = np.asarray(list(field.values()), dtype=float)
    if len(values) == 0:
        return {"median": float("nan"), "ci95": [float("nan"), float("nan")], "field_count": 0}
    rng = np.random.default_rng(seed)
    boot = np.asarray([np.median(rng.choice(values, len(values), replace=True)) for _ in range(BOOTSTRAPS)])
    return {
        "median": estimate,
        "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
        "field_count": len(values),
    }


def order_shift_null(
    groups: dict[tuple[str, str], list[dict]], intervals: list[dict], orientation_sign: int, seed: int
) -> list[dict]:
    by_group: dict[tuple[str, str], list[dict]] = {}
    for interval in intervals:
        by_group.setdefault((str(interval["run"]), str(interval["period"])), []).append(interval)
    rng = np.random.default_rng(seed)
    output: list[dict] = []
    for draw in range(SHIFT_DRAWS):
        records: list[dict] = []
        for key, members in by_group.items():
            rows = groups[key]
            h, q = array(rows, "parent_H"), array(rows, "signed_parent_Q")
            if len(rows) <= 2:
                continue
            shift = int(rng.integers(1, len(rows)))
            shifted_h, shifted_q = np.roll(h, shift), np.roll(q, shift)
            for interval in members:
                records.append(parent_event_for_interval(rows, interval, shifted_h, shifted_q))
        decorated = decorate_expected(records, orientation_sign)
        total = len(decorated)
        expected_share = float(sum(int(row["expected_orientation"]) for row in decorated) / total) if total else float("nan")
        exposure, _ = aggregate_by_field(
            [row for row in decorated if int(row["expected_orientation"])], "parent_ridge_exposure"
        )
        output.append({"draw": draw, "expected_share": expected_share, "parent_ridge_exposure": exposure})
    return output


def empirical_upper_p(null: list[dict], key: str, observed: float) -> float:
    values = np.asarray([float(row[key]) for row in null if math.isfinite(float(row[key]))])
    if len(values) == 0 or not math.isfinite(observed):
        return float("nan")
    return float((1 + np.count_nonzero(values >= observed)) / (1 + len(values)))


def stage_summary(
    stage: str,
    intervals: list[dict],
    scores: list[dict],
    events: list[dict],
    shift_null: list[dict],
) -> dict:
    expected = [row for row in events if int(row["expected_orientation"])]
    total = len(intervals)
    expected_share = float(len(expected) / total) if total else float("nan")
    opposite_share = float(sum(int(row["opposite_orientation"]) for row in events) / total) if total else float("nan")
    q_available_share = float(sum(int(row["q_crossing_count"]) > 0 for row in events) / total) if total else float("nan")
    return_count = sum(int(row["has_return_C1"]) for row in intervals)
    adjacent = []
    by_group: dict[tuple[str, str], list[dict]] = {}
    for row in events:
        by_group.setdefault((str(row["run"]), str(row["period"])), []).append(row)
    for members in by_group.values():
        members.sort(key=lambda item: float(item["start_time_us"]))
        for left, right in zip(members[:-1], members[1:]):
            if int(left["q_direction_code"]) and int(right["q_direction_code"]):
                adjacent.append(int(left["q_direction_code"]) == -int(right["q_direction_code"]))
    effects = {
        "M0_over_M1": field_bootstrap(scores, "advantage_M0_over_M1", SEED + 10),
        "M0_over_M2": field_bootstrap(scores, "advantage_M0_over_M2", SEED + 20),
        "M1_over_M2": field_bootstrap(scores, "advantage_M1_over_M2", SEED + 30),
        "wrong_over_M2": field_bootstrap(scores, "advantage_wrong_over_M2", SEED + 40),
        "reverse_over_M2": field_bootstrap(scores, "advantage_reverse_over_M2", SEED + 50),
        "shift_over_M2": field_bootstrap(scores, "advantage_shift_over_M2", SEED + 60),
        "parent_ridge_exposure": field_bootstrap(expected, "parent_ridge_exposure", SEED + 70),
    }
    mae = {name: aggregate_by_field(scores, f"mae_{name}")[0] for name in ("M0", "M1", "M2", "M2_wrong", "M2_reverse", "M2_shift")}
    rf = {
        period: field_bootstrap(scores, "advantage_M1_over_M2", SEED + 80 + index, period)
        for index, period in enumerate(("RF on", "RF off"))
    }
    summary = {
        "stage": stage,
        "interval_count": total,
        "prediction_interval_count": len(scores),
        "prediction_row_count": sum(int(row["prediction_rows"]) for row in scores),
        "return_C1_count": return_count,
        "parent_q_available_share": q_available_share,
        "expected_orientation_share": expected_share,
        "opposite_orientation_share": opposite_share,
        "parent_q_alternation_share": float(np.mean(adjacent)) if adjacent else float("nan"),
        "field_balanced_mae_us": mae,
        "effects_us": effects,
        "RF_M1_over_M2": rf,
        "order_shift_null": {
            "expected_share_p": empirical_upper_p(shift_null, "expected_share", expected_share),
            "ridge_exposure_p": empirical_upper_p(shift_null, "parent_ridge_exposure", effects["parent_ridge_exposure"]["median"]),
            "draws": len(shift_null),
        },
    }
    return summary


def gates(summary: dict, holdout: bool = False) -> dict:
    effects = summary["effects_us"]
    ci = lambda name: effects[name]["ci95"]
    availability = summary["interval_count"] >= (10 if holdout else 20)
    output = {
        "G1_availability": {"pass": availability, "value": summary["interval_count"], "threshold": 10 if holdout else 20},
        "G2_M2_beats_M0": {"pass": bool(ci("M0_over_M2")[0] > 0), "effect": effects["M0_over_M2"]},
        "G3_M2_beats_M1": {"pass": bool(ci("M1_over_M2")[0] > 0), "effect": effects["M1_over_M2"]},
        "G5_parent_order": {
            "pass": bool(summary["expected_orientation_share"] >= 0.60 and summary["expected_orientation_share"] > summary["opposite_orientation_share"]),
            "expected_share": summary["expected_orientation_share"], "opposite_share": summary["opposite_orientation_share"],
        },
        "G6_parent_ridge_at_phase_crossing": {"pass": bool(ci("parent_ridge_exposure")[0] > 0), "effect": effects["parent_ridge_exposure"]},
        "G7_specificity": {
            "pass": bool(ci("wrong_over_M2")[0] > 0 and ci("reverse_over_M2")[0] > 0),
            "wrong": effects["wrong_over_M2"], "reverse": effects["reverse_over_M2"],
        },
        "G8_RF_robustness": {
            "pass": bool(all(summary["RF_M1_over_M2"][period]["median"] > 0 for period in ("RF on", "RF off"))),
            "effects": summary["RF_M1_over_M2"],
        },
    }
    return output


def status_from(validation: dict, validation_gates: dict, holdout: dict, holdout_gates: dict) -> str:
    all_validation = all(bool(item["pass"]) for item in validation_gates.values())
    g4 = bool(
        holdout_gates["G1_availability"]["pass"]
        and holdout["effects_us"]["M0_over_M2"]["median"] > 0
        and holdout["effects_us"]["M1_over_M2"]["median"] > 0
    )
    if all_validation and g4:
        return "SUPPORTED AS DECOMPRESSED PARENT DI-ARA"
    compressed = bool(
        validation_gates["G1_availability"]["pass"]
        and validation["effects_us"]["M0_over_M1"]["median"] > 0
        and holdout_gates["G1_availability"]["pass"]
        and holdout["effects_us"]["M0_over_M1"]["median"] > 0
    )
    if compressed and not validation_gates["G3_M2_beats_M1"]["pass"]:
        return "SUPPORTED AS COMPRESSED PARENT ONLY"
    if validation["effects_us"]["M0_over_M1"]["median"] <= 0 and validation["effects_us"]["M0_over_M2"]["median"] <= 0:
        return "CHILD-ONLY ARCHITECTURE RETAINED"
    reverse = bool(
        validation["expected_orientation_share"] < validation["opposite_orientation_share"]
        or validation["effects_us"]["wrong_over_M2"]["ci95"][1] < 0
        or validation["effects_us"]["reverse_over_M2"]["ci95"][1] < 0
    )
    return "NOT SUPPORTED" if reverse else "SUGGESTIVE / INCONCLUSIVE"


def run_development() -> dict:
    intervals, rows, groups = build_stage_rows("development")
    if not rows:
        raise RuntimeError("development has no causal prediction rows")
    models = {
        "M0": fit_ridge(rows, BASE_FEATURES),
        "M1": fit_ridge(rows, M1_FEATURES),
        "M2": fit_ridge(rows, M2_FEATURES),
    }
    events_raw = parent_events(groups, intervals)
    orientation_sign = freeze_orientation(events_raw)
    events = decorate_expected(events_raw, orientation_sign)
    detailed, scores = score_predictions("development", rows, models)
    shift_null = order_shift_null(groups, intervals, orientation_sign, SEED)
    summary = stage_summary("development", intervals, scores, events, shift_null)
    summary["gates"] = gates(summary)
    freeze = {
        "test": "T423 parent Di-ARA temporal architecture",
        "frozen_after_stage": "development",
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(Path(__file__)),
        "source_sha256": sha256(stage_source("development")),
        "orientation_sign": orientation_sign,
        "orientation_meaning": "relation_sign = child crossing direction times Q crossing direction",
        "features": {"M0": list(BASE_FEATURES), "M1": list(M1_FEATURES), "M2": list(M2_FEATURES)},
        "models": models,
        "constants": {
            "ridge_penalty": RIDGE_PENALTY, "bootstraps": BOOTSTRAPS,
            "shift_draws": SHIFT_DRAWS, "seed": SEED,
        },
    }
    write_json(FREEZE, freeze)
    save_stage("development", intervals, detailed, scores, events, shift_null, summary)
    return summary


def load_freeze() -> dict:
    if not FREEZE.exists():
        raise FileNotFoundError("run development before evaluation")
    payload = json.loads(FREEZE.read_text(encoding="utf-8"))
    if payload["protocol_sha256"] != sha256(PROTOCOL):
        raise RuntimeError("frozen protocol hash changed")
    if payload["analysis_sha256"] != sha256(Path(__file__)):
        raise RuntimeError("analysis changed after development freeze")
    return payload


def run_evaluation(stage: str) -> dict:
    freeze = load_freeze()
    intervals, rows, groups = build_stage_rows(stage)
    events = decorate_expected(parent_events(groups, intervals), int(freeze["orientation_sign"]))
    detailed, scores = score_predictions(stage, rows, freeze["models"])
    shift_null = order_shift_null(groups, intervals, int(freeze["orientation_sign"]), SEED + (100000 if stage == "validation" else 200000))
    summary = stage_summary(stage, intervals, scores, events, shift_null)
    summary["gates"] = gates(summary, holdout=(stage == "holdout"))
    summary["source_sha256"] = sha256(stage_source(stage))
    save_stage(stage, intervals, detailed, scores, events, shift_null, summary)
    return summary


def save_stage(
    stage: str, intervals: list[dict], detailed: list[dict], scores: list[dict],
    events: list[dict], shift_null: list[dict], summary: dict
) -> None:
    prefix = RESULTS / f"T423_{stage.upper()}"
    write_csv(Path(str(prefix) + "_INTERVALS.csv"), intervals, ["split", "interval_id"])
    write_csv(Path(str(prefix) + "_PREDICTIONS.csv"), detailed, ["split", "interval_id"])
    write_csv(Path(str(prefix) + "_INTERVAL_SCORES.csv"), scores, ["split", "interval_id"])
    write_csv(Path(str(prefix) + "_PARENT_EVENTS.csv"), events, ["split", "interval_id"])
    write_csv(Path(str(prefix) + "_ORDER_SHIFT_NULL.csv"), shift_null, ["draw", "expected_share", "parent_ridge_exposure"])
    result = {
        "test": "T423 parent Di-ARA temporal architecture",
        "stage": stage,
        "identity": "full-detector muoniated-acetone ensemble spin relation",
        "orientation": "U=R child crossover; H=1 parent ridge; Q=1 candidate PA/PB handover",
        "summary": summary,
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(Path(__file__)),
        "source_sha256": sha256(stage_source(stage)),
        "boundaries": [
            "Population-level relation, not an individual muon or neutrino event.",
            "PA/PB are development-frozen temporal labels, not physical sign assignments.",
            "Order landmarks are descriptive; nested row prediction is the causal primary.",
        ],
    }
    write_json(Path(str(prefix) + "_RESULTS.json"), result)


def finalize_status() -> dict:
    validation_path = RESULTS / "T423_VALIDATION_RESULTS.json"
    holdout_path = RESULTS / "T423_HOLDOUT_RESULTS.json"
    if not validation_path.exists() or not holdout_path.exists():
        return {}
    validation = json.loads(validation_path.read_text(encoding="utf-8"))["summary"]
    holdout = json.loads(holdout_path.read_text(encoding="utf-8"))["summary"]
    status = status_from(validation, validation["gates"], holdout, holdout["gates"])
    comparison = {
        "test": "T423 parent Di-ARA temporal architecture",
        "registered_status": status,
        "G4_holdout_transfer": {
            "pass": bool(
                holdout["gates"]["G1_availability"]["pass"]
                and holdout["effects_us"]["M0_over_M2"]["median"] > 0
                and holdout["effects_us"]["M1_over_M2"]["median"] > 0
            ),
            "M0_over_M2": holdout["effects_us"]["M0_over_M2"],
            "M1_over_M2": holdout["effects_us"]["M1_over_M2"],
        },
        "development": json.loads((RESULTS / "T423_DEVELOPMENT_RESULTS.json").read_text(encoding="utf-8"))["summary"],
        "validation": validation,
        "holdout": holdout,
    }
    write_json(RESULTS / "T423_COMPARISON_RESULTS.json", comparison)
    return comparison


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "validation", "holdout", "all"), default="all")
    args = parser.parse_args()
    if args.stage in ("development", "all"):
        print(json.dumps(clean(run_development()), indent=2))
    if args.stage in ("validation", "all"):
        print(json.dumps(clean(run_evaluation("validation")), indent=2))
    if args.stage in ("holdout", "all"):
        print(json.dumps(clean(run_evaluation("holdout")), indent=2))
    comparison = finalize_status()
    if comparison:
        print(json.dumps(clean({"registered_status": comparison["registered_status"]}), indent=2))


if __name__ == "__main__":
    main()
