#!/usr/bin/env python3
"""T415 multichannel ARA state-array prediction.

Development and validation are deliberately separate stages. Validation will
refuse to run if the protocol, this script, or the inherited T414 loader has
changed since development was frozen.
"""

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
RESULTS = HERE / "results"
PROTOCOL = HERE / "T415_FROZEN_PROTOCOL.md"
FREEZE = HERE / "T415_DEVELOPMENT_FREEZE.json"
T414_DIR = HERE.parent / "T414_spin_child_lifespan_parent"
T414_SCRIPT = T414_DIR / "t414_spin_child_lifespan_parent.py"
sys.path.insert(0, str(T414_DIR))
import t414_spin_child_lifespan_parent as t414


TAU_US = 2.203
GAMMA_MHZ_PER_G = 0.013549
HORIZONS = (1, 4, 8)
PRIMARY_HORIZON = 4
LAMBDAS = (0.0, 1e-6, 1e-4, 1e-2, 1e-1, 1.0, 10.0, 100.0)
EARLY_MAX_US = 0.50
PREDICT_MIN_US = 0.50
WRONG_FREQUENCY_OFFSET_MHZ = 4.0 / 5.75
SEED = 415

FEATURES = {
    "M0 parent": ["parent", "parent2"],
    "M1 + spin": [
        "parent", "parent2", "spin_a", "spin_b", "parent_spin_a", "parent_spin_b",
    ],
    "M2 + strength": [
        "parent", "parent2", "spin_a", "spin_b", "parent_spin_a", "parent_spin_b",
        "strength", "strength_change", "strength_spin_a", "strength_spin_b",
    ],
    "M3 + environment": [
        "parent", "parent2", "spin_a", "spin_b", "parent_spin_a", "parent_spin_b",
        "strength", "strength_change", "strength_spin_a", "strength_spin_b",
        "field", "rf", "field_spin_a", "field_spin_b", "rf_spin_a", "rf_spin_b",
    ],
    "M4 full lock": [
        "parent", "parent2", "spin_a", "spin_b", "parent_spin_a", "parent_spin_b",
        "strength", "strength_change", "strength_spin_a", "strength_spin_b",
        "field", "rf", "field_spin_a", "field_spin_b", "rf_spin_a", "rf_spin_b",
        "lock_a", "lock_b", "parent_strength_change",
    ],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Cannot write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def period_arrays(row: dict, period: str) -> dict:
    data = t414.load_run(row)
    p_index = 0 if period == "RF on" else 1
    counts = np.asarray(data["counts"][p_index], dtype=float)
    frames = float(data["frames"][p_index])
    time = np.asarray(data["time"], dtype=float)
    total = counts.sum(axis=0)
    rate = total / frames
    early = (time >= t414.T_MIN) & (time < EARLY_MAX_US)
    if int(np.sum(early)) < 8:
        raise ValueError(f"Insufficient early reference bins for {row['run']} {period}")
    reference_rate = float(np.mean(rate[early]))
    if reference_rate <= 0:
        raise ValueError(f"Non-positive early rate for {row['run']} {period}")
    early_detector = counts[:, early].sum(axis=1)
    early_share = early_detector / max(float(np.sum(early_detector)), 1.0)
    share = counts / np.maximum(total[None, :], 1.0)
    strength = math.sqrt(counts.shape[0]) * np.linalg.norm(share.T - early_share[None, :], axis=1)
    strength_change = np.r_[0.0, np.diff(strength)]
    return {
        "time": time,
        "rate": rate,
        "reference_rate": reference_rate,
        "strength": strength,
        "strength_change": strength_change,
    }


def feature_values(parent: np.ndarray, spin_a: np.ndarray, spin_b: np.ndarray,
                   strength: np.ndarray, strength_change: np.ndarray,
                   field: float, rf: float) -> dict[str, np.ndarray]:
    return {
        "parent": parent,
        "parent2": parent**2,
        "spin_a": spin_a,
        "spin_b": spin_b,
        "parent_spin_a": parent * spin_a,
        "parent_spin_b": parent * spin_b,
        "strength": strength,
        "strength_change": strength_change,
        "strength_spin_a": strength * spin_a,
        "strength_spin_b": strength * spin_b,
        "field": np.full(len(parent), field, dtype=float),
        "rf": np.full(len(parent), rf, dtype=float),
        "field_spin_a": field * spin_a,
        "field_spin_b": field * spin_b,
        "rf_spin_a": rf * spin_a,
        "rf_spin_b": rf * spin_b,
        "lock_a": parent * strength * spin_a,
        "lock_b": parent * strength * spin_b,
        "parent_strength_change": parent * strength_change,
    }


def samples_for(rows: list[dict], horizon: int, control: str = "target") -> dict:
    records: list[dict] = []
    matrices: dict[str, list[np.ndarray]] = {name: [] for name in FEATURES}
    targets: list[np.ndarray] = []
    for row in rows:
        for period in ("RF on", "RF off"):
            data = period_arrays(row, period)
            time = data["time"]
            current_index = np.arange(len(time) - horizon)
            eligible = time[current_index] >= PREDICT_MIN_US
            current_index = current_index[eligible]
            target_index = current_index + horizon
            current_time = time[current_index]
            frequency = GAMMA_MHZ_PER_G * float(row["field_G"])
            if control == "wrong_frequency":
                frequency += WRONG_FREQUENCY_OFFSET_MHZ
            theta = 2.0 * np.pi * frequency * current_time
            spin_a = np.sin(theta)
            spin_b = np.cos(theta)
            strength = np.asarray(data["strength"], dtype=float)
            strength_change = np.asarray(data["strength_change"], dtype=float)
            if control == "broken_history":
                available = max(len(strength) - 128, 1)
                run_number = int(str(row["run"])[-5:])
                offset = 64 + ((run_number + (0 if period == "RF on" else 37)) % available)
                strength = np.roll(strength, offset)
                strength_change = np.roll(strength_change, offset)
            q = strength[current_index]
            dq = strength_change[current_index]
            parent = 2.0 * (1.0 - np.exp(-current_time / TAU_US))
            rf = 1.0 if period == "RF on" else 0.0
            values = feature_values(parent, spin_a, spin_b, q, dq, float(row["field_G"]), rf)
            for model, names in FEATURES.items():
                matrices[model].append(np.column_stack([values[name] for name in names]))
            target_rate = np.maximum(data["rate"][target_index], 1e-15)
            y = np.log(target_rate / float(data["reference_rate"]))
            targets.append(y)
            for local, (i_now, i_target) in enumerate(zip(current_index, target_index)):
                records.append({
                    "run": row["run"],
                    "split": row["split"],
                    "period": period,
                    "field_G": float(row["field_G"]),
                    "temperature_K": float(row["temperature_K"]),
                    "current_time_us": float(time[i_now]),
                    "target_time_us": float(time[i_target]),
                    "target_log_rate": float(y[local]),
                    "parent_ARA": float(parent[local]),
                    "spin_cut_A_ARA": float(1.0 + spin_a[local]),
                    "spin_cut_B_ARA": float(1.0 + spin_b[local]),
                    "strength": float(q[local]),
                    "strength_change": float(dq[local]),
                })
    return {
        "records": records,
        "y": np.concatenate(targets),
        "X": {model: np.vstack(parts) for model, parts in matrices.items()},
    }


def fit_ridge(x: np.ndarray, y: np.ndarray, lam: float) -> dict:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale[scale < 1e-12] = 1.0
    z = (x - mean) / scale
    design = np.column_stack((np.ones(len(z)), z))
    if lam == 0:
        beta = np.linalg.lstsq(design, y, rcond=None)[0]
    else:
        penalty = np.eye(design.shape[1])
        penalty[0, 0] = 0.0
        beta = np.linalg.solve(design.T @ design + lam * penalty, design.T @ y)
    return {
        "mean": mean,
        "scale": scale,
        "beta": beta,
        "lambda": float(lam),
    }


def predict(model: dict, x: np.ndarray) -> np.ndarray:
    z = (x - np.asarray(model["mean"], dtype=float)) / np.asarray(model["scale"], dtype=float)
    design = np.column_stack((np.ones(len(z)), z))
    return design @ np.asarray(model["beta"], dtype=float)


def field_rmse(records: list[dict], y: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    output: dict[str, float] = {}
    runs = sorted({record["run"] for record in records})
    for run in runs:
        mask = np.asarray([record["run"] == run for record in records], dtype=bool)
        output[run] = float(np.sqrt(np.mean((y[mask] - prediction[mask]) ** 2)))
    return output


def period_rmse(records: list[dict], y: np.ndarray, prediction: np.ndarray) -> dict[tuple[str, str], float]:
    output: dict[tuple[str, str], float] = {}
    keys = sorted({(record["run"], record["period"]) for record in records})
    for key in keys:
        mask = np.asarray([(record["run"], record["period"]) == key for record in records], dtype=bool)
        output[key] = float(np.sqrt(np.mean((y[mask] - prediction[mask]) ** 2)))
    return output


def choose_lambda(dataset: dict, model_name: str) -> tuple[float, list[dict]]:
    records = dataset["records"]
    x = dataset["X"][model_name]
    y = dataset["y"]
    runs = sorted({record["run"] for record in records})
    curve: list[dict] = []
    for lam in LAMBDAS:
        fold_rmse = []
        for run in runs:
            test = np.asarray([record["run"] == run for record in records], dtype=bool)
            fitted = fit_ridge(x[~test], y[~test], lam)
            pred = predict(fitted, x[test])
            fold_rmse.append(float(np.sqrt(np.mean((y[test] - pred) ** 2))))
        curve.append({
            "model": model_name,
            "lambda": float(lam),
            "median_leave_run_out_rmse": float(np.median(fold_rmse)),
            "mean_leave_run_out_rmse": float(np.mean(fold_rmse)),
        })
    best = min(curve, key=lambda row: (row["median_leave_run_out_rmse"], row["lambda"]))
    return float(best["lambda"]), curve


def serialise_model(model: dict, names: list[str]) -> dict:
    return {
        "features": names,
        "lambda": model["lambda"],
        "mean": np.asarray(model["mean"]).tolist(),
        "scale": np.asarray(model["scale"]).tolist(),
        "beta": np.asarray(model["beta"]).tolist(),
    }


def development() -> None:
    rows = [row for row in t414.read_manifest() if row["split"] == "development"]
    freeze_models: dict[str, dict] = {}
    cv_rows: list[dict] = []
    for horizon in HORIZONS:
        print(f"Preparing development horizon {horizon}", flush=True)
        dataset = samples_for(rows, horizon)
        freeze_models[str(horizon)] = {}
        for model_name, names in FEATURES.items():
            lam, curve = choose_lambda(dataset, model_name)
            cv_rows.extend({"horizon_bins": horizon, **row} for row in curve)
            fitted = fit_ridge(dataset["X"][model_name], dataset["y"], lam)
            freeze_models[str(horizon)][model_name] = serialise_model(fitted, names)
            print(f"  {model_name}: lambda={lam:g}", flush=True)
    source_hashes = {
        row["run"]: sha256(t414.RAW / f"{row['run']}.nxs")
        for row in rows
    }
    payload = {
        "test": "T415 multichannel ARA state array",
        "stage": "development frozen before validation",
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(Path(__file__).resolve()),
        "t414_loader_sha256": sha256(T414_SCRIPT),
        "tau_us": TAU_US,
        "gamma_MHz_per_G": GAMMA_MHZ_PER_G,
        "horizons_bins": list(HORIZONS),
        "primary_horizon_bins": PRIMARY_HORIZON,
        "development_runs": [row["run"] for row in rows],
        "source_hashes": source_hashes,
        "models": freeze_models,
    }
    FREEZE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_csv(RESULTS / "T415_DEVELOPMENT_CV.csv", cv_rows)
    print(FREEZE)


def load_frozen_model(data: dict) -> dict:
    return {
        "mean": np.asarray(data["mean"], dtype=float),
        "scale": np.asarray(data["scale"], dtype=float),
        "beta": np.asarray(data["beta"], dtype=float),
        "lambda": float(data["lambda"]),
    }


def validation() -> None:
    if not FREEZE.exists():
        raise FileNotFoundError("Run --stage development first")
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    expected = {
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(Path(__file__).resolve()),
        "t414_loader_sha256": sha256(T414_SCRIPT),
    }
    for key, value in expected.items():
        if frozen[key] != value:
            raise RuntimeError(f"Frozen {key} mismatch; validation refused")
    rows = [row for row in t414.read_manifest() if row["split"] == "validation"]
    all_field_rows: list[dict] = []
    all_period_rows: list[dict] = []
    summary_rows: list[dict] = []
    predictions_by_horizon: dict[int, dict] = {}
    for horizon in HORIZONS:
        print(f"Scoring validation horizon {horizon}", flush=True)
        dataset = samples_for(rows, horizon)
        predictions: dict[str, np.ndarray] = {}
        field_scores: dict[str, dict[str, float]] = {}
        period_scores: dict[str, dict[tuple[str, str], float]] = {}
        for model_name in FEATURES:
            model = load_frozen_model(frozen["models"][str(horizon)][model_name])
            pred = predict(model, dataset["X"][model_name])
            predictions[model_name] = pred
            field_scores[model_name] = field_rmse(dataset["records"], dataset["y"], pred)
            period_scores[model_name] = period_rmse(dataset["records"], dataset["y"], pred)
        baseline = field_scores["M0 parent"]
        for model_name in FEATURES:
            improvements = []
            for row in rows:
                run = row["run"]
                rmse = field_scores[model_name][run]
                improvement = 1.0 - rmse / baseline[run]
                improvements.append(improvement)
                all_field_rows.append({
                    "horizon_bins": horizon,
                    "horizon_us": horizon * 0.016,
                    "run": run,
                    "field_G": row["field_G"],
                    "model": model_name,
                    "rmse_log_rate": rmse,
                    "parent_rmse_log_rate": baseline[run],
                    "improvement_fraction": improvement,
                })
            summary_rows.append({
                "horizon_bins": horizon,
                "horizon_us": horizon * 0.016,
                "model": model_name,
                "median_field_improvement_fraction": float(np.median(improvements)),
                "mean_field_improvement_fraction": float(np.mean(improvements)),
                "field_wins": int(np.sum(np.asarray(improvements) > 0)),
                "field_count": len(improvements),
                "lambda": frozen["models"][str(horizon)][model_name]["lambda"],
            })
        base_period = period_scores["M0 parent"]
        for model_name in FEATURES:
            for key, rmse in period_scores[model_name].items():
                run, period = key
                row = next(item for item in rows if item["run"] == run)
                all_period_rows.append({
                    "horizon_bins": horizon,
                    "horizon_us": horizon * 0.016,
                    "run": run,
                    "field_G": row["field_G"],
                    "period": period,
                    "model": model_name,
                    "rmse_log_rate": rmse,
                    "parent_rmse_log_rate": base_period[key],
                    "improvement_fraction": 1.0 - rmse / base_period[key],
                })
        predictions_by_horizon[horizon] = {
            "dataset": dataset,
            "predictions": predictions,
            "field_scores": field_scores,
            "period_scores": period_scores,
        }

    # Frozen controls use the already-fitted primary M4 model.
    correct = predictions_by_horizon[PRIMARY_HORIZON]
    full_model = load_frozen_model(frozen["models"][str(PRIMARY_HORIZON)]["M4 full lock"])
    control_rows: list[dict] = []
    control_field_rows: list[dict] = []
    for control in ("wrong_frequency", "broken_history"):
        control_data = samples_for(rows, PRIMARY_HORIZON, control=control)
        control_pred = predict(full_model, control_data["X"]["M4 full lock"])
        scores = field_rmse(control_data["records"], control_data["y"], control_pred)
        base = correct["field_scores"]["M0 parent"]
        improvements = []
        for row in rows:
            run = row["run"]
            improvement = 1.0 - scores[run] / base[run]
            improvements.append(improvement)
            control_field_rows.append({
                "control": control,
                "run": run,
                "field_G": row["field_G"],
                "rmse_log_rate": scores[run],
                "parent_rmse_log_rate": base[run],
                "improvement_fraction": improvement,
            })
        control_rows.append({
            "control": control,
            "median_field_rmse_log_rate": float(np.median(list(scores.values()))),
            "median_field_improvement_fraction": float(np.median(improvements)),
            "field_wins": int(np.sum(np.asarray(improvements) > 0)),
            "field_count": len(improvements),
        })

    primary_summary = next(
        row for row in summary_rows
        if row["horizon_bins"] == PRIMARY_HORIZON and row["model"] == "M4 full lock"
    )
    primary_periods = [
        row for row in all_period_rows
        if row["horizon_bins"] == PRIMARY_HORIZON and row["model"] == "M4 full lock"
    ]
    period_medians = {
        period: float(np.median([row["improvement_fraction"] for row in primary_periods if row["period"] == period]))
        for period in ("RF on", "RF off")
    }
    correct_rmse = float(np.median(list(correct["field_scores"]["M4 full lock"].values())))
    controls_by_name = {row["control"]: row for row in control_rows}
    gates = {
        "median_improvement_positive": primary_summary["median_field_improvement_fraction"] > 0,
        "at_least_10_of_13_fields_improve": primary_summary["field_wins"] >= 10,
        "beats_wrong_frequency_control": correct_rmse < controls_by_name["wrong_frequency"]["median_field_rmse_log_rate"],
        "beats_broken_history_control": correct_rmse < controls_by_name["broken_history"]["median_field_rmse_log_rate"],
        "both_rf_period_medians_positive": all(value > 0 for value in period_medians.values()),
    }
    gates["full_array_supported"] = all(gates.values())

    # Fixed 284 G profile for a reader-visible trajectory.
    primary_data = correct["dataset"]
    records = primary_data["records"]
    example_mask = np.asarray([
        record["field_G"] == 284.0 and record["period"] == "RF on"
        for record in records
    ], dtype=bool)
    profile_rows: list[dict] = []
    for record, observed, p0, p4 in zip(
        np.asarray(records, dtype=object)[example_mask],
        primary_data["y"][example_mask],
        correct["predictions"]["M0 parent"][example_mask],
        correct["predictions"]["M4 full lock"][example_mask],
    ):
        profile_rows.append({
            "target_time_us": record["target_time_us"],
            "observed_normalized_rate": float(np.exp(observed)),
            "parent_prediction": float(np.exp(p0)),
            "full_array_prediction": float(np.exp(p4)),
            "parent_ARA": record["parent_ARA"],
            "spin_cut_A_ARA": record["spin_cut_A_ARA"],
            "spin_cut_B_ARA": record["spin_cut_B_ARA"],
            "strength": record["strength"],
        })

    # Descriptive ten-bin relation between current strength and future residual.
    residual = primary_data["y"] - correct["predictions"]["M0 parent"]
    strength = np.asarray([record["strength"] for record in records], dtype=float)
    edges = np.quantile(strength, np.linspace(0, 1, 11))
    edges = np.maximum.accumulate(edges)
    strength_rows: list[dict] = []
    for index in range(10):
        if index == 9:
            mask = (strength >= edges[index]) & (strength <= edges[index + 1])
        else:
            mask = (strength >= edges[index]) & (strength < edges[index + 1])
        values = residual[mask]
        strength_rows.append({
            "strength_decile": index + 1,
            "mean_strength": float(np.mean(strength[mask])),
            "mean_future_parent_residual": float(np.mean(values)),
            "se_future_parent_residual": float(np.std(values, ddof=1) / math.sqrt(len(values))),
            "sample_bins": int(len(values)),
        })

    source_hashes = {
        row["run"]: sha256(t414.RAW / f"{row['run']}.nxs")
        for row in rows
    }
    result = {
        "test": "T415 multichannel ARA state array",
        "stage": "validation scored after development freeze",
        "boundary": "ensemble release-profile prediction; not individual muon/neutrino timing",
        "protocol_sha256": frozen["protocol_sha256"],
        "analysis_sha256": frozen["analysis_sha256"],
        "t414_loader_sha256": frozen["t414_loader_sha256"],
        "development_runs": frozen["development_runs"],
        "validation_runs": [row["run"] for row in rows],
        "validation_source_hashes": source_hashes,
        "primary_horizon_bins": PRIMARY_HORIZON,
        "primary_horizon_us": PRIMARY_HORIZON * 0.016,
        "primary_full_array_median_field_rmse": correct_rmse,
        "primary_period_median_improvement": period_medians,
        "gates": gates,
        "summaries": summary_rows,
        "controls": control_rows,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "T415_VALIDATION_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_csv(RESULTS / "T415_MODEL_SUMMARY.csv", summary_rows)
    write_csv(RESULTS / "T415_FIELD_METRICS.csv", all_field_rows)
    write_csv(RESULTS / "T415_PERIOD_METRICS.csv", all_period_rows)
    write_csv(RESULTS / "T415_CONTROL_SUMMARY.csv", control_rows)
    write_csv(RESULTS / "T415_CONTROL_FIELD_METRICS.csv", control_field_rows)
    write_csv(RESULTS / "T415_EXAMPLE_284G_PROFILE.csv", profile_rows)
    write_csv(RESULTS / "T415_STRENGTH_DECILES.csv", strength_rows)
    print(json.dumps({"gates": gates, "primary": primary_summary, "controls": control_rows}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "validation"), required=True)
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    if args.stage == "development":
        development()
    else:
        validation()


if __name__ == "__main__":
    main()

