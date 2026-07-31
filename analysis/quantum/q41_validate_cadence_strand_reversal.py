"""Independent validation of Q41 stored predictions, targets and summaries."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import pathlib
import sys
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import numpy as np


DATA = HERE / "public_data" / "q41_cadence_strand_inhomo_v1_random"
CONNECTED = DATA / "q41_connected_cache.npy"
PREDICTIONS = DATA / "q41_frozen_predictions.npz"
EVENTS = HERE / "Q41_CADENCE_STRAND_REVERSAL_CYCLES.csv.gz"
RESULTS = HERE / "Q41_CADENCE_STRAND_REVERSAL_RESULTS.json"
OUTPUT = HERE / "Q41_CADENCE_STRAND_REVERSAL_VALIDATION.json"
EPS = 1e-12
METHODS = ("q41", "q40", "forward", "persistence", "development_affine")


def digest(path: pathlib.Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def close(left: float, right: float, tolerance: float = 3e-6) -> bool:
    return bool(abs(left - right) <= tolerance * max(1.0, abs(right)))


def metrics(predicted, actual, scale):
    error = float(np.linalg.norm(predicted - actual))
    actual_norm = float(np.linalg.norm(actual))
    predicted_norm = float(np.linalg.norm(predicted))
    predicted_h = float(np.cbrt(abs(np.linalg.det(predicted))))
    actual_h = float(np.cbrt(abs(np.linalg.det(actual))))
    return {
        "scaled_error": error / (scale + EPS),
        "absolute_error": error,
        "nrmse": error / (actual_norm + EPS),
        "cosine": float(
            np.sum(predicted * actual)
            / (predicted_norm * actual_norm + EPS)
        ),
        "closure_error": abs(predicted_h - actual_h) / (actual_h + EPS),
    }


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    connected = np.load(CONNECTED, mmap_mode="r")
    frozen = np.load(PREDICTIONS, allow_pickle=False)
    with gzip.open(EVENTS, "rt", newline="", encoding="utf-8") as stream:
        stored_rows = list(csv.DictReader(stream))
    if tuple(str(value) for value in frozen["methods"]) != METHODS:
        raise RuntimeError("Frozen method names do not match validator")
    if len(stored_rows) != len(frozen["seed"]):
        raise RuntimeError("Event and prediction counts differ")

    mismatches = []
    recomputed = []
    for index, stored in enumerate(stored_rows):
        seed = int(frozen["seed"][index])
        pair = int(frozen["pair"][index])
        start = int(frozen["q4_start"][index])
        end = int(frozen["q4_end"][index])
        actual = np.mean(
            connected[seed, start : end + 1, pair],
            axis=0,
            dtype=np.float64,
        )
        c1, c2, c3 = np.asarray(
            frozen["c_visible"][index], dtype=np.float64
        )
        forward = c1 - c2 + c3
        orientation = float(
            np.sum(forward * actual)
            / (np.linalg.norm(forward) * np.linalg.norm(actual) + EPS)
        )
        target_negative = int(orientation < 0)
        if target_negative != int(stored["target_negative_orientation"]):
            mismatches.append(f"orientation row {index}")
        item = {
            "seed": seed,
            "pair": pair,
            "q40_flag": int(frozen["q40_flag"][index]),
            "q41_flag": int(frozen["q41_flag"][index]),
            "target": target_negative,
        }
        predictions = np.asarray(
            frozen["predictions"][index], dtype=np.float64
        )
        for method_index, method in enumerate(METHODS):
            values = metrics(
                predictions[method_index],
                actual,
                float(frozen["lineage_scale"][index]),
            )
            for name, value in values.items():
                stored_value = float(stored[f"{method}_{name}"])
                if not close(value, stored_value):
                    mismatches.append(f"{method}_{name} row {index}")
                item[f"{method}_{name}"] = value
        recomputed.append(item)

    lineage_groups = defaultdict(list)
    for row in recomputed:
        lineage_groups[(row["seed"], row["pair"])].append(row)
    seed_groups = defaultdict(list)
    for (seed, _pair), values in lineage_groups.items():
        seed_groups[seed].append(
            {
                method: float(
                    np.mean(
                        [row[f"{method}_scaled_error"] for row in values]
                    )
                )
                for method in METHODS
            }
        )
    seed_means = {
        method: float(
            np.mean(
                [
                    np.mean([row[method] for row in values])
                    for values in seed_groups.values()
                ]
            )
        )
        for method in METHODS
    }
    for method in METHODS:
        stored_mean = result["method_summaries"][method]["scaled_error"][
            "seed_balanced_mean"
        ]
        if not close(seed_means[method], stored_mean):
            mismatches.append(f"seed mean {method}")

    q40_advantage = seed_means["q40"] - seed_means["q41"]
    affine_advantage = (
        seed_means["development_affine"] - seed_means["q41"]
    )
    if not close(
        q40_advantage,
        result["comparisons_scaled_error"]["q40"]["advantage"],
    ):
        mismatches.append("q41:q40 advantage")
    if not close(
        affine_advantage,
        result["comparisons_scaled_error"]["development_affine"][
            "advantage"
        ],
    ):
        mismatches.append("q41:affine advantage")

    def confusion(flag_name):
        flag = np.asarray([bool(row[flag_name]) for row in recomputed])
        target = np.asarray([bool(row["target"]) for row in recomputed])
        return {
            "true_positive": int(np.sum(flag & target)),
            "false_positive": int(np.sum(flag & ~target)),
            "false_negative": int(np.sum(~flag & target)),
            "true_negative": int(np.sum(~flag & ~target)),
        }

    for label, flag in (("q40", "q40_flag"), ("q41", "q41_flag")):
        observed = confusion(flag)
        stored = result["reversal_detection"][label]
        for name, value in observed.items():
            if value != int(stored[name]):
                mismatches.append(f"{label} confusion {name}")

    prediction_sha = digest(PREDICTIONS, "sha256")
    if prediction_sha != result["prediction_sha256_before_reveal"]:
        mismatches.append("prediction SHA-256")

    payload = {
        "test_id": result["test_id"],
        "status": "PASS" if not mismatches else "FAIL",
        "prediction_sha256": prediction_sha,
        "cycles_recomputed": len(recomputed),
        "lineages_recomputed": len(lineage_groups),
        "seeds_recomputed": len(seed_groups),
        "seed_balanced_scaled_error": seed_means,
        "q41_over_q40_advantage": q40_advantage,
        "q41_over_development_affine_advantage": affine_advantage,
        "mismatch_count": len(mismatches),
        "mismatches_first_25": mismatches[:25],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if mismatches:
        raise RuntimeError(f"Q41 validation failed: {mismatches[:5]}")


if __name__ == "__main__":
    main()

