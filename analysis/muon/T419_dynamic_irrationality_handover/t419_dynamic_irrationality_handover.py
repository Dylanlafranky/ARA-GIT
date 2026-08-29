#!/usr/bin/env python3
"""T419 direct dynamic Irrationality Di-ARA handover test."""

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
PROTOCOL = HERE / "T419_FROZEN_PROTOCOL.md"
RESULTS = HERE / "results"
FREEZE = HERE / "T419_DEVELOPMENT_FREEZE.json"

sys.path.insert(0, str(T416_DIR))
import t416_dual_irrationality_time_tracking as t416  # noqa: E402


SEED = 419
PRIMARY_HORIZON = 32
DIAGNOSTIC_HORIZONS = (1, 2, 4, 8, 16, 24, 32)
MIN_PRIMARY_ROWS = 8
SHIFT_DRAWS = 1000
BOOTSTRAPS = 10000
EPS = 1e-12
ARMS = ("U_to_R", "R_to_U")


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
    rho, _ = t416.closure_history(phase_history)
    denominator = local_loss + null_loss
    openness = 1.0 if denominator <= EPS else 2.0 * local_loss / denominator
    return {
        "U": float(openness),
        "R": float(2.0 * np.median(rho)),
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
    wrong_paths = [
        t416.extract_spin_path(time, counts, candidate)
        for candidate in wrong_frequencies
    ]

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
            "local_loss": measured["local_loss"],
            "null_loss": measured["null_loss"],
            "wrong_openness_U": float(np.median([item["U"] for item in wrong])),
            "wrong_closure_R": float(np.median([item["R"] for item in wrong])),
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


def build_prediction_rows(timeline: list[dict], horizon: int) -> tuple[list[dict], list[dict]]:
    accepted: list[dict] = []
    eligibility: list[dict] = []
    for _, rows in sorted(grouped(timeline).items()):
        u = np.asarray([float(row["openness_U"]) for row in rows])
        r = np.asarray([float(row["closure_R"]) for row in rows])
        wu = np.asarray([float(row["wrong_openness_U"]) for row in rows])
        wr = np.asarray([float(row["wrong_closure_R"]) for row in rows])
        candidates: list[dict] = []
        for index in range(1, len(rows) - horizon):
            source = rows[index]
            future = rows[index + horizon]
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
                "horizon_us": float(future["time_us"] - source["time_us"]),
                "shared_native_bins": max(0, t416.PATH_WINDOW - horizon * t416.PATH_STEP),
                "parent_ARA": float(source["parent_ARA"]),
                "U": float(u[index]),
                "dU": float(u[index] - u[index - 1]),
                "R": float(r[index]),
                "dR": float(r[index] - r[index - 1]),
                "wrong_U": float(wu[index]),
                "wrong_dU": float(wu[index] - wu[index - 1]),
                "wrong_R": float(wr[index]),
                "wrong_dR": float(wr[index] - wr[index - 1]),
                "future_U": float(u[index + horizon]),
                "future_R": float(r[index + horizon]),
            })
        first = rows[0]
        eligible = len(candidates) >= MIN_PRIMARY_ROWS
        eligibility.append({
            "split": first["split"],
            "run": first["run"],
            "period": first["period"],
            "field_G": float(first["field_G"]),
            "timeline_rows": len(rows),
            "horizon_reads": horizon,
            "prediction_rows": len(candidates),
            "eligible": int(eligible),
        })
        if eligible:
            accepted.extend(candidates)
    return accepted, eligibility


def baseline_matrix(rows: list[dict], arm: str) -> np.ndarray:
    if arm == "U_to_R":
        own = [(row["R"], row["dR"]) for row in rows]
    elif arm == "R_to_U":
        own = [(row["U"], row["dU"]) for row in rows]
    else:
        raise ValueError(arm)
    return np.asarray([
        [value, delta, row["parent_ARA"], row["field_turn_log2"], row["rf_flag"]]
        for (value, delta), row in zip(own, rows)
    ], dtype=float)


