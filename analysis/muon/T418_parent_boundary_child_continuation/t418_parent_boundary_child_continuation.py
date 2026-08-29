#!/usr/bin/env python3
"""T418 parent-boundary child continuation in the muon Irrationality Di-ARA."""

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
PROTOCOL = HERE / "T418_FROZEN_PROTOCOL.md"
RESULTS = HERE / "results"
FREEZE = HERE / "T418_DEVELOPMENT_FREEZE.json"

sys.path.insert(0, str(T416_DIR))
import t416_dual_irrationality_time_tracking as t416  # noqa: E402


SEED = 418
HORIZON_READS = 4
MIN_SEQUENCE_ROWS = 4
SHIFT_DRAWS = 1000
BOOTSTRAPS = 10000
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
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def child_metrics(phase_history: np.ndarray) -> dict:
    parent_i, local_loss, null_loss = t416.stochastic_residual(phase_history)
    rho, _ = t416.closure_history(phase_history)
    denominator = local_loss + null_loss
    q = local_loss / max(null_loss, EPS)
    child = 1.0 if denominator <= EPS else 2.0 * local_loss / denominator
    return {
        "parent_I": float(parent_i),
        "local_loss": float(local_loss),
        "null_loss": float(null_loss),
        "raw_q": float(q),
        "child_x": float(child),
        "child_anti_x": float(2.0 - child),
        "R": float(2.0 * np.median(rho)),
    }


def analyse_run_period(row: dict, period: str) -> list[dict]:
    data = t416.t414.load_run(row)
    period_index = 0 if period == "RF on" else 1
    counts = data["counts"][period_index]
    time = data["time"]
    frequency = t416.GAMMA_MHZ_PER_G * float(row["field_G"])
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

    start = max(t416.PATH_WINDOW - 1, cycle_bins)
    timeline: list[dict] = []
    for end in range(start, len(correct["time"]), t416.PATH_STEP):
        history = correct["phase"][end - t416.PATH_WINDOW + 1 : end + 1]
        measured = child_metrics(history)
        wrong_children = []
        for path in wrong_paths:
            wrong_history = path["phase"][end - t416.PATH_WINDOW + 1 : end + 1]
            wrong_children.append(child_metrics(wrong_history)["child_x"])
        x_l, x_c = t416.state_coordinates(correct["radius"], correct["phase"], end, cycle_bins)
        parent = 2.0 * (1.0 - math.exp(-float(correct["time"][end]) / t416.TAU_US))
        amount = 0.5 * (measured["R"] + measured["parent_I"])
        balance = 1.0 + (
            (measured["parent_I"] - measured["R"])
            / (measured["parent_I"] + measured["R"] + EPS)
        )
        timeline.append({
            "split": row["split"],
            "run": row["run"],
            "period": period,
            "field_G": float(row["field_G"]),
            "time_us": float(correct["time"][end]),
            "parent_ARA": parent,
            "state_x_L": float(x_l),
            "state_x_C": float(x_c),
            "spin_radius": float(correct["radius"][end]),
            "rational_closure_R": measured["R"],
            "irrational_parent_I": measured["parent_I"],
            "coupled_amount_A": amount,
            "coupled_balance_B": balance,
            "local_loss": measured["local_loss"],
            "null_loss": measured["null_loss"],
            "raw_loss_ratio_q": measured["raw_q"],
            "child_x": measured["child_x"],
            "child_anti_x": measured["child_anti_x"],
            "wrong_frequency_child_x": float(np.median(wrong_children)),
            "cycle_bins": cycle_bins,
        })
    return timeline


