"""Independent validation of the Q39A post-result return-flow audit.

This validator does not import the audit module. It independently reloads the
Q39 connected matrices, reconstructs a deterministic sample of cycles, and
checks the saved Q39A table and headline counts.
"""

from __future__ import annotations

import csv
import gzip
import json
import os
import pathlib
import sys


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import numpy as np


DATA = HERE / "public_data" / "q39_information3_strongmax"
CONNECTED = DATA / "q39_connected_cache.npy"
RESULTS = HERE / "Q39A_POST_RESULT_SEAM_PARITY_RESULTS.json"
CYCLES = HERE / "Q39A_POST_RESULT_SEAM_PARITY_CYCLES.csv.gz"
OUTPUT = HERE / "Q39A_POST_RESULT_SEAM_PARITY_VALIDATION.json"
FIGURES = (
    HERE / "Q39A_POST_RESULT_SEAM_PARITY_DIAGNOSTICS.png",
    HERE / "Q39A_POST_RESULT_SEAM_PARITY_DIAGNOSTICS.svg",
    HERE / "Q39A_POST_RESULT_PURITY_NORMALIZATION_DIAGNOSTICS.png",
    HERE / "Q39A_POST_RESULT_PURITY_NORMALIZATION_DIAGNOSTICS.svg",
)

EPS = 1e-12
TOLERANCE = 5e-10


def matrix_mean(
    connected: np.ndarray, seed: int, pair: int, start: int, end: int
) -> np.ndarray:
    return np.mean(
        connected[seed, start : end + 1, pair],
        axis=0,
        dtype=np.float64,
    )


def scores(predicted: np.ndarray, actual: np.ndarray) -> tuple[float, float]:
    actual_norm = float(np.linalg.norm(actual))
    predicted_norm = float(np.linalg.norm(predicted))
    nrmse = float(np.linalg.norm(predicted - actual) / (actual_norm + EPS))
    cosine = float(
        np.sum(predicted * actual)
        / (predicted_norm * actual_norm + EPS)
    )
    return nrmse, cosine


