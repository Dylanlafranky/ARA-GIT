#!/usr/bin/env python3
"""Run the checksum-frozen Q22 Tier-4 to Tier-1 vertical ARA test."""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
from dataclasses import dataclass

import numpy as np

from q21_willow_recursive_child_topology_test import (
    auroc,
    fit_model,
    metrics,
    model_scores,
    serialize_model,
)
from q22_willow_vertical_relation_features import (
    GEOMETRY_ROOT,
    build_feature_sets,
    load_geometry_dataset,
)


ROOT = pathlib.Path(__file__).parent
OUTCOME_ROOT = (
    ROOT
    / "public_data"
    / "q22_willow_105q_outcomes"
    / "d5_at_q6_9"
)
OUTCOME_MANIFEST = (
    ROOT
    / "public_data"
    / "q22_willow_105q_outcomes"
    / "SOURCE_MANIFEST.json"
)
FREEZE_MANIFEST = (
    ROOT / "Q22_WILLOW_VERTICAL_TIER4_TIER1_FREEZE_MANIFEST.json"
)
CALIBRATION = ROOT / "Q22_WILLOW_VERTICAL_RELATION_CALIBRATION.json"
RESULTS = ROOT / "Q22_WILLOW_VERTICAL_TIER4_TIER1_RESULTS.json"
METRICS_CSV = ROOT / "Q22_WILLOW_VERTICAL_TIER4_TIER1_METRICS.csv"
CONTROLS_CSV = ROOT / "Q22_WILLOW_VERTICAL_TIER4_TIER1_CONTROLS.csv"
PROJECTIONS_CSV = ROOT / "Q22_WILLOW_VERTICAL_TIER4_TIER1_PROJECTIONS.csv"

MODEL_NAMES = (
    "vertical_state",
    "vertical_travel",
    "vertical_both",
    "past_travel_control",
    "broken_vertical_both",
    "q21_child_topology",
    "event_fraction",
    "vertical_both_plus_count",
)


@dataclass(frozen=True)
class Dataset:
    basis: str
    split: str
    rounds: int
    shots: int
    labels: np.ndarray
    features: dict[str, np.ndarray]
    quality: dict
    source_hashes: dict[str, str]


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_freeze() -> dict:
    freeze = json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    for relative, expected in freeze["frozen_files_sha256"].items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise RuntimeError(
                f"Q22 freeze mismatch for {relative}: {actual} != {expected}"
            )
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    if not calibration["outcome_blind"]:
        raise RuntimeError("Q22 calibration is not marked outcome-blind.")
    if not calibration["all_construction_checks_pass"]:
        raise RuntimeError("Q22 construction checks did not pass.")
    if list(GEOMETRY_ROOT.rglob("obs_flips_actual.b8")):
        raise RuntimeError("Outcome labels contaminated the geometry tree.")

    outcome_manifest = json.loads(
        OUTCOME_MANIFEST.read_text(encoding="utf-8")
    )
    names = sorted(item["name"] for item in outcome_manifest["members"])
    if (
        outcome_manifest["stage"] != "outcomes"
        or len(names) != 4
        or any(not name.endswith("/obs_flips_actual.b8") for name in names)
    ):
        raise RuntimeError("Unexpected Q22 outcome extraction manifest.")
    return freeze


def unpack_labels(path: pathlib.Path, shots: int) -> np.ndarray:
    packed = np.fromfile(path, dtype=np.uint8)
    if packed.size != shots:
        raise ValueError(f"{path}: {packed.size} bytes; expected {shots}.")
    if np.any(packed & 0b11111110):
        raise ValueError(f"{path}: invalid high bits in one-bit b8 target.")
    return (packed & 1).astype(np.uint8)