def grouped(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    output: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        output.setdefault((str(row["run"]), str(row["period"])), []).append(row)
    for key in output:
        output[key].sort(key=lambda item: float(item["time_us"]))
    return output


def build_prediction_rows(timeline: list[dict]) -> tuple[list[dict], list[dict]]:
    accepted: list[dict] = []
    sequence_summary: list[dict] = []
    for key, rows in sorted(grouped(timeline).items()):
        candidates: list[dict] = []
        child = np.asarray([float(row["child_x"]) for row in rows], dtype=float)
        wrong = np.asarray([float(row["wrong_frequency_child_x"]) for row in rows], dtype=float)
        q = np.asarray([float(row["raw_loss_ratio_q"]) for row in rows], dtype=float)
        for index in range(1, len(rows) - HORIZON_READS):
            if q[index] < 1.0:
                continue
            source = rows[index]
            future = rows[index + HORIZON_READS]
            candidates.append({
                "split": source["split"],
                "run": source["run"],
                "period": source["period"],
                "field_G": float(source["field_G"]),
                "time_us": float(source["time_us"]),
                "future_time_us": float(future["time_us"]),
                "parent_ARA": float(source["parent_ARA"]),
                "R": float(source["rational_closure_R"]),
                "state_x_L": float(source["state_x_L"]),
                "state_x_C": float(source["state_x_C"]),
                "child_x": float(child[index]),
                "child_dx": float(child[index] - child[index - 1]),
                "wrong_child_x": float(wrong[index]),
                "wrong_child_dx": float(wrong[index] - wrong[index - 1]),
                "future_state_x_L": float(future["state_x_L"]),
                "future_state_x_C": float(future["state_x_C"]),
            })
        first = rows[0]
        eligible = len(candidates) >= MIN_SEQUENCE_ROWS
        sequence_summary.append({
            "split": first["split"],
            "run": first["run"],
            "period": first["period"],
            "field_G": float(first["field_G"]),
            "timeline_rows": len(rows),
            "post_boundary_prediction_rows": len(candidates),
            "eligible": int(eligible),
            "first_q": float(q[0]),
            "last_q": float(q[-1]),
            "median_post_boundary_child_x": (
                float(np.median([row["child_x"] for row in candidates]))
                if candidates else float("nan")
            ),
        })
        if eligible:
            accepted.extend(candidates)
    return accepted, sequence_summary


def base_matrix(rows: list[dict]) -> np.ndarray:
    return np.asarray([
        [row["parent_ARA"], row["R"], row["state_x_L"], row["state_x_C"]]
        for row in rows
    ], dtype=float)


def child_matrix(rows: list[dict], source: str = "target") -> np.ndarray:
    base = base_matrix(rows)
    if source == "target":
        extra = np.asarray([[row["child_x"], row["child_dx"]] for row in rows], dtype=float)
    elif source == "wrong":
        extra = np.asarray([[row["wrong_child_x"], row["wrong_child_dx"]] for row in rows], dtype=float)
    else:
        raise ValueError(source)
    return np.column_stack((base, extra))


def target_matrix(rows: list[dict]) -> np.ndarray:
    return np.asarray([
        [row["future_state_x_L"], row["future_state_x_C"]]
        for row in rows
    ], dtype=float)


def fit_linear(x: np.ndarray, y: np.ndarray) -> dict:
    x_mean = np.mean(x, axis=0)
    x_scale = np.std(x, axis=0)
    x_scale[x_scale < EPS] = 1.0
    y_mean = np.mean(y, axis=0)
    y_scale = np.std(y, axis=0)
    y_scale[y_scale < EPS] = 1.0
    zx = (x - x_mean) / x_scale
    zy = (y - y_mean) / y_scale
    design = np.column_stack((np.ones(len(zx)), zx))
    beta = np.linalg.lstsq(design, zy, rcond=None)[0]
    return {
        "x_mean": x_mean.tolist(),
        "x_scale": x_scale.tolist(),
        "y_mean": y_mean.tolist(),
        "y_scale": y_scale.tolist(),
        "beta": beta.tolist(),
    }


def predict(model: dict, x: np.ndarray) -> np.ndarray:
    x_mean = np.asarray(model["x_mean"], dtype=float)
    x_scale = np.asarray(model["x_scale"], dtype=float)
    y_mean = np.asarray(model["y_mean"], dtype=float)
    y_scale = np.asarray(model["y_scale"], dtype=float)
    beta = np.asarray(model["beta"], dtype=float)
    zx = (x - x_mean) / x_scale
    predicted_z = np.column_stack((np.ones(len(zx)), zx)) @ beta
    return predicted_z * y_scale + y_mean


def row_error(predicted: np.ndarray, actual: np.ndarray) -> np.ndarray:
    return np.mean((predicted - actual) ** 2, axis=1)


def add_predictions(rows: list[dict], models: dict) -> list[dict]:
    actual = target_matrix(rows)
    base_prediction = predict(models["baseline"], base_matrix(rows))
    child_prediction = predict(models["child"], child_matrix(rows, "target"))
    wrong_prediction = predict(models["child"], child_matrix(rows, "wrong"))

    output: list[dict] = []
    for index, source in enumerate(rows):
        item = dict(source)
        item.update({
            "baseline_pred_x_L": float(base_prediction[index, 0]),
            "baseline_pred_x_C": float(base_prediction[index, 1]),
            "child_pred_x_L": float(child_prediction[index, 0]),
            "child_pred_x_C": float(child_prediction[index, 1]),
            "wrong_pred_x_L": float(wrong_prediction[index, 0]),
            "wrong_pred_x_C": float(wrong_prediction[index, 1]),
            "baseline_error": float(row_error(base_prediction[index:index+1], actual[index:index+1])[0]),
            "child_error": float(row_error(child_prediction[index:index+1], actual[index:index+1])[0]),
            "wrong_error": float(row_error(wrong_prediction[index:index+1], actual[index:index+1])[0]),
        })
        output.append(item)
    return output


def sequence_metric_rows(prediction_rows: list[dict], models: dict) -> list[dict]:
    scored = add_predictions(prediction_rows, models)
    output: list[dict] = []
    for key, rows in sorted(grouped(scored).items()):
        actual = target_matrix(rows)
        child_values = np.asarray([[row["child_x"], row["child_dx"]] for row in rows], dtype=float)
        reversed_values = child_values[::-1]
        reverse_x = np.column_stack((base_matrix(rows), reversed_values))
        reverse_prediction = predict(models["child"], reverse_x)
        output.append({
            "split": rows[0]["split"],
            "run": rows[0]["run"],
            "period": rows[0]["period"],
            "field_G": float(rows[0]["field_G"]),
            "scored_rows": len(rows),
            "baseline_mse": float(np.mean([row["baseline_error"] for row in rows])),
            "child_mse": float(np.mean([row["child_error"] for row in rows])),
            "wrong_mse": float(np.mean([row["wrong_error"] for row in rows])),
            "reverse_mse": float(np.mean(row_error(reverse_prediction, actual))),
        })
    for row in output:
        row["baseline_minus_child"] = row["baseline_mse"] - row["child_mse"]
        row["wrong_minus_child"] = row["wrong_mse"] - row["child_mse"]
        row["reverse_minus_child"] = row["reverse_mse"] - row["child_mse"]
    return output


def field_values(sequence_rows: list[dict], key: str) -> dict[float, float]:
    output = {}
    for field in sorted({float(row["field_G"]) for row in sequence_rows}):
        values = [float(row[key]) for row in sequence_rows if float(row["field_G"]) == field]
        output[field] = float(np.median(values))
    return output


def bootstrap_interval(values: dict[float, float], seed: int) -> tuple[float, float, float]:
    data = np.asarray([values[field] for field in sorted(values)], dtype=float)
    if len(data) == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    draws = rng.choice(data, size=(BOOTSTRAPS, len(data)), replace=True)
    medians = np.median(draws, axis=1)
    return float(np.median(data)), float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))


