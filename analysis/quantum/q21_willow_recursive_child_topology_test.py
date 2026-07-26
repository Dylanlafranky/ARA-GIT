#!/usr/bin/env python3
"""Run the checksum-frozen Q21 recursive child/topology ARA test."""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
from dataclasses import dataclass

import numpy as np

from q21_willow_child_topology_calibrate import (
    frozen_spatial_shuffle,
    parse_detector_coordinates,
    recursive_features,
    spatial_weights,
    unpack_detectors,
)


ROOT = pathlib.Path(__file__).parent
DEV_ROOT = ROOT / "public_data" / "q20_willow_105q" / "d5_at_q4_7"
HOLDOUT_ROOT = (
    ROOT / "public_data" / "q21_willow_105q" / "d5_at_q6_5"
)
OUTCOME_ROOT = (
    ROOT
    / "public_data"
    / "q21_willow_105q_outcomes"
    / "d5_at_q6_5"
)
OUTCOME_MANIFEST = (
    ROOT
    / "public_data"
    / "q21_willow_105q_outcomes"
    / "SOURCE_MANIFEST.json"
)
PROTOCOL = (
    ROOT / "Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_PROTOCOL_v1_FROZEN.md"
)
PROTOCOL_HASH = (
    "bd26fa2e70c1e4ddbb4e5d768b6099cb6caaea3c96ab1ce3cac545d6575cd24d"
)
CALIBRATION = ROOT / "Q21_WILLOW_CHILD_TOPOLOGY_CALIBRATION.json"
CALIBRATION_HASH = (
    "dcc0e609011e7fb725918cd9222828b0375352d2589eb42a6e477d5d255ad7fd"
)
RESULTS_JSON = (
    ROOT / "Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_RESULTS.json"
)
METRICS_CSV = (
    ROOT / "Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_METRICS.csv"
)
CONTROLS_CSV = (
    ROOT / "Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_CONTROLS.csv"
)
PROJECTIONS_CSV = (
    ROOT / "Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_PROJECTIONS.csv"
)
SEED = 20260726
PERMUTATIONS = 999
MODEL_NAMES = (
    "child_topology",
    "grandchildren_only",
    "parent_xy",
    "q20_global_xt",
    "count_only",
    "topology_plus_count",
    "spatial_shuffle_topology",
)


@dataclass(frozen=True)
class Dataset:
    basis: str
    split: str
    shots: int
    rounds: int
    detector_count: int
    labels: np.ndarray
    features: dict[str, np.ndarray]
    fill: np.ndarray
    quality: dict
    source_hashes: dict[str, str]


@dataclass(frozen=True)
class FittedModel:
    feature_mean: np.ndarray
    feature_sd: np.ndarray
    class_zero: np.ndarray
    class_one: np.ndarray
    direction: np.ndarray


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_freeze() -> None:
    if sha256(PROTOCOL) != PROTOCOL_HASH:
        raise RuntimeError("Frozen Q21 protocol checksum mismatch.")
    if sha256(CALIBRATION) != CALIBRATION_HASH:
        raise RuntimeError("Outcome-blind Q21 calibration checksum mismatch.")
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    if not calibration["outcome_blind_fresh_patch"]:
        raise RuntimeError("Calibration is not marked outcome-blind.")
    if calibration["fresh_outcome_files_extracted"]:
        raise RuntimeError("Calibration says a fresh outcome was extracted.")
    if calibration["primary_feature_count"] != 24:
        raise RuntimeError("Calibration does not freeze 24 primary features.")
    if any(
        "obs_flips" in name
        for name in calibration["fresh_manifest_members"]
    ):
        raise RuntimeError("Pre-freeze manifest includes an outcome member.")
    outcome_manifest = json.loads(
        OUTCOME_MANIFEST.read_text(encoding="utf-8")
    )
    outcome_names = sorted(item["name"] for item in outcome_manifest["members"])
    if len(outcome_names) != 2 or any(
        not name.endswith("/r30/obs_flips_actual.b8")
        for name in outcome_names
    ):
        raise RuntimeError("Post-freeze outcome manifest is not the expected pair.")


