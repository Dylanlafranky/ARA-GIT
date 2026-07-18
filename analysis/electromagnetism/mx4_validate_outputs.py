"""Independent arithmetic validation for the saved MX4 output packet."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


EXPECTED_SOURCE_SHA256 = (
    "6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_columns(path: Path, names: list[str], active_only: bool = False) -> dict[str, np.ndarray]:
    values = {name: [] for name in names}
    with path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if active_only and int(row["active_interior"]) != 1:
                continue
            for name in names:
                values[name].append(float(row[name]))
    return {name: np.asarray(column, dtype=float) for name, column in values.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()

    results_path = args.results_dir / "MX4_LORENTZ_ARA_RESULTS.json"
    particle_path = args.results_dir / "MX4_LORENTZ_ARA_PARTICLE_SAMPLE.csv"
    grid_path = args.results_dir / "MX4_LORENTZ_ARA_GRID_CELLS.csv"
    results = json.loads(results_path.read_text(encoding="utf-8"))

    source_hash = sha256(args.source)
    particle = read_columns(
        particle_path,
        [
            "electric_force_N",
            "magnetic_force_N",
            "channel_cosine",
            "resultant_force_N",
        ],
    )
    electric = particle["electric_force_N"]
    magnetic = particle["magnetic_force_N"]
    cosine = particle["channel_cosine"]
    reconstructed = np.sqrt(
        np.maximum(0.0, electric**2 + magnetic**2 + 2.0 * electric * magnetic * cosine)
    )
    observed = particle["resultant_force_N"]
    sample_relative_l2 = float(np.linalg.norm(reconstructed - observed) / np.linalg.norm(observed))

    names = [
        "particle_first_total_x_N_per_m3",
        "particle_first_total_y_N_per_m3",
        "particle_first_total_z_N_per_m3",
        "field_first_total_x_N_per_m3",
        "field_first_total_y_N_per_m3",
        "field_first_total_z_N_per_m3",
    ]
    grid = read_columns(grid_path, names, active_only=True)
    target = np.column_stack([grid[name] for name in names[:3]])
    estimate = np.column_stack([grid[name] for name in names[3:]])
    target_flat = target.ravel()
    estimate_flat = estimate.ravel()
    vector_correlation = float(
        np.dot(target_flat, estimate_flat)
        / (np.linalg.norm(target_flat) * np.linalg.norm(estimate_flat))
    )
    flattened_pearson = float(np.corrcoef(target_flat, estimate_flat)[0, 1])
    nrmse = float(
        np.sqrt(np.mean((estimate_flat - target_flat) ** 2)) / np.std(target_flat)
    )
    magnitude_ratio = float(np.linalg.norm(estimate_flat) / np.linalg.norm(target_flat))
    target_magnitude = np.linalg.norm(target, axis=1)
    estimate_magnitude = np.linalg.norm(estimate, axis=1)
    scale = max(float(np.max(target_magnitude)), float(np.max(estimate_magnitude)))
    active = (target_magnitude > scale * 1e-12) & (estimate_magnitude > scale * 1e-12)
    cos_angle = np.sum(target[active] * estimate[active], axis=1) / (
        target_magnitude[active] * estimate_magnitude[active]
    )
    median_angle = float(np.median(np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))))

    reported = results["mx4_l2_grid_rung"]["channels"]["total"]
    recalculated = {
        "n_cells": int(len(target)),
        "vector_correlation": vector_correlation,
        "flattened_pearson": flattened_pearson,
        "nrmse_by_target_std": nrmse,
        "l2_magnitude_ratio": magnitude_ratio,
        "median_angular_error_deg": median_angle,
    }
    differences = {
        key: abs(float(recalculated[key]) - float(reported[key]))
        for key in recalculated
        if key != "n_cells"
    }
    validation = {
        "source_sha256": source_hash,
        "source_hash_match": source_hash == EXPECTED_SOURCE_SHA256,
        "particle_sample_count": int(len(observed)),
        "particle_sample_law_of_cosines_relative_l2": sample_relative_l2,
        "grid_metrics_recalculated_from_csv": recalculated,
        "absolute_differences_from_reported_json": differences,
        "grid_cell_count_match": int(recalculated["n_cells"]) == int(reported["n_cells"]),
        "all_grid_metric_differences_le_1e-12": bool(
            all(value <= 1e-12 for value in differences.values())
        ),
        "validation_pass": bool(
            source_hash == EXPECTED_SOURCE_SHA256
            and sample_relative_l2 <= 1e-12
            and int(recalculated["n_cells"]) == int(reported["n_cells"])
            and all(value <= 1e-12 for value in differences.values())
        ),
    }
    output = args.results_dir / "MX4_LORENTZ_ARA_VALIDATION.json"
    output.write_text(json.dumps(validation, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(validation, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