def aggregate_mse(sequence_rows: list[dict], key: str) -> float:
    return float(np.median(list(field_values(sequence_rows, key).values())))


def shifted_null(prediction_rows: list[dict], models: dict) -> np.ndarray:
    groups = grouped(prediction_rows)
    keys = sorted(groups)
    rng = np.random.default_rng(SEED)
    draws = np.empty(SHIFT_DRAWS, dtype=float)
    for draw in range(SHIFT_DRAWS):
        sequence_errors: list[dict] = []
        for key in keys:
            rows = groups[key]
            length = len(rows)
            candidates = np.arange(2, max(3, length - 1), dtype=int)
            shift = int(rng.choice(candidates)) if len(candidates) else 1
            child_values = np.asarray([[row["child_x"], row["child_dx"]] for row in rows], dtype=float)
            shifted = np.roll(child_values, shift, axis=0)
            x = np.column_stack((base_matrix(rows), shifted))
            predicted = predict(models["child"], x)
            error = float(np.mean(row_error(predicted, target_matrix(rows))))
            sequence_errors.append({
                "field_G": float(rows[0]["field_G"]),
                "mse": error,
            })
        draws[draw] = aggregate_mse(sequence_errors, "mse")
    return draws


def empirical_lower_p(null: np.ndarray, observed: float) -> float:
    return float((1 + np.count_nonzero(null <= observed)) / (1 + len(null)))