def unpack_labels(path: pathlib.Path, shots: int) -> np.ndarray:
    packed = np.fromfile(path, dtype=np.uint8)
    if packed.size != shots:
        raise ValueError(f"{path}: {packed.size} bytes; expected {shots}.")
    if np.any(packed & 0b11111110):
        raise ValueError(f"{path}: invalid high bits in one-bit b8 target.")
    return (packed & 1).astype(np.uint8)


def load_dataset(basis: str, split: str) -> Dataset:
    if split == "development":
        path = DEV_ROOT / basis / "r13"
        label_path = path / "obs_flips_actual.b8"
    elif split == "holdout":
        path = HOLDOUT_ROOT / basis / "r30"
        label_path = OUTCOME_ROOT / basis / "r30" / "obs_flips_actual.b8"
    else:
        raise ValueError(split)

    metadata_path = path / "metadata.json"
    circuit_path = path / "circuit_ideal.stim"
    detector_path = path / "detection_events.b8"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    shots = int(metadata["shots"])
    rounds = int(metadata["rounds"])
    coordinates = parse_detector_coordinates(circuit_path)
    detectors = unpack_detectors(
        detector_path, shots, len(coordinates)
    )
    labels = unpack_labels(label_path, shots)
    weights = spatial_weights(coordinates)
    ara, quality = recursive_features(detectors, coordinates, weights)
    shuffled_ara, shuffled_quality = recursive_features(
        detectors,
        coordinates,
        frozen_spatial_shuffle(weights, coordinates),
    )
    fill = detectors.sum(axis=1).astype(np.float64) / len(coordinates)
    features = {
        "child_topology": ara["topology"],
        "grandchildren_only": ara["grandchildren"],
        "parent_xy": ara["parent_xy"],
        "q20_global_xt": ara["q20_global_xt"],
        "count_only": fill[:, None],
        "topology_plus_count": np.column_stack((ara["topology"], fill)),
        "spatial_shuffle_topology": shuffled_ara["topology"],
    }
    return Dataset(
        basis=basis,
        split=split,
        shots=shots,
        rounds=rounds,
        detector_count=len(coordinates),
        labels=labels,
        features=features,
        fill=fill,
        quality={
            **quality,
            "spatial_shuffle": shuffled_quality,
            "mean_event_count": float(detectors.sum(axis=1).mean()),
            "target_prevalence": float(labels.mean()),
        },
        source_hashes={
            "metadata.json": sha256(metadata_path),
            "circuit_ideal.stim": sha256(circuit_path),
            "detection_events.b8": sha256(detector_path),
            "obs_flips_actual.b8": sha256(label_path),
        },
    )


def fit_model(features: np.ndarray, labels: np.ndarray) -> FittedModel:
    feature_mean = features.mean(axis=0)
    feature_sd = features.std(axis=0)
    if np.any(feature_sd <= 0):
        bad = np.flatnonzero(feature_sd <= 0).tolist()
        raise ValueError(f"Registered features have zero variance: {bad}")
    standardized = (features - feature_mean) / feature_sd
    class_zero = standardized[labels == 0].mean(axis=0)
    class_one = standardized[labels == 1].mean(axis=0)
    return FittedModel(
        feature_mean,
        feature_sd,
        class_zero,
        class_one,
        class_one - class_zero,
    )


def model_scores(model: FittedModel, features: np.ndarray) -> np.ndarray:
    standardized = (features - model.feature_mean) / model.feature_sd
    midpoint = (model.class_zero + model.class_one) / 2.0
    return (standardized - midpoint) @ model.direction


def average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(values.size, dtype=np.float64)
    start = 0
    while start < values.size:
        stop = start + 1
        while stop < values.size and sorted_values[stop] == sorted_values[start]:
            stop += 1
        ranks[order[start:stop]] = (start + 1 + stop) / 2.0
        start = stop
    return ranks