def main() -> None:
    required = (CONNECTED, RESULTS, CYCLES, *FIGURES)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing Q39A validation inputs: {missing}")

    with RESULTS.open("r", encoding="utf-8") as stream:
        summary = json.load(stream)
    with gzip.open(CYCLES, "rt", newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    connected = np.load(CONNECTED, mmap_mode="r")

    count = len(rows)
    sample_indices = np.unique(
        np.linspace(0, count - 1, num=min(401, count), dtype=int)
    )
    maximum_errors = {
        "source_cosine": 0.0,
        "absolute_error": 0.0,
        "predicted_c3_cosine": 0.0,
        "visible_relation_reversal_nrmse": 0.0,
        "visible_relation_reversal_cosine": 0.0,
    }
    flag_disagreements = 0
    negative_disagreements = 0

    for index in sample_indices:
        row = rows[int(index)]
        seed = int(row["seed"])
        pair = int(row["pair_index"])
        identities = [
            matrix_mean(
                connected,
                seed,
                pair,
                int(row[f"q{quadrant}_start"]),
                int(row[f"q{quadrant}_end"]),
            )
            for quadrant in range(1, 5)
        ]
        c1, c2, c3, c4 = identities
        delta = c1 - c2
        predicted = c3 + delta
        original_nrmse, original_cosine = scores(predicted, c4)
        predicted_c3_cosine = float(
            np.sum(predicted * c3)
            / (np.linalg.norm(predicted) * np.linalg.norm(c3) + EPS)
        )
        visible_flag = predicted_c3_cosine < 0
        corrected = c3 - delta if visible_flag else predicted
        corrected_nrmse, corrected_cosine = scores(corrected, c4)

        recomputed = {
            "source_cosine": original_cosine,
            "absolute_error": float(np.linalg.norm(predicted - c4)),
            "predicted_c3_cosine": predicted_c3_cosine,
            "visible_relation_reversal_nrmse": corrected_nrmse,
            "visible_relation_reversal_cosine": corrected_cosine,
        }
        saved = {
            "source_cosine": float(row["ara_cosine"]),
            "absolute_error": float(row["absolute_error"]),
            "predicted_c3_cosine": float(row["predicted_c3_cosine"]),
            "visible_relation_reversal_nrmse": float(
                row["visible_relation_reversal_nrmse"]
            ),
            "visible_relation_reversal_cosine": float(
                row["visible_relation_reversal_cosine"]
            ),
        }
        for key in maximum_errors:
            maximum_errors[key] = max(
                maximum_errors[key], abs(recomputed[key] - saved[key])
            )
        flag_disagreements += int(
            visible_flag != bool(int(row["visible_prediction_anti_to_c3"]))
        )
        negative_disagreements += int(
            (original_cosine < 0) != bool(int(row["negative_cosine"]))
        )
        if abs(original_nrmse - float(row["no_parity_nrmse"])) > TOLERANCE:
            raise AssertionError(f"Original NRMSE mismatch at cycle {index}")

    negative = np.asarray(
        [bool(int(row["negative_cosine"])) for row in rows], dtype=bool
    )
    visible = np.asarray(
        [bool(int(row["visible_prediction_anti_to_c3"])) for row in rows],
        dtype=bool,
    )
    original = np.asarray(
        [float(row["no_parity_nrmse"]) for row in rows], dtype=np.float64
    )
    corrected = np.asarray(
        [float(row["visible_relation_reversal_nrmse"]) for row in rows],
        dtype=np.float64,
    )
    confusion = {
        "true_positive": int(np.sum(visible & negative)),
        "false_positive": int(np.sum(visible & ~negative)),
        "false_negative": int(np.sum(~visible & negative)),
        "true_negative": int(np.sum(~visible & ~negative)),
    }
    stored_confusion = summary["seam_association"][
        "visible_prediction_anti_to_c3"
    ]
    confusion_matches = all(
        confusion[key] == int(stored_confusion[key]) for key in confusion
    )

    comparison = summary["visible_relation_reversal_comparison"]
    changed_improved = int(
        np.sum(visible & (corrected < original - 1e-15))
    )
    changed_worsened = int(
        np.sum(visible & (corrected > original + 1e-15))
    )
    headline_matches = {
        "cycle_count": count == int(summary["population"]["cycles"]),
        "negative_count": int(np.sum(negative))
        == int(summary["population"]["negative_cosine_cycles"]),
        "visible_count": int(np.sum(visible))
        == int(comparison["cycles_changed"]),
        "changed_improved": changed_improved
        == int(comparison["changed_cycles_improved"]),
        "changed_worsened": changed_worsened
        == int(comparison["changed_cycles_worsened"]),
        "confusion_matrix": confusion_matches,
    }
    figures = {
        path.name: {
            "exists": path.exists(),
            "bytes": path.stat().st_size if path.exists() else 0,
        }
        for path in FIGURES
    }
    passed = (
        all(value <= TOLERANCE for value in maximum_errors.values())
        and flag_disagreements == 0
        and negative_disagreements == 0
        and all(headline_matches.values())
        and all(item["bytes"] > 1_000 for item in figures.values())
    )

    result = {
        "validator": "Q39A-INDEPENDENT-MATRIX-RECONSTRUCTION-v1",
        "status": "PASS" if passed else "FAIL",
        "audit_module_imported": False,
        "population_rows": count,
        "deterministic_matrix_sample": int(len(sample_indices)),
        "tolerance": TOLERANCE,
        "maximum_absolute_metric_errors": maximum_errors,
        "flag_disagreements": flag_disagreements,
        "negative_disagreements": negative_disagreements,
        "confusion_matrix": confusion,
        "headline_matches": headline_matches,
        "changed_cycles_improved": changed_improved,
        "changed_cycles_worsened": changed_worsened,
        "figures": figures,
        "q39_verdict_unchanged": summary["q39_verdict_unchanged"],
    }
    with OUTPUT.open("w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