def summarize_stage(
    stage: str,
    timeline: list[dict],
    prediction_rows: list[dict],
    eligibility: list[dict],
    sequence_rows: list[dict],
    models: dict,
) -> tuple[dict, np.ndarray]:
    baseline_effect = bootstrap_interval(field_values(sequence_rows, "baseline_minus_child"), SEED + 1)
    wrong_effect = bootstrap_interval(field_values(sequence_rows, "wrong_minus_child"), SEED + 2)
    reverse_effect = bootstrap_interval(field_values(sequence_rows, "reverse_minus_child"), SEED + 3)
    shift = shifted_null(prediction_rows, models)
    observed_child_mse = aggregate_mse(sequence_rows, "child_mse")
    shift_p = empirical_lower_p(shift, observed_child_mse)
    periods = {}
    for period in ("RF on", "RF off"):
        values = [float(row["baseline_minus_child"]) for row in sequence_rows if row["period"] == period]
        periods[period] = float(np.median(values)) if values else float("nan")

    total_sequences = len(eligibility)
    eligible_sequences = int(sum(int(row["eligible"]) for row in eligibility))
    availability = eligible_sequences / max(total_sequences, 1)
    post_rows = [row for row in timeline if float(row["raw_loss_ratio_q"]) >= 1.0]
    child_values = np.asarray([float(row["child_x"]) for row in post_rows], dtype=float)
    null_values = np.asarray([float(row["null_loss"]) for row in timeline], dtype=float)
    gates = {
        "G1_availability": {
            "pass": bool(availability >= 0.75),
            "value": availability,
            "threshold": ">=0.75 of run/period sequences with >=4 post-boundary origins",
        },
        "G2_added_future_state_information": {
            "pass": bool(baseline_effect[1] > 0.0),
            "value": baseline_effect[0],
            "ci95": [baseline_effect[1], baseline_effect[2]],
            "threshold": "field-bootstrap lower 95% bound for baseline-child MSE >0",
        },
        "G3_timing_specificity": {
            "pass": bool(shift_p < 0.05),
            "value": observed_child_mse,
            "empirical_p": shift_p,
            "null_median": float(np.median(shift)),
            "threshold": "observed child MSE below at least 95% of circular shifts",
        },
        "G4_frequency_specificity": {
            "pass": bool(wrong_effect[1] > 0.0),
            "value": wrong_effect[0],
            "ci95": [wrong_effect[1], wrong_effect[2]],
            "threshold": "field-bootstrap lower 95% bound for wrong-child MSE >0",
        },
        "G5_direction_specificity": {
            "pass": bool(reverse_effect[1] > 0.0),
            "value": reverse_effect[0],
            "ci95": [reverse_effect[1], reverse_effect[2]],
            "threshold": "field-bootstrap lower 95% bound for reverse-child MSE >0",
        },
        "G6_rf_robustness": {
            "pass": bool(all(value > 0.0 for value in periods.values())),
            "values": periods,
            "threshold": "median baseline-child MSE >0 in RF-on and RF-off",
        },
    }
    result = {
        "test": "T418 parent-boundary child continuation",
        "stage": stage,
        "boundary": "population spin identity; post-T417 locked reanalysis",
        "run_count": len({row["run"] for row in eligibility}),
        "run_period_sequences": total_sequences,
        "eligible_sequences": eligible_sequences,
        "availability_fraction": availability,
        "timeline_rows": len(timeline),
        "prediction_rows": len(prediction_rows),
        "parent_boundary_rows": len(post_rows),
        "child_post_boundary": {
            "median": float(np.median(child_values)) if len(child_values) else float("nan"),
            "q10": float(np.percentile(child_values, 10)) if len(child_values) else float("nan"),
            "q90": float(np.percentile(child_values, 90)) if len(child_values) else float("nan"),
            "maximum": float(np.max(child_values)) if len(child_values) else float("nan"),
        },
        "null_loss_quality": {
            "minimum": float(np.min(null_values)),
            "median": float(np.median(null_values)),
            "fraction_le_1e12": float(np.mean(null_values <= EPS)),
        },
        "errors": {
            "baseline_mse": aggregate_mse(sequence_rows, "baseline_mse"),
            "child_mse": observed_child_mse,
            "wrong_frequency_mse": aggregate_mse(sequence_rows, "wrong_mse"),
            "reverse_mse": aggregate_mse(sequence_rows, "reverse_mse"),
        },
        "gates": gates,
        "stage_supported": bool(all(item["pass"] for item in gates.values())),
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(Path(__file__).resolve()),
    }
    return result, shift


