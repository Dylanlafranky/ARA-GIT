"""Independent arithmetic validator for Q42 saved results."""

from __future__ import annotations

import csv
import gzip
import json
import math
import os
import pathlib
import sys


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np

import q40_return_flow_relation_reversal_test as base


RESULTS = HERE / "Q42_ARA_DUAL_STRAND_FLOW_RESULTS.json"
STRANDS = HERE / "Q42_ARA_DUAL_STRAND_FLOW_STRANDS.csv.gz"
MATRICES = HERE / "Q42_ARA_DUAL_STRAND_FLOW_MATRICES.csv.gz"
PROFILES = HERE / "Q42_ARA_DUAL_STRAND_FLOW_PROFILES.npz"
VALIDATION = HERE / "Q42_ARA_DUAL_STRAND_FLOW_VALIDATION.json"
EPS = 1e-12


DATASETS = {
    "greedy": {
        "derived": (
            HERE
            / "public_data"
            / "q40_return_flow_inhomo_v1_greedy"
            / "q40_derived_cache.npz"
        ),
        "connected": (
            HERE
            / "public_data"
            / "q40_return_flow_inhomo_v1_greedy"
            / "q40_connected_cache.npy"
        ),
    },
    "landmax": {
        "derived": (
            HERE
            / "public_data"
            / "q41b_cadence_strand_inhomo_v1_landmax"
            / "q41b_derived_cache.npz"
        ),
        "connected": (
            HERE
            / "public_data"
            / "q41b_cadence_strand_inhomo_v1_landmax"
            / "q41b_connected_cache.npy"
        ),
    },
}


def read_rows(path: pathlib.Path) -> list[dict]:
    with gzip.open(path, "rt", newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def close(first: float, second: float, atol: float = 5e-7) -> bool:
    return bool(abs(first - second) <= atol)


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    strands = read_rows(STRANDS)
    matrices = read_rows(MATRICES)
    profiles = np.load(PROFILES)
    residual = np.asarray(profiles["residual"], dtype=np.float64)

    mismatches = []
    if len(strands) != residual.shape[0]:
        mismatches.append("strand/profile row count")
    if len(strands) != sum(
        item["scalar_pairs"] for item in result["inventory"].values()
    ):
        mismatches.append("strand/inventory row count")
    if len(matrices) != sum(
        item["matrix_cycles"] for item in result["inventory"].values()
    ):
        mismatches.append("matrix/inventory row count")

    for archive in DATASETS:
        indices = [
            index
            for index, row in enumerate(strands)
            if row["archive"] == archive
        ]
        maes = np.mean(np.abs(residual[indices]), axis=1)
        signed = np.mean(residual[indices], axis=1)
        expected_mae = result["scalar_strands"][archive]["closure_mae"][
            "median"
        ]
        expected_signed = result["scalar_strands"][archive][
            "closure_signed_mean"
        ]["median"]
        if not close(float(np.median(maes)), expected_mae):
            mismatches.append(f"{archive} scalar MAE median")
        if not close(float(np.median(signed)), expected_signed):
            mismatches.append(f"{archive} scalar signed median")

    matrix_lookup = {
        (
            row["archive"],
            int(row["seed"]),
            int(row["pair"]),
            int(row["cycle"]),
        ): row
        for row in matrices
    }
    checked = 0
    arithmetic_mismatches = 0
    max_alpha_error = 0.0
    max_other_error = 0.0
    max_orthogonality = 0.0
    for archive, paths in DATASETS.items():
        derived = np.load(paths["derived"])
        closure = np.asarray(derived["closure"], dtype=np.float32)
        connected = np.load(paths["connected"], mmap_mode="r")
        for seed in range(closure.shape[0]):
            for pair in range(closure.shape[2]):
                coordinate = base.coordinates(closure[seed, :, pair])
                if coordinate is None:
                    continue
                _u, _v, labels, direction, coherence, occupancy = coordinate
                if coherence < 0.80 or occupancy < 0.05:
                    continue
                windows = base.complete_windows(labels, direction, 250, 498)
                for cycle, window in enumerate(windows):
                    saved = matrix_lookup.get((archive, seed, pair, cycle))
                    if saved is None:
                        arithmetic_mismatches += 1
                        continue
                    c1, c2, c3, c4 = base.identities_for_window(
                        connected, seed, pair, window
                    )
                    relation = c1 - c2
                    movement = c4 - c3
                    relation_sq = float(np.sum(relation * relation))
                    if relation_sq <= EPS:
                        continue
                    alpha = float(np.sum(movement * relation) / relation_sq)
                    residual_matrix = movement - alpha * relation
                    along_sq = float(alpha * alpha * relation_sq)
                    residual_sq = float(np.sum(residual_matrix * residual_matrix))
                    along = float(
                        2
                        * along_sq
                        / (along_sq + residual_sq + EPS)
                    )
                    other = float(2 - along)
                    orthogonality = float(
                        abs(np.sum(residual_matrix * relation))
                        / (
                            np.linalg.norm(residual_matrix)
                            * np.linalg.norm(relation)
                            + EPS
                        )
                    )
                    alpha_error = abs(alpha - float(saved["alpha"]))
                    other_error = abs(other - float(saved["other_teara"]))
                    max_alpha_error = max(max_alpha_error, alpha_error)
                    max_other_error = max(max_other_error, other_error)
                    max_orthogonality = max(max_orthogonality, orthogonality)
                    if alpha_error > 5e-7 or other_error > 5e-7:
                        arithmetic_mismatches += 1
                    checked += 1

    if checked != len(matrices):
        mismatches.append(
            f"matrix recomputation count {checked} != {len(matrices)}"
        )
    if arithmetic_mismatches:
        mismatches.append(f"{arithmetic_mismatches} matrix arithmetic mismatches")

    output = {
        "status": "PASS" if not mismatches else "FAIL",
        "strand_rows": len(strands),
        "matrix_rows": len(matrices),
        "matrix_rows_recomputed": checked,
        "mismatches": mismatches,
        "max_alpha_error": max_alpha_error,
        "max_other_teara_error": max_other_error,
        "max_recomputed_orthogonality_error": max_orthogonality,
        "scalar_profile_rows": int(residual.shape[0]),
    }
    VALIDATION.write_text(
        json.dumps(output, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2), flush=True)
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
