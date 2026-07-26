#!/usr/bin/env python3
"""Independent validation for Q26.

This file deliberately does not import the primary runner. It reparses the
public source, rebuilds the connected tensors and predictors, recomputes the
headline metrics, bootstrap, permutation null, gates, and verdict.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "public_data" / "q26_temperature_ara9" / "SuppFigure10.csv"
PROTOCOL = HERE / "Q26_ARA9_LARGER_WAVE_TRAJECTORY_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q26_ARA9_LARGER_WAVE_TRAJECTORY_PROTOCOL_v1_FROZEN.sha256"
GEOMETRY = HERE / "Q26_ARA9_LARGER_WAVE_GEOMETRY_PACKET.json"
SEALED = HERE / "Q26_ARA9_LARGER_WAVE_SEALED_TARGET_PACKET.json"
PREDICTIONS = HERE / "Q26_ARA9_LARGER_WAVE_PREDICTIONS.json"
PREDICTIONS_SHA = HERE / "Q26_ARA9_LARGER_WAVE_PREDICTIONS.sha256"
PERMUTATIONS = HERE / "Q26_ARA9_LARGER_WAVE_PERMUTATION.csv"
RESULTS = HERE / "Q26_ARA9_LARGER_WAVE_RESULTS.json"
OUTPUT = HERE / "Q26_ARA9_LARGER_WAVE_VALIDATION.json"

SOURCE_MD5 = "9a9e3abac0ee8f80535e17ec72313919"
PROTOCOL_HASH = (
    "0bd8f2a0ee96733e0411d477a5c808c4ebd100b083b84b30108d05ed110347e6"
)
TEMPS = (0.1, 0.2, 0.3, 0.5, 0.7, 0.85, 1.0, 1.1)
STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
WAITS = np.asarray(
    [1.00, 1.99, 3.98, 7.94, 15.85, 31.62, 63.09, 125.89, 251.19, 501.18, 1000.00]
)
DEV = 7
TARGET_INDEX = tuple(range(7, 11))
MODELS = ("ara", "persistence", "linear", "no_rotation", "zero")
PRIMARY_TEMPS = set(TEMPS[1:])
BOOT_DRAWS = 5000
PERM_DRAWS = 999
SEED = 26026

I = np.eye(2, dtype=complex)
X = np.asarray([[0, 1], [1, 0]], dtype=complex)
Y = np.asarray([[0, -1j], [1j, 0]], dtype=complex)
Z = np.asarray([[1, 0], [0, -1]], dtype=complex)
P = (I, X, Y, Z)


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(label)

    def close(self) -> dict[str, Any]:
        return {
            "status": "PASS" if not self.failures else "FAIL",
            "checks": self.checks,
            "passed": self.checks - len(self.failures),
            "failures": self.failures,
        }


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse() -> np.ndarray:
    rows = []
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        for row in csv.reader(stream):
            if any(value.strip() for value in row):
                rows.append([float(value) for value in row])
    return np.asarray(rows, dtype=float).reshape(8, 4, 11, 16)


def connected(c: np.ndarray) -> np.ndarray:
    e = 4.0 * c
    a = e[[4, 8, 12]]
    b = e[[1, 2, 3]]
    t = e[[5, 6, 7, 9, 10, 11, 13, 14, 15]].reshape(3, 3)
    return t - np.outer(a, b)


def rho(c: np.ndarray) -> np.ndarray:
    value = np.zeros((4, 4), dtype=complex)
    for i in range(4):
        for j in range(4):
            value += c[4 * i + j] * np.kron(P[i], P[j])
    return 0.5 * (value + value.conj().T)


def h(matrix: np.ndarray) -> float:
    return float(abs(np.linalg.det(matrix)) ** (1 / 3))


def cls(x: float) -> str:
    return "crest" if x >= 1.5 else "trough" if x <= 0.5 else "handover"


def fixed_basis(vt: np.ndarray) -> np.ndarray:
    result = vt[:2].copy()
    for vector in result:
        pivot = int(np.argmax(np.abs(vector)))
        if vector[pivot] < 0:
            vector *= -1
    return result


def forecast(early: np.ndarray) -> tuple[dict[str, np.ndarray], np.ndarray]:
    q = early[:, :2, :2].reshape(DEV, 4)
    basis = fixed_basis(np.linalg.svd(q, full_matrices=False)[2])
    z = q @ basis.T
    radius = np.linalg.norm(z, axis=1)
    radial = np.polyfit(WAITS[:DEV], np.log(np.maximum(radius, 1e-12)), 1)
    radial[0] = min(float(radial[0]), 0.0)
    angle = np.unwrap(np.arctan2(z[:, 1], z[:, 0]))
    angular = np.polyfit(WAITS[:DEV], angle, 1)
    target_r = np.exp(np.polyval(radial, WAITS[DEV:]))
    target_a = np.polyval(angular, WAITS[DEV:])
    target_z = np.column_stack((target_r * np.cos(target_a), target_r * np.sin(target_a)))
    target_q = target_z @ basis

    ara = np.zeros((4, 3, 3))
    ara[:, :2, :2] = target_q.reshape(-1, 2, 2)
    ara[:, 2, 2] = np.median(early[-3:, 2, 2])
    persistence = np.repeat(early[-1:,:,:], 4, axis=0)
    linear = np.zeros_like(ara)
    for i in range(3):
        for j in range(3):
            linear[:, i, j] = np.polyval(
                np.polyfit(WAITS[:DEV], early[:, i, j], 1), WAITS[DEV:]
            )
    linear = np.clip(linear, -1, 1)
    no_rotation = np.zeros_like(ara)
    last = q[-1]
    direction = last / np.linalg.norm(last) if np.linalg.norm(last) > 1e-12 else last * 0
    no_rotation[:, :2, :2] = (target_r[:, None] * direction).reshape(-1, 2, 2)
    no_rotation[:, 2, 2] = ara[:, 2, 2]
    return {
        "ara": ara,
        "persistence": persistence,
        "linear": linear,
        "no_rotation": no_rotation,
        "zero": np.zeros_like(ara),
    }, basis


def phase(matrix: np.ndarray, basis: np.ndarray) -> float:
    z = matrix[:2, :2].reshape(4) @ basis.T
    return float(math.atan2(float(z[1]), float(z[0])))


def angle_error(a: float, b: float) -> float:
    return float(abs(math.atan2(math.sin(a - b), math.cos(a - b))))


def ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    result = np.empty(len(values))
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[order[end]] == values[order[start]]:
            end += 1
        result[order[start:end]] = 0.5 * (start + end - 1) + 1
        start = end
    return result


def rho_s(left: np.ndarray, right: np.ndarray) -> float:
    a, b = ranks(left), ranks(right)
    return float(np.corrcoef(a, b)[0, 1])


def first_below(values: list[float], threshold: float) -> int | None:
    return next((i for i, value in enumerate(values) if value <= threshold), None)


def orientation_flip(matrices: list[np.ndarray], xs: list[float]) -> bool:
    reliable = [
        (i, np.sign(np.linalg.det(matrix)))
        for i, (matrix, x) in enumerate(zip(matrices, xs))
        if x > 0.5 and abs(np.linalg.det(matrix)) > 1e-12
    ]
    if not reliable:
        return False
    initial = reliable[0][1]
    return any(
        left[1] == -initial
        and right[1] == -initial
        and right[0] == left[0] + 1
        for left, right in zip(reliable[:-1], reliable[1:])
    )


def bootstrap(rows: list[dict[str, Any]], left: str, right: str) -> float:
    table: dict[tuple[float, str], dict[str, float]] = {}
    for row in rows:
        table.setdefault((row["temp"], row["state"]), {})[row["model"]] = row["mae"]
    keys = sorted(table)
    differences = np.asarray([table[key][left] - table[key][right] for key in keys])
    rng = np.random.default_rng(SEED + sum(map(ord, left + right)))
    sample = rng.integers(0, len(keys), size=(BOOT_DRAWS, len(keys)))
    return float(np.mean(np.mean(differences[sample], axis=1) < 0))


def main() -> None:
    audit = Audit()
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    sealed = json.loads(SEALED.read_text(encoding="utf-8"))
    pred_file = json.loads(PREDICTIONS.read_text(encoding="utf-8"))

    audit.check(digest(SOURCE, "md5") == SOURCE_MD5, "source md5")
    audit.check(digest(PROTOCOL, "sha256") == PROTOCOL_HASH, "protocol hash")
    audit.check(PROTOCOL_SHA.read_text().split()[0] == PROTOCOL_HASH, "protocol sha file")
    prediction_hash = digest(PREDICTIONS, "sha256")
    audit.check(PREDICTIONS_SHA.read_text().split()[0] == prediction_hash, "prediction hash")

    source = parse()
    audit.check(source.shape == (8, 4, 11, 16), "source shape")
    audit.check(bool(np.all(np.isfinite(source))), "source finite")
    audit.check(float(np.max(abs(source[:,:,:,0] - 0.25))) <= 1e-12, "cII")

    c_all = np.empty((8, 4, 11, 3, 3))
    minimum_eigenvalue = math.inf
    maximum_trace_error = 0.0
    maximum_hermiticity = 0.0
    psd_count = 0
    for ti in range(8):
        for si in range(4):
            for wi in range(11):
                c_all[ti, si, wi] = connected(source[ti, si, wi])
                density = rho(source[ti, si, wi])
                eig_min = float(np.min(np.linalg.eigvalsh(density)))
                minimum_eigenvalue = min(minimum_eigenvalue, eig_min)
                maximum_trace_error = max(
                    maximum_trace_error, float(abs(np.trace(density) - 1))
                )
                maximum_hermiticity = max(
                    maximum_hermiticity,
                    float(np.max(abs(density - density.conj().T))),
                )
                psd_count += eig_min >= -1e-10

    geometry_map = {
        (row["temperature_K"], row["state"]): np.asarray(row["connected_matrices"])
        for row in geometry["records"]
    }
    sealed_map = {
        (row["temperature_K"], row["state"]): np.asarray(row["connected_matrices"])
        for row in sealed["records"]
    }
    for ti, temp in enumerate(TEMPS):
        for si, state in enumerate(STATES):
            audit.check(
                np.allclose(geometry_map[(temp, state)], c_all[ti, si, :DEV], atol=1e-12),
                f"geometry {temp} {state}",
            )
            audit.check(
                np.allclose(sealed_map[(temp, state)], c_all[ti, si, DEV:], atol=1e-12),
                f"sealed {temp} {state}",
            )

    prediction_map = {
        (row["temperature_K"], row["state"], row["wait_index"], row["model"]):
        np.asarray(row["connected_matrix"])
        for row in pred_file["predictions"]
    }
    basis_map: dict[tuple[float, str], np.ndarray] = {}
    rebuilt: dict[tuple[float, str], dict[str, np.ndarray]] = {}
    for ti, temp in enumerate(TEMPS):
        for si, state in enumerate(STATES):
            models, basis = forecast(c_all[ti, si, :DEV])
            rebuilt[(temp, state)] = models
            basis_map[(temp, state)] = basis
            for model in MODELS:
                frozen = np.asarray([
                    prediction_map[(temp, state, wi, model)]
                    for wi in TARGET_INDEX
                ])
                audit.check(
                    np.allclose(frozen, models[model], atol=1e-12),
                    f"prediction {temp} {state} {model}",
                )

    primary_rows = []
    trajectories = []
    for ti, temp in enumerate(TEMPS):
        if temp not in PRIMARY_TEMPS:
            continue
        for si, state in enumerate(STATES):
            actual = c_all[ti, si, DEV:]
            early = c_all[ti, si, :DEV]
            basis = basis_map[(temp, state)]
            first_h = h(early[0])
            actual_full = list(early) + list(actual)
            h_full = [h(matrix) for matrix in actual_full]
            x_full = [2 * value / first_h for value in h_full]
            actual_ridge = first_below(x_full, 1.0)
            actual_trough = first_below(x_full, 0.5)
            for model in MODELS:
                predicted = rebuilt[(temp, state)][model]
                errors = abs(predicted - actual)
                closure_errors = [abs(h(p) - h(a)) for p, a in zip(predicted, actual)]
                phase_errors = [
                    angle_error(phase(p, basis), phase(a, basis))
                    for p, a in zip(predicted, actual)
                ]
                class_match = [
                    cls(2 * h(p) / first_h) == cls(2 * h(a) / first_h)
                    for p, a in zip(predicted, actual)
                ]
                predicted_full = list(early) + list(predicted)
                predicted_x = [2 * h(matrix) / first_h for matrix in predicted_full]
                pred_ridge = first_below(predicted_x, 1.0)
                pred_trough = first_below(predicted_x, 0.5)
                primary_rows.extend(
                    {
                        "model": model,
                        "cut_mae": float(np.mean(abs(p - a))),
                        "cut_rmse": float(np.sqrt(np.mean((p - a) ** 2))),
                        "closure_error": abs(h(p) - h(a)),
                        "phase_error": angle_error(phase(p, basis), phase(a, basis)),
                        "class_match": cls(2 * h(p) / first_h) == cls(2 * h(a) / first_h),
                    }
                    for p, a in zip(predicted, actual)
                )
                trajectories.append({
                    "temp": temp,
                    "state": state,
                    "model": model,
                    "mae": float(np.mean(errors)),
                    "rmse": float(np.sqrt(np.mean(errors ** 2))),
                    "closure_mae": float(np.mean(closure_errors)),
                    "phase_mae": float(np.mean(phase_errors)),
                    "class_accuracy": float(np.mean(class_match)),
                    "actual_ridge": actual_ridge,
                    "pred_ridge": pred_ridge,
                    "actual_trough": actual_trough,
                    "pred_trough": pred_trough,
                    "spearman": rho_s(WAITS, np.asarray(h_full)),
                    "final_x": x_full[-1],
                    "flip": orientation_flip(actual_full, x_full),
                })

    summaries: dict[str, dict[str, float]] = {}
    for model in MODELS:
        rows = [row for row in primary_rows if row["model"] == model]
        tr = [row for row in trajectories if row["model"] == model]
        summaries[model] = {
            "cut_mae": float(np.mean([row["cut_mae"] for row in rows])),
            "cut_rmse": float(np.sqrt(np.mean([row["cut_rmse"] ** 2 for row in rows]))),
            "closure_mae": float(np.mean([row["closure_error"] for row in rows])),
            "phase_mae_rad": float(np.mean([row["phase_error"] for row in rows])),
            "class_accuracy": float(np.mean([row["class_match"] for row in rows])),
            "trajectory_cut_mae_median": float(np.median([row["mae"] for row in tr])),
        }
        for metric, value in summaries[model].items():
            audit.check(
                math.isclose(value, result["model_summary"][model][metric], abs_tol=1e-12),
                f"summary {model} {metric}",
            )

    ara_rows = [row for row in trajectories if row["model"] == "ara"]
    persistence = {
        (row["temp"], row["state"]): row
        for row in trajectories if row["model"] == "persistence"
    }
    win_fraction = float(np.mean([
        row["mae"] < persistence[(row["temp"], row["state"])]["mae"]
        for row in ara_rows
    ]))
    ridge_eligible = [
        row for row in ara_rows
        if row["actual_ridge"] is not None and row["actual_ridge"] >= DEV
    ]
    trough_eligible = [
        row for row in ara_rows
        if row["actual_trough"] is not None and row["actual_trough"] >= DEV
    ]
    ridge_within = float(np.mean([
        row["pred_ridge"] is not None
        and abs(row["pred_ridge"] - row["actual_ridge"]) <= 1
        for row in ridge_eligible
    ]))
    trough_within = float(np.mean([
        row["pred_trough"] is not None
        and abs(row["pred_trough"] - row["actual_trough"]) <= 1
        for row in trough_eligible
    ]))
    median_spearman = float(np.median([row["spearman"] for row in ara_rows]))
    final_trough = float(np.mean([row["final_x"] <= 0.5 for row in ara_rows]))
    amplitude_flip = final_trough
    orientation_fraction = float(np.mean([row["flip"] for row in ara_rows]))

    trajectory_values = {
        "ara_win_persistence_fraction": win_fraction,
        "ridge_eligible_trajectories": len(ridge_eligible),
        "ridge_within_one_fraction": ridge_within,
        "trough_eligible_trajectories": len(trough_eligible),
        "trough_within_one_fraction": trough_within,
        "median_closure_wait_spearman": median_spearman,
        "final_trough_fraction": final_trough,
        "amplitude_crest_to_trough_fraction": amplitude_flip,
        "stable_orientation_flip_fraction": orientation_fraction,
    }
    for metric, value in trajectory_values.items():
        audit.check(
            math.isclose(value, result["trajectory_summary"][metric], abs_tol=1e-12),
            f"trajectory {metric}",
        )

    boot = {
        "ara_lower_mae_than_persistence": bootstrap(trajectories, "ara", "persistence"),
        "ara_lower_mae_than_linear": bootstrap(trajectories, "ara", "linear"),
        "ara_lower_mae_than_no_rotation": bootstrap(trajectories, "ara", "no_rotation"),
    }
    for metric, value in boot.items():
        audit.check(
            math.isclose(value, result["bootstrap"][metric], abs_tol=1e-12),
            f"bootstrap {metric}",
        )

    rng = np.random.default_rng(SEED)
    perm_values = []
    primary_order = sorted(
        (
            (ti, si, temp, state)
            for ti, temp in enumerate(TEMPS)
            if temp in PRIMARY_TEMPS
            for si, state in enumerate(STATES)
        ),
        key=lambda item: (item[2], item[3]),
    )
    for _ in range(PERM_DRAWS):
        errors = []
        for ti, si, _temp, _state in primary_order:
            shuffled = c_all[ti, si, :DEV][rng.permutation(DEV)]
            predicted = forecast(shuffled)[0]["ara"]
            errors.extend(abs(predicted - c_all[ti, si, DEV:]).reshape(-1))
        perm_values.append(float(np.mean(errors)))
    with PERMUTATIONS.open(newline="", encoding="utf-8") as stream:
        saved_perm = np.asarray([float(row["cut_mae"]) for row in csv.DictReader(stream)])
    audit.check(np.allclose(perm_values, saved_perm, atol=1e-12), "permutation values")
    percentile = float(np.mean(np.asarray(perm_values) > summaries["ara"]["cut_mae"]))
    audit.check(
        math.isclose(percentile, result["permutation"]["time_order_percentile"], abs_tol=1e-12),
        "permutation percentile",
    )

    quality = {
        "record_count": 352,
        "maximum_trace_error": maximum_trace_error,
        "maximum_hermiticity_residual": maximum_hermiticity,
        "minimum_eigenvalue": minimum_eigenvalue,
        "fraction_positive_semidefinite_at_minus_1e_10": psd_count / 352,
    }
    for metric, value in quality.items():
        audit.check(
            math.isclose(value, result["data_quality"][metric], abs_tol=1e-12),
            f"quality {metric}",
        )

    gates = {
        "D1_source_checksum": digest(SOURCE, "md5") == SOURCE_MD5,
        "D2_schema_8x4x11x16": source.shape == (8, 4, 11, 16),
        "D3_cII_invariant": float(np.max(abs(source[:,:,:,0] - 0.25))) <= 1e-12,
        "D4_predictions_frozen_before_reveal": (
            len([
                row for row in pred_file["predictions"]
                if row["temperature_K"] in PRIMARY_TEMPS and row["model"] == "ara"
            ]) == 112
            and PREDICTIONS_SHA.read_text().split()[0] == prediction_hash
        ),
        "P1_ara_beats_persistence_cut_mae": summaries["ara"]["cut_mae"] < summaries["persistence"]["cut_mae"],
        "P2_ara_beats_linear_cut_mae": summaries["ara"]["cut_mae"] < summaries["linear"]["cut_mae"],
        "P3_ara_beats_no_rotation_cut_mae": summaries["ara"]["cut_mae"] < summaries["no_rotation"]["cut_mae"],
        "P4_ara_beats_persistence_70pct_trajectories": win_fraction >= 0.70,
        "P5_ara_beats_persistence_closure_mae": summaries["ara"]["closure_mae"] < summaries["persistence"]["closure_mae"],
        "P6_ara_beats_no_rotation_phase_error": summaries["ara"]["phase_mae_rad"] < summaries["no_rotation"]["phase_mae_rad"],
        "P7_class_accuracy_70pct": summaries["ara"]["class_accuracy"] >= 0.70,
        "P8_ridge_within_one_60pct": ridge_within >= 0.60,
        "P9_trough_within_one_60pct": trough_within >= 0.60,
        "W1_median_spearman_at_most_minus_0p70": median_spearman <= -0.70,
        "W2_final_trough_75pct": final_trough >= 0.75,
        "W3_amplitude_flip_75pct": amplitude_flip >= 0.75,
        "W4_time_order_beats_95pct_permutations": percentile >= 0.95,
        "W5_bootstrap_95pct_vs_persistence_and_linear": (
            boot["ara_lower_mae_than_persistence"] >= 0.95
            and boot["ara_lower_mae_than_linear"] >= 0.95
        ),
    }
    audit.check(gates == result["gates"], "gate dictionary")
    data_ok = all(value for key, value in gates.items() if key.startswith("D"))
    core_ok = all(gates[key] for key in (
        "P1_ara_beats_persistence_cut_mae",
        "P2_ara_beats_linear_cut_mae",
        "P3_ara_beats_no_rotation_cut_mae",
    ))
    wave_ok = all(gates[key] for key in (
        "W1_median_spearman_at_most_minus_0p70",
        "W2_final_trough_75pct",
        "W3_amplitude_flip_75pct",
    ))
    scored = sum(value for key, value in gates.items() if key[0] in "PW")
    if data_ok and core_ok and wave_ok and scored >= 11:
        verdict = "SUPPORTED"
    elif data_ok and wave_ok and sum(gates[key] for key in (
        "P1_ara_beats_persistence_cut_mae",
        "P2_ara_beats_linear_cut_mae",
        "P3_ara_beats_no_rotation_cut_mae",
    )) >= 2:
        verdict = "PARTIALLY SUPPORTED"
    else:
        verdict = "NOT SUPPORTED"
    audit.check(verdict == result["verdict"], "verdict")

    payload = {
        "test_id": "Q26-ARA9-LARGER-WAVE-v1-validation",
        "validation": audit.close(),
        "independence": (
            "Reparsed source and independently rebuilt tensors, predictions, "
            "metrics, bootstrap, permutation null, gates, and verdict without "
            "importing the primary runner."
        ),
        "recomputed": {
            "ara_cut_mae": summaries["ara"]["cut_mae"],
            "persistence_cut_mae": summaries["persistence"]["cut_mae"],
            "linear_cut_mae": summaries["linear"]["cut_mae"],
            "no_rotation_cut_mae": summaries["no_rotation"]["cut_mae"],
            "median_spearman": median_spearman,
            "amplitude_flip_fraction": amplitude_flip,
            "stable_orientation_flip_fraction": orientation_fraction,
            "time_order_percentile": percentile,
            "verdict": verdict,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    status = payload["validation"]["status"]
    print(
        f"Q26 independent validation: {status} — "
        f"{payload['validation']['passed']}/{payload['validation']['checks']} checks"
    )
    if audit.failures:
        for failure in audit.failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