def run_stage(stage: str) -> None:
    manifest = [row for row in t416.t414.read_manifest() if row["split"] == stage]
    if not manifest:
        raise ValueError(f"no source rows for stage {stage}")
    timeline: list[dict] = []
    for index, row in enumerate(manifest, start=1):
        print(f"{stage}: {index}/{len(manifest)} {row['run']} {row['field_G']:.0f} G", flush=True)
        for period in ("RF on", "RF off"):
            timeline.extend(analyse_run_period(row, period))
    prediction_rows, eligibility = build_prediction_rows(timeline)

    if stage == "development":
        models = {
            "baseline": fit_linear(base_matrix(prediction_rows), target_matrix(prediction_rows)),
            "child": fit_linear(child_matrix(prediction_rows, "target"), target_matrix(prediction_rows)),
        }
    else:
        if not FREEZE.exists():
            raise FileNotFoundError("T418 development freeze missing")
        frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
        for key, current in (
            ("protocol_sha256", sha256(PROTOCOL)),
            ("analysis_sha256", sha256(Path(__file__).resolve())),
        ):
            if frozen[key] != current:
                raise RuntimeError(f"{stage} refused: frozen {key} mismatch")
        models = frozen["models"]

    scored_rows = add_predictions(prediction_rows, models)
    sequence_rows = sequence_metric_rows(prediction_rows, models)
    result, shift = summarize_stage(stage, timeline, prediction_rows, eligibility, sequence_rows, models)
    result["source_hashes"] = {
        row["run"]: sha256(t416.t414.RAW / f"{row['run']}.nxs")
        for row in manifest
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    prefix = f"T418_{stage.upper()}"
    write_csv(RESULTS / f"{prefix}_TIMELINE.csv", timeline)
    write_csv(RESULTS / f"{prefix}_PREDICTION_ROWS.csv", scored_rows)
    write_csv(RESULTS / f"{prefix}_SEQUENCE_ELIGIBILITY.csv", eligibility)
    write_csv(RESULTS / f"{prefix}_SEQUENCE_METRICS.csv", sequence_rows)
    write_csv(RESULTS / f"{prefix}_SHIFT_NULL.csv", [
        {"draw": index, "shifted_child_mse": float(value)}
        for index, value in enumerate(shift)
    ])
    write_json(RESULTS / f"{prefix}_RESULTS.json", result)

    if stage == "development":
        write_json(FREEZE, {
            "test": result["test"],
            "frozen_after_development_before_validation_and_holdout": True,
            "protocol_sha256": result["protocol_sha256"],
            "analysis_sha256": result["analysis_sha256"],
            "constants": {
                "horizon_reads": HORIZON_READS,
                "minimum_sequence_rows": MIN_SEQUENCE_ROWS,
                "shift_draws": SHIFT_DRAWS,
                "bootstraps": BOOTSTRAPS,
                "seed": SEED,
                "path_window": t416.PATH_WINDOW,
                "path_step": t416.PATH_STEP,
            },
            "models": models,
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