def auroc(labels: np.ndarray, scores: np.ndarray) -> float:
    positive = labels == 1
    n_positive = int(positive.sum())
    n_negative = int((~positive).sum())
    if not n_positive or not n_negative:
        return float("nan")
    ranks = average_ranks(scores)
    return float(
        (
            ranks[positive].sum()
            - n_positive * (n_positive + 1) / 2.0
        )
        / (n_positive * n_negative)
    )


def average_precision(labels: np.ndarray, scores: np.ndarray) -> float:
    order = np.argsort(-scores, kind="mergesort")
    ordered = labels[order]
    positives = int(ordered.sum())
    if positives == 0:
        return float("nan")
    cumulative = np.cumsum(ordered)
    precision = cumulative / np.arange(1, ordered.size + 1)
    return float(precision[ordered == 1].sum() / positives)


def metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    predicted = scores > 0
    positive = labels == 1
    negative = ~positive
    true_positive_rate = float(predicted[positive].mean())
    true_negative_rate = float((~predicted[negative]).mean())
    accuracy = float((predicted == positive).mean())
    return {
        "prevalence": float(labels.mean()),
        "accuracy": accuracy,
        "balanced_accuracy": (true_positive_rate + true_negative_rate) / 2.0,
        "auroc": auroc(labels, scores),
        "average_precision": average_precision(labels, scores),
        "error_rate": 1.0 - accuracy,
    }


def serialize_model(model: FittedModel) -> dict:
    return {
        "feature_mean": model.feature_mean.tolist(),
        "feature_sd": model.feature_sd.tolist(),
        "class_zero": model.class_zero.tolist(),
        "class_one": model.class_one.tolist(),
        "direction": model.direction.tolist(),
    }


def local_time_ara(grandchildren: np.ndarray) -> np.ndarray:
    pairs = grandchildren.reshape(-1, 4, 2)
    totals = pairs.sum(axis=2)
    output = np.ones((len(grandchildren), 4), dtype=np.float64)
    active = totals > 0
    output[active] = (
        2.0
        * pairs[:, :, 1][active]
        / totals[active]
    )
    return output


def construction_ok(dataset: Dataset) -> bool:
    quality = dataset.quality
    return bool(
        dataset.shots == 50000
        and dataset.detector_count
        == (312 if dataset.split == "development" else 720)
        and quality["grandchild_sum_max_error"] <= 1e-12
        and quality["handover_sum_max_error"] <= 1e-12
        and quality["grandchild_min"] >= -1e-12
        and quality["grandchild_max"] <= 2.0 + 1e-12
        and quality["handover_min"] >= -1e-12
        and quality["handover_max"] <= 2.0 + 1e-12
    )


