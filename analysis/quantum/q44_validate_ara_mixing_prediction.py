"""Independent numerical and leakage validation for Q44."""

from __future__ import annotations

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

import q40_return_flow_relation_reversal_test as base


DATA = HERE / "public_data" / "q44_mixing_inhomo_v1_mimic"
CONNECTED = DATA / "q44_connected_cache.npy"
PREDICTIONS = DATA / "q44_frozen_predictions.npz"
RESULTS = HERE / "Q44_ARA_MIXING_PREDICTION_RESULTS.json"
VALIDATION = HERE / "Q44_ARA_MIXING_PREDICTION_VALIDATION.json"
EPS = 1e-12
METHODS = (
    "ara_mixing",
    "diameter_only",
    "persistence",
    "forward_relation",
    "reverse_relation",
    "local_linear",
    "pooled_affine",
    "grouped_affine",
)
METRICS = (
    "scaled_error",
    "nrmse",
    "cosine",
    "closure_error",
    "orientation_correct",
)


def sha256(path: pathlib.Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def metric_block(predicted, actual, scale, forward):
    error = float(np.linalg.norm(predicted - actual))
    predicted_norm = float(np.linalg.norm(predicted))
    actual_norm = float(np.linalg.norm(actual))
    predicted_h = float(np.cbrt(abs(np.linalg.det(predicted))))
    actual_h = float(np.cbrt(abs(np.linalg.det(actual))))
    return {
        "scaled_error": error / (scale + EPS),
        "nrmse": error / (actual_norm + EPS),
        "cosine": float(
            np.sum(predicted * actual)
            / (predicted_norm * actual_norm + EPS)
        ),
        "closure_error": abs(predicted_h - actual_h) / (actual_h + EPS),
        "orientation_correct": float(
            np.sign(np.sum(predicted * forward))
            == np.sign(np.sum(actual * forward))
        ),
    }


def recompute():
    frozen = np.load(PREDICTIONS, allow_pickle=False)
    keys = set(frozen.files)
    forbidden = sorted(
        key
        for key in keys
        if (
            key.lower().startswith("actual")
            or key.lower() in {"c4", "target", "targets", "y_eval"}
        )
    )
    if tuple(str(value) for value in frozen["methods"]) != METHODS:
        raise RuntimeError("Frozen method order differs")
    connected = np.load(CONNECTED, mmap_mode="r")
    cycle_rows = []
    for index in range(len(frozen["seed"])):
        seed, pair = int(frozen["seed"][index]), int(frozen["pair"][index])
        start, end = (
            int(frozen["q4_start"][index]),
            int(frozen["q4_end"][index]),
        )
        actual = np.mean(
            connected[seed, start : end + 1, pair],
            axis=0,
            dtype=np.float64,
        )
        c1, c2, c3 = np.asarray(frozen["c_visible"][index], dtype=np.float64)
        forward = c3 + c1 - c2
        predictions = np.asarray(frozen["predictions"][index], dtype=np.float64)
        row = {
            "seed": seed,
            "pair": pair,
        }
        for method_index, method in enumerate(METHODS):
            values = metric_block(
                predictions[method_index],
                actual,
                float(frozen["lineage_scale"][index]),
                forward,
            )
            for metric, value in values.items():
                row[f"{method}_{metric}"] = value
        cycle_rows.append(row)

    lineage_groups = defaultdict(list)
    for row in cycle_rows:
        lineage_groups[(row["seed"], row["pair"])].append(row)
    lineage_rows = []
    for (seed, pair), values in lineage_groups.items():
        row = {"seed": seed, "pair": pair}
        for method in METHODS:
            for metric in METRICS:
                row[f"{method}_{metric}"] = float(
                    np.mean([value[f"{method}_{metric}"] for value in values])
                )
        lineage_rows.append(row)
    seed_groups = defaultdict(list)
    for row in lineage_rows:
        seed_groups[row["seed"]].append(row)
    seed_rows = []
    for seed, values in seed_groups.items():
        row = {"seed": seed}
        for method in METHODS:
            for metric in METRICS:
                row[f"{method}_{metric}"] = float(
                    np.mean([value[f"{method}_{metric}"] for value in values])
                )
        seed_rows.append(row)
    summary = {
        method: {
            metric: float(
                np.mean([row[f"{method}_{metric}"] for row in seed_rows])
            )
            for metric in METRICS
        }
        for method in METHODS
    }
    return summary, forbidden, len(cycle_rows), len(lineage_rows), len(seed_rows)


def main() -> None:
    recorded = json.loads(RESULTS.read_text(encoding="utf-8"))
    summary, forbidden, cycles, lineages, seeds = recompute()
    differences = {}
    for method in METHODS:
        for metric in METRICS:
            key = f"{method}.{metric}"
            differences[key] = abs(
                summary[method][metric]
                - recorded["seed_balanced_methods"][method][metric]
            )
    maximum_difference = max(differences.values())
    checks = {
        "prediction_artifact_contains_no_named_target_arrays": not forbidden,
        "prediction_sha256_matches_result": (
            sha256(PREDICTIONS)
            == recorded["frozen_artifacts"]["prediction_sha256"]
        ),
        "cycle_count_matches": cycles == recorded["sample"]["evaluation_cycles"],
        "lineage_count_matches": (
            lineages == recorded["sample"]["represented_lineages"]
        ),
        "seed_count_matches": seeds == recorded["sample"]["represented_seeds"],
        "all_seed_balanced_metrics_match_within_1e_12": (
            maximum_difference <= 1e-12
        ),
        "all_recomputed_metrics_finite": all(
            np.isfinite(value)
            for method in summary.values()
            for value in method.values()
        ),
    }
    output = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "forbidden_prediction_artifact_keys": forbidden,
        "maximum_absolute_metric_difference": maximum_difference,
        "recomputed_seed_balanced_methods": summary,
    }
    VALIDATION.write_text(
        json.dumps(output, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2), flush=True)
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