def source_values(rows: list[dict], arm: str, source: str = "correct") -> np.ndarray:
    if arm == "U_to_R":
        keys = ("U", "dU") if source == "correct" else ("wrong_U", "wrong_dU")
    elif arm == "R_to_U":
        keys = ("R", "dR") if source == "correct" else ("wrong_R", "wrong_dR")
    else:
        raise ValueError(arm)
    return np.asarray([[row[keys[0]], row[keys[1]]] for row in rows], dtype=float)


def transfer_matrix(rows: list[dict], arm: str, source: str = "correct") -> np.ndarray:
    return np.column_stack((baseline_matrix(rows, arm), source_values(rows, arm, source)))


def target_vector(rows: list[dict], arm: str) -> np.ndarray:
    key = "future_R" if arm == "U_to_R" else "future_U"
    return np.asarray([row[key] for row in rows], dtype=float)


def fit_linear(x: np.ndarray, y: np.ndarray) -> dict:
    x_mean = np.mean(x, axis=0)
    x_scale = np.std(x, axis=0)
    x_scale[x_scale < EPS] = 1.0
    y_mean = float(np.mean(y))
    y_scale = float(np.std(y))
    if y_scale < EPS:
        y_scale = 1.0
    zx = (x - x_mean) / x_scale
    zy = (y - y_mean) / y_scale
    design = np.column_stack((np.ones(len(zx)), zx))
    beta = np.linalg.lstsq(design, zy, rcond=None)[0]
    return {
        "x_mean": x_mean.tolist(),
        "x_scale": x_scale.tolist(),
        "y_mean": y_mean,
        "y_scale": y_scale,
        "beta": beta.tolist(),
    }


def predict(model: dict, x: np.ndarray) -> np.ndarray:
    x_mean = np.asarray(model["x_mean"], dtype=float)
    x_scale = np.asarray(model["x_scale"], dtype=float)
    beta = np.asarray(model["beta"], dtype=float)
    zx = (x - x_mean) / x_scale
    predicted_z = np.column_stack((np.ones(len(zx)), zx)) @ beta
    return predicted_z * float(model["y_scale"]) + float(model["y_mean"])


def fit_arm_models(rows: list[dict], arm: str) -> dict:
    y = target_vector(rows, arm)
    return {
        "baseline": fit_linear(baseline_matrix(rows, arm), y),
        "transfer": fit_linear(transfer_matrix(rows, arm, "correct"), y),
    }