def main() -> None:
    verify_freeze()
    rng = np.random.default_rng(SEED)
    results_by_basis = {}
    metric_rows = []
    control_rows = []
    projection_rows = []

    for basis in ("X", "Z"):
        development = load_dataset(basis, "development")
        holdout = load_dataset(basis, "holdout")
        fitted = {
            name: fit_model(development.features[name], development.labels)
            for name in MODEL_NAMES
        }
        scores = {
            name: model_scores(fitted[name], holdout.features[name])
            for name in MODEL_NAMES
        }
        basis_models = {}
        for name in MODEL_NAMES:
            development_score = model_scores(
                fitted[name], development.features[name]
            )
            development_metrics = metrics(
                development.labels, development_score
            )
            holdout_metrics = metrics(holdout.labels, scores[name])
            basis_models[name] = {
                "feature_count": int(development.features[name].shape[1]),
                "parameters": serialize_model(fitted[name]),
                "development_metrics": development_metrics,
                "holdout_metrics": holdout_metrics,
            }
            for split_name, values in (
                ("development", development_metrics),
                ("holdout", holdout_metrics),
            ):
                metric_rows.append(
                    {
                        "basis": basis,
                        "split": split_name,
                        "model": name,
                        **values,
                    }
                )

        observed_auc = basis_models["child_topology"][
            "holdout_metrics"
        ]["auroc"]
        null_aurocs = np.empty(PERMUTATIONS, dtype=np.float64)
        for iteration in range(PERMUTATIONS):
            permuted = rng.permutation(development.labels)
            null_model = fit_model(
                development.features["child_topology"], permuted
            )
            null_score = model_scores(
                null_model, holdout.features["child_topology"]
            )
            null_auc = auroc(holdout.labels, null_score)
            null_aurocs[iteration] = null_auc
            control_rows.append(
                {
                    "basis": basis,
                    "control": "development_label_permutation",
                    "iteration": iteration,
                    "holdout_auroc": null_auc,
                }
            )
        permutation = {
            "iterations": PERMUTATIONS,
            "seed": SEED,
            "p_value_one_sided": float(
                (1 + np.sum(null_aurocs >= observed_auc)) / 1000
            ),
            "null_auroc_mean": float(null_aurocs.mean()),
            "null_auroc_sd": float(null_aurocs.std()),
            "null_auroc_99th_percentile": float(
                np.quantile(null_aurocs, 0.99)
            ),
        }
        basis_models["child_topology"]["permutation_control"] = permutation

        for split_name, dataset, score_map in (
            (
                "development",
                development,
                {
                    name: model_scores(
                        fitted[name], development.features[name]
                    )
                    for name in MODEL_NAMES
                },
            ),
            ("holdout", holdout, scores),
        ):
            indices = np.unique(
                np.linspace(0, dataset.shots - 1, 200, dtype=int)
            )
            grand = dataset.features["grandchildren_only"]
            local = local_time_ara(grand)
            parent = dataset.features["parent_xy"]
            handover = dataset.features["child_topology"][:, 8:]
            strongest = np.argmax(handover, axis=1)
            for index in indices:
                projection_rows.append(
                    {
                        "basis": basis,
                        "split": split_name,
                        "shot_index": int(index),
                        "target": int(dataset.labels[index]),
                        "parent_x": float(parent[index, 0]),
                        "parent_y": float(parent[index, 1]),
                        "parent_relation": float(parent[index, 2]),
                        "child_AA_time_ara": float(local[index, 0]),
                        "child_AB_time_ara": float(local[index, 1]),
                        "child_BB_time_ara": float(local[index, 2]),
                        "child_BA_time_ara": float(local[index, 3]),
                        "strongest_handover_index": int(strongest[index]),
                        "strongest_handover_share": float(
                            handover[index, strongest[index]]
                        ),
                        "event_fill": float(dataset.fill[index]),
                        "child_topology_score": float(
                            score_map["child_topology"][index]
                        ),
                        "parent_xy_score": float(
                            score_map["parent_xy"][index]
                        ),
                        "count_score": float(
                            score_map["count_only"][index]
                        ),
                    }
                )

        results_by_basis[basis] = {
            "development": {
                "patch": "d5_at_q4_7",
                "rounds": development.rounds,
                "shots": development.shots,
                "detector_count": development.detector_count,
                "quality": development.quality,
                "source_hashes": development.source_hashes,
            },
            "holdout": {
                "patch": "d5_at_q6_5",
                "rounds": holdout.rounds,
                "shots": holdout.shots,
                "detector_count": holdout.detector_count,
                "quality": holdout.quality,
                "source_hashes": holdout.source_hashes,
            },
            "models": basis_models,
        }

    mean_metrics = {}
    for name in MODEL_NAMES:
        mean_metrics[name] = {
            metric: float(
                np.mean(
                    [
                        results_by_basis[basis]["models"][name][
                            "holdout_metrics"
                        ][metric]
                        for basis in ("X", "Z")
                    ]
                )
            )
            for metric in (
                "accuracy",
                "balanced_accuracy",
                "auroc",
                "average_precision",
                "error_rate",
            )
        }

    auc = {
        name: {
            basis: results_by_basis[basis]["models"][name][
                "holdout_metrics"
            ]["auroc"]
            for basis in ("X", "Z")
        }
        for name in MODEL_NAMES
    }
    mean_auc = {
        name: float(np.mean(list(values.values())))
        for name, values in auc.items()
    }
    gates = {
        "construction_and_source_integrity": bool(
            all(
                results_by_basis[basis][split]["shots"] == 50000
                and results_by_basis[basis][split]["detector_count"]
                == (312 if split == "development" else 720)
                and results_by_basis[basis][split]["quality"][
                    "grandchild_sum_max_error"
                ]
                <= 1e-12
                and results_by_basis[basis][split]["quality"][
                    "handover_sum_max_error"
                ]
                <= 1e-12
                and results_by_basis[basis][split]["quality"][
                    "grandchild_min"
                ]
                >= -1e-12
                and results_by_basis[basis][split]["quality"][
                    "grandchild_max"
                ]
                <= 2.0 + 1e-12
                and results_by_basis[basis][split]["quality"][
                    "handover_min"
                ]
                >= -1e-12
                and results_by_basis[basis][split]["quality"][
                    "handover_max"
                ]
                <= 2.0 + 1e-12
                for basis in ("X", "Z")
                for split in ("development", "holdout")
            )
        ),
        "child_topology_auroc_at_least_0_55_both_bases": bool(
            all(value >= 0.55 for value in auc["child_topology"].values())
        ),
        "mean_child_minus_parent_xy_at_least_0_01": bool(
            mean_auc["child_topology"] - mean_auc["parent_xy"] >= 0.01
        ),
        "mean_child_minus_q20_global_xt_at_least_0_01": bool(
            mean_auc["child_topology"] - mean_auc["q20_global_xt"] >= 0.01
        ),
        "permutation_p_at_most_0_01_both_bases": bool(
            all(
                results_by_basis[basis]["models"]["child_topology"][
                    "permutation_control"
                ]["p_value_one_sided"]
                <= 0.01
                for basis in ("X", "Z")
            )
        ),
        "mean_topology_plus_count_minus_count_at_least_0_01": bool(
            mean_auc["topology_plus_count"] - mean_auc["count_only"] >= 0.01
        ),
        "mean_child_minus_spatial_shuffle_at_least_0_01": bool(
            mean_auc["child_topology"]
            - mean_auc["spatial_shuffle_topology"]
            >= 0.01
        ),
        "combined_not_over_0_01_worse_than_count_either_basis": bool(
            all(
                auc["topology_plus_count"][basis]
                >= auc["count_only"][basis] - 0.01
                for basis in ("X", "Z")
            )
        ),
    }
    verdict = "SUPPORTED" if all(gates.values()) else "NOT SUPPORTED"
    results = {
        "claim": "Q21-WILLOW-RECURSIVE-CHILD-TOPOLOGY-v1",
        "created": "2026-07-26",
        "protocol_sha256": PROTOCOL_HASH,
        "calibration_sha256": CALIBRATION_HASH,
        "outcome_manifest_sha256": sha256(OUTCOME_MANIFEST),
        "source_doi": "10.5281/zenodo.13273331",
        "development_patch": "d5_at_q4_7/r13",
        "holdout_patch": "d5_at_q6_5/r30",
        "seed": SEED,
        "permutations_per_basis": PERMUTATIONS,
        "bases": results_by_basis,
        "holdout_equal_basis_mean": mean_metrics,
        "holdout_equal_basis_mean_auroc": mean_auc,
        "gates": gates,
        "verdict": verdict,
        "interpretation_fence": (
            "A parent near 1.0 is expected coarse-graining. Q21 tests only "
            "whether the frozen eight-grandchild/sixteen-handover cut retains "
            "fresh-patch logical-outcome information."
        ),
    }
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with METRICS_CSV.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(metric_rows[0]))
        writer.writeheader()
        writer.writerows(metric_rows)
    with CONTROLS_CSV.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(control_rows[0]))
        writer.writeheader()
        writer.writerows(control_rows)
    with PROJECTIONS_CSV.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(projection_rows[0]))
        writer.writeheader()
        writer.writerows(projection_rows)

    print(
        json.dumps(
            {
                "verdict": verdict,
                "gates": gates,
                "holdout_mean_auroc": mean_auc,
                "permutation_p": {
                    basis: results_by_basis[basis]["models"][
                        "child_topology"
                    ]["permutation_control"]["p_value_one_sided"]
                    for basis in ("X", "Z")
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
