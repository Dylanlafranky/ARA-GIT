#!/usr/bin/env python3
"""Run the frozen Q20 Willow ARA relation-decoder test."""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
from dataclasses import dataclass

import numpy as np


ROOT = pathlib.Path(__file__).parent
SOURCE_ROOT = ROOT / "public_data" / "q20_willow_105q" / "d5_at_q4_7"
PROTOCOL = ROOT / "Q20_WILLOW_ARA_RELATION_DECODER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_HASH = "3a55824116968450d43f64770933059c4ce00b0a873a7302b417111986118d6f"
GEOMETRY = ROOT / "Q20_WILLOW_ARA_GEOMETRY_CALIBRATION.json"
GEOMETRY_HASH = "29449fd5c5a27c87c2a0966afbcaaa0b20b28f480ca952c0bfc44d5071e0ed4e"
RESULTS_JSON = ROOT / "Q20_WILLOW_ARA_RELATION_DECODER_RESULTS.json"
METRICS_CSV = ROOT / "Q20_WILLOW_ARA_RELATION_DECODER_METRICS.csv"
CONTROLS_CSV = ROOT / "Q20_WILLOW_ARA_RELATION_DECODER_CONTROLS.csv"
PROJECTIONS_CSV = ROOT / "Q20_WILLOW_ARA_RELATION_DECODER_PROJECTIONS.csv"
SEED = 20260726
PERMUTATIONS = 999
AXIS_INDEX = {"x": 0, "y": 1, "t": 2}
AXIS_PAIRS = ("xt", "xy", "yt")
PRIMARY_PAIR = "xt"


@dataclass(frozen=True)
class Dataset:
    basis: str
    split: str
    rounds: int
    shots: int
    labels: np.ndarray
    feature_sets: dict[str, np.ndarray]
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
        raise RuntimeError("Frozen Q20 protocol checksum mismatch.")
    if sha256(GEOMETRY) != GEOMETRY_HASH:
        raise RuntimeError("Outcome-blind Q20 geometry checksum mismatch.")
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    if not geometry["outcome_blind"] or geometry["outcome_files_read"]:
        raise RuntimeError("Geometry artifact does not preserve the outcome-blind fence.")
    if geometry["selected_axis_pair"] != PRIMARY_PAIR:
        raise RuntimeError("Geometry artifact does not select the frozen x-time pair.")


