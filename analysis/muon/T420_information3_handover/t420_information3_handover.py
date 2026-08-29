#!/usr/bin/env python3
"""T420 independent Information^3 handover-channel test."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
MUON = HERE.parent
T416_DIR = MUON / "T416_dual_irrationality_time_tracking"
T419_DIR = MUON / "T419_dynamic_irrationality_handover"
PROTOCOL = HERE / "T420_FROZEN_PROTOCOL.md"
RESULTS = HERE / "results"
FREEZE = HERE / "T420_DEVELOPMENT_FREEZE.json"

sys.path.insert(0, str(T416_DIR))
sys.path.insert(0, str(T419_DIR))
import t416_dual_irrationality_time_tracking as t416  # noqa: E402
import t419_dynamic_irrationality_handover as t419  # noqa: E402


SEED = 420
PRIMARY_HORIZON = 32
DIAGNOSTIC_HORIZONS = (1, 2, 4, 8, 16, 24, 32)
MIN_PRIMARY_ROWS = 8
SHIFT_DRAWS = 1000
BOOTSTRAPS = 10000
EVENT_HALF_WIDTH = 8
EPS = 1e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def relation_metrics(phase_history: np.ndarray) -> dict:
    _, local_loss, null_loss = t416.stochastic_residual(phase_history)
    rho, miss = t416.closure_history(phase_history)
    denominator = local_loss + null_loss
    openness = 1.0 if denominator <= EPS else 2.0 * local_loss / denominator
    return {
        "U": float(openness),
        "R": float(2.0 * np.median(rho)),
        "H": float(2.0 * np.median(miss)),
        "local_loss": float(local_loss),
        "null_loss": float(null_loss),
    }


def analyse_run_period(row: dict, period: str) -> list[dict]:
    data = t416.t414.load_run(row)
    period_index = 0 if period == "RF on" else 1
    counts = data["counts"][period_index]
    time = data["time"]
    field = float(row["field_G"])
    frequency = t416.GAMMA_MHZ_PER_G * field
    correct = t416.extract_spin_path(time, counts, frequency)
    dt = float(np.median(np.diff(correct["time"])))
    cycle_bins = max(4, int(round(1.0 / max(frequency * dt, EPS))))

    wrong_frequencies: list[float] = []
    for k in t416.WRONG_K:
        for sign in (-1.0, 1.0):
            candidate = frequency + sign * float(k) / t416.LENGTH_US
            if candidate > 0.05:
                wrong_frequencies.append(candidate)
    wrong_paths = [t416.extract_spin_path(time, counts, value) for value in wrong_frequencies]

    turns_per_lifetime = max(frequency * t416.TAU_US, EPS)
    field_turn_log2 = math.log2(turns_per_lifetime)
    start = max(t416.PATH_WINDOW - 1, cycle_bins)
    timeline: list[dict] = []
    for end in range(start, len(correct["time"]), t416.PATH_STEP):
        history = correct["phase"][end - t416.PATH_WINDOW + 1 : end + 1]
        measured = relation_metrics(history)
        wrong = []
        for path in wrong_paths:
            wrong_history = path["phase"][end - t416.PATH_WINDOW + 1 : end + 1]
            wrong.append(relation_metrics(wrong_history))
        x_l, x_c = t416.state_coordinates(correct["radius"], correct["phase"], end, cycle_bins)
        time_us = float(correct["time"][end])
        timeline.append({
            "split": row["split"],
            "run": row["run"],
            "period": period,
            "rf_flag": 1 if period == "RF on" else 0,
            "temperature_K": float(row["temperature_K"]),
            "field_G": field,
            "frequency_MHz": frequency,
            "turns_per_lifetime": turns_per_lifetime,
            "field_turn_log2": field_turn_log2,
            "time_us": time_us,
            "parent_ARA": 2.0 * (1.0 - math.exp(-time_us / t416.TAU_US)),
            "state_x_L": float(x_l),
            "state_x_C": float(x_c),
            "spin_radius": float(correct["radius"][end]),
            "observed_phase_ARA": 2.0 * float(correct["phase"][end]),
            "openness_U": measured["U"],
            "closure_R": measured["R"],
            "handover_H": measured["H"],
            "local_loss": measured["local_loss"],
            "null_loss": measured["null_loss"],
            "wrong_openness_U": float(np.median([item["U"] for item in wrong])),
            "wrong_closure_R": float(np.median([item["R"] for item in wrong])),
            "wrong_handover_H": float(np.median([item["H"] for item in wrong])),
            "cycle_bins": cycle_bins,
            "history_native_bins": t416.PATH_WINDOW,
        })
    return timeline


def grouped(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    output: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        output.setdefault((str(row["run"]), str(row["period"])), []).append(row)
    for key in output:
        output[key].sort(key=lambda item: float(item["time_us"]))
    return output


def interpolate(a: float, b: float, fraction: float) -> float:
    return float(a + fraction * (b - a))


def crossing_events(timeline: list[dict], affine: tuple[float, float] | None = None) -> tuple[list[dict], list[dict]]:
    events: list[dict] = []
    centered: list[dict] = []
    for _, rows in sorted(grouped(timeline).items()):
        u = np.asarray([float(row["openness_U"]) for row in rows])
        r = np.asarray([float(row["closure_R"]) for row in rows])
        h = np.asarray([float(row["handover_H"]) for row in rows])
        wh = np.asarray([float(row["wrong_handover_H"]) for row in rows])
        history_median_h = float(np.median(h))
        # Median over all circular placements is the exact timing-destroyed null
        # for a scalar event read and avoids privileging one arbitrary shift.
        shifted_h = history_median_h
        for index in range(1, len(rows)):
            da, db = u[index - 1] - r[index - 1], u[index] - r[index]
            if da == 0.0:
                fraction = 0.0
            elif db == 0.0:
                fraction = 1.0
            elif da * db > 0.0:
                continue
            else:
                fraction = float(-da / (db - da))
            if not 0.0 <= fraction <= 1.0:
                continue
            cross_u = interpolate(u[index - 1], u[index], fraction)
            cross_r = interpolate(r[index - 1], r[index], fraction)
            cross_h = interpolate(h[index - 1], h[index], fraction)
            wrong_h = interpolate(wh[index - 1], wh[index], fraction)
            parent = interpolate(float(rows[index - 1]["parent_ARA"]), float(rows[index]["parent_ARA"]), fraction)
            time_us = interpolate(float(rows[index - 1]["time_us"]), float(rows[index]["time_us"]), fraction)
            e2 = abs(2.0 - cross_u - cross_r)
            e3 = abs(2.0 - cross_u - cross_r - cross_h)
            e3_shift = abs(2.0 - cross_u - cross_r - shifted_h)
            e3_wrong = abs(2.0 - cross_u - cross_r - wrong_h)
            affine_h = float("nan") if affine is None else float(affine[0] + affine[1] * cross_h)
            e3_affine = float("nan") if affine is None else abs(2.0 - cross_u - cross_r - affine_h)
            direction = "R_to_U" if da < 0.0 and db > 0.0 else "U_to_R"
            event_id = f"{rows[index]['run']}|{rows[index]['period']}|{index}"
            events.append({
                "split": rows[index]["split"],
                "event_id": event_id,
                "run": rows[index]["run"],
                "period": rows[index]["period"],
                "rf_flag": rows[index]["rf_flag"],
                "temperature_K": rows[index]["temperature_K"],
                "field_G": rows[index]["field_G"],
                "direction": direction,
                "crossing_time_us": time_us,
                "crossing_U": cross_u,
                "crossing_R": cross_r,
                "crossing_H": cross_h,
                "wrong_H": wrong_h,
                "shifted_H": shifted_h,
                "history_median_H": history_median_h,
                "parent_ARA": parent,
                "H_exposure": cross_h - history_median_h,
                "E2": e2,
                "E3_correct": e3,
                "E3_shifted": e3_shift,
                "E3_wrong": e3_wrong,
                "affine_H": affine_h,
                "E3_affine": e3_affine,
                "closure_gain": e2 - e3,
                "shifted_minus_correct": e3_shift - e3,
                "wrong_minus_correct": e3_wrong - e3,
            })
            for offset in range(-EVENT_HALF_WIDTH, EVENT_HALF_WIDTH + 1):
                pos = index + offset
                if not 0 <= pos < len(rows):
                    continue
                centered.append({
                    "split": rows[index]["split"],
                    "event_id": event_id,
                    "run": rows[index]["run"],
                    "period": rows[index]["period"],
                    "field_G": rows[index]["field_G"],
                    "direction": direction,
                    "offset_reads": offset,
                    "offset_us": float(rows[pos]["time_us"]) - time_us,
                    "U": float(rows[pos]["openness_U"]),
                    "R": float(rows[pos]["closure_R"]),
                    "H": float(rows[pos]["handover_H"]),
                    "parent_ARA": float(rows[pos]["parent_ARA"]),
                })
    return events, centered


def build_prediction_rows(timeline: list[dict], horizon: int) -> tuple[list[dict], list[dict]]:
    accepted: list[dict] = []
    eligibility: list[dict] = []
    for _, rows in sorted(grouped(timeline).items()):
        candidates: list[dict] = []
        for index in range(1, len(rows) - horizon):
            source, previous, future = rows[index], rows[index - 1], rows[index + horizon]
            candidates.append({
                "split": source["split"],
                "run": source["run"],
                "period": source["period"],
                "rf_flag": int(source["rf_flag"]),
                "temperature_K": float(source["temperature_K"]),
                "field_G": float(source["field_G"]),
                "field_turn_log2": float(source["field_turn_log2"]),
                "turns_per_lifetime": float(source["turns_per_lifetime"]),
                "time_us": float(source["time_us"]),
                "future_time_us": float(future["time_us"]),
                "horizon_reads": horizon,
                "horizon_native_bins": horizon * t416.PATH_STEP,
                "horizon_us": float(future["time_us"]) - float(source["time_us"]),
                "shared_native_bins": max(0, t416.PATH_WINDOW - horizon * t416.PATH_STEP),
                "parent_ARA": float(source["parent_ARA"]),
                "U": float(source["openness_U"]),
                "dU": float(source["openness_U"]) - float(previous["openness_U"]),
                "R": float(source["closure_R"]),
                "dR": float(source["closure_R"]) - float(previous["closure_R"]),
                "H": float(source["handover_H"]),
                "dH": float(source["handover_H"]) - float(previous["handover_H"]),
                "wrong_H": float(source["wrong_handover_H"]),
                "wrong_dH": float(source["wrong_handover_H"]) - float(previous["wrong_handover_H"]),
                "future_U": float(future["openness_U"]),
                "future_R": float(future["closure_R"]),
            })
        first = rows[0]
        eligible = len(candidates) >= MIN_PRIMARY_ROWS
        eligibility.append({
            "split": first["split"], "run": first["run"], "period": first["period"],
            "field_G": float(first["field_G"]), "timeline_rows": len(rows),
            "horizon_reads": horizon, "prediction_rows": len(candidates), "eligible": int(eligible),
        })
        if eligible:
            accepted.extend(candidates)
    return accepted, eligibility


def baseline_matrix(rows: list[dict]) -> np.ndarray:
    return np.asarray([[r["U"], r["dU"], r["R"], r["dR"], r["parent_ARA"], r["field_turn_log2"], r["rf_flag"]] for r in rows], dtype=float)


def source_matrix(rows: list[dict], source: str = "correct") -> np.ndarray:
    keys = ("H", "dH") if source == "correct" else ("wrong_H", "wrong_dH")
    return np.asarray([[r[keys[0]], r[keys[1]]] for r in rows], dtype=float)


def transfer_matrix(rows: list[dict], source: str = "correct") -> np.ndarray:
    return np.column_stack((baseline_matrix(rows), source_matrix(rows, source)))


def target_vector(rows: list[dict], target: str) -> np.ndarray:
    key = "future_U" if target == "future_U" else "future_R"
    return np.asarray([r[key] for r in rows], dtype=float)


def fit_models(rows: list[dict], target: str) -> dict:
    y = target_vector(rows, target)
    return {
        "baseline": t419.fit_linear(baseline_matrix(rows), y),
        "transfer": t419.fit_linear(transfer_matrix(rows), y),
    }


def add_predictions(rows: list[dict], target: str, models: dict) -> list[dict]:
    actual = target_vector(rows, target)
    baseline = t419.predict(models["baseline"], baseline_matrix(rows))
    transfer = t419.predict(models["transfer"], transfer_matrix(rows, "correct"))
    wrong = t419.predict(models["transfer"], transfer_matrix(rows, "wrong"))
    output = []
    for index, source in enumerate(rows):
        item = dict(source)
        item.update({
            "target": target,
            "actual_target": float(actual[index]),
            "baseline_prediction": float(baseline[index]),
            "transfer_prediction": float(transfer[index]),
            "wrong_prediction": float(wrong[index]),
            "baseline_sq_error": float((baseline[index] - actual[index]) ** 2),
            "transfer_sq_error": float((transfer[index] - actual[index]) ** 2),
            "wrong_sq_error": float((wrong[index] - actual[index]) ** 2),
        })
        output.append(item)
    return output


def sequence_metrics(rows: list[dict], target: str, models: dict) -> list[dict]:
    scored = add_predictions(rows, target, models)
    output = []
    for _, sequence in sorted(grouped(scored).items()):
        actual = target_vector(sequence, target)
        reverse_x = np.column_stack((baseline_matrix(sequence), source_matrix(sequence)[::-1]))
        reverse_prediction = t419.predict(models["transfer"], reverse_x)
        item = {
            "split": sequence[0]["split"], "run": sequence[0]["run"], "period": sequence[0]["period"],
            "field_G": float(sequence[0]["field_G"]), "target": target, "scored_rows": len(sequence),
            "baseline_mse": float(np.mean([r["baseline_sq_error"] for r in sequence])),
            "transfer_mse": float(np.mean([r["transfer_sq_error"] for r in sequence])),
            "wrong_mse": float(np.mean([r["wrong_sq_error"] for r in sequence])),
            "reverse_mse": float(np.mean((reverse_prediction - actual) ** 2)),
        }
        item["baseline_minus_transfer"] = item["baseline_mse"] - item["transfer_mse"]
        item["wrong_minus_transfer"] = item["wrong_mse"] - item["transfer_mse"]
        item["reverse_minus_transfer"] = item["reverse_mse"] - item["transfer_mse"]
        output.append(item)
    return output


def field_values(rows: list[dict], key: str) -> dict[float, float]:
    output = {}
    for field in sorted({float(r["field_G"]) for r in rows}):
        output[field] = float(np.median([float(r[key]) for r in rows if float(r["field_G"]) == field]))
    return output


def aggregate(rows: list[dict], key: str) -> float:
    values = list(field_values(rows, key).values())
    return float(np.median(values)) if values else float("nan")


def bootstrap_interval(values: dict[float, float], seed: int) -> tuple[float, float, float]:
    data = np.asarray([values[k] for k in sorted(values)], dtype=float)
    if len(data) == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    draws = rng.choice(data, size=(BOOTSTRAPS, len(data)), replace=True)
    medians = np.median(draws, axis=1)
    return float(np.median(data)), float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))


def shifted_null(rows: list[dict], target: str, models: dict) -> np.ndarray:
    groups = grouped(rows)
    rng = np.random.default_rng(SEED + (0 if target == "future_U" else 10000))
    draws = np.empty(SHIFT_DRAWS, dtype=float)
    for draw in range(SHIFT_DRAWS):
        errors = []
        for _, sequence in sorted(groups.items()):
            n = len(sequence)
            candidates = np.arange(2, max(3, n - 1), dtype=int)
            shift = int(rng.choice(candidates)) if len(candidates) else 1
            shifted = np.roll(source_matrix(sequence), shift, axis=0)
            prediction = t419.predict(models["transfer"], np.column_stack((baseline_matrix(sequence), shifted)))
            errors.append({"field_G": float(sequence[0]["field_G"]), "mse": float(np.mean((prediction - target_vector(sequence, target)) ** 2))})
        draws[draw] = aggregate(errors, "mse")
    return draws


def prediction_summary(stage: str, rows: list[dict], target: str, models: dict) -> tuple[dict, list[dict], list[dict], np.ndarray]:
    scored = add_predictions(rows, target, models)
    sequences = sequence_metrics(rows, target, models)
    added = bootstrap_interval(field_values(sequences, "baseline_minus_transfer"), SEED + 1)
    wrong = bootstrap_interval(field_values(sequences, "wrong_minus_transfer"), SEED + 2)
    reverse = bootstrap_interval(field_values(sequences, "reverse_minus_transfer"), SEED + 3)
    shifts = shifted_null(rows, target, models)
    transfer_mse = aggregate(sequences, "transfer_mse")
    shift_p = float((1 + np.count_nonzero(shifts <= transfer_mse)) / (1 + len(shifts)))
    rf = {period: float(np.median([r["baseline_minus_transfer"] for r in sequences if r["period"] == period])) for period in ("RF on", "RF off")}
    result = {
        "target": target, "stage": stage, "prediction_rows": len(rows),
        "errors": {
            "baseline_mse": aggregate(sequences, "baseline_mse"),
            "transfer_mse": transfer_mse,
            "wrong_frequency_mse": aggregate(sequences, "wrong_mse"),
            "reverse_mse": aggregate(sequences, "reverse_mse"),
        },
        "effects": {
            "baseline_minus_transfer": {"median": added[0], "ci95": [added[1], added[2]]},
            "wrong_minus_transfer": {"median": wrong[0], "ci95": [wrong[1], wrong[2]]},
            "reverse_minus_transfer": {"median": reverse[0], "ci95": [reverse[1], reverse[2]]},
            "rf_baseline_minus_transfer": rf,
            "shift": {"observed_transfer_mse": transfer_mse, "null_median": float(np.median(shifts)), "empirical_p": shift_p},
        },
        "passes": {
            "added_information": bool(added[1] > 0.0),
            "timing_specificity": bool(shift_p < 0.05),
            "frequency_specificity": bool(wrong[1] > 0.0),
            "direction_specificity": bool(reverse[1] > 0.0),
            "rf_robustness": bool(all(value > 0.0 for value in rf.values())),
        },
    }
    return result, scored, sequences, shifts


def event_summary(events: list[dict]) -> dict:
    if not events:
        return {"event_count": 0, "passes": {"crossing_exposure": False, "closure_gain": False, "shift_specificity": False, "frequency_specificity": False}}
    exposure = bootstrap_interval(field_values(events, "H_exposure"), SEED + 11)
    closure = bootstrap_interval(field_values(events, "closure_gain"), SEED + 12)
    shift = bootstrap_interval(field_values(events, "shifted_minus_correct"), SEED + 13)
    wrong = bootstrap_interval(field_values(events, "wrong_minus_correct"), SEED + 14)
    return {
        "event_count": len(events),
        "sequence_count": len({(r["run"], r["period"]) for r in events}),
        "field_count": len({float(r["field_G"]) for r in events}),
        "direction_counts": {direction: sum(r["direction"] == direction for r in events) for direction in ("R_to_U", "U_to_R")},
        "median_crossing_coordinate": float(np.median([r["crossing_U"] for r in events])),
        "median_parent_ARA": float(np.median([r["parent_ARA"] for r in events])),
        "median_H": float(np.median([r["crossing_H"] for r in events])),
        "median_E2": float(np.median([r["E2"] for r in events])),
        "median_E3_correct": float(np.median([r["E3_correct"] for r in events])),
        "median_E3_shifted": float(np.median([r["E3_shifted"] for r in events])),
        "median_E3_wrong": float(np.median([r["E3_wrong"] for r in events])),
        "median_E3_affine": float(np.median([r["E3_affine"] for r in events])) if np.isfinite([r["E3_affine"] for r in events]).any() else float("nan"),
        "effects": {
            "H_cross_minus_history": {"median": exposure[0], "ci95": [exposure[1], exposure[2]]},
            "E2_minus_E3": {"median": closure[0], "ci95": [closure[1], closure[2]]},
            "shifted_minus_correct": {"median": shift[0], "ci95": [shift[1], shift[2]]},
            "wrong_minus_correct": {"median": wrong[0], "ci95": [wrong[1], wrong[2]]},
        },
        "passes": {
            "crossing_exposure": bool(exposure[1] > 0.0),
            "closure_gain": bool(closure[1] > 0.0),
            "shift_specificity": bool(shift[1] > 0.0),
            "frequency_specificity": bool(wrong[1] > 0.0),
        },
    }


def coordinate_summary(timeline: list[dict]) -> dict:
    u = np.asarray([float(r["openness_U"]) for r in timeline])
    rr = np.asarray([float(r["closure_R"]) for r in timeline])
    h = np.asarray([float(r["handover_H"]) for r in timeline])
    return {
        "std_U_plus_R_plus_H": float(np.std(u + rr + h)),
        "corr_H_U": float(np.corrcoef(h, u)[0, 1]),
        "corr_H_R": float(np.corrcoef(h, rr)[0, 1]),
        "median_U_plus_R_plus_H": float(np.median(u + rr + h)),
    }


def fit_affine(events: list[dict]) -> tuple[float, float]:
    h = np.asarray([r["crossing_H"] for r in events], dtype=float)
    target = np.asarray([2.0 - r["crossing_U"] - r["crossing_R"] for r in events], dtype=float)
    design = np.column_stack((np.ones(len(h)), h))
    beta = np.linalg.lstsq(design, target, rcond=None)[0]
    return float(beta[0]), float(beta[1])


def lag_diagnostics(stage: str, timeline: list[dict], models: dict) -> list[dict]:
    output = []
    for horizon in DIAGNOSTIC_HORIZONS:
        rows, _ = build_prediction_rows(timeline, horizon)
        for target in ("future_U", "future_R"):
            sequences = sequence_metrics(rows, target, models[str(horizon)][target])
            baseline = aggregate(sequences, "baseline_mse")
            transfer = aggregate(sequences, "transfer_mse")
            output.append({
                "split": stage, "target": target, "horizon_reads": horizon,
                "horizon_native_bins": horizon * t416.PATH_STEP,
                "horizon_us_median": float(np.median([r["horizon_us"] for r in rows])),
                "shared_native_bins": max(0, t416.PATH_WINDOW - horizon * t416.PATH_STEP),
                "overlapping_histories": int(horizon < PRIMARY_HORIZON),
                "prediction_rows": len(rows), "baseline_mse": baseline, "transfer_mse": transfer,
                "baseline_minus_transfer": baseline - transfer,
                "relative_improvement_pct": 100.0 * (baseline - transfer) / max(baseline, EPS),
            })
    return output


def run_stage(stage: str) -> None:
    manifest = [row for row in t416.t414.read_manifest() if row["split"] == stage]
    if not manifest:
        raise ValueError(f"no source rows for stage {stage}")
    timeline: list[dict] = []
    for index, row in enumerate(manifest, start=1):
        print(f"{stage}: {index}/{len(manifest)} {row['run']} {row['field_G']:.0f} G", flush=True)
        for period in ("RF on", "RF off"):
            timeline.extend(analyse_run_period(row, period))

    primary_rows, eligibility = build_prediction_rows(timeline, PRIMARY_HORIZON)
    preliminary_events, _ = crossing_events(timeline)
    if stage == "development":
        affine = fit_affine(preliminary_events)
        primary_models = {target: fit_models(primary_rows, target) for target in ("future_U", "future_R")}
        lag_models = {}
        for horizon in DIAGNOSTIC_HORIZONS:
            lag_rows, _ = build_prediction_rows(timeline, horizon)
            lag_models[str(horizon)] = {target: fit_models(lag_rows, target) for target in ("future_U", "future_R")}
    else:
        if not FREEZE.exists():
            raise FileNotFoundError("T420 development freeze missing")
        frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
        for key, current in (("protocol_sha256", sha256(PROTOCOL)), ("analysis_sha256", sha256(Path(__file__).resolve()))):
            if frozen[key] != current:
                raise RuntimeError(f"{stage} refused: frozen {key} mismatch")
        affine = tuple(frozen["affine_closure"])
        primary_models = frozen["primary_models"]
        lag_models = frozen["lag_models"]

    events, centered = crossing_events(timeline, affine)
    event_result = event_summary(events)
    coordinate_result = coordinate_summary(timeline)
    prediction_results = {}
    scored_rows: list[dict] = []
    sequence_rows: list[dict] = []
    shift_rows: list[dict] = []
    for target in ("future_U", "future_R"):
        result, scored, sequences, shifts = prediction_summary(stage, primary_rows, target, primary_models[target])
        prediction_results[target] = result
        scored_rows.extend(scored)
        sequence_rows.extend(sequences)
        shift_rows.extend({"target": target, "draw": i, "shifted_transfer_mse": float(value)} for i, value in enumerate(shifts))

    availability = sum(int(r["eligible"]) for r in eligibility) / max(len(eligibility), 1)
    non_complementary = coordinate_result["std_U_plus_R_plus_H"] > 0.01 and abs(coordinate_result["corr_H_U"]) < 0.95 and abs(coordinate_result["corr_H_R"]) < 0.95
    primary_prediction_passes = prediction_results["future_U"]["passes"]
    gates = {
        "G1_availability": {"pass": bool(availability >= 0.75), "value": availability},
        "G2_independent_not_complement": {"pass": bool(non_complementary), **coordinate_result},
        "G3_crossing_exposure": {"pass": bool(event_result["passes"]["crossing_exposure"])},
        "G4_three_part_closure": {"pass": bool(event_result["passes"]["closure_gain"] and event_result["passes"]["shift_specificity"] and event_result["passes"]["frequency_specificity"]), "parts": event_result["passes"]},
        "G5_future_openness_added_information": {"pass": bool(primary_prediction_passes["added_information"])},
        "G6_prediction_specificity": {"pass": bool(primary_prediction_passes["timing_specificity"] and primary_prediction_passes["frequency_specificity"] and primary_prediction_passes["direction_specificity"]), "parts": primary_prediction_passes},
        "G7_rf_robustness": {"pass": bool(primary_prediction_passes["rf_robustness"]), "effects": prediction_results["future_U"]["effects"]["rf_baseline_minus_transfer"]},
    }
    result = {
        "test": "T420 independent Information^3 handover channel",
        "stage": stage,
        "identity": "muoniated-acetone detector-population spin relation",
        "primary_horizon": {"reads": PRIMARY_HORIZON, "native_bins": PRIMARY_HORIZON * t416.PATH_STEP, "median_us": float(np.median([r["horizon_us"] for r in primary_rows])), "shared_native_bins": 0},
        "run_count": len(manifest), "run_period_sequences": len(eligibility),
        "eligible_sequences": int(sum(int(r["eligible"]) for r in eligibility)),
        "availability_fraction": availability, "timeline_rows": len(timeline),
        "primary_prediction_rows": len(primary_rows), "affine_closure": list(affine),
        "coordinate_independence": coordinate_result, "crossings": event_result,
        "predictions": prediction_results, "gates": gates,
        "stage_supported": bool(all(g["pass"] for g in gates.values())),
        "protocol_sha256": sha256(PROTOCOL), "analysis_sha256": sha256(Path(__file__).resolve()),
        "source_hashes": {row["run"]: sha256(t416.t414.RAW / f"{row['run']}.nxs") for row in manifest},
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    prefix = f"T420_{stage.upper()}"
    write_csv(RESULTS / f"{prefix}_TIMELINE.csv", timeline)
    write_csv(RESULTS / f"{prefix}_CROSSING_EVENTS.csv", events)
    write_csv(RESULTS / f"{prefix}_EVENT_CENTERED.csv", centered)
    write_csv(RESULTS / f"{prefix}_PREDICTION_ROWS.csv", scored_rows)
    write_csv(RESULTS / f"{prefix}_SEQUENCE_ELIGIBILITY.csv", eligibility)
    write_csv(RESULTS / f"{prefix}_SEQUENCE_METRICS.csv", sequence_rows)
    write_csv(RESULTS / f"{prefix}_SHIFT_NULL.csv", shift_rows)
    write_csv(RESULTS / f"{prefix}_LAG_DIAGNOSTICS.csv", lag_diagnostics(stage, timeline, lag_models))
    write_json(RESULTS / f"{prefix}_RESULTS.json", result)

    if stage == "development":
        write_json(FREEZE, {
            "test": result["test"], "frozen_after_development_before_validation_and_holdout": True,
            "protocol_sha256": result["protocol_sha256"], "analysis_sha256": result["analysis_sha256"],
            "constants": {"primary_horizon_reads": PRIMARY_HORIZON, "diagnostic_horizons": list(DIAGNOSTIC_HORIZONS), "minimum_primary_rows": MIN_PRIMARY_ROWS, "history_native_bins": t416.PATH_WINDOW, "path_step_native_bins": t416.PATH_STEP, "event_half_width_reads": EVENT_HALF_WIDTH, "shift_draws": SHIFT_DRAWS, "bootstraps": BOOTSTRAPS, "seed": SEED},
            "affine_closure": list(affine), "primary_models": primary_models,
            "lag_models": lag_models, "development_result": result,
        })
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "validation", "holdout"), required=True)
    args = parser.parse_args()
    run_stage(args.stage)


if __name__ == "__main__":
    main()
