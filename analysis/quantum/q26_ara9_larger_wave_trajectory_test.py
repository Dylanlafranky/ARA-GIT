#!/usr/bin/env python3
"""Run the staged Q26 ARA^9 larger-wave trajectory test.

Stages
------
prepare
    Verify and split the immutable target into exposed geometry and sealed
    later matrices without displaying target values.
predict
    Read only the exposed packet, write every model prediction, and hash it.
reveal
    Verify the frozen prediction hash, open the sealed packet, score the
    registered gates, and write the bounded audit artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q26_temperature_ara9"
SOURCE = DATA / "SuppFigure10.csv"
PROTOCOL = HERE / "Q26_ARA9_LARGER_WAVE_TRAJECTORY_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q26_ARA9_LARGER_WAVE_TRAJECTORY_PROTOCOL_v1_FROZEN.sha256"
GEOMETRY = HERE / "Q26_ARA9_LARGER_WAVE_GEOMETRY_PACKET.json"
SEALED = HERE / "Q26_ARA9_LARGER_WAVE_SEALED_TARGET_PACKET.json"
PREDICTIONS = HERE / "Q26_ARA9_LARGER_WAVE_PREDICTIONS.json"
PREDICTIONS_SHA = HERE / "Q26_ARA9_LARGER_WAVE_PREDICTIONS.sha256"
PREDICTIONS_CSV = HERE / "Q26_ARA9_LARGER_WAVE_PREDICTIONS.csv"
METRICS_CSV = HERE / "Q26_ARA9_LARGER_WAVE_METRICS.csv"
TRAJECTORIES_CSV = HERE / "Q26_ARA9_LARGER_WAVE_TRAJECTORIES.csv"
PERMUTATION_CSV = HERE / "Q26_ARA9_LARGER_WAVE_PERMUTATION.csv"
RESULTS = HERE / "Q26_ARA9_LARGER_WAVE_RESULTS.json"

EXPECTED_SOURCE_MD5 = "9a9e3abac0ee8f80535e17ec72313919"
EXPECTED_PROTOCOL_SHA = (
    "0bd8f2a0ee96733e0411d477a5c808c4ebd100b083b84b30108d05ed110347e6"
)
TEMPERATURES = (0.1, 0.2, 0.3, 0.5, 0.7, 0.85, 1.0, 1.1)
STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
WAITS = np.asarray(
    [1.00, 1.99, 3.98, 7.94, 15.85, 31.62, 63.09, 125.89, 251.19, 501.18, 1000.00],
    dtype=float,
)
DEV_COUNT = 7
TARGET_INDICES = tuple(range(DEV_COUNT, len(WAITS)))
BASIS = (
    "II", "IX", "IY", "IZ",
    "XI", "XX", "XY", "XZ",
    "YI", "YX", "YY", "YZ",
    "ZI", "ZX", "ZY", "ZZ",
)
CELLS = ("XX", "XY", "XZ", "YX", "YY", "YZ", "ZX", "ZY", "ZZ")
MODELS = ("ara", "persistence", "linear", "no_rotation", "zero")
PRIMARY_TEMPERATURES = set(TEMPERATURES[1:])
BOOTSTRAP_DRAWS = 5000
PERMUTATION_DRAWS = 999
SEED = 26026

I2 = np.eye(2, dtype=complex)
X = np.asarray([[0, 1], [1, 0]], dtype=complex)
Y = np.asarray([[0, -1j], [1j, 0]], dtype=complex)
Z = np.asarray([[1, 0], [0, -1]], dtype=complex)
PAULI = (I2, X, Y, Z)


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def canonical_json(path: Path, payload: Any) -> str:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return digest(path, "sha256")


def verify_frozen_protocol() -> str:
    recorded = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    actual = digest(PROTOCOL, "sha256")
    if actual != EXPECTED_PROTOCOL_SHA or recorded != EXPECTED_PROTOCOL_SHA:
        raise RuntimeError(
            f"Frozen protocol mismatch: actual={actual}, recorded={recorded}"
        )
    return actual


def parse_source() -> np.ndarray:
    if digest(SOURCE, "md5") != EXPECTED_SOURCE_MD5:
        raise RuntimeError("Q26 target-source checksum mismatch")
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        raw_rows = list(csv.reader(stream))
    rows = []
    for row in raw_rows:
        if not any(value.strip() for value in row):
            continue
        if len(row) != 16:
            raise RuntimeError(f"Expected 16 coefficients, found {len(row)}")
        rows.append([float(value) for value in row])
    array = np.asarray(rows, dtype=float)
    if array.shape != (8 * 4 * 11, 16):
        raise RuntimeError(f"Unexpected Q26 target shape: {array.shape}")
    if not np.all(np.isfinite(array)):
        raise RuntimeError("Q26 target contains non-finite coefficients")
    if np.max(np.abs(array[:, 0] - 0.25)) > 1e-12:
        raise RuntimeError("Q26 c_II invariant failed")
    return array.reshape(8, 4, 11, 16)


def rho_from_coefficients(coefficients: np.ndarray) -> np.ndarray:
    rho = np.zeros((4, 4), dtype=complex)
    for i in range(4):
        for j in range(4):
            rho += coefficients[4 * i + j] * np.kron(PAULI[i], PAULI[j])
    return 0.5 * (rho + rho.conj().T)


def connected_from_coefficients(coefficients: np.ndarray) -> np.ndarray:
    expectations = 4.0 * np.asarray(coefficients, dtype=float)
    a = expectations[[4, 8, 12]]
    b = expectations[[1, 2, 3]]
    tensor = expectations[[5, 6, 7, 9, 10, 11, 13, 14, 15]].reshape(3, 3)
    return tensor - np.outer(a, b)


def closure(matrix: np.ndarray) -> float:
    return float(abs(np.linalg.det(matrix)) ** (1.0 / 3.0))


def ara_class(x_value: float) -> str:
    if x_value >= 1.5:
        return "crest"
    if x_value <= 0.5:
        return "trough"
    return "handover"


def standardize_basis(basis: np.ndarray) -> np.ndarray:
    fixed = np.asarray(basis, dtype=float).copy()
    for row in fixed:
        pivot = int(np.argmax(np.abs(row)))
        if row[pivot] < 0:
            row *= -1
    return fixed


def fit_ara_predictor(
    early: np.ndarray,
    early_waits: np.ndarray,
    target_waits: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    q_early = early[:, :2, :2].reshape(len(early), 4)
    _, singular, vt = np.linalg.svd(q_early, full_matrices=False)
    basis = standardize_basis(vt[:2])
    z = q_early @ basis.T
    radius = np.linalg.norm(z, axis=1)
    log_fit = np.polyfit(early_waits, np.log(np.maximum(radius, 1e-12)), 1)
    log_fit[0] = min(float(log_fit[0]), 0.0)
    angle = np.unwrap(np.arctan2(z[:, 1], z[:, 0]))
    angle_fit = np.polyfit(early_waits, angle, 1)

    predicted_radius = np.exp(np.polyval(log_fit, target_waits))
    predicted_angle = np.polyval(angle_fit, target_waits)
    predicted_z = np.column_stack(
        (
            predicted_radius * np.cos(predicted_angle),
            predicted_radius * np.sin(predicted_angle),
        )
    )
    predicted_q = predicted_z @ basis

    ara = np.zeros((len(target_waits), 3, 3), dtype=float)
    ara[:, :2, :2] = predicted_q.reshape(-1, 2, 2)
    ara[:, 2, 2] = float(np.median(early[-3:, 2, 2]))

    persistence = np.repeat(early[-1:,:,:], len(target_waits), axis=0)

    linear = np.zeros_like(ara)
    for i in range(3):
        for j in range(3):
            linear[:, i, j] = np.polyval(
                np.polyfit(early_waits, early[:, i, j], 1),
                target_waits,
            )
    linear = np.clip(linear, -1.0, 1.0)

    no_rotation = np.zeros_like(ara)
    last_q = q_early[-1]
    last_norm = float(np.linalg.norm(last_q))
    fixed_direction = (
        last_q / last_norm if last_norm > 1e-12 else np.zeros_like(last_q)
    )
    no_rotation[:, :2, :2] = (
        predicted_radius[:, None] * fixed_direction[None, :]
    ).reshape(-1, 2, 2)
    no_rotation[:, 2, 2] = ara[:, 2, 2]

    fit = {
        "basis": basis.tolist(),
        "relation_plane_singular_values": singular.tolist(),
        "log_radius_intercept": float(log_fit[1]),
        "log_radius_slope_per_us": float(log_fit[0]),
        "angle_intercept": float(angle_fit[1]),
        "angle_slope_per_us": float(angle_fit[0]),
        "predicted_radius": predicted_radius.tolist(),
        "predicted_angle": predicted_angle.tolist(),
    }
    return {
        "ara": ara,
        "persistence": persistence,
        "linear": linear,
        "no_rotation": no_rotation,
        "zero": np.zeros_like(ara),
    }, fit


def phase_angle(matrix: np.ndarray, basis: np.ndarray) -> float:
    q = matrix[:2, :2].reshape(4)
    z = q @ basis.T
    return float(math.atan2(float(z[1]), float(z[0])))


def circular_error(left: float, right: float) -> float:
    return float(abs(math.atan2(math.sin(left - right), math.cos(left - right))))


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = 0.5 * (start + end - 1) + 1.0
        start = end
    return ranks


def spearman(left: np.ndarray, right: np.ndarray) -> float:
    a = rankdata(np.asarray(left, dtype=float))
    b = rankdata(np.asarray(right, dtype=float))
    if np.std(a) <= 1e-15 or np.std(b) <= 1e-15:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def first_at_or_below(values: list[float], threshold: float) -> int | None:
    for index, value in enumerate(values):
        if value <= threshold:
            return index
    return None


def stable_orientation_flip(matrices: list[np.ndarray], x_values: list[float]) -> bool:
    reliable = [
        (index, np.sign(np.linalg.det(matrix)))
        for index, (matrix, x_value) in enumerate(zip(matrices, x_values))
        if x_value > 0.5 and abs(np.linalg.det(matrix)) > 1e-12
    ]
    if not reliable:
        return False
    initial = reliable[0][1]
    for left, right in zip(reliable[:-1], reliable[1:]):
        if (
            left[1] == -initial
            and right[1] == -initial
            and right[0] == left[0] + 1
        ):
            return True
    return False


def prepare() -> None:
    protocol_hash = verify_frozen_protocol()
    source = parse_source()
    geometry_records = []
    target_records = []
    quality = []

    for t_index, temperature in enumerate(TEMPERATURES):
        for s_index, state in enumerate(STATES):
            connected = np.asarray(
                [
                    connected_from_coefficients(source[t_index, s_index, w_index])
                    for w_index in range(11)
                ]
            )
            for w_index in range(11):
                rho = rho_from_coefficients(source[t_index, s_index, w_index])
                quality.append(
                    {
                        "temperature_K": temperature,
                        "state": state,
                        "wait_index": w_index,
                        "trace_error": float(abs(np.trace(rho) - 1.0)),
                        "hermiticity_residual": float(
                            np.max(np.abs(rho - rho.conj().T))
                        ),
                        "minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(rho))),
                    }
                )
            geometry_records.append(
                {
                    "temperature_K": temperature,
                    "state": state,
                    "wait_indices": list(range(DEV_COUNT)),
                    "wait_us": WAITS[:DEV_COUNT].tolist(),
                    "connected_matrices": connected[:DEV_COUNT].tolist(),
                }
            )
            target_records.append(
                {
                    "temperature_K": temperature,
                    "state": state,
                    "wait_indices": list(TARGET_INDICES),
                    "wait_us": WAITS[DEV_COUNT:].tolist(),
                    "connected_matrices": connected[DEV_COUNT:].tolist(),
                }
            )

    geometry_payload = {
        "test_id": "Q26-ARA9-LARGER-WAVE-v1",
        "protocol_sha256": protocol_hash,
        "source_md5": EXPECTED_SOURCE_MD5,
        "target_values_included": False,
        "records": geometry_records,
    }
    sealed_payload = {
        "test_id": "Q26-ARA9-LARGER-WAVE-v1",
        "protocol_sha256": protocol_hash,
        "source_md5": EXPECTED_SOURCE_MD5,
        "target_values_included": True,
        "records": target_records,
        "data_quality": quality,
    }
    geometry_hash = canonical_json(GEOMETRY, geometry_payload)
    sealed_hash = canonical_json(SEALED, sealed_payload)
    print(
        "Q26 prepare complete: "
        f"{len(geometry_records)} exposed trajectories, "
        f"{len(target_records) * len(TARGET_INDICES)} sealed matrices"
    )
    print(f"geometry_sha256={geometry_hash}")
    print(f"sealed_sha256={sealed_hash}")


def predict() -> None:
    protocol_hash = verify_frozen_protocol()
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    if geometry["protocol_sha256"] != protocol_hash:
        raise RuntimeError("Q26 geometry packet protocol mismatch")
    prediction_records = []
    fits = []

    for record in geometry["records"]:
        early = np.asarray(record["connected_matrices"], dtype=float)
        model_predictions, fit = fit_ara_predictor(
            early, WAITS[:DEV_COUNT], WAITS[DEV_COUNT:]
        )
        first_h = closure(early[0])
        fit_record = {
            "temperature_K": record["temperature_K"],
            "state": record["state"],
            "first_closure": first_h,
            **fit,
        }
        fits.append(fit_record)
        basis = np.asarray(fit["basis"], dtype=float)
        for target_position, wait_index in enumerate(TARGET_INDICES):
            for model in MODELS:
                matrix = model_predictions[model][target_position]
                h_value = closure(matrix)
                x_value = 2.0 * h_value / first_h if first_h > 1e-12 else 0.0
                prediction_records.append(
                    {
                        "temperature_K": record["temperature_K"],
                        "state": record["state"],
                        "wait_index": wait_index,
                        "wait_us": float(WAITS[wait_index]),
                        "model": model,
                        "connected_matrix": matrix.tolist(),
                        "closure": h_value,
                        "ara_x": x_value,
                        "ara_class": ara_class(x_value),
                        "relation_plane_angle": phase_angle(matrix, basis),
                    }
                )

    payload = {
        "test_id": "Q26-ARA9-LARGER-WAVE-v1",
        "protocol_sha256": protocol_hash,
        "geometry_sha256": digest(GEOMETRY, "sha256"),
        "sealed_packet_read": False,
        "fits": fits,
        "predictions": prediction_records,
    }
    prediction_hash = canonical_json(PREDICTIONS, payload)
    PREDICTIONS_SHA.write_text(
        f"{prediction_hash}  {PREDICTIONS.name}\n", encoding="utf-8"
    )

    with PREDICTIONS_CSV.open("w", newline="", encoding="utf-8") as stream:
        fields = [
            "temperature_K", "state", "wait_index", "wait_us", "model",
            *[f"pred_{cell}" for cell in CELLS],
            "pred_closure", "pred_ara_x", "pred_class",
            "pred_relation_plane_angle",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for record in prediction_records:
            matrix = np.asarray(record["connected_matrix"])
            flattened = matrix.reshape(-1)
            row = {
                "temperature_K": record["temperature_K"],
                "state": record["state"],
                "wait_index": record["wait_index"],
                "wait_us": record["wait_us"],
                "model": record["model"],
                **{
                    f"pred_{cell}": float(value)
                    for cell, value in zip(CELLS, flattened)
                },
                "pred_closure": record["closure"],
                "pred_ara_x": record["ara_x"],
                "pred_class": record["ara_class"],
                "pred_relation_plane_angle": record["relation_plane_angle"],
            }
            writer.writerow(row)

    primary_count = sum(
        record["temperature_K"] in PRIMARY_TEMPERATURES
        and record["model"] == "ara"
        for record in prediction_records
    )
    print(
        f"Q26 predictions frozen: {primary_count} primary ARA^9 matrices; "
        f"sha256={prediction_hash}"
    )


def bootstrap_probability(
    trajectory_metrics: list[dict[str, Any]],
    left_model: str,
    right_model: str,
) -> float:
    by_key: dict[tuple[float, str], dict[str, float]] = {}
    for row in trajectory_metrics:
        key = (float(row["temperature_K"]), str(row["state"]))
        by_key.setdefault(key, {})[str(row["model"])] = float(row["cut_mae"])
    keys = sorted(by_key)
    differences = np.asarray(
        [by_key[key][left_model] - by_key[key][right_model] for key in keys],
        dtype=float,
    )
    rng = np.random.default_rng(SEED + sum(map(ord, left_model + right_model)))
    indices = rng.integers(0, len(keys), size=(BOOTSTRAP_DRAWS, len(keys)))
    sampled = np.mean(differences[indices], axis=1)
    return float(np.mean(sampled < 0.0))


def reveal() -> None:
    protocol_hash = verify_frozen_protocol()
    recorded_prediction_hash = PREDICTIONS_SHA.read_text(
        encoding="utf-8"
    ).split()[0]
    actual_prediction_hash = digest(PREDICTIONS, "sha256")
    if recorded_prediction_hash != actual_prediction_hash:
        raise RuntimeError("Q26 prediction hash mismatch")

    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    sealed = json.loads(SEALED.read_text(encoding="utf-8"))
    predictions = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    for payload in (geometry, sealed, predictions):
        if payload["protocol_sha256"] != protocol_hash:
            raise RuntimeError("Q26 staged packet protocol mismatch")

    geometry_by_key = {
        (float(row["temperature_K"]), str(row["state"])): row
        for row in geometry["records"]
    }
    target_by_key = {
        (float(row["temperature_K"]), str(row["state"])): row
        for row in sealed["records"]
    }
    fit_by_key = {
        (float(row["temperature_K"]), str(row["state"])): row
        for row in predictions["fits"]
    }
    pred_by_key: dict[tuple[float, str, int, str], dict[str, Any]] = {}
    for row in predictions["predictions"]:
        pred_by_key[
            (
                float(row["temperature_K"]),
                str(row["state"]),
                int(row["wait_index"]),
                str(row["model"]),
            )
        ] = row

    metric_rows: list[dict[str, Any]] = []
    trajectory_rows: list[dict[str, Any]] = []
    primary_keys = [
        key for key in sorted(target_by_key) if key[0] in PRIMARY_TEMPERATURES
    ]

    for key in sorted(target_by_key):
        temperature, state = key
        early = np.asarray(geometry_by_key[key]["connected_matrices"], dtype=float)
        targets = np.asarray(target_by_key[key]["connected_matrices"], dtype=float)
        first_h = closure(early[0])
        basis = np.asarray(fit_by_key[key]["basis"], dtype=float)
        true_h = [closure(matrix) for matrix in targets]
        true_x = [
            2.0 * value / first_h if first_h > 1e-12 else 0.0
            for value in true_h
        ]
        true_class = [ara_class(value) for value in true_x]

        for model in MODELS:
            cut_errors = []
            h_errors = []
            phase_errors = []
            class_matches = []
            for position, wait_index in enumerate(TARGET_INDICES):
                pred_record = pred_by_key[(temperature, state, wait_index, model)]
                predicted = np.asarray(pred_record["connected_matrix"], dtype=float)
                actual = targets[position]
                errors = np.abs(predicted - actual)
                cut_errors.extend(errors.reshape(-1).tolist())
                h_errors.append(abs(float(pred_record["closure"]) - true_h[position]))
                actual_phase = phase_angle(actual, basis)
                predicted_phase = float(pred_record["relation_plane_angle"])
                phase_errors.append(circular_error(predicted_phase, actual_phase))
                class_matches.append(
                    str(pred_record["ara_class"]) == true_class[position]
                )
                metric_rows.append(
                    {
                        "partition": (
                            "primary"
                            if temperature in PRIMARY_TEMPERATURES
                            else "replication_0p1K"
                        ),
                        "temperature_K": temperature,
                        "state": state,
                        "wait_index": wait_index,
                        "wait_us": float(WAITS[wait_index]),
                        "model": model,
                        "cut_mae": float(np.mean(errors)),
                        "cut_rmse": float(np.sqrt(np.mean(errors ** 2))),
                        "true_closure": true_h[position],
                        "pred_closure": float(pred_record["closure"]),
                        "closure_abs_error": h_errors[-1],
                        "true_ara_x": true_x[position],
                        "pred_ara_x": float(pred_record["ara_x"]),
                        "true_class": true_class[position],
                        "pred_class": str(pred_record["ara_class"]),
                        "class_match": bool(class_matches[-1]),
                        "true_relation_plane_angle": actual_phase,
                        "pred_relation_plane_angle": predicted_phase,
                        "phase_abs_error_rad": phase_errors[-1],
                    }
                )

            predicted_hidden = [
                np.asarray(
                    pred_by_key[(temperature, state, wait_index, model)][
                        "connected_matrix"
                    ],
                    dtype=float,
                )
                for wait_index in TARGET_INDICES
            ]
            actual_full = list(early) + list(targets)
            predicted_full = list(early) + predicted_hidden
            actual_h_full = [closure(matrix) for matrix in actual_full]
            predicted_h_full = [closure(matrix) for matrix in predicted_full]
            actual_x_full = [
                2.0 * value / first_h if first_h > 1e-12 else 0.0
                for value in actual_h_full
            ]
            predicted_x_full = [
                2.0 * value / first_h if first_h > 1e-12 else 0.0
                for value in predicted_h_full
            ]
            actual_ridge = first_at_or_below(actual_x_full, 1.0)
            predicted_ridge = first_at_or_below(predicted_x_full, 1.0)
            actual_trough = first_at_or_below(actual_x_full, 0.5)
            predicted_trough = first_at_or_below(predicted_x_full, 0.5)

            trajectory_rows.append(
                {
                    "partition": (
                        "primary"
                        if temperature in PRIMARY_TEMPERATURES
                        else "replication_0p1K"
                    ),
                    "temperature_K": temperature,
                    "state": state,
                    "model": model,
                    "cut_mae": float(np.mean(cut_errors)),
                    "cut_rmse": float(np.sqrt(np.mean(np.square(cut_errors)))),
                    "closure_mae": float(np.mean(h_errors)),
                    "phase_mae_rad": float(np.mean(phase_errors)),
                    "class_accuracy": float(np.mean(class_matches)),
                    "actual_ridge_index": actual_ridge,
                    "predicted_ridge_index": predicted_ridge,
                    "ridge_error_samples": (
                        abs(predicted_ridge - actual_ridge)
                        if actual_ridge is not None and predicted_ridge is not None
                        else None
                    ),
                    "actual_trough_index": actual_trough,
                    "predicted_trough_index": predicted_trough,
                    "trough_error_samples": (
                        abs(predicted_trough - actual_trough)
                        if actual_trough is not None and predicted_trough is not None
                        else None
                    ),
                    "closure_wait_spearman": spearman(
                        WAITS, np.asarray(actual_h_full)
                    ),
                    "final_ara_x": actual_x_full[-1],
                    "final_class": ara_class(actual_x_full[-1]),
                    "amplitude_crest_to_trough": bool(actual_x_full[-1] <= 0.5),
                    "stable_orientation_flip": stable_orientation_flip(
                        actual_full, actual_x_full
                    ),
                    "reliable_orientation_sign_fraction_initial": float(
                        np.mean(
                            [
                                np.sign(np.linalg.det(matrix))
                                == np.sign(np.linalg.det(actual_full[0]))
                                for matrix, x_value in zip(
                                    actual_full, actual_x_full
                                )
                                if x_value > 0.5
                                and abs(np.linalg.det(matrix)) > 1e-12
                            ]
                        )
                    ),
                }
            )

    primary_metrics = [
        row for row in metric_rows if row["partition"] == "primary"
    ]
    primary_trajectories = [
        row for row in trajectory_rows if row["partition"] == "primary"
    ]

    model_summary = {}
    for model in MODELS:
        rows = [row for row in primary_metrics if row["model"] == model]
        trajectories = [
            row for row in primary_trajectories if row["model"] == model
        ]
        model_summary[model] = {
            "cut_mae": float(np.mean([row["cut_mae"] for row in rows])),
            "cut_rmse": float(np.sqrt(np.mean(
                [row["cut_rmse"] ** 2 for row in rows]
            ))),
            "closure_mae": float(
                np.mean([row["closure_abs_error"] for row in rows])
            ),
            "phase_mae_rad": float(
                np.mean([row["phase_abs_error_rad"] for row in rows])
            ),
            "class_accuracy": float(np.mean([row["class_match"] for row in rows])),
            "trajectory_cut_mae_median": float(
                np.median([row["cut_mae"] for row in trajectories])
            ),
        }

    ara_traj = [
        row for row in primary_trajectories if row["model"] == "ara"
    ]
    persistence_by_key = {
        (row["temperature_K"], row["state"]): row
        for row in primary_trajectories
        if row["model"] == "persistence"
    }
    ara_win_persistence_fraction = float(
        np.mean(
            [
                row["cut_mae"]
                < persistence_by_key[(row["temperature_K"], row["state"])][
                    "cut_mae"
                ]
                for row in ara_traj
            ]
        )
    )

    ridge_eligible = [
        row
        for row in ara_traj
        if row["actual_ridge_index"] is not None
        and row["actual_ridge_index"] >= DEV_COUNT
    ]
    trough_eligible = [
        row
        for row in ara_traj
        if row["actual_trough_index"] is not None
        and row["actual_trough_index"] >= DEV_COUNT
    ]
    ridge_within_one = float(
        np.mean(
            [
                row["ridge_error_samples"] is not None
                and row["ridge_error_samples"] <= 1
                for row in ridge_eligible
            ]
        )
    ) if ridge_eligible else 0.0
    trough_within_one = float(
        np.mean(
            [
                row["trough_error_samples"] is not None
                and row["trough_error_samples"] <= 1
                for row in trough_eligible
            ]
        )
    ) if trough_eligible else 0.0

    median_spearman = float(
        np.median([row["closure_wait_spearman"] for row in ara_traj])
    )
    final_trough_fraction = float(
        np.mean([row["final_class"] == "trough" for row in ara_traj])
    )
    amplitude_flip_fraction = float(
        np.mean([row["amplitude_crest_to_trough"] for row in ara_traj])
    )
    stable_orientation_flip_fraction = float(
        np.mean([row["stable_orientation_flip"] for row in ara_traj])
    )

    bootstrap = {
        "ara_lower_mae_than_persistence": bootstrap_probability(
            primary_trajectories, "ara", "persistence"
        ),
        "ara_lower_mae_than_linear": bootstrap_probability(
            primary_trajectories, "ara", "linear"
        ),
        "ara_lower_mae_than_no_rotation": bootstrap_probability(
            primary_trajectories, "ara", "no_rotation"
        ),
    }

    rng = np.random.default_rng(SEED)
    permutation_mae = []
    actual_targets_by_key = {
        key: np.asarray(target_by_key[key]["connected_matrices"], dtype=float)
        for key in primary_keys
    }
    for permutation_index in range(PERMUTATION_DRAWS):
        errors = []
        for key in primary_keys:
            early = np.asarray(
                geometry_by_key[key]["connected_matrices"], dtype=float
            )
            shuffled = early[rng.permutation(DEV_COUNT)]
            permuted, _ = fit_ara_predictor(
                shuffled, WAITS[:DEV_COUNT], WAITS[DEV_COUNT:]
            )
            errors.extend(
                np.abs(permuted["ara"] - actual_targets_by_key[key])
                .reshape(-1)
                .tolist()
            )
        permutation_mae.append(float(np.mean(errors)))
    observed_ara_mae = model_summary["ara"]["cut_mae"]
    time_order_percentile = float(
        np.mean(np.asarray(permutation_mae) > observed_ara_mae)
    )

    quality = sealed["data_quality"]
    quality_summary = {
        "record_count": len(quality),
        "maximum_trace_error": float(
            max(row["trace_error"] for row in quality)
        ),
        "maximum_hermiticity_residual": float(
            max(row["hermiticity_residual"] for row in quality)
        ),
        "minimum_eigenvalue": float(
            min(row["minimum_eigenvalue"] for row in quality)
        ),
        "fraction_positive_semidefinite_at_minus_1e_10": float(
            np.mean([row["minimum_eigenvalue"] >= -1e-10 for row in quality])
        ),
    }

    gates = {
        "D1_source_checksum": digest(SOURCE, "md5") == EXPECTED_SOURCE_MD5,
        "D2_schema_8x4x11x16": len(quality) == 8 * 4 * 11,
        "D3_cII_invariant": True,
        "D4_predictions_frozen_before_reveal": (
            len([
                row for row in predictions["predictions"]
                if float(row["temperature_K"]) in PRIMARY_TEMPERATURES
                and row["model"] == "ara"
            ]) == 112
            and recorded_prediction_hash == actual_prediction_hash
        ),
        "P1_ara_beats_persistence_cut_mae": (
            model_summary["ara"]["cut_mae"]
            < model_summary["persistence"]["cut_mae"]
        ),
        "P2_ara_beats_linear_cut_mae": (
            model_summary["ara"]["cut_mae"]
            < model_summary["linear"]["cut_mae"]
        ),
        "P3_ara_beats_no_rotation_cut_mae": (
            model_summary["ara"]["cut_mae"]
            < model_summary["no_rotation"]["cut_mae"]
        ),
        "P4_ara_beats_persistence_70pct_trajectories": (
            ara_win_persistence_fraction >= 0.70
        ),
        "P5_ara_beats_persistence_closure_mae": (
            model_summary["ara"]["closure_mae"]
            < model_summary["persistence"]["closure_mae"]
        ),
        "P6_ara_beats_no_rotation_phase_error": (
            model_summary["ara"]["phase_mae_rad"]
            < model_summary["no_rotation"]["phase_mae_rad"]
        ),
        "P7_class_accuracy_70pct": (
            model_summary["ara"]["class_accuracy"] >= 0.70
        ),
        "P8_ridge_within_one_60pct": ridge_within_one >= 0.60,
        "P9_trough_within_one_60pct": trough_within_one >= 0.60,
        "W1_median_spearman_at_most_minus_0p70": median_spearman <= -0.70,
        "W2_final_trough_75pct": final_trough_fraction >= 0.75,
        "W3_amplitude_flip_75pct": amplitude_flip_fraction >= 0.75,
        "W4_time_order_beats_95pct_permutations": (
            time_order_percentile >= 0.95
        ),
        "W5_bootstrap_95pct_vs_persistence_and_linear": (
            bootstrap["ara_lower_mae_than_persistence"] >= 0.95
            and bootstrap["ara_lower_mae_than_linear"] >= 0.95
        ),
    }
    data_pass = all(gates[key] for key in gates if key.startswith("D"))
    core_pass = all(gates[key] for key in ("P1_ara_beats_persistence_cut_mae",
                                           "P2_ara_beats_linear_cut_mae",
                                           "P3_ara_beats_no_rotation_cut_mae"))
    wave_pass = all(gates[key] for key in (
        "W1_median_spearman_at_most_minus_0p70",
        "W2_final_trough_75pct",
        "W3_amplitude_flip_75pct",
    ))
    scored_keys = [
        key for key in gates if key.startswith("P") or key.startswith("W")
    ]
    scored_passes = sum(bool(gates[key]) for key in scored_keys)
    if data_pass and core_pass and wave_pass and scored_passes >= 11:
        verdict = "SUPPORTED"
    elif (
        data_pass
        and wave_pass
        and sum(
            gates[key]
            for key in (
                "P1_ara_beats_persistence_cut_mae",
                "P2_ara_beats_linear_cut_mae",
                "P3_ara_beats_no_rotation_cut_mae",
            )
        )
        >= 2
    ):
        verdict = "PARTIALLY SUPPORTED"
    else:
        verdict = "NOT SUPPORTED"

    with METRICS_CSV.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(metric_rows[0]))
        writer.writeheader()
        writer.writerows(metric_rows)
    with TRAJECTORIES_CSV.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(trajectory_rows[0]))
        writer.writeheader()
        writer.writerows(trajectory_rows)
    with PERMUTATION_CSV.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["permutation_index", "cut_mae"])
        for index, value in enumerate(permutation_mae):
            writer.writerow([index, value])

    result_payload = {
        "test_id": "Q26-ARA9-LARGER-WAVE-v1",
        "ledger_id": "T282",
        "verdict": verdict,
        "test_class": "public-data, staged partially blind trajectory prediction",
        "source": {
            "doi": "10.5281/zenodo.14880901",
            "file": SOURCE.name,
            "md5": EXPECTED_SOURCE_MD5,
            "protocol_sha256": protocol_hash,
            "prediction_sha256": actual_prediction_hash,
        },
        "sample": {
            "all_trajectories": 32,
            "primary_trajectories": 28,
            "replication_trajectories": 4,
            "exposed_matrices_per_trajectory": DEV_COUNT,
            "hidden_matrices_per_trajectory": len(TARGET_INDICES),
            "primary_hidden_matrices": 112,
            "primary_hidden_cuts": 112 * 9,
        },
        "model_summary": model_summary,
        "trajectory_summary": {
            "ara_win_persistence_fraction": ara_win_persistence_fraction,
            "ridge_eligible_trajectories": len(ridge_eligible),
            "ridge_within_one_fraction": ridge_within_one,
            "trough_eligible_trajectories": len(trough_eligible),
            "trough_within_one_fraction": trough_within_one,
            "median_closure_wait_spearman": median_spearman,
            "final_trough_fraction": final_trough_fraction,
            "amplitude_crest_to_trough_fraction": amplitude_flip_fraction,
            "stable_orientation_flip_fraction": stable_orientation_flip_fraction,
            "interpretation": (
                "amplitude crest-to-trough with stable orientation"
                if amplitude_flip_fraction >= 0.75
                and stable_orientation_flip_fraction < 0.25
                else "mixed or unresolved orientation outcome"
            ),
        },
        "bootstrap": bootstrap,
        "permutation": {
            "draws": PERMUTATION_DRAWS,
            "seed": SEED,
            "observed_ara_cut_mae": observed_ara_mae,
            "permutation_mean_cut_mae": float(np.mean(permutation_mae)),
            "time_order_percentile": time_order_percentile,
        },
        "data_quality": quality_summary,
        "gates": gates,
        "gate_counts": {
            "data": sum(gates[key] for key in gates if key.startswith("D")),
            "data_total": sum(key.startswith("D") for key in gates),
            "scored": scored_passes,
            "scored_total": len(scored_keys),
        },
        "blindness_boundary": (
            "Coarse faster decoherence at higher temperature was published; "
            "exact target matrices, transition positions, orientation outcome, "
            "and model comparisons were sealed until prediction hashing."
        ),
    }
    canonical_json(RESULTS, result_payload)
    print(
        f"Q26 verdict: {verdict} — "
        f"{result_payload['gate_counts']['scored']}/"
        f"{result_payload['gate_counts']['scored_total']} scored gates"
    )
    print(
        "ARA / persistence / linear / no-rotation cut MAE: "
        f"{model_summary['ara']['cut_mae']:.6f} / "
        f"{model_summary['persistence']['cut_mae']:.6f} / "
        f"{model_summary['linear']['cut_mae']:.6f} / "
        f"{model_summary['no_rotation']['cut_mae']:.6f}"
    )
    print(
        "Larger wave: "
        f"median rho={median_spearman:.4f}, "
        f"final trough={final_trough_fraction:.1%}, "
        f"amplitude flips={amplitude_flip_fraction:.1%}, "
        f"stable orientation flips={stable_orientation_flip_fraction:.1%}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("prepare", "predict", "reveal"))
    args = parser.parse_args()
    {"prepare": prepare, "predict": predict, "reveal": reveal}[args.stage]()


if __name__ == "__main__":
    main()
