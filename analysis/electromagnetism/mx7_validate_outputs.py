"""Independent arithmetic validation for the saved MX7 output packet."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


EXPECTED_SOURCE_SHA256 = "6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5"
QUADRANTS = ("AA", "AB", "BA", "BB")
QUADRANT_SIGNS = np.asarray([1.0, -1.0, -1.0, 1.0])
MODELS = {
    "flat_parent": "flat_N_per_m3",
    "mx5_first_moment": "first_moment_N_per_m3",
    "independent_phase_marginals": "marginal_N_per_m3",
    "joint_quadrant_triangle": "joint_N_per_m3",
    "conditioned_amplitude_pyramid": "pyramid_N_per_m3",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_cells(path: Path) -> tuple[dict[str, np.ndarray], list[tuple[int, int, int, str]]]:
    numeric = [
        "target_N_per_m3", "flat_N_per_m3", "first_moment_N_per_m3",
        "marginal_N_per_m3", "joint_N_per_m3", "pyramid_N_per_m3",
        "reassembled_N_per_m3", "absolute_charge_density_C_per_m3",
        "mean_abs_E_V_per_m", "charge_sign_mean", "field_sign_mean",
        "joint_sign_mean", "phase_coupling_covariance",
        "amplitude_relation_covariance_V_per_m", "phase_correction_N_per_m3",
        "amplitude_correction_N_per_m3", "mutual_information_bits",
    ]
    numeric.extend(f"p_{quadrant}" for quadrant in QUADRANTS)
    numeric.extend(f"mean_abs_E_{quadrant}_V_per_m" for quadrant in QUADRANTS)
    values = {name: [] for name in numeric}
    keys: list[tuple[int, int, int, str]] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            keys.append((int(row["z"]), int(row["y"]), int(row["x"]), row["component"]))
            for name in numeric:
                values[name].append(float(row[name]))
    return {name: np.asarray(column, dtype=float) for name, column in values.items()}, keys


def vector_metrics(target_rows: np.ndarray, estimate_rows: np.ndarray) -> dict[str, float]:
    target = target_rows.reshape(-1, 3)
    estimate = estimate_rows.reshape(-1, 3)
    target_flat = target.ravel()
    estimate_flat = estimate.ravel()
    target_norm = float(np.linalg.norm(target_flat))
    estimate_norm = float(np.linalg.norm(estimate_flat))
    vector_correlation = float(np.dot(target_flat, estimate_flat) / (target_norm * estimate_norm))
    nrmse = float(np.sqrt(np.mean((estimate_flat - target_flat) ** 2)) / np.std(target_flat))
    target_magnitude = np.linalg.norm(target, axis=1)
    estimate_magnitude = np.linalg.norm(estimate, axis=1)
    scale = max(float(np.max(target_magnitude)), float(np.max(estimate_magnitude)))
    active = (target_magnitude > scale * 1e-12) & (estimate_magnitude > scale * 1e-12)
    cosine = np.sum(target[active] * estimate[active], axis=1) / (
        target_magnitude[active] * estimate_magnitude[active]
    )
    angles = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return {
        "n_cells": int(len(target)),
        "vector_correlation": vector_correlation,
        "nrmse_by_target_std": nrmse,
        "median_angular_error_deg": float(np.median(angles)),
        "relative_l2": float(np.linalg.norm(estimate_flat - target_flat) / target_norm),
    }


def relative_l2(target: np.ndarray, estimate: np.ndarray) -> float:
    return float(np.linalg.norm(estimate - target) / np.linalg.norm(target))


def mutual_information(probabilities: np.ndarray) -> np.ndarray:
    total = np.sum(probabilities, axis=1, keepdims=True)
    p = np.divide(probabilities, total, out=np.zeros_like(probabilities), where=total > 0)
    q_a = p[:, 0] + p[:, 1]
    q_b = p[:, 2] + p[:, 3]
    e_a = p[:, 0] + p[:, 2]
    e_b = p[:, 1] + p[:, 3]
    independent = np.column_stack((q_a * e_a, q_a * e_b, q_b * e_a, q_b * e_b))
    terms = np.zeros_like(p)
    valid = (p > 0) & (independent > 0)
    terms[valid] = p[valid] * np.log2(p[valid] / independent[valid])
    return np.sum(terms, axis=1)


def relative_change(metric: str, baseline: float, candidate: float) -> float:
    denominator = max(abs(baseline), np.finfo(float).tiny)
    if metric == "vector_correlation":
        return (candidate - baseline) / denominator
    return (baseline - candidate) / denominator


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()

    results_path = args.results_dir / "MX7_PHASE_FIRST_INFORMATION3_PYRAMID_RESULTS.json"
    cells_path = args.results_dir / "MX7_PHASE_FIRST_INFORMATION3_PYRAMID_CELLS.csv"
    results = json.loads(results_path.read_text(encoding="utf-8"))
    cells, keys = read_cells(cells_path)

    row_order_pass = bool(
        len(keys) % 3 == 0
        and all(
            keys[index][0:3] == keys[index + 1][0:3] == keys[index + 2][0:3]
            and (keys[index][3], keys[index + 1][3], keys[index + 2][3]) == ("x", "y", "z")
            for index in range(0, len(keys), 3)
        )
    )
    target = cells["target_N_per_m3"]
    q = cells["absolute_charge_density_C_per_m3"]
    mean_magnitude = cells["mean_abs_E_V_per_m"]
    charge_sign = cells["charge_sign_mean"]
    field_sign = cells["field_sign_mean"]
    joint_sign = cells["joint_sign_mean"]
    probabilities = np.column_stack([cells[f"p_{name}"] for name in QUADRANTS])
    amplitudes = np.column_stack([cells[f"mean_abs_E_{name}_V_per_m"] for name in QUADRANTS])

    marginal = q * mean_magnitude * charge_sign * field_sign
    joint = q * mean_magnitude * joint_sign
    phase_correction = q * mean_magnitude * (joint_sign - charge_sign * field_sign)
    pyramid = q * np.sum(np.nan_to_num(probabilities * amplitudes, nan=0.0) * QUADRANT_SIGNS, axis=1)
    amplitude_correction = q * cells["amplitude_relation_covariance_V_per_m"]
    reassembled = marginal + phase_correction + amplitude_correction
    mi = mutual_information(probabilities)

    identity_errors = {
        "marginal_formula_relative_l2": relative_l2(cells["marginal_N_per_m3"], marginal),
        "joint_formula_relative_l2": relative_l2(cells["joint_N_per_m3"], joint),
        "phase_correction_formula_relative_l2": relative_l2(
            cells["phase_correction_N_per_m3"], phase_correction
        ),
        "joint_equals_marginal_plus_phase_relative_l2": relative_l2(
            joint, marginal + phase_correction
        ),
        "pyramid_formula_relative_l2": relative_l2(cells["pyramid_N_per_m3"], pyramid),
        "pyramid_to_target_relative_l2": relative_l2(target, pyramid),
        "full_reassembly_relative_l2": relative_l2(target, reassembled),
        "saved_reassembly_relative_l2": relative_l2(target, cells["reassembled_N_per_m3"]),
        "mutual_information_max_absolute_error_bits": float(
            np.max(np.abs(mi - cells["mutual_information_bits"]))
        ),
        "quadrant_probability_sum_max_absolute_error": float(
            np.max(np.abs(np.sum(probabilities, axis=1) - 1.0))
        ),
    }

    recalculated_metrics = {
        name: vector_metrics(target, cells[column]) for name, column in MODELS.items()
    }
    metric_differences: dict[str, dict[str, float]] = {}
    for name, recalculated in recalculated_metrics.items():
        reported = results["models"][name]
        metric_differences[name] = {
            metric: abs(float(value) - float(reported[metric]))
            for metric, value in recalculated.items()
        }

    marginal_metrics = recalculated_metrics["independent_phase_marginals"]
    joint_metrics = recalculated_metrics["joint_quadrant_triangle"]
    changes = {
        key: relative_change(key, marginal_metrics[key], joint_metrics[key])
        for key in ("vector_correlation", "nrmse_by_target_std", "median_angular_error_deg")
    }
    full_data_gate_checks = {
        "all_three_metrics_favourable": bool(all(value > 0 for value in changes.values())),
        "at_least_two_metrics_improve_ge_5_percent": bool(
            sum(value >= 0.05 for value in changes.values()) >= 2
        ),
        "residual_relative_l2_reduction": float(
            (marginal_metrics["relative_l2"] - joint_metrics["relative_l2"])
            / marginal_metrics["relative_l2"]
        ),
    }
    reported_gates = results["joint_phase_result"]["frozen_gates"]
    gate_differences = {
        "changes": {
            key: abs(value - reported_gates["favourable_relative_changes"][key])
            for key, value in changes.items()
        },
        "residual_relative_l2_reduction": abs(
            full_data_gate_checks["residual_relative_l2_reduction"]
            - reported_gates["residual_relative_l2_reduction"]
        ),
        "boolean_checks_match": bool(
            full_data_gate_checks["all_three_metrics_favourable"]
            == reported_gates["all_three_metrics_favourable"]
            and full_data_gate_checks["at_least_two_metrics_improve_ge_5_percent"]
            == reported_gates["at_least_two_metrics_improve_ge_5_percent"]
        ),
    }

    source_hash = sha256(args.source)
    maximum_metric_difference = max(
        value for model in metric_differences.values() for value in model.values()
    )
    maximum_identity_error = max(identity_errors.values())
    validation_pass = bool(
        source_hash == EXPECTED_SOURCE_SHA256
        and row_order_pass
        and len(keys) == 3 * int(results["data_quality"]["active_interior_cells"])
        and maximum_metric_difference <= 1e-12
        and maximum_identity_error <= 1e-12
        and max(gate_differences["changes"].values()) <= 1e-12
        and gate_differences["residual_relative_l2_reduction"] <= 1e-12
        and gate_differences["boolean_checks_match"]
    )
    validation = {
        "source_sha256": source_hash,
        "source_hash_match": source_hash == EXPECTED_SOURCE_SHA256,
        "cell_csv_rows": len(keys),
        "active_vector_cells": len(keys) // 3,
        "component_row_order_xyz_pass": row_order_pass,
        "independent_identity_errors": identity_errors,
        "recalculated_model_metrics": recalculated_metrics,
        "absolute_differences_from_reported_metrics": metric_differences,
        "maximum_reported_metric_absolute_difference": maximum_metric_difference,
        "recalculated_full_data_frozen_gate": full_data_gate_checks,
        "frozen_gate_differences": gate_differences,
        "validation_pass": validation_pass,
    }
    output = args.results_dir / "MX7_PHASE_FIRST_INFORMATION3_PYRAMID_VALIDATION.json"
    output.write_text(json.dumps(validation, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "validation_pass": validation_pass,
        "maximum_identity_error": maximum_identity_error,
        "maximum_reported_metric_absolute_difference": maximum_metric_difference,
    }, indent=2))


if __name__ == "__main__":
    main()
