#!/usr/bin/env python3
"""T413 frozen live-state muonium handover test.

The operational definitions are frozen in ``T413_FROZEN_PROTOCOL.md``.
This script deliberately uses only samples before 2.5 microseconds to fit a
within-run predictor and evaluates later samples without refitting.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MUON_DIR = HERE.parent
import numpy as np

# Load the current runtime's NumPy before exposing the legacy local pyhdf
# vendor directory, which also contains an older Python-specific NumPy wheel.
sys.path.insert(0, str(MUON_DIR / "_vendor"))
from pyhdf.SD import SD, SDC


PROTOCOL = HERE / "T413_FROZEN_PROTOCOL.md"
MANIFEST = HERE / "source" / "T413_SOURCE_MANIFEST.csv"
RAW = HERE / "source" / "raw"
RESULTS = HERE / "results"

REBIN = 8
T_MIN = 0.25
T_SPLIT = 2.5
T_MAX = 6.0
SEED = 413
N_BOOT = 10_000
FREQUENCIES = np.arange(0.01, 12.0001, 0.01)
DECAYS = np.arange(0.0, 2.0001, 0.05)
MODELS = (
    "ara_full",
    "persistence",
    "ar1",
    "diagonal",
    "harmonic",
    "wrong_orientation",
    "broken_order",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_field(handle: SD, name: str) -> str:
    values = np.asarray(handle.select(name)[:]).reshape(-1).tolist()
    return b"".join(values).decode("latin1").rstrip("\x00 ")


def read_manifest() -> list[dict]:
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["datafile_id"] = int(row["datafile_id"])
        row["temperature_K"] = float(row["temperature_K"])
        row["field_G"] = float(row["field_G"])
        row["file_size"] = int(row["file_size"])
    return rows


def rebin_sum(values: np.ndarray, factor: int) -> np.ndarray:
    usable = values.shape[-1] // factor * factor
    shape = values.shape[:-1] + (usable // factor, factor)
    return values[..., :usable].reshape(shape).sum(axis=-1)


def rebin_mean(values: np.ndarray, factor: int) -> np.ndarray:
    usable = values.shape[-1] // factor * factor
    return values[:usable].reshape(usable // factor, factor).mean(axis=1)


def load_run(row: dict) -> dict:
    path = RAW / f"{row['run']}.nxs"
    if not path.exists():
        raise FileNotFoundError(path)
    if path.stat().st_size != row["file_size"]:
        raise ValueError(f"size mismatch for {path.name}")

    handle = SD(str(path), SDC.READ)
    counts = np.asarray(handle.select("counts")[:], dtype=float)
    corrected_time = np.asarray(handle.select("corrected_time")[:], dtype=float)
    frames = np.asarray(handle.select("frames_period")[:], dtype=float).reshape(-1)
    switching_states = int(np.asarray(handle.select("switching_states")[:]).reshape(-1)[0])
    labels = text_field(handle, "period_labels")
    recorded_temperature = float(np.asarray(handle.select("temperature")[:]).reshape(-1)[0])
    recorded_field = float(np.asarray(handle.select("magnetic_field")[:]).reshape(-1)[0])
    recorded_run = int(np.asarray(handle.select("number")[:]).reshape(-1)[0])

    checks = {
        "counts_192_by_time": counts.ndim == 2 and counts.shape[0] == 192,
        "two_switching_states": switching_states == 2,
        "period_order": labels == "RF on;RF off",
        "two_positive_frame_counts": len(frames) == 2 and np.all(frames > 0),
        "manifest_temperature_matches": abs(recorded_temperature - row["temperature_K"]) < 0.51,
        "manifest_field_matches": abs(recorded_field - row["field_G"]) < 0.51,
        "manifest_run_matches": recorded_run == int(row["run"][-5:]),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"structural check failed for {path.name}: {failed}")

    counts = rebin_sum(counts, REBIN)
    time = rebin_mean(corrected_time, REBIN)
    on_counts = counts[:96]
    off_counts = counts[96:]
    on_rate = on_counts / frames[0]
    off_rate = off_counts / frames[1]
    denominator = on_rate + off_rate
    valid_denominator = denominator > 0
    x = np.ones_like(denominator)
    x[valid_denominator] = 2.0 * on_rate[valid_denominator] / denominator[valid_denominator]
    relation = x - 1.0
    pair_counts = on_counts + off_counts

    eligible = (time >= T_MIN) & (time < T_MAX) & (pair_counts.sum(axis=0) > 0)
    time = time[eligible]
    relation = relation[:, eligible]
    pair_counts = pair_counts[:, eligible]
    development = time < T_SPLIT
    future = ~development
    if development.sum() < 10 or future.sum() < 10:
        raise ValueError(f"insufficient causal/future bins for {path.name}")

    return {
        "path": path,
        "time": time,
        "relation": relation,
        "weights": pair_counts,
        "development": development,
        "future": future,
        "checks": checks,
        "frames": frames,
    }


def weighted_rmse(observed: np.ndarray, predicted: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sqrt(np.sum(weights * (observed - predicted) ** 2) / np.sum(weights)))


def weighted_corr(observed: np.ndarray, predicted: np.ndarray, weights: np.ndarray) -> float:
    w = weights.astype(float)
    w /= w.sum()
    mx = float(np.sum(w * observed))
    my = float(np.sum(w * predicted))
    cov = float(np.sum(w * (observed - mx) * (predicted - my)))
    vx = float(np.sum(w * (observed - mx) ** 2))
    vy = float(np.sum(w * (predicted - my) ** 2))
    if vx <= 0 or vy <= 0:
        return float("nan")
    return cov / math.sqrt(vx * vy)


def fit_affine(states: np.ndarray, diagonal: bool = False) -> tuple[np.ndarray, np.ndarray]:
    previous = states[:-1]
    following = states[1:]
    if diagonal:
        matrix = np.zeros((2, 2), dtype=float)
        intercept = np.zeros(2, dtype=float)
        for axis in range(2):
            design = np.column_stack((previous[:, axis], np.ones(len(previous))))
            beta = np.linalg.lstsq(design, following[:, axis], rcond=None)[0]
            matrix[axis, axis] = beta[0]
            intercept[axis] = beta[1]
        return matrix, intercept
    design = np.column_stack((previous, np.ones(len(previous))))
    beta = np.linalg.lstsq(design, following, rcond=None)[0]
    return beta[:2].T, beta[2]


def forecast_state(matrix: np.ndarray, intercept: np.ndarray, initial: np.ndarray, count: int) -> np.ndarray:
    current = initial.astype(float).copy()
    output = np.empty((count, 2), dtype=float)
    for index in range(count):
        current = matrix @ current + intercept
        output[index] = current
    return output


def fit_ar1(values: np.ndarray) -> tuple[float, float]:
    design = np.column_stack((values[:-1], np.ones(len(values) - 1)))
    beta = np.linalg.lstsq(design, values[1:], rcond=None)[0]
    return float(beta[0]), float(beta[1])


def forecast_ar1(rho: float, intercept: float, initial: float, count: int) -> np.ndarray:
    current = float(initial)
    output = np.empty(count, dtype=float)
    for index in range(count):
        current = rho * current + intercept
        output[index] = current
    return output


def fit_harmonic(time: np.ndarray, values: np.ndarray, weights: np.ndarray) -> tuple[dict, np.ndarray]:
    root_w = np.sqrt(weights / np.mean(weights))
    best_score = float("inf")
    best = None
    omega_time = 2.0 * np.pi * FREQUENCIES[:, None] * time[None, :]
    cosines = np.cos(omega_time)
    sines = np.sin(omega_time)
    for decay in DECAYS:
        envelope = np.exp(-decay * time)
        design = np.empty((len(FREQUENCIES), len(time), 3), dtype=float)
        design[:, :, 0] = 1.0
        design[:, :, 1] = envelope[None, :] * cosines
        design[:, :, 2] = envelope[None, :] * sines
        weighted_design = design * root_w[None, :, None]
        weighted_y = values * root_w
        xtx = np.einsum("fti,ftj->fij", weighted_design, weighted_design)
        xty = np.einsum("fti,t->fi", weighted_design, weighted_y)
        xtx += np.eye(3)[None, :, :] * 1e-12
        beta = np.linalg.solve(xtx, xty[..., None])[..., 0]
        fitted = np.einsum("fti,fi->ft", design, beta)
        scores = np.sum(weights[None, :] * (values[None, :] - fitted) ** 2, axis=1)
        index = int(np.argmin(scores))
        if scores[index] < best_score:
            best_score = float(scores[index])
            best = {
                "frequency_MHz": float(FREQUENCIES[index]),
                "decay_per_us": float(decay),
                "beta": beta[index].copy(),
            }
    assert best is not None
    return best, best["beta"]


def predict_harmonic(model: dict, time: np.ndarray) -> np.ndarray:
    frequency = model["frequency_MHz"]
    decay = model["decay_per_us"]
    beta = model["beta"]
    envelope = np.exp(-decay * time)
    phase = 2.0 * np.pi * frequency * time
    design = np.column_stack((np.ones(len(time)), envelope * np.cos(phase), envelope * np.sin(phase)))
    return design @ beta


def first_crossing_time(time: np.ndarray, values: np.ndarray) -> float | None:
    for index in range(1, len(values)):
        left = values[index - 1]
        right = values[index]
        if left == 0:
            return float(time[index - 1])
        if left * right < 0:
            fraction = abs(left) / (abs(left) + abs(right))
            return float(time[index - 1] + fraction * (time[index] - time[index - 1]))
    return None


def analyse_run(row: dict) -> tuple[dict, list[dict], dict]:
    data = load_run(row)
    time = data["time"]
    relation = data["relation"]
    weights = data["weights"]
    development = data["development"]
    future = data["future"]
    time_weights = weights.sum(axis=0)

    ridge = np.average(relation[:, development], axis=1, weights=time_weights[development])
    residual = relation - ridge[:, None]
    development_matrix = residual[:, development].T
    development_row_weights = np.sqrt(time_weights[development] / np.mean(time_weights[development]))
    weighted_matrix = development_matrix * development_row_weights[:, None]
    _, singular_values, vt = np.linalg.svd(weighted_matrix, full_matrices=False)
    mode = vt[0]
    score = residual.T @ mode
    nonzero = np.flatnonzero(np.abs(score[development]) > 1e-15)
    if len(nonzero) and score[np.flatnonzero(development)[nonzero[0]]] < 0:
        mode = -mode
        score = -score

    dev_score = score[development]
    future_count = int(future.sum())
    state_dev = np.column_stack((dev_score[1:], np.diff(dev_score)))

    full_matrix, full_intercept = fit_affine(state_dev, diagonal=False)
    ara_future_state = forecast_state(full_matrix, full_intercept, state_dev[-1], future_count)

    diagonal_matrix, diagonal_intercept = fit_affine(state_dev, diagonal=True)
    diagonal_future_state = forecast_state(diagonal_matrix, diagonal_intercept, state_dev[-1], future_count)

    wrong_matrix = full_matrix.copy()
    wrong_matrix[0, 1] *= -1.0
    wrong_matrix[1, 0] *= -1.0
    wrong_future_state = forecast_state(wrong_matrix, full_intercept, state_dev[-1], future_count)

    rho, ar1_intercept = fit_ar1(dev_score)
    ar1_future = forecast_ar1(rho, ar1_intercept, dev_score[-1], future_count)
    persistence_future = np.repeat(dev_score[-1], future_count)

    harmonic_model, _ = fit_harmonic(time[development], dev_score, time_weights[development])
    harmonic_future = predict_harmonic(harmonic_model, time[future])

    rng = np.random.default_rng(SEED + int(row["run"][-5:]))
    permuted = dev_score[rng.permutation(len(dev_score))]
    permuted_state = np.column_stack((permuted[1:], np.diff(permuted)))
    broken_matrix, broken_intercept = fit_affine(permuted_state, diagonal=False)
    broken_future_state = forecast_state(broken_matrix, broken_intercept, permuted_state[-1], future_count)

    predictions = {
        "ara_full": ara_future_state[:, 0],
        "persistence": persistence_future,
        "ar1": ar1_future,
        "diagonal": diagonal_future_state[:, 0],
        "harmonic": harmonic_future,
        "wrong_orientation": wrong_future_state[:, 0],
        "broken_order": broken_future_state[:, 0],
    }

    observed_future = score[future]
    future_weights = time_weights[future]
    metrics = {}
    full_pattern_metrics = {}
    for name, predicted in predictions.items():
        metrics[name] = weighted_rmse(observed_future, predicted, future_weights)
        reconstructed = ridge[:, None] + mode[:, None] * predicted[None, :]
        full_pattern_metrics[name] = weighted_rmse(
            relation[:, future], reconstructed, weights[:, future]
        )

    observed_crossing = first_crossing_time(time[future], observed_future)
    future_duration = float(time[future][-1] - time[future][0])
    crossing_errors = {}
    crossing_times = {}
    for name, predicted in predictions.items():
        predicted_crossing = first_crossing_time(time[future], predicted)
        crossing_times[name] = predicted_crossing
        if observed_crossing is None:
            crossing_errors[name] = None
        elif predicted_crossing is None:
            crossing_errors[name] = future_duration
        else:
            crossing_errors[name] = abs(predicted_crossing - observed_crossing)

    summary = {
        "split": row["split"],
        "run": row["run"],
        "temperature_K": row["temperature_K"],
        "field_G": row["field_G"],
        "development_bins": int(development.sum()),
        "future_bins": int(future.sum()),
        "mode_variance_fraction": float(singular_values[0] ** 2 / np.sum(singular_values ** 2)),
        "ara_matrix_00": float(full_matrix[0, 0]),
        "ara_matrix_01": float(full_matrix[0, 1]),
        "ara_matrix_10": float(full_matrix[1, 0]),
        "ara_matrix_11": float(full_matrix[1, 1]),
        "harmonic_frequency_MHz": harmonic_model["frequency_MHz"],
        "harmonic_decay_per_us": harmonic_model["decay_per_us"],
        "observed_future_crossing_us": observed_crossing,
        "future_correlation_ara": weighted_corr(observed_future, predictions["ara_full"], future_weights),
    }
    for name in MODELS:
        summary[f"rmse_{name}"] = metrics[name]
        summary[f"pattern_rmse_{name}"] = full_pattern_metrics[name]
        summary[f"crossing_time_{name}_us"] = crossing_times[name]
        summary[f"crossing_error_{name}_us"] = crossing_errors[name]

    prediction_rows = []
    future_times = time[future]
    for index, current_time in enumerate(future_times):
        for name in MODELS:
            prediction_rows.append({
                "split": row["split"],
                "run": row["run"],
                "field_G": row["field_G"],
                "time_us": float(current_time),
                "model": name,
                "observed_A": float(observed_future[index]),
                "predicted_A": float(predictions[name][index]),
                "weight": float(future_weights[index]),
            })

    detail = {
        "time": time.tolist(),
        "development": development.astype(int).tolist(),
        "score": score.tolist(),
        "ridge_mean": float(np.mean(ridge)),
        "ridge_min": float(np.min(ridge)),
        "ridge_max": float(np.max(ridge)),
        "mode": mode.tolist(),
        "predictions": {name: values.tolist() for name, values in predictions.items()},
    }
    return summary, prediction_rows, detail


def bootstrap_interval(values: np.ndarray, seed: int = SEED) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(values), size=(N_BOOT, len(values)))
    estimates = np.median(values[draws], axis=1)
    return float(np.quantile(estimates, 0.025)), float(np.quantile(estimates, 0.975))


def aggregate(rows: list[dict]) -> dict:
    output = {}
    for split in sorted({row["split"] for row in rows}):
        selected = [row for row in rows if row["split"] == split]
        medians = {
            name: float(np.median([row[f"rmse_{name}"] for row in selected]))
            for name in MODELS
        }
        simple_names = ("persistence", "ar1", "diagonal")
        paired_simple_advantage = np.asarray([
            min(row[f"rmse_{name}"] for name in simple_names) - row["rmse_ara_full"]
            for row in selected
        ])
        harmonic_advantage = np.asarray([
            row["rmse_harmonic"] - row["rmse_ara_full"] for row in selected
        ])
        wrong_advantage = np.asarray([
            row["rmse_wrong_orientation"] - row["rmse_ara_full"] for row in selected
        ])
        broken_advantage = np.asarray([
            row["rmse_broken_order"] - row["rmse_ara_full"] for row in selected
        ])
        output[split] = {
            "run_count": len(selected),
            "median_rmse": medians,
            "ara_pairwise_win_fraction": {
                name: float(np.mean([
                    row["rmse_ara_full"] < row[f"rmse_{name}"] for row in selected
                ]))
                for name in MODELS if name != "ara_full"
            },
            "median_advantage_over_best_simple": float(np.median(paired_simple_advantage)),
            "bootstrap95_advantage_over_best_simple": bootstrap_interval(paired_simple_advantage),
            "median_advantage_over_harmonic": float(np.median(harmonic_advantage)),
            "bootstrap95_advantage_over_harmonic": bootstrap_interval(harmonic_advantage, SEED + 1),
            "median_advantage_over_wrong_orientation": float(np.median(wrong_advantage)),
            "median_advantage_over_broken_order": float(np.median(broken_advantage)),
            "crossing_run_count": int(sum(row["observed_future_crossing_us"] is not None for row in selected)),
        }
    if "holdout" in output:
        h = output["holdout"]
        simple = h["median_rmse"]
        interval = h["bootstrap95_advantage_over_best_simple"]
        relational = (
            simple["ara_full"] < simple["persistence"]
            and simple["ara_full"] < simple["ar1"]
            and simple["ara_full"] < simple["diagonal"]
            and interval[0] > 0
            and simple["ara_full"] < simple["broken_order"]
        )
        orientation = (
            simple["ara_full"] < simple["wrong_orientation"]
            and h["ara_pairwise_win_fraction"]["wrong_orientation"] > 0.5
        )
        harmonic_interval = h["bootstrap95_advantage_over_harmonic"]
        harmonic_gain = h["median_advantage_over_harmonic"] / simple["harmonic"] if simple["harmonic"] else 0.0
        added = harmonic_gain >= 0.02 and harmonic_interval[0] > 0
        output["frozen_gates"] = {
            "relational_predictive_support": bool(relational),
            "orientation_support": bool(orientation),
            "added_value_beyond_harmonic": bool(added),
            "relative_median_gain_over_harmonic": float(harmonic_gain),
        }
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--splits", default="development,validation,holdout")
    parser.add_argument("--suffix", default="FULL")
    args = parser.parse_args()
    requested = {part.strip() for part in args.splits.split(",") if part.strip()}
    manifest = [row for row in read_manifest() if row["split"] in requested]
    if not manifest:
        raise SystemExit("No manifest rows selected")

    summaries = []
    predictions = []
    details = {}
    hashes = []
    for index, row in enumerate(manifest, start=1):
        print(f"[{index}/{len(manifest)}] {row['split']} {row['run']} F={row['field_G']:g}", flush=True)
        summary, prediction_rows, detail = analyse_run(row)
        summaries.append(summary)
        predictions.extend(prediction_rows)
        details[row["run"]] = detail
        path = RAW / f"{row['run']}.nxs"
        hashes.append({"run": row["run"], "sha256": sha256(path), "bytes": path.stat().st_size})

    RESULTS.mkdir(parents=True, exist_ok=True)
    suffix = args.suffix.upper()
    write_csv(RESULTS / f"T413_{suffix}_RUN_METRICS.csv", summaries)
    write_csv(RESULTS / f"T413_{suffix}_PREDICTIONS.csv", predictions)
    write_csv(RESULTS / f"T413_{suffix}_SOURCE_HASHES.csv", hashes)
    result = {
        "test": "T413 live-state muonium handover",
        "protocol_sha256": sha256(PROTOCOL),
        "requested_splits": sorted(requested),
        "run_count": len(summaries),
        "aggregate": aggregate(summaries),
        "run_details": details,
    }
    with (RESULTS / f"T413_{suffix}_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
    print(json.dumps(result["aggregate"], indent=2))


if __name__ == "__main__":
    main()