def parse_detector_coordinates(path: pathlib.Path) -> np.ndarray:
    coordinates = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DETECTOR("):
            raw = line.split("(", 1)[1].split(")", 1)[0]
            values = [float(value) for value in raw.split(",")]
            coordinates.append(values[:3])
    return np.asarray(coordinates, dtype=np.float32)


def normalize_axis(coordinates: np.ndarray, axis: int) -> np.ndarray:
    values = coordinates[:, axis]
    span = float(values.max() - values.min())
    if span <= 0:
        raise ValueError(f"Axis {axis} has no span.")
    return (2.0 * (values - values.min()) / span - 1.0).astype(np.float32)


def unpack_detectors(
    detector_path: pathlib.Path, shots: int, detector_count: int
) -> np.ndarray:
    bytes_per_shot = (detector_count + 7) // 8
    packed = np.fromfile(detector_path, dtype=np.uint8)
    expected = shots * bytes_per_shot
    if packed.size != expected:
        raise ValueError(f"{detector_path}: {packed.size} bytes; expected {expected}.")
    packed = packed.reshape(shots, bytes_per_shot)
    return np.unpackbits(packed, axis=1, bitorder="little")[:, :detector_count]


def unpack_labels(path: pathlib.Path, shots: int) -> np.ndarray:
    packed = np.fromfile(path, dtype=np.uint8)
    if packed.size != shots:
        raise ValueError(f"{path}: {packed.size} bytes; expected {shots}.")
    if np.any(packed & 0b11111110):
        raise ValueError(f"{path}: non-padding bits are set in a one-bit b8 target.")
    return (packed & 1).astype(np.uint8)


def ara_features(
    detectors: np.ndarray, coordinates: np.ndarray, pair: str
) -> tuple[np.ndarray, dict]:
    axis_a = AXIS_INDEX[pair[0]]
    axis_b = AXIS_INDEX[pair[1]]
    first = normalize_axis(coordinates, axis_a)
    second = normalize_axis(coordinates, axis_b)
    first_a = (1.0 - first) / 2.0
    first_b = (1.0 + first) / 2.0
    second_a = (1.0 - second) / 2.0
    second_b = (1.0 + second) / 2.0
    children = np.column_stack(
        (
            detectors @ (first_a * second_a),
            detectors @ (first_a * second_b),
            detectors @ (first_b * second_a),
            detectors @ (first_b * second_b),
        )
    ).astype(np.float64)
    totals = children.sum(axis=1, keepdims=True)
    empty = totals[:, 0] == 0
    totals[empty] = 1.0
    children /= totals
    children[empty] = 0.25
    coordinates_ara = np.column_stack(
        (
            2.0 * (children[:, 2] + children[:, 3]),
            2.0 * (children[:, 1] + children[:, 3]),
            2.0 * (children[:, 1] + children[:, 2]),
        )
    )
    quality = {
        "empty_fraction": float(empty.mean()),
        "max_child_sum_error": float(np.max(np.abs(children.sum(axis=1) - 1.0))),
        "ara_min": float(coordinates_ara.min()),
        "ara_max": float(coordinates_ara.max()),
        "child_means": [float(value) for value in children.mean(axis=0)],
    }
    return coordinates_ara, quality


def load_dataset(basis: str, rounds_name: str, split: str) -> Dataset:
    path = SOURCE_ROOT / basis / rounds_name
    metadata_path = path / "metadata.json"
    circuit_path = path / "circuit_ideal.stim"
    detector_path = path / "detection_events.b8"
    label_path = path / "obs_flips_actual.b8"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    shots = int(metadata["shots"])
    rounds = int(metadata["rounds"])
    coordinates = parse_detector_coordinates(circuit_path)
    detector_count = coordinates.shape[0]
    if detector_count != 24 * rounds:
        raise ValueError(f"{basis}/{rounds_name}: expected 24 detectors per round.")
    detectors = unpack_detectors(detector_path, shots, detector_count)
    labels = unpack_labels(label_path, shots)
    feature_sets = {}
    pair_quality = {}
    for pair in AXIS_PAIRS:
        feature_sets[pair], pair_quality[pair] = ara_features(
            detectors, coordinates, pair
        )
    fill = detectors.sum(axis=1).astype(np.float64) / detector_count
    quality = {
        "detector_count": int(detector_count),
        "bytes_per_shot": int((detector_count + 7) // 8),
        "mean_event_count": float(detectors.sum(axis=1).mean()),
        "target_prevalence": float(labels.mean()),
        "pair_quality": pair_quality,
    }
    return Dataset(
        basis=basis,
        split=split,
        rounds=rounds,
        shots=shots,
        labels=labels,
        feature_sets=feature_sets,
        fill=fill,
        quality=quality,
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
        raise ValueError("A registered feature has zero development variance.")
    standardized = (features - feature_mean) / feature_sd
    if not np.any(labels == 0) or not np.any(labels == 1):
        raise ValueError("Both target classes must occur in development.")
    class_zero = standardized[labels == 0].mean(axis=0)
    class_one = standardized[labels == 1].mean(axis=0)
    direction = class_one - class_zero
    return FittedModel(feature_mean, feature_sd, class_zero, class_one, direction)


def model_scores(model: FittedModel, features: np.ndarray) -> np.ndarray:
    standardized = (features - model.feature_mean) / model.feature_sd
    midpoint = (model.class_zero + model.class_one) / 2.0
    return (standardized - midpoint) @ model.direction


def average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(values.size, dtype=np.float64)
    starts = np.flatnonzero(
        np.concatenate(([True], sorted_values[1:] != sorted_values[:-1]))
    )
    ends = np.concatenate((starts[1:], [values.size]))
    average = (starts + 1 + ends) / 2.0
    ranks[order] = np.repeat(average, ends - starts)
    return ranks


def auroc(labels: np.ndarray, scores: np.ndarray) -> float:
    positives = labels == 1
    positive_count = int(positives.sum())
    negative_count = labels.size - positive_count
    if positive_count == 0 or negative_count == 0:
        return float("nan")
    rank_sum = average_ranks(scores)[positives].sum()
    return float(
        (rank_sum - positive_count * (positive_count + 1) / 2.0)
        / (positive_count * negative_count)
    )


def average_precision(labels: np.ndarray, scores: np.ndarray) -> float:
    positive_count = int(labels.sum())
    if positive_count == 0:
        return float("nan")
    order = np.argsort(-scores, kind="mergesort")
    ordered = labels[order]
    cumulative = np.cumsum(ordered)
    precision = cumulative / np.arange(1, labels.size + 1)
    return float(precision[ordered == 1].sum() / positive_count)


def metrics(labels: np.ndarray, scores: np.ndarray) -> dict:
    prediction = (scores > 0).astype(np.uint8)
    positive = labels == 1
    negative = ~positive
    true_positive_rate = float(np.mean(prediction[positive] == 1))
    true_negative_rate = float(np.mean(prediction[negative] == 0))
    accuracy = float(np.mean(prediction == labels))
    return {
        "prevalence": float(labels.mean()),
        "accuracy": accuracy,
        "balanced_accuracy": (true_positive_rate + true_negative_rate) / 2.0,
        "auroc": auroc(labels, scores),
        "average_precision": average_precision(labels, scores),
        "error_rate": 1.0 - accuracy,
        "true_positive_rate": true_positive_rate,
        "true_negative_rate": true_negative_rate,
    }


def serialize_model(model: FittedModel) -> dict:
    return {
        "feature_mean": [float(value) for value in model.feature_mean],
        "feature_sd": [float(value) for value in model.feature_sd],
        "class_zero": [float(value) for value in model.class_zero],
        "class_one": [float(value) for value in model.class_one],
        "direction": [float(value) for value in model.direction],
    }


def registered_feature_sets(dataset: Dataset) -> dict[str, np.ndarray]:
    ara = dataset.feature_sets[PRIMARY_PAIR]
    return {
        "ARA_relation": ara,
        "count_only": dataset.fill[:, None],
        "ARA_plus_count": np.column_stack((ara, dataset.fill)),
    }


def main() -> None:
    verify_freeze()
    loaded: dict[str, dict[str, Dataset]] = {}
    for basis in ("X", "Z"):
        loaded[basis] = {
            "development": load_dataset(basis, "r13", "development"),
            "holdout": load_dataset(basis, "r30", "holdout"),
        }

    metric_rows = []
    control_rows = []
    result_bases = {}
    projection_rows = []
    rng = np.random.default_rng(SEED)

    for basis in ("X", "Z"):
        development = loaded[basis]["development"]
        holdout = loaded[basis]["holdout"]
        development_features = registered_feature_sets(development)
        holdout_features = registered_feature_sets(holdout)
        basis_result = {
            "development": {
                "rounds": development.rounds,
                "shots": development.shots,
                "quality": development.quality,
                "source_hashes": development.source_hashes,
            },
            "holdout": {
                "rounds": holdout.rounds,
                "shots": holdout.shots,
                "quality": holdout.quality,
                "source_hashes": holdout.source_hashes,
            },
            "models": {},
            "secondary_diameters": {},
        }
        fitted_models = {}
        holdout_scores = {}
        for model_name in ("ARA_relation", "count_only", "ARA_plus_count"):
            fitted = fit_model(
                development_features[model_name], development.labels
            )
            fitted_models[model_name] = fitted
            development_score = model_scores(
                fitted, development_features[model_name]
            )
            holdout_score = model_scores(fitted, holdout_features[model_name])
            holdout_scores[model_name] = holdout_score
            development_metrics = metrics(development.labels, development_score)
            holdout_metrics = metrics(holdout.labels, holdout_score)
            basis_result["models"][model_name] = {
                "parameters": serialize_model(fitted),
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
                        "model": model_name,
                        **values,
                    }
                )

        observed_auc = basis_result["models"]["ARA_relation"][
            "holdout_metrics"
        ]["auroc"]
        null_aurocs = np.empty(PERMUTATIONS, dtype=np.float64)
        for permutation in range(PERMUTATIONS):
            permuted = rng.permutation(development.labels)
            null_model = fit_model(
                development_features["ARA_relation"], permuted
            )
            null_score = model_scores(
                null_model, holdout_features["ARA_relation"]
            )
            null_auc = auroc(holdout.labels, null_score)
            null_aurocs[permutation] = null_auc
            control_rows.append(
                {
                    "basis": basis,
                    "control": "development_label_permutation",
                    "iteration": permutation,
                    "holdout_auroc": null_auc,
                }
            )
        p_value = float((1 + np.sum(null_aurocs >= observed_auc)) / 1000)
        basis_result["models"]["ARA_relation"]["permutation_control"] = {
            "iterations": PERMUTATIONS,
            "seed": SEED,
            "p_value_one_sided": p_value,
            "null_auroc_mean": float(null_aurocs.mean()),
            "null_auroc_sd": float(null_aurocs.std()),
            "null_auroc_99th_percentile": float(np.quantile(null_aurocs, 0.99)),
        }

        for pair in ("xy", "yt"):
            model = fit_model(
                development.feature_sets[pair], development.labels
            )
            score = model_scores(model, holdout.feature_sets[pair])
            basis_result["secondary_diameters"][pair] = {
                "parameters": serialize_model(model),
                "holdout_metrics": metrics(holdout.labels, score),
            }

        sample_indices = np.unique(
            np.linspace(0, development.shots - 1, 200, dtype=int)
        )
        for split_name, dataset, score_map in (
            (
                "development",
                development,
                {
                    name: model_scores(
                        fitted_models[name],
                        registered_feature_sets(development)[name],
                    )
                    for name in fitted_models
                },
            ),
            ("holdout", holdout, holdout_scores),
        ):
            indices = (
                sample_indices
                if split_name == "development"
                else np.unique(
                    np.linspace(0, holdout.shots - 1, 200, dtype=int)
                )
            )
            ara = dataset.feature_sets[PRIMARY_PAIR]
            for index in indices:
                projection_rows.append(
                    {
                        "basis": basis,
                        "split": split_name,
                        "shot_index": int(index),
                        "target": int(dataset.labels[index]),
                        "x_parent": float(ara[index, 0]),
                        "time_parent": float(ara[index, 1]),
                        "relation_j": float(ara[index, 2]),
                        "event_fill": float(dataset.fill[index]),
                        "ara_score": float(score_map["ARA_relation"][index]),
                        "count_score": float(score_map["count_only"][index]),
                        "ara_plus_count_score": float(
                            score_map["ARA_plus_count"][index]
                        ),
                    }
                )
        result_bases[basis] = basis_result

    holdout_mean = {}
    for model_name in ("ARA_relation", "count_only", "ARA_plus_count"):
        holdout_mean[model_name] = {
            metric: float(
                np.mean(
                    [
                        result_bases[basis]["models"][model_name][
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

    ara_auc = {
        basis: result_bases[basis]["models"]["ARA_relation"]["holdout_metrics"][
            "auroc"
        ]
        for basis in ("X", "Z")
    }
    count_auc = {
        basis: result_bases[basis]["models"]["count_only"]["holdout_metrics"][
            "auroc"
        ]
        for basis in ("X", "Z")
    }
    combined_auc = {
        basis: result_bases[basis]["models"]["ARA_plus_count"][
            "holdout_metrics"
        ]["auroc"]
        for basis in ("X", "Z")
    }
    gates = {
        "construction_and_source_integrity": bool(all(
            result_bases[basis][split]["shots"] == 50000
            and result_bases[basis][split]["quality"]["detector_count"]
            == (312 if split == "development" else 720)
            and all(
                pair_quality["max_child_sum_error"] <= 1e-12
                and pair_quality["ara_min"] >= -1e-12
                and pair_quality["ara_max"] <= 2.0 + 1e-12
                for pair_quality in result_bases[basis][split]["quality"][
                    "pair_quality"
                ].values()
            )
            for basis in ("X", "Z")
            for split in ("development", "holdout")
        )),
        "ara_auroc_at_least_0_55_both_bases": bool(all(
            value >= 0.55 for value in ara_auc.values()
        )),
        "mean_ara_minus_count_auroc_at_least_0_01": bool(
            np.mean(list(ara_auc.values())) - np.mean(list(count_auc.values()))
            >= 0.01
        ),
        "ara_permutation_p_at_most_0_01_both_bases": bool(all(
            result_bases[basis]["models"]["ARA_relation"][
                "permutation_control"
            ]["p_value_one_sided"]
            <= 0.01
            for basis in ("X", "Z")
        )),
        "mean_combined_minus_count_auroc_at_least_0_01": bool(
            np.mean(list(combined_auc.values()))
            - np.mean(list(count_auc.values()))
            >= 0.01
        ),
        "combined_not_over_0_01_worse_than_count_either_basis": bool(all(
            combined_auc[basis] >= count_auc[basis] - 0.01
            for basis in ("X", "Z")
        )),
    }
    verdict = "SUPPORTED" if all(gates.values()) else "NOT SUPPORTED"
    results = {
        "claim": "Q20-WILLOW-ARA-RELATION-v1",
        "created": "2026-07-26",
        "protocol_sha256": PROTOCOL_HASH,
        "geometry_sha256": GEOMETRY_HASH,
        "source_doi": "10.5281/zenodo.13273331",
        "source_archive": "google_105Q_surface_code_d3_d5_d7.zip",
        "source_archive_md5": "21fa6ad35b395d838ebcdbc92e364a12",
        "primary_axis_pair": PRIMARY_PAIR,
        "seed": SEED,
        "permutations_per_basis": PERMUTATIONS,
        "bases": result_bases,
        "holdout_equal_basis_mean": holdout_mean,
        "holdout_auroc_differences": {
            basis: {
                "ARA_relation_minus_count": ara_auc[basis] - count_auc[basis],
                "ARA_plus_count_minus_count": (
                    combined_auc[basis] - count_auc[basis]
                ),
            }
            for basis in ("X", "Z")
        },
        "gates": gates,
        "verdict": verdict,
        "interpretation_fence": (
            "This is a same-patch cross-duration ARA relation test, not a "
            "competitive established-decoder benchmark or a rare-burst cause claim."
        ),
    }
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
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

    print(json.dumps({"verdict": verdict, "gates": gates, "means": holdout_mean}, indent=2))


if __name__ == "__main__":
    main()
