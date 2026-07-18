"""Independent spot-validation of exported MX5 results.

This validator reads the CSV and JSON products rather than importing the MX5
analysis functions.  It independently recomputes the headline vector metrics,
the two exact identity errors and TE-ARA-style coordinate bounds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


EXPECTED_SOURCE_SHA256 = (
    "6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def vectors(frame: pd.DataFrame, prefix: str) -> np.ndarray:
    return frame[[f"{prefix}_{component}" for component in "xyz"]].to_numpy(float)


def headline_metrics(target: np.ndarray, estimate: np.ndarray) -> dict[str, float]:
    target_flat = target.ravel()
    estimate_flat = estimate.ravel()
    error = estimate_flat - target_flat
    target_norm = np.linalg.norm(target_flat)
    estimate_norm = np.linalg.norm(estimate_flat)
    target_magnitude = np.linalg.norm(target, axis=1)
    estimate_magnitude = np.linalg.norm(estimate, axis=1)
    valid = (target_magnitude > 0) & (estimate_magnitude > 0)
    cosine = np.sum(target[valid] * estimate[valid], axis=1) / (
        target_magnitude[valid] * estimate_magnitude[valid]
    )
    return {
        "vector_correlation": float(
            np.dot(target_flat, estimate_flat) / (target_norm * estimate_norm)
        ),
        "nrmse_by_target_std": float(
            np.sqrt(np.mean(error**2)) / np.std(target_flat)
        ),
        "median_angular_error_deg": float(
            np.median(np.degrees(np.arccos(np.clip(cosine, -1, 1))))
        ),
    }


def relative_l2(target: np.ndarray, estimate: np.ndarray) -> float:
    return float(np.linalg.norm(estimate - target) / np.linalg.norm(target))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()

    observed_hash = sha256(args.source)
    if observed_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError(f"Unexpected source hash: {observed_hash}")

    results_path = args.results_dir / "MX5_CHILD_ARA_TEARA_CLOSURE_RESULTS.json"
    cells_path = args.results_dir / "MX5_CHILD_ARA_TEARA_GRID_CELLS.csv"
    results = json.loads(results_path.read_text(encoding="utf-8"))
    frame = pd.read_csv(cells_path)
    active = frame.loc[frame["active_interior"] == 1].copy()
    if len(active) != 9266:
        raise ValueError(f"Expected 9266 active cells; found {len(active)}")

    target = vectors(active, "child_total")
    child_ara = vectors(active, "child_ara")
    flat = vectors(active, "flat_total")
    other = vectors(active, "other_total")
    first = vectors(active, "first_moment_total")
    exact_recovered = flat + other

    recomputed = {
        "version_a_grid_relative_l2": relative_l2(target, child_ara),
        "version_b_grid_relative_l2": relative_l2(target, exact_recovered),
        "flat_total": headline_metrics(target, flat),
        "first_moment_total": headline_metrics(target, first),
        "te_force_coherence_min": float(active["te_force_coherence"].min()),
        "te_force_coherence_max": float(active["te_force_coherence"].max()),
        "x_other_min": float(active["x_other"].min()),
        "x_other_max": float(active["x_other"].max()),
        "fraction_x_other_gt_1": float(np.mean(active["x_other"] > 1.0)),
    }

    claimed_first = results["version_c_first_moment_gradient"]["channels"]["total"]
    claimed_flat = results["flat_parent_recalculation"]["channels"]["total"]
    comparisons = {
        "source_hash": observed_hash == results["source"]["sha256"],
        "version_a": bool(
            abs(
                recomputed["version_a_grid_relative_l2"]
                - results["version_a_exact_child_ara"]["grid_relative_l2"]
            )
            <= 1e-12
        ),
        "version_b": bool(
            abs(
                recomputed["version_b_grid_relative_l2"]
                - results["version_b_parent_plus_exact_other"]["grid_relative_l2"]
            )
            <= 1e-12
        ),
        "te_force_bounds": bool(
            recomputed["te_force_coherence_min"] >= -1e-12
            and recomputed["te_force_coherence_max"] <= 2 + 1e-12
        ),
        "x_other_bounds": bool(
            recomputed["x_other_min"] >= -1e-12
            and recomputed["x_other_max"] <= 2 + 1e-12
        ),
        "fraction_x_other": bool(
            abs(
                recomputed["fraction_x_other_gt_1"]
                - results["version_b_parent_plus_exact_other"]["diagnostics"][
                    "fraction_other_dominant_x_gt_1"
                ]
            )
            <= 1e-12
        ),
    }
    for metric in (
        "vector_correlation",
        "nrmse_by_target_std",
        "median_angular_error_deg",
    ):
        comparisons[f"flat_{metric}"] = bool(
            abs(recomputed["flat_total"][metric] - claimed_flat[metric]) <= 1e-12
        )
        comparisons[f"first_moment_{metric}"] = bool(
            abs(recomputed["first_moment_total"][metric] - claimed_first[metric])
            <= 1e-12
        )

    output = {
        "test": "MX5 independent exported-output validation",
        "source_sha256": observed_hash,
        "active_cells": int(len(active)),
        "recomputed": recomputed,
        "checks": comparisons,
        "validation_pass": bool(all(comparisons.values())),
    }
    output_path = args.results_dir / "MX5_CHILD_ARA_TEARA_VALIDATION.json"
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))

    if not output["validation_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