def load_dataset(basis: str, split: str) -> Dataset:
    rounds = "r13" if split == "development" else "r30"
    detectors, coordinates, weights, metadata = load_geometry_dataset(
        basis, rounds
    )
    features, quality = build_feature_sets(detectors, coordinates, weights)
    label_path = OUTCOME_ROOT / basis / rounds / "obs_flips_actual.b8"
    labels = unpack_labels(label_path, int(metadata["shots"]))
    geometry_path = GEOMETRY_ROOT / basis / rounds
    return Dataset(
        basis=basis,
        split=split,
        rounds=int(metadata["rounds"]),
        shots=int(metadata["shots"]),
        labels=labels,
        features=features,
        quality=quality,
        source_hashes={
            name: sha256(geometry_path / name)
            for name in (
                "metadata.json",
                "circuit_ideal.stim",
                "detection_events.b8",
            )
        }
        | {"obs_flips_actual.b8": sha256(label_path)},
    )


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    freeze = verify_freeze()
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    results_by_basis = {}
    metric_rows: list[dict] = []
    projection_rows: list[dict] = []
    permutation_rows: list[dict] = []

    for basis in ("X", "Z"):
        development = load_dataset(basis, "development")
        holdout = load_dataset(basis, "holdout")
        fitted = {
            name: fit_model(development.features[name], development.labels)
            for name in MODEL_NAMES
        }
        basis_models = {}
        holdout_scores = {}
        for name in MODEL_NAMES:
            development_scores = model_scores(
                fitted[name], development.features[name]
            )
            holdout_score = model_scores(
                fitted[name], holdout.features[name]
            )
            holdout_scores[name] = holdout_score
            development_metrics = metrics(
                development.labels, development_scores
            )
            holdout_metrics = metrics(holdout.labels, holdout_score)
            basis_models[name] = {
                "feature_count": int(
                    development.features[name].shape[1]
                ),
                "development": development_metrics,
                "holdout": holdout_metrics,
                "fitted_model": serialize_model(fitted[name]),
            }
            for split, values in (
                ("development", development_metrics),
                ("holdout", holdout_metrics),
            ):
                metric_rows.append(
                    {
                        "basis": basis,
                        "split": split,
                        "model": name,
                        "feature_count": int(
                            development.features[name].shape[1]
                        ),
                        **values,
                    }
                )

        rng = np.random.default_rng(20260726)
        observed_auc = basis_models["vertical_both"]["holdout"]["auroc"]
        null_aucs = np.empty(999, dtype=np.float64)
        for index in range(999):
            permuted = rng.permutation(development.labels)
            null_model = fit_model(
                development.features["vertical_both"], permuted
            )
            null_score = model_scores(
                null_model, holdout.features["vertical_both"]
            )
            null_aucs[index] = auroc(holdout.labels, null_score)
        p_value = float((1 + np.sum(null_aucs >= observed_auc)) / 1000)
        permutation = {
            "count": 999,
            "seed": 20260726,
            "observed_holdout_auroc": observed_auc,
            "null_mean_auroc": float(null_aucs.mean()),
            "null_sd_auroc": float(null_aucs.std()),
            "null_max_auroc": float(null_aucs.max()),
            "one_sided_empirical_p": p_value,
        }
        basis_models["vertical_both"]["permutation_control"] = permutation
        permutation_rows.append({"basis": basis, **permutation})

        for index in np.linspace(0, holdout.shots - 1, 24, dtype=int):
            projection_rows.append(
                {
                    "basis": basis,
                    "shot_index": int(index),
                    "target": int(holdout.labels[index]),
                    "vertical_state_score": float(
                        holdout_scores["vertical_state"][index]
                    ),
                    "vertical_travel_score": float(
                        holdout_scores["vertical_travel"][index]
                    ),
                    "vertical_both_score": float(
                        holdout_scores["vertical_both"][index]
                    ),
                    "past_control_score": float(
                        holdout_scores["past_travel_control"][index]
                    ),
                    "broken_control_score": float(
                        holdout_scores["broken_vertical_both"][index]
                    ),
                    "q21_topology_score": float(
                        holdout_scores["q21_child_topology"][index]
                    ),
                }
            )

        results_by_basis[basis] = {
            "development": {
                "rounds": development.rounds,
                "shots": development.shots,
                "prevalence": float(development.labels.mean()),
                "quality": development.quality,
                "source_sha256": development.source_hashes,
            },
            "holdout": {
                "rounds": holdout.rounds,
                "shots": holdout.shots,
                "prevalence": float(holdout.labels.mean()),
                "quality": holdout.quality,
                "source_sha256": holdout.source_hashes,
            },
            "models": basis_models,
        }

    auc = {
        name: {
            basis: results_by_basis[basis]["models"][name]["holdout"][
                "auroc"
            ]
            for basis in ("X", "Z")
        }
        for name in MODEL_NAMES
    }
    mean_auc = {
        name: float(np.mean(list(values.values())))
        for name, values in auc.items()
    }
    holdout_geometry = {
        basis: calibration["datasets"][f"{basis}_r30"]["quality"]
        for basis in ("X", "Z")
    }

    gates = {
        "future_closer_than_past_both_holdout_bases": bool(
            all(
                quality["future_ridge_distance_mean"]
                < quality["past_ridge_distance_mean"]
                for quality in holdout_geometry.values()
            )
        ),
        "future_closer_than_broken_future_both_holdout_bases": bool(
            all(
                quality["future_ridge_distance_mean"]
                < quality["broken_future_ridge_distance_mean"]
                for quality in holdout_geometry.values()
            )
        ),
        "vertical_state_auroc_at_least_0_52_both_bases": bool(
            all(value >= 0.52 for value in auc["vertical_state"].values())
        ),
        "vertical_travel_auroc_at_least_0_52_both_bases": bool(
            all(value >= 0.52 for value in auc["vertical_travel"].values())
        ),
        "vertical_both_auroc_at_least_0_55_both_bases": bool(
            all(value >= 0.55 for value in auc["vertical_both"].values())
        ),
        "mean_vertical_both_minus_q21_at_least_0_01": bool(
            mean_auc["vertical_both"]
            - mean_auc["q21_child_topology"]
            >= 0.01
        ),
        "mean_vertical_both_minus_count_at_least_0_01": bool(
            mean_auc["vertical_both"] - mean_auc["event_fraction"] >= 0.01
        ),
        "mean_vertical_both_minus_past_at_least_0_01": bool(
            mean_auc["vertical_both"]
            - mean_auc["past_travel_control"]
            >= 0.01
        ),
        "mean_vertical_both_minus_broken_at_least_0_01": bool(
            mean_auc["vertical_both"]
            - mean_auc["broken_vertical_both"]
            >= 0.01
        ),
        "permutation_p_at_most_0_01_both_bases": bool(
            all(
                results_by_basis[basis]["models"]["vertical_both"][
                    "permutation_control"
                ]["one_sided_empirical_p"]
                <= 0.01
                for basis in ("X", "Z")
            )
        ),
        "count_changes_mean_auroc_by_less_than_0_01": bool(
            abs(
                mean_auc["vertical_both_plus_count"]
                - mean_auc["vertical_both"]
            )
            < 0.01
        ),
        "vertical_both_direction_concordant_both_bases": bool(
            all(
                results_by_basis[basis]["models"]["vertical_both"][
                    "development"
                ]["auroc"]
                >= 0.5
                and results_by_basis[basis]["models"]["vertical_both"][
                    "holdout"
                ]["auroc"]
                >= 0.5
                for basis in ("X", "Z")
            )
        ),
    }
    geometry_gate_names = tuple(list(gates)[:2])
    geometry_supported = all(gates[name] for name in geometry_gate_names)
    predictive_supported = all(
        gates[name] for name in list(gates)[2:]
    )
    overall_supported = bool(geometry_supported and predictive_supported)

    control_rows = [
        {
            "control": name,
            "X_holdout_auroc": auc[name]["X"],
            "Z_holdout_auroc": auc[name]["Z"],
            "mean_holdout_auroc": mean_auc[name],
        }
        for name in MODEL_NAMES
    ]
    control_rows.extend(
        {
            "control": f"gate::{name}",
            "X_holdout_auroc": "",
            "Z_holdout_auroc": "",
            "mean_holdout_auroc": int(value),
        }
        for name, value in gates.items()
    )
    write_csv(METRICS_CSV, metric_rows)
    write_csv(CONTROLS_CSV, control_rows)
    write_csv(PROJECTIONS_CSV, projection_rows)

    result = {
        "test": "Q22",
        "title": "Tier-4 to Tier-1 vertical ARA state and travel",
        "source_doi": "10.5281/zenodo.13273331",
        "patch": "d5_at_q6_9",
        "development": "r13",
        "holdout": "r30",
        "protocol_freeze_manifest": freeze,
        "calibration_sha256": sha256(CALIBRATION),
        "outcome_manifest_sha256": sha256(OUTCOME_MANIFEST),
        "results_by_basis": results_by_basis,
        "holdout_auroc": auc,
        "mean_holdout_auroc": mean_auc,
        "holdout_directional_geometry": holdout_geometry,
        "permutation_controls": permutation_rows,
        "gates": gates,
        "gate_count_passed": int(sum(gates.values())),
        "gate_count_total": int(len(gates)),
        "geometry_supported": bool(geometry_supported),
        "prediction_supported": bool(predictive_supported),
        "overall_verdict": (
            "SUPPORTED" if overall_supported else "NOT SUPPORTED"
        ),
        "claim_boundary": (
            "Tests the frozen q6_9 Tier-4/Tier-1 state and delayed-travel "
            "construction. It does not establish universal fractality, "
            "causation, a new quantum state, or decoder superiority."
        ),
    }
    RESULTS.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        result["overall_verdict"],
        f"{result['gate_count_passed']}/{result['gate_count_total']} gates",
    )
    for name, values in auc.items():
        print(name, values, "mean", mean_auc[name])
    print("geometry_supported", geometry_supported)
    print("prediction_supported", predictive_supported)


if __name__ == "__main__":
    main()