def add_predictions(rows: list[dict], arm: str, models: dict) -> list[dict]:
    actual = target_vector(rows, arm)
    baseline = predict(models["baseline"], baseline_matrix(rows, arm))
    transfer = predict(models["transfer"], transfer_matrix(rows, arm, "correct"))
    wrong = predict(models["transfer"], transfer_matrix(rows, arm, "wrong"))
    output: list[dict] = []
    for index, source in enumerate(rows):
        item = dict(source)
        item.update({
            "arm": arm,
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


def sequence_metrics(rows: list[dict], arm: str, models: dict) -> list[dict]:
    scored = add_predictions(rows, arm, models)
    output: list[dict] = []
    for _, sequence in sorted(grouped(scored).items()):
        actual = target_vector(sequence, arm)
        reversed_source = source_values(sequence, arm, "correct")[::-1]
        reverse_x = np.column_stack((baseline_matrix(sequence, arm), reversed_source))
        reverse_prediction = predict(models["transfer"], reverse_x)
        item = {
            "split": sequence[0]["split"],
            "run": sequence[0]["run"],
            "period": sequence[0]["period"],
            "field_G": float(sequence[0]["field_G"]),
            "arm": arm,
            "scored_rows": len(sequence),
            "baseline_mse": float(np.mean([row["baseline_sq_error"] for row in sequence])),
            "transfer_mse": float(np.mean([row["transfer_sq_error"] for row in sequence])),
            "wrong_mse": float(np.mean([row["wrong_sq_error"] for row in sequence])),
            "reverse_mse": float(np.mean((reverse_prediction - actual) ** 2)),
        }
        item["baseline_minus_transfer"] = item["baseline_mse"] - item["transfer_mse"]
        item["wrong_minus_transfer"] = item["wrong_mse"] - item["transfer_mse"]
        item["reverse_minus_transfer"] = item["reverse_mse"] - item["transfer_mse"]
        output.append(item)
    return output


def field_values(sequence_rows: list[dict], key: str) -> dict[float, float]:
    output = {}
    for field in sorted({float(row["field_G"]) for row in sequence_rows}):
        values = [float(row[key]) for row in sequence_rows if float(row["field_G"]) == field]
        output[field] = float(np.median(values))
    return output


def aggregate(sequence_rows: list[dict], key: str) -> float:
    values = list(field_values(sequence_rows, key).values())
    return float(np.median(values)) if values else float("nan")


def bootstrap_interval(values: dict[float, float], seed: int) -> tuple[float, float, float]:
    data = np.asarray([values[field] for field in sorted(values)], dtype=float)
    if len(data) == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    draws = rng.choice(data, size=(BOOTSTRAPS, len(data)), replace=True)
    medians = np.median(draws, axis=1)
    return (
        float(np.median(data)),
        float(np.percentile(medians, 2.5)),
        float(np.percentile(medians, 97.5)),
    )


def shifted_null(rows: list[dict], arm: str, models: dict) -> np.ndarray:
    groups = grouped(rows)
    rng = np.random.default_rng(SEED + (0 if arm == "U_to_R" else 10000))
    draws = np.empty(SHIFT_DRAWS, dtype=float)
    for draw in range(SHIFT_DRAWS):
        sequence_errors: list[dict] = []
        for _, sequence in sorted(groups.items()):
            length = len(sequence)
            candidates = np.arange(2, max(3, length - 1), dtype=int)
            shift = int(rng.choice(candidates)) if len(candidates) else 1
            shifted = np.roll(source_values(sequence, arm, "correct"), shift, axis=0)
            x = np.column_stack((baseline_matrix(sequence, arm), shifted))
            prediction = predict(models["transfer"], x)
            error = float(np.mean((prediction - target_vector(sequence, arm)) ** 2))
            sequence_errors.append({"field_G": float(sequence[0]["field_G"]), "mse": error})
        draws[draw] = aggregate(sequence_errors, "mse")
    return draws


def empirical_lower_p(null: np.ndarray, observed: float) -> float:
    return float((1 + np.count_nonzero(null <= observed)) / (1 + len(null)))


def summarize_arm(stage: str, rows: list[dict], arm: str, models: dict) -> tuple[dict, list[dict], list[dict], np.ndarray]:
    scored = add_predictions(rows, arm, models)
    sequences = sequence_metrics(rows, arm, models)
    added = bootstrap_interval(field_values(sequences, "baseline_minus_transfer"), SEED + 1)
    wrong = bootstrap_interval(field_values(sequences, "wrong_minus_transfer"), SEED + 2)
    reverse = bootstrap_interval(field_values(sequences, "reverse_minus_transfer"), SEED + 3)
    shift = shifted_null(rows, arm, models)
    observed = aggregate(sequences, "transfer_mse")
    shift_p = empirical_lower_p(shift, observed)
    periods = {}
    for period in ("RF on", "RF off"):
        selected = [row["baseline_minus_transfer"] for row in sequences if row["period"] == period]
        periods[period] = float(np.median(selected)) if selected else float("nan")
    result = {
        "arm": arm,
        "stage": stage,
        "prediction_rows": len(rows),
        "errors": {
            "baseline_mse": aggregate(sequences, "baseline_mse"),
            "transfer_mse": observed,
            "wrong_frequency_mse": aggregate(sequences, "wrong_mse"),
            "reverse_mse": aggregate(sequences, "reverse_mse"),
        },
        "effects": {
            "baseline_minus_transfer": {"median": added[0], "ci95": [added[1], added[2]]},
            "wrong_minus_transfer": {"median": wrong[0], "ci95": [wrong[1], wrong[2]]},
            "reverse_minus_transfer": {"median": reverse[0], "ci95": [reverse[1], reverse[2]]},
            "rf_baseline_minus_transfer": periods,
            "shift": {
                "observed_transfer_mse": observed,
                "null_median": float(np.median(shift)),
                "empirical_p": shift_p,
            },
        },
        "passes": {
            "added_information": bool(added[1] > 0.0),
            "timing_specificity": bool(shift_p < 0.05),
            "frequency_specificity": bool(wrong[1] > 0.0),
            "direction_specificity": bool(reverse[1] > 0.0),
            "rf_robustness": bool(all(value > 0.0 for value in periods.values())),
        },
    }
    return result, scored, sequences, shift


def lag_diagnostic(stage: str, timeline: list[dict], lag_models: dict) -> list[dict]:
    output: list[dict] = []
    for horizon in DIAGNOSTIC_HORIZONS:
        rows, _ = build_prediction_rows(timeline, horizon)
        for arm in ARMS:
            models = lag_models[str(horizon)][arm]
            sequences = sequence_metrics(rows, arm, models)
            baseline = aggregate(sequences, "baseline_mse")
            transfer = aggregate(sequences, "transfer_mse")
            output.append({
                "split": stage,
                "arm": arm,
                "horizon_reads": horizon,
                "horizon_native_bins": horizon * t416.PATH_STEP,
                "horizon_us_median": float(np.median([row["horizon_us"] for row in rows])),
                "shared_native_bins": max(0, t416.PATH_WINDOW - horizon * t416.PATH_STEP),
                "overlapping_histories": int(horizon < PRIMARY_HORIZON),
                "prediction_rows": len(rows),
                "baseline_mse": baseline,
                "transfer_mse": transfer,
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
    if stage == "development":
        primary_models = {arm: fit_arm_models(primary_rows, arm) for arm in ARMS}
        lag_models = {}
        for horizon in DIAGNOSTIC_HORIZONS:
            lag_rows, _ = build_prediction_rows(timeline, horizon)
            lag_models[str(horizon)] = {arm: fit_arm_models(lag_rows, arm) for arm in ARMS}
    else:
        if not FREEZE.exists():
            raise FileNotFoundError("T419 development freeze missing")
        frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
        for key, current in (
            ("protocol_sha256", sha256(PROTOCOL)),
            ("analysis_sha256", sha256(Path(__file__).resolve())),
        ):
            if frozen[key] != current:
                raise RuntimeError(f"{stage} refused: frozen {key} mismatch")
        primary_models = frozen["primary_models"]
        lag_models = frozen["lag_models"]

    arm_results = {}
    scored_rows: list[dict] = []
    sequence_rows: list[dict] = []
    shift_rows: list[dict] = []
    for arm in ARMS:
        result, scored, sequences, shift = summarize_arm(stage, primary_rows, arm, primary_models[arm])
        arm_results[arm] = result
        scored_rows.extend(scored)
        sequence_rows.extend(sequences)
        shift_rows.extend({"arm": arm, "draw": i, "shifted_transfer_mse": float(value)} for i, value in enumerate(shift))

    total_sequences = len(eligibility)
    eligible_sequences = int(sum(int(row["eligible"]) for row in eligibility))
    availability = eligible_sequences / max(total_sequences, 1)
    gates = {
        "G1_availability": {
            "pass": bool(availability >= 0.75),
            "value": availability,
            "threshold": ">=0.75 of run/period histories with >=8 non-overlap pairs",
        },
        "G2_bidirectional_added_information": {
            "pass": bool(all(arm_results[arm]["passes"]["added_information"] for arm in ARMS)),
            "arms": {arm: arm_results[arm]["passes"]["added_information"] for arm in ARMS},
        },
        "G3_bidirectional_timing_specificity": {
            "pass": bool(all(arm_results[arm]["passes"]["timing_specificity"] for arm in ARMS)),
            "arms": {arm: arm_results[arm]["passes"]["timing_specificity"] for arm in ARMS},
        },
        "G4_bidirectional_frequency_specificity": {
            "pass": bool(all(arm_results[arm]["passes"]["frequency_specificity"] for arm in ARMS)),
            "arms": {arm: arm_results[arm]["passes"]["frequency_specificity"] for arm in ARMS},
        },
        "G5_bidirectional_direction_specificity": {
            "pass": bool(all(arm_results[arm]["passes"]["direction_specificity"] for arm in ARMS)),
            "arms": {arm: arm_results[arm]["passes"]["direction_specificity"] for arm in ARMS},
        },
        "G6_rf_robustness": {
            "pass": bool(all(arm_results[arm]["passes"]["rf_robustness"] for arm in ARMS)),
            "arms": {arm: arm_results[arm]["passes"]["rf_robustness"] for arm in ARMS},
        },
    }
    lag_rows = lag_diagnostic(stage, timeline, lag_models)
    result = {
        "test": "T419 direct dynamic Irrationality Di-ARA handover",
        "stage": stage,
        "identity": "muoniated-acetone detector-population spin relation",
        "primary_horizon": {
            "reads": PRIMARY_HORIZON,
            "native_bins": PRIMARY_HORIZON * t416.PATH_STEP,
            "median_us": float(np.median([row["horizon_us"] for row in primary_rows])),
            "shared_native_bins": 0,
        },
        "run_count": len(manifest),
        "run_period_sequences": total_sequences,
        "eligible_sequences": eligible_sequences,
        "availability_fraction": availability,
        "timeline_rows": len(timeline),
        "primary_prediction_rows": len(primary_rows),
        "arms": arm_results,
        "gates": gates,
        "stage_supported": bool(all(item["pass"] for item in gates.values())),
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(Path(__file__).resolve()),
        "source_hashes": {
            row["run"]: sha256(t416.t414.RAW / f"{row['run']}.nxs")
            for row in manifest
        },
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    prefix = f"T419_{stage.upper()}"
    write_csv(RESULTS / f"{prefix}_TIMELINE.csv", timeline)
    write_csv(RESULTS / f"{prefix}_PREDICTION_ROWS.csv", scored_rows)
    write_csv(RESULTS / f"{prefix}_SEQUENCE_ELIGIBILITY.csv", eligibility)
    write_csv(RESULTS / f"{prefix}_SEQUENCE_METRICS.csv", sequence_rows)
    write_csv(RESULTS / f"{prefix}_SHIFT_NULL.csv", shift_rows)
    write_csv(RESULTS / f"{prefix}_LAG_DIAGNOSTICS.csv", lag_rows)
    write_json(RESULTS / f"{prefix}_RESULTS.json", result)

    if stage == "development":
        write_json(FREEZE, {
            "test": result["test"],
            "frozen_after_development_before_validation_and_holdout": True,
            "protocol_sha256": result["protocol_sha256"],
            "analysis_sha256": result["analysis_sha256"],
            "constants": {
                "primary_horizon_reads": PRIMARY_HORIZON,
                "diagnostic_horizons": list(DIAGNOSTIC_HORIZONS),
                "minimum_primary_rows": MIN_PRIMARY_ROWS,
                "history_native_bins": t416.PATH_WINDOW,
                "path_step_native_bins": t416.PATH_STEP,
                "shift_draws": SHIFT_DRAWS,
                "bootstraps": BOOTSTRAPS,
                "seed": SEED,
            },
            "primary_models": primary_models,
            "lag_models": lag_models,
            "development_result": result,
        })
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "validation", "holdout"), required=True)
    args = parser.parse_args()
    run_stage(args.stage)


if __name__ == "__main__":
    main()

